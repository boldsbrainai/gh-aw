---
"gh-aw": patch
---

Atualizar a imagem do gateway MCP para `v0.3.9` para que os fluxos de trabalho compilados utilizem o contêiner `gh-aw-mcpg` atualizado. Esta versão move o diretório de cache de compilação do wazero para `/tmp/gh-aw/wazero-cache/` (fora de `/tmp/gh-aw/mcp-logs/`), corrigindo o erro EACCES quando a etapa de upload de artefatos tenta compactar o diretório de logs.
