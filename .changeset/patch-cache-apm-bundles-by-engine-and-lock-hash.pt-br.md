---
"gh-aw": patch
---

Armazenar em cache os pacotes APM por `engine_id` e pelo hash do arquivo de bloqueio do fluxo de trabalho, para que as execuções possam reutilizar pacotes previamente compactados em diferentes execuções do fluxo de trabalho, mantendo o envio de um artefato para garantir uma restauração confiável da mesma execução.

Expor o `engine_id` nas saídas da tarefa de ativação para que os fluxos de trabalho compartilhados possam criar chaves de cache específicas do mecanismo ao preparar as dependências do agente.
