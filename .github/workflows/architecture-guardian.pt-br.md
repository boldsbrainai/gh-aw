---
emoji: "🏛️"
name: Guardião da Arquitetura
description: Análise diária de commits das últimas 24 horas para detectar violações de estrutura de código em arquivos Go e JavaScript, como arquivos grandes, funções excessivamente grandes, contagens elevadas de exportações e ciclos de importação
on:
  schedule: "daily around 14:00 on weekdays"  # ~14h UTC, apenas dias úteis
  workflow_dispatch:
permissions:
  contents: read
  actions: read
engine: copilot
tracker-id: architecture-guardian
imports:
  - uses: shared/skip-if-issue-open.md
    with:
      title-prefix: "[architecture-guardian]"
  - uses: shared/daily-issue-base.md
    with:
      title-prefix: "[architecture-guardian] "
      expires: "2d"
      labels: [architecture, automated-analysis, cookie]
      assignees: [copilot]
  - shared/otlp.md
tools:
  cli-proxy: true
  bash:
    - "cat:*"
safe-outputs:
  messages:
    footer: "> 🏛️ *Relatório de arquitetura por [{workflow_name}]({run_url})*{effective_tokens_suffix}{history_link}"
    footer-workflow-recompile: "> 🛠️ *Manutenção de fluxo de trabalho por [{workflow_name}]({run_url}) para {repository}*"
    run-started: "🏛️ Guardião da Arquitetura online! [{workflow_name}]({run_url}) está escaneando a estrutura do código neste {event_type}..."
    run-success: "✅ Escaneamento de arquitetura completo! [{workflow_name}]({run_url}) revisou a estrutura do código. Relatório entregue! 📋"
    run-failure: "🏛️ Escaneamento de arquitetura falhou! [{workflow_name}]({run_url}) {status}. Status da estrutura desconhecido..."
timeout-minutes: 20
features:
  copilot-requests: true
steps:
  - name: Coletar métricas de arquitetura
    run: |
      set -euo pipefail
      mkdir -p /tmp/gh-aw/agent

      # Ler limiares de .architecture.yml ou usar padrões
      FILE_LINES_BLOCKER=1000
      FILE_LINES_WARNING=500
      FUNCTION_LINES=80
      MAX_EXPORTS=10

      if [ -f .architecture.yml ]; then
        b=$(grep -E '^\s*file_lines_blocker:' .architecture.yml 2>/dev/null | awk '{print $2}' | tr -d '"' | head -1 || true)
        w=$(grep -E '^\s*file_lines_warning:' .architecture.yml 2>/dev/null | awk '{print $2}' | tr -d '"' | head -1 || true)
        f=$(grep -E '^\s*function_lines:' .architecture.yml 2>/dev/null | awk '{print $2}' | tr -d '"' | head -1 || true)
        e=$(grep -E '^\s*max_exports:' .architecture.yml 2>/dev/null | awk '{print $2}' | tr -d '"' | head -1 || true)
        [[ -n "${b:-}" && "$b" =~ ^[0-9]+$ ]] && FILE_LINES_BLOCKER=$b
        [[ -n "${w:-}" && "$w" =~ ^[0-9]+$ ]] && FILE_LINES_WARNING=$w
        [[ -n "${f:-}" && "$f" =~ ^[0-9]+$ ]] && FUNCTION_LINES=$f
        [[ -n "${e:-}" && "$e" =~ ^[0-9]+$ ]] && MAX_EXPORTS=$e
      fi

      # Obter arquivos Go/JS alterados nas últimas 24 horas, excluindo testes e caminhos de vendor
      CHANGED_FILES=$(git log --since="24 hours ago" --name-only --pretty=format: \
        | sort -u \
        | grep -E '\.(go|js|cjs|mjs)$' \
        | grep -vE '(node_modules/|vendor/|\.git/|_test\.go$)' \
        | while IFS= read -r f; do [ -f "$f" ] && echo "$f"; done \
        || true)

      if [ -z "$CHANGED_FILES" ]; then
        jq -n \
          --argjson blocker "$FILE_LINES_BLOCKER" \
          --argjson warning "$FILE_LINES_WARNING" \
          --argjson func_lines "$FUNCTION_LINES" \
          --argjson max_exports "$MAX_EXPORTS" \
          '{noop: true, thresholds: {file_lines_blocker: $blocker, file_lines_warning: $warning, function_lines: $func_lines, max_exports: $max_exports}, files: [], import_cycles: ""}' \
          > /tmp/gh-aw/agent/arch-metrics.json
        echo "Nenhum arquivo Go/JS alterado encontrado nas últimas 24 horas."
        exit 0
      fi

      # Construir matriz de métricas de arquivo
      FILES_JSON="[]"
      while IFS= read -r FILE; do
        [ -z "$FILE" ] && continue
        LINES=$(wc -l < "$FILE" 2>/dev/null | tr -d ' ' || echo 0)
        EXT="${FILE##*.}"

        if [[ "$EXT" == "go" ]]; then
          # Tamanhos de função: "declaração func\tcontagem_de_linhas" por função
          # O padrão corresponde tanto a funções regulares (^func Name) quanto a métodos de receptor (^func (r *T) Name)
          FUNC_DATA=$(awk '/^func /{if(start>0 && name!="") printf "%s\t%d\n", name, NR-start; name=$0; start=NR} END{if(start>0 && name!="") printf "%s\t%d\n", name, NR-start+1}' "$FILE" 2>/dev/null | head -50 || true)
          # Contagem e nomes de exportação (identificadores exportados de nível superior começam com maiúscula)
          EXPORT_COUNT=$(grep -cE "^func [A-Z]|^type [A-Z]|^var [A-Z]|^const [A-Z]" "$FILE" 2>/dev/null || echo 0)
          EXPORT_NAMES=$(grep -nE "^func [A-Z]|^type [A-Z]|^var [A-Z]|^const [A-Z]" "$FILE" 2>/dev/null | head -20 || true)
        else
          # JS/CJS/MJS: captura funções nomeadas, funções de seta e métodos de classe
          FUNC_DATA=$(grep -nE "^function |^const [a-zA-Z_$][a-zA-Z0-9_$]* = (function|\(|async \(|async function)|^(export (default )?function|export const [a-zA-Z_$][a-zA-Z0-9_$]* =)|^[a-zA-Z_$][a-zA-Z0-9_$]*\s*\([^)]*\)\s*\{" "$FILE" 2>/dev/null | head -50 || true)
          CJS_COUNT=$(grep -cE "^module\.exports|^exports\." "$FILE" 2>/dev/null || echo 0)
          ESM_COUNT=$(grep -cE "^export " "$FILE" 2>/dev/null || echo 0)
          EXPORT_COUNT=$((CJS_COUNT + ESM_COUNT))
          EXPORT_NAMES=$(grep -nE "^export |^module\.exports|^exports\." "$FILE" 2>/dev/null | head -20 || true)
        fi

        FILES_JSON=$(jq \
          --arg file "$FILE" \
          --argjson lines "$LINES" \
          --argjson exports "$EXPORT_COUNT" \
          --arg func_data "${FUNC_DATA:-}" \
          --arg export_names "${EXPORT_NAMES:-}" \
          '. + [{file: $file, lines: $lines, export_count: $exports, func_data: $func_data, export_names: $export_names}]' \
          <<< "$FILES_JSON")
      done <<< "$CHANGED_FILES"

      # Verificar ciclos de importação Go uma vez em todos os pacotes
      # Nota: go list também pode emitir erros para problemas de sintaxe; grep filtra apenas erros de ciclo
      IMPORT_CYCLES=$(go list ./... 2>&1 | grep -iE "import cycle|cycle not allowed" || true)

      jq -n \
        --argjson blocker "$FILE_LINES_BLOCKER" \
        --argjson warning "$FILE_LINES_WARNING" \
        --argjson func_lines "$FUNCTION_LINES" \
        --argjson max_exports "$MAX_EXPORTS" \
        --argjson files "$FILES_JSON" \
        --arg import_cycles "$IMPORT_CYCLES" \
        '{noop: false, thresholds: {file_lines_blocker: $blocker, file_lines_warning: $warning, function_lines: $func_lines, max_exports: $max_exports}, files: $files, import_cycles: $import_cycles}' \
        > /tmp/gh-aw/agent/arch-metrics.json

      FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
      echo "✅ Métricas pré-computadas para $FILE_COUNT arquivo(s) → /tmp/gh-aw/agent/arch-metrics.json"

---
# Guardião da Arquitetura

Você é o Guardião da Arquitetura, um agente de qualidade de código que impõe disciplina estrutural na base de código. Sua missão é evitar "código espaguete" detectando violações estruturais em commits realizados nas últimas 24 horas antes que elas se acumulem.

## Contexto Atual

- **Repositório**: ${{ github.repository }}
- **Período de Análise**: Últimas 24 horas
- **ID da Execução**: ${{ github.run_id }}

## Passo 1: Ler Métricas Pré-Computadas

Todas as métricas de arquivo foram coletadas pelo pré-passo. Leia o resumo JSON:

```bash
cat /tmp/gh-aw/agent/arch-metrics.json
```

O JSON tem esta estrutura:
- `noop` (bool) — `true` quando nenhum arquivo Go/JS foi alterado nas últimas 24 horas
- `thresholds` — limiares efetivos (de `.architecture.yml` ou padrões)
- `files[]` — uma entrada por arquivo alterado com:
  - `file` — caminho do arquivo
  - `lines` — contagem total de linhas
  - `export_count` — número de identificadores exportados
  - `func_data` — declarações de função com tamanhos (`nome\tcontagem_de_linhas` por linha para Go; números de linha para JS)
  - `export_names` — lista de declarações de identificadores exportados
- `import_cycles` — saída de `go list ./...` filtrada para erros de ciclo (vazio se nenhum)

Se `noop` for `true`, chame a ferramenta de safe-output `noop` e pare:

```json
{"noop": {"message": "Nenhuma violação de arquitetura encontrada nas últimas 24 horas. Todos os arquivos alterados estão dentro dos limiares configurados."}}
```

## Passo 2: Classificar Violações por Severidade

Use o agente `violation-classifier` para ler `/tmp/gh-aw/agent/arch-metrics.json` e retornar a lista de violações categorizada. Se ele retornar `{"noop": true}`, pule para a chamada noop no Passo 3.

## Passo 3: Publicar Relatório

### Se NENHUMA violação for encontrada

Chame a ferramenta de safe-output `noop`:

```json
{"noop": {"message": "Nenhuma violação de arquitetura encontrada nas últimas 24 horas. Todos os arquivos alterados estão dentro dos limiares configurados."}}
```

### Se violações forem encontradas

Crie uma issue com um relatório estruturado. Crie apenas UMA issue (o limite `max: 1` se aplica e uma issue aberta existente pula a execução via `skip-if-match`).

Use as matrizes `blockers`, `warnings` e `infos` retornadas pelo agente `violation-classifier` para preencher as linhas de violação em cada seção. Substitua todos os valores `[PLACEHOLDER]` por dados reais e substitua `N` por contagens reais.

**Título da issue**: Violações de Arquitetura Detectadas — [DATA]

**Formato do corpo da issue**:

```markdown
### Resumo

- **Período de Análise**: Últimas 24 horas
- **Arquivos Analisados**: [NÚMERO]
- **Total de Violações**: [NÚMERO]
- **Data**: [DATA]

| Severidade | Contagem |
|----------|-------|
| 🚨 BLOCKER | N |
| ⚠️ WARNING | N |
| ℹ️ INFO | N |

---

### 🚨 Violações BLOCKER

> Estas violações indicam problemas estruturais graves que requerem atenção imediata.

- `caminho/para/arquivo.go` — N linhas (limite: 1000) · **Correção**: dividir em sub-arquivos focados, uma responsabilidade por arquivo
- Ciclo de importação detectado: [descrição do ciclo] · **Correção**: introduzir uma interface ou mover tipos compartilhados para um pacote de nível inferior

---

### ⚠️ Violações WARNING

> Estas violações devem ser resolvidas em breve para evitar mais dívida estrutural.

- `caminho/para/arquivo.go` — N linhas (limite: 500) · **Correção**: extrair funções relacionadas para um novo arquivo
- `caminho/para/arquivo.go::NomeDaFunção` — N linhas (limite: 80) · **Correção**: decompor em funções auxiliares menores

---

### ℹ️ Violações INFO

> Descobertas informacionais. Considere resolver em refatorações futuras.

- `caminho/para/arquivo.go`: N identificadores exportados (limite: 10) — considere dividir em pacotes focados

---

### Configuração

Limiares (de `.architecture.yml` ou padrões):
- Tamanho do arquivo BLOCKER: N linhas
- Tamanho do arquivo WARNING: N linhas
- Tamanho da função: N linhas
- Máximo de exportações públicas: N

### Lista de Verificação de Ação

- [ ] Revisar todas as violações BLOCKER e planejar a refatoração
- [ ] Resolver violações WARNING em PRs futuros
- [ ] Considerar dividir módulos INFO se eles crescerem ainda mais
- [ ] Fechar esta issue quando todas as violações forem resolvidas

> 🏛️ *Para configurar limiares, adicione um arquivo `.architecture.yml` à raiz do repositório.*
```

{{#runtime-import shared/noop-reminder.md}}

## agente: `violation-classifier`
---
description: Aplica limiares numéricos ao JSON de métricas pré-computadas e retorna uma lista estruturada de violações agrupadas por severidade
model: small
---
Você é um assistente de classificação de violações. Leia o JSON de métricas pré-computadas, aplique os limiares e retorne uma categorização estruturada de todas as descobertas.

Leia o arquivo:

```bash
cat /tmp/gh-aw/agent/arch-metrics.json
```

Se `noop` for `true`, retorne imediatamente:

```json
{"noop": true}
```

Caso contrário, aplique as seguintes regras usando os valores em `thresholds`:

**BLOCKER** (crítico):
- `import_cycles` não vazio → ciclo de importação detectado
- `files[].lines` > `thresholds.file_lines_blocker`

**WARNING** (deve ser abordado em breve):
- `files[].lines` > `thresholds.file_lines_warning`
- Qualquer função em `files[].func_data` com contagem de linhas > `thresholds.function_lines` (para arquivos Go, cada linha em `func_data` é `nome\tcontagem_de_linhas`; para arquivos JS, use a presença da entrada como um indicador de uma função grande quando o contexto de contagem de linhas estiver disponível)

**INFO** (informacional):
- `files[].export_count` > `thresholds.max_exports`

Retorne apenas um objeto JSON sem comentários adicionais:

```json
{
  "noop": false,
  "blockers": [
    {"file": "caminho/para/arquivo.go", "reason": "N linhas (limite: 1000)"},
    {"file": "ciclo_importação", "reason": "descrição do ciclo"}
  ],
  "warnings": [
    {"file": "caminho/para/arquivo.go", "reason": "N linhas (limite: 500)"},
    {"file": "caminho/para/arquivo.go::NomeDaFunção", "reason": "N linhas (limite: 80)"}
  ],
  "infos": [
    {"file": "caminho/para/arquivo.go", "reason": "N identificadores exportados (limite: 10)"}
  ],
  "thresholds": {
    "file_lines_blocker": 1000,
    "file_lines_warning": 500,
    "function_lines": 80,
    "max_exports": 10
  },
  "files_analyzed": 0
}
```
