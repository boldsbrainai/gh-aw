---
title: Dependências APM
description: Instale e gerencie pacotes APM (Agent Package Manager) em seus fluxos de trabalho agentic, incluindo skills, prompts, instruções, agentes, hooks e plugins.
sidebar:
  order: 330
---

O [APM (Agent Package Manager)](https://microsoft.github.io/apm/) gerencia primitivos de agente de IA, como skills, prompts, instruções, agentes, hooks e plugins (incluindo a especificação `plugin.json` do Claude). Pacotes podem depender de outros pacotes e o APM resolve toda a árvore de dependências.

O APM é configurado importando o fluxo de trabalho `shared/apm.md`, que cria um job `apm` dedicado que empacota pacotes e envia o pacote como um artefato do GitHub Actions. O job do agente então baixa e descompacta o pacote para inicialização determinística.

## De onde vem `shared/apm.md`

`shared/apm.md` é um **arquivo de fluxo de trabalho local** que o gh-aw resolve em `.github/workflows/shared/apm.md` em seu repositório — não é uma importação remota (a sintaxe `uses:` dentro de `imports:` é a forma de importação local do gh-aw, não a `uses: proprietário/repo@ref` do GitHub Actions).

A fonte canônica é mantida em [microsoft/apm](https://github.com/microsoft/apm/blob/main/.github/workflows/shared/apm.md). Adicione-o ao seu repositório com:

```bash
gh aw add microsoft/apm/.github/workflows/shared/apm.md --dir shared
```

Executar `gh aw update` manterá sua cópia vendored sincronizada com a fonte canônica. O arquivo `shared/apm.md` declara um `redirect` para a biblioteca `microsoft/apm`, então qualquer cópia originada do gh-aw seguirá automaticamente o redirecionamento e reescreverá seu campo `source` para rastrear a localização canônica na próxima execução de `gh aw update`.

A versão canônica fixa `microsoft/apm-action@v1.5.0` e suporta autenticação GitHub App multi-org (`apps:[]`) e restauração multi-bundle.

## Uso

Importe `shared/apm.md` e forneça a lista de pacotes através do parâmetro `packages`:

```aw wrap
imports:
  - uses: shared/apm.md
    with:
      packages:
        - microsoft/apm-sample-package
        - github/awesome-copilot/skills/review-and-refactor
        - anthropics/skills/skills/frontend-design
```

## Reprodutibilidade e governança

Arquivos de lock do APM (`apm.lock`) fixam cada pacote a um SHA de commit exato, para que as mesmas versões sejam instaladas em cada execução. Diffs de arquivo de lock aparecem em pull requests e são revisáveis antes da mesclagem, dando a equipes e empresas um rastro de auditoria claro e a capacidade de governar qual contexto de agente está em uso. Veja o [guia de governança do APM](https://microsoft.github.io/apm/enterprise/governance/) para detalhes sobre aplicação de políticas e controles de acesso.

## Formatos de referência de pacote

Cada entrada em `packages` é uma referência de pacote APM. Formatos suportados:

| Formato | Descrição |
|--------|-------------|
| `proprietário/repo` | Pacote APM completo |
| `proprietário/repo/caminho/para/primitivo` | Primitivo individual (skill, instrução, plugin, etc.) de um repositório |
| `proprietário/repo#ref` | Pacote fixado em uma tag, branch ou SHA de commit |

### Exemplos

```aw wrap
imports:
  - uses: shared/apm.md
    with:
      packages:
        # Pacote APM completo
        - microsoft/apm-sample-package
        # Primitivo individual de qualquer repositório
        - github/awesome-copilot/skills/review-and-refactor
        # Plugin (formato plugin.json do Claude)
        - github/awesome-copilot/plugins/context-engineering
        # Fixado em uma tag
        - microsoft/apm-sample-package#v2.0
        # Fixado em uma branch
        - microsoft/apm-sample-package#main
```

## Como funciona

A importação `shared/apm.md` adiciona um job `apm` dedicado ao fluxo de trabalho compilado. Este job executa `microsoft/apm-action` para instalar pacotes e criar um arquivo de pacote, que é enviado como um artefato do GitHub Actions. O job do agente baixa e restaura o pacote como pré-etapas, tornando todas as skills e ferramentas disponíveis em tempo de execução.

Os pacotes são buscados usando o fallback em cascata de token: `GH_AW_PLUGINS_TOKEN` → `GH_AW_GITHUB_TOKEN` → `GITHUB_TOKEN`.

Para reproduzir ou depurar o fluxo de empacotamento/desempacotamento localmente, execute `apm pack` e `apm unpack` diretamente. Veja o [guia de empacotar e distribuir](https://microsoft.github.io/apm/guides/pack-distribute/) para instruções.

## Referência

| Recurso | URL |
|----------|-----|
| Documentação do APM | https://microsoft.github.io/apm/ |
| Guia de governança do APM | https://microsoft.github.io/apm/enterprise/governance/ |
| Guia de empacotar e distribuir | https://microsoft.github.io/apm/guides/pack-distribute/ |
| Integração gh-aw (docs APM) | https://microsoft.github.io/apm/integrations/gh-aw/ |
| apm-action (GitHub) | https://github.com/microsoft/apm-action |
| microsoft/apm (GitHub) | https://github.com/microsoft/apm |
| shared/apm.md (canônico) | https://github.com/microsoft/apm/blob/main/.github/workflows/shared/apm.md |
