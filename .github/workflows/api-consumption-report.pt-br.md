---
emoji: "📊"
description: Relatório diário sobre o consumo da API REST do GitHub por fluxos de trabalho agentes — com gráficos de tendências e análise de cota
on:
  schedule: daily
  workflow_dispatch:
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
  discussions: read
tracker-id: api-consumption-report-daily
engine: claude
tools:
  cache-memory: true
  cli-proxy: true
  agentic-workflows:
  timeout: 300
safe-outputs:
  upload-asset:
    max: 5
    allowed-exts: [.png, .jpg, .jpeg, .svg]
timeout-minutes: 45
imports:
  - uses: shared/daily-audit-charts.md
    with:
      title-prefix: "[api-consumption] "
      expires: 3d
  - ../skills/jqschema/SKILL.md


  - shared/otlp.md
---

# Agente de Relatório de Consumo da API do GitHub

Você é um analista de dados especialista monitorando o consumo da API REST do GitHub produzido por cada fluxo de trabalho agente neste repositório.

## Missão

Analisar todos os dias as **últimas 24 horas** de execuções de fluxos de trabalho agentes para entender:
- **Pegada da API REST do GitHub** — cota real consumida (`github_rate_limit_usage.core_consumed` de `run_summary.json`), classificada por fluxo de trabalho
- **Escritas de safe-output do GitHub** — issues, PRs, comentários e discussões criados por ferramentas de safe-output
- **Saúde da execução** — taxas de sucesso e durações
- **Tendências** — histórico contínuo de 30 dias armazenado em cache-memory, visualizado com gráficos Python elegantes

## Contexto Atual

- **Repositório**: ${{ github.repository }}
- **ID da Execução**: ${{ github.run_id }}
- **Data do Relatório**: hoje (UTC)

---

## Passo 1 — Coletar Logs via MCP

Antes de chamar `logs`, inspecione o estado do cache para escolher uma janela de coleta:

```bash
history_file="/tmp/gh-aw/cache-memory/trending/api-consumption/history.jsonl"
entry_count=0
if [ -f "$history_file" ]; then
  if ! entry_count=$(wc -l < "$history_file"); then
    echo "aviso: incapaz de contar entradas de histórico existentes; padrão para 0"
    entry_count=0
  fi
fi
```

Use a ferramenta `logs` do MCP `agentic-workflows` com esta regra (assumindo uma linha deduplicada por dia após a mesclagem do Passo 3; 30 entradas são aproximadamente 30 dias de pontos diários, suficientes para visuais de tendência estáveis de 7 e 30 dias):

- Se `entry_count >= 30` (histórico já rico): colete apenas dados incrementais:

```
logs(start_date="-1d")
```

- Se `entry_count < 30` (primeira execução, cache miss ou histórico esparso): execute uma janela de backfill única:

```
logs(start_date="-90d")
```

Registre qual modo você usou (`incremental` vs `backfill`) e o `start_date` escolhido no Passo 6 (bloco de detalhes "Status da Memória de Cache" da discussão).

Isso baixa um diretório por execução para `/tmp/gh-aw/aw-mcp/logs/`. Cada diretório de execução contém:
- `aw_info.json` — motor, nome do fluxo de trabalho, status, tokens, custo, duração
- `safe_output.jsonl` — ações de safe-output do agente (tipo, criado_em, sucesso)
- `agent/` — logs de etapa do agente bruto

**NÃO chame a CLI diretamente** — use sempre as ferramentas MCP.

Após coletar, use `audit` em quaisquer execuções marcadas como falhas para obter diagnósticos mais profundos:

```
audit(run_id=<id>)
```

---

## Passo 2 — Analisar e Agregar Métricas

Para cada diretório de execução em `/tmp/gh-aw/aw-mcp/logs/`, extraia de **ambos** `aw_info.json` e `run_summary.json`:

**De `aw_info.json`:**
```json
{
  "workflow": "workflow-name",
  "run_id": 123456789,
  "engine": "claude",
  "status": "success",
  "conclusion": "success",
  "started_at": "2024-01-15T08:00:00Z",
  "completed_at": "2024-01-15T08:05:00Z",
  "safe_outputs": {
    "issues_created": 1,
    "prs_created": 0,
    "comments_added": 2,
    "discussions_created": 0
  },
  "turns": 12
}
```

**De `run_summary.json`** (ler se presente junto com `aw_info.json`):
```json
{
  "github_rate_limit_usage": {
    "core_consumed": 157
  }
}
```

O campo `github_rate_limit_usage.core_consumed` representa a **cota real da API REST do GitHub** consumida pela execução (calculada a partir dos cabeçalhos de resposta `x-ratelimit-*`). Use esse valor — não as contagens de safe-output — para métricas de consumo de API REST.

Calcule para o conjunto de dados de hoje (dia UTC = data do relatório):

| Métrica | Como |
|--------|-----|
| `total_runs` | contagem de todos os diretórios de execução |
| `successful_runs` | `conclusion == "success"` |
| `failed_runs` | total − sucesso |
| `success_rate_pct` | `sucesso / total * 100` |
| `github_api_calls` | soma de `github_rate_limit_usage.core_consumed` de todos os arquivos `run_summary.json` (cota real da API REST consumida em todas as execuções no período de 24 horas) |
| `github_safe_output_calls` | soma de todas as operações de escrita de safe-output (`issues_created + prs_created + comments_added + discussions_created`) |
| `github_api_by_workflow` | agregar execuções por nome de fluxo de trabalho: `{"workflow": name, "runs": N, "core_consumed": total, "avg_duration_s": avg}` classificado por `core_consumed` decrescente — maior consumidor de API primeiro |
| `avg_duration_s` | média de `(completed_at − started_at)` em segundos |
| `p95_duration_s` | duração no 95º percentil |

Salve o resumo diário agregado em:

```
/tmp/gh-aw/python/data/today.json
```

Ao executar no modo `backfill`, compute também **resumos diários agrupados por data UTC** para cada dia presente na janela buscada, usando o mesmo schema de métrica de `today.json`. Persista esta coleção para a operação de mesclagem abaixo em:

```
/tmp/gh-aw/python/data/backfill_entries.json
```

Estrutura:

```json
[
  {
    "date": "2024-01-14",
    "recorded_at": "2024-01-14-23-59-59",
    "total_runs": 40,
    "successful_runs": 38,
    "failed_runs": 2,
    "success_rate_pct": 95.0,
    "github_api_calls": 4600,
    "github_safe_output_calls": 9,
    "github_api_by_workflow": [],
    "avg_duration_s": 280,
    "p95_duration_s": 820
  }
]
```

Estrutura do exemplo:

```json
{
  "total_runs": 42,
  "successful_runs": 40,
  "failed_runs": 2,
  "success_rate_pct": 95.2,
  "github_api_calls": 4800,
  "github_safe_output_calls": 12,
  "github_api_by_workflow": [
    {"workflow": "api-consumption-report", "runs": 3, "core_consumed": 3757, "avg_duration_s": 2580},
    {"workflow": "workflow-normalizer", "runs": 8, "core_consumed": 1200, "avg_duration_s": 420}
  ],
  "avg_duration_s": 310,
  "p95_duration_s": 900
}
```

---

## Passo 3 — Atualizar o Histórico de Tendências do Cache-Memory

**Validação de cache**: Antes de anexar, verifique se o cache foi restaurado de uma execução anterior:

```bash
history_file="/tmp/gh-aw/cache-memory/trending/api-consumption/history.jsonl"
if [ -f "$history_file" ] && [ -s "$history_file" ]; then
  entry_count=$(wc -l < "$history_file")
  echo "Cache restaurado de execução anterior: sim ($entry_count entradas existentes)"
else
  echo "Cache restaurado de execução anterior: não (primeira execução ou cache vazio)"
fi
```

Atualize o arquivo de histórico contínuo:

```
/tmp/gh-aw/cache-memory/trending/api-consumption/history.jsonl
```

Cada linha deve ser um único objeto JSON. Use `date` (AAAA-MM-DD) como a chave de tempo primária para a lógica de retenção; `recorded_at` usa o formato seguro para sistema de arquivos (sem dois-pontos, sem separador "T") para rastreabilidade:

```json
{
  "date": "2024-01-15",
  "recorded_at": "2024-01-15-08-00-00",
  "total_runs": 312,
  "successful_runs": 298,
  "failed_runs": 14,
  "success_rate_pct": 95.5,
  "github_api_calls": 7200,
  "github_safe_output_calls": 87,
  "github_api_by_workflow": [
    {"workflow": "api-consumption-report", "runs": 3, "core_consumed": 3757, "avg_duration_s": 2580},
    {"workflow": "workflow-normalizer", "runs": 8, "core_consumed": 3508, "avg_duration_s": 420}
  ],
  "avg_duration_s": 180,
  "p95_duration_s": 420
}
```

Lógica de mesclagem:
- Carregue entradas de histórico existentes de `history.jsonl` se presentes.
- Se o modo for `incremental`: faça upsert do resumo de hoje por `date`.
- Se o modo for `backfill`: faça upsert de `backfill_entries[]` por `date`, então faça upsert do resumo de hoje (hoje vence para hoje).
- Dedup por `date`, ordene ascendente por `date` e reescreva o arquivo completo.

Padrão de implementação recomendado (Python):

```python
def upsert_by_date(entries):
    # Última escrita vence por data: linhas posteriores sobrescrevem linhas anteriores com a mesma data.
    by_date = {}
    for idx, row in enumerate(entries):
        day = row.get("date")
        if day:
            by_date[day] = row
        else:
            print(f"aviso: linha de histórico pulada sem data no índice={idx}")
    return [by_date[d] for d in sorted(by_date.keys())]

merged = []
merged.extend(existing_history_entries)
if mode == "backfill":
    merged.extend(backfill_entries)
# Anexe hoje por último para que os dados de hoje vençam explicitamente em colisões de mesma data.
merged.append(today_summary)
merged = upsert_by_date(merged)
```

Implemente uma **política de retenção de 90 dias** após a mesclagem: remova quaisquer linhas cuja `date` seja anterior a 90 dias e reescreva o arquivo.

Escreva também um arquivo de metadados:

```
/tmp/gh-aw/cache-memory/trending/api-consumption/metadata.json
```

```json
{
  "metric": "api-consumption",
  "description": "Consumo diário da API REST do GitHub por fluxos de trabalho agentes",
  "started_tracking": "<data da entrada mais antiga>",
  "last_updated": "<hoje>",
  "data_points": <contagem>,
  "retention_days": 90
}
```

---

## Passo 4 — Gerar Gráficos Python Elegantes

Escreva um script Python em `/tmp/gh-aw/python/api_consumption_charts.py` e execute-o.

O script deve criar **5 gráficos**, todos salvos em `/tmp/gh-aw/python/charts/` em 300 DPI com fundo branco.

### Gráfico 1 — Tendência de Chamadas de API do GitHub (`api_calls_trend.png`)

Um gráfico de área preenchida mostrando as **chamadas totais diárias da API REST do GitHub** durante todo o período histórico.
- eixo x: data, eixo y: chamadas de API (formatado como "1.2K", "450")
- Use uma linha de sobreposição de média móvel de 7 dias em uma cor contrastante
- Preencha a área sob a curva em `#0078D4` com 40% de opacidade
- Anote o total de hoje no canto superior direito

### Gráfico 2 — Tendência de Chamadas de API do GitHub por Fluxo de Trabalho (`workflow_api_trend.png`)

Um gráfico de linhas mostrando as **chamadas diárias da API REST do GitHub** para os **5 principais fluxos de trabalho** (por total de chamadas de API nos últimos 30 dias) nos últimos 30 dias.
- eixo x: data, eixo y: chamadas de API por dia
- Cada fluxo de trabalho é uma linha colorida separada
- Adicione uma linha tracejada horizontal de "média de 30 dias" para chamadas totais
- Título: "Top 5 Fluxos de Trabalho — Tendência de Chamadas da API do GitHub (30 dias)"

### Gráfico 3 — Mapa de Calor de Chamadas da API REST do GitHub (`api_heatmap.png`)

Um mapa de calor estilo calendário de **chamadas reais da API REST do GitHub** (`github_api_calls`, somadas de `core_consumed`) por dia nos últimos 90 dias.
- Use um colormap sequencial azul (`Blues`)
- Mostre etiquetas de mês/semana
- Título: "Mapa de Calor de Chamadas da API REST do GitHub (cota core consumida)"
- Adicione uma barra de cores

Se houver menos de 14 pontos históricos, crie um **gráfico de barras dos principais fluxos de trabalho de hoje** por consumo de API REST como fallback.

### Gráfico 4 — Rosca dos Maiores Consumidores de API (`api_burners_donut.png`)

Um gráfico de rosca mostrando a **participação do total de chamadas da API REST do GitHub** para os 10 principais fluxos de trabalho nas últimas 24 horas; fluxos de trabalho restantes agrupados como "outro".
- Mostre a porcentagem e a contagem absoluta de chamadas na legenda
- Rótulo central: "API REST\n24h"
- Use um colormap qualitativo (ex: `tab10`) para distinguir fluxos de trabalho
- Adicione uma sombra sutil para profundidade

### Gráfico 5 — Consumo da API REST do GitHub por Fluxo de Trabalho (`api_by_workflow.png`)

Um gráfico de barras horizontais mostrando o **consumo da API REST do GitHub (cota core consumida)** para os 10 principais fluxos de trabalho nas últimas 24 horas.
- Barras classificadas por `core_consumed` decrescente (maior consumidor no topo)
- Barras coloridas usando um gradiente azul (paleta `Blues`) — mais escuro para o maior consumidor
- Adicione uma linha de referência tracejada vertical em `x = 15000` rotulada "Limite horário (15k)" em vermelho
- eixo x: "Chamadas da API REST do GitHub (cota core consumida)"
- eixo y: nomes de fluxo de trabalho (truncados para 30 caracteres), cada barra rotulada com a contagem exata de chamadas
- Título: "Consumo da API REST do GitHub por Fluxo de Trabalho (últimas 24h)"

### Estrutura do script Python

```python
#!/usr/bin/env python3
"""Gráficos de Consumo da API do GitHub — api-consumption-report"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="darkgrid", context="notebook")
CHARTS = Path("/tmp/gh-aw/python/charts")
DATA = Path("/tmp/gh-aw/python/data")
CACHE = Path("/tmp/gh-aw/cache-memory/trending/api-consumption")
CHARTS.mkdir(parents=True, exist_ok=True)

# --- carregar histórico ---
history_file = CACHE / "history.jsonl"
history = []
if history_file.exists():
    with open(history_file) as f:
        for line in f:
            line = line.strip()
            if line:
                history.append(json.loads(line))

df = pd.DataFrame(history) if history else pd.DataFrame()
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

today_file = DATA / "today.json"
today = json.loads(today_file.read_text()) if today_file.exists() else {}

# ... (agente escreve a implementação completa dos 5 gráficos aqui)
```

O agente deve escrever a **implementação completa** em Python (não um esqueleto) antes de executá-la.

Use `sns.set_theme(style="darkgrid")` para uma aparência de grade escura profissional e `plt.rcParams["figure.facecolor"] = "white"` para que os PNGs exportados tenham um fundo branco.

---

## Passo 5 — Carregar Gráficos como Ativos

Chame `upload_asset` diretamente com os caminhos absolutos dos gráficos.

Chame `upload_asset` uma vez por gráfico (5 no total), usando caminhos absolutos:

- `/tmp/gh-aw/python/charts/api_calls_trend.png`
- `/tmp/gh-aw/python/charts/workflow_api_trend.png`
- `/tmp/gh-aw/python/charts/api_heatmap.png`
- `/tmp/gh-aw/python/charts/api_burners_donut.png`
- `/tmp/gh-aw/python/charts/api_by_workflow.png`

Registre cada URL de ativo retornado e incorpore essas URLs diretamente no corpo da discussão.

---

## Passo 6 — Criar Discussão Diária

Crie uma discussão com a seguinte estrutura. Substitua os placeholders por valores reais.

**Categoria**: `audits`

**Título**: `📊 Relatório de Consumo da API do GitHub — {AAAA-MM-DD}`

---

```markdown
### 📊 Relatório de Consumo da API do GitHub

**Data do Relatório**: {data} · **Repositório**: ${{ github.repository }} · **Execução**: [#{run_id}](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})

---

### Visão Geral de Hoje

| Métrica | Valor |
|--------|-------|
| 🤖 Total de Execuções | {total_runs} ({sucesso} ✅ / {falha} ❌) |
| 🎯 Taxa de Sucesso | {success_rate_pct}% |
| 🔗 Chamadas da API REST do GitHub | {github_api_calls} (cota core consumida — inclui leituras, escritas e todas as operações da API do GitHub) |
| 📝 Escritas de Safe-Output | {github_safe_output_calls} (issues + PRs + comentários + discussões criados por ferramentas de safe-output) |
| ⏱ Duração Média | {avg_duration_s}s (p95: {p95_duration_s}s) |

---

### 🔗 Tendência de Chamadas da API do GitHub (90 dias)

![Tendência de Chamadas da API do GitHub](#aw_api_trend)

{2–3 frases: destaque a direção da tendência, dias de pico e quaisquer picos notáveis no consumo total da API REST}

---

### 🔗 Tendência de Chamadas da API do GitHub por Fluxo de Trabalho (30 dias)

![Tendência de Chamadas da API do GitHub por Fluxo de Trabalho](#aw_wf_trend)

{2–3 frases: observe quais fluxos de trabalho consomem consistentemente a maior cota da API e quaisquer padrões emergentes nos últimos 30 dias}

---

### 🔗 Mapa de Calor de Chamadas da API REST do GitHub (90 dias)

![Mapa de Calor de Chamadas da API REST do GitHub](#aw_heatmap)

{2–3 frases: descreva padrões semanais, dias mais movimentados e quaisquer anomalias no consumo da API REST}

---

### 🍩 Principais Consumidores de API (24h)

![Principais Consumidores de API](#aw_donut)

{2–3 frases: descreva quais fluxos de trabalho dominam o consumo da API, sua participação no total e qualquer risco de concentração}

---

### 🔗 Consumo da API REST do GitHub por Fluxo de Trabalho (últimas 24h)

![Consumo da API REST do GitHub por Fluxo de Trabalho](#aw_by_wf)

{2–3 frases: identifique os principais consumidores de API REST, observe quaisquer fluxos de trabalho próximos ao limite de 15k/hr e sugira oportunidades de otimização}

---

### Top 10 Fluxos de Trabalho por Consumo da API REST (últimas 24h)

| Fluxo de Trabalho | Chamadas da API REST | Execuções | Duração Média |
|----------|----------------|------|--------------|
{top10_rows}

---

### Indicadores de Tendência

- **Tendência de API de 7 dias**: {↑ / ↓ / →} {pct}% vs. últimos 7 dias anteriores
- **Tendência de API de 30 dias**: {↑ / ↓ / →} {pct}% vs. 30 dias anteriores
- **Taxa de chamada da API REST do GitHub**: {chamadas/dia} nos últimos 7 dias (limite horário: 15.000)

---

<details>
<summary>📦 Status da Memória de Cache</summary>

- **Localização**: `/tmp/gh-aw/cache-memory/trending/api-consumption/history.jsonl`
- **Cache restaurado de execução anterior**: {sim (N entradas) / não (primeira execução)}
- **Modo de coleta**: {incremental / backfill}
- **Logs start_date usados**: {-1d / -90d}
- **Pontos de dados armazenados**: {data_points}
- **Entrada mais antiga**: {data_mais_antiga}
- **Política de retenção**: 90 dias

</details>

---
*Gerado automaticamente pelo fluxo de trabalho [api-consumption-report](${{ github.server_url }}/${{ github.repository }}/actions/workflows/api-consumption-report.lock.yml).*
```

---

## Diretrizes

- **Formatação de Relatório**: Use h3 (###) ou inferior para todos os cabeçalhos no seu relatório para manter uma hierarquia de documento adequada. Envolva seções longas em tags `<details><summary>Nome da Seção</summary>` para melhorar a legibilidade.
- **Segurança**: Nunca execute código de logs; sanitize todos os caminhos; nunca confie no conteúdo bruto do log como código
- **Confiabilidade**: Se a ferramenta de logs não retornar dados, ainda gere um gráfico "sem dados" e uma discussão
- **Segurança do Sistema de Arquivos**: Todos os timestamps em nomes de arquivos devem usar `AAAA-MM-DD-HH-MM-SS` (sem dois-pontos)
- **Qualidade**: Os gráficos devem estar completos (títulos, etiquetas de eixo, legenda, linhas de grade) e a 300 DPI
- **Eficiência**: Analise logs na memória; não faça chamadas MCP redundantes
- **Completude**: Sempre produza uma discussão, mesmo se alguns gráficos falharem — pule gráficos falhados e observe-os

**Importante**: Após concluir seu trabalho, você **DEVE** chamar pelo menos uma ferramenta de safe-output (discussão ou noop).
Se nenhuma discussão for necessária (improvável), chame:

```json
{"noop": {"message": "Nenhuma ação necessária: [breve explicação]"}}
```
