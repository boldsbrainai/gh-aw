---
"gh-aw": patch
---

Adiciona a opção de configuração `unassign-first` à saída segura do comando `assign-to-user`. Quando ativada, ela retira automaticamente todos os responsáveis atuais de uma issue ou pull request antes de designar novos responsáveis, resolvendo o problema em que a API `addAssignees` do GitHub não substitui os responsáveis existentes.
