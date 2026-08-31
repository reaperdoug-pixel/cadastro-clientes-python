"""
Módulo de Persistência de Dados
Responsável por toda a comunicação com o banco de dados SQLite (sistema.db),
incluindo criação de tabelas, consultas, inserções, atualizações e exclusão lógica (soft delete).
"""

import sqlite3

NOME_BANCO = "sistema.db"

# ==========================================
# INICIALIZAÇÃO DO BANCO DE DADOS
# ==========================================

def inicializar_banco() -> None:
    """
    Cria o arquivo do banco de dados (se não existir) e inicializa as tabelas
    'clientes' e 'fornecedores' com suas respectivas restrições e constraints.
    """
    conn = sqlite3.connect(NOME_BANCO)
    cursor = conn.cursor()

    # Tabela Clientes com campo 'ativo' para controle de Soft Delete
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

    # Tabela Fornecedores com constraint de validação de máscara de CNPJ e unicidade
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

def salvar_cliente(cliente: dict) -> None:
    """
    Insere um novo cliente ativo no banco de dados.
    
    Parâmetros:
        cliente (dict): Dicionário contendo as chaves 'nome', 'idade', 'sexo', 'email' e 'telefone'.
    """
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


def carregar_clientes() -> list:
    """
    Recupera do banco de dados todos os clientes que estão com status ativo (ativo = 1).
    
    Retorno:
        list[tuple]: Lista de tuplas contendo (id, nome, idade, sexo, email, telefone).
    """
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
    """
    Busca um cliente ativo específico a partir do seu ID numérico.
    
    Parâmetros:
        cliente_id (int): Identificador único do cliente.
        
    Retorno:
        tuple | None: Dados do cliente se encontrado e ativo, ou None caso contrário.
    """
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


def buscar_clientes_por_nome_banco(nome_busca: str) -> list:
    """
    Busca clientes ativos cujo nome contenha o termo pesquisado (busca parcial / LIKE).
    
    Parâmetros:
        nome_busca (str): Trecho ou nome completo para pesquisa.
        
    Retorno:
        list[tuple]: Lista de clientes correspondentes ordenados alfabeticamente.
    """
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


def atualizar_cliente(cliente_id: int, dados_atualizados: dict) -> None:
    """
    Atualiza os dados cadastrais de um cliente existente no banco de dados.
    
    Parâmetros:
        cliente_id (int): ID do cliente a ser atualizado.
        dados_atualizados (dict): Dicionário com os novos dados (nome, idade, sexo, email, telefone).
    """
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


def inativar_cliente(cliente_id: int) -> None:
    """
    Realiza a exclusão lógica (Soft Delete) de um cliente, alterando seu campo 'ativo' para 0.
    
    Parâmetros:
        cliente_id (int): ID do cliente a ser inativado.
    """
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
    """
    Insere um novo fornecedor na tabela 'fornecedores'.
    
    Parâmetros:
        cnpj (str): CNPJ formatado no padrão 'XX.XXX.XXX/XXXX-XX'.
        razao_social (str): Razão Social da empresa.
        nome_fantasia (str): Nome Fantasia (opcional).
        endereco (str): Logradouro e número (opcional).
        uf (str): Unidade Federativa de 2 letras (opcional).
        telefone (str): Telefone de contato (opcional).
        contato (str): Nome do responsável pelo contato (opcional).
        
    Retorno:
        bool: True se o cadastro foi realizado com sucesso, False em caso de erro (ex: CNPJ duplicado).
    """
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
    """
    Busca um fornecedor ativo a partir do seu CNPJ formatado.
    
    Parâmetros:
        cnpj_formatado (str): CNPJ com máscara completa.
        
    Retorno:
        sqlite3.Row | None: Objeto com acesso por coluna (ex: fornecedor['razao_social']) ou None.
    """
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
    """
    Atualiza todos os dados de um fornecedor ativo pelo seu ID.
    
    Parâmetros:
        id_fornecedor (int): Identificador único do fornecedor.
        demais parâmetros: Novos dados cadastrais a serem persistidos.
        
    Retorno:
        bool: True se atualizado com sucesso, False se o ID não existir ou houver erro de integridade.
    """
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
    """
    Realiza a exclusão lógica (Soft Delete) do fornecedor, alterando 'ativo' para 0.
    
    Parâmetros:
        id_fornecedor (int): ID do fornecedor a ser inativado.
        
    Retorno:
        bool: True se inativado com sucesso, False se não encontrado.
    """
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


def buscar_fornecedores_por_nome_banco(termo_busca: str) -> list:
    """
    Busca fornecedores ativos cuja Razão Social ou Nome Fantasia contenham o termo pesquisado.
    
    Parâmetros:
        termo_busca (str): Trecho do texto para pesquisa.
        
    Retorno:
        list[tuple]: Lista de fornecedores correspondentes contendo (id, cnpj, razao_social, nome_fantasia, telefone, contato).
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