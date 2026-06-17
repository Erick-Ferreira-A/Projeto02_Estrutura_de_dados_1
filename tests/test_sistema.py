import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from atendimento.arquivos import carregar_estado, salvar_estado
from atendimento.modelos import Atendente, Cliente
from atendimento.relatorios import (
    exportar_historico_csv,
    exportar_resumo_csv,
    exportar_top_clientes_csv,
)
from atendimento.servico import SistemaAtendimento


class SistemaAtendimentoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = SistemaAtendimento()
        self.sistema.cadastrar_cliente(
            Cliente(20, "Bruno", "2222-2222", prioridade=False)
        )
        self.sistema.cadastrar_cliente(
            Cliente(10, "Ana", "1111-1111", prioridade=True)
        )
        self.sistema.cadastrar_cliente(
            Cliente(30, "Carla", "3333-3333", prioridade=False)
        )
        self.sistema.cadastrar_cliente(
            Cliente(40, "Diego", "4444-4444", prioridade=True)
        )
        self.sistema.cadastrar_atendente(Atendente(1, "Mariana"))
        self.sistema.cadastrar_atendente(Atendente(2, "Rafael"))

    def test_cadastro_mantem_vetor_ordenado_para_busca_binaria(self) -> None:
        ids = [cliente.id for cliente in self.sistema.listar_clientes_ordenados()]
        cliente = self.sistema.buscar_cliente(30)

        self.assertEqual(ids, [10, 20, 30, 40])
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nome, "Carla")

    def test_nao_permite_cliente_duplicado(self) -> None:
        with self.assertRaises(ValueError):
            self.sistema.cadastrar_cliente(Cliente(10, "Outra Ana", "9999"))

    def test_prioridade_chama_primeiro_mantendo_ordem_da_fila(self) -> None:
        base = datetime(2026, 6, 17, 9, 0)
        self.sistema.abrir_atendimento(20, aberto_em=base)
        self.sistema.abrir_atendimento(10, aberto_em=base + timedelta(minutes=1))
        self.sistema.abrir_atendimento(40, aberto_em=base + timedelta(minutes=2))

        primeiro = self.sistema.chamar_proximo(1, iniciado_em=base)
        segundo = self.sistema.chamar_proximo(2, iniciado_em=base)

        self.assertEqual(primeiro.cliente_id, 10)
        self.assertEqual(segundo.cliente_id, 40)

    def test_atendente_nao_atende_dois_clientes_ao_mesmo_tempo(self) -> None:
        self.sistema.abrir_atendimento(20)
        self.sistema.chamar_proximo(1)
        self.sistema.abrir_atendimento(30)

        with self.assertRaises(ValueError):
            self.sistema.chamar_proximo(1)

    def test_finalizacao_e_desfazer_usam_pilha(self) -> None:
        base = datetime(2026, 6, 17, 9, 0)
        self.sistema.abrir_atendimento(20, aberto_em=base)
        self.sistema.chamar_proximo(1, iniciado_em=base + timedelta(minutes=5))
        registro = self.sistema.finalizar_atendimento(
            1,
            18,
            finalizado_em=base + timedelta(minutes=23),
        )
        desfeito = self.sistema.desfazer_ultima_finalizacao()

        self.assertEqual(registro.id_atendimento, desfeito.id_atendimento)
        self.assertEqual(len(self.sistema.historico), 0)
        self.assertIn(1, self.sistema.em_atendimento)

    def test_remove_clientes_inativos_com_lista_encadeada(self) -> None:
        self.sistema.desativar_cliente(30)
        removidos = self.sistema.remover_clientes_inativos()

        self.assertEqual([cliente.id for cliente in removidos], [30])
        self.assertIsNone(self.sistema.buscar_cliente(30))
        self.assertIsNone(self.sistema.clientes_encadeados.buscar(30))

    def test_nao_desativa_cliente_com_atendimento_aberto(self) -> None:
        self.sistema.abrir_atendimento(20)

        with self.assertRaises(ValueError):
            self.sistema.desativar_cliente(20)

    def test_relatorios_media_top_e_alerta(self) -> None:
        base = datetime(2026, 6, 17, 9, 0)
        self._finalizar_cliente(20, 1, 10, base)
        self._finalizar_cliente(20, 1, 20, base + timedelta(hours=1))
        self._finalizar_cliente(10, 2, 30, base + timedelta(hours=2))
        self.sistema.abrir_atendimento(30, aberto_em=base)

        media = self.sistema.tempo_medio_atendimento()
        top = self.sistema.top_clientes_mais_atendidos()
        alertas = self.sistema.alertas_espera_alta(
            15,
            agora=base + timedelta(minutes=20),
        )

        self.assertEqual(media, 20.0)
        self.assertEqual(top[0]["cliente_id"], 20)
        self.assertEqual(alertas[0]["cliente_id"], 30)

    def test_persistencia_e_exportacao_csv(self) -> None:
        base = datetime(2026, 6, 17, 9, 0)
        self._finalizar_cliente(20, 1, 12, base)

        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            estado = raiz / "estado.json"
            historico = raiz / "historico.csv"
            resumo = raiz / "resumo.csv"
            top = raiz / "top.csv"

            salvar_estado(estado, self.sistema)
            carregado = carregar_estado(estado)
            exportar_historico_csv(historico, carregado.historico)
            exportar_resumo_csv(resumo, carregado)
            exportar_top_clientes_csv(top, carregado)

            self.assertTrue(historico.exists())
            self.assertTrue(resumo.exists())
            self.assertTrue(top.exists())
            self.assertEqual(len(carregado.historico), 1)

    def _finalizar_cliente(
        self,
        cliente_id: int,
        atendente_id: int,
        duracao: int,
        base: datetime,
    ) -> None:
        self.sistema.abrir_atendimento(cliente_id, aberto_em=base)
        self.sistema.chamar_proximo(
            atendente_id,
            iniciado_em=base + timedelta(minutes=5),
        )
        self.sistema.finalizar_atendimento(
            atendente_id,
            duracao,
            finalizado_em=base + timedelta(minutes=5 + duracao),
        )


if __name__ == "__main__":
    unittest.main()
