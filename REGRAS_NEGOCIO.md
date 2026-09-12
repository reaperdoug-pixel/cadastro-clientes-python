# Regras de negócio

## Confirmadas

- Cada empresa deverá ter seu próprio banco local ou ambiente em nuvem.
- O administrador possui acesso total.
- Permissões parciais podem ser delegadas por módulo, parametrização e operações CRUD.
- Estoquista é um exemplo de usuário limitado ao estoque.
- Distribuição de estoque ocorre do CD para as lojas.
- Transferência de estoque ocorre entre lojas.
- Vendas ficam fora da primeira versão.
- Integrações externas ficam fora da primeira versão.
- Promoções podem ter início e fim; também foi indicada a possibilidade de permanecerem válidas até o fim do produto.
- Com CD ativo, a Gestão de Estoque exibe Distribuição de Produtos, restrita ao fluxo CD para loja. Sem CD, esta opção não é exibida.
- Transferência de produtos é o fluxo entre unidades; a distribuição é o fluxo específico com origem em CD.
- Movimentação de produtos no menu representa ajuste de inventário e registra `AJUSTE` no Kardex.
- A entrada de nota aceita múltiplos itens e, quando confirmada, atualiza todos os saldos e grava `ENTRADA_NOTA` no Kardex atomicamente.
- Uma promoção é específica de produto e loja, tem número, vigência e responsável. A promoção ativa mais recente e vigente define o preço praticado.
- Perfis implementados: `ADMIN` com acesso total, `ESTOQUISTA` para operações de estoque e `CONSULTA` somente para listagem e Kardex.

## Regras a detalhar

- Hierarquia avançada e permissões customizáveis por ação.
- Empresas, usuários, filiais e isolamento de dados.
- Custos, tributos, cancelamento e devolução de notas de entrada.
- Financeiro.
- Cancelamentos, devoluções, descontos e ajustes.
- Aprovação de alterações sensíveis.
- Retenção e eliminação de dados pessoais.
