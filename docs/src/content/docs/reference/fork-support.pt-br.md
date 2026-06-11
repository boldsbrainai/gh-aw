---
title: Suporte a Fork
description: Como o GitHub Agentic Workflows se comporta em repositórios forkados e como permitir PRs de forks confiáveis.
sidebar:
  order: 7
---

O GitHub Agentic Workflows tem dois cenários de fork distintos com comportamentos diferentes: **pull requests de entrada de forks** e **execução de fluxos de trabalho dentro de um repositório forkado**.

## Execução de fluxos de trabalho em um fork

Fluxos de trabalho agentic **não** são executados em repositórios forkados. Quando um fluxo de trabalho é executado em um fork, todos os jobs são ignorados (skip) automaticamente usando a condição `if: ${{ !github.event.repository.fork }}` injetada no momento da compilação.

Isso significa:

- Jobs de agente são ignorados — nenhuma execução de IA ocorre
- Jobs de manutenção e auto-atualização não são executados
- Nenhum segredo do repositório upstream está disponível

Isso é intencional. Forks carecem dos segredos e do contexto necessários para que os fluxos de trabalho agentic funcionem corretamente, e não há maneira segura de executar agentes com configuração parcial.

> [!NOTE]
> Para executar fluxos de trabalho agentic em seu próprio repositório, faça o fork do repositório upstream e configure seus próprios segredos — os fluxos de trabalho serão então executados em sua cópia do repositório, que não é um fork da perspectiva do GitHub Actions.

## Pull requests de entrada de forks

Quando um pull request é aberto de um fork para seu repositório, o comportamento padrão é **bloquear a execução do fluxo de trabalho** — o trigger `pull_request` inclui uma verificação de ID de repositório que verifica se o branch head do PR vem do mesmo repositório.

Para permitir que fluxos de trabalho sejam executados para PRs de repositórios fork confiáveis, use o campo `forks:`:

```aw wrap
---
on:
  pull_request:
    types: [opened, synchronize]
    forks: ["trusted-org/*"]
---
```

### Padrões de Fork

O campo `forks:` aceita uma string ou uma lista de padrões de repositório:

| Padrão | Corresponde a |
|---|---|
| `"*"` | Todos os forks (use com cautela) |
| `"owner/*"` | Todos os forks de um usuário ou organização específica |
| `"owner/repo"` | Um repositório fork específico |

```aw wrap
---
on:
  pull_request:
    types: [opened, synchronize]
    forks:
      - "trusted-org/*"
      - "partner/specific-fork"
---
```

> [!WARNING]
> Permitir todos os forks (`"*"`) significa que qualquer usuário que fizer um fork do seu repositório poderá acionar a execução do agente. Fluxos de trabalho acionados de PRs de fork são executados com as permissões configuradas no fluxo de trabalho — revise essas permissões cuidadosamente antes de permitir forks não confiáveis.
