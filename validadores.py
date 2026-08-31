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


# ==========================================
# VALIDADORES DE PRODUTO
# ==========================================

def obter_preco_custo_valido() -> float:
    """
    Solicita o preço de custo do produto e valida se é um valor numérico positivo (> 0).
    Aceita vírgula ou ponto como separador decimal.
    
    Retorno:
        float: Preço de custo arredondado para 2 casas decimais.
    """
    while True:
        entrada = input("Digite o Preço de Custo (R$): ").strip().replace(",", ".")
        try:
            preco = float(entrada)
            if preco > 0:
                return round(preco, 2)
            print("Dado inválido! O preço de custo deve ser maior que zero (ex: 50.00 ou 50,00).")
        except ValueError:
            print("Dado inválido! Digite um valor numérico válido para o custo.")


def obter_markup_valido() -> float:
    """
    Solicita o fator multiplicador de markup para o produto (>= 0).
    Exemplos:
        - 2: dobra o valor de custo (15 * 2 = 30.00)
        - 1.86: multiplica por 1.86 (10 * 1.86 = 18.60)
        - 0: não utiliza markup multiplicador e permite informar o preço de venda manualmente.
    
    Retorno:
        float: Índice multiplicador de markup (ex: 2.0, 1.86 ou 0).
    """
    while True:
        entrada = input("Digite o Markup multiplicador (ex: 2 para dobrar, 1.86 ou 0 para preço manual): ").strip().replace(",", ".")
        try:
            markup = float(entrada)
            if markup >= 0:
                return round(markup, 4)
            print("Dado inválido! O markup multiplicador não pode ser negativo.")
        except ValueError:
            print("Dado inválido! Digite um valor numérico para o markup (ex: 2, 1.86 ou 0).")


def obter_preco_venda_valido(preco_custo: float = None) -> float:
    """
    Solicita o preço de venda manual e valida se é um valor numérico positivo (> 0).
    
    Parâmetros:
        preco_custo (float, opcional): Se fornecido, avisa caso a venda seja inferior ao custo.
        
    Retorno:
        float: Preço de venda validado.
    """
    while True:
        entrada = input("Digite o Preço de Venda Final (R$): ").strip().replace(",", ".")
        try:
            venda = float(entrada)
            if venda > 0:
                if preco_custo is not None and venda < preco_custo:
                    print(f"⚠️ Atenção: Preço de venda (R$ {venda:.2f}) está abaixo do custo (R$ {preco_custo:.2f})!")
                return round(venda, 2)
            print("Dado inválido! O preço de venda deve ser maior que zero.")
        except ValueError:
            print("Dado inválido! Digite um número válido para o preço de venda.")


def obter_quantidade_valida() -> int:
    """
    Solicita a quantidade em estoque do produto e valida se é um número inteiro >= 0.
    
    Retorno:
        int: Quantidade em estoque.
    """
    while True:
        entrada = input("Digite a quantidade em estoque: ").strip()
        try:
            qtd = int(entrada)
            if qtd >= 0:
                return qtd
            print("Dado inválido! A quantidade em estoque não pode ser negativa.")
        except ValueError:
            print("Dado inválido! Digite um número inteiro.")


def obter_nome_produto_valido() -> str:
    """
    Solicita o nome/descrição do produto e garante que tenha pelo menos 2 caracteres.
    
    Retorno:
        str: Nome do produto formatado em Title Case.
    """
    while True:
        nome = input("Digite o nome do produto: ").strip().title()
        if len(nome) >= 2:
            return nome
        print("Opção inválida! O nome do produto deve ter no mínimo 2 caracteres.")


def obter_categoria_valida() -> str:
    """
    Solicita a categoria do produto (opcional).
    
    Retorno:
        str: Categoria formatada em Title Case ou vazia.
    """
    cat = input("Digite a categoria do produto (opcional): ").strip().title()
    return cat


def obter_fornecedor_id_valido(ids_permitidos: list) -> int:
    """
    Solicita e valida a seleção de um fornecedor a partir de uma lista de IDs ativos existentes.
    
    Parâmetros:
        ids_permitidos (list[int]): Lista de IDs numéricos de fornecedores ativos válidos.
        
    Retorno:
        int: ID do fornecedor validado e selecionado pelo usuário.
    """
    while True:
        entrada = input("Digite o ID do Fornecedor vinculado ao produto: ").strip()
        try:
            fornecedor_id = int(entrada)
            if fornecedor_id in ids_permitidos:
                return fornecedor_id
            print(f"❌ Fornecedor ID {fornecedor_id} não encontrado na lista de fornecedores ativos!")
        except ValueError:
            print("❌ ID inválido! Digite apenas números inteiros correspondentes a um fornecedor.")


def obter_preco_promocao_valido(preco_venda: float = None) -> float:
    """
    Solicita o preço promocional do produto (opcional).
    Se o valor for 0, vazio ou nulo, indica que o produto não está em promoção e utilizará o preço normal.
    
    Parâmetros:
        preco_venda (float, opcional): Preço de venda normal para conferência/aviso.
        
    Retorno:
        float: Preço promocional validado ou 0.0 caso não esteja em promoção.
    """
    while True:
        entrada = input("Preço Promocional em R$ (pressione Enter ou digite 0 para sem promoção): ").strip().replace(",", ".")
        if not entrada or entrada == "0":
            return 0.0
        try:
            promo = float(entrada)
            if promo < 0:
                print("❌ Dado inválido! O preço de promoção não pode ser negativo.")
                continue
            if preco_venda is not None and promo >= preco_venda:
                print(f"⚠️ Aviso: O preço de promoção (R$ {promo:.2f}) é maior ou igual ao preço de venda normal (R$ {preco_venda:.2f})!")
            return round(promo, 2)
        except ValueError:
            print("❌ Dado inválido! Digite um valor numérico para a promoção ou pressione Enter para 0.")