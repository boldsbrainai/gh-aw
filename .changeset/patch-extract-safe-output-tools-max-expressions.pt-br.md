---
"gh-aw": patch
---

Extrair expressões `${{ }}` dos valores `max:` no bloco de prompt `<safe-output-tools>` para variáveis de ambiente `GH_AW_*` (seguindo os padrões de extração de prompt existentes). Isso evita que `${{ }}` apareça inline no heredoc `run:`, que estava sujeito ao limite de tamanho de expressão de 21 KB do GitHub Actions e causava falhas de compilação em fluxos de trabalho com prompts grandes que usavam `${{ inputs.* }}` nos valores de configuração `max:` de saída segura.
