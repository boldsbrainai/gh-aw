---
emoji: "🔍"
description: Investiga falhas [aw] das últimas 6 horas, correlaciona com issues abertas de agentic-workflows, fecha issues corrigidas e abre sub-issues de correção focadas quando necessário
on:
  schedule:
    - cron: "every 6h"  # A cada ~6 horas (dispersas para evitar thundering herd)
  workflow_dispatch:
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
tracker-id: aw-failure-investigator
engine: claude
tools:
  bash: ["*"]
cache:
  - key: aw-failure-investigator-prefetch-${{ github.run_id }}
    name: Prefetch do investigador de falhas
    path: /tmp/gh-aw/failure-investigator
safe-outputs:
  create-issue:
    expires: 7d
    title-prefix: "[aw-failures] "
    labels: [agentic-workflows, automation, cookie]
    max: 2
    group: true
  update-issue:
    target: "*"
    max: 10
  link-sub-issue:
    max: 10
  noop:
timeout-minutes: 60
imports:
  - uses: shared/meta-analysis-base.md
    with:
      toolsets: [default, actions]
  - shared/reporting.md

  - shared/otlp.md
steps:
  - name: Pré-fetch determinístico para análise de falhas
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      set -euo pipefail
      mkdir -p /tmp/gh-aw/failure-investigator
      python3 - <<'PY'
      import json
      import os
      import subprocess
      from datetime import datetime, timezone
      
      REPO = os.environ["GITHUB_REPOSITORY"]
      OUT = "/tmp/gh-aw/failure-investigator/prefetch.json"
      TRACKER_ID = "aw-failure-investigator"
      LOOKBACK = "-6h"
      MAX_FAILED_RUNS = 20
      MAX_RUNS_TO_FETCH = 200
      MAX_LOG_TAIL_LINES = 200
      
      def cmd_display(args):
          return " ".join(args)
      
      def run_json(args):
          try:
              out = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
              return json.loads(out)
          except subprocess.CalledProcessError as error:
              print(f"Aviso: comando falhou: {cmd_display(args)}")
              print(error.output)
              return None
          except json.JSONDecodeError as error:
              print(f"Aviso: saída não-JSON do comando: {cmd_display(args)} ({error})")
              return None
          except OSError as error:
              print(f"Aviso: não foi possível executar o comando: {cmd_display(args)} ({error})")
              return None
      
      def run_text(args):
          try:
              return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
          except subprocess.CalledProcessError as error:
              print(f"Aviso: comando falhou: {cmd_display(args)}")
              print(error.output)
              return ""
          except OSError as error:
              print(f"Aviso: não foi possível executar o comando: {cmd_display(args)} ({error})")
              return ""
      
      logs = run_json(["gh", "aw", "logs", "--start-date", LOOKBACK, "--json", "-c", str(MAX_RUNS_TO_FETCH)]) or {"runs": []}
      failed_runs = []
      for run in logs.get("runs", []):
          if (run.get("conclusion") or "").lower() != "failure":
              continue
          failed_runs.append(
              {
                  "run_id": run.get("run_id"),
                  "workflow_name": run.get("workflow_name"),
                  "workflow_path": run.get("workflow_path"),
                  "created_at": run.get("created_at"),
                  "status": run.get("status"),
                  "conclusion": run.get("conclusion"),
                  "url": run.get("url"),
              }
          )
          if len(failed_runs) >= MAX_FAILED_RUNS:
              break
      
      failure_details = []
      for run in failed_runs:
          run_id = run.get("run_id")
          if not run_id:
              continue
      
          run_view = run_json(
              [
                  "gh",
                  "run",
                  "view",
                  str(run_id),
                  "--repo",
                  REPO,
                  "--json",
                  "databaseId,url,name,workflowName,createdAt,conclusion,status,jobs",
              ]
          )
          if not run_view:
              continue
      
          failed_steps = []
          truncated_error_logs = []
          for job in run_view.get("jobs", []):
              if (job.get("conclusion") or "").lower() == "failure":
                  for step in job.get("steps", []):
                      if (step.get("conclusion") or "").lower() == "failure":
                          failed_steps.append(
                              {
                                  "job_id": job.get("databaseId"),
                                  "job_name": job.get("name"),
                                  "step_name": step.get("name"),
                              }
                          )
      
                  job_id = job.get("databaseId")
                  if job_id:
                      log_text = run_text(
                          [
                              "gh",
                              "run",
                              "view",
                              str(run_id),
                              "--repo",
                              REPO,
                              "--job",
                              str(job_id),
                              "--log-failed",
                          ]
                      )
                      if log_text:
                          tail_lines = log_text.splitlines()[-MAX_LOG_TAIL_LINES:]
                          truncated_error_logs.append(
                              {
                                  "job_id": job_id,
                                  "job_name": job.get("name"),
                                  "line_count": len(tail_lines),
                                  "tail_200_lines": "\n".join(tail_lines),
                              }
                          )
      
          failure_details.append(
              {
                  "run_id": run_id,
                  "workflow_name": run_view.get("workflowName") or run_view.get("name"),
                  "url": run_view.get("url"),
                  "created_at": run_view.get("createdAt"),
                  "status": run_view.get("status"),
                  "conclusion": run_view.get("conclusion"),
                  "failed_steps": failed_steps,
                  "truncated_error_logs": truncated_error_logs,
              }
          )
      
      existing_tracking_issues = run_json(
          [
              "gh",
              "issue",
              "list",
              "--repo",
              REPO,
              "--state",
              "open",
              "--search",
              f"gh-aw-tracker-id: {TRACKER_ID}",
              "--limit",
              "100",
              "--json",
              "number,title,state,url,labels,createdAt,updatedAt",
          ]
      ) or []
      
      payload = {
          "generated_at": datetime.now(timezone.utc).isoformat(),
          "repository": REPO,
          "lookback_window": "6h",
          "failed_run_ids": [run.get("run_id") for run in failed_runs if run.get("run_id")],
          "failures": failure_details,
          "existing_tracking_issues": existing_tracking_issues,
      }
      
      with open(OUT, "w", encoding="utf-8") as f:
          json.dump(payload, f, indent=2)
          f.write("\n")
      
      print(f"Escreveu payload de prefetch determinístico para {OUT}")
      print(f"Execuções com falha no payload: {len(payload['failed_run_ids'])}")
      print(f"Issues de rastreamento existentes no payload: {len(existing_tracking_issues)}")
      PY
---

# [aw] Investigador de Falhas (6h)

Investiga falhas de workflows agenticos das últimas 6 horas e produz rastreamento de issues acionável com sub-issues.

## Escopo

- **Repositório**: `${{ github.repository }}`
- **Janela de lookback**: últimas 6 horas
- **Query de issue para inspecionar primeiro**: <https://github.com/github/gh-aw/issues?q=is%3Aissue%20state%3Aopen%20label%3Aagentic-workflows>
- **Payload de pre-fetch determinístico**: `/tmp/gh-aw/failure-investigator/prefetch.json`

## Missão

1. Encontrar falhas recentes de workflows agenticos nas últimas 6 horas.
2. Correlacionar descobertas com issues de `agentic-workflows` atualmente abertas.
3. Realizar análise de falha em larga escala usando logs + auditoria + audit-diff.
4. Fechar issues corrigidas/obsoletas primeiro, depois criar apenas o mínimo necessário de sub-issues de correção vinculadas.

## Etapas de Investigação Necessárias

### 0) Use o payload de pre-fetch determinístico primeiro (obrigatório)

Leia `/tmp/gh-aw/failure-investigator/prefetch.json` primeiro. Ele já inclui:
- IDs de execuções com falha recentes para a janela de 6 horas
- Nomes de etapas com falha
- Logs de erro truncados (até as últimas 200 linhas por job com falha)
- Issues de rastreamento abertas existentes filtradas por `gh-aw-tracker-id: aw-failure-investigator`

Use este payload como o conjunto de dados de descoberta primária. Chame APIs adicionais de logs/listagem apenas quando um campo estiver ausente ou obsoleto.

### 1) Buscar e revisar contexto de issue existente

Use o agente `issue-context-fetcher` para recuperar issues de `agentic-workflows` abertas agrupadas em clusters, lacunas e possíveis duplicatas. Mescle isso com `existing_tracking_issues` do payload de pre-fetch ao correlacionar falhas.

### 2) Coletar execuções de workflow e isolar falhas (últimas 6h)

Comece a partir de `failed_run_ids` e `failures` no payload de pre-fetch para construir linhas de falha agrupadas com IDs de execução representativos + comparadores.
Execute consultas de logs adicionais apenas se o payload de pre-fetch não puder suportar uma decisão de cluster.

### 3) Aprofundar cada cluster de falha com `audit`

Use o agente `cluster-evidence-extractor`, passando os clusters da etapa 2, para recuperar evidências por cluster (erro dominante, padrão de falha de ferramenta, anomalias, classe de falha).

### 4) Comparar comportamento com `audit-diff`

Use o `audit-diff` do MCP `agentic-workflows` para comparar:
- execução com falha vs. execução bem-sucedida mais próxima do mesmo workflow, ou
- execução com falha vs. execução com falha anterior para detectar desvio (drift)

Identifique regressões e deltas (métricas/ferramentas/firewall/comportamento do MCP) que suportam recomendações de correção.

### 5) Fechar issues corrigidas primeiro, depois adicionar sub-issues focadas

Primeiro, identifique issues de `agentic-workflows` atualmente abertas que estão agora corrigidas, obsoletas ou não mais acionáveis com base em novas evidências, e feche-as usando `update-issue`.

Então, se permanecer trabalho não coberto, adicione **sub-issues** para correções concretas à **issue de relatório pai mais recente** em vez de criar um novo pai por padrão.

Crie uma nova issue de relatório pai (formato de ID temporário `aw_` + 3-8 alfanuméricos) apenas quando **falhas P0 não tiverem cobertura de rastreamento existente**.

Cada sub-issue nova deve incluir:
- declaração clara do problema
- workflows afetados e IDs de execução
- causa raiz provável
- remediação proposta específica
- critérios de sucesso / verificação

## Requisitos de Saída

**Formatação do Relatório**: Use `###` ou inferior para todos os cabeçalhos no corpo da issue. Envolva trechos de evidência/logs e tabelas prolixas em tags `<details><summary>Nome da Seção</summary>` para melhorar a legibilidade.

### Estrutura da issue de relatório pai

Inclua estas seções:
1. Resumo executivo
2. Clusters de falha (tabela)
3. Evidência (logs/auditoria/audit-diff)
4. Correlação de issue existente
5. Roadmap de correção proposto (P0/P1/P2)
6. Sub-issues criadas

### Barra de qualidade da sub-issue

- Prefira algumas sub-issues de alta qualidade e acionáveis a muitas fracas.
- Evite duplicatas de issues já abertas, a menos que novas evidências alterem materialmente o escopo.
- Referencie a issue pai e os IDs de execução concretos analisados.

## Regras de Decisão

- Se não houver **falhas** nas últimas 6h, ou nenhum delta acionável vs issues existentes, chame `noop` com um motivo conciso.
- Se existirem falhas, mas já estiverem totalmente rastreadas, prefira fechar issues obsoletas/corrigidas e evite criar novas issues.
- Crie uma nova issue de relatório pai apenas quando falhas P0 não tiverem cobertura de rastreamento existente.
- Prefira fechar issues obsoletas/corrigidas em vez de criar novas issues quando o volume de issues for alto.
- Sempre seja explícito sobre confiança e desconhecidos.

**Importante**: Se nenhuma ação for necessária após concluir sua análise, você **DEVE** chamar a ferramenta de safe-output `noop` com uma breve explicação.

```json
{"noop": {"message": "Nenhuma ação necessária: [breve explicação do que foi analisado e por que]"}}
```
