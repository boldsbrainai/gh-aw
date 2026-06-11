---
"gh-aw": patch
---

Corrigimos a geração de patches incrementais para `push_to_pull_request_branch`, recorrendo a uma referência de rastreamento existente em `origin/<branch>` quando o `git fetch` falha, e adicionamos cobertura de integração para o caminho alternativo.
