---
"gh-aw": patch
---

Corrigir a aplicação das permissões de ferramentas do motor Claude usando `--permission-mode acceptEdits` em vez de `bypassPermissions`, para que as restrições de `--allowed-tools` do fluxo de trabalho sejam respeitadas nas execuções de CI.
