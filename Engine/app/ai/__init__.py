"""Camada de IA da Engine.

Este pacote mantem os clientes atuais e recebe a nova estrutura agentica
sem substituir o fluxo existente de uma vez.
"""

from Engine.app.ai.agentic import AgenticOllamaClient

__all__ = ["AgenticOllamaClient"]
