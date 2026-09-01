"""
Módulo de Regras de Negócio: Produtos
Responsável por orquestrar a interação com o usuário (coleta e validação de dados),
vínculo obrigatório com fornecedores cadastrados, cálculo de preço de venda e promoção
por filial/loja (com suporte a promoções exclusivas na Loja A sem afetar a Loja B),
controle de saldos de estoque segregados, auditoria de movimentações de estoque (Kardex),
e acionamento dos métodos de persistência transacional com resiliência.
"""

from datetime import datetime
from validadores import (
    obter_nome_produto_valido,
    obter_preco_custo_valido,
    obter_markup_valido,
    obter_preco_venda_valido,
    obter_preco_promocao_valido,
    obter_quantidade_valida,
    obter_estoque_minimo_valido,
    obter_categoria_valida,
    obter_fornecedor_id_valido,
    obter_loja_id_valido,
    obter_tipo_movimentacao_valido,
    obter_motivo_movimentacao,
    obter_quantidade_movimentacao_valida
)
from persistencia import (
    salvar_produto_completo,
    carregar_produtos,
    buscar_produto_por_id_banco,
    buscar_produtos_por_nome_banco,
    atualizar_produto_dados_cadastrais,
    inativar_produto_banco,
    carregar_fornecedores_ativos,
    buscar_fornecedor_por_id_banco,
    carregar_lojas_ativas,
    buscar_loja_por_id_banco,
    obter_precos_produto_todas_lojas,
    atualizar_preco_loja_banco,
    obter_saldos_produto_todas_lojas,
    registrar_movimentacao_estoque_banco,
    carregar_extrato_kardex_banco
)


# ==========================================
# CÁLCULO DE PRECIFICAÇÃO E PROMOÇÃO
# ==========================================

def calcular_preco_venda(preco_custo: float, markup: float, preco_venda_manual: float = None) -> float:
    """
    Calcula o preço de venda final baseado no preço de custo e no markup multiplicador.
    """
    if markup > 0:
        return round(preco_custo * markup, 2)
    elif preco_venda_manual is not None and preco_venda_manual > 0:
        return round(preco_venda_manual, 2)
    return round(preco_custo, 2)


def obter_preco_venda_efetivo(preco_venda: float, preco_promocao: float = 0.0) -> tuple[float, bool]:
    """
    Determina o preço real que deve ser praticado na venda do produto:
    - Se preco_promocao > 0: utiliza o PREÇO DE PROMOÇÃO.
    - Se preco_promocao == 0: utiliza o PREÇO DE VENDA normal.
    """
    if preco_promocao and preco_promocao > 0:
        return round(preco_promocao, 2), True
    return round(preco_venda, 2), False


# ==========================================
# SELEÇÃO AUXILIAR DE LOJAS
# ==========================================

def selecionar_loja_interativa(mensagem: str = "Selecione a Loja:") -> tuple[int, str]:
    """
    Lista as lojas ativas cadastradas e solicita que o usuário selecione uma.
    Retorna (loja_id, nome_loja).
    """
    lojas = carregar_lojas_ativas()
    if not lojas:
        return 1, "Loja Padrão"

    print(f"\n--- {mensagem} ---")
    ids_permitidos = []
    for l in lojas:
        ids_permitidos.append(l[0])
        print(f"[{l[0]}] - {l[1]} (Código: {l[2]})")
    
    loja_id = obter_loja_id_valido(ids_permitidos)
    loja_info = buscar_loja_por_id_banco(loja_id)
    return loja_id, loja_info[1]


# ==========================================
# REGRAS DE NEGÓCIO: CADASTRO E LISTAGEM
# ==========================================

def cadastrar_produto() -> None:
    """
    Cadastra um novo produto no sistema com fornecedor obrigatório,
    preço inicial para as filiais e saldo inicial com registro de auditoria.
    """
    print("\n" + "=" * 65)
    print("                    CADASTRO DE NOVO PRODUTO                    ")
    print("=" * 65)

    # 1. Validação de Fornecedores Ativos
    fornecedores = carregar_fornecedores_ativos()
    if not fornecedores:
        print("\n⚠️  ATENÇÃO: Nenhum fornecedor ativo encontrado no sistema!")
        print("ℹ️  Para cadastrar um produto, é OBRIGATÓRIO vincular um fornecedor.")
        print("👉 Por favor, cadastre primeiro o fornecedor no menu 'Gestão de Fornecedores'.\n")
        return

    # 2. Seleção de Fornecedor
    print("\n--- Selecione o Fornecedor do Produto ---")
    print("-" * 75)
    print(f"{'ID':<4} | {'CNPJ':<18} | {'Razão Social':<25} | {'Nome Fantasia'}")
    print("-" * 75)
    ids_fornecedores = [f[0] for f in fornecedores]
    for f in fornecedores:
        fantasia = f[3] if f[3] else "-"
        print(f"{f[0]:<4} | {f[1]:<18} | {f[2]:<25} | {fantasia}")
    print("-" * 75)

    fornecedor_id = obter_fornecedor_id_valido(ids_fornecedores)
    fornecedor_selecionado = buscar_fornecedor_por_id_banco(fornecedor_id)
    print(f"✅ Fornecedor selecionado: {fornecedor_selecionado[2]} (ID: {fornecedor_id})\n")

    # 3. Dados Cadastrais
    nome = obter_nome_produto_valido()
    categoria = obter_categoria_valida()

    # 4. Loja Base para Cadastro Inicial
    loja_id, loja_nome = selecionar_loja_interativa("Selecione a Loja para o Estoque/Preço Inicial")

    # 5. Precificação
    print(f"\n--- Definição de Preço Inicial ({loja_nome}) ---")
    preco_custo = obter_preco_custo_valido()
    markup = obter_markup_valido()

    if markup > 0:
        preco_venda = calcular_preco_venda(preco_custo, markup)
        print(f"💡 Preço de Venda calculado (Custo R$ {preco_custo:.2f} x Markup {markup}): R$ {preco_venda:.2f}")
    else:
        print("💡 Markup definido em 0: Informe o preço de venda manualmente.")
        preco_venda = obter_preco_venda_valido(preco_custo=preco_custo)

    preco_promocao = obter_preco_promocao_valido(preco_venda=preco_venda)
    preco_efetivo, em_promocao = obter_preco_venda_efetivo(preco_venda, preco_promocao)

    # 6. Estoque Inicial
    print(f"\n--- Definição de Estoque Inicial ({loja_nome}) ---")
    quantidade = obter_quantidade_valida()
    estoque_minimo = obter_estoque_minimo_valido()

    # 7. Timestamps
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    dados_produto = {
        'fornecedor_id': fornecedor_id,
        'nome': nome,
        'categoria': categoria,
        'data_cadastro': data_atual,
        'data_alteracao': data_atual
    }

    dados_preco = {
        'loja_id': loja_id,
        'preco_custo': preco_custo,
        'markup': markup,
        'preco_venda': preco_venda,
        'preco_promocao': preco_promocao,
        'data_atualizacao': data_atual
    }

    dados_saldo = {
        'loja_id': loja_id,
        'quantidade': quantidade,
        'estoque_minimo': estoque_minimo,
        'data_atualizacao': data_atual
    }

    # 8. Salvamento Atômico
    produto_id = salvar_produto_completo(dados_produto, dados_preco, dados_saldo)
    print(f"\n✅ Produto '{nome}' (ID: {produto_id}) cadastrado com sucesso!")
    print(f"🏢 Fornecedor: {fornecedor_selecionado[2]}")
    print(f"🏪 Loja Inicial: {loja_nome} | Saldo: {quantidade} un (Mín: {estoque_minimo})")
    print(f"💰 Custo: R$ {preco_custo:.2f} | Venda Normal: R$ {preco_venda:.2f}")
    if em_promocao:
        print(f"🏷️  PROMOÇÃO ATIVA NESTA LOJA: R$ {preco_efetivo:.2f}")
    print(f"🕒 Cadastrado em: {data_atual}")


def listar_produtos() -> None:
    """
    Recupera e exibe em formato tabular todos os produtos ativos,
    permitindo escolher uma loja específica para conferência de saldo e preço.
    """
    lojas = carregar_lojas_ativas()
    print("\n--- Visualização de Produtos ---")
    print("Selecione a Loja para consulta:")
    ids_lojas = []
    for l in lojas:
        ids_lojas.append(l[0])
        print(f"[{l[0]}] - {l[1]}")
    
    loja_id = obter_loja_id_valido(ids_lojas)
    loja_info = buscar_loja_por_id_banco(loja_id)
    nome_loja = loja_info[1] if loja_info else "Loja Selecionada"

    print("\n" + "=" * 150)
    print(f"                                      LISTA DE PRODUTOS ATIVOS - {nome_loja.upper()}                                      ")
    print("=" * 150)

    produtos = carregar_produtos(loja_id=loja_id)
    if not produtos:
        print("⚠️ Nenhum produto ativo encontrado no sistema.")
        return

    print(f"{'ID':<4} | {'Produto':<18} | {'Fornecedor':<18} | {'Custo':<9} | {'Markup':<7} | {'Venda (R$)':<10} | {'Promoção':<10} | {'Preço Final':<11} | {'Qtd':<4} | {'Mín':<4} | {'Categoria':<10} | {'Cadastrado Em':<19}")
    print("-" * 150)
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
        fornecedor_nome = p[12]
        est_min = p[15]

        preco_efetivo, em_promocao = obter_preco_venda_efetivo(venda, promo)
        promo_str = f"R$ {promo:.2f}" if em_promocao else "-"
        final_str = f"R$ {preco_efetivo:.2f}*" if em_promocao else f"R$ {preco_efetivo:.2f}"

        nome_fmt = (nome[:16] + "..") if len(nome) > 18 else nome
        forn_fmt = (fornecedor_nome[:16] + "..") if len(fornecedor_nome) > 18 else fornecedor_nome

        # Alerta se estoque abaixo do mínimo
        alerta_min = "⚠️" if qtd <= est_min and est_min > 0 else " "

        print(f"{id_prod:<4} | {nome_fmt:<18} | {forn_fmt:<18} | R$ {custo:<6.2f} | {markup:>5.2f}x | R$ {venda:<7.2f} | {promo_str:<10} | {final_str:<11} | {qtd:<4} | {est_min:<4}{alerta_min}| {cat:<10} | {data_cad:<19}")
    print("-" * 150)
    print("(*) Indica preço promocional ativo nesta filial. (⚠️) Indica saldo em alerta de estoque mínimo.")


def consultar_produto() -> None:
    """
    Busca produtos por nome e exibe visão detalhada incluindo tabela de preços
    em todas as lojas e tabela de saldos em todas as lojas.
    """
    print("\n--- Consulta Detalhada de Produto ---")
    termo = input("Digite o nome (ou parte dele) para pesquisar: ").strip()

    if not termo:
        print("❌ Erro: Digite pelo menos um caractere para pesquisar.")
        return

    produtos = buscar_produtos_por_nome_banco(termo)
    if not produtos:
        print(f"⚠️ Nenhum produto encontrado com o termo '{termo}'.")
        return

    for p in produtos:
        id_prod = p[0]
        nome = p[1]
        cat = p[7] if p[7] else "Nenhuma"
        data_cad = p[8]
        data_alt = p[9]
        forn_id = p[11]
        forn_razao = p[12]

        print("\n" + "=" * 80)
        print(f"📦 ID: {id_prod} | PRODUTO: {nome}")
        print(f"🏢 Fornecedor: {forn_razao} (ID: {forn_id}) | Categoria: {cat}")
        print(f"📅 Cadastro: {data_cad} | Última Alteração: {data_alt}")
        print("-" * 80)

        # Exibe Tabela de Preços por Loja
        print("💰 TABELA DE PREÇOS POR LOJA:")
        precos_lojas = obter_precos_produto_todas_lojas(id_prod)
        print(f"{'Loja':<22} | {'Custo':<9} | {'Markup':<7} | {'Venda':<10} | {'Promoção':<10} | {'Preço Praticado'}")
        print("-" * 80)
        for pl in precos_lojas:
            loja_nome = pl[1]
            custo = pl[3]
            mk = pl[4]
            venda = pl[5]
            promo = pl[6]
            preco_ef, em_pr = obter_preco_venda_efetivo(venda, promo)
            promo_txt = f"R$ {promo:.2f}" if em_pr else "Sem Promo"
            praticado_txt = f"R$ {preco_ef:.2f} 🔥 (Promo)" if em_pr else f"R$ {preco_ef:.2f}"
            print(f"{loja_nome:<22} | R$ {custo:<6.2f} | {mk:>5.2f}x | R$ {venda:<7.2f} | {promo_txt:<10} | {praticado_txt}")
        print("-" * 80)

        # Exibe Tabela de Saldos por Loja
        print("📊 TABELA DE ESTOQUE / SALDOS POR LOJA:")
        saldos_lojas = obter_saldos_produto_todas_lojas(id_prod)
        print(f"{'Loja':<22} | {'Saldo Atual':<12} | {'Estoque Mínimo':<15} | {'Última Atualização'}")
        print("-" * 80)
        for sl in saldos_lojas:
            loja_nome = sl[1]
            qtd = sl[3]
            est_m = sl[4]
            dt_att = sl[5]
            print(f"{loja_nome:<22} | {qtd:<12} | {est_m:<15} | {dt_att}")
        print("=" * 80)


def editar_produto() -> None:
    """
    Edita dados cadastrais gerais do produto (Nome, Categoria e Fornecedor).
    """
    print("\n--- Edição de Dados Cadastrais do Produto ---")
    listar_produtos()

    try:
        produto_id = int(input("\nDigite o ID do produto que deseja editar: ").strip())
    except ValueError:
        print("❌ ID inválido! Digite apenas números.")
        return

    produto = buscar_produto_por_id_banco(produto_id)
    if not produto:
        print("❌ Produto não encontrado ou inativo.")
        return

    id_prod, nome_antigo, _, _, _, _, _, cat_antiga, data_cad, data_alt_antiga, _, forn_antigo_id, forn_antigo_razao, _, _, _ = produto

    print(f"\n✏️  Editando Produto: {nome_antigo} (ID: {id_prod})")
    print(f"🏢 Fornecedor Atual: {forn_antigo_razao} (ID: {forn_antigo_id})")

    # Opção de alterar fornecedor
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

    nome_novo = obter_nome_produto_valido()
    cat_nova = obter_categoria_valida()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    dados_atualizados = {
        'fornecedor_id': fornecedor_id_novo,
        'nome': nome_novo,
        'categoria': cat_nova,
        'data_alteracao': data_atual
    }

    sucesso = atualizar_produto_dados_cadastrais(produto_id, dados_atualizados)
    if sucesso:
        print("\n✅ Dados cadastrais do produto atualizados com sucesso!")
        print("ℹ️  Para alterar preços, promoções ou movimentar estoque, use as opções específicas do menu.")
    else:
        print("\n❌ Falha ao atualizar dados cadastrais do produto.")


# ==========================================
# REGRAS DE NEGÓCIO: PREÇOS E PROMOÇÕES POR LOJA
# ==========================================

def gerenciar_precos_promocoes() -> None:
    """
    Permite gerenciar preços e promoções específicas para uma loja/filial.
    Exemplo: aplicar promoção de R$ 35 na Loja A mantendo R$ 50 na Loja B.
    """
    print("\n" + "=" * 65)
    print("           GERENCIAMENTO DE PREÇOS E PROMOÇÕES POR LOJA           ")
    print("=" * 65)

    listar_produtos()
    try:
        produto_id = int(input("\nDigite o ID do produto: ").strip())
    except ValueError:
        print("❌ ID inválido!")
        return

    produto = buscar_produto_por_id_banco(produto_id)
    if not produto:
        print("❌ Produto não encontrado.")
        return

    print(f"\n📦 Produto Selecionado: {produto[1]} (ID: {produto[0]})")
    loja_id, loja_nome = selecionar_loja_interativa("Selecione a Loja para ajustar o Preço / Promoção")

    # Exibe preços atuais nesta loja
    precos_atuais = obter_precos_produto_todas_lojas(produto_id)
    preco_loja_atual = next((p for p in precos_atuais if p[0] == loja_id), None)

    if preco_loja_atual:
        custo_atual, mk_atual, venda_atual, promo_atual = preco_loja_atual[3], preco_loja_atual[4], preco_loja_atual[5], preco_loja_atual[6]
        print(f"\nValores atuais em '{loja_nome}':")
        print(f"Custo: R$ {custo_atual:.2f} | Markup: {mk_atual}x | Venda: R$ {venda_atual:.2f} | Promoção: R$ {promo_atual:.2f}")
    else:
        custo_atual, mk_atual, venda_atual, promo_atual = 0.0, 0.0, 0.0, 0.0

    print("\nInforme os novos valores para esta loja:")
    custo_novo = obter_preco_custo_valido()
    markup_novo = obter_markup_valido()

    if markup_novo > 0:
        venda_nova = calcular_preco_venda(custo_novo, markup_novo)
        print(f"💡 Preço de Venda calculado: R$ {venda_nova:.2f}")
    else:
        venda_nova = obter_preco_venda_valido(preco_custo=custo_novo)

    promo_nova = obter_preco_promocao_valido(preco_venda=venda_nova)
    preco_efetivo, em_promocao = obter_preco_venda_efetivo(venda_nova, promo_nova)
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    sucesso = atualizar_preco_loja_banco(produto_id, loja_id, custo_novo, markup_novo, venda_nova, promo_nova, data_atual)
    if sucesso:
        print(f"\n✅ Preço atualizado com sucesso para a filial '{loja_nome}'!")
        if em_promocao:
            print(f"🏷️  PROMOÇÃO EXCLUSIVA ATIVADA EM '{loja_nome}': R$ {preco_efetivo:.2f} (Venda Normal: R$ {venda_nova:.2f})")
        else:
            print(f"💵 Preço de venda normal em '{loja_nome}': R$ {preco_efetivo:.2f} (Sem promoção ativa)")
    else:
        print(f"\n❌ Falha ao atualizar preço na loja '{loja_nome}'.")


# ==========================================
# REGRAS DE NEGÓCIO: MOVIMENTAÇÃO DE ESTOQUE (KARDEX)
# ==========================================

def movimentar_estoque_produto() -> None:
    """
    Realiza uma movimentação de estoque (Entrada, Saída ou Ajuste) para um produto em uma loja específica,
    garantindo integridade de saldo e registro no Kardex.
    """
    print("\n" + "=" * 65)
    print("                 MOVIMENTAÇÃO DE ESTOQUE (KARDEX)                 ")
    print("=" * 65)

    listar_produtos()
    try:
        produto_id = int(input("\nDigite o ID do produto para movimentar: ").strip())
    except ValueError:
        print("❌ ID inválido!")
        return

    produto = buscar_produto_por_id_banco(produto_id)
    if not produto:
        print("❌ Produto não encontrado.")
        return

    print(f"\n📦 Produto: {produto[1]} (ID: {produto[0]})")
    loja_id, loja_nome = selecionar_loja_interativa("Selecione a Loja onde ocorrerá a movimentação")

    # Exibe saldo atual na loja
    saldos = obter_saldos_produto_todas_lojas(produto_id)
    saldo_loja = next((s for s in saldos if s[0] == loja_id), None)
    saldo_atual = saldo_loja[3] if saldo_loja else 0
    print(f"📊 Saldo atual em '{loja_nome}': {saldo_atual} unidades.")

    tipo = obter_tipo_movimentacao_valido()
    
    if tipo == "AJUSTE":
        print(f"\nInforme o novo saldo total apurado em inventário físico (Saldo atual: {saldo_atual}):")
        qtd_mov = obter_quantidade_valida()
    else:
        qtd_mov = obter_quantidade_movimentacao_valida()

    motivo = obter_motivo_movimentacao()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    sucesso, mensagem, novo_saldo = registrar_movimentacao_estoque_banco(
        produto_id=produto_id,
        loja_id=loja_id,
        tipo=tipo,
        quantidade=qtd_mov,
        motivo=motivo,
        data_movimentacao=data_atual
    )

    if sucesso:
        print(f"\n✅ {mensagem}")
        print(f"🏢 Loja: {loja_nome} | Data: {data_atual}")
        print(f"📝 Motivo registrado: {motivo}")
    else:
        print(f"\n❌ Falha na movimentação: {mensagem}")


def consultar_extrato_kardex() -> None:
    """
    Exibe o histórico cronológico detalhado de auditoria de estoque (Kardex) de um produto.
    """
    print("\n--- Extrato de Movimentações de Estoque (Kardex) ---")
    listar_produtos()
    try:
        produto_id = int(input("\nDigite o ID do produto para ver o extrato: ").strip())
    except ValueError:
        print("❌ ID inválido!")
        return

    produto = buscar_produto_por_id_banco(produto_id)
    if not produto:
        print("❌ Produto não encontrado.")
        return

    print(f"\n📦 Extrato Kardex do Produto: {produto[1]} (ID: {produto[0]})")
    extrato = carregar_extrato_kardex_banco(produto_id)

    if not extrato:
        print("⚠️ Nenhuma movimentação registrada para este produto.")
        return

    print("=" * 110)
    print(f"{'ID':<4} | {'Loja':<20} | {'Tipo':<16} | {'Qtd':<5} | {'Anterior':<9} | {'Novo':<6} | {'Data':<19} | {'Motivo'}")
    print("-" * 110)
    for row in extrato:
        mov_id, loja, tipo, qtd, anterior, novo, motivo, dt = row
        print(f"{mov_id:<4} | {loja:<20} | {tipo:<16} | {qtd:<5} | {anterior:<9} | {novo:<6} | {dt:<19} | {motivo}")
    print("=" * 110)


def inativar_produto_funcao() -> None:
    """
    Solicita o ID de um produto ativo e realiza exclusão lógica (Soft Delete).
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


# Aliases para compatibilidade
excluir_produto = inativar_produto_funcao
inativar_produto = inativar_produto_funcao
