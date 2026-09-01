"""
DEGEHUB ERP • Ponto de Entrada Principal (Main)
Plataforma integrada de gestão empresarial multi-filiais:
Clientes, Fornecedores, Produtos, Estoque Kardex e Centros de Distribuição.
"""

from menu_clientes import sub_menu_clientes
from menu_fornecedores import sub_menu_fornecedores
from menu_produtos import sub_menu_produtos
from menu_filiais import sub_menu_filiais
from persistencia import inicializar_banco


def menu_principal() -> None:
    """
    Controla o fluxo do menu principal do DegeHub ERP em um loop contínuo,
    inicializando o banco de dados e roteando para os módulos de gestão.
    """
    # Garante que o banco sistema.db e todas as tabelas existam ao abrir o sistema
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 52)
            print("         DEGEHUB ERP • SISTEMA DE GESTÃO         ")
            print("               Multi-Filiais v2.0               ")
            print("=" * 52)
            print("1. Gestão de Clientes")
            print("2. Gestão de Fornecedores")
            print("3. Gestão de Produtos e Estoque")
            print("4. Gestão de Filiais e Depósitos (CD)")
            print("5. Sair do Sistema")
            print("-" * 52)

            opcao = input("Digite a opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaindo do DegeHub ERP... Até logo!")
            break

        match opcao:
            case "1":
                sub_menu_clientes()
            case "2":
                sub_menu_fornecedores()
            case "3":
                sub_menu_produtos()
            case "4":
                sub_menu_filiais()
            case "5":
                print("\nSaindo do DegeHub ERP... Até logo!")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 5.")


if __name__ == "__main__":
    menu_principal()