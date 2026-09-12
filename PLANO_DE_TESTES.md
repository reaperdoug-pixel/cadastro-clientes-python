# Plano de testes

## Execução

Os testes automatizados ficam em `tests/` e usam somente `unittest`.

```bash
python -m unittest discover -s tests -v
```

Cada caso cria um banco SQLite temporário. O banco real `sistema.db` não deve ser usado nos testes.

## Cobertura inicial

- Inicialização do schema.
- Cadastro e soft delete de clientes e fornecedores.
- Cadastro de produto com preço, saldo inicial e Kardex.
- Entrada, saída e bloqueio de saldo negativo.
- Transferência entre filiais e registros no Kardex.
- Bloqueio de inativação de filial com estoque.
- Isolamento de preços por filial.
- Criação do schema de usuários, promoções e notas de entrada.
- Promoção ativa por produto e loja aplicada ao preço consultado.
- Nota com múltiplos itens: saldo e lançamento `ENTRADA_NOTA` no Kardex.

## Registro

Registrar data, versão do código, ambiente Python, total, aprovados, falhos e erros. O relatório manual anterior de 36 testes é histórico até haver evidência reproduzível.

## Pendências

Testes de CLI completo para autenticação, concorrência, retry, migração de promoção legada, política de senhas, LGPD e critérios de aceite do PRD.
