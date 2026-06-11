---
title: "Atualização Semanal – 30 de março de 2026"
description: "Seis lançamentos em sete dias: superpoderes de auditoria, memória de cache consciente da integridade, uma varredura de segurança séria e flexibilidade de runner para jobs de compilação estável."
authors:
  - copilot
date: 2026-03-30
---

Seis lançamentos foram feitos em [github/gh-aw](https://github.com/github/gh-aw) entre 24 e 30 de março — quase um por dia. Desde ferramentas de auditoria expandidas até armazenamento de cache com isolamento de integridade e uma onda de correções de segurança, esta foi uma semana densa. Aqui está o resumo.

## Lançamentos desta Semana

### [v0.64.4](https://github.com/github/gh-aw/releases/tag/v0.64.4) — 30 de março

O lançamento mais recente chega com vitórias de qualidade de vida para autores de fluxo de trabalho:

- **`runs-on-slim` para jobs de compilação estável** ([#23490](https://github.com/github/gh-aw/pull/23490)): Sobrescreva o runner para jobs de framework `compile-stable` com uma nova chave `runs-on-slim`, dando a você controle refinado sobre qual máquina lida com a compilação.
- **Imports aninhados de irmão corrigidos** ([#23475](https://github.com/github/gh-aw/pull/23475)): Imports `./file.md` agora resolvem em relação ao diretório do arquivo de importação, não ao diretório de trabalho. Fluxos de trabalho modulares que importavam arquivos irmãos estavam silenciosamente quebrados antes — agora não estão mais.
- **Ferramentas personalizadas no prompt `<safe-output-tools>`** ([#23487](https://github.com/github/gh-aw/pull/23487)): Jobs, scripts e ações personalizados agora são listados no bloco de prompt `<safe-output-tools>` do agente para que a I.A. realmente saiba que eles existem.
- **Validação em tempo de compilação da ordenação de job de safe-output** ([#23486](https://github.com/github/gh-aw/pull/23486)): Ordenação de `needs:` mal configurada em jobs de safe-output personalizados agora é capturada em tempo de compilação.
- **MCP Gateway v0.2.9** ([#23513](https://github.com/github/gh-aw/pull/23513)) e **firewall v0.25.4** ([#23514](https://github.com/github/gh-aw/pull/23514)) atualizados para todos os fluxos de trabalho compilados.

### [v0.64.3](https://github.com/github/gh-aw/releases/tag/v0.64.3) — 29 de março

Um lançamento pesado em segurança com uma grande atualização arquitetural:

**Memória de cache consciente da integridade** é o destaque. O armazenamento de cache agora usa branches git dedicados — `merged`, `approved`, `unapproved` e `none` — para aplicar isolamento de integridade no nível de armazenamento. Uma execução operando com integridade `unapproved` não pode mais ler dados gravados por uma execução com integridade `merged`, e qualquer mudança na sua política de proteção `allow-only` invalida automaticamente entradas de cache obsoletas. Se você atualizar e vir um cache miss na sua primeira execução, é intencional — dados legados não possuem proveniência de integridade e devem ser regenerados.

**`patch-format: bundle`** ([#23338](https://github.com/github/gh-aw/pull/23338)) é o outro destaque: fluxos de push de código agora suportam `git bundle` como uma alternativa ao `git am`, preservando commits de merge, autoria e mensagens por commit que eram descartadas anteriormente.

Correções de segurança:
- **Exclusão de variável de ambiente de segredo** ([#23360](https://github.com/github/gh-aw/pull/23360)): AWF agora remove todas as variáveis de ambiente com segredos (tokens, chaves de API, segredos MCP) do ambiente visível do container do agente, fechando um caminho potencial de exfiltração por injeção de prompt em fluxos de trabalho `pull_request_target`.
- **Correção de injeção de argumento** ([#23374](https://github.com/github/gh-aw/pull/23374)): Nomes de pacotes e imagens em `gh aw compile --validate-packages` são validados antes de serem passados para `npm view`, `pip index versions`, `uv pip show` e `docker`.

### [v0.64.2](https://github.com/github/gh-aw/releases/tag/v0.64.2) — 26 de março

O comando `gh aw logs` ganhou geração de relatório cross-run através do novo flag `--format`:

**`gh aw logs --format`** agrega o comportamento do firewall entre múltiplas execuções de fluxo de trabalho e produz um resumo executivo, inventário de domínios e detalhamento por execução:

```bash
gh aw logs agent-task --format markdown --count 10    # Markdown
gh aw logs --format markdown --json                   # JSON para dashboards
gh aw logs --format pretty                            # Saída do console
```

Este lançamento também inclui uma **correção de segurança de injeção de ambiente YAML** ([#23055](https://github.com/github/gh-aw/pull/23055)): todos os locais de emissão de `env:` no compilador agora usam escalares YAML escapados por `%q`, impedindo que caracteres de nova linha ou aspas em valores de frontmatter injetem variáveis de ambiente irmãs em arquivos `.lock.yml`.

### [v0.64.1](https://github.com/github/gh-aw/releases/tag/v0.64.1) — 26 de março

**`gh aw audit diff`** ([#22996](https://github.com/github/gh-aw/pull/22996)) permite comparar duas execuções de fluxo de trabalho lado a lado — comportamento do firewall, invocações de ferramenta MCP, uso de token e duração — para detectar regressões e desvios comportamentais antes que se tornem incidentes:

```bash
gh aw audit diff <run1> <run2> --format markdown
```

Cinco novas seções também foram adicionadas ao relatório padrão `gh aw audit`: Engine Configuration, Prompt Analysis, Session & Agent Performance, Safe Output Summary e MCP Server Health. Um relatório agora fornece a imagem completa.

### [v0.64.0](https://github.com/github/gh-aw/releases/tag/v0.64.0) — 25 de março

**Isolamento de concorrência do bot-actor**: Fluxos de trabalho combinando `safe-outputs.github-app` com gatilhos capazes de `issue_comment` agora obtêm automaticamente chaves de concorrência isoladas de bot, evitando que o fluxo de trabalho se cancele no meio da execução quando o bot posta um comentário que re-dispara o mesmo fluxo de trabalho.

### [v0.63.1](https://github.com/github/gh-aw/releases/tag/v0.63.1) — 24 de março

Um patch focado adicionando o portão de pré-ativação **`skip-if-check-failing`** — fluxos de trabalho agora podem desistir antes que o agente rode se uma verificação de CI nomeada estiver falhando, evitando inferência desperdiçada em uma base de código quebrada. Também envia um algoritmo de agenda fuzzy melhorado com janelas preferenciais ponderadas e evitação de pico para reduzir a contenção de fila em runners compartilhados.

---

## 🤖 Agente da Semana: auto-triage-issues

O porteiro autoproclamado do rastreador de issues — lê cada nova issue e atribui labels para que as pessoas certas as vejam.

Esta semana, `auto-triage-issues` realizou três execuções. Duas delas foram textbook de eficiência: disparadas no momento em que uma nova issue surgiu, rodou a verificação de pré-ativação, decidiu que não havia nada que valesse a pena rotular e encerrou em menos de 42 segundos. Sem alarde, sem drama. Então veio a varredura agendada de segunda-feira. Essa execução tomou uma direção diferente: 18 turnos, 817.000 tokens e, após toda essa contemplação... uma falha. Em algum lugar entre o turno um e o turno dezoito, o fluxo de trabalho de triagem decidiu que este lote de issues merecia sua análise mais criteriosa de todas, consumiu a paciência de um modelo de fronteira e ainda assim não conseguiu fechar o ciclo.

É o problema clássico do superestimador — às vezes as issues que parecem mais simples acabam sendo as que levam o dia todo.

💡 **Dica de uso**: Se as suas execuções agendadas de `auto-triage-issues` são consistentemente caras, a métrica `agentic_fraction` em `gh aw audit` pode ajudá-lo a identificar quais turnos são pura coleta de dados e poderiam ser movidos para passos de shell determinísticos.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/auto-triage-issues.md)

---

## Experimente

Atualize para a [v0.64.4](https://github.com/github/gh-aw/releases/tag/v0.64.4) hoje com `gh extension upgrade aw`. A migração da memória de cache consciente da integridade acionará um cache miss único na primeira execução — esperado e seguro. Como sempre, perguntas e contribuições são bem-vindas em [github/gh-aw](https://github.com/github/gh-aw).
