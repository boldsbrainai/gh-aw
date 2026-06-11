---
"gh-aw": patch
---

Correção do `gh aw add`, que resolvia incorretamente a importação `{{#import shared/X.md}}` no corpo do arquivo a partir da raiz do repositório, em vez do diretório do arquivo de fluxo de trabalho (`.github/workflows/`). Além disso, agora as importações no corpo do arquivo são preservadas como referências locais quando o arquivo de destino já existe no repositório de destino, de acordo com o comportamento já implementado para o `gh aw update`.
