---
"gh-aw": menor
---

Adicionar a opção `preserve-branch-name: true` às saídas seguras do `create-pull-request`. Quando ativada, nenhum sufixo aleatório é anexado ao nome do branch especificado pelo agente. Caracteres inválidos ainda são substituídos por motivos de segurança, e as maiúsculas e minúsculas são sempre preservadas, independentemente dessa configuração. Útil quando o repositório de destino impõe convenções de nomenclatura de ramificações, como chaves do Jira em maiúsculas (por exemplo, `bugfix/BR-329-red`).
