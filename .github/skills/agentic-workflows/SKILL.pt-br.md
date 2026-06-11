---
name: agentic-workflows
description: Roteie solicitações de criação/depuração/atualização de fluxo de trabalho gh-aw para os prompts corretos.
---

# Roteador de Fluxos de Trabalho Agentic

Use esta skill quando um usuário pedir para criar, atualizar, depurar ou atualizar GitHub Agentic Workflows.

Quando a tarefa envolver OTEL, OTLP, rastreamentos, backends de observabilidade ou análise orientada por telemetria, leia também `skills/otel-queries/SKILL.md` após carregar o prompt de fluxo de trabalho correspondente.

1. Leia `.github/agents/agentic-workflows.agent.md` (também referido como `.github/actions/agentic-workflows.agent.md` em notas anteriores).
2. Selecione e leia o prompt correspondente em `.github/aw/*.md`.
3. Se a tarefa for orientada por telemetria, leia também `skills/otel-queries/SKILL.md` e use seu loop de consulta fixo.
4. Siga o prompt carregado diretamente e mantenha as respostas concisas.
