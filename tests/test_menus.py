from unittest import TestCase
from unittest.mock import patch

import menu_filiais
import menu_produtos


class MenusTestCase(TestCase):
    def test_menu_estoque_direciona_para_submenu_produtos(self):
        with patch("builtins.input", side_effect=["1", "7"]), \
             patch("menu_produtos.inicializar_banco"), \
             patch("menu_produtos.existe_cd_ativo", return_value=False), \
             patch("menu_produtos.sub_menu_produtos") as produtos:
            menu_produtos.sub_menu_estoque()

        produtos.assert_called_once_with()


    def test_submenu_produtos_expoe_apenas_crud(self):
        with patch("builtins.input", side_effect=["1", "2", "3", "4", "5"]), \
             patch("menu_produtos.cadastrar_produto") as cadastrar, \
             patch("menu_produtos.listar_produtos") as listar, \
             patch("menu_produtos.editar_produto") as editar, \
             patch("menu_produtos.inativar_produto") as inativar:
            menu_produtos.sub_menu_produtos()

        cadastrar.assert_called_once_with()
        listar.assert_called_once_with()
        editar.assert_called_once_with()
        inativar.assert_called_once_with()


    def test_menu_filiais_retorna_na_opcao_seis(self):
        with patch("builtins.input", side_effect=["6"]), \
             patch("menu_filiais.inicializar_banco"):
            menu_filiais.sub_menu_filiais()
