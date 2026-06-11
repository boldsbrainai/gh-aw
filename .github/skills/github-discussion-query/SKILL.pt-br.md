---
name: github-discussion-query
description: Consulte discussões do GitHub com filtragem jq e seletores reutilizáveis.
---

# Habilidade de Consulta de Discussão do GitHub

Consulte discussões do GitHub de forma eficiente com filtragem jq integrada.

## Importante: O Parâmetro jq é Opcional

O parâmetro `--jq` é **opcional**. Sem `--jq`, esta habilidade retorna **informações sobre o esquema e tamanho dos dados** em vez dos dados completos.
Use isto para evitar respostas grandes demais e inspecionar a estrutura antes de consultas direcionadas.

Use `--jq '.'` para obter todos os dados, ou use um filtro mais específico para resultados direcionados.

## Uso

Use esta habilidade para consultar discussões do repositório atual ou de qualquer repositório especificado.

### Consulta Básica (Retorna Apenas Esquema)

Para listar discussões do repositório atual:

```bash
./query-discussions.sh
# Retorna informações de esquema e tamanho dos dados, não os dados completos
```

### Obter Todos os Dados

Para obter todos os dados de discussão:

```bash
./query-discussions.sh --jq '.'
```

### Com Repositório

Para consultar um repositório específico:

```bash
./query-discussions.sh --repo owner/repo
```

### Com Filtragem jq

Use o argumento `--jq` para filtrar e transformar a saída:

```bash
# Obter números e títulos de discussão
./query-discussions.sh --jq '.[] | {number, title}'

# Obter discussões por um autor específico
./query-discussions.sh --jq '.[] | select(.author.login == "username")'

# Obter discussões em uma categoria específica
./query-discussions.sh --jq '.[] | select(.category.name == "Ideas")'

# Obter discussões respondidas
./query-discussions.sh --jq '.[] | select(.answer != null)'

# Contar discussões por categoria
./query-discussions.sh --jq 'group_by(.category.name) | map({category: .[0].category.name, count: length})'
```

### Opções Comuns

- `--limit`: Número máximo de discussões a buscar. Padrão: 30
- `--repo`: Repositório no formato owner/repo. Padrão: repositório atual
- `--jq`: (Opcional) expressão jq para filtragem/transformação da saída. Se omitido, retorna informações de esquema

### Exemplos de Consultas

**Encontrar discussões com muitos comentários:**
```bash
./query-discussions.sh --jq '.[] | select(.comments.totalCount > 5) | {number, title, comments: .comments.totalCount}'
```

**Obter discussões não respondidas:**
```bash
./query-discussions.sh --jq '.[] | select(.answer == null) | {number, title, category: .category.name}'
```

**Listar discussões com suas etiquetas (labels):**
```bash
./query-discussions.sh --jq '.[] | {number, title, labels: [.labels[].name]}'
```

**Encontrar discussões por categoria:**
```bash
./query-discussions.sh --jq '.[] | select(.category.name == "Q&A") | {number, title, author: .author.login}'
```

**Obter discussões atualizadas recentemente:**
```bash
./query-discussions.sh --jq 'sort_by(.updatedAt) | reverse | .[0:10] | .[] | {number, title, updatedAt}'
```

## Formato de Saída

O script gera JSON por padrão, facilitando o pipe através do jq para processamento adicional.

## Requisitos

- CLI do GitHub (`gh`) autenticada
- `jq` para filtragem (instalado por padrão na maioria dos sistemas)
---
