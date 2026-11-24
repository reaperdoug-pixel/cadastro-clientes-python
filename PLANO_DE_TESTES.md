# Plano de testes

## Execução

Os testes automatizados ficam em `tests/` e usam somente `unittest`.

```bash
python -m unittest discover -s tests -v
```

Cada caso cria um banco SQLite temporário. O banco real `sistema.db` não deve ser usado nos testes.

No Linux, após ativar `.venv`, também é possível usar `./scripts/verificar.sh`. No Windows (PowerShell), use `./scripts/verificar.ps1`. Os dois scripts priorizam o Python da `.venv` e caem para o interpretador do sistema se ela não existir ou não for utilizável neste sistema operacional.

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
- Hash e validação de senha, usuário inativo, primeiro administrador e proteção contra inativação da própria sessão.
- Acesso do perfil `CONSULTA` ao menu principal e às opções exclusivamente de leitura do estoque.
- Rollback integral de nota inválida, número de nota único e migração idempotente de promoção legada.
- Retry de conexão SQLite após bloqueio temporário.

## Registro

Registrar data, versão do código, ambiente Python, total, aprovados, falhos e erros. O relatório manual anterior de 36 testes é histórico até haver evidência reproduzível.

## Pendências

Testes completos dos fluxos interativos de criação/edição, concorrência real entre processos, política de senhas, LGPD e critérios de aceite do PRD.
