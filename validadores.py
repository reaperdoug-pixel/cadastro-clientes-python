"""
Módulo de Validações de Entrada
Responsável por solicitar dados ao usuário pelo terminal e garantir que apenas valores
válidos e devidamente formatados sejam aceitos pelo sistema.
"""

def obter_idade_valida() -> int:
    """
    Solicita a idade do cliente via terminal e valida se é um número inteiro
    positivo em uma faixa aceitável (1 a 119 anos).
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
    """
    while True:
        email = input("Digite o e-mail do cliente: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("E-mail inválido! Certifique-se de incluir '@' e '.'.")


def obter_telefone_valido() -> str:
    """
    Solicita o telefone com DDD (10 ou 11 dígitos numéricos)
    e retorna o número formatado no padrão '(XX) XXXXX-XXXX' ou '(XX) XXXX-XXXX'.
    """
    while True:
        telefone = input("Digite o telefone com DDD (apenas números): ").strip()
        if telefone.isdigit() and 10 <= len(telefone) <= 11:
            ddd = telefone[:2]
            meio = telefone[2:-4]
            fim = telefone[-4:]
            return f"({ddd}) {meio}-{fim}"
        print("Dado inválido! Digite apenas números do telefone com DDD (10 ou 11 dígitos).")


def obter_nome_valido() -> str:
    """
    Solicita o nome do cliente e valida se é composto exclusivamente por letras
    (com acentos) e espaços, exigindo no mínimo 3 caracteres alfabéticos.
    """
    while True:
        nome = input("Digite o nome do cliente: ").strip().title()
        nome_sem_espacos = nome.replace(" ", "")
        if len(nome_sem_espacos) >= 3 and nome_sem_espacos.isalpha():
            return nome     
        print("Opção inválida! Digite um nome válido (apenas letras, mínimo 3 caracteres).")


# ==========================================
# VALIDADORES DE PRODUTO, PREÇOS E ESTOQUE
# ==========================================

def obter_preco_custo_valido() -> float:
    """Solicita o preço de custo do produto e valida se é numérico positivo (> 0)."""
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
    """Solicita o fator multiplicador de markup para o produto (>= 0)."""
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
    """Solicita o preço de venda manual e valida se é positivo (> 0)."""
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
    """Solicita a quantidade em estoque do produto (>= 0)."""
    while True:
        entrada = input("Digite a quantidade inicial em estoque: ").strip()
        try:
            qtd = int(entrada)
            if qtd >= 0:
                return qtd
            print("Dado inválido! A quantidade em estoque não pode ser negativa.")
        except ValueError:
            print("Dado inválido! Digite um número inteiro.")


def obter_estoque_minimo_valido() -> int:
    """Solicita o estoque mínimo do produto (>= 0)."""
    while True:
        entrada = input("Digite o estoque mínimo de segurança (pressione Enter para 0): ").strip()
        if not entrada:
            return 0
        try:
            est_min = int(entrada)
            if est_min >= 0:
                return est_min
            print("Dado inválido! O estoque mínimo não pode ser negativo.")
        except ValueError:
            print("Dado inválido! Digite um número inteiro válido.")


def obter_nome_produto_valido() -> str:
    """Solicita o nome do produto (mínimo 2 caracteres)."""
    while True:
        nome = input("Digite o nome do produto: ").strip().title()
        if len(nome) >= 2:
            return nome
        print("Opção inválida! O nome do produto deve ter no mínimo 2 caracteres.")


def obter_categoria_valida() -> str:
    """Solicita a categoria do produto (opcional)."""
    cat = input("Digite a categoria do produto (opcional): ").strip().title()
    return cat


def obter_fornecedor_id_valido(ids_permitidos: list) -> int:
    """Solicita e valida o ID de fornecedor existente."""
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
    """Solicita o preço promocional do produto (opcional, 0 se sem promoção)."""
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


def obter_loja_id_valido(ids_lojas_permitidos: list, permitir_geral: bool = False) -> int:
    """Solicita e valida a seleção de uma filial a partir dos IDs válidos."""
    while True:
        if permitir_geral:
            entrada = input("Digite o ID da Loja/Filial (ou Enter para todas): ").strip()
            if not entrada:
                return 0
        else:
            entrada = input("Digite o ID da Loja/Filial desejada: ").strip()
            
        try:
            loja_id = int(entrada)
            if loja_id in ids_lojas_permitidos:
                return loja_id
            print(f"❌ Filial ID {loja_id} não encontrada na lista!")
        except ValueError:
            print("❌ ID inválido! Digite o número correspondente à filial.")


def obter_tipo_movimentacao_valido() -> str:
    """Solicita e valida o tipo de movimentação de estoque."""
    while True:
        print("\nTipos de Movimentação:")
        print("1. ENTRADA (Acrescentar ao saldo)")
        print("2. SAÍDA (Subtrair do saldo)")
        print("3. AJUSTE (Definir novo saldo exato por inventário)")
        
        opcao = input("Escolha o tipo de movimentação (1/2/3): ").strip()
        match opcao:
            case "1":
                return "ENTRADA"
            case "2":
                return "SAIDA"
            case "3":
                return "AJUSTE"
            case _:
                print("❌ Opção inválida! Escolha 1, 2 ou 3.")


def obter_motivo_movimentacao() -> str:
    """Solicita a justificativa para a movimentação de estoque."""
    while True:
        motivo = input("Digite o motivo/justificativa da movimentação: ").strip()
        if len(motivo) >= 3:
            return motivo
        print("❌ Motivo muito curto! Digite uma descrição clara (mínimo 3 caracteres).")


def obter_quantidade_movimentacao_valida() -> int:
    """Solicita a quantidade a movimentar (> 0)."""
    while True:
        entrada = input("Digite a quantidade a movimentar: ").strip()
        try:
            qtd = int(entrada)
            if qtd > 0:
                return qtd
            print("❌ Dado inválido! A quantidade deve ser maior que zero.")
        except ValueError:
            print("❌ Dado inválido! Digite um número inteiro.")


# ==========================================
# VALIDADORES DE FILIAIS E CENTROS DE DISTRIBUIÇÃO
# ==========================================

def obter_tipo_filial_valido() -> str:
    """
    Solicita o tipo de estabelecimento:
    1. LOJA_FISICA (Loja padrão)
    2. CENTRO_DISTRIBUICAO (CD / Depósito Central)
    3. LOJA_VIRTUAL (E-Commerce / Marketplace)
    """
    while True:
        print("\nTipo de Estabelecimento:")
        print("1. Loja Física")
        print("2. Centro de Distribuição (CD / Depósito)")
        print("3. Loja Virtual / E-Commerce")
        
        opcao = input("Selecione o tipo (1/2/3): ").strip()
        match opcao:
            case "1":
                return "LOJA_FISICA"
            case "2":
                return "CENTRO_DISTRIBUICAO"
            case "3":
                return "LOJA_VIRTUAL"
            case _:
                print("❌ Opção inválida! Escolha 1, 2 ou 3.")


def obter_codigo_filial_valido() -> str:
    """Solicita um código curto alfanumérico para identificação rápida da filial."""
    while True:
        codigo = input("Digite o Código da Filial (ex: CD-01, LOJA-CENTRO, ECOM): ").strip().upper()
        if len(codigo) >= 2 and not " " in codigo:
            return codigo
        print("❌ Código inválido! O código deve ter pelo menos 2 caracteres e não pode conter espaços.")


def obter_nome_fantasia_filial_valido() -> str:
    """Solicita o Nome Fantasia da Filial."""
    while True:
        nome = input("Digite o Nome Fantasia da Filial/CD: ").strip().title()
        if len(nome) >= 2:
            return nome
        print("❌ Nome Fantasia muito curto! Digite no mínimo 2 caracteres.")


def obter_razao_social_filial_valida() -> str:
    """Solicita a Razão Social da Filial (opcional)."""
    razao = input("Digite a Razão Social (opcional, Enter para vazio): ").strip().title()
    return razao


def obter_cnpj_filial_valido() -> str:
    """
    Solicita o CNPJ da filial.
    Se o cliente digitar '0' ou pressionar Enter, considera '0' (Sem CNPJ / Loja Virtual).
    Caso contrário, valida se possui 14 dígitos numéricos e formata como XX.XXX.XXX/XXXX-XX.
    """
    while True:
        entrada = input("Digite o CNPJ da Filial (apenas números ou '0' se não possuir CNPJ próprio): ").strip()
        
        if entrada == "0" or not entrada:
            return "0"
            
        cnpj_limpo = entrada.replace(".", "").replace("/", "").replace("-", "").strip()
        
        if len(cnpj_limpo) == 14 and cnpj_limpo.isdigit():
            # Aplica máscara de CNPJ
            cnpj_fmt = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
            return cnpj_fmt
            
        print("❌ CNPJ inválido! Digite 14 números para CNPJ ou '0' para Isento / Sem CNPJ.")


def obter_telefone_filial_valido() -> str:
    """Solicita o telefone da filial (opcional)."""
    telefone = input("Digite o Telefone com DDD (ou Enter para vazio): ").strip()
    if not telefone:
        return "-"
    if telefone.isdigit() and 10 <= len(telefone) <= 11:
        ddd = telefone[:2]
        meio = telefone[2:-4]
        fim = telefone[-4:]
        return f"({ddd}) {meio}-{fim}"
    return telefone


def obter_endereco_filial_valido() -> str:
    """Solicita o endereço da filial (opcional)."""
    endereco = input("Digite o Endereço completo (ou Enter para vazio): ").strip()
    return endereco if endereco else "-"