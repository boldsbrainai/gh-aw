---
emoji: "📊"
name: Rendimento do Portfólio de Workflow Agentico
description: Análise semanal do portfólio de workflows agenticos usando pontuação determinística, detecção de sobreposição e evidências apoiadas por OTel para recomendações de governança
on:
  schedule: weekly on monday around 09:00
  workflow_dispatch:
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
engine: copilot
strict: true
timeout-minutes: 25
network:
  allowed: [defaults, github]
tools:
  bash: true
  github:
    mode: gh-proxy
    toolsets: [default, actions, pull_requests]
safe-outputs:
  mentions: false
  allowed-github-references: []
  create-issue:
    labels: [automation, report, observability]
    max: 1
    close-older-issues: true
    expires: 30d
imports:
  - shared/mcp/grafana.md
  - shared/otlp.md
  - shared/otel-queries.md
pre-agent-steps:
  - name: Coletar instantâneo de telemetria do workflow
    uses: actions/github-script@v9
    env:
      AW_YIELD_TELEMETRY_OUT: /tmp/aw-yield-telemetry-summary.json
    with:
      script: |
        const fs = require("fs");
        const owner = context.repo.owner;
        const repo = context.repo.repo;
        const now = Date.now();
        const windowMs = 90 * 24 * 60 * 60 * 1000;
        const workflowIdToSourcePath = new Map();
        const workflows = await github.paginate(github.rest.actions.listRepoWorkflows, {
          owner,
          repo,
          per_page: 100,
        });
        for (const workflow of workflows) {
          const workflowPath = workflow.path || "";
          if (!workflowPath.startsWith(".github/workflows/") || !workflowPath.endsWith(".lock.yml")) {
            continue;
          }
          workflowIdToSourcePath.set(workflow.id, workflowPath.replace(/\.lock\.yml$/, ".md"));
        }

        const aggregates = new Map();
        let pageCount = 0;
        let reachedWindowLimit = false;
        for await (const page of github.paginate.iterator(github.rest.actions.listWorkflowRunsForRepo, {
          owner,
          repo,
          status: "completed",
          per_page: 100,
        })) {
          pageCount += 1;
          for (const run of page.data.workflow_runs || []) {
            const sourcePath = workflowIdToSourcePath.get(run.workflow_id);
            if (!sourcePath) {
              continue;
            }
            const createdAt = run.created_at ? Date.parse(run.created_at) : Number.NaN;
            if (!Number.isNaN(createdAt) && createdAt < now - windowMs) {
              reachedWindowLimit = true;
              break;
            }
            const startedAt = run.run_started_at ? Date.parse(run.run_started_at) : Number.NaN;
            const updatedAt = run.updated_at ? Date.parse(run.updated_at) : Number.NaN;
            const durationSeconds =
              !Number.isNaN(startedAt) && !Number.isNaN(updatedAt) && updatedAt >= startedAt
                ? (updatedAt - startedAt) / 1000
                : 0;
            const aggregate = aggregates.get(sourcePath) || {
              runs: 0,
              successfulRuns: 0,
              runtimeSeconds: 0,
              runtimeSamples: 0,
            };
            aggregate.runs += 1;
            if (run.conclusion === "success") {
              aggregate.successfulRuns += 1;
            }
            if (durationSeconds > 0) {
              aggregate.runtimeSeconds += durationSeconds;
              aggregate.runtimeSamples += 1;
            }
            aggregates.set(sourcePath, aggregate);
          }
          if (reachedWindowLimit || pageCount >= 10) {
            break;
          }
        }

        const workflow_metrics = {};
        for (const [path, aggregate] of aggregates.entries()) {
          workflow_metrics[path] = {
            workflow_path: path,
            workflow_invocation_count: aggregate.runs,
            success_rate: aggregate.runs ? Number((aggregate.successfulRuns / aggregate.runs).toFixed(4)) : 0,
            runtime_duration: aggregate.runtimeSamples
              ? Number((aggregate.runtimeSeconds / aggregate.runtimeSamples).toFixed(2))
              : 0,
            observed: aggregate.runs > 0,
            validated: aggregate.runs > 0,
            source: "github-actions-runs",
          };
        }

        fs.writeFileSync(
          process.env.AW_YIELD_TELEMETRY_OUT,
          JSON.stringify(
            {
              generated_at: new Date().toISOString(),
              source: "github-actions-runs",
              window_days: 90,
              workflow_metrics,
            },
            null,
            2,
          ) + "\n",
        );
  - name: Pré-computar dados do portfólio de workflow
    uses: actions/github-script@v9
    env:
      AW_YIELD_WORKSPACE: ${{ github.workspace }}
      AW_YIELD_WORKFLOWS: .github/workflows
      AW_YIELD_OUT: /tmp/aw-yield-precompute.json
      AWY_OTEL_SUMMARY_JSON: /tmp/aw-yield-telemetry-summary.json
    with:
      script: |
        const path = require("path");
        const { runPrecompute } = require(path.join(process.env.AW_YIELD_WORKSPACE, "scripts/aw_yield_precompute.cjs"));
        await runPrecompute({
          workspace: process.env.AW_YIELD_WORKSPACE,
          workflows: process.env.AW_YIELD_WORKFLOWS,
          out: process.env.AW_YIELD_OUT,
        });
post-steps:
  - name: Finalizar relatório de portfólio de workflow
    uses: actions/github-script@v9
    env:
      AW_YIELD_WORKSPACE: ${{ github.workspace }}
      AW_YIELD_PRECOMPUTE: /tmp/aw-yield-precompute.json
      AW_YIELD_AGENT_OUTPUT: /tmp/gh-aw
      AW_YIELD_OUT: /tmp/aw-yield-final.json
    with:
      script: |
        const path = require("path");
        const { runPostcompute } = require(path.join(process.env.AW_YIELD_WORKSPACE, "scripts/aw_yield_postcompute.cjs"));
        await runPostcompute({
          workspace: process.env.AW_YIELD_WORKSPACE,
          precompute: process.env.AW_YIELD_PRECOMPUTE,
          agentOutput: process.env.AW_YIELD_AGENT_OUTPUT,
          out: process.env.AW_YIELD_OUT,
        });
---
# Rendimento do Portfólio de Workflow Agentico

Você é o intérprete semântico do portfólio de workflows agenticos do repositório.

## Regras Rígidas

- Trate `/tmp/aw-yield-precompute.json` como a fonte factual da verdade.
- Telemetria = fatos. Pré-computação/Pós-computação determinística = matemática. Agente = interpretação.
- **Não** recompute pontuações brutas, classificação, valores de sobreposição, frações ou matemática de portfólio do zero.
- **Não** invente telemetria, economia, confiança ou evidências de sucesso.
- Quando a telemetria existir, use o servidor Grafana MCP neste workflow para validar a telemetria pré-computada com rastreamentos recentes do `gh-aw` antes de finalizar as recomendações.
- Não execute ações de escrita com as ferramentas do GitHub.

## Escopo de Interpretação Necessário

Avalie explicitamente estes três níveis:

1. **Nível de workflow** — vale a pena executar cada workflow?
2. **Nível de episódio** — grupos de workflows relacionados criam valor ou atraso de coordenação?
3. **Nível de portfólio** — o ecossistema geral de workflows está se tornando mais coerente e reutilizável, ou mais fragmentado e ruidoso?

## Entradas

Leia e confie em:

- `/tmp/aw-yield-precompute.json`
- Sementes de recomendação de workflow já computadas lá
- Clusters de sobreposição já computados lá
- Sinais de saúde organizacional já computados lá
- Resumos de telemetria opcionais já inseridos no payload de pré-computação

## Entregáveis

1. Escreva `/tmp/gh-aw/portfolio-yield-agent.json` com este formato:

```json
{
  "executive_summary": "",
  "recommendations": {
    "keep": [{"path": "", "reason": ""}],
    "revise": [{"path": "", "reason": ""}],
    "merge": [{"path": "", "reason": ""}],
    "instrument": [{"path": "", "reason": ""}],
    "retire": [{"path": "", "reason": ""}]
  },
  "highest_value_actions": ["", "", ""],
  "deterministic_vs_agentic_findings": [""],
  "episode_observations": [""],
  "retirement_candidates": [""],
  "consolidation_opportunities": [""],
  "instrumentation_gaps": [""],
  "telemetry_claims": []
}
```

2. Produza exatamente uma saída segura `create_issue` intitulada:

`Relatório de Rendimento do Portfólio de Workflow Agentico — AAAA-MM-DD`

3. O corpo da issue deve incluir estas seções:

- `# Relatório de Rendimento do Portfólio de Workflow Agentico`
- `## Resumo Executivo`
- `## Saúde do Portfólio`
- `## Portfólio de Workflow`
- `## Clusters de Sobreposição`
- `## Observações em Nível de Episódio` (apenas se houver evidências)
- `## Sinais de Saúde Organizacional`
- `## Descobertas Determinísticas vs Agenticas`
- `## Ações de Maior Valor`
- `## Candidatos à Aposentadoria`
- `## Oportunidades de Consolidação`
- `## Lacunas de Instrumentação`
- `## JSON do Portfólio Determinístico`

## Regras de Recomendação

- Keep (Manter) = alto rendimento, alta confiança, baixo risco, baixa sobreposição.
- Revise (Revisar) = utilidade plausível, mas custo excessivo, arrasto de manutenção, risco ou fração agentica.
- Merge (Mesclar) = workflows ou clusters sobrepostos competindo pelo mesmo nicho.
- Instrument (Instrumentar) = falta de telemetria, observabilidade ou evidência segura.
- Retire (Aposentar) = baixo rendimento, baixa confiança e alto arrasto.

## Uso

Este workflow é executado semanalmente e também suporta `workflow_dispatch` manual para revisões de portfólio sob demanda.
