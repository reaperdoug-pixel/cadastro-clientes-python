def obter_idade_valida():
    while True:
        entrada = input("Digite a idade do cliente: ").strip()
        try:
            idade = int(entrada)
            if 0 < idade < 120:
                return idade
            print("Dado inválido! A idade deve ser entre 1 e 119 anos.")
        except ValueError:
            print("Dado inválido! Digite apenas números inteiros positivos.")
            



def obter_sexo_valido():
    while True:
        sexo = input("Digite o sexo do cliente (M/F/O): ").strip().upper()
        if sexo in ["M", "F", "O"]:
            return sexo
        print("Opção inválida! Digite M para Masculino, F para Feminino ou O para Outro.") 



def obter_email_valido():
    while True:
        email = input("Digite o e-mail do cliente: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("E-mail inválido! Certifique-se de incluir '@' e '.'.")


def obter_telefone_valido():
    while True:
        telefone = input("Digite o telefone do cliente com DDD (apenas números): ").strip()
        
        if telefone.isdigit() and 10 <= len(telefone) <= 11:
            ddd = telefone[:2]
            meio = telefone[2:-4]
            fim = telefone[-4:]
            
            telefone_formatado = f"({ddd}) {meio}-{fim}"
            return telefone_formatado
        print("Dado inválido! Digite apenas números do telefone com DDD (10 ou 11 dígitos).")



def obter_nome_valido():
    while True:
        nome = input("Digite o nome do cliente: ").strip().title()
        nome_sem_espacos = nome.replace(" ", "")
        if len(nome_sem_espacos) >= 3 and nome_sem_espacos.isalpha():
            return nome     
        print("Opção inválida! Digite um nome válido (apenas letras, mínimo 3 caracteres).")