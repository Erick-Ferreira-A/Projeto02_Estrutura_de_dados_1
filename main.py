"""Ponto de entrada do Sistema de Atendimento e Analise."""

from __future__ import annotations

from pathlib import Path

from atendimento.interface import executar_app


def main() -> None:
    """Executa a aplicacao."""
    base_dir = Path(__file__).resolve().parent
    executar_app(base_dir)


if __name__ == "__main__":
    main()
