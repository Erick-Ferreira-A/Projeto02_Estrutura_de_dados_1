"""Persistencia em JSON."""

from __future__ import annotations

import json
from pathlib import Path

from atendimento.servico import SistemaAtendimento


def salvar_estado(caminho: str | Path, sistema: SistemaAtendimento) -> None:
    """Salva estado completo do sistema em arquivo JSON."""
    arquivo = Path(caminho)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with arquivo.open("w", encoding="utf-8") as saida:
        json.dump(sistema.para_dict(), saida, ensure_ascii=True, indent=2)


def carregar_estado(caminho: str | Path) -> SistemaAtendimento:
    """Carrega estado do sistema a partir de arquivo JSON."""
    arquivo = Path(caminho)
    if not arquivo.exists():
        return SistemaAtendimento()

    with arquivo.open("r", encoding="utf-8") as entrada:
        dados = json.load(entrada)

    if not isinstance(dados, dict):
        raise ValueError("Arquivo de dados deve conter um objeto JSON.")
    return SistemaAtendimento.de_dict(dados)
