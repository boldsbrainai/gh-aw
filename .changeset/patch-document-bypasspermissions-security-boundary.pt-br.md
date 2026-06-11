---
"gh-aw": patch
---

Documentar o limite de segurança do Claude `bypassPermissions` + `--allowed-tools`: esclarecer no AGENTS.md, na referência dos engines e no guia do MCP que `--allowed-tools` é silenciosamente ignorado no modo `bypassPermissions` (bash irrestrito) e que o filtro `allowed:` do gateway do MCP é o único limite de ferramentas efetivo nesse caso.
