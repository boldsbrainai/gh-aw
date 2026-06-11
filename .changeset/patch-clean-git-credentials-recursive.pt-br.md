---
"gh-aw": patch
---

Garantir que o `clean_git_credentials.sh` identifique recursivamente todos os arquivos `.git/config` presentes na área de trabalho e no diretório `/tmp/`, elimine duplicatas da lista e reutilize um auxiliar ao limpar cada arquivo.
