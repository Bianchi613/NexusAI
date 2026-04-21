"""Fluxo agentico com Ollama concentrado em um unico ponto.

Este modulo junta:
- cliente HTTP do Ollama
- utilitarios comuns dos agentes
- orquestracao do fluxo facts -> structure -> writer -> editor
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from typing import Optional

import requests

from Engine.app.ai.ollama import GeneratedArticlePayload
from Engine.app.models import RawArticle


@dataclass
class FactSheet:
    """Mapa factual extraido da fonte original."""

    main_event: str
    key_points: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    numbers: list[str] = field(default_factory=list)
    source_limits: list[str] = field(default_factory=list)
    factual_notes: list[str] = field(default_factory=list)


@dataclass
class ArticleOutline:
    """Estrutura editorial que orienta a redacao."""

    angle: str
    title: str
    summary: str
    section_order: list[str] = field(default_factory=list)
    paragraph_goals: list[str] = field(default_factory=list)
    category: str = "Geral"
    tags: list[str] = field(default_factory=list)


@dataclass
class DraftArticle:
    """Rascunho produzido pelo agente redator."""

    title: str
    summary: Optional[str]
    body: str
    category: str
    tags: list[str] = field(default_factory=list)
    editor_notes: list[str] = field(default_factory=list)


class BaseAgent:
    """Classe base enxuta para os agentes editoriais."""

    def __init__(self, *, provider: Any, prompt_path: Path) -> None:
        self.provider = provider
        self.prompt_path = prompt_path

    def load_prompt(self) -> str:
        """Carrega o prompt do agente a partir de disco."""
        if not self.prompt_path.exists():
            return ""
        return self.prompt_path.read_text(encoding="utf-8").strip()

    def request_json(self, prompt: str) -> dict[str, Any]:
        """Encaminha o prompt ao Ollama e normaliza a resposta."""
        try:
            payload = self.provider.generate_json(prompt)
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def dump_json(data: Any) -> str:
        """Serializa conteudo auxiliar sem escapar acentos."""
        return json.dumps(data, ensure_ascii=False, indent=2)


class AgenticOllamaClient:
    """Cliente compativel com a interface atual de geracao do pipeline."""

    def __init__(
        self,
        *,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
        prompts_dir: Path | None = None,
    ) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.timeout_seconds = timeout_seconds or int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))
        self.prompts_dir = prompts_dir or Path(__file__).resolve().parents[2] / "prompts" / "agents"

        # Import local para evitar circularidade: os agentes usam `BaseAgent`
        # definido neste arquivo.
        from Engine.app.ai.agents.editor_agent import EditorAgent
        from Engine.app.ai.agents.facts_agent import FactsAgent
        from Engine.app.ai.agents.structure_agent import StructureAgent
        from Engine.app.ai.agents.writer_agent import WriterAgent

        self.facts_agent = FactsAgent(provider=self, prompt_path=self.prompts_dir / "facts_agent.txt")
        self.structure_agent = StructureAgent(provider=self, prompt_path=self.prompts_dir / "structure_agent.txt")
        self.writer_agent = WriterAgent(provider=self, prompt_path=self.prompts_dir / "writer_agent.txt")
        self.editor_agent = EditorAgent(provider=self, prompt_path=self.prompts_dir / "editor_agent.txt")

    def generate_json(self, prompt: str) -> dict[str, Any]:
        """Executa um prompt no Ollama pedindo resposta JSON."""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        raw_text = payload.get("response", "")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            return {}

        return parsed if isinstance(parsed, dict) else {}

    def generate_article(self, raw_article: RawArticle, prompt_template: str = "") -> GeneratedArticlePayload:
        """Executa o fluxo editorial completo com os quatro agentes."""
        fact_sheet = self.facts_agent.run(raw_article=raw_article)
        outline = self.structure_agent.run(
            raw_article=raw_article,
            fact_sheet=fact_sheet,
            prompt_template=prompt_template,
        )
        draft = self.writer_agent.run(
            raw_article=raw_article,
            fact_sheet=fact_sheet,
            outline=outline,
            prompt_template=prompt_template,
        )
        return self.editor_agent.run(
            raw_article=raw_article,
            fact_sheet=fact_sheet,
            outline=outline,
            draft=draft,
            prompt_template=prompt_template,
        )
