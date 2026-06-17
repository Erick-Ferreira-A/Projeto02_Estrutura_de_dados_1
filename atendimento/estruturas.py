"""Estruturas e algoritmos usados pelo sistema."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TypeVar

from atendimento.modelos import Cliente, validar_id

T = TypeVar("T")


def busca_binaria_cliente(
    clientes_ordenados: list[Cliente],
    cliente_id: int | str,
) -> Cliente | None:
    """Busca cliente por id usando recursao e vetor ordenado."""
    id_validado = validar_id(cliente_id, "id do cliente")
    return _busca_binaria_recursiva(
        clientes_ordenados,
        id_validado,
        0,
        len(clientes_ordenados) - 1,
    )


def _busca_binaria_recursiva(
    clientes_ordenados: list[Cliente],
    cliente_id: int,
    esquerda: int,
    direita: int,
) -> Cliente | None:
    if esquerda > direita:
        return None

    meio = (esquerda + direita) // 2
    cliente = clientes_ordenados[meio]

    if cliente.id == cliente_id:
        return cliente
    if cliente.id < cliente_id:
        return _busca_binaria_recursiva(
            clientes_ordenados,
            cliente_id,
            meio + 1,
            direita,
        )
    return _busca_binaria_recursiva(
        clientes_ordenados,
        cliente_id,
        esquerda,
        meio - 1,
    )


def posicao_insercao_cliente(
    clientes_ordenados: list[Cliente],
    cliente_id: int,
) -> int:
    """Retorna posicao correta para manter o vetor ordenado por id."""
    esquerda = 0
    direita = len(clientes_ordenados)

    while esquerda < direita:
        meio = (esquerda + direita) // 2
        if clientes_ordenados[meio].id < cliente_id:
            esquerda = meio + 1
        else:
            direita = meio
    return esquerda


@dataclass
class NoCliente:
    """No da lista encadeada de clientes."""

    cliente: Cliente
    proximo: "NoCliente | None" = None


class ListaEncadeadaClientes:
    """Lista encadeada usada para controlar clientes ativos/inativos."""

    def __init__(self, clientes: Iterable[Cliente] | None = None) -> None:
        self.inicio: NoCliente | None = None
        self.fim: NoCliente | None = None
        self.tamanho = 0

        if clientes:
            for cliente in clientes:
                self.adicionar(cliente)

    def adicionar(self, cliente: Cliente) -> None:
        """Adiciona cliente ao final da lista encadeada."""
        if self.buscar(cliente.id) is not None:
            return

        novo_no = NoCliente(cliente)
        if self.inicio is None:
            self.inicio = novo_no
            self.fim = novo_no
        else:
            assert self.fim is not None
            self.fim.proximo = novo_no
            self.fim = novo_no
        self.tamanho += 1

    def buscar(self, cliente_id: int | str) -> Cliente | None:
        """Busca cliente na lista encadeada de forma linear."""
        id_validado = validar_id(cliente_id, "id do cliente")
        atual = self.inicio
        while atual is not None:
            if atual.cliente.id == id_validado:
                return atual.cliente
            atual = atual.proximo
        return None

    def remover_por_id(self, cliente_id: int | str) -> Cliente | None:
        """Remove um cliente especifico da lista encadeada."""
        id_validado = validar_id(cliente_id, "id do cliente")
        anterior: NoCliente | None = None
        atual = self.inicio

        while atual is not None:
            if atual.cliente.id == id_validado:
                if anterior is None:
                    self.inicio = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if self.fim == atual:
                    self.fim = anterior
                self.tamanho -= 1
                return atual.cliente
            anterior = atual
            atual = atual.proximo
        return None

    def remover_inativos(self) -> list[Cliente]:
        """Remove e retorna todos os clientes marcados como inativos."""
        removidos: list[Cliente] = []
        anterior: NoCliente | None = None
        atual = self.inicio

        while atual is not None:
            proximo = atual.proximo
            if not atual.cliente.ativo:
                removidos.append(atual.cliente)
                if anterior is None:
                    self.inicio = proximo
                else:
                    anterior.proximo = proximo
                if self.fim == atual:
                    self.fim = anterior
                self.tamanho -= 1
            else:
                anterior = atual
            atual = proximo
        return removidos

    def listar(self) -> list[Cliente]:
        """Retorna clientes armazenados na lista encadeada."""
        clientes: list[Cliente] = []
        atual = self.inicio
        while atual is not None:
            clientes.append(atual.cliente)
            atual = atual.proximo
        return clientes


def merge_sort(
    itens: list[T],
    chave: Callable[[T], object],
    reverso: bool = False,
) -> list[T]:
    """Ordena itens com merge sort recursivo."""
    if len(itens) <= 1:
        return list(itens)

    meio = len(itens) // 2
    esquerda = merge_sort(itens[:meio], chave, reverso)
    direita = merge_sort(itens[meio:], chave, reverso)
    return _intercalar(esquerda, direita, chave, reverso)


def _intercalar(
    esquerda: list[T],
    direita: list[T],
    chave: Callable[[T], object],
    reverso: bool,
) -> list[T]:
    resultado: list[T] = []
    i = 0
    j = 0

    while i < len(esquerda) and j < len(direita):
        deve_usar_esquerda = chave(esquerda[i]) <= chave(direita[j])
        if reverso:
            deve_usar_esquerda = chave(esquerda[i]) >= chave(direita[j])

        if deve_usar_esquerda:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1

    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado
