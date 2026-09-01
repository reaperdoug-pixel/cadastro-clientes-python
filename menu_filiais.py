"""
Módulo de Interface CLI: Filiais e Centros de Distribuição
Responsável por exibir o submenu interativo para gerenciamento de filiais e CDs
e direcionar as ações do usuário para as funções correspondentes:
Cadastro, Listagem, Consulta com Balanço, Edição, Inativação e Transferência de Estoque.
"""

from funcoes_filiais import (
    cadastrar_filial,
    listar_filiais,
    consultar_filial,
    editar_filial,
    inativar_filial,
    transferir_estoque_filiais
)
from persistencia import inicializar_banco


def sub_menu_filiais() -> None:
    """
    Exibe o menu de opções para a gestão de filiais e CDs em loop interativo.
    """
    # Garante que o banco e as tabelas estejam acessíveis e atualizados
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 48)
            print("        GESTÃO DE FILIAIS E DEPÓSITOS (CD)      ")
            print("=" * 48)
            print("1. Cadastrar Nova Filial / CD")
            print("2. Listar Todas as Filiais Ativas")
            print("3. Consultar Filial por Nome ou Código")
            print("4. Editar Dados da Filial / CD")
            print("5. Inativar Filial (Soft Delete)")
            print("6. Transferência de Estoque (CD ➔ Loja)")
            print("7. Voltar ao Menu Principal")
            print("-" * 48)

            opcao = input("Digite o número da opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nRetornando ao menu principal.")
            break

        match opcao:
            case "1":
                cadastrar_filial()
            case "2":
                listar_filiais()
            case "3":
                consultar_filial()
            case "4":
                editar_filial()
            case "5":
                inativar_filial()
            case "6":
                transferir_estoque_filiais()
            case "7":
                print("Voltando ao menu principal...")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 7.")
