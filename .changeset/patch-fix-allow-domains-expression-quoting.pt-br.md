---
"gh-aw": patch
---

Corrigir o escapamento de argumentos do shell para `--allow-domains`/`--block-domains` quando os valores contêm expressões `${{ }}` do GitHub Actions, utilizando aspas duplas para que as expressões com strings entre aspas simples permaneçam válidas.
