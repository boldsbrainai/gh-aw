---
"gh-aw": patch
---

Certifique-se de que o `check_mcp_servers.sh` utilize `tools/list` em vez de `ping`, para que o teste de disponibilidade aguarde até que os contêineres de back-end fiquem disponíveis.
