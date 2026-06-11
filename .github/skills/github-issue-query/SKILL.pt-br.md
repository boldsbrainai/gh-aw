---
name: github-issue-query
description: Consulte issues do GitHub com filtragem jq e seletores reutilizáveis.
---

# Habilidade de Consulta de Issue do GitHub

Consulte issues do GitHub de forma eficiente com filtragem jq integrada.

## Importante: O Parâmetro jq é Opcional

O parâmetro `--jq` é **opcional**. Sem `--jq`, esta habilidade retorna **informações sobre o esquema e tamanho dos dados** em vez dos dados completos.
Use isto para evitar respostas grandes demais e inspecionar a estrutura antes de consultas direcionadas.

Use `--jq '.'` para obter todos os dados, ou use um filtro mais específico para resultados direcionados.

## Uso

Use esta habilidade para consultar issues do repositório atual ou de qualquer repositório especificado.

### Consulta Básica (Retorna Apenas Esquema)

Para listar issues do repositório atual:

```bash
./query-issues.sh
# Retorna informações de esquema e tamanho dos dados, não os dados completos
```

### Obter Todos os Dados

Para obter todos os dados de issue:

```bash
./query-issues.sh --jq '.'
```

### Com Repositório

Para consultar um repositório específico:

```bash
./query-issues.sh --repo owner/repo
```

### Com Filtragem jq

Use o argumento `--jq` para filtrar e transformar a saída:

```bash
# Obter apenas issues abertas
./query-issues.sh --jq '.[] | select(.state == "OPEN")'

# Obter números e títulos de issue
./query-issues.sh --jq '.[] | {number, title}'

# Obter issues por um autor específico
./query-issues.sh --jq '.[] | select(.author.login == "username")'

# Obter issues com etiqueta específica
./query-issues.sh --jq '.[] | select(.labels | map(.name) | index("bug"))'

# Contar issues por estado
./query-issues.sh --jq 'group_by(.state) | map({state: .[0].state, count: length})'
```

### Opções Comuns

- `--state`: Filtrar por estado (open, closed, all). Padrão: open
- `--limit`: Número máximo de issues a buscar. Padrão: 30
- `--repo`: Repositório no formato owner/repo. Padrão: repositório atual
- `--jq`: (Opcional) expressão jq para filtragem/transformação da saída. Se omitido, retorna informações de esquema

### Exemplos de Consultas

**Encontrar issues com muitos comentários:**
```bash
./query-issues.sh --jq '.[] | select(.comments.totalCount > 5) | {number, title, comments: .comments.totalCount}'
```

**Obter issues atribuídas a alguém:**
```bash
./query-issues.sh --jq '.[] | select(.assignees | length > 0) | {number, title, assignees: [.assignees[].login]}'
```

**Listar issues com suas etiquetas (labels):**
```bash
./query-issues.sh --jq '.[] | {number, title, labels: [.labels[].name]}'
```

**Obter atribuições de board de projeto:**
```bash
./query-issues.sh --jq '.[] | {number, title, projects: [.projectItems.nodes[]? | .project?.url]}'
```

**Encontrar issues antigas (criadas há mais de 30 dias):**
```bash
./query-issues.sh --jq '.[] | select(.createdAt < (now - 2592000 | strftime("%Y-%m-%dT%H:%M:%SZ")))'
```

## Formato de Saída

O script gera JSON por padrão, facilitando o pipe através do jq para processamento adicional.

## Requisitos

- CLI do GitHub (`gh`) autenticada
- `jq` para filtragem (instalado por padrão na maioria dos sistemas)
---
