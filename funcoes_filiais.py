"""
Módulo de Regras de Negócio: Filiais e Centros de Distribuição (CDs)
Responsável por orquestrar a gestão de unidades físicas e virtuais:
Cadastro, Listagem consolidada, Consulta com balanço de estoque,
Edição cadastral, Inativação com trava de segurança de estoque
e Transferência atômica de mercadorias entre filiais.
"""

from datetime import datetime
from validadores import (
    obter_tipo_filial_valido,
    obter_codigo_filial_valido,
    obter_nome_fantasia_filial_valido,
    obter_razao_social_filial_valida,
    obter_cnpj_filial_valido,
    obter_telefone_filial_valido,
    obter_endereco_filial_valido,
    obter_loja_id_valido,
    obter_quantidade_movimentacao_valida,
    obter_motivo_movimentacao
)
from persistencia import (
    cadastrar_filial_banco,
    carregar_filiais_ativas,
    buscar_filial_por_id_banco,
    buscar_filiais_por_nome_ou_codigo,
    atualizar_filial_banco,
    verificar_saldo_total_filial,
    inativar_filial_banco,
    carregar_produtos,
    buscar_produto_por_id_banco,
    transferir_estoque_entre_filiais_banco
)


def formatar_tipo_filial(tipo: str) -> str:
    """Retorna uma descrição amigável com ícone para o tipo de estabelecimento."""
    match tipo:
        case "CENTRO_DISTRIBUICAO":
            return "🏭 CD / Depósito"
        case "LOJA_VIRTUAL":
            return "🌐 Loja Virtual"
        case "LOJA_FISICA" | _:
            return "🏪 Loja Física"


def cadastrar_filial() -> None:
    """
    Cadastra uma nova filial ou Centro de Distribuição no sistema
    e inicializa automaticamente o vínculo com os produtos existentes.
    """
    print("\n" + "=" * 65)
    print("           CADASTRO DE NOVA FILIAL / CENTRO DE DISTRIBUIÇÃO          ")
    print("=" * 65)

    tipo = obter_tipo_filial_valido()
    codigo = obter_codigo_filial_valido()
    nome_fantasia = obter_nome_fantasia_filial_valido()
    razao_social = obter_razao_social_filial_valida()
    cnpj = obter_cnpj_filial_valido()
    telefone = obter_telefone_filial_valido()
    endereco = obter_endereco_filial_valido()

    dados_filial = {
        'tipo': tipo,
        'codigo': codigo,
        'nome_fantasia': nome_fantasia,
        'razao_social': razao_social if razao_social else nome_fantasia,
        'cnpj': cnpj,
        'telefone': telefone,
        'endereco': endereco
    }

    sucesso, mensagem, filial_id = cadastrar_filial_banco(dados_filial)
    if sucesso:
        print(f"\n✅ {mensagem}")
        print(f"🏢 Tipo: {formatar_tipo_filial(tipo)} | Código: {codigo}")
        print(f"📄 CNPJ: {cnpj if cnpj != '0' else 'Sem CNPJ / Isento'}")
        print(f"📞 Telefone: {telefone} | 📍 Endereço: {endereco}")
    else:
        print(f"\n❌ Falha no cadastro da filial: {mensagem}")


def listar_filiais() -> None:
    """
    Exibe em formato tabular todas as filiais e CDs ativos cadastrados,
    incluindo a quantidade total de itens em estoque em cada unidade.
    """
    print("\n" + "=" * 115)
    print("                                      LISTA DE FILIAIS E CDS ATIVOS                                      ")
    print("=" * 115)

    filiais = carregar_filiais_ativas()
    if not filiais:
        print("⚠️ Nenhuma filial ativa encontrada no sistema.")
        return

    print(f"{'ID':<4} | {'Código':<12} | {'Nome Fantasia':<25} | {'Tipo':<18} | {'CNPJ':<18} | {'Telefone':<15} | {'Estoque Total'}")
    print("-" * 115)
    for f in filiais:
        f_id, tipo, codigo, nome_fantasia, razao, cnpj, tel, end = f
        saldo_total = verificar_saldo_total_filial(f_id)
        tipo_txt = formatar_tipo_filial(tipo)
        cnpj_txt = cnpj if cnpj != "0" else "Isento / Sem CNPJ"
        
        nome_fmt = (nome_fantasia[:23] + "..") if len(nome_fantasia) > 25 else nome_fantasia
        print(f"{f_id:<4} | {codigo:<12} | {nome_fmt:<25} | {tipo_txt:<18} | {cnpj_txt:<18} | {tel:<15} | {saldo_total:>6} un")
    print("-" * 115)


def consultar_filial() -> None:
    """
    Pesquisa filiais por nome fantasia, razão social ou código,
    exibindo dados detalhados da unidade e a lista de produtos com estoque nela.
    """
    print("\n--- Consulta de Filiais / Centros de Distribuição ---")
    termo = input("Digite o nome ou código da filial para pesquisar: ").strip()

    if not termo:
        print("❌ Digite pelo menos um caractere para pesquisar.")
        return

    filiais = buscar_filiais_por_nome_ou_codigo(termo)
    if not filiais:
        print(f"⚠️ Nenhuma filial encontrada com o termo '{termo}'.")
        return

    for f in filiais:
        f_id, tipo, codigo, nome_fantasia, razao, cnpj, tel, end = f
        saldo_total = verificar_saldo_total_filial(f_id)
        
        print("\n" + "=" * 80)
        print(f"🏢 FILIAL: {nome_fantasia} (ID: {f_id})")
        print(f"🏷️  Tipo: {formatar_tipo_filial(tipo)} | Código: {codigo}")
        print(f"📄 Razão Social: {razao}")
        print(f"📑 CNPJ: {cnpj if cnpj != '0' else 'Sem CNPJ / Loja Virtual'} | 📞 Telefone: {tel}")
        print(f"📍 Endereço: {end}")
        print(f"📦 Total de Mercadorias em Estoque nesta unidade: {saldo_total} unidades")
        print("-" * 80)

        # Exibe os produtos com saldo nesta filial
        produtos = carregar_produtos(loja_id=f_id)
        if produtos:
            print("Produtos nesta unidade:")
            print(f"{'ID':<4} | {'Produto':<25} | {'Preço Venda':<12} | {'Saldo':<8} | {'Estoque Mínimo'}")
            print("-" * 80)
            for p in produtos:
                p_id = p[0]
                p_nome = p[1]
                p_venda = p[4]
                p_promo = p[5]
                p_qtd = p[6]
                p_min = p[15]
                
                preco_efetivo = p_promo if p_promo > 0 else p_venda
                promo_tag = " 🔥" if p_promo > 0 else ""
                print(f"{p_id:<4} | {p_nome:<25} | R$ {preco_efetivo:<6.2f}{promo_tag} | {p_qtd:<8} | {p_min}")
        print("=" * 80)


def editar_filial() -> None:
    """
    Permite editar dados cadastrais de uma filial/CD ativa.
    """
    print("\n--- Edição de Dados da Filial / CD ---")
    listar_filiais()

    try:
        filial_id = int(input("\nDigite o ID da filial que deseja editar: ").strip())
    except ValueError:
        print("❌ ID inválido! Digite apenas números.")
        return

    filial = buscar_filial_por_id_banco(filial_id)
    if not filial:
        print("❌ Filial não encontrada ou inativa.")
        return

    f_id, tipo_antigo, cod_antigo, nome_antigo, razao_antiga, cnpj_antigo, tel_antigo, end_antigo = filial

    print(f"\n✏️  Editando Filial: {nome_antigo} (Código: {cod_antigo})")
    print(f"Tipo Atual: {formatar_tipo_filial(tipo_antigo)} | CNPJ Atual: {cnpj_antigo}")
    print("-" * 65)

    tipo_novo = obter_tipo_filial_valido()
    codigo_novo = obter_codigo_filial_valido()
    nome_novo = obter_nome_fantasia_filial_valido()
    razao_nova = obter_razao_social_filial_valida()
    cnpj_novo = obter_cnpj_filial_valido()
    tel_novo = obter_telefone_filial_valido()
    end_novo = obter_endereco_filial_valido()

    dados_atualizados = {
        'tipo': tipo_novo,
        'codigo': codigo_novo,
        'nome_fantasia': nome_novo,
        'razao_social': razao_nova if razao_nova else nome_novo,
        'cnpj': cnpj_novo,
        'telefone': tel_novo,
        'endereco': end_novo
    }

    sucesso, mensagem = atualizar_filial_banco(filial_id, dados_atualizados)
    if sucesso:
        print(f"\n✅ {mensagem}")
    else:
        print(f"\n❌ Falha ao atualizar filial: {mensagem}")


def inativar_filial() -> None:
    """
    Realiza Soft Delete de uma filial após conferir a trava de segurança de estoque.
    """
    print("\n--- Inativar Filial / CD (Soft Delete) ---")
    listar_filiais()

    try:
        filial_id = int(input("\nDigite o ID da filial que deseja inativar: ").strip())
    except ValueError:
        print("❌ ID inválido!")
        return

    filial = buscar_filial_por_id_banco(filial_id)
    if not filial:
        print("❌ Filial não encontrada ou já inativa.")
        return

    confirmacao = input(f"Tem certeza que deseja inativar a filial '{filial[3]}' (Código: {filial[2]})? (S/N): ").strip().upper()
    if confirmacao == "S":
        sucesso, mensagem = inativar_filial_banco(filial_id)
        if sucesso:
            print(f"\n✅ {mensagem}")
        else:
            print(f"\n⚠️ {mensagem}")
    else:
        print("\nOperação cancelada.")


def transferir_estoque_filiais() -> None:
    """
    Permite transferir mercadorias de uma filial de origem (ex: CD) para uma filial de destino (ex: Loja).
    """
    print("\n" + "=" * 65)
    print("         TRANSFERÊNCIA DE ESTOQUE ENTRE FILIAIS (CD ➔ LOJA)         ")
    print("=" * 65)

    filiais = carregar_filiais_ativas()
    if len(filiais) < 2:
        print("⚠️ É necessário ter pelo menos 2 filiais cadastradas para realizar transferências.")
        return

    # 1. Seleciona Filial de Origem
    print("\n--- 1. Selecione a Filial de ORIGEM (Saída de Estoque) ---")
    ids_filiais = [f[0] for f in filiais]
    for f in filiais:
        print(f"[{f[0]}] - {f[3]} ({formatar_tipo_filial(f[1])} | Código: {f[2]})")
    
    origem_id = obter_loja_id_valido(ids_filiais)
    origem_info = buscar_filial_por_id_banco(origem_id)

    # 2. Seleciona Filial de Destino
    print(f"\n--- 2. Selecione a Filial de DESTINO (Entrada de Estoque) ---")
    ids_destino = [f_id for f_id in ids_filiais if f_id != origem_id]
    for f in filiais:
        if f[0] != origem_id:
            print(f"[{f[0]}] - {f[3]} ({formatar_tipo_filial(f[1])} | Código: {f[2]})")
            
    destino_id = obter_loja_id_valido(ids_destino)
    destino_info = buscar_filial_por_id_banco(destino_id)

    # 3. Lista produtos com estoque disponível na origem
    print(f"\n--- 3. Selecione o Produto com saldo disponível em '{origem_info[3]}' ---")
    produtos_origem = carregar_produtos(loja_id=origem_id)
    produtos_com_saldo = [p for p in produtos_origem if p[6] > 0]

    if not produtos_com_saldo:
        print(f"⚠️ A filial de origem '{origem_info[3]}' não possui nenhum produto com estoque positivo para transferir.")
        return

    print(f"{'ID':<4} | {'Produto':<25} | {'Saldo Disponível na Origem'}")
    print("-" * 50)
    for p in produtos_com_saldo:
        print(f"{p[0]:<4} | {p[1]:<25} | {p[6]} unidades")
    print("-" * 50)

    try:
        produto_id = int(input("Digite o ID do produto a transferir: ").strip())
    except ValueError:
        print("❌ ID inválido!")
        return

    produto_selecionado = next((p for p in produtos_com_saldo if p[0] == produto_id), None)
    if not produto_selecionado:
        print("❌ Produto não encontrado ou sem saldo disponível na origem informada.")
        return

    saldo_max = produto_selecionado[6]
    print(f"\n📦 Produto: {produto_selecionado[1]} (Saldo atual na origem: {saldo_max} un)")

    # 4. Quantidade e Motivo
    while True:
        qtd_transferir = obter_quantidade_movimentacao_valida()
        if qtd_transferir <= saldo_max:
            break
        print(f"❌ Quantidade solicitada ({qtd_transferir} un) é maior que o saldo disponível ({saldo_max} un)!")

    motivo = obter_motivo_movimentacao()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 5. Executa transferência atômica
    sucesso, mensagem = transferir_estoque_entre_filiais_banco(
        produto_id=produto_id,
        loja_origem_id=origem_id,
        loja_destino_id=destino_id,
        quantidade=qtd_transferir,
        motivo=motivo,
        data_movimentacao=data_atual
    )

    if sucesso:
        print(f"\n✅ {mensagem}")
        print(f"📋 Produto: {produto_selecionado[1]} | Quantidade: {qtd_transferir} un")
        print(f"🚚 Rota: {origem_info[3]} ➔ {destino_info[3]}")
        print(f"🕒 Data: {data_atual} | Motivo: {motivo}")
    else:
        print(f"\n❌ Falha na transferência: {mensagem}")
