---
"gh-aw": patch
---

Corrigido o comando `create-pull-request` com `target-repo`: a etapa de checkout `safe_outputs` agora usa uma expressão de referência segura entre repositórios (omitindo `github.ref_name`) para evitar falhas quando o branch de origem não existe no repositório de destino.
