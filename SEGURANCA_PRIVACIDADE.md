# Segurança e privacidade

## Diretrizes confirmadas

- O sistema terá autenticação, perfis, permissões hierárquicas e logs.
- Cadastros de clientes envolvem dados pessoais e devem observar a LGPD.
- O primeiro acesso solicita a criação do administrador; não há senha padrão no código.
- Senhas são armazenadas somente como hash PBKDF2-HMAC-SHA256 com salt e comparação em tempo constante.
- Usuários inativados por `data_exclusao` não podem autenticar. As operações de promoção e entrada de nota registram o usuário responsável.

## Decisões pendentes

- Dados coletados, finalidade, base legal, retenção e eliminação/anonymização.
- Papéis de controlador e operador.
- Política de expiração, troca obrigatória e recuperação de senha.
- Conteúdo, retenção e proteção dos logs.
- Criptografia, segregação por empresa e gestão de backups.
