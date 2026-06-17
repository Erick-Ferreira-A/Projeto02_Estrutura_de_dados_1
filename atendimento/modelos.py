"""Modelos e validacoes do sistema de atendimento."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def validar_id(valor: int | str, campo: str = "id") -> int:
    """Valida identificador inteiro positivo."""
    try:
        numero = int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{campo.capitalize()} deve ser inteiro.") from exc

    if numero <= 0:
        raise ValueError(f"{campo.capitalize()} deve ser positivo.")
    return numero


def validar_texto(valor: str, campo: str) -> str:
    """Valida texto obrigatorio."""
    texto = str(valor).strip()
    if not texto:
        raise ValueError(f"{campo.capitalize()} nao pode ficar vazio.")
    return texto


def validar_duracao(valor: int | str) -> int:
    """Valida duracao em minutos."""
    try:
        minutos = int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError("Duracao deve ser um numero inteiro.") from exc

    if minutos <= 0:
        raise ValueError("Duracao deve ser maior que zero.")
    return minutos


def converter_bool(valor: bool | str | int) -> bool:
    """Converte valores comuns para booleano."""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, int):
        return valor != 0

    texto = str(valor).strip().lower()
    if texto in {"s", "sim", "true", "1", "prioridade"}:
        return True
    if texto in {"n", "nao", "não", "false", "0", "comum"}:
        return False
    raise ValueError("Valor booleano invalido.")


def converter_data(valor: datetime | str) -> datetime:
    """Converte datetime ou string ISO em datetime."""
    if isinstance(valor, datetime):
        return valor
    try:
        return datetime.fromisoformat(str(valor))
    except ValueError as exc:
        raise ValueError("Data deve estar em formato ISO.") from exc


@dataclass
class Cliente:
    """Cliente cadastrado no sistema."""

    id: int
    nome: str
    telefone: str
    prioridade: bool = False
    ativo: bool = True

    def __post_init__(self) -> None:
        self.id = validar_id(self.id, "id do cliente")
        self.nome = validar_texto(self.nome, "nome")
        self.telefone = validar_texto(self.telefone, "telefone")
        self.prioridade = converter_bool(self.prioridade)
        self.ativo = converter_bool(self.ativo)

    def para_dict(self) -> dict[str, int | str | bool]:
        """Converte cliente para dicionario."""
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "prioridade": self.prioridade,
            "ativo": self.ativo,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> "Cliente":
        """Cria cliente a partir de dicionario."""
        return cls(
            id=int(dados["id"]),
            nome=str(dados["nome"]),
            telefone=str(dados["telefone"]),
            prioridade=bool(dados.get("prioridade", False)),
            ativo=bool(dados.get("ativo", True)),
        )


@dataclass
class Atendente:
    """Atendente cadastrado."""

    id: int
    nome: str
    ativo: bool = True

    def __post_init__(self) -> None:
        self.id = validar_id(self.id, "id do atendente")
        self.nome = validar_texto(self.nome, "nome")
        self.ativo = converter_bool(self.ativo)

    def para_dict(self) -> dict[str, int | str | bool]:
        """Converte atendente para dicionario."""
        return {"id": self.id, "nome": self.nome, "ativo": self.ativo}

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> "Atendente":
        """Cria atendente a partir de dicionario."""
        return cls(
            id=int(dados["id"]),
            nome=str(dados["nome"]),
            ativo=bool(dados.get("ativo", True)),
        )


@dataclass
class SolicitacaoAtendimento:
    """Entrada de um cliente em uma fila."""

    id_atendimento: int
    cliente_id: int
    prioridade: bool
    aberto_em: datetime

    def __post_init__(self) -> None:
        self.id_atendimento = validar_id(
            self.id_atendimento,
            "id do atendimento",
        )
        self.cliente_id = validar_id(self.cliente_id, "id do cliente")
        self.prioridade = converter_bool(self.prioridade)
        self.aberto_em = converter_data(self.aberto_em)

    def para_dict(self) -> dict[str, int | str | bool]:
        """Converte solicitacao para dicionario."""
        return {
            "id_atendimento": self.id_atendimento,
            "cliente_id": self.cliente_id,
            "prioridade": self.prioridade,
            "aberto_em": self.aberto_em.isoformat(timespec="seconds"),
        }

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> "SolicitacaoAtendimento":
        """Cria solicitacao a partir de dicionario."""
        return cls(
            id_atendimento=int(dados["id_atendimento"]),
            cliente_id=int(dados["cliente_id"]),
            prioridade=bool(dados["prioridade"]),
            aberto_em=converter_data(str(dados["aberto_em"])),
        )


@dataclass
class AtendimentoEmAndamento:
    """Atendimento chamado e vinculado a um atendente."""

    id_atendimento: int
    cliente_id: int
    atendente_id: int
    prioridade: bool
    aberto_em: datetime
    iniciado_em: datetime

    def __post_init__(self) -> None:
        self.id_atendimento = validar_id(
            self.id_atendimento,
            "id do atendimento",
        )
        self.cliente_id = validar_id(self.cliente_id, "id do cliente")
        self.atendente_id = validar_id(self.atendente_id, "id do atendente")
        self.prioridade = converter_bool(self.prioridade)
        self.aberto_em = converter_data(self.aberto_em)
        self.iniciado_em = converter_data(self.iniciado_em)

    def para_dict(self) -> dict[str, int | str | bool]:
        """Converte atendimento em andamento para dicionario."""
        return {
            "id_atendimento": self.id_atendimento,
            "cliente_id": self.cliente_id,
            "atendente_id": self.atendente_id,
            "prioridade": self.prioridade,
            "aberto_em": self.aberto_em.isoformat(timespec="seconds"),
            "iniciado_em": self.iniciado_em.isoformat(timespec="seconds"),
        }

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> "AtendimentoEmAndamento":
        """Cria atendimento em andamento a partir de dicionario."""
        return cls(
            id_atendimento=int(dados["id_atendimento"]),
            cliente_id=int(dados["cliente_id"]),
            atendente_id=int(dados["atendente_id"]),
            prioridade=bool(dados["prioridade"]),
            aberto_em=converter_data(str(dados["aberto_em"])),
            iniciado_em=converter_data(str(dados["iniciado_em"])),
        )


@dataclass
class RegistroAtendimento:
    """Registro historico de atendimento finalizado."""

    id_atendimento: int
    cliente_id: int
    atendente_id: int
    aberto_em: datetime
    iniciado_em: datetime
    finalizado_em: datetime
    duracao_minutos: int
    espera_minutos: int

    def __post_init__(self) -> None:
        self.id_atendimento = validar_id(
            self.id_atendimento,
            "id do atendimento",
        )
        self.cliente_id = validar_id(self.cliente_id, "id do cliente")
        self.atendente_id = validar_id(self.atendente_id, "id do atendente")
        self.aberto_em = converter_data(self.aberto_em)
        self.iniciado_em = converter_data(self.iniciado_em)
        self.finalizado_em = converter_data(self.finalizado_em)
        self.duracao_minutos = validar_duracao(self.duracao_minutos)
        self.espera_minutos = max(0, int(self.espera_minutos))

    def para_dict(self) -> dict[str, int | str]:
        """Converte registro para dicionario."""
        return {
            "id_atendimento": self.id_atendimento,
            "cliente_id": self.cliente_id,
            "atendente_id": self.atendente_id,
            "aberto_em": self.aberto_em.isoformat(timespec="seconds"),
            "iniciado_em": self.iniciado_em.isoformat(timespec="seconds"),
            "finalizado_em": self.finalizado_em.isoformat(timespec="seconds"),
            "duracao_minutos": self.duracao_minutos,
            "espera_minutos": self.espera_minutos,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> "RegistroAtendimento":
        """Cria registro a partir de dicionario."""
        return cls(
            id_atendimento=int(dados["id_atendimento"]),
            cliente_id=int(dados["cliente_id"]),
            atendente_id=int(dados["atendente_id"]),
            aberto_em=converter_data(str(dados["aberto_em"])),
            iniciado_em=converter_data(str(dados["iniciado_em"])),
            finalizado_em=converter_data(str(dados["finalizado_em"])),
            duracao_minutos=int(dados["duracao_minutos"]),
            espera_minutos=int(dados["espera_minutos"]),
        )
