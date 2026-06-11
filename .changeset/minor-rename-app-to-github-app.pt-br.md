---
"gh-aw": major
---

Renomeamos o campo de workflow obsoleto `app:` para `github-app:` e adicionamos o codemod, além de atualizações no schema/Go, para manter as ferramentas sincronizadas.

**⚠️ Alteração compatibilidade**: O campo de workflow `app:` foi renomeado para `github-app:`. Os workflows que utilizam `app:` não passarão na validação.

**Guia de migração:**
- Substitua `app:` por `github-app:` no frontmatter do seu fluxo de trabalho
- Exemplo:
  ```yaml
  # Antes
  app:
    id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}

  # Depois
  github-app:
    id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
  ```
- Está disponível um codemod para automatizar essa migração: execute `gh aw fix` para atualizar os fluxos de trabalho existentes
