---
"gh-aw": patch
---

Adicionar script de configuração da CLI do gh para suporte ao GitHub Enterprise. Os fluxos de trabalho agora podem chamar `configure_gh_for_ghe.sh` antes de executar comandos `gh` para detectar e configurar automaticamente o host correto do GitHub Enterprise a partir de variáveis de ambiente (`GITHUB_SERVER_URL`, `GITHUB_ENTERPRISE_HOST`, `GITHUB_HOST` ou `GH_HOST`). Isso corrige o erro “nenhum dos remotos git configurados para este repositório aponta para um host GitHub conhecido” ao executar fluxos de trabalho como o repo-assist em domínios GHE.
