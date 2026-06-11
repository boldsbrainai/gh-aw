---
emoji: "📦"
description: Gera um resumo abrangente do uso de artefatos do GitHub Actions em todos os workflows do repositório
on:
  workflow_dispatch:
  schedule: weekly on sunday around 06:00
permissions:
  contents: read
  actions: read
engine: copilot
network:
  allowed:
    - defaults
    - node
sandbox:
  agent: awf  # Firewall habilitado (migrado de network.firewall)
tools:
  cli-proxy: true
  edit:
  bash: true
  github:
    mode: gh-proxy
    toolsets: [actions, repos]
safe-outputs:
  create-discussion:
    expires: 1d
    category: "artifacts"
    max: 1
    close-older-discussions: true
timeout-minutes: 15
strict: true
imports:
  - shared/reporting.md
  - shared/safe-output-app.md
  - shared/otlp.md
---

# Resumo de Artefatos

Gere uma tabela de resumo abrangente do uso de artefatos do GitHub Actions no repositório ${{ github.repository }}.

## Requisitos da Tarefa

1. **Analisar todos os workflows** no repositório para identificar quais geram artefatos
2. **Coletar dados de artefatos** para execuções recentes de workflow (últimos 30 dias recomendado)
3. **Calcular estatísticas**:
   - Número total de artefatos por workflow
   - Tamanho total de todos os artefatos por workflow
   - Tamanho médio do artefato
   - Data da execução mais recente
   - Status (Ativo/Inativo)
4. **Criar uma tabela markdown** com o resumo
5. **Incluir insights** como:
   - Quais workflows geram mais artefatos
   - Quais workflows usam mais armazenamento
   - Tendências no uso de artefatos
   - Recomendações para otimização

## Formato de Saída

Crie uma issue com uma tabela markdown como esta:

```markdown
# Relatório de Uso de Artefatos

| Nome do Workflow | Contagem de Artefatos | Tamanho Total | Tam. Médio | Execução Mais Recente | Status |
|---------------|-----------------|------------|----------|------------|--------|
| workflow-1    | 45             | 2.3 GB     | 52 MB    | 2024-01-15 | Ativo |
| workflow-2    | 12             | 456 MB     | 38 MB    | 2024-01-10 | Ativo |

## Insights e Recomendações
[Sua análise e recomendações aqui]
```

## Notas Importantes

- Foque nos workflows que realmente geram artefatos (pule aqueles sem nenhum)
- Converta tamanhos para formatos legíveis por humanos (MB, GB)
- Considere as políticas de retenção de artefatos em sua análise
- Inclua execuções bem-sucedidas e com falha na análise, ignore execuções canceladas

{{#runtime-import shared/noop-reminder.md}}
