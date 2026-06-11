---
name: github-pr-query
description: Consulte pull requests do GitHub com filtragem jq e seletores reutilizáveis.
---

# Habilidade de Consulta de Pull Request do GitHub

Consulte pull requests do GitHub de forma eficiente com filtragem jq integrada.

## Importante: O Parâmetro jq é Opcional

O parâmetro `--jq` é **opcional**. Sem `--jq`, esta habilidade retorna **informações sobre o esquema e tamanho dos dados** em vez dos dados completos.
Use isto para evitar respostas grandes demais e inspecionar a estrutura antes de consultas direcionadas.

Use `--jq '.'` para obter todos os dados, ou use um filtro mais específico para resultados direcionados.

## Uso

Use esta habilidade para consultar pull requests do repositório atual ou de qualquer repositório especificado.

### Consulta Básica (Retorna Apenas Esquema)

Para listar pull requests do repositório atual:

```bash
./query-prs.sh
# Retorna informações de esquema e tamanho dos dados, não os dados completos
```

### Obter Todos os Dados

Para obter todos os dados de PR:

```bash
./query-prs.sh --jq '.'
```

### Com Repositório

Para consultar um repositório específico:

```bash
./query-prs.sh --repo owner/repo
```

### Com Filtragem jq

Use o argumento `--jq` para filtrar e transformar a saída:

```bash
# Obter apenas PRs abertos
./query-prs.sh --jq '.[] | select(.state == "open")'

# Obter números e títulos de PR
./query-prs.sh --jq '.[] | {number, title}'

# Obter PRs por um autor específico
./query-prs.sh --jq '.[] | select(.author.login == "username")'

# Obter PRs mesclados da semana passada
./query-prs.sh --jq '.[] | select(.mergedAt != null)'

# Contar PRs por estado
./query-prs.sh --jq 'group_by(.state) | map({state: .[0].state, count: length})'
```

### Opções Comuns

- `--state`: Filtrar por estado (open, closed, merged, all). Padrão: open
- `--limit`: Número máximo de PRs a buscar. Padrão: 30
- `--repo`: Repositório no formato owner/repo. Padrão: repositório atual
- `--jq`: (Opcional) expressão jq para filtragem/transformação da saída. Se omitido, retorna informações de esquema

### Exemplos de Consultas

**Encontrar PRs grandes (muitos arquivos alterados):**

```bash
./query-prs.sh --jq '.[] | select(.changedFiles > 10) | {number, title, changedFiles}'
```

**Obter PRs aguardando revisão:**

```bash
./query-prs.sh --jq '.[] | select(.reviewDecision == "REVIEW_REQUIRED") | {number, title, author: .author.login}'
```

**Listar PRs com suas etiquetas (labels):**
```bash
./query-prs.sh --jq '.[] | {number, title, labels: [.labels[].name]}'
```

## Formato de Saída

O script gera JSON por padrão, facilitando o pipe através do jq para processamento adicional.

## Requisitos

- CLI do GitHub (`gh`) autenticada
- `jq` para filtragem (instalado por padrão na maioria dos sistemas)
---
