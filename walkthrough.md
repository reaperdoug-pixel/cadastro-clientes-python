# Walkthrough Consolidado: Gestão de Filiais, Centros de Distribuição (CDs), Saldos, Kardex e Resiliência

Foi implementado com sucesso o novo **Módulo de Gestão de Filiais e Centros de Distribuição (CDs)**, integrando-o de forma nativa com a arquitetura de **Saldos Segregados**, **Preços por Filial** e **Auditoria Kardex**.

---

## 🏢 O que foi implementado no Módulo de Filiais

### 1. Modelagem de Dados & Tipos de Unidades (`persistencia.py`)
- Tabela `lojas` enriquecida:
  - `id`: Identificador numérico único.
  - `tipo`: `LOJA_FISICA`, `CENTRO_DISTRIBUICAO` ou `LOJA_VIRTUAL`.
  - `codigo`: Código identificador único (ex: `CD-SUL`, `LOJA-CENTRO`, `ECOM-SP`).
  - `nome_fantasia`: Nome de exibição principal.
  - `razao_social`: Razão social da empresa.
  - `cnpj`: CNPJ formatado no padrão `XX.XXX.XXX/XXXX-XX` ou `0` / `ISENTO` para lojas virtuais e filiais sem CNPJ próprio.
  - `telefone` e `endereco`.
  - `ativo`: Controle de Soft Delete.

---

### 2. Regras de Negócio e Segurança de Filiais (`funcoes_filiais.py` e `persistencia.py`)

1. **Auto-vínculo no Cadastro de Filial**:
   - Ao cadastrar um novo CD ou Loja, o sistema gera automaticamente os registros de `saldos` (zerados) e `precos` (herdando o padrão da matriz) para todos os produtos ativos existentes.
2. **Trava de Segurança na Inativação**:
   - Uma filial/CD **não pode ser inativada** se ainda contiver saldo positivo em algum produto (`quantidade > 0`). O sistema impede a exclusão lógica e orienta o operador a zerar ou transferir o estoque antes.
3. **Transferência de Estoque entre Filiais (CD ➔ Loja)**:
   - Permite transferir mercadorias de uma unidade de origem para uma unidade de destino em uma única transação atômica.
   - O Kardex audita a movimentação com `TRANSFERENCIA_SAIDA` na origem e `TRANSFERENCIA_ENTRADA` no destino com seus respectivos motivos.
4. **Consulta com Balanço em Tempo Real**:
   - A consulta de filiais exibe a soma total de peças em estoque e a lista de produtos com saldo naquela unidade.

---

### 3. Navegação CLI e Menus (`main.py` e `menu_filiais.py`)

No **Menu Principal (`main.py`)**:
- `1. Gestão de Clientes`
- `2. Gestão de Fornecedores`
- `3. Gestão de Produtos`
- `4. Gestão de Filiais e Depósitos (CD)` *(Novo)*
- `5. Sair do Sistema`

No **Submenu de Filiais (`menu_filiais.py`)**:
- `1. Cadastrar Nova Filial / CD`
- `2. Listar Todas as Filiais Ativas`
- `3. Consultar Filial por Nome ou Código`
- `4. Editar Dados da Filial / CD`
- `5. Inativar Filial (Soft Delete)`
- `6. Transferência de Estoque (CD ➔ Loja)`
- `7. Voltar ao Menu Principal`

---

## 🧪 Validação dos Testes Automatizados

Executados 100% com sucesso:
- **Cadastro e Inicialização de Filiais**: CD e Loja Virtual criados e vinculados a produtos existentes.
- **Transferência Atômica de Estoque**: 10 unidades transferidas do `CD-SUL` para a `Loja Virtual ECOM-SP`, atualizando saldos e Kardex.
- **Trava de Inativação**: Tentativa de inativar filial com 50 unidades bloqueada com sucesso; filial vazia inativada normalmente.
- **Transações Atômicas**: Rollback automático em caso de falha de conexão ou erro operacional.
