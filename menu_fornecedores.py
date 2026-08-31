"""
Módulo de Interface CLI: Fornecedores
Responsável por exibir o submenu interativo para gerenciamento de fornecedores e
direcionar as ações do usuário para as funções correspondentes.
"""

from funcoes_fornecedores import (
    cadastrar_fornecedor,
    consultar_fornecedor,
    consultar_fornecedor_por_nome,
    editar_fornecedor,
    inativar_fornecedor
)
from persistencia import inicializar_banco

def sub_menu_fornecedores() -> None:
    """
    Exibe o menu de opções para a gestão de fornecedores em loop interativo até que
    o usuário opte por voltar ao menu principal ou interrompa o programa.
    """
    # Garante que o banco e as tabelas estejam acessíveis
    inicializar_banco()

    while True:
        try:
            print("\n" + "=" * 45)
            print("       GESTÃO DE FORNECEDORES          ")
            print("=" * 45)
            print("1. Cadastrar Fornecedor")
            print("2. Consultar Fornecedor por CNPJ")
            print("3. Consultar por Razão Social / Nome Fantasia")
            print("4. Editar Fornecedor")
            print("5. Inativar Fornecedor") 
            print("6. Voltar ao Menu Principal")
            print("-" * 45)

            opcao = input("Digite o número da opção desejada: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nRetornando ao menu principal.")
            break

        match opcao:
            case "1":
                print("\n--- CADASTRO DE FORNECEDOR ---")
                cnpj = input("CNPJ (apenas números ou formatado): ").strip()
                razao_social = input("Razão Social (obrigatório): ").strip()
                nome_fantasia = input("Nome Fantasia: ").strip()
                endereco = input("Endereço: ").strip()
                uf = input("UF (Estado): ").strip()
                telefone = input("Telefone: ").strip()
                contato = input("Nome do Contato: ").strip()
                
                cadastrar_fornecedor(
                    cnpj=cnpj,
                    razao_social=razao_social,
                    nome_fantasia=nome_fantasia,
                    endereco=endereco,
                    uf=uf,
                    telefone=telefone,
                    contato=contato
                )

            case "2":
                print("\n--- CONSULTAR FORNECEDOR POR CNPJ ---")
                cnpj_busca = input("Digite o CNPJ para pesquisar: ").strip()
                fornecedor = consultar_fornecedor(cnpj_busca)
                
                if fornecedor:
                    print("\n" + "-" * 60)
                    print(f"ID: {fornecedor['id']}")
                    print(f"CNPJ: {fornecedor['cnpj']}")
                    print(f"Razão Social: {fornecedor['razao_social']}")
                    print(f"Nome Fantasia: {fornecedor['nome_fantasia']}")
                    print(f"Endereço: {fornecedor['endereco']} - UF: {fornecedor['uf']}")
                    print(f"Telefone: {fornecedor['telefone']} | Contato: {fornecedor['contato']}")
                    print("-" * 60)
                else:
                    print("⚠️ Fornecedor não localizado ou inativo.")

            case "3":
                consultar_fornecedor_por_nome()

            case "4":
                print("\n--- EDITAR FORNECEDOR ---")
                try:
                    id_fornecedor = int(input("Digite o ID do fornecedor que deseja editar: ").strip())
                    cnpj = input("Novo CNPJ: ").strip()
                    razao_social = input("Nova Razão Social (obrigatório): ").strip()
                    nome_fantasia = input("Novo Nome Fantasia: ").strip()
                    endereco = input("Novo Endereço: ").strip()
                    uf = input("Nova UF: ").strip()
                    telefone = input("Novo Telefone: ").strip()
                    contato = input("Novo Contato: ").strip()
                    
                    editar_fornecedor(
                        id_fornecedor=id_fornecedor,
                        cnpj=cnpj,
                        razao_social=razao_social,
                        nome_fantasia=nome_fantasia,
                        endereco=endereco,
                        uf=uf,
                        telefone=telefone,
                        contato=contato
                    )
                except ValueError:
                    print("⚠️ Erro: O ID precisa ser um número inteiro válido.")

            case "5":
                print("\n--- INATIVAR FORNECEDOR ---")
                try:
                    id_fornecedor = int(input("Digite o ID do fornecedor que deseja inativar: ").strip())
                    confirmacao = input(f"Tem certeza que deseja inativar o fornecedor ID {id_fornecedor}? (S/N): ").strip().upper()
                    
                    if confirmacao == "S":
                        inativar_fornecedor(id_fornecedor)
                    else:
                        print("Operação cancelada.")
                except ValueError:
                    print("⚠️ Erro: O ID precisa ser um número inteiro válido.")

            case "6":
                print("Voltando ao menu principal...")
                break

            case _:
                print("\n⚠️ Opção inválida! Escolha um número de 1 a 6.")