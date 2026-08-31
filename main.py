"""
Ponto de Entrada Principal (Main)
Responsável por iniciar o sistema, garantir a criação do banco de dados e exibir
o menu principal que redireciona o usuário para os módulos de Clientes, Fornecedores e Produtos.
"""

from menu_clientes import sub_menu_clientes
from menu_fornecedores import sub_menu_fornecedores
from menu_produtos import sub_menu_produtos
from persistencia import inicializar_banco

def menu_principal() -> None:
    """
    Controla o fluxo do menu principal do sistema em um loop contínuo,
    inicializando o banco de dados e roteando para os módulos de gestão.
    """
    # Garante que o banco sistema.db e todas as tabelas existam ao abrir o sistema
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 40)
            print("       SISTEMA DE GESTÃO - MAIN        ")
            print("=" * 40)
            print("1. Gestão de Clientes")
            print("2. Gestão de Fornecedores")
            print("3. Gestão de Produtos")
            print("4. Sair do Sistema")
            print("-" * 40)

            opcao = input("Digite a opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaindo do sistema... Até logo!")
            break

        match opcao:
            case "1":
                sub_menu_clientes()
            case "2":
                sub_menu_fornecedores()
            case "3":
                sub_menu_produtos()
            case "4":
                print("\nSaindo do sistema... Até logo!")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha 1, 2, 3 ou 4.")

if __name__ == "__main__":
    menu_principal()