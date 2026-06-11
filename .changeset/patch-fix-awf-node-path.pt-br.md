---
"gh-aw": patch
---

Corrigimos a execução do AWF Copilot para que utilize um caminho absoluto para o binário do Node.js, quando disponível, de modo que os fluxos de trabalho não falhem mais com a mensagem `node: comando não encontrado` em executores onde o `sudo` redefine o `PATH`.

Além disso, regeneramos os arquivos de bloqueio de fluxos de trabalho compilados e desatualizados após as refatorações de propagação de contexto.
