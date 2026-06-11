---
"gh-aw": patch
---

Atualizar a versão padrão do firewall para v0.25.43. Esta versão adiciona suporte a ARC/DinD (`dockerHostPathPrefix`), um limite máximo fixo para `apiProxy.maxRuns`, troca de credenciais em nuvem baseada em OIDC (`apiProxy.auth`), `hidepid=2` na montagem do procfs do host e várias correções de bugs, incluindo o alinhamento da API de comunicação GPT-5 BYOK e patches de alta gravidade para babel/fast-uri.
