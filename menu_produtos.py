"""Interface CLI do módulo de Estoque e do CRUD de Produtos."""

from funcoes_filiais import distribuir_produtos_cd, transferir_estoque_filiais
from funcoes_produtos import (
    cadastrar_produto,
    consultar_extrato_kardex,
    entrada_de_notas,
    editar_produto,
    gerenciar_precos_promocoes,
    inativar_produto,
    listar_produtos,
    movimentar_estoque_produto,
)
from persistencia import inicializar_banco
from persistencia import existe_cd_ativo
import sessao


def sub_menu_produtos() -> None:
    """Exibe o CRUD de produtos dentro do módulo de Estoque."""
    while True:
        try:
            print("\n" + "=" * 48)
            print("        DEGEHUB ERP | ESTOQUE > PRODUTOS       ")
            print("=" * 48)
            print("1. Cadastrar Produto")
            print("2. Listar Produtos (por Filial/Loja)")
            print("3. Alterar Dados Cadastrais do Produto")
            print("4. Inativar Produto (Soft Delete)")
            print("5. Voltar ao Menu Estoque")
            print("-" * 48)
            opcao = input("Digite o número da opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nRetornando ao menu Estoque.")
            break

        match opcao:
            case "1":
                cadastrar_produto()
            case "2":
                listar_produtos()
            case "3":
                editar_produto()
            case "4":
                inativar_produto()
            case "5":
                print("Voltando ao menu Estoque...")
                break
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 5.")


def sub_menu_estoque() -> None:
    """Exibe as operações de estoque e o acesso ao CRUD de Produtos."""
    inicializar_banco()

    if sessao.possui_permissao("CONSULTA"):
        while True:
            print("\n" + "=" * 48)
            print("      DEGEHUB ERP | GESTÃO DE ESTOQUE (CONSULTA)")
            print("=" * 48)
            print("1. Listar Produtos")
            print("2. Extrato de Movimentações (Kardex)")
            print("3. Voltar ao Menu Principal")
            opcao = input("Digite a opção desejada: ").strip()
            if opcao == "1":
                listar_produtos()
            elif opcao == "2":
                consultar_extrato_kardex()
            elif opcao == "3":
                return
            else:
                print("Opção inválida.")

    while True:
        try:
            print("\n" + "=" * 48)
            print("          DEGEHUB ERP | GESTÃO DE ESTOQUE       ")
            print("=" * 48)
            print("1. Produtos")
            opcoes = {"1": sub_menu_produtos, "2": movimentar_estoque_produto,
                       "3": transferir_estoque_filiais, "4": gerenciar_precos_promocoes,
                       "5": entrada_de_notas, "6": consultar_extrato_kardex}
            proxima = 7
            possui_cd = existe_cd_ativo()
            if possui_cd:
                print("2. Distribuição de Produtos (CD para Loja)")
                opcoes["2"] = distribuir_produtos_cd
                opcoes["3"] = movimentar_estoque_produto
                opcoes["4"] = transferir_estoque_filiais
                opcoes["5"] = gerenciar_precos_promocoes
                opcoes["6"] = entrada_de_notas
                opcoes["7"] = consultar_extrato_kardex
                proxima = 8
            print(f"{'3' if possui_cd else '2'}. Movimentação de Produtos (Ajuste)")
            print(f"{'4' if possui_cd else '3'}. Transferência de Produtos")
            print(f"{'5' if possui_cd else '4'}. Gerenciar Preços e Promoções")
            print(f"{'6' if possui_cd else '5'}. Entrada de Notas")
            print(f"{'7' if possui_cd else '6'}. Extrato de Movimentações (Kardex)")
            print(f"{proxima}. Voltar ao Menu Principal")
            print("-" * 48)
            opcao = input("Digite o número da opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nRetornando ao menu principal.")
            break

        match opcao:
            case _ if opcao == str(proxima):
                print("Voltando ao menu principal...")
                break
            case _ if opcao in opcoes:
                opcoes[opcao]()
            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 6.")


# Compatibilidade com importações externas que usem o nome explícito do módulo.
sub_menu_produto_estoque = sub_menu_estoque
