# 🏢 Sistema de Gestão Empresarial (Clientes, Fornecedores e Produtos)

Sistema de cadastro e gestão comercial desenvolvido em Python com persistência em SQLite. O projeto utiliza uma arquitetura modular em camadas, separando as responsabilidades de interface (CLI), regras de negócio/validação e persistência de dados, com relacionamentos entre tabelas e regras de **Soft Delete** (exclusão lógica).

---

## 📸 Demonstração do Sistema

![Demonstração do Sistema](Print.png)

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Banco de Dados:** SQLite3 (com Chaves Estrangeiras e integridade referencial)
- **Biblioteca Nativa:** `re` (Expressões Regulares para validação e formatação)
- **Módulo `datetime`:** Rastreamento temporal de cadastros, edições gerais e alterações de preço.

---

## 🏗️ Arquitetura do Projeto

A aplicação segue uma estrutura modular para facilitar a manutenção e escalabilidade do código:

```text
Sistema de Gestão/
│
├── sistema.db              # Banco de dados SQLite (gerado automaticamente)
├── persistencia.py         # Camada de dados (conexões, consultas SQL, FKs e CRUD)
│
├── validadores.py          # Validações de entradas (nome, e-mail, telefone, preços, fornecedores, etc.)
├── funcoes_clientes.py     # Regras de negócio do módulo de Clientes
├── funcoes_fornecedores.py # Regras de negócio do módulo de Fornecedores (com máscara CNPJ)
├── funcoes_produtos.py     # Regras de negócio de Produtos (vínculo com fornecedor, markup, datas e recálculo)
│
├── menu_clientes.py        # Interface CLI para gestão de Clientes
├── menu_fornecedores.py    # Interface CLI para gestão de Fornecedores
├── menu_produtos.py        # Interface CLI para gestão de Produtos
└── main.py                 # Ponto de entrada do sistema
```

---

## 🚀 Funcionalidades

### 👥 Módulo de Clientes
- **Cadastro de Clientes:** Coleta e validação de nome, idade, sexo, e-mail e telefone.
- **Listagem e Busca Inteligente:** Consulta de clientes por trecho do nome (`LIKE`).
- **Edição de Dados:** Atualização de informações mantendo validações ativas.
- **Inativação (Soft Delete):** Inativação de registros para preservar o histórico no banco de dados.

### 🏭 Módulo de Fornecedores
- **Cadastro com Máscara de CNPJ:** Formatação automática do CNPJ para o padrão `XX.XXX.XXX/XXXX-XX`.
- **Validação de Unicidade:** Garantia de CNPJ único por fornecedor (`UNIQUE` constraint).
- **Consulta por CNPJ:** Busca direta pelo documento formatado ou apenas numérico.
- **Consulta por Razão Social / Fantasia:** Busca de fornecedores por termo.
- **Edição e Inativação Lógica:** Atualização e desativação sem exclusão física do banco.

### 📦 Módulo de Produtos
- **Vínculo Obrigatório com Fornecedor:**
  - O sistema impede o cadastro de produtos caso não existam fornecedores ativos cadastrados, orientando o usuário a cadastrar o fornecedor primeiro.
  - Seleção interativa e validação do fornecedor responsável pelo produto.
- **Precificação Inteligente e Markup Multiplicador:**
  - Cálculo automático do preço de venda com base no índice multiplicador de markup: $\text{Preço de Venda} = \text{Preço de Custo} \times \text{Markup}$.
    - Exemplo 1: Custo $\text{R\$} 15,00 \times \text{Markup } 2 = \text{R\$} 30,00$.
    - Exemplo 2: Custo $\text{R\$} 10,00 \times \text{Markup } 1,86 = \text{R\$} 18,60$.
  - Se o markup for definido como `0` (sem multiplicador), o sistema permite a digitação manual do preço de venda final.
  - Recálculo automático do preço de venda sempre que o preço de custo ou o markup forem alterados na edição.
- **Preço de Promoção (Preço Efetivo de Venda):**
  - Permite definir um valor promocional manual para o produto.
  - **Regra de Venda**: Se o preço de promoção for informado ($> 0$), o sistema utiliza automaticamente o valor promocional como preço final para a venda. Se estiver com $0$ ou vazio, utiliza o preço de venda normal.
- **Rastreamento Temporal Completo de Datas:**
  - `data_cadastro`: Registra data e hora da inclusão inicial do produto (`DD/MM/AAAA HH:MM:SS`).
  - `data_alteracao`: Atualizada automaticamente a cada modificação cadastral ou geral do produto.
  - `data_atualizacao_preco`: Registra especificamente o momento em que os preços de custo/markup/venda/promoção foram modificados.
- **Listagem Tabular com JOIN:** Exibe ID, Nome do Produto, Fornecedor Vinculado, Custo, Markup (ex: `1.86x`), Preço de Venda, Preço de Promoção, Preço Final Praticado, Estoque, Categoria e Datas.
- **Busca por Nome e Soft Delete:** Consulta detalhada e inativação lógica (`ativo = 0`) com confirmação de segurança.

---

## 🔄 Histórico de Alterações e Melhorias

- **Validação Rigorosa de Nomes (`validadores.py`):**
  - A função `obter_nome_valido()` foi refatorada para aceitar exclusivamente letras (incluindo caracteres acentuados) e espaços, exigindo no mínimo 3 caracteres alfabéticos e bloqueando números ou caracteres especiais misturados.
- **Limpeza de Código e Otimização (`funcoes_clientes.py`):**
  - Remoção de funções legadas/duplicadas que não eram utilizadas (`validar_email()` e `formatar_telefone()`).
  - Remoção da importação não utilizada do módulo `re`, centralizando e padronizando todas as validações de entrada no módulo `validadores.py`.
- **Correção da Estrutura da Documentação (`README.md`):**
  - Formatação corrigida dos blocos de código e inclusão de seções detalhadas de funcionalidades e histórico.

---

## ⚙️ Como Executar

Para iniciar o sistema, execute o comando abaixo no terminal:

```bash
python main.py
```

> **Nota:** O banco de dados `sistema.db` será criado e inicializado automaticamente na primeira execução caso ainda não exista.

---

## 📝 Licença
Este projeto foi desenvolvido para fins educacionais e de estudo.