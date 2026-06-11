---
"gh-aw": patch
---

Adicionar suporte a `blocked-users` e `approval-labels` às políticas de guarda do `tools.github`, incluindo atualizações no esquema, no analisador e na validação, além da análise em tempo de execução por meio do `parse_guard_list.sh` — que mescla valores estáticos em tempo de compilação com as variáveis de organização/repositório `GH_AW_GITHUB_BLOCKED_USERS` e `GH_AW_GITHUB_APPROVAL_LABELS` em matrizes JSON adequadas (separadas por vírgula/nova linha, validadas e codificadas com jq).
