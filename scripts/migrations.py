"""Helper local para comandos comuns do Alembic.

O objetivo e evitar lembrar a sintaxe completa de cada comando e padronizar o
uso do Alembic dentro do projeto.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Sequence


def run_alembic(args: Sequence[str]) -> int:
    """Executa `python -m alembic ...` e devolve o exit code."""
    command = [sys.executable, "-m", "alembic", *args]
    result = subprocess.run(command, check=False)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    """Monta a CLI enxuta usada pelo helper de migrations."""
    parser = argparse.ArgumentParser(description="Helper para comandos do Alembic.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("current", help="Mostra a revision atual do banco.")
    subparsers.add_parser("history", help="Mostra o historico de migrations.")
    subparsers.add_parser("heads", help="Mostra as revisions head.")
    subparsers.add_parser("upgrade", help="Aplica migrations ate o head.")
    subparsers.add_parser("stamp", help="Marca o banco atual como head sem aplicar DDL.")

    revision_parser = subparsers.add_parser("revision", help="Cria uma nova migration.")
    revision_parser.add_argument("message", help="Mensagem da migration.")
    revision_parser.add_argument(
        "--autogenerate",
        action="store_true",
        help="Gera a migration comparando metadata e banco.",
    )

    return parser


def main() -> int:
    """Resolve o subcomando pedido e o traduz para o Alembic."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "current":
        return run_alembic(["current"])
    if args.command == "history":
        return run_alembic(["history", "--verbose"])
    if args.command == "heads":
        return run_alembic(["heads"])
    if args.command == "upgrade":
        return run_alembic(["upgrade", "head"])
    if args.command == "stamp":
        return run_alembic(["stamp", "head"])
    if args.command == "revision":
        command = ["revision", "-m", args.message]
        if args.autogenerate:
            command.append("--autogenerate")
        return run_alembic(command)

    parser.error("Comando invalido.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
