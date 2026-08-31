# 🏢 Sistema de Gestão de Clientes e Fornecedores

Sistema de cadastro e gestão de entidades desenvolvido em Python com persistência em SQLite. O projeto utiliza uma arquitetura modular em camadas, separando as responsabilidades de interface (CLI), regras de negócio/validação e persistência de dados, incluindo regras de **Soft Delete** (exclusão lógica).

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Banco de Dados:** SQLite3
- **Biblioteca Nativa:** `re` (Expressões Regulares para validação e formatação)

---

## 🏗️ Arquitetura do Projeto

A aplicação segue uma estrutura modular para facilitar a manutenção e escalabilidade do código:

```text
Sistema de Gestão/
│
├── sistema.db              # Banco de dados SQLite (gerado automaticamente)
├── persistencia.py         # Camada de dados (conexões, consultas SQL e CRUD)
│
├── validadores.py          # Validações de entradas (nome, e-mail, telefone, etc.)
├── funcoes_clientes.py     # Regras de negócio do módulo de Clientes
├── funcoes_fornecedores.py # Regras de negócio do módulo de Fornecedores (com máscara CNPJ)
│
├── menu_clientes.py        # Interface CLI para gestão de Clientes
├── menu_fornecedores.py    # Interface CLI para gestão de Fornecedores
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