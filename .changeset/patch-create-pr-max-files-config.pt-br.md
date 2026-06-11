---
"gh-aw": patch
---
Corrigir o limite de 100 arquivos do `create_pull_request` para que conte arquivos únicos (e não cabeçalhos `diff --git` brutos, que inflacionam a contagem quando um único push contém vários commits que afetam os mesmos arquivos) e adicionar uma opção configurável de saída segura de nível superior `max-patch-files` (padrão 100) para que ramos de longa duração possam optar por um limite mais alto.
