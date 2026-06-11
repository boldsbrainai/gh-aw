---
"gh-aw": major
---
Removemos a opção de nível superior `sandbox: false`, que estava obsoleta, e a substituímos por `sandbox.agent: false`, de modo que apenas o firewall do agente possa ser desativado enquanto o gateway do MCP permanece ativado. Adicione `gh aw fix` para migrar os fluxos de trabalho existentes.

**⚠️ Mudança significativa**: O campo de nível superior `sandbox: false` foi removido.

**Guia de migração:**
- Substitua `sandbox: false` por `sandbox.agent: false` no frontmatter do seu fluxo de trabalho
- Exemplo:
  ```yaml
  # Antes
  sandbox: false

  # Depois
  sandbox:
    agent: false
  ```
- Execute `gh aw fix` para migrar automaticamente os fluxos de trabalho existentes
