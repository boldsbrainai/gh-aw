---
"gh-aw": patch
---

Corrigimos o comportamento da atribuição do Copilot para `create-issue` e `create-pull-request`, tornando o gerenciamento do estado da atribuição seguro contra concorrência e atribuindo o Copilot diretamente durante os fluxos de criação de issues. Também atualizamos a ligação entre o ambiente e o token no safe-outputs do compilador para que a atribuição do Copilot receba o token necessário quando configurada.
