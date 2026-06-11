---
title: "Lições de Segurança da Fábrica de Agentes"
description: "Projetando ambientes seguros onde os agentes não podem causar danos acidentalmente"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-02-02
draft: true
prev:
  link: /gh-aw/blog/2026-01-30-imports-and-sharing/
  label: Imports & Compartilhamento
next:
  link: /gh-aw/blog/2026-02-05-how-workflows-work/
  label: Como os Workflows Funcionam
---

[Artigo Anterior](/gh-aw/blog/2026-01-30-imports-and-sharing/)

---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

Reúnam-se, reúnam-se para *o próximo banquete delicioso* na série Fábrica de Agentes de Peli! Tendo acabado de saborear as maravilhas dos [imports e compartilhamento](/gh-aw/blog/2026-01-30-imports-and-sharing/), agora nos aventuramos no *cofre* - a câmara mais crítica de todas - onde discutimos segurança!

A segurança em fluxos de trabalho agentic não é apenas sobre bloquear coisas - é sobre projetar ambientes onde os fluxos de trabalho agentic podem fazer seu trabalho com segurança, mesmo se cometerem erros. Nossa coleção de fluxos de trabalho na prática nos ensinou muito sobre o que funciona (e o que não funciona).

Aqui está a questão: **segurança não é apenas sobre permissões**. É sobre criar barreiras que permitam que os fluxos de trabalho sejam produtivos enquanto os impedem de causar danos acidentalmente. Muitas das características de segurança nos fluxos de trabalho agentic do GitHub vieram diretamente das lições que aprendemos na fábrica.

Vamos compartilhar o que descobrimos para que você possa construir ecossistemas de agentes seguros desde o primeiro dia.

## Princípios Fundamentais de Segurança

### Privilégio Mínimo, Sempre

**Comece com somente leitura. Adicione permissões de escrita apenas quando absolutamente necessário, e sempre através de safe outputs limitados.**

Todo fluxo de trabalho começa com `permissions: contents: read`. Essa é nossa postura padrão. Permissões de escrita (`contents: write`, `pull-requests: write`, `issues: write`) são concedidas parcimoniosamente e apenas através de mecanismos de safe output.

**Exemplo**: O agente [`audit-workflows`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/audit-workflows.md) tem acesso somente leitura às execuções de fluxo de trabalho, mas cria relatórios via discussões, que são somente para anexar por natureza.

**Por que isso funciona**: Se um agente só pode ler, o pior que ele pode fazer é desperdiçar tempo de computação. Ele não pode deletar código, fechar issues importantes ou enviar mudanças maliciosas.

### Safe Outputs como o Gateway

**Todas as operações efetivas passam por safe outputs com limites integrados.**

Safe outputs são, sem dúvida, o controle de segurança mais importante da fábrica. Eles fornecem uma API limitada para os agentes interagirem com o GitHub, com barreiras que impedem erros comuns:

**Proteções Integradas:**

- Número máximo de itens para criar (evita spam)
- Tempos de expiração (evita issues esquecidas)
- Lógica de "fechar duplicatas mais antigas" (evita duplicação)
- Guardas "se não houver mudanças" (evita PRs vazios)
- Validação de template (impõe estrutura)
- Limitação de taxa (evita abuso)

**Exemplo**: Um agente criando issues através de safe outputs pode especificar:

```yaml
safe_outputs:
  create_issue:
    title: "Encontrada vulnerabilidade de segurança"
    body: "Detalhes aqui"
    labels: ["security"]
    max_items: 3  # Crie no máximo 3 issues
    close_older: true  # Feche instâncias antigas
    expire: "+7d"  # Auto-feche se não for endereçado
```

**Por que isso funciona**: Safe outputs transformam "o agente pode fazer X?" em "sob quais restrições o agente pode fazer X?" O agente tem poder, mas não pode abusar dele. Bastante inteligente, não é?

### Ativação com Controle por Função (Role-Gated)

**Agentes poderosos (corretores, otimizadores) exigem funções específicas para serem invocados.**

Nem toda menção ou evento de fluxo de trabalho deve disparar agentes poderosos. Usamos controle por função (role-gating) para garantir que apenas usuários autorizados possam invocar operações sensíveis.

**Exemplo**: O otimizador [`q`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/q.md) exige que o usuário comentando `/q` seja um mantenedor do repositório. Contribuidores aleatórios não podem disparar execuções de otimização caras.

**Implementação**:

```yaml
on:
  issue_comment:
    types: [created]

jobs:
  check:
    if: |
      contains(github.event.comment.body, '/q') &&
      (github.event.comment.author_association == 'OWNER' ||
       github.event.comment.author_association == 'MEMBER')
```

**Por que isso funciona**: A autorização é aplicada no nível da plataforma GitHub, não pelo agente. O agente nem chega a rodar se o usuário não tiver permissões.

### ⏱️ Experimentos com Limite de Tempo

**Agentes experimentais incluem `stop-after: +1mo` para expirar automaticamente.**

Incentivamos a experimentação, mas os experimentos não devem rodar para sempre. Limites de tempo impedem que demos esquecidas consumam recursos ou causem confusão.

**Exemplo**:

```yaml
---
description: Agente experimental de desduplicação de código
stop-after: +1mo
---
```

Após um mês, o fluxo de trabalho se desabilita automaticamente. Se o experimento funcionar, você pode graduá-lo para a produção sem o limite de tempo.

**Por que isso funciona**: A expiração explícita força decisões intencionais. Todo agente rodando na fábrica está lá deliberadamente, não apenas esquecido.

### Listas de Ferramentas Explícitas

**Os fluxos de trabalho declaram exatamente quais ferramentas usam. Sem autoridade ambiente.**

Cada fluxo de trabalho lista explicitamente seus requisitos de ferramenta. Não existe "me dê acesso a tudo". Isso torna a revisão de segurança direta e detecta o uso indevido de ferramentas precocemente.

**Exemplo**:

```yaml
tools:
  github:
    toolsets: [repos, issues]  # Apenas repos e issues
  bash:
    commands: [git, jq, python]  # Apenas estes comandos
network:
  allowed:
    - "api.github.com"  # Apenas GitHub API
```

**Por que isso funciona**: Explícito é melhor que implícito sempre. Os revisores podem avaliar rapidamente o risco. Agentes não podem usar ferramentas por acidente que não deveriam ter.

### 📋 Auditável por Padrão

**Discussões e ativos criam um "livro-razão do agente" natural. Você sempre pode rastrear o que um agente fez e quando.**

Cada ação do agente deixa um rastro:

- Issues e PRs são carimbados com data/hora
- Comentários são atribuídos
- Discussões são permanentes
- Artefatos são versionados
- As execuções do fluxo de trabalho são registradas

**Exemplo**: O [`agent-performance-analyzer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/agent-performance-analyzer.md) cria posts semanais de discussão. Você pode voltar meses para ver como a qualidade do agente evoluiu ao longo do tempo.

**Por que isso funciona**: A transparência constrói confiança. Quando algo dá errado, a trilha de auditoria torna a depuração direta. Quando algo dá certo, a evidência está lá para todos verem.

## Padrões de Segurança

### Padrão 1: Analistas Somente Leitura (Read-Only Analysts)

Os agentes mais seguros são somente leitura. Eles observam, analisam e relatam - mas nunca modificam nada.

**Propriedades de Segurança:**

- ✅ Risco zero de dano ao código
- ✅ Não podem fechar ou modificar issues
- ✅ Não podem criar spam
- ✅ Seguro para rodar em qualquer frequência

**Caso de uso**: Coleta de métricas, monitoramento de saúde, pesquisa, auditoria

**Exemplo**: Todos os 15 fluxos de trabalho de analista somente leitura na fábrica têm registros de segurança perfeitos - zero incidentes. Isso diz algo!

### Padrão 2: Escritas Delimitadas por Safe Output

Quando os agentes precisam de acesso de escrita, use safe outputs com limites rigorosos.

**Propriedades de Segurança:**

- ✅ Limitado por número máximo de itens
- ✅ Issues/PRs de expiração automática
- ✅ Detecção de duplicação
- ✅ Aplicação de template
- ✅ Limite de taxa (rate limited)

**Caso de uso**: Triagem de issue, criação de PR, atualizações de documentação

**Exemplo**: O [`issue-triage-agent`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/issue-triage-agent.md) pode adicionar labels, mas não pode fechar issues ou modificar código.

### Padrão 3: Humano-no-Loop (Human-in-the-Loop)

Para operações de alto impacto, exija aprovação humana antes da execução.

**Propriedades de Segurança:**

- ✅ Humano revisa PR antes do merge
- ✅ Passo de aprovação explícito
- ✅ Pode ser revertido
- ✅ Trilha de responsabilidade mantida

**Caso de uso**: Mudanças de código, atualizações de dependência, mudanças de configuração

**Exemplo**: O [`daily-workflow-updater`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/daily-workflow-updater.md) cria PRs para atualizações de dependência, mas nunca os faz merge automaticamente.

### Padrão 4: ChatOps com Controle por Função

Agentes interativos que exigem autorização para serem invocados.

**Propriedades de Segurança:**

- ✅ Autorização imposta pela plataforma
- ✅ Trilha de invocação clara
- ✅ Atribuição de usuário
- ✅ Pode ser desabilitado por usuário

**Caso de uso**: Revisão de código, otimização, assistência de depuração

**Exemplo**: O [`grumpy-reviewer`](https://github.com/github/gh-aw/tree/2c1f68a721ae7b3b67d0c2d93decf1fa5bcf7ee3/.github/workflows/grumpy-reviewer.md) exige acesso de colaborador para ser invocado via `/grumpy`.

### Padrão 5: Rede Restrita

Limite o acesso à rede a domínios permitidos específicos.

**Propriedades de Segurança:**

- ✅ Impede exfiltração de dados
- ✅ Bloqueia chamadas de API não autorizadas
- ✅ Imposto no nível da infraestrutura
- ✅ Auditoria clara do uso de rede

**Caso de uso**: Qualquer agente que não precise de acesso externo à rede

**Exemplo**: A maioria dos agentes de análise só precisa de acesso a `api.github.com` - nada mais.

## Lições Chave

Construir ecossistemas de agentes seguros não é sobre dizer "não" para tudo. É sobre projetar ambientes onde os agentes podem ser produtivos enquanto permanecem seguros:

1. **Comece somente leitura** - Adicione permissões de escrita apenas quando necessário
2. **Use safe outputs** - Eles são seu controle de segurança mais importante
3. **Limite operações poderosas** - O acesso baseado em função evita abusos
4. **Limite o tempo de experimentos** - Evite que demos esquecidas rodem para sempre
5. **Seja explícito sobre ferramentas** - Sem autoridade ambiente
6. **Abrace a auditabilidade** - A transparência constrói confiança
7. **Combine padrões** - Camadas de controles de segurança para defesa em profundidade

A segurança em fluxos de trabalho agentic é sobre permitir a inovação com segurança. Com as barreiras certas, os agentes podem fazer coisas incríveis sem tirar seu sono à noite.

- ✅ Não podem exfiltrar dados
- ✅ Não podem acessar serviços internos
- ✅ Não podem baixar payloads maliciosos
- ✅ Imposto no nível da infraestrutura

**Caso de uso**: Fluxos de trabalho que precisam de APIs externas

**Exemplo**: Fluxos de trabalho usando pesquisa Tavily só podem acessar `api.tavily.com`, não sites arbitrários.

## Erros Comuns de Segurança

### Erro 1: Padrões Excessivamente Permissivos

**Problema**: Conceder `contents: write` quando `contents: read` é suficiente.

**Impacto**: O agente pode empurrar alterações de código acidentalmente.

**Solução**: Comece com privilégio mínimo. Adicione permissões apenas quando safe outputs as exigirem.

### Erro 2: Safe Outputs Sem Limites

**Problema**: Esquecer o limite `max_items` na criação de safe output.

**Impacto**: O agente cria centenas de issues duplicadas.

**Solução**: Sempre defina `max_items`, `expire` e `close_older` em safe outputs.

### Erro 3: Falta de Lista de Permissões de Ferramentas

**Problema**: Permitir `bash: "*"` (todos os comandos bash).

**Impacto**: O agente pode rodar `rm -rf` ou outros comandos destrutivos.

**Solução**: Liste explicitamente os comandos permitidos: `bash: [git, jq, python]`.

### Erro 4: Falta de Portões de Função (Role Gates)

**Problema**: Qualquer um pode disparar o comando `/deploy`.

**Impacto**: Ator malicioso dispara operações caras ou destrutivas.

**Solução**: Adicione verificações de associação de autor para operações sensíveis.

### Erro 5: Sem Restrições de Rede

**Problema**: Permitir acesso de rede aberto.

**Impacto**: O agente pode acessar serviços internos ou exfiltrar dados.

**Solução**: Use `network.allowed` para listar domínios específicos.

## Incidentes de Segurança e Resposta

A fábrica vivenciou alguns incidentes próximos à segurança que ensinaram lições valiosas:

### Incidente 1: Spam de Issue

**O que aconteceu**: Agente com safe output `create_issue` ilimitado criou 50+ issues duplicadas.

**Causa raiz**: Falta de limites `max_items` e `close_older`.

**Correção**: Adicionado `max_items: 3` e `close_older: true` a todas as safe outputs de criação de issue.

**Lição**: Safe outputs precisam de limites explícitos, não apenas portões de permissão.

### Incidente 2: Loop de Fluxo de Trabalho Caro

**O que aconteceu**: Agente disparou a si mesmo recursivamente, criando um loop de fluxo de trabalho.

**Causa raiz**: Fluxo de trabalho disparado em `workflow_run: completed` sem filtragem.

**Correção**: Adicionado filtro de nome de fluxo de trabalho para evitar o auto-disparo.

**Lição**: Filtros de evento são controles de segurança, não apenas otimizações.

### Incidente 3: Referência de Segredo Vazada

**O que aconteceu**: Agente registrou o token do GitHub na mensagem de erro.

**Causa raiz**: Tratamento de erro excessivamente verboso.

**Correção**: Sanitizadas todas as mensagens de erro. Adicionado escaneamento de segredos ao CI.

**Lição**: Trate logs como públicos. Nunca registre credenciais.

### Incidente 4: Tentativa de Escalonamento de Permissão

**O que aconteceu**: Usuário tentou invocar `/q` sem permissões.

**Causa raiz**: Verificação de função foi comentada durante a depuração.

**Correção**: Reabilitada verificação de função. Adicionado teste para verificar.

**Lição**: Controles de segurança devem ser testados e visíveis.

## Referência de Arquitetura de Segurança

Para detalhes técnicos mais profundos, veja:

- [Arquitetura de Segurança](https://github.github.com/gh-aw/introduction/architecture/)
- [Documentação de Safe Outputs](https://github.github.com/gh-aw/reference/safe-outputs/)

## Defesa em Profundidade

A segurança da fábrica não é um mecanismo único - é em camadas:

1. **Plataforma**: Isolamento do GitHub Actions, sandboxing de runner
2. **Permissões**: Privilégio mínimo via GITHUB_TOKEN
3. **Safe Outputs**: API limitada com barreiras
4. **Portões de Função**: Verificações de autorização
5. **Rede**: Domínios listados
6. **Ferramentas**: Listadas explicitamente, sem curingas
7. **Auditoria**: Logs de atividade completos
8. **Limites de Tempo**: Auto-expiração para experimentos
9. **Revisão de Código**: Revisão de segurança antes do merge
10. **Monitoramento**: Meta-agentes vigiam anomalias

Se uma camada falhar, outras ainda oferecem proteção.

## O Que Vem a Seguir?

Com os fundamentos de segurança estabelecidos, podemos explorar como os fluxos de trabalho agentic realmente funcionam nos bastidores - desde markdown de linguagem natural até execução segura no GitHub Actions.

Em nosso próximo artigo, percorreremos a arquitetura técnica que alimenta a fábrica.

_Mais artigos nesta série em breve._

[Artigo Anterior](/gh-aw/blog/2026-01-30-imports-and-sharing/)
