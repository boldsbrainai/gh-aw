---
title: ChatOps
description: Automação interativa disparada por comandos (slash commands como /review, /deploy) em issues e PRs - fluxos de trabalho com intervenção humana
sidebar:
  badge: { text: 'Disparado por comando', variant: 'note' }
---

ChatOps traz automação para as conversas do GitHub através de gatilhos de comando que respondem a slash commands em issues, pull requests e comentários. Membros da equipe podem disparar fluxos de trabalho digitando comandos como `/review` ou `/deploy` diretamente nas discussões.

## Quando usar ChatOps

- **Revisões de código interativas** - `/review` para analisar alterações de PR sob demanda
- **Implantações sob demanda** - `/deploy staging` quando você estiver pronto
- **Análise assistida** - `/analyze` para investigações específicas
- **Colaboração em equipe** - Comandos compartilhados que todos podem usar

```aw wrap
---
on:
  slash_command:
    name: review
    events: [pull_request_comment]  # Responda apenas a /review em comentários de PR
permissions:
  contents: read
  pull-requests: read
safe-outputs:
  create-pull-request-review-comment:
    max: 5
  add-comment:
---

# Assistente de Revisão de Código

Quando alguém digitar /review em um comentário de pull request, realize uma análise detalhada das alterações.

Examine o diff em busca de possíveis bugs, vulnerabilidades de segurança, implicações de desempenho, problemas de estilo de código e testes ou documentação ausentes.

Crie comentários de revisão específicos nas linhas relevantes de código e adicione um comentário de resumo com observações e recomendações gerais.
```

Quando alguém digita `/review`, a IA analisa as alterações de código e posta comentários de revisão. O agente é executado com permissões somente leitura enquanto [safe-outputs](/gh-aw/reference/safe-outputs/) (operações validadas do GitHub) lidam com as operações de escrita com segurança.

## Filtrando Eventos de Comando

Gatilhos de comando respondem a todos os contextos de comentário por padrão. Use o campo `events:` para restringir onde os comandos são ativados:

```aw wrap
---
on:
  slash_command:
    name: triage
    events: [issues, issue_comment]  # Apenas em corpos de issue e comentários de issue
---

# Bot de Triagem de Issues

Este comando só responde quando mencionado em issues, não em pull requests.
```

**Identificadores de evento suportados:**

- `issues` - Corpos de issue (abertas, editadas, reabertas)
- `issue_comment` - Comentários apenas em issues (exclui comentários de PR)
- `pull_request_comment` - Comentários apenas em pull requests (exclui comentários de issue)
- `pull_request` - Corpos de pull request (abertos, editados, reabertos)
- `pull_request_review_comment` - Comentários de revisão de pull request
- `*` - Todos os eventos relacionados a comentários (padrão quando `events:` é omitido)

**Nota**: Tanto `issue_comment` quanto `pull_request_comment` mapeiam para o evento `issue_comment` do GitHub Actions, mas com filtragem automática para distinguir entre comentários de issue e comentários de PR. Isso fornece controle preciso sobre onde seus comandos estão ativos.

## Segurança e Controle de Acesso

Fluxos de trabalho de ChatOps restringem a execução a usuários com permissões de administrador, mantenedor ou escrita por padrão. As verificações de permissão ocorrem em tempo de execução, cancelando fluxos de trabalho para usuários não autorizados.

Personalize o acesso com a configuração `roles:`. Use `roles: [admin, maintainer]` para um controle mais rígido. Evite `roles: all` em repositórios públicos, pois qualquer usuário autenticado poderia disparar fluxos de trabalho.

## Acessando Informações de Contexto

Acesse o contexto de evento higienizado através de `steps.sanitized.outputs.text`:

```aw wrap
# Referencie o texto higienizado no seu fluxo de trabalho:
Analise este conteúdo: "${{ steps.sanitized.outputs.text }}"
```

A sanitização filtra menções não autorizadas, links maliciosos e conteúdo excessivo, preservando informações essenciais.

**Segurança**: Trate o conteúdo fornecido pelo usuário como não confiável. Projete fluxos de trabalho para resistir a tentativas de injeção de prompt em descrições de issue, comentários ou conteúdo de pull request.

## Exemplos de Fluxos de Trabalho

Exemplos de fluxos de trabalho de ChatOps demonstram padrões de automação disparados por comando:

- **[Revisor de Código Rabugento (Grumpy Code Reviewer)](https://github.com/github/gh-aw/blob/main/.github/workflows/grumpy-reviewer.md)** - Disparado por `/grumpy` em comentários de PR, revisa alterações de código com a personalidade de um desenvolvedor sênior rabugento, identificando problemas de qualidade de código e postando comentários de revisão específicos. Usa memória de cache para rastrear revisões anteriores e evitar feedback duplicado.
