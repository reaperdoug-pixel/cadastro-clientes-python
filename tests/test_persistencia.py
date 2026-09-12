import os
import tempfile
import unittest

import persistencia


class PersistenciaTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temp_dir.name, "teste.db")
        self.original_database = persistencia.NOME_BANCO
        persistencia.NOME_BANCO = self.database_path
        persistencia.inicializar_banco()

        with persistencia.transacao_banco() as cursor:
            cursor.execute(
                "INSERT INTO fornecedores (cnpj, razao_social, nome_fantasia) VALUES (?, ?, ?)",
                ("12.345.678/0001-90", "Fornecedor Teste", "Teste"),
            )

    def tearDown(self):
        persistencia.NOME_BANCO = self.original_database
        self.temp_dir.cleanup()

    def test_inicializacao_cria_tabelas_principais(self):
        with persistencia.transacao_banco() as cursor:
            tabelas = {
                linha[0]
                for linha in cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        esperadas = {
            "clientes", "fornecedores", "lojas", "produtos",
            "precos", "saldos", "movimentacoes_estoque", "usuarios",
            "promocoes", "notas_entrada", "itens_notas_entrada",
        }
        self.assertTrue(esperadas <= tabelas)

    def test_cliente_pode_ser_inativado_sem_apagar_registro(self):
        persistencia.salvar_cliente({
            "nome": "Cliente Teste",
            "idade": 30,
            "sexo": "O",
            "email": "cliente@teste.com",
            "telefone": "(11) 99999-9999",
        })
        cliente = persistencia.carregar_clientes()[0]
        persistencia.inativar_cliente(cliente[0])
        self.assertEqual(persistencia.carregar_clientes(), [])

        with persistencia.transacao_banco() as cursor:
            ativo = cursor.execute(
                "SELECT ativo FROM clientes WHERE id = ?", (cliente[0],)
            ).fetchone()[0]
        self.assertEqual(ativo, 0)

    def test_estoque_bloqueia_saida_maior_que_saldo(self):
        produto_id = self._criar_produto(quantidade=5)
        sucesso, _, saldo = persistencia.registrar_movimentacao_estoque_banco(
            produto_id, 1, "SAIDA", 6, "Teste de saldo", "2026-09-12T10:00:00"
        )
        self.assertFalse(sucesso)
        self.assertEqual(saldo, 5)

    def test_transferencia_atualiza_origem_destino_e_kardex(self):
        produto_id = self._criar_produto(quantidade=10)
        sucesso, mensagem = persistencia.transferir_estoque_entre_filiais_banco(
            produto_id, 1, 2, 4, "Distribuicao de teste", "2026-09-12T10:00:00"
        )
        self.assertTrue(sucesso, mensagem)
        saldos = {
            linha[0]: linha[3]
            for linha in persistencia.obter_saldos_produto_todas_lojas(produto_id)
        }
        self.assertEqual(saldos[1], 6)
        self.assertEqual(saldos[2], 4)
        self.assertEqual(len(persistencia.carregar_extrato_kardex_banco(produto_id)), 3)

    def test_nota_entrada_atualiza_saldo_e_kardex(self):
        usuario_id = persistencia.criar_usuario_banco("admin", "hash", "ADMIN", "2026-09-12")
        produto_id = self._criar_produto(quantidade=1)
        sucesso, mensagem = persistencia.registrar_nota_entrada_banco({
            "numero_nota": "NF-001", "fornecedor_id": 1, "loja_id": 1,
            "usuario_id": usuario_id, "data_entrada": "2026-09-12 10:00:00",
            "data_criacao": "2026-09-12 10:00:00",
        }, [{"produto_id": produto_id, "quantidade": 4}])
        self.assertTrue(sucesso, mensagem)
        self.assertEqual(persistencia.obter_saldos_produto_todas_lojas(produto_id)[0][3], 5)
        self.assertEqual(persistencia.carregar_extrato_kardex_banco(produto_id)[0][2], "ENTRADA_NOTA")

    def test_promocao_ativa_e_aplicada_ao_preco_da_loja(self):
        usuario_id = persistencia.criar_usuario_banco("precos", "hash", "ADMIN", "2026-09-12")
        produto_id = self._criar_produto()
        persistencia.criar_promocao_banco({
            "produto_id": produto_id, "loja_id": 1, "numero_promocao": "PROMO-1",
            "criacao_promocao": "2026-09-12", "preco_promocao": 15.0,
            "inicio_promocao": "2000-01-01", "fim_promocao": None,
            "data_alteracao_preco": "2026-09-12", "usuario_id": usuario_id,
        })
        self.assertEqual(persistencia.buscar_produto_por_id_banco(produto_id, 1)[5], 15.0)

    def _criar_produto(self, quantidade=0):
        return persistencia.salvar_produto_completo(
            {
                "fornecedor_id": 1,
                "nome": "Produto Teste",
                "categoria": "Teste",
                "data_cadastro": "2026-09-12",
                "data_alteracao": "2026-09-12",
            },
            {
                "loja_id": 1,
                "preco_custo": 10.0,
                "markup": 2.0,
                "preco_venda": 20.0,
                "preco_promocao": 0.0,
                "data_atualizacao": "2026-09-12",
            },
            {
                "quantidade": quantidade,
                "estoque_minimo": 0,
                "data_atualizacao": "2026-09-12",
            },
        )


if __name__ == "__main__":
    unittest.main()
