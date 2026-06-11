---
"gh-aw": patch
---

Permite que saídas seguras de `add_comment` sejam publicadas mesmo quando uma operação de envio de código anterior (`create_pull_request` ou `push_to_pull_request_branch`) falha. O corpo do comentário é acompanhado de uma nota de aviso descrevendo a falha, para que os usuários vejam o resultado. Anteriormente, o comentário de status era cancelado silenciosamente quando a aplicação do patch falhava, não deixando nenhuma atualização na issue ou no PR.
