"""Ponto de entrada simples do backend NexusAI.

Este modulo existe para manter a execucao do pipeline previsivel:
- nao decide regra de negocio
- nao cria schema manualmente
- apenas prepara o ambiente e dispara o fluxo principal
"""

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
