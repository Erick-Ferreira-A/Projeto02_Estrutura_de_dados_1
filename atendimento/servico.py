"""Regras de negocio do sistema de atendimento."""

from __future__ import annotations

from collections import deque
from datetime import datetime

from atendimento.estruturas import (
    ListaEncadeadaClientes,
    busca_binaria_cliente,
    merge_sort,
    posicao_insercao_cliente,
)
from atendimento.modelos import (
    Atendente,
    AtendimentoEmAndamento,
    Cliente,
    RegistroAtendimento,
    SolicitacaoAtendimento,
    validar_duracao,
    validar_id,
)


class SistemaAtendimento:
    """Controla cadastros, filas, historico e relatorios."""

    def __init__(self) -> None:
        self.clientes_temporarios: list[Cliente] = []
        self.clientes_por_id: list[Cliente] = []
        self.clientes_encadeados = ListaEncadeadaClientes()
        self.atendentes: list[Atendente] = []
        self.fila_prioridade: deque[SolicitacaoAtendimento] = deque()
        self.fila_comum: deque[SolicitacaoAtendimento] = deque()
        self.em_atendimento: dict[int, AtendimentoEmAndamento] = {}
        self.historico: list[RegistroAtendimento] = []
        self.pilha_desfazer: list[tuple[
            RegistroAtendimento,
            AtendimentoEmAndamento,
        ]] = []
        self.proximo_atendimento_id = 1

    def cadastrar_cliente(self, cliente: Cliente) -> Cliente:
        """Cadastra cliente em vetor nao ordenado e vetor ordenado."""
        if self.buscar_cliente(cliente.id) is not None:
            raise ValueError("Ja existe cliente com esse id.")

        self.clientes_temporarios.append(cliente)
        posicao = posicao_insercao_cliente(self.clientes_por_id, cliente.id)
        self.clientes_por_id.insert(posicao, cliente)
        self.clientes_encadeados.adicionar(cliente)
        return cliente

    def cadastrar_atendente(self, atendente: Atendente) -> Atendente:
        """Cadastra atendente."""
        if self.buscar_atendente(atendente.id) is not None:
            raise ValueError("Ja existe atendente com esse id.")
        self.atendentes.append(atendente)
        return atendente

    def buscar_cliente(self, cliente_id: int | str) -> Cliente | None:
        """Busca rapida por id usando vetor ordenado e busca binaria."""
        return busca_binaria_cliente(self.clientes_por_id, cliente_id)

    def buscar_atendente(self, atendente_id: int | str) -> Atendente | None:
        """Busca atendente por id em vetor simples."""
        id_validado = validar_id(atendente_id, "id do atendente")
        for atendente in self.atendentes:
            if atendente.id == id_validado:
                return atendente
        return None

    def abrir_atendimento(
        self,
        cliente_id: int | str,
        aberto_em: datetime | None = None,
    ) -> SolicitacaoAtendimento:
        """Coloca cliente na fila comum ou prioridade."""
        cliente = self._obter_cliente(cliente_id)
        if not cliente.ativo:
            raise ValueError("Cliente inativo nao pode abrir atendimento.")
        if self._cliente_tem_atendimento_aberto(cliente.id):
            raise ValueError("Cliente ja possui atendimento aberto.")

        solicitacao = SolicitacaoAtendimento(
            id_atendimento=self.proximo_atendimento_id,
            cliente_id=cliente.id,
            prioridade=cliente.prioridade,
            aberto_em=aberto_em or datetime.now(),
        )
        self.proximo_atendimento_id += 1

        if cliente.prioridade:
            self.fila_prioridade.append(solicitacao)
        else:
            self.fila_comum.append(solicitacao)
        return solicitacao

    def chamar_proximo(
        self,
        atendente_id: int | str,
        iniciado_em: datetime | None = None,
    ) -> AtendimentoEmAndamento:
        """Chama proximo atendimento priorizando a fila urgente."""
        atendente = self._obter_atendente(atendente_id)
        if not atendente.ativo:
            raise ValueError("Atendente inativo nao pode atender.")
        if atendente.id in self.em_atendimento:
            raise ValueError("Atendente ja esta em atendimento.")

        if self.fila_prioridade:
            solicitacao = self.fila_prioridade.popleft()
        elif self.fila_comum:
            solicitacao = self.fila_comum.popleft()
        else:
            raise ValueError("Nao ha atendimento em fila.")

        atendimento = AtendimentoEmAndamento(
            id_atendimento=solicitacao.id_atendimento,
            cliente_id=solicitacao.cliente_id,
            atendente_id=atendente.id,
            prioridade=solicitacao.prioridade,
            aberto_em=solicitacao.aberto_em,
            iniciado_em=iniciado_em or datetime.now(),
        )
        self.em_atendimento[atendente.id] = atendimento
        return atendimento

    def finalizar_atendimento(
        self,
        atendente_id: int | str,
        duracao_minutos: int | str,
        finalizado_em: datetime | None = None,
    ) -> RegistroAtendimento:
        """Finaliza atendimento em andamento e registra historico."""
        id_atendente = validar_id(atendente_id, "id do atendente")
        if id_atendente not in self.em_atendimento:
            raise ValueError("Nao existe atendimento em andamento para esse atendente.")

        duracao = validar_duracao(duracao_minutos)
        atendimento = self.em_atendimento.pop(id_atendente)
        fim = finalizado_em or datetime.now()
        tempo_espera = atendimento.iniciado_em - atendimento.aberto_em
        espera = int(tempo_espera.total_seconds() // 60)
        espera = max(0, espera)

        registro = RegistroAtendimento(
            id_atendimento=atendimento.id_atendimento,
            cliente_id=atendimento.cliente_id,
            atendente_id=atendimento.atendente_id,
            aberto_em=atendimento.aberto_em,
            iniciado_em=atendimento.iniciado_em,
            finalizado_em=fim,
            duracao_minutos=duracao,
            espera_minutos=espera,
        )
        self.historico.append(registro)
        self.pilha_desfazer.append((registro, atendimento))
        return registro

    def desfazer_ultima_finalizacao(self) -> RegistroAtendimento:
        """Desfaz a ultima finalizacao usando pilha."""
        if not self.pilha_desfazer:
            raise ValueError("Nao ha finalizacao para desfazer.")

        registro, atendimento = self.pilha_desfazer.pop()
        if atendimento.atendente_id in self.em_atendimento:
            self.pilha_desfazer.append((registro, atendimento))
            raise ValueError("Atendente ja esta em outro atendimento.")

        self.historico = [
            item
            for item in self.historico
            if item.id_atendimento != registro.id_atendimento
        ]
        self.em_atendimento[atendimento.atendente_id] = atendimento
        return registro

    def desativar_cliente(self, cliente_id: int | str) -> Cliente:
        """Marca cliente como inativo se nao houver atendimento aberto."""
        cliente = self._obter_cliente(cliente_id)
        if self._cliente_tem_atendimento_aberto(cliente.id):
            raise ValueError(
                "Nao e permitido desativar cliente com atendimento aberto."
            )
        cliente.ativo = False
        return cliente

    def remover_clientes_inativos(self) -> list[Cliente]:
        """Remove clientes inativos usando a lista encadeada."""
        bloqueados = self._ids_clientes_com_atendimento_aberto()
        inativos_bloqueados = [
            cliente.id
            for cliente in self.clientes_temporarios
            if not cliente.ativo and cliente.id in bloqueados
        ]
        if inativos_bloqueados:
            raise ValueError("Existe cliente inativo com atendimento aberto.")

        removidos = self.clientes_encadeados.remover_inativos()
        ids_removidos = {cliente.id for cliente in removidos}
        self.clientes_temporarios = [
            cliente
            for cliente in self.clientes_temporarios
            if cliente.id not in ids_removidos
        ]
        self.clientes_por_id = [
            cliente
            for cliente in self.clientes_por_id
            if cliente.id not in ids_removidos
        ]
        return removidos

    def historico_por_cliente(
        self,
        cliente_id: int | str,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> list[RegistroAtendimento]:
        """Retorna historico de atendimentos do cliente."""
        id_validado = validar_id(cliente_id, "id do cliente")
        registros = [
            registro
            for registro in self.historico
            if registro.cliente_id == id_validado
        ]
        return self._filtrar_por_data(registros, data_inicio, data_fim)

    def tempo_medio_atendimento(
        self,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> float:
        """Calcula tempo medio de atendimento."""
        registros = self._filtrar_por_data(self.historico, data_inicio, data_fim)
        if not registros:
            return 0.0
        total = sum(registro.duracao_minutos for registro in registros)
        return round(total / len(registros), 2)

    def top_clientes_mais_atendidos(self, limite: int = 5) -> list[dict[str, object]]:
        """Retorna top clientes mais atendidos usando merge sort."""
        contagens: dict[int, int] = {}
        for registro in self.historico:
            contagens[registro.cliente_id] = contagens.get(registro.cliente_id, 0) + 1

        linhas = []
        for cliente_id, total in contagens.items():
            cliente = self.buscar_cliente(cliente_id)
            linhas.append(
                {
                    "cliente_id": cliente_id,
                    "nome": cliente.nome if cliente else "Cliente removido",
                    "total_atendimentos": total,
                }
            )

        ordenados = merge_sort(
            linhas,
            chave=lambda item: (
                int(item["total_atendimentos"]),
                -int(item["cliente_id"]),
            ),
            reverso=True,
        )
        return ordenados[:limite]

    def alertas_espera_alta(
        self,
        limite_minutos: int | str,
        agora: datetime | None = None,
    ) -> list[dict[str, object]]:
        """Lista atendimentos aguardando acima do limite."""
        limite = validar_duracao(limite_minutos)
        momento = agora or datetime.now()
        alertas: list[dict[str, object]] = []

        filas = [
            ("prioridade", list(self.fila_prioridade)),
            ("comum", list(self.fila_comum)),
        ]
        for nome_fila, fila in filas:
            for solicitacao in fila:
                espera = int((momento - solicitacao.aberto_em).total_seconds() // 60)
                if espera >= limite:
                    cliente = self.buscar_cliente(solicitacao.cliente_id)
                    alertas.append(
                        {
                            "fila": nome_fila,
                            "atendimento_id": solicitacao.id_atendimento,
                            "cliente_id": solicitacao.cliente_id,
                            "cliente": cliente.nome if cliente else "Cliente removido",
                            "espera_minutos": max(0, espera),
                        }
                    )
        return alertas

    def listar_clientes_ordenados(self) -> list[Cliente]:
        """Retorna clientes ordenados por id."""
        return list(self.clientes_por_id)

    def listar_atendentes(self) -> list[Atendente]:
        """Retorna atendentes cadastrados."""
        return list(self.atendentes)

    def listar_filas(self) -> dict[str, list[SolicitacaoAtendimento]]:
        """Retorna filas comum e prioridade."""
        return {
            "prioridade": list(self.fila_prioridade),
            "comum": list(self.fila_comum),
        }

    def para_dict(self) -> dict[str, object]:
        """Serializa estado do sistema."""
        return {
            "clientes": [
                cliente.para_dict()
                for cliente in self.clientes_temporarios
            ],
            "atendentes": [
                atendente.para_dict()
                for atendente in self.atendentes
            ],
            "fila_prioridade": [
                item.para_dict()
                for item in self.fila_prioridade
            ],
            "fila_comum": [
                item.para_dict()
                for item in self.fila_comum
            ],
            "em_atendimento": [
                item.para_dict()
                for item in self.em_atendimento.values()
            ],
            "historico": [
                registro.para_dict()
                for registro in self.historico
            ],
            "proximo_atendimento_id": self.proximo_atendimento_id,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, object]) -> "SistemaAtendimento":
        """Cria sistema a partir do estado persistido."""
        sistema = cls()
        for item in dados.get("clientes", []):
            sistema.cadastrar_cliente(Cliente.de_dict(item))
        for item in dados.get("atendentes", []):
            sistema.cadastrar_atendente(Atendente.de_dict(item))
        for item in dados.get("fila_prioridade", []):
            sistema.fila_prioridade.append(SolicitacaoAtendimento.de_dict(item))
        for item in dados.get("fila_comum", []):
            sistema.fila_comum.append(SolicitacaoAtendimento.de_dict(item))
        for item in dados.get("em_atendimento", []):
            atendimento = AtendimentoEmAndamento.de_dict(item)
            sistema.em_atendimento[atendimento.atendente_id] = atendimento
        for item in dados.get("historico", []):
            sistema.historico.append(RegistroAtendimento.de_dict(item))

        proximo = int(dados.get("proximo_atendimento_id", 1))
        maior_id = sistema._maior_id_atendimento()
        sistema.proximo_atendimento_id = max(proximo, maior_id + 1)
        return sistema

    def _obter_cliente(self, cliente_id: int | str) -> Cliente:
        cliente = self.buscar_cliente(cliente_id)
        if cliente is None:
            raise ValueError("Cliente nao encontrado.")
        return cliente

    def _obter_atendente(self, atendente_id: int | str) -> Atendente:
        atendente = self.buscar_atendente(atendente_id)
        if atendente is None:
            raise ValueError("Atendente nao encontrado.")
        return atendente

    def _cliente_tem_atendimento_aberto(self, cliente_id: int) -> bool:
        return cliente_id in self._ids_clientes_com_atendimento_aberto()

    def _ids_clientes_com_atendimento_aberto(self) -> set[int]:
        ids = {item.cliente_id for item in self.fila_prioridade}
        ids.update(item.cliente_id for item in self.fila_comum)
        ids.update(item.cliente_id for item in self.em_atendimento.values())
        return ids

    def _filtrar_por_data(
        self,
        registros: list[RegistroAtendimento],
        data_inicio: datetime | None,
        data_fim: datetime | None,
    ) -> list[RegistroAtendimento]:
        filtrados = registros
        if data_inicio is not None:
            filtrados = [
                registro
                for registro in filtrados
                if registro.finalizado_em.date() >= data_inicio.date()
            ]
        if data_fim is not None:
            filtrados = [
                registro
                for registro in filtrados
                if registro.finalizado_em.date() <= data_fim.date()
            ]
        return filtrados

    def _maior_id_atendimento(self) -> int:
        ids = [item.id_atendimento for item in self.fila_prioridade]
        ids.extend(item.id_atendimento for item in self.fila_comum)
        ids.extend(item.id_atendimento for item in self.em_atendimento.values())
        ids.extend(item.id_atendimento for item in self.historico)
        return max(ids, default=0)
