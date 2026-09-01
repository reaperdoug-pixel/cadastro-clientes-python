"""
DEGEHUB ERP • Módulo de Interface CLI: Clientes
Responsável por exibir o submenu interativo para gerenciamento de clientes e
direcionar as ações do usuário para as funções correspondentes.
"""

from funcoes_clientes import (
    cadastrar_cliente,
    listar_clientes,
    consultar_cliente,
    editar_cliente,
    excluir_cliente
)
from persistencia import inicializar_banco


def sub_menu_clientes() -> None:
    """
    Exibe o menu de opções para a gestão de clientes em loop interativo até que
    o usuário opte por voltar ao menu principal ou interrompa o programa.
    """
    # Garante que o banco e as tabelas estejam acessíveis
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 46)
            print("         DEGEHUB ERP | GESTÃO DE CLIENTES     ")
            print("=" * 46)
            print("1. Cadastrar Cliente")
            print("2. Listar Todos os Clientes")
            print("3. Consultar Cliente por Nome")
            print("4. Editar Cliente")
            print("5. Inativar Cliente (Soft Delete)") 
            print("6. Voltar ao Menu Principal")
            print("-" * 46)

            opcao = input("Digite o número da opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nRetornando ao menu principal.")
            break

        match opcao:
            case "1":
                cadastrar_cliente()
            case "2":
                listar_clientes()
            case "3":
                consultar_cliente()
            case "4":
                editar_cliente()
            case "5":
                excluir_cliente()
            case "6":
                print("Voltando ao menu principal...")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 6.")