---
"gh-aw": patch
---

Fazer com que a saída segura do comando `add-comment` acrescente o marcador `gh-aw-workflow-call-id` quando o ID do fluxo de trabalho de origem for fornecido, para que os fluxos de trabalho reutilizáveis possam ser distinguidos na lógica de pesquisa do comando `close-older-comments`.
