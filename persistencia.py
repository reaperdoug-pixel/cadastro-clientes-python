import sqlite3

NOME_BANCO = "sistema.db"

# ==========================================
# INICIALIZAÇÃO DO BANCO
# ==========================================

def inicializar_banco():
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    # Tabela Clientes
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

    # Tabela Fornecedores
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

    conn.commit()
    conn.close()


# ==========================================
# PERSISTÊNCIA: CLIENTES
# ==========================================

def salvar_cliente(cliente):
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


def carregar_clientes():
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, idade, sexo, email, telefone
        FROM clientes
        WHERE ativo = 1
    """)
    clientes = cursor.fetchall()

    conn.close()
    return clientes


def buscar_cliente_por_id_banco(cliente_id: int):
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, idade, sexo, email, telefone
        FROM clientes
        WHERE id = ? AND ativo = 1
    """, (cliente_id,))
    cliente = cursor.fetchone()

    conn.close()
    return cliente


def buscar_clientes_por_nome_banco(nome_busca: str):
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, idade, sexo, email, telefone 
        FROM clientes 
        WHERE nome LIKE ? AND ativo = 1 
        ORDER BY nome ASC
    """, (f"%{nome_busca}%",))

    clientes = cursor.fetchall()
    conn.close()
    return clientes


def atualizar_cliente(cliente_id, dados_atualizados):
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


def inativar_cliente(cliente_id):
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes
        SET ativo = 0
        WHERE id = ?
    """, (cliente_id,))

    conn.commit()
    conn.close()


# ==========================================
# PERSISTÊNCIA: FORNECEDORES
# ==========================================

def cadastrar_fornecedor_banco(cnpj: str, razao_social: str, nome_fantasia: str = "", 
                             endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fornecedores (cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato))
        
        conn.commit()
        conn.close()
        print(f"✅ Fornecedor '{razao_social}' cadastrado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ Erro: O CNPJ '{cnpj}' já está cadastrado no banco de dados.")
        return False
    except sqlite3.Error as err:
        print(f"❌ Erro de Banco de Dados: {err}")
        return False


def buscar_fornecedor_por_cnpj_banco(cnpj_formatado: str):
    conn = sqlite3.connect(NOME_BANCO)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM fornecedores 
        WHERE cnpj = ? AND ativo = 1
    """, (cnpj_formatado,))
    
    fornecedor = cursor.fetchone()
    conn.close()
    return fornecedor


def atualizar_fornecedor_banco(id_fornecedor: int, cnpj: str, razao_social: str, nome_fantasia: str = "", 
                              endereco: str = "", uf: str = "", telefone: str = "", contato: str = "") -> bool:
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fornecedores
            SET cnpj = ?, razao_social = ?, nome_fantasia = ?, endereco = ?, uf = ?, telefone = ?, contato = ?
            WHERE id = ? AND ativo = 1
        """, (cnpj, razao_social, nome_fantasia, endereco, uf, telefone, contato, id_fornecedor))
        
        linhas = cursor.rowcount
        conn.commit()
        conn.close()
        
        if linhas > 0:
            print(f"✅ Fornecedor ID {id_fornecedor} atualizado com sucesso!")
            return True
        else:
            print(f"❌ Fornecedor ID {id_fornecedor} não encontrado ou está inativo.")
            return False
    except sqlite3.Error as err:
        print(f"❌ Erro ao atualizar no banco: {err}")
        return False


def inativar_fornecedor_banco(id_fornecedor: int) -> bool:
    try:
        conn = sqlite3.connect(NOME_BANCO)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fornecedores
            SET ativo = 0
            WHERE id = ?
        """, (id_fornecedor,))
        
        linhas = cursor.rowcount
        conn.commit()
        conn.close()
        
        if linhas > 0:
            print(f"✅ Fornecedor ID {id_fornecedor} inativado com sucesso!")
            return True
        else:
            print(f"❌ Fornecedor ID {id_fornecedor} não encontrado.")
            return False
    except sqlite3.Error as err:
        print(f"❌ Erro ao inativar no banco: {err}")
        return False

def buscar_fornecedores_por_nome_banco(termo_busca: str):
    """
    Busca fornecedores ativos cuja Razão Social ou Nome Fantasia contenham o termo digitado.
    """
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cnpj, razao_social, nome_fantasia, telefone, contato
        FROM fornecedores
        WHERE (razao_social LIKE ? OR nome_fantasia LIKE ?) AND ativo = 1
        ORDER BY razao_social ASC
    """, (f"%{termo_busca}%", f"%{termo_busca}%"))

    fornecedores = cursor.fetchall()
    conn.close()
    return fornecedores