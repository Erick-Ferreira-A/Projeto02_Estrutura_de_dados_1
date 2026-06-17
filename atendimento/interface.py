"""Interface de terminal do sistema."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from atendimento.arquivos import carregar_estado, salvar_estado
from atendimento.logs import registrar_log
from atendimento.modelos import Atendente, Cliente, RegistroAtendimento
from atendimento.relatorios import (
    exportar_historico_csv,
    exportar_resumo_csv,
    exportar_top_clientes_csv,
)
from atendimento.servico import SistemaAtendimento


TAMANHO_PAGINA = 8


def executar_app(base_dir: Path) -> None:
    """Executa o menu principal."""
    arquivo_dados = base_dir / "dados" / "estado.json"
    arquivo_log = base_dir / "logs" / "operacoes.log"
    pasta_exports = base_dir / "exports"

    try:
        sistema = carregar_estado(arquivo_dados)
    except ValueError as erro:
        print(f"Erro ao carregar dados: {erro}")
        sistema = SistemaAtendimento()

    registrar_log(arquivo_log, "Sistema iniciado")
    continuar = True
    while continuar:
        opcao = input(_menu()).strip()
        continuar = _executar_opcao(
            opcao,
            sistema,
            arquivo_dados,
            arquivo_log,
            pasta_exports,
        )
        if continuar:
            _pausar()


def _menu() -> str:
    return """
========== Sistema de Atendimento e Analise ==========
1. Cadastrar cliente
2. Cadastrar atendente
3. Abrir atendimento
4. Chamar proximo atendimento
5. Finalizar atendimento
6. Historico por cliente
7. Desfazer ultima finalizacao
8. Desativar cliente
9. Remover clientes inativos
10. Relatorio de tempo medio
11. Exportar relatorios CSV
12. Buscar cliente por id
13. Listar filas
14. Listar clientes
15. Top 5 clientes mais atendidos
16. Alertas de espera alta
17. Salvar dados
18. Carregar dados
0. Sair
======================================================
Escolha uma opcao: """


def _executar_opcao(
    opcao: str,
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
    pasta_exports: Path,
) -> bool:
    acoes = {
        "1": lambda: _cadastrar_cliente(sistema, arquivo_dados, arquivo_log),
        "2": lambda: _cadastrar_atendente(sistema, arquivo_dados, arquivo_log),
        "3": lambda: _abrir_atendimento(sistema, arquivo_dados, arquivo_log),
        "4": lambda: _chamar_proximo(sistema, arquivo_dados, arquivo_log),
        "5": lambda: _finalizar_atendimento(sistema, arquivo_dados, arquivo_log),
        "6": lambda: _historico_cliente(sistema),
        "7": lambda: _desfazer_finalizacao(sistema, arquivo_dados, arquivo_log),
        "8": lambda: _desativar_cliente(sistema, arquivo_dados, arquivo_log),
        "9": lambda: _remover_inativos(sistema, arquivo_dados, arquivo_log),
        "10": lambda: _relatorio_tempo_medio(sistema),
        "11": lambda: _exportar_relatorios(sistema, pasta_exports, arquivo_log),
        "12": lambda: _buscar_cliente(sistema),
        "13": lambda: _listar_filas(sistema),
        "14": lambda: _listar_clientes(sistema),
        "15": lambda: _top_clientes(sistema),
        "16": lambda: _alertas_espera(sistema),
        "17": lambda: _salvar(sistema, arquivo_dados, arquivo_log),
        "18": lambda: _carregar_manual(sistema, arquivo_dados, arquivo_log),
    }

    if opcao == "0":
        salvar_estado(arquivo_dados, sistema)
        registrar_log(arquivo_log, "Sistema encerrado")
        print("Dados salvos. Ate logo!")
        return False

    acao = acoes.get(opcao)
    if acao is None:
        print("Opcao invalida.")
        return True

    try:
        acao()
    except ValueError as erro:
        print(f"Erro: {erro}")
    return True


def _cadastrar_cliente(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    print("\nCadastro de cliente")
    cliente = Cliente(
        id=_ler_inteiro("Id do cliente: ", minimo=1),
        nome=_ler_texto("Nome: "),
        telefone=_ler_texto("Telefone: "),
        prioridade=_ler_bool("Cliente tem prioridade? [s/N]: "),
    )
    sistema.cadastrar_cliente(cliente)
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(arquivo_log, f"Cliente cadastrado: {cliente.id}")
    print("Cliente cadastrado com sucesso.")


def _cadastrar_atendente(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    print("\nCadastro de atendente")
    atendente = Atendente(
        id=_ler_inteiro("Id do atendente: ", minimo=1),
        nome=_ler_texto("Nome: "),
    )
    sistema.cadastrar_atendente(atendente)
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(arquivo_log, f"Atendente cadastrado: {atendente.id}")
    print("Atendente cadastrado com sucesso.")


def _abrir_atendimento(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    print("\nAbertura de atendimento")
    cliente_id = _ler_inteiro("Id do cliente: ", minimo=1)
    solicitacao = sistema.abrir_atendimento(cliente_id)
    fila = "prioridade" if solicitacao.prioridade else "comum"
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(
        arquivo_log,
        f"Atendimento aberto: {solicitacao.id_atendimento}",
    )
    print(f"Atendimento {solicitacao.id_atendimento} entrou na fila {fila}.")


def _chamar_proximo(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    print("\nChamar proximo atendimento")
    atendente_id = _ler_inteiro("Id do atendente: ", minimo=1)
    atendimento = sistema.chamar_proximo(atendente_id)
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(
        arquivo_log,
        f"Atendimento chamado: {atendimento.id_atendimento}",
    )
    print(
        f"Atendimento {atendimento.id_atendimento} iniciado "
        f"para o cliente {atendimento.cliente_id}."
    )


def _finalizar_atendimento(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    print("\nFinalizacao de atendimento")
    atendente_id = _ler_inteiro("Id do atendente: ", minimo=1)
    duracao = _ler_inteiro("Duracao em minutos: ", minimo=1)
    registro = sistema.finalizar_atendimento(atendente_id, duracao)
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(
        arquivo_log,
        f"Atendimento finalizado: {registro.id_atendimento}",
    )
    print(
        f"Atendimento {registro.id_atendimento} finalizado. "
        f"Espera: {registro.espera_minutos} min."
    )


def _historico_cliente(sistema: SistemaAtendimento) -> None:
    print("\nHistorico por cliente")
    cliente_id = _ler_inteiro("Id do cliente: ", minimo=1)
    data_inicio = _ler_data_opcional("Data inicial YYYY-MM-DD (opcional): ")
    data_fim = _ler_data_opcional("Data final YYYY-MM-DD (opcional): ")
    registros = sistema.historico_por_cliente(cliente_id, data_inicio, data_fim)
    _mostrar_historico(registros)


def _desfazer_finalizacao(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    registro = sistema.desfazer_ultima_finalizacao()
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(
        arquivo_log,
        f"Finalizacao desfeita: {registro.id_atendimento}",
    )
    print(f"Finalizacao do atendimento {registro.id_atendimento} desfeita.")


def _desativar_cliente(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    print("\nDesativar cliente")
    cliente_id = _ler_inteiro("Id do cliente: ", minimo=1)
    cliente = sistema.desativar_cliente(cliente_id)
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(arquivo_log, f"Cliente desativado: {cliente.id}")
    print(f"Cliente {cliente.nome} marcado como inativo.")


def _remover_inativos(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    removidos = sistema.remover_clientes_inativos()
    _salvar(sistema, arquivo_dados, arquivo_log, silencioso=True)
    registrar_log(arquivo_log, f"Clientes inativos removidos: {len(removidos)}")
    if not removidos:
        print("Nenhum cliente inativo para remover.")
        return

    print("Clientes removidos:")
    _mostrar_clientes(removidos, paginar=False)


def _relatorio_tempo_medio(sistema: SistemaAtendimento) -> None:
    print("\nTempo medio de atendimento")
    data_inicio = _ler_data_opcional("Data inicial YYYY-MM-DD (opcional): ")
    data_fim = _ler_data_opcional("Data final YYYY-MM-DD (opcional): ")
    media = sistema.tempo_medio_atendimento(data_inicio, data_fim)
    print(f"Tempo medio: {media:.2f} minuto(s).")


def _exportar_relatorios(
    sistema: SistemaAtendimento,
    pasta_exports: Path,
    arquivo_log: Path,
) -> None:
    historico = pasta_exports / "historico.csv"
    resumo = pasta_exports / "resumo.csv"
    top_clientes = pasta_exports / "top_clientes.csv"
    exportar_historico_csv(historico, sistema.historico)
    exportar_resumo_csv(resumo, sistema)
    exportar_top_clientes_csv(top_clientes, sistema)
    registrar_log(arquivo_log, "Relatorios CSV exportados")
    print("Relatorios exportados:")
    print(f"- {historico}")
    print(f"- {resumo}")
    print(f"- {top_clientes}")


def _buscar_cliente(sistema: SistemaAtendimento) -> None:
    print("\nBusca rapida por cliente")
    cliente_id = _ler_inteiro("Id do cliente: ", minimo=1)
    cliente = sistema.buscar_cliente(cliente_id)
    if cliente is None:
        print("Cliente nao encontrado.")
    else:
        _mostrar_clientes([cliente], paginar=False)


def _listar_filas(sistema: SistemaAtendimento) -> None:
    filas = sistema.listar_filas()
    print("\nFila de prioridade")
    _mostrar_fila(filas["prioridade"])
    print("\nFila comum")
    _mostrar_fila(filas["comum"])
    print("\nAtendimentos em andamento")
    if not sistema.em_atendimento:
        print("Nenhum atendimento em andamento.")
    else:
        for atendimento in sistema.em_atendimento.values():
            print(
                f"Atendimento {atendimento.id_atendimento} | "
                f"Cliente {atendimento.cliente_id} | "
                f"Atendente {atendimento.atendente_id}"
            )


def _listar_clientes(sistema: SistemaAtendimento) -> None:
    print("\nClientes ordenados por id")
    _mostrar_clientes(sistema.listar_clientes_ordenados())


def _top_clientes(sistema: SistemaAtendimento) -> None:
    linhas = sistema.top_clientes_mais_atendidos()
    if not linhas:
        print("Nao ha atendimentos finalizados.")
        return

    print(f"{'Id':<8} {'Nome':<30} {'Atendimentos':>13}")
    print("-" * 55)
    for linha in linhas:
        print(
            f"{linha['cliente_id']:<8} "
            f"{str(linha['nome']):<30.30} "
            f"{linha['total_atendimentos']:>13}"
        )


def _alertas_espera(sistema: SistemaAtendimento) -> None:
    print("\nAlertas de espera alta")
    limite = _ler_inteiro("Limite em minutos: ", minimo=1)
    alertas = sistema.alertas_espera_alta(limite)
    if not alertas:
        print("Nenhum alerta de espera alta.")
        return

    print(f"{'Fila':<12} {'Atend.':<8} {'Cliente':<30} {'Espera':>8}")
    print("-" * 62)
    for alerta in alertas:
        print(
            f"{alerta['fila']:<12} "
            f"{alerta['atendimento_id']:<8} "
            f"{str(alerta['cliente']):<30.30} "
            f"{alerta['espera_minutos']:>8}"
        )


def _salvar(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
    silencioso: bool = False,
) -> None:
    salvar_estado(arquivo_dados, sistema)
    if not silencioso:
        registrar_log(arquivo_log, "Dados salvos manualmente")
        print(f"Dados salvos em {arquivo_dados}.")


def _carregar_manual(
    sistema: SistemaAtendimento,
    arquivo_dados: Path,
    arquivo_log: Path,
) -> None:
    carregado = carregar_estado(arquivo_dados)
    sistema.__dict__.update(carregado.__dict__)
    registrar_log(arquivo_log, "Dados carregados manualmente")
    print("Dados carregados com sucesso.")


def _mostrar_clientes(clientes: list[Cliente], paginar: bool = True) -> None:
    if not clientes:
        print("Nenhum cliente encontrado.")
        return

    print(f"{'Id':<8} {'Nome':<30} {'Telefone':<18} {'Prior.':<8} {'Ativo':<7}")
    print("-" * 78)
    for indice, cliente in enumerate(clientes, start=1):
        print(
            f"{cliente.id:<8} "
            f"{cliente.nome:<30.30} "
            f"{cliente.telefone:<18.18} "
            f"{_sim_nao(cliente.prioridade):<8} "
            f"{_sim_nao(cliente.ativo):<7}"
        )
        if paginar and indice % TAMANHO_PAGINA == 0 and indice < len(clientes):
            input("-- ENTER para proxima pagina --")


def _mostrar_fila(fila: list[object]) -> None:
    if not fila:
        print("Fila vazia.")
        return

    print(f"{'Atend.':<8} {'Cliente':<10} {'Aberto em':<20} {'Prior.':<8}")
    print("-" * 52)
    for item in fila:
        print(
            f"{item.id_atendimento:<8} "
            f"{item.cliente_id:<10} "
            f"{item.aberto_em.strftime('%Y-%m-%d %H:%M'):<20} "
            f"{_sim_nao(item.prioridade):<8}"
        )


def _mostrar_historico(registros: list[RegistroAtendimento]) -> None:
    if not registros:
        print("Nenhum atendimento encontrado.")
        return

    print(
        f"{'Atend.':<8} {'Cliente':<8} {'Atend.':<8} "
        f"{'Finalizado':<20} {'Dur.':>6} {'Espera':>8}"
    )
    print("-" * 68)
    for registro in registros:
        print(
            f"{registro.id_atendimento:<8} "
            f"{registro.cliente_id:<8} "
            f"{registro.atendente_id:<8} "
            f"{registro.finalizado_em.strftime('%Y-%m-%d %H:%M'):<20} "
            f"{registro.duracao_minutos:>6} "
            f"{registro.espera_minutos:>8}"
        )


def _ler_texto(rotulo: str) -> str:
    while True:
        valor = input(rotulo).strip()
        if valor:
            return valor
        print("Entrada obrigatoria. Tente novamente.")


def _ler_inteiro(rotulo: str, minimo: int | None = None) -> int:
    while True:
        valor = input(rotulo).strip()
        try:
            numero = int(valor)
        except ValueError:
            print("Digite um numero inteiro valido.")
            continue

        if minimo is not None and numero < minimo:
            print(f"Digite um valor maior ou igual a {minimo}.")
            continue
        return numero


def _ler_bool(rotulo: str) -> bool:
    resposta = input(rotulo).strip().lower()
    return resposta in {"s", "sim", "1", "true"}


def _ler_data_opcional(rotulo: str) -> datetime | None:
    valor = input(rotulo).strip()
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        raise ValueError("Data deve estar no formato YYYY-MM-DD.")


def _sim_nao(valor: bool) -> str:
    return "sim" if valor else "nao"


def _pausar() -> None:
    input("\nPressione ENTER para continuar...")
