---
"gh-aw": patch
---

Corrigimos as saídas seguras do `update-issue`/`update_pull_request` entre repositórios, respeitando o `target-repo` mesmo na ausência de um `repo` explícito e permitindo que `target-repo: "*"` valide outros repositórios.
