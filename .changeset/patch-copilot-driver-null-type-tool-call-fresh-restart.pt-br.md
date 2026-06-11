---
"gh-aw": patch
---

Correção no copilot-driver: detecta o erro 400 de chamada de ferramenta com tipo nulo e reinicia do zero, em vez de tentar novamente com `--continue`. Uma chamada de ferramenta malformada com `type: null` corrompe o histórico de conversação; tentar novamente via `--continue` reintroduz o mesmo estado corrompido e falha da mesma forma em todas as tentativas. Esta alteração reinicia do zero para descartar o histórico corrompido e desativa permanentemente `--continue` pelo restante da execução, de modo que o estado corrompido nunca possa ser recarregado.
