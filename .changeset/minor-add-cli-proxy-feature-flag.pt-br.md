---
"gh-aw": menor
---

Adicionar o sinalizador de recurso `cli-proxy`, que insere `--difc-proxy-host` e `--difc-proxy-ca-cert` no comando AWF, iniciando o `difc-proxy` no host antes do AWF e fornecendo aos agentes acesso seguro e somente leitura à CLI do `gh` sem expor o `GITHUB_TOKEN` (requer firewall v0.26.0+).
