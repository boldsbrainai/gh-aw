---
title: "Atualização Semanal – 6 de abril de 2026"
description: "Dez lançamentos em sete dias: rastreamento distribuído OpenTelemetry completo, um novo safe output report_incomplete, suporte ao Claude Code 1.0.0 e endurecimento de segurança em toda a linha."
authors:
  - copilot
date: 2026-04-06
---

Dez lançamentos desembarcaram em [github/gh-aw](https://github.com/github/gh-aw) entre 31 de março e 6 de abril — um ritmo implacável que entregou rastreamento distribuído pronto para produção, novos sinais de safe output e uma varredura de segurança abrangente. Aqui está o que foi enviado.

## Destaques do Lançamento

### [v0.67.1](https://github.com/github/gh-aw/releases/tag/v0.67.1) — Revisão do OpenTelemetry & Endurecimento de Segurança (6 de abril)

O lançamento de destaque da semana refina o rastreamento OTLP introduzido na v0.67.0 e adiciona uma onda de correções de segurança.

- **Nomes de span precisos e durações de job reais** ([#24823](https://github.com/github/gh-aw/pull/24823)): Spans de ciclo de vida de job agora usam o nome real do job (ex: `gh-aw.agent.conclusion`) e registram o tempo de execução real — anteriormente, os spans sempre relatavam 2-5 ms devido a um `startMs` ausente.
- **Sanitização de payload OTLP**: Valores sensíveis (`token`, `secret`, `key`, `auth`, etc.) nos atributos de span são automaticamente redigidos antes de enviar para qualquer coletor OTLP.
- **Mascaramento de cabeçalhos OTLP** ([#24805](https://github.com/github/gh-aw/pull/24805)): `OTEL_EXPORTER_OTLP_HEADERS` é mascarado com `::add-mask::` em cada job, impedindo que tokens de autenticação vazem para os logs de depuração do GitHub Actions.
- **OpenTelemetry no MCP Gateway** ([#24697](https://github.com/github/gh-aw/pull/24697)): O MCP Gateway agora recebe configuração de OpenTelemetry derivada do frontmatter `observability.otlp` e os trace IDs do `actions/setup`, correlacionando todos os rastreamentos de invocação de ferramenta MCP sob o rastreamento raiz do fluxo de trabalho.
- **Safe output `report_incomplete`** ([#24796](https://github.com/github/gh-aw/pull/24796)): Um novo sinal de primeira classe permite que os agentes exibam falhas de infraestrutura ou ferramenta sem serem classificados incorretamente como execuções bem-sucedidas. Quando um agente emite `report_incomplete`, o manipulador de safe-outputs ativa o tratamento de falhas independentemente do código de saída do agente.
- **`checks` como ferramenta MCP de primeira classe** ([#24818](https://github.com/github/gh-aw/pull/24818)): A ferramenta `checks` agora está registrada no servidor MCP gh-aw, retornando um veredito de CI normalizado (`success`, `failed`, `pending`, `no_checks`, `policy_blocked`).
- **Prevenção de injeção de token/segredo**: 422 instâncias de `${{ secrets.* }}` interpoladas diretamente em blocos `run:` foram movidas para mapeamentos `env:` em todos os arquivos de trava.
- **Compatibilidade com Claude Code 1.0.0** ([#24807](https://github.com/github/gh-aw/pull/24807)): Removido o flag `--disable-slash-commands` que foi descartado no Claude Code 1.0.0.

### [v0.67.0](https://github.com/github/gh-aw/releases/tag/v0.67.0) — Exportação de Trace OTLP & Analytics de Limite de Taxa da API GitHub (5 de abril)

O lançamento do marco que trouxe o suporte ao rastreamento distribuído:

- **Frontmatter `observability.otlp`**: Fluxos de trabalho agora podem exportar spans estruturados de OpenTelemetry para qualquer backend compatível com OTLP (Honeycomb, Grafana Tempo, Sentry) com um único bloco de frontmatter. Cada job emite spans de setup e conclusão; a correlação de trace cross-job é conectada automaticamente com um único ID de trace do job de ativação.
- **Analytics de limite de taxa da API GitHub**: `gh aw audit`, `gh aw logs` e `gh aw audit diff` agora mostram a cota da API GitHub consumida por execução, por recurso.
- **Referência de Variável de Ambiente**: Uma nova seção de referência abrangente cobre todas as variáveis de configuração da CLI.

### [v0.66.1](https://github.com/github/gh-aw/releases/tag/v0.66.1) — `gh aw logs` mais rico & Mudança Importante (4 de abril)

**⚠️ Mudança importante**: `gh aw audit report` foi removido. Relatórios de segurança cross-run agora são gerados diretamente por `gh aw logs --format`. O novo flag `--last` cria um alias para `--count` para facilitar a migração.

- **Classificação de execução plana** em `gh aw logs --json`: Cada execução agora carrega uma string de `classification` de nível superior (`"risky"`, `"normal"`, `"baseline"` ou `"unclassified"`), eliminando a necessidade de ginástica com guardas nulas.
- **Métricas por chamada de ferramenta nos logs**: Uso granular de token, contagem de falhas e latência por ferramenta — perfeito para identificar quais ferramentas consomem mais recursos.

### [v0.66.0](https://github.com/github/gh-aw/releases/tag/v0.66.0) — Artefatos de Uso de Token & Extensibilidade de Detecção de Ameaças (3 de abril)

- **Artefato de Uso de Token** ([#24315](https://github.com/github/gh-aw/pull/24315)): O uso de token do agente agora é feito upload como um artefato de fluxo de trabalho, tornando fácil rastrear o gasto ao longo do tempo.
- Melhorias na confiabilidade do fluxo de trabalho e na extensibilidade da detecção de ameaças foram lançadas junto.

### Anteriormente na semana

[v0.65.7](https://github.com/github/gh-aw/releases/tag/v0.65.7) até [v0.65.2](https://github.com/github/gh-aw/releases/tag/v0.65.2) (31 de março–3 de abril) focaram na confiabilidade de fluxo de trabalho cross-repo, configuração de keepalive do gateway MCP, melhorias de safe-outputs e ferramentas de otimização de token.

---

## 🤖 Agente da Semana: agentic-observability-kit

O incansável cão de guarda que monitora toda a sua frota de fluxos de trabalho agentic e escala quando as coisas saem dos trilhos.

Todos os dias, `agentic-observability-kit` puxa logs de todos os fluxos de trabalho em execução, classifica seus comportamentos e posta um relatório de observabilidade estruturado como uma Discussão no GitHub — depois arquiva issues quando padrões de desperdício ou falha cruzam limites definidos. Na semana passada, teve uma execução particularmente movimentada: em 6 de abril, detectou que `smoke-copilot` e `smoke-claude` tinham consumido entre 675 mil e 1,7 milhão de tokens cada em múltiplas execuções (marcadas como `resource_heavy_for_domain` com alta severidade), e abriu uma issue intitulada *"Smoke Copilot and Smoke Claude repeatedly resource-heavy"* antes que alguém da equipe notasse. Também detectou que o fluxo de trabalho de Teste de Autenticação MCP Remoto do GitHub teve uma taxa de falha de 100% em duas execuções — uma das quais foi concluída com zero tokens, sugerindo um problema de configuração ou autenticação em vez de um agente se comportando mal.

Em um momento deliciosamente meta, o próprio kit de observabilidade atingiu erros de limite de token ao tentar ingerir seus próprios dados de log — fez quatro tentativas com parâmetros de `count` e `max_tokens` progressivamente menores antes que pudesse ajustar a saída ao contexto. Conseguiu no final.

💡 **Dica de uso**: Combine `agentic-observability-kit` com notificações do Slack ou e-mail para que issues de escalonamento disparem um alerta — caso contrário, as issues que ele abre podem ficar sem leitura enquanto a conta de tokens aumenta silenciosamente.

→ [Ver o fluxo de trabalho no GitHub](https://github.com/github/gh-aw/blob/main/.github/workflows/agentic-observability-kit.md)

---

## Experimente

Atualize para a [v0.67.1](https://github.com/github/gh-aw/releases/tag/v0.67.1) e comece a exportar rastreamentos de seus fluxos de trabalho hoje — tudo o que é preciso é um bloco `observability.otlp` no seu frontmatter. Feedback e contribuições são sempre bem-vindos em [github/gh-aw](https://github.com/github/gh-aw).
