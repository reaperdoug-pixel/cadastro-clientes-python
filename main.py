"""
DEGEHUB ERP • Ponto de Entrada Principal (Main)
Plataforma integrada de gestão empresarial multi-filiais:
Clientes, Fornecedores, Estoque, Kardex e Centros de Distribuição.
"""

from menu_clientes import sub_menu_clientes
from menu_fornecedores import sub_menu_fornecedores
from menu_produtos import sub_menu_estoque
from menu_filiais import sub_menu_filiais
from menu_admin import sub_menu_admin
from funcoes_admin import criar_administrador_inicial
import sessao
from persistencia import inicializar_banco


def menu_principal() -> None:
    """
    Controla o fluxo do menu principal do DegeHub ERP em um loop contínuo,
    inicializando o banco de dados e roteando para os módulos de gestão.
    """
    # Garante que o banco sistema.db e todas as tabelas existam ao abrir o sistema
    inicializar_banco()
    criar_administrador_inicial()

    while True:
        try:
            print("\n" + "=" * 52)
            print("         DEGEHUB ERP • SISTEMA DE GESTÃO         ")
            print("               Multi-Filiais v2.0               ")
            print("=" * 52)
            print("1. Gestão de Clientes")
            print("2. Gestão de Fornecedores")
            print("3. Gestão de Estoque")
            print("4. Gestão de Filiais e Depósitos (CD)")
            print("5. Admin")
            print("6. Sair do Sistema")
            print("-" * 52)

            opcao = input("Digite a opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaindo do DegeHub ERP... Até logo!")
            break

        match opcao:
            case "1":
                if sessao.possui_permissao("ADMIN"):
                    sub_menu_clientes()
                else:
                    print("Acesso restrito a administradores.")
            case "2":
                if sessao.possui_permissao("ADMIN"):
                    sub_menu_fornecedores()
                else:
                    print("Acesso restrito a administradores.")
            case "3":
                if sessao.possui_permissao("ADMIN", "ESTOQUISTA", "CONSULTA"):
                    sub_menu_estoque()
                else:
                    print("Faça login no menu Admin para acessar o estoque.")
            case "4":
                if sessao.possui_permissao("ADMIN"):
                    sub_menu_filiais()
                else:
                    print("Acesso restrito a administradores.")
            case "5":
                sub_menu_admin()
            case "6":
                print("\nSaindo do DegeHub ERP... Até logo!")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 6.")


if __name__ == "__main__":
    menu_principal()
