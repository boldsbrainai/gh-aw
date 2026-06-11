---
"gh-aw": alteração menor
---

Ativar `reaction: eyes` e `status-comment: true` por padrão quando forem usados os gatilhos `slash_command` ou `label_command`. Ambos podem ser desativados explicitamente com `reaction: none` e `status-comment: false`.

Anteriormente, `reaction: eyes` era ativado automaticamente apenas para fluxos de trabalho `slash_command`, e `status-comment` sempre exigia ativação explícita. Agora, ambas as configurações padrão se aplicam também aos fluxos de trabalho `label_command`, e `status-comment: true` é o padrão para ambos os tipos de gatilho de comando.
