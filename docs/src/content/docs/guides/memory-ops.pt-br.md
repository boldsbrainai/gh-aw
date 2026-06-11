---
title: MemoryOps
description: Técnicas para usar cache-memory e repo-memory para construir fluxos de trabalho com estado que rastreiam o progresso, compartilham dados e calculam tendências
sidebar:
  badge: { text: 'Padrões', variant: 'note' }
---

O MemoryOps permite que fluxos de trabalho persistam o estado entre execuções usando `cache-memory` e `repo-memory`. Construa fluxos de trabalho que se lembram do seu progresso, retomam após interrupções, compartilham dados entre fluxos de trabalho e evitam o estrangulamento (throttling) de API.

Use o MemoryOps para processamento incremental, análise de tendências, tarefas em várias etapas e coordenação de fluxos de trabalho.

## Como Usar Estes Padrões

> [!TIP]
> Declare seu objetivo de alto nível no prompt do fluxo de trabalho e deixe o agente de IA lidar com a implementação. Os exemplos abaixo são prompts que você escreveria — o agente gera o código automaticamente com base na sua configuração de memória.

## Tipos de Memória

### Memória de Cache (Cache Memory)

Armazenamento rápido e efêmero usando o cache do GitHub Actions (retenção de 7 dias):

```yaml
tools:
  cache-memory:
    key: my-workflow-state
```

**Use para**: Estado temporário, dados de sessão, cache de curto prazo  
**Localização**: `/tmp/gh-aw/cache-memory/`

### Memória de Repositório (Repository Memory)

Armazenamento persistente e versionado em uma branch Git dedicada:

```yaml
tools:
  repo-memory:
    branch-name: memory/my-workflow
    file-glob: ["*.json", "*.jsonl"]
```

**Use para**: Dados históricos, rastreamento de tendências, estado permanente  
**Localização**: `/tmp/gh-aw/repo-memory/default/`

## Padrão 1: Processamento Exaustivo

Rastreie o progresso através de grandes conjuntos de dados com listas de "a fazer/feito" para garantir cobertura completa entre várias execuções.

```markdown
Analise todas as issues abertas no repositório. Rastreie seu progresso na cache-memory
para que você possa retomar se o fluxo de trabalho atingir o timeout. Marque cada issue como feita após
processá-la. Gere um relatório final com estatísticas.
```

O agente mantém um arquivo de estado com itens a processar e itens concluídos, atualizando-o após cada item para que o fluxo de trabalho possa retomar se for interrompido:

```json
{
  "todo": [123, 456, 789],
  "done": [101, 102],
  "errors": [],
  "last_run": 1705334400
}
```

Exemplos reais: `.github/workflows/repository-quality-improver.md`, `.github/workflows/copilot-agent-analysis.md`

## Padrão 2: Persistência de Estado

Salve pontos de verificação (checkpoints) do fluxo de trabalho para retomar tarefas de longa duração que podem atingir timeout.

```markdown
Migre 10.000 registros do formato antigo para o novo formato. Processe 500
registros por execução e salve um checkpoint. Cada execução deve retomar do último
checkpoint até que todos os registros sejam migrados.
```

O agente armazena um checkpoint com a última posição processada e retoma a partir dele em cada execução:

```json
{
  "last_processed_id": 1250,
  "batch_number": 13,
  "total_migrated": 1250,
  "status": "in_progress"
}
```

Exemplos reais: `.github/workflows/daily-news.md`, `.github/workflows/cli-consistency-checker.md`

## Padrão 3: Informações Compartilhadas

Compartilhe dados entre fluxos de trabalho usando branches de repo-memory. Um fluxo de trabalho produtor armazena dados; os consumidores os leem usando o mesmo nome de branch.

*Fluxo de trabalho produtor:*
```markdown
A cada 6 horas, colete métricas do repositório (issues, PRs, estrelas) e armazene-as
na repo-memory para que outros fluxos de trabalho possam analisar os dados mais tarde.
```

*Fluxo de trabalho consumidor:*
```markdown
Carregue as métricas históricas da repo-memory e calcule tendências semanais.
Gere um relatório de tendências com visualizações.
```

Ambos os fluxos de trabalho referenciam a mesma branch:

```yaml
tools:
  repo-memory:
    branch-name: memory/shared-data
```

Exemplos reais: `.github/workflows/metrics-collector.md` (produtor), fluxos de trabalho de análise de tendências (consumidores)

## Padrão 4: Cache de Dados

Faça cache de respostas de API para evitar limites de taxa (rate limits) e reduzir o tempo do fluxo de trabalho. O agente verifica se há dados em cache atualizados antes de fazer chamadas de API, usando TTLs sugeridos: metadados do repositório (24h), listas de colaboradores (12h), issues/PRs (1h), execuções de fluxo de trabalho (30m).

```markdown
Busque metadados do repositório e listas de colaboradores. Faça cache dos dados por 24 horas
para evitar chamadas de API repetidas. Se o cache estiver atualizado, use-o. Caso contrário, busque
novos dados e atualize o cache.
```

Exemplos reais: `.github/workflows/daily-news.md`

## Padrão 5: Computação de Tendências

Armazene dados de séries temporais e calcule tendências, médias móveis e estatísticas. O agente anexa novos pontos de dados a um arquivo de histórico JSON Lines e calcula tendências usando Python.

```markdown
Colete tempos de build diários e tempos de teste. Armazene-os na repo-memory como
dados de série temporal. Calcule médias móveis de 7 e 30 dias. Gere gráficos de tendência
mostrando se o desempenho está melhorando ou diminuindo ao longo do tempo.
```

Exemplos reais: `.github/workflows/daily-code-metrics.md`, `.github/workflows/shared/charts-with-trending.md`

## Padrão 6: Múltiplos Armazenamentos de Memória

Use múltiplas instâncias de memória para diferentes ciclos de vida — cache-memory para dados temporários de sessão, branches de repo-memory separadas para métricas, configuração e arquivos.

```markdown
Use cache-memory para respostas de API temporárias durante esta execução. Armazene métricas diárias
em uma branch de repo-memory para análise de tendências. Mantenha esquemas de dados em
outra branch. Arquive snapshots completos em uma terceira branch com compactação.
```

```yaml
tools:
  cache-memory:
    key: session-data  # Rápido, temporário

  repo-memory:
    - id: metrics
      branch-name: memory/metrics  # Dados de série temporal

    - id: config
      branch-name: memory/config  # Esquema e metadados

    - id: archive
      branch-name: memory/archive  # Backups compactados
```

## Melhores Práticas

### Use JSON Lines para Dados de Série Temporal

Formato somente anexo ideal para logs e métricas:

```bash
# Anexar sem ler o arquivo inteiro
echo '{"date": "2024-01-15", "value": 42}' >> data.jsonl
```

### Inclua Metadados

Documente sua estrutura de dados:

```json
{
  "dataset": "performance-metrics",
  "schema": {
    "date": "YYYY-MM-DD",
    "value": "integer"
  },
  "retention": "90 days"
}
```

### Implemente Rotação de Dados

Evite crescimento ilimitado:

```bash
# Manter apenas as últimas 90 entradas
tail -n 90 history.jsonl > history-trimmed.jsonl
mv history-trimmed.jsonl history.jsonl
```

### Valide o Estado

Verifique a integridade antes de processar:

```bash
if [ -f state.json ] && jq empty state.json 2>/dev/null; then
  echo "Estado válido"
else
  echo "Estado corrompido, reinicializando..."
  echo '{}' > state.json
fi
```

## Considerações de Segurança

Os armazenamentos de memória são visíveis para qualquer pessoa com acesso ao repositório. Nunca armazene credenciais, tokens de API, PII ou segredos — apenas estatísticas agregadas e dados anonimizados.

```bash
# ✅ BOM - Estatísticas agregadas
echo '{"open_issues": 42}' > metrics.json

# ❌ RUIM - Dados individuais de usuário
echo '{"user": "alice", "email": "alice@example.com"}' > users.json
```

## Solução de Problemas

**Cache não persiste**: Verifique se a chave de cache é consistente entre as execuções

**Repo memory não atualiza**: Verifique se os padrões `file-glob` correspondem aos seus arquivos e se os arquivos estão dentro do limite de `max-file-size`

**Erros de falta de memória (Out of memory)**: Processe dados em chunks em vez de carregar tudo, implemente rotação de dados

**Conflitos de merge**: Use o formato JSON Lines (somente anexo), branches separadas por fluxo de trabalho ou adicione o ID de execução aos nomes dos arquivos

## Documentação relacionada

- [Servidores MCP](/gh-aw/guides/mcps/) - Configuração do servidor MCP de memória
- [DeterministicOps](/gh-aw/patterns/deterministic-ops/) - Pré-processamento e extração de dados
- [Saídas Seguras (Safe Outputs)](/gh-aw/reference/custom-safe-outputs/) - Armazenando saídas de fluxo de trabalho
- [Referência de Frontmatter](/gh-aw/reference/frontmatter/) - Opções de configuração
