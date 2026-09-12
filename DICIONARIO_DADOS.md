# Dicionário de dados — estado atual

| Tabela | Finalidade | Campos principais |
|---|---|---|
| `clientes` | Cadastro de clientes | `id`, `nome`, `idade`, `sexo`, `email`, `telefone`, `ativo` |
| `fornecedores` | Cadastro de fornecedores | `id`, `cnpj`, `razao_social`, `nome_fantasia`, `endereco`, `uf`, `telefone`, `contato`, `ativo` |
| `lojas` | Filiais, CDs e lojas virtuais | `id`, `tipo`, `codigo`, `nome_fantasia`, `razao_social`, `cnpj`, `telefone`, `endereco`, `ativo` |
| `produtos` | Catálogo de produtos | `id`, `fornecedor_id`, `nome`, `categoria`, datas, `ativo` |
| `precos` | Preços por produto e filial | custo, markup, venda, promoção e data de atualização |
| `saldos` | Estoque por produto e filial | quantidade, estoque mínimo e data de atualização |
| `movimentacoes_estoque` | Kardex | tipo, quantidade, saldo anterior/novo, motivo e data |
| `usuarios` | Acesso ao sistema | `id`, `login` único, `senha_hash`, `data_criacao`, `data_exclusao`, `permissoes` |
| `promocoes` | Histórico de promoções por produto e unidade | `id`, `produto_id`, `loja_id`, `numero_promocao`, preço, vigência, status e `usuario_id` |
| `notas_entrada` | Cabeçalho de entrada de mercadorias | `id`, `numero_nota` único, fornecedor, unidade, usuário e datas |
| `itens_notas_entrada` | Itens de uma nota de entrada | `id`, `nota_entrada_id`, `produto_id`, `quantidade` |

## Regras de integridade adicionadas

- `promocoes` possui ID próprio e referencia produto, loja e usuário; assim preserva o histórico de cada produto por unidade.
- O valor promocional vigente vem da promoção ativa, dentro do período informado. O campo legado `precos.preco_promocao` é migrado para `promocoes` e zerado.
- `notas_entrada` e seus itens são gravados junto com saldos e Kardex em uma única transação.
- `usuarios.data_exclusao` representa a inativação lógica; usuários inativos não autenticam.

## Pendências

- Tipos, obrigatoriedade, domínios, chaves, índices e cardinalidades.
- Modelo multiempresa da futura versão web.
- Política de migrações e compatibilidade.
