---
title: MemoryOps
description: Técnicas para usar cache-memory e repo-memory para construir fluxos de trabalho stateful que rastreiam progresso, compartilham dados e computam tendências
sidebar:
  badge: { text: 'Padrões', variant: 'note' }
---

O MemoryOps permite que fluxos de trabalho persistam o estado entre execuções usando `cache-memory` e `repo-memory`. Construa fluxos de trabalho que lembram seu progresso, retomam após interrupções, compartilham dados entre fluxos de trabalho e evitam limitação de API (throttling).

Use MemoryOps para processamento incremental, análise de tendências, tarefas de múltiplas etapas e coordenação de fluxo de trabalho.

## Como Usar Estes Padrões

> [!TIP]
> Declare seu objetivo de alto nível no prompt do fluxo de trabalho e deixe o agente de IA lidar com a implementação. Os exemplos abaixo são prompts que você escreveria — o agente gera o código automaticamente com base na sua configuração de memória.

## Tipos de Memória

### Cache Memory

Armazenamento rápido e efêmero usando cache do GitHub Actions (retenção de 7 dias):

```yaml
tools:
  cache-memory:
    key: meu-estado-de-fluxo-de-trabalho
```

**Use para**: Estado temporário, dados de sessão, cache de curto prazo  
**Localização**: `/tmp/gh-aw/cache-memory/`

### Repository Memory (Memória de Repositório)

Armazenamento persistente e versionado em um branch Git dedicado:

```yaml
tools:
  repo-memory:
    branch-name: memory/meu-fluxo-de-trabalho
    file-glob: ["*.json", "*.jsonl"]
```

**Use para**: Dados históricos, rastreamento de tendências, estado permanente  
**Localização**: `/tmp/gh-aw/repo-memory/default/`

## Padrão 1: Processamento Exaustivo

Rastreie o progresso através de grandes conjuntos de dados com listas de tarefas a fazer/feitas para garantir cobertura completa entre múltiplas execuções.

```markdown
Analise todas as issues abertas no repositório. Rastreie seu progresso em cache-memory
para que você possa retomar se o fluxo de trabalho atingir o tempo limite (timeout). Marque cada issue como feita após
processá-la. Gere um relatório final com estatísticas.
```

O agente mantém um arquivo de estado com itens a processar e itens concluídos, atualizando-o após cada item para que o fluxo de trabalho possa retomar se interrompido:

```json
{
  "a_fazer": [123, 456, 789],
  "feito": [101, 102],
  "erros": [],
  "ultima_execucao": 1705334400
}
```

Exemplos reais: `.github/workflows/repository-quality-improver.md`, `.github/workflows/copilot-agent-analysis.md`

## Padrão 2: Persistência de Estado

Salve pontos de verificação (checkpoints) do fluxo de trabalho para retomar tarefas de longa duração que podem atingir o tempo limite.

```markdown
Migre 10.000 registros do formato antigo para o novo formato. Processe 500
registros por execução e salve um checkpoint. Cada execução deve retomar a partir do último
checkpoint até que todos os registros sejam migrados.
```

O agente armazena um checkpoint com a última posição processada e retoma a partir dela a cada execução:

```json
{
  "ultimo_id_processado": 1250,
  "numero_do_lote": 13,
  "total_migrado": 1250,
  "status": "em_progresso"
}
```

Exemplos reais: `.github/workflows/daily-news.md`, `.github/workflows/cli-consistency-checker.md`

## Padrão 3: Informações Compartilhadas

Compartilhe dados entre fluxos de trabalho usando branches de repo-memory. Um fluxo de trabalho produtor armazena dados; os consumidores os leem usando o mesmo nome de branch.

*Fluxo de trabalho produtor:*
```markdown
A cada 6 horas, colete métricas do repositório (issues, PRs, estrelas) e armazene-as
em repo-memory para que outros fluxos de trabalho possam analisar os dados mais tarde.
```

*Fluxo de trabalho consumidor:*
```markdown
Carregue as métricas históricas de repo-memory e compute tendências semanais.
Gere um relatório de tendência com visualizações.
```

Ambos os fluxos de trabalho referenciam o mesmo branch:

```yaml
tools:
  repo-memory:
    branch-name: memory/dados-compartilhados
```

Exemplos reais: `.github/workflows/metrics-collector.md` (produtor), fluxos de trabalho de análise de tendência (consumidores)

## Padrão 4: Cache de Dados

Faça cache de respostas de API para evitar limites de taxa (rate limits) e reduzir o tempo do fluxo de trabalho. O agente verifica dados em cache recentes antes de fazer chamadas de API, usando TTLs sugeridos: metadados de repositório (24h), listas de contribuidores (12h), issues/PRs (1h), execuções de fluxo de trabalho (30m).

```markdown
Busque metadados do repositório e listas de contribuidores. Faça cache dos dados por 24 horas
para evitar chamadas de API repetidas. Se o cache estiver recente, use-o. Caso contrário, busque
novos dados e atualize o cache.
```

Exemplos reais: `.github/workflows/daily-news.md`

## Padrão 5: Computação de Tendência

Armazene dados de série temporal e compute tendências, médias móveis e estatísticas. O agente anexa novos pontos de dados a um arquivo de histórico JSON Lines e compute tendências usando Python.

```markdown
Colete tempos diários de build e tempos de teste. Armazene-os em repo-memory como
dados de série temporal. Compute médias móveis de 7 e 30 dias. Gere gráficos de tendência
mostrando se o desempenho está melhorando ou diminuindo ao longo do tempo.
```

Exemplos reais: `.github/workflows/daily-code-metrics.md`, `.github/workflows/shared/charts-with-trending.md`

## Padrão 6: Múltiplos Armazenamentos de Memória

Use múltiplas instâncias de memória para ciclos de vida diferentes — cache-memory para dados de sessão temporários, branches de repo-memory separados para métricas, configuração e arquivos.

```markdown
Use cache-memory para respostas de API temporárias durante esta execução. Armazene métricas diárias
em um branch de repo-memory para análise de tendência. Mantenha schemas de dados em
outro branch. Arquive snapshots completos em um terceiro branch com compressão.
```

```yaml
tools:
  cache-memory:
    key: dados-de-sessao  # Rápido, temporário

  repo-memory:
    - id: metricas
      branch-name: memory/metricas  # Dados de série temporal

    - id: config
      branch-name: memory/config  # Schema e metadados

    - id: arquivo
      branch-name: memory/arquivo  # Backups comprimidos
```

## Melhores Práticas

### Use JSON Lines para Dados de Série Temporal

Formato somente anexo ideal para logs e métricas:

```bash
# Anexar sem ler o arquivo inteiro
echo '{"data": "2024-01-15", "valor": 42}' >> dados.jsonl
```

### Inclua Metadados

Documente sua estrutura de dados:

```json
{
  "dataset": "metricas-de-desempenho",
  "schema": {
    "data": "AAAA-MM-DD",
    "valor": "inteiro"
  },
  "retencao": "90 dias"
}
```

### Implemente Rotação de Dados

Evite crescimento ilimitado:

```bash
# Mantenha apenas as últimas 90 entradas
tail -n 90 historico.jsonl > historico-cortado.jsonl
mv historico-cortado.jsonl historico.jsonl
```

### Valide o Estado

Verifique a integridade antes de processar:

```bash
if [ -f estado.json ] && jq empty estado.json 2>/dev/null; then
  echo "Estado válido"
else
  echo "Estado corrompido, reinicializando..."
  echo '{}' > estado.json
fi
```

## Considerações de Segurança

Armazenamentos de memória são visíveis para qualquer pessoa com acesso ao repositório. Nunca armazene credenciais, tokens de API, PII ou segredos — apenas estatísticas agregadas e dados anonimizados.

```bash
# ✅ BOM - Estatísticas agregadas
echo '{"issues_abertas": 42}' > metricas.json

# ❌ RUIM - Dados individuais de usuário
echo '{"usuario": "alice", "email": "alice@exemplo.com"}' > usuarios.json
```

## Resolução de Problemas

**Cache não persistindo**: Verifique se a chave de cache é consistente entre execuções

**Memória de repositório não atualizando**: Verifique se os padrões de `file-glob` correspondem aos seus arquivos e se os arquivos estão dentro do limite de `max-file-size`

**Erros de memória insuficiente (Out of memory)**: Processe dados em lotes (chunks) em vez de carregar tudo, implemente rotação de dados

**Conflitos de merge**: Use o formato JSON Lines (somente anexo), branches separados por fluxo de trabalho, ou adicione ID da execução aos nomes de arquivo

## Documentação Relacionada

- [Servidores MCP](/gh-aw/guides/mcps/) - Configuração do servidor MCP de memória
- [DeterministicOps](/gh-aw/patterns/deterministic-ops/) - Pré-processamento e extração de dados
- [Saídas Seguras (Safe Outputs)](/gh-aw/reference/custom-safe-outputs/) - Armazenando saídas de fluxo de trabalho
- [Referência de Frontmatter](/gh-aw/reference/frontmatter/) - Opções de configuração
