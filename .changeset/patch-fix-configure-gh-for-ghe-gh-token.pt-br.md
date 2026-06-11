---
"gh-aw": patch
---

Correção de uma falha no `configure_gh_for_ghe.sh` quando `GH_TOKEN` está definido. Anteriormente, o script sempre executava `gh auth login --with-token`, o que a CLI do `gh` rejeita quando `GH_TOKEN` já está no ambiente. Agora, quando `GH_TOKEN` está presente, o script ignora `gh auth login` e exporta apenas `GH_HOST` para `GITHUB_ENV` — o token já lida com a autenticação e `GH_HOST` é tudo o que é necessário para direcionar o `gh` para o host correto do GitHub Enterprise.
