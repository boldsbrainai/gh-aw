---
"gh-aw": patch
---

Corrigida a falha do `create_pull_request` com o erro `spawnSync git ENOBUFS` em diferenças grandes (por exemplo, mais de 47 arquivos alterados).

O helper `execGitSync` em `git_helpers.cjs` usava o `spawnSync` do Node.js sem um `maxBuffer` explícito, com o padrão definido em ~1 MB. Quando `git format-patch --stdout` produzia uma saída que excedia esse limite, todas as estratégias de geração de patch falhavam silenciosamente com um erro enganoso: "No changes to commit".

A correção:
- Defina `maxBuffer: 100 * 1024 * 1024` (100 MB) como padrão em `execGitSync`, correspondendo à margem de `max_patch_size` e em consonância com outros manipuladores na base de código (por exemplo, os manipuladores MCP usam 10 MB).
- Detectar erros `ENOBUFS` e exibir uma mensagem de erro acionável que revele a causa real, em vez do fallback genérico “nenhum commit encontrado”.
- Os chamadores ainda podem substituir `maxBuffer` por meio do conjunto de opções.
