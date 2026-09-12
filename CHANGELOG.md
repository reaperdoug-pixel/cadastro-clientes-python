# Changelog

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
