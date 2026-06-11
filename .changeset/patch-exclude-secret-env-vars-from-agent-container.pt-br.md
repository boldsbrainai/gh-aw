---
"gh-aw": patch
---

Segurança: exclua `COPILOT_GITHUB_TOKEN` e `GITHUB_MCP_SERVER_TOKEN` do ambiente visível do contêiner do agente usando o novo sinalizador `--exclude-env` do AWF (requer AWF v0.26.0 ou superior). Isso impede que um agente injetado por prompt exfiltre esses tokens por meio de ferramentas bash, como `env` ou `printenv`. O proxy de API do AWF lida com a autenticação desses tokens de forma transparente. Atualiza a versão padrão do firewall para v0.26.0.
