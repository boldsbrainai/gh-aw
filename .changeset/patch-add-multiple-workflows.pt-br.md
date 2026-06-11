---
"gh-aw": patch
---

Correção da opção `--name` para que ela se aplique apenas ao primeiro fluxo de trabalho ao adicionar vários fluxos de trabalho com `gh aw add workflow1 workflow2 ...`. Anteriormente, o nome era aplicado a todos os fluxos de trabalho, fazendo com que cada um sobrescrevesse o anterior.
