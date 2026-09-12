# PRD — DegeHub ERP

Status: RASCUNHO — pendente de validação dos sete pilares  
Versão: 0.1  
Data: 2026-09-12

## 1. Problema e contexto

O produto pretende apoiar pequenas empresas que hoje usam planilhas ou sistemas estáticos para controlar entrada de produtos, gestão de produtos, clientes, movimentações e relacionamento com clientes (CRM).

O projeto também é uma base de aprendizado em Python, com intenção de ser apresentado futuramente a clientes. A direção é oferecer controle e visibilidade sobre o que ocorre dentro da empresa, sem pressa de implementação.

Pendências: delimitar o problema prioritário, o perfil de empresa inicial e a justificativa de negócio mensurável.

## 2. Personas e público-alvo

- Administrador: acesso total.
- Usuário com acesso parcial: permissões delegáveis por módulos, parametrizações e operações CRUD.
- Estoquista: exemplo de usuário restrito ao estoque.

O produto poderá atender empresas individuais, com banco local ou ambiente em nuvem. A lista final de perfis e suas permissões ainda não foi definida.

## 3. Métricas de sucesso

Pendente de definição. Não avançar para aprovação do PRD sem indicadores e metas mensuráveis.

## 4. Escopo funcional

### Escopo atual

- Clientes, fornecedores, produtos e filiais.
- Estoque por filial, entradas, saídas, ajustes, transferências e Kardex.
- Preços por filial e promoções com possibilidade de validade inicial e final ou vigência até o fim do produto.

### Próxima evolução indicada

- Estoque mais robusto.
- Módulo financeiro.

### Evolução posterior

- Módulo de vendas, opcional.

Regras de vendas, cancelamentos, devoluções, descontos e ajustes detalhados permanecem pendentes.

## 5. Requisitos não funcionais

- A direção futura é uma aplicação web; a implementação atual é CLI.
- Deve existir autenticação, perfis hierárquicos, permissões e logs das operações.
- Dados de clientes estarão sujeitos à LGPD.
- Backup e recuperação ficarão sob responsabilidade do cliente no servidor de hospedagem, conforme contratação.

Pendências: níveis de serviço, disponibilidade, desempenho, retenção de dados pessoais, segurança, recuperação, auditoria e responsabilidades operacionais.

## 6. Fora de escopo da primeira versão

- Vendas.
- Integrações com emissão fiscal, meios de pagamento, e-commerce, contabilidade e bancos.
- Integrações futuras poderão ser cobradas devido a custos de APIs e serviços.

## 7. Critérios de aceite

Pendente de definição pelo responsável do produto. O relatório existente de 36 testes não substitui critérios de aceite nem possui suíte reproduzível versionada.

## Pendências para aprovação

1. Definir problema prioritário e segmento inicial.
2. Definir perfis, permissões e responsabilidades.
3. Definir KPIs e metas.
4. Fechar regras do estoque e do financeiro.
5. Definir requisitos de segurança, LGPD, disponibilidade e retenção.
6. Definir critérios de aceite e plano de validação.
