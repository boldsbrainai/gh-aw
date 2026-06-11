---
"gh-aw": menor
---

Alterada a configuração `headers` do OpenTelemetry no gateway MCP para aceitar apenas um valor de string e repassá-lo sem alterações.

## Codemod

Se você atualmente configura os cabeçalhos OTLP como um objeto no frontmatter do fluxo de trabalho:

```yaml
mcp-gateway:
  opentelemetry:
    headers:
      Authorization: "Bearer ${OTLP_TOKEN}"
      X-Scope-OrgID: "my-tenant"
```

Atualize-a para uma string:

```yaml
mcp-gateway:
  opentelemetry:
    headers: "Authorization=Bearer ${OTLP_TOKEN},X-Scope-OrgID=my-tenant"
```

Isso se aplica a fluxos de trabalho que usam a configuração `mcp-gateway.opentelemetry.headers`.
