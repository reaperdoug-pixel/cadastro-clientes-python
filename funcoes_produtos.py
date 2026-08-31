"""
Módulo de Regras de Negócio: Produtos
Responsável por orquestrar a interação com o usuário (coleta e validação de dados),
vínculo obrigatório com fornecedores cadastrados, cálculo de preço de venda baseado 
em custo e markup multiplicador, suporte a preço de promoção (com ativação/desativação automática),
controle rigoroso de data de cadastro, data de alteração e data de atualização de preços,
além do acionamento dos métodos de persistência para produtos.
"""

from datetime import datetime
from validadores import (
    obter_nome_produto_valido,
    obter_preco_custo_valido,
    obter_markup_valido,
    obter_preco_venda_valido,
    obter_preco_promocao_valido,
    obter_quantidade_valida,
    obter_categoria_valida,
    obter_fornecedor_id_valido
)
from persistencia import (
    salvar_produto,
    carregar_produtos,
    buscar_produto_por_id_banco,
    buscar_produtos_por_nome_banco,
    atualizar_produto_banco,
    inativar_produto_banco,
    carregar_fornecedores_ativos,
    buscar_fornecedor_por_id_banco
)


# ==========================================
# CÁLCULO DE PRECIFICAÇÃO E PROMOÇÃO
# ==========================================

def calcular_preco_venda(preco_custo: float, markup: float, preco_venda_manual: float = None) -> float:
    """
    Calcula o preço de venda final baseado no preço de custo e no markup multiplicador.
    
    Regras de Negócio:
        - Se markup > 0: Preço de Venda = Custo * Markup (ex: Custo 15 * Markup 2 = 30.00 | Custo 10 * Markup 1.86 = 18.60)
        - Se markup == 0: Utiliza o preço de venda manual informado pelo usuário.
        
    Parâmetros:
        preco_custo (float): Preço de aquisição/custo do produto.
        markup (float): Índice multiplicador de markup (ex: 2.0, 1.86).
        preco_venda_manual (float, opcional): Valor manual caso markup seja 0.
        
    Retorno:
        float: Preço de venda final arredondado em 2 casas decimais.
    """
    # Se o markup multiplicador for maior que zero, calcula Custo * Markup
    if markup > 0:
        return round(preco_custo * markup, 2)
    # Se markup for 0, utiliza o preço de venda manual informado pelo usuário
    elif preco_venda_manual is not None and preco_venda_manual > 0:
        return round(preco_venda_manual, 2)
    # Fallback de segurança retornando o próprio custo
    return round(preco_custo, 2)


def obter_preco_venda_efetivo(preco_venda: float, preco_promocao: float = 0.0) -> tuple[float, bool]:
    """
    Determina o preço real que deve ser praticado na venda do produto:
        - Se o preço de promoção for maior que zero: utiliza o PREÇO DE PROMOÇÃO.
        - Se o preço de promoção for 0 ou nulo: utiliza o PREÇO DE VENDA normal.
        
    Parâmetros:
        preco_venda (float): Preço de venda normal (calculado ou manual).
        preco_promocao (float): Preço promocional (se houver).
        
    Retorno:
        tuple[float, bool]: (preco_efetivo, em_promocao)
    """
    if preco_promocao and preco_promocao > 0:
        return round(preco_promocao, 2), True
    return round(preco_venda, 2), False


# ==========================================
# REGRAS DE NEGÓCIO E INTERAÇÕES COM O USUÁRIO
# ==========================================

def cadastrar_produto() -> None:
    """
    Cadastra um novo produto no sistema com fornecedor obrigatório e suporte a promoção.
    
    Fluxo obrigatório:
        1. Verifica se existem fornecedores ativos cadastrados (bloqueia se não houver).
        2. Exibe os fornecedores ativos disponíveis e solicita a seleção de um ID válido.
        3. Coleta nome, preço de custo e markup multiplicador.
        4. Calcula o preço de venda (se markup > 0) ou solicita entrada manual (se markup = 0).
        5. Coleta o preço promocional (opcional, 0 se não houver).
        6. Coleta quantidade em estoque e categoria.
        7. Registra data_cadastro, data_alteracao e data_atualizacao_preco.
        8. Persiste o produto no banco de dados SQLite.
    """
    print("\n" + "=" * 60)
    print("                CADASTRO DE NOVO PRODUTO                ")
    print("=" * 60)

    # 1. Passo: Validação prévia de Fornecedores Ativos
    fornecedores = carregar_fornecedores_ativos()
    if not fornecedores:
        print("\n⚠️  ATENÇÃO: Nenhum fornecedor ativo encontrado no sistema!")
        print("ℹ️  Para cadastrar um produto, é OBRIGATÓRIO vincular um fornecedor.")
        print("👉 Por favor, cadastre primeiro o fornecedor no menu 'Gestão de Fornecedores' antes de prosseguir.\n")
        return

    # 2. Passo: Listagem e Seleção do Fornecedor
    print("\n--- Selecione o Fornecedor do Produto ---")
    print("-" * 75)
    print(f"{'ID':<4} | {'CNPJ':<18} | {'Razão Social':<25} | {'Nome Fantasia'}")
    print("-" * 75)
    ids_fornecedores = []
    for f in fornecedores:
        ids_fornecedores.append(f[0])
        fantasia = f[3] if f[3] else "-"
        print(f"{f[0]:<4} | {f[1]:<18} | {f[2]:<25} | {fantasia}")
    print("-" * 75)

    # Valida se o ID escolhido pertence à lista de fornecedores ativos
    fornecedor_id = obter_fornecedor_id_valido(ids_fornecedores)
    fornecedor_selecionado = buscar_fornecedor_por_id_banco(fornecedor_id)
    print(f"✅ Fornecedor selecionado: {fornecedor_selecionado[2]} (ID: {fornecedor_id})\n")

    # 3. Passo: Coleta e validação dos dados do produto
    nome = obter_nome_produto_valido()
    preco_custo = obter_preco_custo_valido()
    markup = obter_markup_valido()

    # 4. Passo: Precificação (automática com markup > 0 ou manual com markup = 0)
    if markup > 0:
        preco_venda = calcular_preco_venda(preco_custo, markup)
        print(f"💡 Preço de Venda calculado automaticamente (Custo R$ {preco_custo:.2f} x Markup {markup}): R$ {preco_venda:.2f}")
    else:
        print("💡 Markup definido em 0: Informe o preço de venda manualmente.")
        preco_venda = obter_preco_venda_valido(preco_custo=preco_custo)

    # 5. Passo: Preço Promocional (opcional)
    preco_promocao = obter_preco_promocao_valido(preco_venda=preco_venda)
    preco_efetivo, em_promocao = obter_preco_venda_efetivo(preco_venda, preco_promocao)

    if em_promocao:
        print(f"🏷️  PROMOÇÃO ATIVA: O produto será vendido por R$ {preco_efetivo:.2f} (Preço Normal: R$ {preco_venda:.2f})")
    else:
        print(f"🏷️  Sem promoção ativa: Preço de venda praticado será R$ {preco_efetivo:.2f}")

    # 6. Passo: Estoque e Categoria
    quantidade = obter_quantidade_valida()
    categoria = obter_categoria_valida()

    # 7. Passo: Rastreamento temporal de Datas
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    novo_produto = {
        'fornecedor_id': fornecedor_id,
        'nome': nome,
        'preco_custo': preco_custo,
        'markup': markup,
        'preco_venda': preco_venda,
        'preco_promocao': preco_promocao,
        'quantidade': quantidade,
        'categoria': categoria,
        'data_cadastro': data_atual,
        'data_alteracao': data_atual,
        'data_atualizacao_preco': data_atual
    }

    # 8. Passo: Salvar no banco de dados SQLite
    salvar_produto(novo_produto)
    print(f"\n✅ Produto '{nome}' cadastrado com sucesso!")
    print(f"📦 Fornecedor: {fornecedor_selecionado[2]} | Custo: R$ {preco_custo:.2f} | Venda: R$ {preco_venda:.2f} | Promoção: {'R$ ' + f'{preco_promocao:.2f}' if em_promocao else 'Nenhuma'}")
    print(f"💵 Preço Efetivo para Venda: R$ {preco_efetivo:.2f}")
    print(f"🕒 Data de Cadastro: {data_atual}")


def listar_produtos() -> None:
    """
    Recupera e exibe em formato tabular todos os produtos ativos (ativo = 1),
    mostrando Fornecedor, Custo, Markup, Preço de Venda, Preço de Promoção, 
    Preço Efetivo praticado, Estoque, Categoria e Datas.
    """
    print("\n" + "=" * 148)
    print("                                                 LISTA DE PRODUTOS ATIVOS                                                 ")
    print("=" * 148)

    produtos = carregar_produtos()
    if not produtos:
        print("⚠️ Nenhum produto ativo encontrado no sistema.")
        return

    print(f"{'ID':<4} | {'Produto':<18} | {'Fornecedor':<18} | {'Custo':<9} | {'Markup':<7} | {'Venda (R$)':<10} | {'Promoção':<10} | {'Preço Final':<11} | {'Qtd':<4} | {'Categoria':<10} | {'Cadastrado Em':<19}")
    print("-" * 148)
    for p in produtos:
        id_prod = p[0]
        nome = p[1]
        custo = p[2]
        markup = p[3]
        venda = p[4]
        promo = p[5] if p[5] is not None else 0.0
        qtd = p[6]
        cat = p[7] if p[7] else "-"
        data_cad = p[8]
        fornecedor_nome = p[12]  # Razão Social do fornecedor
        
        # Determina o preço de venda efetivo (se tem promoção ou venda normal)
        preco_efetivo, em_promocao = obter_preco_venda_efetivo(venda, promo)
        
        promo_str = f"R$ {promo:.2f}" if em_promocao else "-"
        final_str = f"R$ {preco_efetivo:.2f}*" if em_promocao else f"R$ {preco_efetivo:.2f}"
        
        # Limita o tamanho dos textos longos para não quebrar a formatação da tabela
        nome_fmt = (nome[:16] + "..") if len(nome) > 18 else nome
        forn_fmt = (fornecedor_nome[:16] + "..") if len(fornecedor_nome) > 18 else fornecedor_nome
        
        print(f"{id_prod:<4} | {nome_fmt:<18} | {forn_fmt:<18} | R$ {custo:<6.2f} | {markup:>5.2f}x | R$ {venda:<7.2f} | {promo_str:<10} | {final_str:<11} | {qtd:<4} | {cat:<10} | {data_cad:<19}")
    print("-" * 148)
    print("(*) Indica produto com Preço Promocional ativo para venda.")


def consultar_produto() -> None:
    """
    Solicita um termo ao usuário e busca produtos ativos cujo nome contenha
    o texto pesquisado (LIKE), exibindo dados detalhados do item, fornecedor, preços e promoção.
    """
    print("\n--- Consulta de Produto por Nome ---")
    termo = input("Digite o nome (ou parte dele) para pesquisar: ").strip()

    if not termo:
        print("❌ Erro: Digite pelo menos um caractere para pesquisar.")
        return

    produtos = buscar_produtos_por_nome_banco(termo)
    if not produtos:
        print(f"⚠️ Nenhum produto encontrado com o termo '{termo}'.")
        return

    print("\n" + "-" * 85)
    for p in produtos:
        id_prod = p[0]
        nome = p[1]
        custo = p[2]
        markup = p[3]
        venda = p[4]
        promo = p[5] if p[5] is not None else 0.0
        qtd = p[6]
        cat = p[7] if p[7] else "Nenhuma"
        data_cad = p[8]
        data_alt = p[9]
        data_preco = p[10]
        forn_id = p[11]
        forn_razao = p[12]
        
        preco_efetivo, em_promocao = obter_preco_venda_efetivo(venda, promo)

        print(f"📦 ID: {id_prod} - Produto: {nome}")
        print(f"🏢 Fornecedor: {forn_razao} (ID: {forn_id})")
        print(f"💰 Custo: R$ {custo:.2f} | Markup: {markup:.2f}x | Preço Venda Normal: R$ {venda:.2f}")
        if em_promocao:
            print(f"🏷️  PROMOÇÃO ATIVA: R$ {promo:.2f} 🔥 (Desconto aplicado)")
            print(f"🛒 Preço Praticado na Venda: R$ {preco_efetivo:.2f}")
        else:
            print("🏷️  Promoção: Nenhuma ativa (Preço Praticado: R$ {:.2f})".format(preco_efetivo))
        print(f"📊 Estoque: {qtd} unidades | Categoria: {cat}")
        print(f"📅 Data de Cadastro: {data_cad}")
        print(f"🔄 Última Alteração Geral: {data_alt}")
        print(f"💲 Última Atualização de Preço: {data_preco}")
        print("-" * 85)


def editar_produto() -> None:
    """
    Lista os produtos ativos, solicita o ID a editar e permite atualizar todos os campos:
        - Fornecedor vinculado (com validação de existência)
        - Nome, Preço de Custo e Markup multiplicador
        - Preço de Venda (recalculado ou manual)
        - Preço Promocional (permite adicionar, alterar ou remover informando 0)
        - Quantidade e Categoria
        - Atualização dos timestamps de alteração.
    """
    print("\n--- Edição / Alteração de Produto ---")
    listar_produtos()

    try:
        produto_id = int(input("\nDigite o ID do produto que deseja editar: ").strip())
    except ValueError:
        print("❌ ID inválido! Digite apenas números.")
        return

    # Busca os dados atuais do produto no banco
    produto = buscar_produto_por_id_banco(produto_id)
    if not produto:
        print("❌ Produto não encontrado ou inativo.")
        return

    id_prod, nome_antigo, custo_antigo, markup_antigo, venda_antiga, promo_antiga, qtd_antiga, cat_antiga, data_cad, data_alt_antiga, data_preco_antiga, forn_antigo_id, forn_antigo_razao, forn_antigo_fantasia = produto

    promo_antiga = promo_antiga if promo_antiga is not None else 0.0
    preco_efetivo_antigo, em_promo_antiga = obter_preco_venda_efetivo(venda_antiga, promo_antiga)

    print(f"\n✏️  Editando Produto: {nome_antigo} (ID: {id_prod})")
    print(f"🏢 Fornecedor Atual: {forn_antigo_razao} (ID: {forn_antigo_id})")
    print(f"💵 Valores Atuais -> Custo: R$ {custo_antigo:.2f} | Markup: {markup_antigo}x | Venda: R$ {venda_antiga:.2f} | Promoção: R$ {promo_antiga:.2f} | Preço Efetivo: R$ {preco_efetivo_antigo:.2f}")
    print("-" * 75)

    # 1. Opção de alterar fornecedor
    fornecedores = carregar_fornecedores_ativos()
    ids_fornecedores = [f[0] for f in fornecedores]
    
    trocar_forn = input("Deseja alterar o fornecedor deste produto? (S/N): ").strip().upper()
    if trocar_forn == "S":
        print("\nFornecedores disponíveis:")
        for f in fornecedores:
            print(f"ID: {f[0]} | Razão Social: {f[2]} | CNPJ: {f[1]}")
        fornecedor_id_novo = obter_fornecedor_id_valido(ids_fornecedores)
    else:
        fornecedor_id_novo = forn_antigo_id

    # 2. Novos dados do produto
    print("\nPreencha os novos dados cadastrais:")
    nome_novo = obter_nome_produto_valido()
    custo_novo = obter_preco_custo_valido()
    markup_novo = obter_markup_valido()

    # 3. Recálculo ou entrada de preço de venda normal
    if markup_novo > 0:
        venda_nova = calcular_preco_venda(custo_novo, markup_novo)
        print(f"💡 Preço de Venda recalculado automaticamente (Custo R$ {custo_novo:.2f} x Markup {markup_novo}): R$ {venda_nova:.2f}")
    else:
        print("💡 Markup definido em 0: Informe o preço de venda manualmente.")
        venda_nova = obter_preco_venda_valido(preco_custo=custo_novo)

    # 4. Novo preço promocional
    print(f"Preço promocional atual: R$ {promo_antiga:.2f} (digite novo valor, 0 para desativar ou Enter para manter):")
    promo_nova = obter_preco_promocao_valido(preco_venda=venda_nova)

    preco_efetivo_novo, em_promo_nova = obter_preco_venda_efetivo(venda_nova, promo_nova)
    if em_promo_nova:
        print(f"🏷️  PROMOÇÃO ATIVA: Preço efetivo na venda será R$ {preco_efetivo_novo:.2f}")
    else:
        print(f"🏷️  Sem promoção: Preço efetivo na venda será R$ {preco_efetivo_novo:.2f}")

    qtd_nova = obter_quantidade_valida()
    cat_nova = obter_categoria_valida()

    # 5. Atualização das datas
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data_alteracao = data_atual

    # Se houve alteração nos preços, markup ou promoção, atualiza a data do preço
    if (custo_novo != custo_antigo) or (markup_novo != markup_antigo) or (venda_nova != venda_antiga) or (promo_nova != promo_antiga):
        data_atualizacao_preco = data_atual
        print(f"🕒 Data de alteração de preços atualizada para: {data_atualizacao_preco}")
    else:
        data_atualizacao_preco = data_preco_antiga

    dados_atualizados = {
        'fornecedor_id': fornecedor_id_novo,
        'nome': nome_novo,
        'preco_custo': custo_novo,
        'markup': markup_novo,
        'preco_venda': venda_nova,
        'preco_promocao': promo_nova,
        'quantidade': qtd_nova,
        'categoria': cat_nova,
        'data_alteracao': data_alteracao,
        'data_atualizacao_preco': data_atualizacao_preco
    }

    sucesso = atualizar_produto_banco(produto_id, dados_atualizados)
    if sucesso:
        print("\n✅ Produto atualizado com sucesso!")
        print(f"🕒 Data da Alteração: {data_alteracao}")
    else:
        print("\n❌ Falha ao atualizar produto no banco de dados.")


def inativar_produto_funcao() -> None:
    """
    Solicita o ID de um produto ativo, pede confirmação do usuário (S/N)
    e realiza a exclusão lógica (Soft Delete) alterando o campo 'ativo' para 0.
    """
    print("\n--- Inativar Produto (Soft Delete) ---")
    listar_produtos()

    try:
        produto_id = int(input("\nDigite o ID do produto que deseja inativar: ").strip())
    except ValueError:
        print("❌ ID inválido! Digite apenas números.")
        return

    produto = buscar_produto_por_id_banco(produto_id)
    if not produto:
        print("❌ Produto não encontrado ou já inativo.")
        return

    confirmacao = input(f"Tem certeza que deseja inativar o produto '{produto[1]}' (ID: {produto[0]})? (S/N): ").strip().upper()

    if confirmacao == "S":
        sucesso = inativar_produto_banco(produto_id)
        if sucesso:
            print("\n✅ Produto inativado com sucesso!")
        else:
            print("\n❌ Não foi possível inativar o produto.")
    else:
        print("\nOperação cancelada.")


# Alias para compatibilidade com outros módulos
excluir_produto = inativar_produto_funcao
inativar_produto = inativar_produto_funcao
