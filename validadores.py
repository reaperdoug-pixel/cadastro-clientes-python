"""
Módulo de Validações de Entrada
Responsável por solicitar dados ao usuário pelo terminal e garantir que apenas valores
válidos e devidamente formatados sejam aceitos pelo sistema.
"""

def obter_idade_valida() -> int:
    """
    Solicita a idade do cliente via terminal e valida se é um número inteiro
    positivo em uma faixa aceitável (1 a 119 anos).
    
    Retorno:
        int: Idade válida informada pelo usuário.
    """
    while True:
        entrada = input("Digite a idade do cliente: ").strip()
        try:
            idade = int(entrada)
            if 0 < idade < 120:
                return idade
            print("Dado inválido! A idade deve ser entre 1 e 119 anos.")
        except ValueError:
            print("Dado inválido! Digite apenas números inteiros positivos.")


def obter_sexo_valido() -> str:
    """
    Solicita o sexo do cliente e valida se corresponde a uma das opções permitidas:
    M (Masculino), F (Feminino) ou O (Outro).
    
    Retorno:
        str: Caractere em maiúsculo ('M', 'F' ou 'O').
    """
    while True:
        sexo = input("Digite o sexo do cliente (M/F/O): ").strip().upper()
        if sexo in ["M", "F", "O"]:
            return sexo
        print("Opção inválida! Digite M para Masculino, F para Feminino ou O para Outro.") 


def obter_email_valido() -> str:
    """
    Solicita o e-mail do cliente e realiza uma validação estrutural básica,
    assegurando a presença dos caracteres '@' e '.'.
    
    Retorno:
        str: E-mail formatado em letras minúsculas.
    """
    while True:
        email = input("Digite o e-mail do cliente: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("E-mail inválido! Certifique-se de incluir '@' e '.'.")


def obter_telefone_valido() -> str:
    """
    Solicita o telefone do cliente com DDD (10 ou 11 dígitos numéricos)
    e retorna o número formatado no padrão '(XX) XXXXX-XXXX' ou '(XX) XXXX-XXXX'.
    
    Retorno:
        str: Telefone com máscara de formatação aplicada.
    """
    while True:
        telefone = input("Digite o telefone do cliente com DDD (apenas números): ").strip()
        
        # Verifica se contém apenas números e tem 10 (fixo) ou 11 (celular) dígitos
        if telefone.isdigit() and 10 <= len(telefone) <= 11:
            ddd = telefone[:2]
            meio = telefone[2:-4]
            fim = telefone[-4:]
            
            telefone_formatado = f"({ddd}) {meio}-{fim}"
            return telefone_formatado
        print("Dado inválido! Digite apenas números do telefone com DDD (10 ou 11 dígitos).")


def obter_nome_valido() -> str:
    """
    Solicita o nome do cliente e valida se é composto exclusivamente por letras
    (com acentos) e espaços, exigindo no mínimo 3 caracteres alfabéticos.
    
    Retorno:
        str: Nome com as primeiras letras de cada palavra em maiúsculo (Title Case).
    """
    while True:
        nome = input("Digite o nome do cliente: ").strip().title()
        nome_sem_espacos = nome.replace(" ", "")
        
        # Garante que possui ao menos 3 letras e nenhum número ou caractere especial
        if len(nome_sem_espacos) >= 3 and nome_sem_espacos.isalpha():
            return nome     
        print("Opção inválida! Digite um nome válido (apenas letras, mínimo 3 caracteres).")