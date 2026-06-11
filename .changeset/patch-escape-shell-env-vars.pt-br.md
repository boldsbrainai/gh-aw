---
"gh-aw": patch
---

Cite as variáveis de ambiente com `${VAR@Q}` nos scripts de shell localizados em `actions/setup/sh/`, para que as instruções `echo` não possam ser exploradas por caracteres especiais ou vetores de injeção.
