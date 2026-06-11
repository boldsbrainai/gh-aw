---
"gh-aw": patch
---

Adiciona suporte ao gatilho `label_command` para que os fluxos de trabalho possam ser executados quando uma etiqueta configurada for adicionada a uma issue, solicitação de pull ou discussão. A tarefa de ativação agora remove a etiqueta que acionou o gatilho no momento da inicialização e expõe `needs.activation.outputs.label_command` para uso posterior.
