"""
Módulo de Regras de Negócio: Fornecedores
Responsável por orquestrar a coleta, formatação com máscara de CNPJ e acionamento
dos métodos de persistência para a gestão de fornecedores.
"""

import re
from persistencia import (
    cadastrar_fornecedor_banco,
    buscar_fornecedor_por_cnpj_banco,
    buscar_fornecedores_por_nome_banco,
    atualizar_fornecedor_banco,
    inativar_fornecedor_banco
)

# ==========================================
# FUNÇÃO AUXILIAR
# ==========================================

def formatar_cnpj(cnpj: str) -> str:
    """
    Remove caracteres não numéricos e aplica a máscara oficial de CNPJ: XX.XXX.XXX/XXXX-XX.
    
    Parâmetros:
        cnpj (str): CNPJ fornecido pelo usuário (formatado ou apenas dígitos).
        
    Retorno:
        str: CNPJ formatado com exatamente 18 caracteres.
        
    Lança:
        ValueError: Caso o CNPJ não possua exatamente 14 dígitos numéricos.
    """
    numeros = re.sub(r'\D', '', str(cnpj))
    if len(numeros) != 14:
        raise ValueError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
    return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"


# ==========================================
# REGRAS DE NEGÓCIO: FORNECEDORES
# ==========================================

def cadastrar_fornecedor(cnpj: str, razao_social: str, nome_fantasia: str = "", 
                         endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
    """
    Valida a obrigatoriedade da Razão Social, aplica a máscara de formatação ao CNPJ
    e envia os dados para cadastro no banco de dados.
    
    Retorno:
        bool: True se cadastrado com sucesso, False em caso de falha de validação ou duplicidade.
    """
    try:
        if not razao_social.strip():
            print("❌ Erro: A Razão Social é obrigatória.")
            return False

        cnpj_formatado = formatar_cnpj(cnpj)
        
        return cadastrar_fornecedor_banco(
            cnpj=cnpj_formatado,
            razao_social=razao_social.strip(),
            nome_fantasia=nome_fantasia.strip(),
            endereco=endereco.strip(),
            uf=uf.strip().upper(),
            telefone=telefone.strip(),
            contato=contato.strip()
        )
    except ValueError as err:
        print(f"❌ Erro de Validação: {err}")
        return False


def consultar_fornecedor(cnpj: str):
    """
    Aplica a máscara ao CNPJ informado e consulta o fornecedor ativo correspondente no banco.
    
    Parâmetros:
        cnpj (str): CNPJ (apenas dígitos ou com pontuação).
        
    Retorno:
        sqlite3.Row | None: Registro do fornecedor se encontrado, ou None.
    """
    try:
        cnpj_formatado = formatar_cnpj(cnpj)
        return buscar_fornecedor_por_cnpj_banco(cnpj_formatado)
    except ValueError as err:
        print(f"❌ Erro na Busca: {err}")
        return None


def editar_fornecedor(id_fornecedor: int, cnpj: str, razao_social: str, nome_fantasia: str = "", 
                      endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
    """
    Valida o ID, a Razão Social e formata o novo CNPJ antes de enviar a atualização para o banco.
    
    Retorno:
        bool: True se atualizado com sucesso, False em caso de falha.
    """
    try:
        if not id_fornecedor:
            print("❌ Erro: ID do fornecedor é inválido.")
            return False

        if not razao_social.strip():
            print("❌ Erro: A Razão Social não pode ficar em branco.")
            return False

        cnpj_formatado = formatar_cnpj(cnpj)

        return atualizar_fornecedor_banco(
            id_fornecedor=id_fornecedor,
            cnpj=cnpj_formatado,
            razao_social=razao_social.strip(),
            nome_fantasia=nome_fantasia.strip(),
            endereco=endereco.strip(),
            uf=uf.strip().upper(),
            telefone=telefone.strip(),
            contato=contato.strip()
        )
    except ValueError as err:
        print(f"❌ Erro na Edição: {err}")
        return False


def inativar_fornecedor(id_fornecedor: int) -> bool:
    """
    Valida o ID do fornecedor e executa a inativação lógica (ativo = 0).
    
    Parâmetros:
        id_fornecedor (int): ID numérico do fornecedor.
        
    Retorno:
        bool: True se inativado com sucesso, False caso contrário.
    """
    if not id_fornecedor:
        print("❌ Erro: ID do fornecedor é inválido.")
        return False

    return inativar_fornecedor_banco(id_fornecedor)


def consultar_fornecedor_por_nome() -> None:
    """
    Solicita um termo ao usuário e lista os fornecedores encontrados por Razão Social ou Nome Fantasia.
    """
    print("\n--- CONSULTA DE FORNECEDOR POR RAZÃO SOCIAL / FANTASIA ---")
    termo = input("Digite a Razão Social ou Nome Fantasia (ou parte dele): ").strip()

    if not termo:
        print("❌ Erro: Digite pelo menos um caractere para pesquisar.")
        return

    fornecedores = buscar_fornecedores_por_nome_banco(termo)

    if not fornecedores:
        print(f"⚠️ Nenhum fornecedor encontrado com o termo '{termo}'.")
        return

    print("-" * 75)
    for f in fornecedores:
        print(f"ID: {f[0]} | CNPJ: {f[1]} | Razão Social: {f[2]} | Fantasia: {f[3]} | Tel: {f[4]}")
    print("-" * 75)