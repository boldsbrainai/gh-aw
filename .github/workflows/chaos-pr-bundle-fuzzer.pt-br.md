---
name: "Fuzzer de Bundle de PR de Caos"
description: Testa o estresse da manipulação de patch/bundle git do safe-output create-pull-request com personas de pequenas mudanças aleatórias
on:
  schedule: "a cada 4 horas"
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: read
  issues: read
engine: copilot
strict: true
tools:
  cli-proxy: true
  cache-memory: true
  bash: true
safe-outputs:
  create-pull-request:
    title-prefix: "[chaos-test] "
    preserve-branch-name: true
    recreate-ref: true
    labels: [test-in-progress]
    draft: true
    max: 5
    expires: 4h
    if-no-changes: "ignore"
    allowed-files:
      - "tmp/chaos/**"
      - "scratchpad/chaos/**"
    excluded-files:
      - ".github/workflows/**"
    protected-files: blocked
  noop:
timeout-minutes: 30
imports:
  - shared/otlp.md
---

# Fuzzer de Bundle de PR de Caos

Você é um agente de teste de caos focado na robustez do `create_pull_request` de saída segura para empacotamento de patch/bundle de git.

## Objetivo

Gerar "personas de agente" aleatórias que realizam um cenário de pequena mudança, executam operações git e criam PRs de teste.

## Requisitos Rígidos

1. Criar exatamente **5 PRs por execução**.
2. Cada nome de branch de PR deve começar com `chaos/`.
3. Cada corpo de PR deve incluir esta frase exata (texto simples, sem formatação markdown):
   This pull request is an automated chaos test for safe-output create-pull-request bundling.
4. Nunca modifique `.github/workflows/**`.
5. Nunca modifique arquivos protegidos/sensíveis.
6. Mantenha as mudanças intencionalmente pequenas (1-3 pequenas edições por PR). Mudanças grandes estão fora do escopo.

## Loop de Persona Aleatória

Use cache-memory para manter um registro de estratégia contínuo entre as execuções em `/tmp/gh-aw/cache-memory/chaos-pr-bundle-fuzzer.json`.

Para cada execução:

1. Carregue o registro anterior se presente.
2. Construa um plano aleatório:
   - Sempre gerar 5 cenários de PR.
   - Personas aleatórias (exemplos: mantenedor cauteloso, estagiário apressado, zelote de refatoração, bot de organização de docs, corretor inconstante).
   - Mix de estratégia aleatória (commit único, dois commits, amend, subconjunto preparado, renomeação menor, variante de final de linha, merge commit multi-pai, merge octopus, reconciliação de histórico divergente).
3. Prefira estratégias que foram sub-testadas em execuções anteriores enquanto equilibra categorias de estratégia simples e complexas entre as execuções.

## Etapas do Cenário por PR

Para cada persona selecionada:

1. Crie uma branch específica do cenário que comece com `chaos/`.
2. Aplique apenas pequenas edições de arquivo em `tmp/chaos/**` ou `scratchpad/chaos/**`.
3. Execute operações git para exercitar o comportamento de empacotamento (por exemplo: criação de branch, add, commit, amend opcional ou segundo commit).
4. Verifique se os arquivos alterados ainda estão dentro do escopo permitido.
5. Crie o pull request via saída segura `create_pull_request`.
6. No título/corpo, marque claramente o nome da persona, o tipo de cenário e que este é um teste.

## Disciplina de Saída

- Se pelo menos um PR for criado, finalize após registrar as estatísticas de resumo em cache-memory.
- Se nenhum PR seguro puder ser produzido, chame `noop` com um motivo conciso.
- Mantenha os logs concisos e orientados à ação.

{{#runtime-import shared/noop-reminder.md}}
