---
name: go-linters
description: Adicione e valide linters de análise Go personalizados no gh-aw.
---

# Linters Go

Use este guia ao adicionar um novo linter de análise Go personalizado neste repositório.

Para geração de linter orientada a PR (derivar uma regra de um padrão específico de pull request), use `.github/skills/pr-to-go-linter/SKILL.md`.

## Onde adicionar um novo linter

1. Crie um novo pacote em `pkg/linters/<linter-name>/`.
2. Defina um analisador nesse pacote (exportado como `Analyzer`).
3. Adicione testes no mesmo pacote usando `analysistest` com fixtures em `testdata/src/...`.
4. Registre o analisador em `cmd/linters/main.go` para que ele seja executado através do binário multichecker.

## Build e teste de linters

- Teste apenas seu pacote de linter:
  - `go test ./pkg/linters/<linter-name>/...`
- Compile o executor de linter personalizado:
  - `go build ./cmd/linters`
- Execute todos os linters personalizados em todo o repositório:
  - `make golint-custom`

`make golint-custom` compila `cmd/linters` e executa-o contra `./cmd/...` e `./pkg/...`.
---
