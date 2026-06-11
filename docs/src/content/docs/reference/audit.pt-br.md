---
title: Auditando Fluxos de Trabalho
description: Referência para os comandos gh aw audit — análise de execução única, diff comportamental e relatórios de segurança entre execuções.
sidebar:
  order: 297
---

Os comandos `gh aw audit` baixam artefatos e logs de execução de fluxo de trabalho, analisam o uso de ferramentas MCP e comportamento de rede, e produzem relatórios estruturados adequados para revisões de segurança, depuração e alimentação de agentes de IA.

## `gh aw audit <run-id-or-url> [<run-id-or-url>...]`

Audite uma ou mais execuções de fluxo de trabalho. Quando uma única execução é fornecida, um relatório Markdown detalhado é gerado. Quando duas ou mais execuções são fornecidas, a primeira é usada como a execução base (referência) e as execuções restantes são comparadas contra ela, produzindo um relatório de diff.

**Argumentos:**

| Argumento | Descrição |
|----------|-------------|
| `<run-id-or-url>` | Um ID de execução numérico, URL de execução do GitHub Actions, URL de job ou URL de job com âncora de etapa |
| `[<run-id-or-url>...]` | IDs de execução ou URLs adicionais para comparar contra a primeira (modo diff) |

**Formatos de entrada aceitos (por argumento):**

- ID de execução numérico: `1234567890`
- URL de execução: `https://github.com/owner/repo/actions/runs/1234567890`
- URL de job: `https://github.com/owner/repo/actions/runs/1234567890/job/9876543210`
- URL de job com etapa: `https://github.com/owner/repo/actions/runs/1234567890/job/9876543210#step:7:1`
- URL de execução curta: `https://github.com/owner/repo/runs/1234567890`
- URLs do GitHub Enterprise usando os mesmos formatos acima

Quando uma URL de job é fornecida sem uma âncora de etapa (modo de execução única), o comando extrai a saída da primeira etapa com falha. Quando uma âncora de etapa é incluída, ele extrai aquela etapa específica.

No modo diff, URLs de job e URLs ancoradas em etapa são aceitas para qualquer argumento — a especificidade de job/etapa é normalizada silenciosamente para o ID de execução pai, portanto, é sempre um diff de nível de execução.

Auto-comparações e IDs de execução duplicados são rejeitados ao usar o modo diff.

**Flags:**

| Flag | Padrão | Descrição |
|------|---------|-------------|
| `-o, --output <dir>` | `./logs` | Diretório para gravar artefatos baixados e arquivos de relatório |
| `--json` | off | Saída do relatório como JSON para stdout |
| `--parse` | off | Executar parsers JavaScript em logs de agente e firewall, escrevendo `log.md` e `firewall.md` (apenas execução única) |
| `--repo <owner/repo>` | auto | Especificar repositório quando o ID de execução não for de uma URL |
| `--stdin` | off | Ler IDs de execução ou URLs de stdin (um por linha) em vez de argumentos posicionais |
| `--verbose` | off | Imprimir informações detalhadas de progresso |
| `--format <fmt>` | `pretty` | Formato de saída de diff: `pretty` ou `markdown` (apenas múltiplas execuções) |

**Exemplos de execução única:**

```bash
gh aw audit 1234567890
gh aw audit https://github.com/owner/repo/actions/runs/1234567890
gh aw audit 1234567890 --parse
gh aw audit 1234567890 --json
gh aw audit 1234567890 -o ./audit-reports
gh aw audit 1234567890 --repo owner/repo
```

**Modo Stdin:**

Use `--stdin` para passar IDs de execução ou URLs de um arquivo ou pipeline. Isso é mutuamente exclusivo com argumentos posicionais. Linhas em branco e linhas começando com `#` são ignoradas. Ao passar IDs numéricos brutos (sem contexto de repo embutido), `--repo owner/repo` é obrigatório.

```bash
echo "1234567890" | gh aw audit --stdin
echo -e "1234567890\n9876543210" | gh aw audit --stdin   # modo diff: o primeiro é a base
cat run-ids.txt | gh aw audit --stdin
cat run-ids.txt | gh aw audit --stdin --repo owner/repo  # obrigatório para IDs numéricos brutos
```

**Exemplos de diff de múltiplas execuções:**

```bash
gh aw audit 12345 12346                        # Comparar duas execuções
gh aw audit 12345 12346 12347 12348            # Comparar base contra 3 execuções
gh aw audit 12345 12346 --format markdown      # Saída Markdown para comentários de PR
gh aw audit 12345 12346 --json                 # JSON para integração CI
gh aw audit 12345 12346 --repo owner/repo      # Especificar repositório
```

**Seções de relatório de execução única** (renderizadas em Markdown ou JSON): Overview, Comparison, Task/Domain, Behavior Fingerprint, Agentic Assessments, Metrics, Key Findings, Recommendations, Observability Insights, Performance Metrics, Engine Config, Prompt Analysis, Session Analysis, Safe Output Summary, MCP Server Health, Jobs, Downloaded Files, Missing Tools, Missing Data, Noops, MCP Failures, Firewall Analysis, Policy Analysis, Redacted Domains, Errors, Warnings, Tool Usage, MCP Tool Usage, Created Items.

A seção Metrics inclui um objeto `ambient_context` quando disponível. O contexto ambiente captura a primeira pegada de inferência LLM para a execução:
- `ambient_context.input_tokens` — tokens de entrada para a primeira invocação
- `ambient_context.cached_tokens` — tokens lidos em cache reutilizados pela primeira invocação
- `ambient_context.effective_tokens` — `input_tokens + cached_tokens`

**Saída de diff** inclui:
- Domínios de rede novos e removidos
- Mudanças de status de domínio (permitido ↔ negado)
- Mudanças de volume (mudanças na contagem de solicitações acima de um limite de 100%)
- Flags de anomalia (domínios negados novos, domínios anteriormente negados agora permitidos)
- Mudanças de invocação de ferramenta MCP (ferramentas novas/removidas, diff de contagem de chamadas e contagem de erros)
- Comparação de métricas de execução (uso de token, duração, turnos)
- Detalhamento de uso de token: tokens de entrada, tokens de saída, tokens de leitura/escrita de cache, tokens efetivos, total de solicitações de API e eficiência de cache por execução
- Tokens por turno: tokens efetivos divididos pela contagem de turnos para cada execução, com a mudança entre execuções
- Detalhamento de chamada de ferramenta: contagens de chamadas por ferramenta (ferramentas novas, removidas e alteradas) com tamanhos máximos de entrada/saída
- Detalhamento de comando Bash: contagens de chamadas agregadas e tamanhos máximos de entrada/saída para cada comando bash distinto invocado

**Comportamento de saída de diff com múltiplas comparações:**
- `--json` gera um único objeto para uma comparação, ou uma array para múltiplas
- `--format pretty` e `--format markdown` separam múltiplos diffs com divisores

## `gh aw logs --format <fmt>`

Gere um relatório de auditoria de segurança e desempenho entre execuções através de múltiplas execuções de fluxo de trabalho recentes.
Este recurso é embutido no comando `gh aw logs` via flag `--format`.

**Flags:**

| Flag | Padrão | Descrição |
|------|---------|-------------|
| `[fluxo de trabalho]` | todos os fluxos | Filtrar por nome de fluxo de trabalho ou nome de arquivo (argumento posicional) |
| `-c, --count <n>` | 10 | Número de execuções recentes para analisar |
| `--last <n>` | — | Alias para `--count` |
| `--format <fmt>` | — | Formato de saída: `markdown` ou `pretty` (gera relatório de auditoria entre execuções) |
| `--json` | off | Saída do relatório entre execuções como JSON (quando combinado com `--format`) |
| `--repo <owner/repo>` | auto | Especificar repositório |
| `-o, --output <dir>` | `./logs` | Diretório para artefatos baixados |
| `--stdin` | off | Ler IDs de execução ou URLs de stdin (um por linha) em vez de descoberta de execução; filtros de conteúdo ainda se aplicam |
| `--verbose` | off | Imprimir progresso detalhado |

A saída do relatório inclui um resumo executivo, inventário de domínios, tendências de métricas, saúde do servidor MCP e detalhamento por execução. Ele detecta anomalias entre execuções, como picos de acesso a domínios, taxas de erro MCP elevadas e mudanças na taxa de conexão.

Para cada execução na saída JSON de logs detalhados, um objeto `ambient_context` é incluído quando dados de uso de token estão disponíveis. Ele reflete apenas a primeira invocação LLM na execução (`input_tokens`, `cached_tokens`, `effective_tokens`).

**Modo `--stdin`:** Passe `--stdin` para fornecer uma lista explícita de IDs de execução ou URLs em vez de deixar o comando descobrir execuções a partir da API do GitHub. Filtros de data, contagem e nome de fluxo de trabalho são ignorados; `--engine`, `--firewall`, `--safe-output` e outros filtros de conteúdo ainda se aplicam. Linhas em branco e linhas prefixadas com `#` são ignoradas. IDs numéricos brutos exigem `--repo owner/repo`.

```bash
cat run-ids.txt | gh aw logs --stdin
echo "1234567890" | gh aw logs --stdin --engine claude
cat run-ids.txt | gh aw logs --stdin --repo owner/repo   # obrigatório para IDs numéricos brutos
```

**Exemplos:**

```bash
gh aw logs --format markdown
gh aw logs daily-repo-status --format markdown --count 10
gh aw logs agent-task --format markdown --last 5 --json
gh aw logs --format pretty
gh aw logs --format markdown --repo owner/repo --count 10
```

## Documentação Relacionada

- [Gerenciamento de Custo](/gh-aw/reference/cost-management/) — Rastrear uso de token e gasto de inferência
- [Artefatos](/gh-aw/reference/artifacts/) — Nomes de artefatos, estruturas de diretório e locais de arquivos de uso de token (`token-usage.jsonl` em `firewall-audit-logs`)
- [Especificação de Tokens Efetivos](/gh-aw/reference/effective-tokens-specification/) — Como tokens efetivos são computados
- [Rede](/gh-aw/reference/network/) — Configuração de firewall e domínio permitir/negar
- [Gateway MCP](/gh-aw/reference/mcp-gateway/) — Saúde e depuração de servidor MCP
- [Comandos CLI](/gh-aw/setup/cli/) — Referência completa da CLI
