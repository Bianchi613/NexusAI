"""Ponto de entrada simples do backend NexusAI.

Este modulo existe para manter a execucao do pipeline previsivel:
- nao decide regra de negocio
- nao cria schema manualmente
- apenas prepara o ambiente e dispara o fluxo principal
"""

from pathlib import Path
import sys

# Permite executar `python app/main.py` ou o botao "Executar Arquivo do Python"
# do VS Code sem quebrar os imports absolutos do pacote `app`.
if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.db import init_db
from app.core.pipeline import NewsPipeline


def main() -> None:
    """Executa uma rodada completa do pipeline e imprime um resumo final."""
    init_db()
    pipeline = NewsPipeline()
    result = pipeline.run()
    print(f"Pipeline finalizado. Materias geradas: {len(result)}")


if __name__ == "__main__":
    main()
