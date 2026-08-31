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
    numeros = re.sub(r'\D', '', str(cnpj))
    if len(numeros) != 14:
        raise ValueError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
    return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"


# ==========================================
# REGRAS DE NEGÓCIO: FORNECEDORES
# ==========================================

def cadastrar_fornecedor(cnpj: str, razao_social: str, nome_fantasia: str = "", 
                         endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
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
    try:
        cnpj_formatado = formatar_cnpj(cnpj)
        return buscar_fornecedor_por_cnpj_banco(cnpj_formatado)
    except ValueError as err:
        print(f"❌ Erro na Busca: {err}")
        return None


def editar_fornecedor(id_fornecedor: int, cnpj: str, razao_social: str, nome_fantasia: str = "", 
                      endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
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
    if not id_fornecedor:
        print("❌ Erro: ID do fornecedor é inválido.")
        return False

    return inativar_fornecedor_banco(id_fornecedor)

def consultar_fornecedor_por_nome():
    """
    Solicita um termo ao usuário e lista os fornecedores encontrados por Razão Social/Nome Fantasia.
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