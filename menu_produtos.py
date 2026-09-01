"""
Módulo de Interface CLI: Produtos
Responsável por exibir o submenu interativo para gerenciamento de produtos e
direcionar as ações do usuário para as funções correspondentes:
Cadastro, Listagem por Loja, Consulta Geral, Edição Cadastral,
Preços e Promoções por Loja, Movimentação de Estoque e Extrato Kardex.
"""

from funcoes_produtos import (
    cadastrar_produto,
    listar_produtos,
    consultar_produto,
    editar_produto,
    gerenciar_precos_promocoes,
    movimentar_estoque_produto,
    consultar_extrato_kardex,
    inativar_produto
)
from persistencia import inicializar_banco


def sub_menu_produtos() -> None:
    """
    Exibe o menu de opções para a gestão de produtos em loop interativo até que
    o usuário opte por voltar ao menu principal ou interrompa o programa.
    """
    # Garante que o banco e as tabelas estejam acessíveis e atualizados
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 48)
            print("     DEGEHUB ERP | GESTÃO DE PRODUTOS & ESTOQUE   ")
            print("=" * 48)
            print("1. Cadastrar Produto")
            print("2. Listar Produtos (por Filial/Loja)")
            print("3. Consultar Produto por Nome (Visão Geral)")
            print("4. Editar Dados Cadastrais do Produto")
            print("5. Gerenciar Preços e Promoções por Loja")
            print("6. Movimentar Estoque (Entrada/Saída/Ajuste)")
            print("7. Extrato de Movimentações de Estoque (Kardex)")
            print("8. Inativar Produto (Soft Delete)") 
            print("9. Voltar ao Menu Principal")
            print("-" * 45)

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
                gerenciar_precos_promocoes()
            case "6":
                movimentar_estoque_produto()
            case "7":
                consultar_extrato_kardex()
            case "8":
                inativar_produto()
            case "9":
                print("Voltando ao menu principal...")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 9.")
