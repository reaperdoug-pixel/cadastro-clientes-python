import os
import tempfile
import unittest
from unittest.mock import patch

import funcoes_admin
import persistencia
import sessao


class AdministracaoTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database = persistencia.NOME_BANCO
        persistencia.NOME_BANCO = os.path.join(self.temp_dir.name, "teste.db")
        persistencia.inicializar_banco()
        sessao.encerrar()

    def tearDown(self):
        sessao.encerrar()
        persistencia.NOME_BANCO = self.original_database
        self.temp_dir.cleanup()

    def test_hash_da_senha_nao_expoe_valor_e_valida_corretamente(self):
        senha_hash = funcoes_admin.gerar_hash_senha("senha-segura")
        self.assertNotIn("senha-segura", senha_hash)
        self.assertTrue(funcoes_admin.validar_senha("senha-segura", senha_hash))
        self.assertFalse(funcoes_admin.validar_senha("senha-incorreta", senha_hash))

    def test_login_rejeita_usuario_inativo(self):
        usuario_id = persistencia.criar_usuario_banco(
            "inativo", funcoes_admin.gerar_hash_senha("senha-segura"), "ADMIN", "2026-09-12"
        )
        persistencia.inativar_usuario_banco(usuario_id, "2026-09-12 10:00:00")
        with patch("builtins.input", return_value="inativo"), patch(
            "getpass.getpass", return_value="senha-segura"
        ), patch("builtins.print"):
            self.assertFalse(funcoes_admin.login())
        self.assertIsNone(sessao.usuario_atual)

    def test_criacao_do_primeiro_administrador_autentica_a_sessao(self):
        with patch("builtins.input", return_value="admin"), patch(
            "getpass.getpass", side_effect=["senha-segura", "senha-segura"]
        ), patch("builtins.print"):
            self.assertTrue(funcoes_admin.criar_administrador_inicial())
        self.assertEqual(sessao.usuario_atual["login"], "admin")
        self.assertEqual(sessao.usuario_atual["permissoes"], "ADMIN")

    def test_usuario_da_sessao_nao_pode_ser_inativado(self):
        usuario_id = persistencia.criar_usuario_banco(
            "admin", funcoes_admin.gerar_hash_senha("senha-segura"), "ADMIN", "2026-09-12"
        )
        sessao.iniciar(usuario_id, "admin", "ADMIN")
        with patch("builtins.input", return_value=str(usuario_id)), patch(
            "funcoes_admin.listar_usuarios"
        ), patch("builtins.print") as output:
            funcoes_admin.inativar_usuario()
        self.assertIsNotNone(persistencia.buscar_usuario_por_login("admin"))
        output.assert_any_call("Não é permitido inativar o usuário da sessão atual.")
