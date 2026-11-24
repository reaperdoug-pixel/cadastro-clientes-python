import unittest
from unittest.mock import patch

import main
import menu_produtos
import sessao


class AcessoMenusTestCase(unittest.TestCase):
    def tearDown(self):
        sessao.encerrar()

    def test_consulta_so_acessa_estoque_no_menu_principal(self):
        sessao.iniciar(1, "consulta", "CONSULTA")
        with patch("builtins.input", side_effect=["1", "3", "6"]), patch(
            "main.inicializar_banco"
        ), patch("main.criar_administrador_inicial"), patch(
            "main.sub_menu_clientes"
        ) as clientes, patch("main.sub_menu_estoque") as estoque, patch("builtins.print"):
            main.menu_principal()
        clientes.assert_not_called()
        estoque.assert_called_once_with()

    def test_consulta_recebe_apenas_opcoes_de_leitura_no_estoque(self):
        sessao.iniciar(1, "consulta", "CONSULTA")
        with patch("builtins.input", side_effect=["1", "3"]), patch(
            "menu_produtos.inicializar_banco"
        ), patch("menu_produtos.listar_produtos") as listar, patch(
            "menu_produtos.movimentar_estoque_produto"
        ) as movimentar:
            menu_produtos.sub_menu_estoque()
        listar.assert_called_once_with()
        movimentar.assert_not_called()
