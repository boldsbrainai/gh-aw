---
"gh-aw": patch
---

Corrigida a análise do manipulador de saída segura para permitir `target-repo: "*"` nos manipuladores add-comment, create-issue, create-discussion, close-entity, add-reviewer e create-pull-request, de modo que os manipuladores direcionados por curinga sejam preservados em `GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG`.
