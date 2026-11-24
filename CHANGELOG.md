# Changelog

## Documentação e ambiente Linux — 2026-11-24

- README passou a documentar execução e testes no Linux/Omarchy, com uma seção curta para Windows.
- Árvore do projeto, módulos, perfis e tipos de Kardex (incluindo `ENTRADA_NOTA`) alinhados ao código.
- Criado `scripts/verificar.sh`, equivalente ao verificador em PowerShell.
- A captura de tela versionada como `Print.png` foi renomeada para `print.png`, alinhada à referência do README.
- Suíte reexecutada neste ambiente: 19 testes aprovados, 0 falhas e 0 erros.

## Estabilização de ambiente e testes — 2026-09-12

- Adicionados `.editorconfig` e `.gitattributes` para padronizar UTF-8 e finais de linha.
- Documentado o bootstrap com `python -m venv` e criado `scripts/verificar.ps1` para executar a validação local.
- Suíte `unittest` ampliada de 9 para 19 casos, cobrindo autenticação, sessão, menus de consulta, rollback de nota, unicidade, migração legada e retry SQLite.
- Atualizados o plano e o relatório de testes com a evidência reproduzível mais recente.

## Gestão de Estoque e Administração — 2026-09-12

- Renomeado o acesso principal para Gestão de Estoque e reorganizado o menu em Produtos, Distribuição, Transferência, Ajuste, Preços e Promoções, Entrada de Notas e Kardex.
- Distribuição é exibida apenas quando há CD ativo e restringe a origem a CDs.
- Criadas as tabelas `usuarios`, `promocoes`, `notas_entrada` e `itens_notas_entrada`.
- Adicionados login, criação assistida do primeiro administrador, CRUD de usuários e perfis ADMIN, ESTOQUISTA e CONSULTA.
- Senhas passaram a usar PBKDF2-HMAC-SHA256 com salt.
- Promoções agora têm histórico, vigência, unidade e responsável; valores legados são migrados da tabela de preços.
- Entrada de notas multi-item atualiza saldo e Kardex de forma atômica.
- Validação automatizada: 9 testes aprovados.

## Estado encontrado — 2026-09-12

- Sistema CLI em Python com SQLite.
- Cadastros de clientes, fornecedores, produtos e filiais.
- Estoque segregado por filial e Kardex.
- Preços por filial e promoções.
- Soft delete e transações atômicas.
- Documentação de PRD, regras, dados, testes, segurança e operação iniciada.

## Próximas entradas

Registrar versão, data, alteração, motivação e evidência de teste de cada mudança aprovada.
