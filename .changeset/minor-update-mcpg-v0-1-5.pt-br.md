---
"gh-aw": major
---

Atualize a dependência do MCP Gateway para a versão v0.1.5 e sincronize a validação com as novas
regras de compatibilidade (servidores stdio TOML exclusivos para Docker, modos de montagem explícitos e nenhuma
montagem em servidores MCP HTTP).

**⚠️ Mudança de compatibilidade**: O MCP Gateway v0.1.5 introduz regras de validação mais rígidas que rejeitam configurações que antes eram válidas.

**Guia de migração:**
- **Servidores MCP stdio** agora devem usar configuração TOML exclusiva para Docker; servidores stdio que não sejam Docker não são mais suportados
- **Configurações de montagem** agora devem especificar um modo de montagem explícito; modos de montagem implícitos não são mais aceitos
- **Servidores MCP HTTP** não devem incluir nenhuma configuração de montagem; remova todas as seções `mounts:` das definições de servidores MCP HTTP
- Exemplo de migração para servidor stdio:
  ```yaml
  # Antes (stdio não Docker)
  mcp:
    servers:
      my-server:
        type: stdio
        command: my-server-binary

  # Depois (stdio exclusivo para Docker)
  mcp:
    servers:
      my-server:
        type: stdio
        image: my-server-image:latest
  ```
- Valide suas configurações de servidor MCP de acordo com as novas regras antes de atualizar
