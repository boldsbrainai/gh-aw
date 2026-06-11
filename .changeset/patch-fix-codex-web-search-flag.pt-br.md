---
"gh-aw": patch
---

Corrigimos a geração de comandos do Codex para usar `-c web_search="disabled"` em vez do sinalizador inválido `--no-search`, e deixamos de gerar um sinalizador `--search` inexistente quando a pesquisa na web está ativada.
