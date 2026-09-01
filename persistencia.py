"""
Módulo de Persistência de Dados
Responsável por toda a comunicação com o banco de dados SQLite (sistema.db),
incluindo criação de tabelas, migração automática, transações atômicas seguras,
consultas, inserções, atualizações, exclusão lógica (soft delete),
gestão completa de filiais e centros de distribuição, controle de saldos,
precificação multi-loja e auditoria de movimentações de estoque (Kardex).
"""

import sqlite3
import time
from contextlib import contextmanager

NOME_BANCO = "sistema.db"
MAX_RETRIES = 3
RETRY_DELAY = 0.4  # segundos


# ==========================================
# GERENCIAMENTO DE CONEXÃO & TRAVA DE RESILIÊNCIA
# ==========================================

def obter_conexao(timeout: float = 10.0) -> sqlite3.Connection:
    """
    Abre e retorna uma conexão com o banco de dados SQLite com timeout e foreign keys ativadas.
    Implementa mecanismo de retry automático contra bloqueios temporários de arquivo ou I/O.
    """
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            conn = sqlite3.connect(NOME_BANCO, timeout=timeout)
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except (sqlite3.OperationalError, sqlite3.DatabaseError) as err:
            if tentativa < MAX_RETRIES:
                time.sleep(RETRY_DELAY * tentativa)
            else:
                print(f"\n🚨 [TRAVA DE SEGURANÇA]: Erro crítico ao conectar com o banco de dados ({NOME_BANCO}): {err}")
                raise


@contextmanager
def transacao_banco(timeout: float = 10.0):
    """
    Context manager para transações atômicas com tratamento rigoroso de exceções e ROLLBACK automático.
    """
    conn = obter_conexao(timeout=timeout)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except (sqlite3.OperationalError, sqlite3.DatabaseError, Exception) as err:
        conn.rollback()
        print(f"\n🚨 [TRAVA DE SEGURANÇA]: Falha na operação. Transação revertida (Rollback): {err}")
        raise
    finally:
        conn.close()


# ==========================================
# INICIALIZAÇÃO E MIGRAÇÃO DO BANCO DE DADOS
# ==========================================

def inicializar_banco() -> None:
    """
    Cria o arquivo do banco de dados (se não existir), inicializa todas as tabelas
    (clientes, fornecedores, lojas, produtos, saldos, precos, movimentacoes_estoque)
    e executa a migração transparente de modelos legados.
    """
    with transacao_banco() as cursor:
        # 1. Tabela Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                sexo TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                ativo INTEGER DEFAULT 1
            );
        """)

        # 2. Tabela Fornecedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cnpj VARCHAR(18) NOT NULL UNIQUE CHECK (length(cnpj) = 18 AND cnpj LIKE '__.___.___/____-__'),
                razao_social TEXT NOT NULL,
                nome_fantasia TEXT,
                endereco TEXT,
                uf VARCHAR(2),
                telefone TEXT,
                contato TEXT,
                ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
            );
        """)

        # 3. Tabela Lojas / Filiais / Centros de Distribuição
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lojas';")
        tabela_lojas_existe = cursor.fetchone() is not None

        if tabela_lojas_existe:
            cursor.execute("PRAGMA table_info(lojas);")
            colunas_lojas = [col[1] for col in cursor.fetchall()]
            if "nome_fantasia" not in colunas_lojas:
                # Migração da tabela lojas antiga para a nova estrutura rica
                cursor.execute("""
                    CREATE TABLE lojas_nova (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT NOT NULL DEFAULT 'LOJA_FISICA',
                        codigo TEXT NOT NULL UNIQUE,
                        nome_fantasia TEXT NOT NULL,
                        razao_social TEXT,
                        cnpj TEXT NOT NULL DEFAULT '0',
                        telefone TEXT,
                        endereco TEXT,
                        ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
                    );
                """)
                # Copia registros antigos
                cursor.execute("SELECT id, nome, codigo, ativo FROM lojas;")
                lojas_antigas = cursor.fetchall()
                for l in lojas_antigas:
                    l_id, l_nome, l_cod, l_ativo = l
                    tipo_padrao = "CENTRO_DISTRIBUICAO" if "MATRIZ" in l_nome.upper() or "CD" in l_nome.upper() else "LOJA_FISICA"
                    cursor.execute("""
                        INSERT INTO lojas_nova (id, tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco, ativo)
                        VALUES (?, ?, ?, ?, ?, '0', '-', '-', ?);
                    """, (l_id, tipo_padrao, l_cod, l_nome, l_nome, l_ativo))
                
                cursor.execute("DROP TABLE lojas;")
                cursor.execute("ALTER TABLE lojas_nova RENAME TO lojas;")
        else:
            cursor.execute("""
                CREATE TABLE lojas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL DEFAULT 'LOJA_FISICA',
                    codigo TEXT NOT NULL UNIQUE,
                    nome_fantasia TEXT NOT NULL,
                    razao_social TEXT,
                    cnpj TEXT NOT NULL DEFAULT '0',
                    telefone TEXT,
                    endereco TEXT,
                    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
                );
            """)

        # Garante a existência de unidades padrão caso a tabela esteja vazia
        cursor.execute("SELECT COUNT(*) FROM lojas;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO lojas (id, tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco, ativo)
                VALUES (1, 'CENTRO_DISTRIBUICAO', 'CD-MATRIZ', 'Centro de Distribuição Matriz', 'Matriz Geral de Gestão LTDA', '12.345.678/0001-90', '(11) 3333-0001', 'Av. Principal, 1000 - Centro, SP', 1);
            """)
            cursor.execute("""
                INSERT INTO lojas (id, tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco, ativo)
                VALUES (2, 'LOJA_FISICA', 'LOJA-01', 'Filial Shopping', 'Filial Shopping LTDA', '12.345.678/0002-71', '(11) 3333-0002', 'Rua das Flores, 500 - Jardim, SP', 1);
            """)

        # 4. Verificação de Migração da Tabela Movimentações de Estoque
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='movimentacoes_estoque';")
        sql_mov = cursor.fetchone()
        if sql_mov and sql_mov[0] and "CHECK" in sql_mov[0] and "TRANSFERENCIA" not in sql_mov[0]:
            cursor.execute("DROP TABLE IF EXISTS mov_antiga_temp;")
            cursor.execute("ALTER TABLE movimentacoes_estoque RENAME TO mov_antiga_temp;")
            cursor.execute("""
                CREATE TABLE movimentacoes_estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    loja_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                    saldo_anterior INTEGER NOT NULL CHECK (saldo_anterior >= 0),
                    saldo_novo INTEGER NOT NULL CHECK (saldo_novo >= 0),
                    motivo TEXT,
                    data_movimentacao TEXT NOT NULL,
                    FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE,
                    FOREIGN KEY (loja_id) REFERENCES lojas (id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                INSERT INTO movimentacoes_estoque (id, produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao)
                SELECT id, produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao FROM mov_antiga_temp;
            """)
            cursor.execute("DROP TABLE mov_antiga_temp;")

        # 5. Verificação da Tabela Produtos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos';")
        tabela_produtos_existe = cursor.fetchone() is not None

        precisa_migrar_produtos = False
        if tabela_produtos_existe:
            cursor.execute("PRAGMA table_info(produtos);")
            colunas_prod = [col[1] for col in cursor.fetchall()]
            if "quantidade" in colunas_prod or "preco_venda" in colunas_prod:
                precisa_migrar_produtos = True

        if precisa_migrar_produtos:
            cursor.execute("""
                SELECT id, fornecedor_id, nome, preco_custo, markup, preco_venda, 
                       COALESCE(preco_promocao, 0), quantidade, categoria, 
                       data_cadastro, data_alteracao, data_atualizacao_preco, ativo
                FROM produtos;
            """)
            produtos_legados = cursor.fetchall()
            cursor.execute("ALTER TABLE produtos RENAME TO produtos_legado_temp;")

            cursor.execute("""
                CREATE TABLE produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fornecedor_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    categoria TEXT,
                    data_cadastro TEXT NOT NULL,
                    data_alteracao TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
                    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
                );
            """)
            _criar_tabelas_filhas(cursor)

            for prod in produtos_legados:
                p_id, forn_id, nome, custo, markup, venda, promo, qtd, cat, dt_cad, dt_alt, dt_preco, ativo = prod
                cursor.execute("""
                    INSERT INTO produtos (id, fornecedor_id, nome, categoria, data_cadastro, data_alteracao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (p_id, forn_id, nome, cat, dt_cad, dt_alt, ativo))

                for l_id in (1, 2):
                    cursor.execute("""
                        INSERT OR REPLACE INTO precos (produto_id, loja_id, preco_custo, markup, preco_venda, preco_promocao, data_atualizacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, (p_id, l_id, custo, markup, venda, promo, dt_preco))

                cursor.execute("""
                    INSERT OR REPLACE INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                    VALUES (?, ?, ?, 0, ?);
                """, (p_id, 1, qtd, dt_alt))
                cursor.execute("""
                    INSERT OR REPLACE INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                    VALUES (?, ?, 0, 0, ?);
                """, (p_id, 2, dt_alt))

                if qtd > 0:
                    cursor.execute("""
                        INSERT INTO movimentacoes_estoque (produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao)
                        VALUES (?, ?, 'CADASTRO_INICIAL', ?, 0, ?, 'Migração automática de estoque legado', ?);
                    """, (p_id, 1, qtd, qtd, dt_alt))

            cursor.execute("DROP TABLE produtos_legado_temp;")
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fornecedor_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    categoria TEXT,
                    data_cadastro TEXT NOT NULL,
                    data_alteracao TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
                    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
                );
            """)
            _criar_tabelas_filhas(cursor)


def _criar_tabelas_filhas(cursor: sqlite3.Cursor) -> None:
    """Cria as tabelas de precos, saldos e movimentacoes_estoque."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            loja_id INTEGER NOT NULL,
            preco_custo REAL NOT NULL CHECK (preco_custo >= 0),
            markup REAL NOT NULL DEFAULT 0,
            preco_venda REAL NOT NULL CHECK (preco_venda > 0),
            preco_promocao REAL DEFAULT 0 CHECK (preco_promocao >= 0),
            data_atualizacao TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE,
            FOREIGN KEY (loja_id) REFERENCES lojas (id) ON DELETE CASCADE,
            UNIQUE (produto_id, loja_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saldos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            loja_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
            estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
            data_atualizacao TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE,
            FOREIGN KEY (loja_id) REFERENCES lojas (id) ON DELETE CASCADE,
            UNIQUE (produto_id, loja_id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            loja_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            saldo_anterior INTEGER NOT NULL CHECK (saldo_anterior >= 0),
            saldo_novo INTEGER NOT NULL CHECK (saldo_novo >= 0),
            motivo TEXT,
            data_movimentacao TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE,
            FOREIGN KEY (loja_id) REFERENCES lojas (id) ON DELETE CASCADE
        );
    """)


# ==========================================
# PERSISTÊNCIA: FILIAIS & CENTROS DE DISTRIBUIÇÃO
# ==========================================

def cadastrar_filial_banco(dados_filial: dict) -> tuple[bool, str, int]:
    """
    Insere uma nova filial/CD no banco de dados e gera automaticamente
    os saldos (zerados) e preços base para todos os produtos já ativos.
    
    Retorno:
        tuple[bool, str, int]: (sucesso, mensagem, filial_id)
    """
    try:
        with transacao_banco() as cursor:
            # Insere a nova filial
            cursor.execute("""
                INSERT INTO lojas (tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1);
            """, (
                dados_filial['tipo'],
                dados_filial['codigo'],
                dados_filial['nome_fantasia'],
                dados_filial.get('razao_social', ''),
                dados_filial.get('cnpj', '0'),
                dados_filial.get('telefone', ''),
                dados_filial.get('endereco', '')
            ))
            filial_id = cursor.lastrowid

            # Busca todos os produtos ativos existentes
            cursor.execute("SELECT id FROM produtos WHERE ativo = 1;")
            produtos_ativos = [r[0] for r in cursor.fetchall()]

            data_atual = time.strftime("%d/%m/%Y %H:%M:%S")

            # Inicializa saldos zerados e preços padrão para a nova filial
            for p_id in produtos_ativos:
                # Busca preço de referência da Matriz (loja 1) se existir
                cursor.execute("""
                    SELECT preco_custo, markup, preco_venda, preco_promocao 
                    FROM precos WHERE produto_id = ? AND loja_id = 1;
                """, (p_id,))
                preco_base = cursor.fetchone()
                
                custo = preco_base[0] if preco_base else 0.0
                markup = preco_base[1] if preco_base else 0.0
                venda = preco_base[2] if preco_base else 0.0
                promo = preco_base[3] if preco_base else 0.0

                cursor.execute("""
                    INSERT OR IGNORE INTO precos (produto_id, loja_id, preco_custo, markup, preco_venda, preco_promocao, data_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (p_id, filial_id, custo, markup, venda, promo, data_atual))

                cursor.execute("""
                    INSERT OR IGNORE INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                    VALUES (?, ?, 0, 0, ?);
                """, (p_id, filial_id, data_atual))

            return True, f"Filial '{dados_filial['nome_fantasia']}' cadastrada com sucesso! ({len(produtos_ativos)} produtos vinculados)", filial_id
    except sqlite3.IntegrityError:
        return False, f"Já existe uma filial cadastrada com o código '{dados_filial['codigo']}'.", 0
    except Exception as err:
        return False, f"Erro ao cadastrar filial: {err}", 0


def carregar_lojas_ativas() -> list:
    """Recupera todas as filiais/lojas ativas."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco
            FROM lojas
            WHERE ativo = 1
            ORDER BY id ASC;
        """)
        return cursor.fetchall()


# Alias de compatibilidade
carregar_filiais_ativas = carregar_lojas_ativas


def buscar_loja_por_id_banco(loja_id: int):
    """Busca os dados completos de uma filial pelo ID."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco
            FROM lojas
            WHERE id = ? AND ativo = 1;
        """, (loja_id,))
        return cursor.fetchone()


buscar_filial_por_id_banco = buscar_loja_por_id_banco


def buscar_filiais_por_nome_ou_codigo(termo: str) -> list:
    """Busca filiais ativas por nome fantasia, razão social ou código."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, tipo, codigo, nome_fantasia, razao_social, cnpj, telefone, endereco
            FROM lojas
            WHERE (nome_fantasia LIKE ? OR razao_social LIKE ? OR codigo LIKE ?) AND ativo = 1
            ORDER BY id ASC;
        """, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
        return cursor.fetchall()


def atualizar_filial_banco(filial_id: int, dados_atualizados: dict) -> tuple[bool, str]:
    """Atualiza os dados cadastrais de uma filial."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("""
                UPDATE lojas
                SET tipo = ?, codigo = ?, nome_fantasia = ?, razao_social = ?, 
                    cnpj = ?, telefone = ?, endereco = ?
                WHERE id = ? AND ativo = 1;
            """, (
                dados_atualizados['tipo'],
                dados_atualizados['codigo'],
                dados_atualizados['nome_fantasia'],
                dados_atualizados.get('razao_social', ''),
                dados_atualizados.get('cnpj', '0'),
                dados_atualizados.get('telefone', ''),
                dados_atualizados.get('endereco', ''),
                filial_id
            ))
            return True, "Dados da filial atualizados com sucesso!"
    except sqlite3.IntegrityError:
        return False, f"O código '{dados_atualizados['codigo']}' já está sendo utilizado por outra filial."
    except Exception as err:
        return False, f"Erro ao atualizar filial: {err}"


def verificar_saldo_total_filial(filial_id: int) -> int:
    """Retorna a soma total de itens em estoque presentes em uma filial específica."""
    with transacao_banco() as cursor:
        cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM saldos WHERE loja_id = ?;", (filial_id,))
        return cursor.fetchone()[0]


def inativar_filial_banco(filial_id: int) -> tuple[bool, str]:
    """
    Realiza Soft Delete de uma filial com trava de segurança de estoque.
    Impede a inativação se a filial tiver saldo positivo de produtos.
    """
    total_estoque = verificar_saldo_total_filial(filial_id)
    if total_estoque > 0:
        return False, f"Não é possível inativar a filial! Ela ainda possui {total_estoque} unidades de produtos em estoque. Zere ou transfira o estoque antes."

    try:
        with transacao_banco() as cursor:
            cursor.execute("UPDATE lojas SET ativo = 0 WHERE id = ?;", (filial_id,))
            return True, "Filial inativada com sucesso!"
    except Exception as err:
        return False, f"Erro ao inativar filial: {err}"


def transferir_estoque_entre_filiais_banco(produto_id: int, loja_origem_id: int, loja_destino_id: int, 
                                           quantidade: int, motivo: str, data_movimentacao: str) -> tuple[bool, str]:
    """
    Executa a transferência atômica de estoque entre filiais (ex: CD -> Loja).
    Subtrai do estoque da origem, soma no destino e registra duas movimentações no Kardex.
    """
    if loja_origem_id == loja_destino_id:
        return False, "A loja de origem e a loja de destino não podem ser iguais."

    if quantidade <= 0:
        return False, "A quantidade para transferência deve ser maior que zero."

    try:
        with transacao_banco() as cursor:
            # 1. Busca nome das lojas para auditoria
            cursor.execute("SELECT nome_fantasia FROM lojas WHERE id = ?;", (loja_origem_id,))
            origem_nome = cursor.fetchone()[0]
            cursor.execute("SELECT nome_fantasia FROM lojas WHERE id = ?;", (loja_destino_id,))
            destino_nome = cursor.fetchone()[0]

            # 2. Busca saldo na origem
            cursor.execute("SELECT quantidade, estoque_minimo FROM saldos WHERE produto_id = ? AND loja_id = ?;", (produto_id, loja_origem_id))
            saldo_origem_reg = cursor.fetchone()
            saldo_origem = saldo_origem_reg[0] if saldo_origem_reg else 0
            est_min_origem = saldo_origem_reg[1] if saldo_origem_reg else 0

            if saldo_origem < quantidade:
                return False, f"Saldo insuficiente na origem '{origem_nome}'! Saldo disponível: {saldo_origem} un. Solicitado: {quantidade} un."

            # 3. Busca saldo no destino
            cursor.execute("SELECT quantidade, estoque_minimo FROM saldos WHERE produto_id = ? AND loja_id = ?;", (produto_id, loja_destino_id))
            saldo_dest_reg = cursor.fetchone()
            saldo_dest = saldo_dest_reg[0] if saldo_dest_reg else 0
            est_min_dest = saldo_dest_reg[1] if saldo_dest_reg else 0

            # 4. Atualiza saldos
            novo_saldo_origem = saldo_origem - quantidade
            novo_saldo_dest = saldo_dest + quantidade

            cursor.execute("""
                INSERT INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(produto_id, loja_id) DO UPDATE SET
                    quantidade = excluded.quantidade,
                    data_atualizacao = excluded.data_atualizacao;
            """, (produto_id, loja_origem_id, novo_saldo_origem, est_min_origem, data_movimentacao))

            cursor.execute("""
                INSERT INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(produto_id, loja_id) DO UPDATE SET
                    quantidade = excluded.quantidade,
                    data_atualizacao = excluded.data_atualizacao;
            """, (produto_id, loja_destino_id, novo_saldo_dest, est_min_dest, data_movimentacao))

            # 5. Registra no Kardex
            motivo_origem = f"Transferência para {destino_nome} - {motivo}"
            motivo_destino = f"Transferência recebida de {origem_nome} - {motivo}"

            cursor.execute("""
                INSERT INTO movimentacoes_estoque (produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao)
                VALUES (?, ?, 'TRANSFERENCIA_SAIDA', ?, ?, ?, ?, ?);
            """, (produto_id, loja_origem_id, quantidade, saldo_origem, novo_saldo_origem, motivo_origem, data_movimentacao))

            cursor.execute("""
                INSERT INTO movimentacoes_estoque (produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao)
                VALUES (?, ?, 'TRANSFERENCIA_ENTRADA', ?, ?, ?, ?, ?);
            """, (produto_id, loja_destino_id, quantidade, saldo_dest, novo_saldo_dest, motivo_destino, data_movimentacao))

            return True, f"Transferência de {quantidade} unidades de '{origem_nome}' para '{destino_nome}' realizada com sucesso!"
    except Exception as err:
        return False, f"Erro na transferência de estoque: {err}"


# ==========================================
# PERSISTÊNCIA: CLIENTES
# ==========================================

def salvar_cliente(cliente: dict) -> None:
    """Insere um novo cliente ativo no banco de dados com transação segura."""
    with transacao_banco() as cursor:
        cursor.execute("""
            INSERT INTO clientes (nome, idade, sexo, email, telefone)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente['nome'],
            cliente['idade'],
            cliente['sexo'],
            cliente['email'],
            cliente['telefone']
        ))


def carregar_clientes() -> list:
    """Recupera todos os clientes ativos."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, sexo, email, telefone
            FROM clientes
            WHERE ativo = 1
        """)
        return cursor.fetchall()


def buscar_cliente_por_id_banco(cliente_id: int):
    """Busca um cliente ativo específico a partir do seu ID."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, sexo, email, telefone
            FROM clientes
            WHERE id = ? AND ativo = 1
        """, (cliente_id,))
        return cursor.fetchone()


def buscar_clientes_por_nome_banco(nome_busca: str) -> list:
    """Busca clientes ativos por termo parcial no nome."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, sexo, email, telefone 
            FROM clientes 
            WHERE nome LIKE ? AND ativo = 1 
            ORDER BY nome ASC
        """, (f"%{nome_busca}%",))
        return cursor.fetchall()


def atualizar_cliente(cliente_id: int, dados_atualizados: dict) -> None:
    """Atualiza dados cadastrais de um cliente ativo."""
    with transacao_banco() as cursor:
        cursor.execute("""
            UPDATE clientes
            SET nome = ?, idade = ?, sexo = ?, email = ?, telefone = ?
            WHERE id = ? AND ativo = 1
        """, (
            dados_atualizados['nome'],
            dados_atualizados['idade'],
            dados_atualizados['sexo'],
            dados_atualizados['email'],
            dados_atualizados['telefone'],
            cliente_id
        ))


def inativar_cliente(cliente_id: int) -> None:
    """Realiza Soft Delete de um cliente."""
    with transacao_banco() as cursor:
        cursor.execute("UPDATE clientes SET ativo = 0 WHERE id = ?", (cliente_id,))


# ==========================================
# PERSISTÊNCIA: FORNECEDORES
# ==========================================

def cadastrar_fornecedor_banco(cnpj: str, razao_social: str, nome_fantasia: str = "", 
                             endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
    """Insere um novo fornecedor com verificação de unicidade."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("""
                INSERT INTO fornecedores (cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato))
        print(f"✅ Fornecedor '{razao_social}' cadastrado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ Erro: O CNPJ '{cnpj}' já está cadastrado no banco de dados.")
        return False
    except Exception as err:
        print(f"❌ Erro ao cadastrar fornecedor: {err}")
        return False


def buscar_fornecedor_por_cnpj_banco(cnpj_formatado: str):
    """Busca um fornecedor ativo pelo CNPJ."""
    conn = obter_conexao()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fornecedores WHERE cnpj = ? AND ativo = 1", (cnpj_formatado,))
    fornecedor = cursor.fetchone()
    conn.close()
    return fornecedor


def atualizar_fornecedor_banco(id_fornecedor: int, cnpj: str, razao_social: str, nome_fantasia: str = "", 
                              endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
    """Atualiza dados cadastrais de um fornecedor."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("""
                UPDATE fornecedores 
                SET cnpj = ?, razao_social = ?, nome_fantasia = ?, endereco = ?, 
                    uf = ?, telefone = ?, contato = ?
                WHERE id = ? AND ativo = 1
            """, (cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato, id_fornecedor))
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        print(f"❌ Erro: Já existe outro fornecedor cadastrado com o CNPJ '{cnpj}'.")
        return False
    except Exception as err:
        print(f"❌ Erro ao atualizar fornecedor: {err}")
        return False


def inativar_fornecedor_banco(id_fornecedor: int) -> bool:
    """Realiza Soft Delete de um fornecedor."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("UPDATE fornecedores SET ativo = 0 WHERE id = ?", (id_fornecedor,))
            return cursor.rowcount > 0
    except Exception as err:
        print(f"❌ Erro ao inativar fornecedor: {err}")
        return False


def carregar_fornecedores_ativos() -> list:
    """Recupera todos os fornecedores ativos."""
    with transacao_banco() as cursor:
        cursor.execute("SELECT id, cnpj, razao_social, nome_fantasia FROM fornecedores WHERE ativo = 1 ORDER BY razao_social ASC;")
        return cursor.fetchall()


def buscar_fornecedor_por_id_banco(fornecedor_id: int):
    """Busca um fornecedor ativo pelo ID."""
    with transacao_banco() as cursor:
        cursor.execute("SELECT id, cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato FROM fornecedores WHERE id = ? AND ativo = 1;", (fornecedor_id,))
        return cursor.fetchone()


def buscar_fornecedores_por_razao_banco(termo_busca: str) -> list:
    """Busca fornecedores ativos por razão social ou nome fantasia."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT id, cnpj, razao_social, nome_fantasia 
            FROM fornecedores 
            WHERE (razao_social LIKE ? OR nome_fantasia LIKE ?) AND ativo = 1 
            ORDER BY razao_social ASC
        """, (f"%{termo_busca}%", f"%{termo_busca}%"))
        return cursor.fetchall()


# ==========================================
# PERSISTÊNCIA: PRODUTOS, SALDOS, PREÇOS & KARDEX
# ==========================================

def salvar_produto_completo(dados_produto: dict, dados_preco: dict, dados_saldo: dict) -> int:
    """
    Insere atomicamente o produto, seus preços nas filiais e seu saldo inicial com auditoria.
    """
    with transacao_banco() as cursor:
        cursor.execute("""
            INSERT INTO produtos (fornecedor_id, nome, categoria, data_cadastro, data_alteracao, ativo)
            VALUES (?, ?, ?, ?, ?, 1);
        """, (
            dados_produto['fornecedor_id'],
            dados_produto['nome'],
            dados_produto.get('categoria', ''),
            dados_produto['data_cadastro'],
            dados_produto['data_alteracao']
        ))
        produto_id = cursor.lastrowid

        # Recupera todas as lojas ativas
        cursor.execute("SELECT id FROM lojas WHERE ativo = 1;")
        lojas = [row[0] for row in cursor.fetchall()]

        loja_alvo = dados_preco.get('loja_id', 1)

        # Preços para todas as lojas
        for l_id in lojas:
            custo = dados_preco['preco_custo']
            markup = dados_preco['markup']
            venda = dados_preco['preco_venda']
            promo = dados_preco.get('preco_promocao', 0.0) if l_id == loja_alvo else 0.0
            
            cursor.execute("""
                INSERT INTO precos (produto_id, loja_id, preco_custo, markup, preco_venda, preco_promocao, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (produto_id, l_id, custo, markup, venda, promo, dados_preco['data_atualizacao']))

        # Saldos para todas as lojas
        qtd_inicial = dados_saldo.get('quantidade', 0)
        est_min = dados_saldo.get('estoque_minimo', 0)
        
        for l_id in lojas:
            qtd = qtd_inicial if l_id == loja_alvo else 0
            cursor.execute("""
                INSERT INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                VALUES (?, ?, ?, ?, ?);
            """, (produto_id, l_id, qtd, est_min, dados_saldo['data_atualizacao']))

            if qtd > 0:
                cursor.execute("""
                    INSERT INTO movimentacoes_estoque (produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao)
                    VALUES (?, ?, 'CADASTRO_INICIAL', ?, 0, ?, 'Saldo inicial no cadastro do produto', ?);
                """, (produto_id, l_id, qtd, qtd, dados_saldo['data_atualizacao']))

        return produto_id


def carregar_produtos(loja_id: int = 1) -> list:
    """
    Recupera produtos ativos trazendo o fornecedor, o preço e o saldo da loja selecionada.
    """
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT p.id, p.nome, 
                   COALESCE(pr.preco_custo, 0.0), 
                   COALESCE(pr.markup, 0.0), 
                   COALESCE(pr.preco_venda, 0.0), 
                   COALESCE(pr.preco_promocao, 0.0),
                   COALESCE(s.quantidade, 0), 
                   p.categoria, 
                   p.data_cadastro, 
                   p.data_alteracao, 
                   COALESCE(pr.data_atualizacao, p.data_alteracao),
                   p.fornecedor_id, 
                   f.razao_social, 
                   f.nome_fantasia,
                   COALESCE(l.nome_fantasia, 'Geral'),
                   COALESCE(s.estoque_minimo, 0)
            FROM produtos p
            INNER JOIN fornecedores f ON p.fornecedor_id = f.id
            LEFT JOIN precos pr ON p.id = pr.produto_id AND pr.loja_id = ?
            LEFT JOIN saldos s ON p.id = s.produto_id AND s.loja_id = ?
            LEFT JOIN lojas l ON l.id = ?
            WHERE p.ativo = 1
            ORDER BY p.nome ASC;
        """, (loja_id, loja_id, loja_id))
        return cursor.fetchall()


def buscar_produto_por_id_banco(produto_id: int, loja_id: int = 1):
    """Busca um produto ativo específico trazendo dados de preço e saldo para a loja solicitada."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT p.id, p.nome, 
                   COALESCE(pr.preco_custo, 0.0), 
                   COALESCE(pr.markup, 0.0), 
                   COALESCE(pr.preco_venda, 0.0), 
                   COALESCE(pr.preco_promocao, 0.0),
                   COALESCE(s.quantidade, 0), 
                   p.categoria, 
                   p.data_cadastro, 
                   p.data_alteracao, 
                   COALESCE(pr.data_atualizacao, p.data_alteracao),
                   p.fornecedor_id, 
                   f.razao_social, 
                   f.nome_fantasia,
                   COALESCE(l.nome_fantasia, 'Geral'),
                   COALESCE(s.estoque_minimo, 0)
            FROM produtos p
            INNER JOIN fornecedores f ON p.fornecedor_id = f.id
            LEFT JOIN precos pr ON p.id = pr.produto_id AND pr.loja_id = ?
            LEFT JOIN saldos s ON p.id = s.produto_id AND s.loja_id = ?
            LEFT JOIN lojas l ON l.id = ?
            WHERE p.id = ? AND p.ativo = 1;
        """, (loja_id, loja_id, loja_id, produto_id))
        return cursor.fetchone()


def buscar_produtos_por_nome_banco(nome_busca: str, loja_id: int = 1) -> list:
    """Busca produtos ativos cujo nome contenha o termo pesquisado."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT p.id, p.nome, 
                   COALESCE(pr.preco_custo, 0.0), 
                   COALESCE(pr.markup, 0.0), 
                   COALESCE(pr.preco_venda, 0.0), 
                   COALESCE(pr.preco_promocao, 0.0),
                   COALESCE(s.quantidade, 0), 
                   p.categoria, 
                   p.data_cadastro, 
                   p.data_alteracao, 
                   COALESCE(pr.data_atualizacao, p.data_alteracao),
                   p.fornecedor_id, 
                   f.razao_social, 
                   f.nome_fantasia,
                   COALESCE(l.nome_fantasia, 'Geral'),
                   COALESCE(s.estoque_minimo, 0)
            FROM produtos p
            INNER JOIN fornecedores f ON p.fornecedor_id = f.id
            LEFT JOIN precos pr ON p.id = pr.produto_id AND pr.loja_id = ?
            LEFT JOIN saldos s ON p.id = s.produto_id AND s.loja_id = ?
            LEFT JOIN lojas l ON l.id = ?
            WHERE p.nome LIKE ? AND p.ativo = 1 
            ORDER BY p.nome ASC;
        """, (loja_id, loja_id, loja_id, f"%{nome_busca}%"))
        return cursor.fetchall()


def atualizar_produto_dados_cadastrais(produto_id: int, dados_cadastrais: dict) -> bool:
    """Atualiza dados cadastrais (nome, fornecedor, categoria, data_alteracao) do produto."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("""
                UPDATE produtos
                SET fornecedor_id = ?, nome = ?, categoria = ?, data_alteracao = ?
                WHERE id = ? AND ativo = 1;
            """, (
                dados_cadastrais['fornecedor_id'],
                dados_cadastrais['nome'],
                dados_cadastrais.get('categoria', ''),
                dados_cadastrais['data_alteracao'],
                produto_id
            ))
            return cursor.rowcount > 0
    except Exception as err:
        print(f"❌ Erro ao atualizar dados cadastrais do produto: {err}")
        return False


def inativar_produto_banco(produto_id: int) -> bool:
    """Realiza Soft Delete de um produto."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?;", (produto_id,))
            return cursor.rowcount > 0
    except Exception as err:
        print(f"❌ Erro ao inativar produto no banco: {err}")
        return False


# ==========================================
# GESTÃO DE PREÇOS E PROMOÇÕES POR LOJA
# ==========================================

def obter_precos_produto_todas_lojas(produto_id: int) -> list:
    """Retorna a tabela de preços de um produto em todas as lojas ativas."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT l.id, l.nome_fantasia, l.codigo,
                   COALESCE(pr.preco_custo, 0.0), 
                   COALESCE(pr.markup, 0.0), 
                   COALESCE(pr.preco_venda, 0.0), 
                   COALESCE(pr.preco_promocao, 0.0),
                   COALESCE(pr.data_atualizacao, '-')
            FROM lojas l
            LEFT JOIN precos pr ON l.id = pr.loja_id AND pr.produto_id = ?
            WHERE l.ativo = 1
            ORDER BY l.id ASC;
        """, (produto_id,))
        return cursor.fetchall()


def atualizar_preco_loja_banco(produto_id: int, loja_id: int, preco_custo: float, 
                              markup: float, preco_venda: float, preco_promocao: float, 
                              data_atualizacao: str) -> bool:
    """Atualiza ou insere o preço/promoção de um produto em uma loja específica."""
    try:
        with transacao_banco() as cursor:
            cursor.execute("""
                INSERT INTO precos (produto_id, loja_id, preco_custo, markup, preco_venda, preco_promocao, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(produto_id, loja_id) DO UPDATE SET
                    preco_custo = excluded.preco_custo,
                    markup = excluded.markup,
                    preco_venda = excluded.preco_venda,
                    preco_promocao = excluded.preco_promocao,
                    data_atualizacao = excluded.data_atualizacao;
            """, (produto_id, loja_id, preco_custo, markup, preco_venda, preco_promocao, data_atualizacao))
            return True
    except Exception as err:
        print(f"❌ Erro ao atualizar preço na loja: {err}")
        return False


# ==========================================
# GESTÃO DE ESTOQUE, SALDOS & AUDITORIA KARDEX
# ==========================================

def obter_saldos_produto_todas_lojas(produto_id: int) -> list:
    """Retorna os saldos de um produto em todas as lojas ativas."""
    with transacao_banco() as cursor:
        cursor.execute("""
            SELECT l.id, l.nome_fantasia, l.codigo,
                   COALESCE(s.quantidade, 0),
                   COALESCE(s.estoque_minimo, 0),
                   COALESCE(s.data_atualizacao, '-')
            FROM lojas l
            LEFT JOIN saldos s ON l.id = s.loja_id AND s.produto_id = ?
            WHERE l.ativo = 1
            ORDER BY l.id ASC;
        """, (produto_id,))
        return cursor.fetchall()


def registrar_movimentacao_estoque_banco(produto_id: int, loja_id: int, tipo: str, 
                                        quantidade: int, motivo: str, data_movimentacao: str) -> tuple[bool, str, int]:
    """
    Registra atomicamente a movimentação de estoque (Kardex) e atualiza o saldo na tabela saldos.
    """
    try:
        with transacao_banco() as cursor:
            cursor.execute("SELECT quantidade, estoque_minimo FROM saldos WHERE produto_id = ? AND loja_id = ?;", (produto_id, loja_id))
            registro_saldo = cursor.fetchone()
            
            saldo_anterior = registro_saldo[0] if registro_saldo else 0
            est_minimo = registro_saldo[1] if registro_saldo else 0

            if tipo == "ENTRADA":
                saldo_novo = saldo_anterior + quantidade
                qtd_mov = quantidade
            elif tipo == "SAIDA":
                if quantidade > saldo_anterior:
                    return False, f"Saldo insuficiente! Saldo atual na loja: {saldo_anterior} un. Tentativa de saída: {quantidade} un.", saldo_anterior
                saldo_novo = saldo_anterior - quantidade
                qtd_mov = quantidade
            elif tipo == "AJUSTE":
                saldo_novo = quantidade
                qtd_mov = abs(saldo_novo - saldo_anterior)
                if qtd_mov == 0:
                    return True, "O novo saldo informado é idêntico ao saldo atual. Nenhuma alteração realizada.", saldo_anterior
            else:
                return False, f"Tipo de movimentação '{tipo}' inválido.", saldo_anterior

            cursor.execute("""
                INSERT INTO saldos (produto_id, loja_id, quantidade, estoque_minimo, data_atualizacao)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(produto_id, loja_id) DO UPDATE SET
                    quantidade = excluded.quantidade,
                    data_atualizacao = excluded.data_atualizacao;
            """, (produto_id, loja_id, saldo_novo, est_minimo, data_movimentacao))

            cursor.execute("""
                INSERT INTO movimentacoes_estoque (produto_id, loja_id, tipo, quantidade, saldo_anterior, saldo_novo, motivo, data_movimentacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (produto_id, loja_id, tipo, qtd_mov, saldo_anterior, saldo_novo, motivo, data_movimentacao))

            return True, f"Movimentação de {tipo} ({qtd_mov} un) realizada com sucesso! Novo saldo: {saldo_novo} un.", saldo_novo
    except Exception as err:
        return False, f"Erro ao registrar movimentação de estoque: {err}", 0


def carregar_extrato_kardex_banco(produto_id: int, loja_id: int = None) -> list:
    """
    Retorna o histórico cronológico de movimentações (Kardex) de um produto.
    """
    with transacao_banco() as cursor:
        if loja_id:
            cursor.execute("""
                SELECT m.id, l.nome_fantasia, m.tipo, m.quantidade, m.saldo_anterior, m.saldo_novo, m.motivo, m.data_movimentacao
                FROM movimentacoes_estoque m
                INNER JOIN lojas l ON m.loja_id = l.id
                WHERE m.produto_id = ? AND m.loja_id = ?
                ORDER BY m.id DESC;
            """, (produto_id, loja_id))
        else:
            cursor.execute("""
                SELECT m.id, l.nome_fantasia, m.tipo, m.quantidade, m.saldo_anterior, m.saldo_novo, m.motivo, m.data_movimentacao
                FROM movimentacoes_estoque m
                INNER JOIN lojas l ON m.loja_id = l.id
                WHERE m.produto_id = ?
                ORDER BY m.id DESC;
            """, (produto_id,))
        return cursor.fetchall()