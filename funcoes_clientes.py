import re
from validadores import (
    obter_nome_valido,
    obter_idade_valida,
    obter_sexo_valido,
    obter_email_valido,
    obter_telefone_valido
)
from persistencia import (
    salvar_cliente,
    carregar_clientes,
    buscar_clientes_por_nome_banco,
    buscar_cliente_por_id_banco,
    atualizar_cliente,
    inativar_cliente
)

# ==========================================
# FUNÇÕES AUXILIARES DE VALIDAÇÃO
# ==========================================

def validar_email(email: str) -> bool:
    """
    Valida a estrutura básica de um e-mail utilizando regex.
    """
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(padrao, email.strip()))


def formatar_telefone(telefone: str) -> str:
    """
    Remove caracteres não numéricos do telefone.
    """
    return re.sub(r'\D', '', str(telefone))


# ==========================================
# REGRAS DE NEGÓCIO E INTERAÇÕES
# ==========================================

def cadastrar_cliente():
    """
    Coleta e valida as entradas do usuário para cadastrar um novo cliente.
    """
    print("\n--- Cadastro de novo Cliente ---")
    nome = obter_nome_valido()
    idade = obter_idade_valida()
    sexo = obter_sexo_valido()
    email = obter_email_valido()
    telefone = obter_telefone_valido()

    novo_cliente = {
        'nome': nome,
        'idade': idade,
        'sexo': sexo,
        'email': email,
        'telefone': telefone
    }
    salvar_cliente(novo_cliente)
    print(f"\n✅ Cliente '{nome}' cadastrado com sucesso!")


def listar_clientes():
    """
    Exibe a lista de todos os clientes ativos no banco de dados.
    """
    print("\n--- Lista de Clientes Ativos ---")
    clientes = carregar_clientes()
    if not clientes:
        print("⚠️ Nenhum cliente ativo encontrado.")
        return
    print("-" * 75)
    for cliente in clientes:
        id_cli, nome, idade, sexo, email, telefone = cliente[0], cliente[1], cliente[2], cliente[3], cliente[4], cliente[5]
        print(f"ID: {id_cli:<3} | Nome: {nome:<20} | Idade: {idade:<3} | Sexo: {sexo} | Tel: {telefone} | E-mail: {email}")
    print("-" * 75)


def consultar_cliente():
    """
    Busca clientes ativos por trecho do nome informado pelo usuário.
    """
    print("\n--- Consulta de Cliente por Nome ---")
    nome_busca = input("Digite o nome (ou parte dele) para pesquisar: ").strip()
    
    if not nome_busca:
        print("❌ Erro: Digite pelo menos uma letra para pesquisar.")
        return

    clientes = buscar_clientes_por_nome_banco(nome_busca)
    
    if not clientes:
        print(f"⚠️ Nenhum cliente encontrado com o termo '{nome_busca}'.")
        return

    print("-" * 75)
    for c in clientes:
        print(f"ID: {c[0]:<3} | Nome: {c[1]:<20} | Idade: {c[2]:<3} | Sexo: {c[3]} | Tel: {c[5]} | E-mail: {c[4]}")
    print("-" * 75)


def editar_cliente():
    """
    Solicita o ID de um cliente ativo, valida sua existência e atualiza os dados.
    """
    print("\n--- Edição de Cliente ---")
    listar_clientes()

    try:
        cliente_id = int(input("\nDigite o ID do cliente que deseja editar: ").strip())
    except ValueError:
        print("❌ ID inválido! Digite apenas números.")
        return

    cliente = buscar_cliente_por_id_banco(cliente_id)
    if not cliente:
        print("❌ Cliente não encontrado ou inativo.")
        return

    print(f"\nAtualização de Dados do Cliente: {cliente[1]} (ID: {cliente[0]})")
    print("Preencha os novos dados:")
        
    nome = obter_nome_valido()
    idade = obter_idade_valida()
    sexo = obter_sexo_valido()
    email = obter_email_valido()
    telefone = obter_telefone_valido()

    dados_novos = {
        'nome': nome,
        'idade': idade,
        'sexo': sexo,
        'email': email,
        'telefone': telefone
    }

    atualizar_cliente(cliente_id, dados_novos)
    print("\n✅ Dados do cliente atualizados com sucesso!")


def inativar_cliente_funcao():
    """
    Realiza a exclusão lógica (Soft Delete) do cliente após confirmação do usuário.
    """
    print("\n--- Inativar Cliente (Soft Delete) ---")
    listar_clientes()

    try:
        cliente_id = int(input("\nDigite o ID do cliente que deseja inativar: ").strip())
    except ValueError:
        print("❌ ID inválido! Digite apenas números.")
        return

    cliente = buscar_cliente_por_id_banco(cliente_id)

    if not cliente:
        print("❌ Cliente não encontrado ou já inativo.")
        return

    confirmacao = input(f"Tem certeza que deseja inativar o cliente '{cliente[1]}' (ID: {cliente[0]})? (S/N): ").strip().upper()

    if confirmacao == "S":
        inativar_cliente(cliente_id)
        print("\n✅ Cliente inativado com sucesso!")
    else:
        print("\nOperação cancelada.")


# Aliases para manter compatibilidade com o menu_clientes.py
excluir_cliente = inativar_cliente_funcao