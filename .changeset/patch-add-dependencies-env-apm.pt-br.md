---
"gh-aw": patch
---

Adicionado suporte ao `dependencies.env` para dependências do APM, de modo que os fluxos de trabalho possam passar variáveis de ambiente para a etapa do pacote `microsoft/apm-action` (por exemplo, autenticação em registro privado), mantendo a ordem determinística das variáveis de ambiente nas etapas geradas do fluxo de trabalho e ignorando entradas duplicadas de `GITHUB_TOKEN` quando o `github-app` estiver configurado.

Atualizadas as versões padrão do APM para `microsoft/apm@v0.8.2` e `microsoft/apm-action@v1.3.4`.
