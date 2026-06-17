"""Relatorios e exportacao CSV."""

from __future__ import annotations

import csv
from pathlib import Path

from atendimento.modelos import RegistroAtendimento
from atendimento.servico import SistemaAtendimento


def exportar_historico_csv(
    caminho: str | Path,
    registros: list[RegistroAtendimento],
) -> None:
    """Exporta historico de atendimentos para CSV."""
    campos = [
        "id_atendimento",
        "cliente_id",
        "atendente_id",
        "aberto_em",
        "iniciado_em",
        "finalizado_em",
        "duracao_minutos",
        "espera_minutos",
    ]
    linhas = [registro.para_dict() for registro in registros]
    _exportar_csv(caminho, campos, linhas)


def exportar_resumo_csv(
    caminho: str | Path,
    sistema: SistemaAtendimento,
) -> None:
    """Exporta resumo com tempo medio e total de atendimentos."""
    campos = ["indicador", "valor"]
    linhas = [
        {
            "indicador": "total_atendimentos",
            "valor": len(sistema.historico),
        },
        {
            "indicador": "tempo_medio_minutos",
            "valor": sistema.tempo_medio_atendimento(),
        },
    ]
    _exportar_csv(caminho, campos, linhas)


def exportar_top_clientes_csv(
    caminho: str | Path,
    sistema: SistemaAtendimento,
) -> None:
    """Exporta top 5 clientes mais atendidos para CSV."""
    campos = ["cliente_id", "nome", "total_atendimentos"]
    linhas = sistema.top_clientes_mais_atendidos()
    _exportar_csv(caminho, campos, linhas)


def _exportar_csv(
    caminho: str | Path,
    campos: list[str],
    linhas: list[dict[str, object]],
) -> None:
    arquivo = Path(caminho)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with arquivo.open("w", newline="", encoding="utf-8") as saida:
        escritor = csv.DictWriter(saida, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)
