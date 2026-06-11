---
"gh-aw": patch
---

Adicionada limpeza pós-tarefa para a ação `actions/setup` a fim de remover `/tmp/gh-aw/` após a execução do fluxo de trabalho, e atualizado o comportamento do checkout para que os arquivos de execução da ação sejam preservados para a etapa posterior.
