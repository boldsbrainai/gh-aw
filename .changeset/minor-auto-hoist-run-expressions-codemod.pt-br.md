---
"gh-aw": menor
---

Ampliar o codemod `steps-run-secrets-to-env` para elevar **todas** as expressões `${{ ... }}` dos blocos `run:` — não apenas segredos, `env.*` e `github.token`. Expressões arbitrárias como `github.repository`, `github.event.issue.title`, `inputs.*` e `steps.*.outputs.*` agora recebem ligações `env:` no nível da etapa `EXPR_*`. As etapas do PowerShell (`shell: pwsh` / `shell: powershell`) recebem a sintaxe `$env:VARNAME`. Isso elimina a necessidade do codemod `auto-hoist-run-expressions`, que antes era necessário.
