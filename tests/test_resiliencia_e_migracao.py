import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import persistencia


class PersistenciaCriticaTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database = persistencia.NOME_BANCO
        persistencia.NOME_BANCO = os.path.join(self.temp_dir.name, "teste.db")
        persistencia.inicializar_banco()
        with persistencia.transacao_banco() as cursor:
            cursor.execute(
                "INSERT INTO fornecedores (cnpj, razao_social, nome_fantasia) VALUES (?, ?, ?)",
                ("12.345.678/0001-90", "Fornecedor Teste", "Teste"),
            )
            cursor.execute(
                "INSERT INTO usuarios (login, senha_hash, data_criacao, permissoes) VALUES (?, ?, ?, ?)",
                ("admin", "hash", "2026-09-12", "ADMIN"),
            )
        self.produto_id = persistencia.salvar_produto_completo(
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
            {"quantidade": 2, "estoque_minimo": 0, "data_atualizacao": "2026-09-12"},
        )

    def tearDown(self):
        persistencia.NOME_BANCO = self.original_database
        self.temp_dir.cleanup()

    def _dados_nota(self, numero="NF-001"):
        return {
            "numero_nota": numero,
            "fornecedor_id": 1,
            "loja_id": 1,
            "usuario_id": 1,
            "data_entrada": "2026-09-12 10:00:00",
            "data_criacao": "2026-09-12 10:00:00",
        }

    def test_nota_invalida_reverte_cabecalho_itens_saldos_e_kardex(self):
        sucesso, _ = persistencia.registrar_nota_entrada_banco(
            self._dados_nota(),
            [{"produto_id": self.produto_id, "quantidade": 3}, {"produto_id": 999, "quantidade": 1}],
        )
        self.assertFalse(sucesso)
        with persistencia.transacao_banco() as cursor:
            self.assertEqual(cursor.execute("SELECT COUNT(*) FROM notas_entrada").fetchone()[0], 0)
            self.assertEqual(cursor.execute("SELECT COUNT(*) FROM itens_notas_entrada").fetchone()[0], 0)
            self.assertEqual(cursor.execute("SELECT quantidade FROM saldos WHERE produto_id = ? AND loja_id = 1", (self.produto_id,)).fetchone()[0], 2)
            self.assertEqual(cursor.execute("SELECT COUNT(*) FROM movimentacoes_estoque WHERE produto_id = ?", (self.produto_id,)).fetchone()[0], 1)

    def test_numero_de_nota_unico_nao_duplica_estoque(self):
        self.assertTrue(persistencia.registrar_nota_entrada_banco(
            self._dados_nota(), [{"produto_id": self.produto_id, "quantidade": 3}]
        )[0])
        self.assertFalse(persistencia.registrar_nota_entrada_banco(
            self._dados_nota(), [{"produto_id": self.produto_id, "quantidade": 3}]
        )[0])
        with persistencia.transacao_banco() as cursor:
            saldo = cursor.execute(
                "SELECT quantidade FROM saldos WHERE produto_id = ? AND loja_id = 1", (self.produto_id,)
            ).fetchone()[0]
        self.assertEqual(saldo, 5)

    def test_migracao_converte_promocao_legada_uma_unica_vez(self):
        with persistencia.transacao_banco() as cursor:
            cursor.execute("UPDATE precos SET preco_promocao = 15 WHERE produto_id = ? AND loja_id = 1", (self.produto_id,))
        persistencia.inicializar_banco()
        persistencia.inicializar_banco()
        with persistencia.transacao_banco() as cursor:
            preco_legado = cursor.execute(
                "SELECT preco_promocao FROM precos WHERE produto_id = ? AND loja_id = 1", (self.produto_id,)
            ).fetchone()[0]
            promocoes = cursor.execute(
                "SELECT COUNT(*) FROM promocoes WHERE numero_promocao = ?", (f"LEGADA-{self.produto_id}-1",)
            ).fetchone()[0]
        self.assertEqual(preco_legado, 0)
        self.assertEqual(promocoes, 1)

    def test_conexao_tenta_novamente_apos_trava_temporaria(self):
        conexao = sqlite3.connect(":memory:")
        with patch("persistencia.sqlite3.connect", side_effect=[sqlite3.OperationalError("locked"), conexao]), patch(
            "persistencia.time.sleep"
        ) as sleep:
            resultado = persistencia.obter_conexao()
        self.assertIs(resultado, conexao)
        sleep.assert_called_once_with(persistencia.RETRY_DELAY)
        resultado.close()
