---
"gh-aw": patch
---

`push_to_pull_request_branch`: quando `patch-format` não estiver explicitamente configurado e o intervalo incremental (`origin/<branch>..<branch>`) contiver um commit de mesclagem, use automaticamente o transporte `bundle` em vez do transporte padrão `am`. O `git am` não consegue aplicar commits de mesclagem; portanto, sem esse recurso de fallback, ramos de PR de longa duração que mesclam periodicamente seu ramo base localmente falhariam com conflitos de adição/adição a cada tentativa de push. Defina `patch-format: am` explicitamente para desativar o fallback automático. O transporte bundle agora também registra o `diff_size` incremental líquido, de modo que `max-patch-size` é validado em relação ao tamanho real da alteração, em vez do tamanho do artefato bundle (que costuma ser muito maior).
