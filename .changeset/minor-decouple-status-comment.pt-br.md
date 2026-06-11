---
"gh-aw": major
---

Desvinculamos o comentário de status do emoji comum de reação de IA, de modo que cada um deles deve ser ativado explicitamente (por exemplo, adicione `status-comment: true` se você ainda precisar do comentário de "iniciado/concluído"). Isso corrige o problema github/gh-aw#15831.

**⚠️ Mudança significativa**: O comentário de status (notificação de iniciado/concluído) não está mais habilitado por padrão. Anteriormente, ele era habilitado implicitamente junto com o emoji de reação de IA; agora, ambos devem ser habilitados explicitamente.

**Guia de migração:**
- Se seus fluxos de trabalho dependem do comentário de status automático, adicione `status-comment: true` explicitamente ao frontmatter do seu fluxo de trabalho
- Exemplo:
  ```yaml
  # Antes (o comentário de status era implícito)
  # (nenhuma configuração necessária)

  # Depois (deve ser explícito)
  status-comment: true
  ```
- Fluxos de trabalho que não dependiam de comentários de status não requerem alterações
