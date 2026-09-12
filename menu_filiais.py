"""Interface CLI para gestão cadastral de Filiais e Centros de Distribuição."""

from funcoes_filiais import (
    cadastrar_filial,
    consultar_filial,
    editar_filial,
    inativar_filial,
    listar_filiais,
)
from persistencia import inicializar_banco


def sub_menu_filiais() -> None:
    """Exibe o menu de cadastro de filiais e CDs em loop interativo."""
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 50)
            print("        DEGEHUB ERP | GESTÃO DE FILIAIS & CDS     ")
            print("=" * 50)
            print("1. Cadastrar Nova Filial / CD")
            print("2. Listar Todas as Filiais Ativas")
            print("3. Consultar Filial por Nome ou Código")
            print("4. Editar Dados da Filial / CD")
            print("5. Inativar Filial (Soft Delete)")
            print("6. Voltar ao Menu Principal")
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
                print("Voltando ao menu principal...")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 6.")
