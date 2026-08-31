"""
Módulo de Interface CLI: Produtos
Responsável por exibir o submenu interativo para gerenciamento de produtos e
direcionar as ações do usuário para as funções correspondentes.
"""

from funcoes_produtos import (
    cadastrar_produto,
    listar_produtos,
    consultar_produto,
    editar_produto,
    inativar_produto
)
from persistencia import inicializar_banco


def sub_menu_produtos() -> None:
    """
    Exibe o menu de opções para a gestão de produtos em loop interativo até que
    o usuário opte por voltar ao menu principal ou interrompa o programa.
    """
    # Garante que o banco e as tabelas estejam acessíveis
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 35)
            print("       GESTÃO DE PRODUTOS          ")
            print("=" * 35)
            print("1. Cadastrar Produto")
            print("2. Listar Todos os Produtos")
            print("3. Consultar Produto por Nome")
            print("4. Editar / Alterar Produto")
            print("5. Inativar Produto") 
            print("6. Voltar ao Menu Principal")
            print("-" * 35)

            opcao = input("Digite o número da opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nRetornando ao menu principal.")
            break

        match opcao:
            case "1":
                cadastrar_produto()
            case "2":
                listar_produtos()
            case "3":
                consultar_produto()
            case "4":
                editar_produto()
            case "5":
                inativar_produto()
            case "6":
                print("Voltando ao menu principal...")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 6.")
