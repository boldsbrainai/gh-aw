---
title: Glossário
description: Definições de termos técnicos e conceitos usados em toda a documentação do GitHub Agentic Workflows.
sidebar:
  order: 1000
---

Este glossário fornece definições para termos técnicos e conceitos-chave usados no GitHub Agentic Workflows.

## Conceitos Fundamentais

### Agentic (Agêntico)

Ter agência - a capacidade de agir de forma independente, tomar decisões baseadas no contexto e adaptar o comportamento com base nas circunstâncias. Os fluxos de trabalho agentic usam IA para entender o contexto e escolher ações apropriadas, contrastando com fluxos de trabalho determinísticos que executam sequências fixas. De "agente" + "-ico" (tendo as características de).

### Fluxo de Trabalho Agentic (Agentic Workflow)

Um fluxo de trabalho impulsionado por IA que raciocina, toma decisões e realiza ações autônomas usando instruções em linguagem natural. Escritos em markdown em vez de YAML complexo, os fluxos de trabalho agentic interpretam o contexto e adaptam o comportamento de forma flexível. Por exemplo, em vez de "se a issue tiver a label X, faça Y", você escreve "analise esta issue e forneça contexto útil", e a IA decide o que é útil com base no conteúdo específico da issue.

### Orquestração

Fluxos de trabalho que coordenam um ou mais fluxos de trabalho trabalhadores (worker) em direção a um objetivo compartilhado. Um orquestrador decide qual trabalho fazer a seguir e despacha trabalhadores, enquanto trabalhadores executam tarefas concretas com ferramentas e limites definidos. Veja o [guia de Orquestração](/gh-aw/patterns/orchestration/).

### Fluxo de Trabalho Orquestrador

Um fluxo de trabalho que distribui trabalho despachando outros fluxos de trabalho (trabalhadores), agrega resultados e, opcionalmente, posta resumos.

### Fluxo de Trabalho Trabalhador (Worker)

Um fluxo de trabalho despachado por um orquestrador que realiza uma unidade de trabalho focada (triagem, análise, alterações de código, validação).

### Motor Agentic ou Agente de Codificação

O sistema de IA (tipicamente GitHub Copilot CLI) que executa instruções em linguagem natural em um fluxo de trabalho agentic. O agente interpreta tarefas, usa ferramentas disponíveis (API do GitHub, sistema de arquivos, busca na web) e gera saídas com base no contexto de forma autônoma.

### Frontmatter

Seção de configuração no topo de um arquivo de fluxo de trabalho, delimitada por marcadores `---`. Contém configurações YAML que controlam quando o fluxo de trabalho é executado, permissões e ferramentas disponíveis, separando a configuração técnica das instruções em linguagem natural.

### Compilação

Tradução de fluxos de trabalho Markdown (arquivos `.md`) para o formato YAML do GitHub Actions (arquivos `.lock.yml`), incluindo validação, resolução de importação, configuração de ferramenta e endurecimento de segurança.

### Arquivo de Bloqueio de Fluxo de Trabalho (.lock.yml)

O arquivo de fluxo de trabalho do GitHub Actions compilado a partir de um arquivo markdown de fluxo de trabalho (`.md`). Contém o YAML completo do GitHub Actions com endurecimento de segurança aplicado. Tanto os arquivos `.md` quanto os `.lock.yml` devem ser comitados no controle de versão. Em tempo de execução, o GitHub Actions executa o arquivo de bloqueio usando um agente de codificação enquanto referencia o markdown para instruções.

## Ferramentas e Integração

### MCP (Model Context Protocol)

Um protocolo padronizado que permite que agentes de IA se conectem de forma segura a ferramentas, bancos de dados e serviços externos. O MCP permite que fluxos de trabalho se integrem com APIs do GitHub, serviços web, sistemas de arquivos e integrações personalizadas, mantendo controles de segurança.

### Gateway MCP

Um serviço de proxy transparente que permite acesso HTTP unificado a múltiplos servidores MCP usando diferentes mecanismos de transporte (stdio, HTTP). Fornece tradução de protocolo, isolamento de servidor, autenticação e monitoramento de integridade, permitindo que clientes interajam com múltiplos backends por meio de um único endpoint HTTP.

### Bots Confiáveis (`sandbox.mcp.trusted-bots`)

Um campo de frontmatter que passa strings de identidade de bots do GitHub adicionais para o [Gateway MCP](#mcp-gateway). O gateway mescla estas com sua lista de identidade confiável embutida para determinar quais identidades de bot são permitidas. Este campo é aditivo — ele pode apenas estender a lista interna do gateway, não remover entradas embutidas. Configurado sob `sandbox.mcp:` e compilado na array `trustedBots` na configuração do gateway gerada. Exemplos de entradas: `github-actions[bot]`, `copilot-swe-agent[bot]`. Veja [Referência do Gateway MCP](/gh-aw/reference/mcp-gateway/).

### Servidor MCP

Um serviço que implementa o Model Context Protocol para fornecer capacidades específicas aos agentes de IA. Exemplos incluem o servidor MCP do GitHub (para operações da API do GitHub), servidor MCP do Playwright (para automação de navegador) ou servidores MCP personalizados para ferramentas especializadas. Veja [Referência do Playwright](/gh-aw/reference/playwright/) para configuração de automação de navegador.

### Busca na Documentação QMD (`qmd:`)

Uma ferramenta embutida que fornece busca de similaridade vetorial sobre arquivos de documentação. Configurada via `tools.qmd:` no frontmatter, a ferramenta `qmd` executa o [tobi/qmd](https://github.com/tobi/qmd) como um servidor MCP para que os agentes possam encontrar documentação relevante por consulta de linguagem natural. O índice de busca é construído em um job de indexação dedicado (que possui `contents: read`) e compartilhado com o job do agente via `actions/cache`, portanto, o job do agente não precisa de `contents: read`. Suporta indexação a partir de checkouts de repositório, consultas de busca de código do GitHub e modo somente leitura apenas de cache. Veja [Busca na Documentação QMD](/gh-aw/reference/qmd/).

### Ferramentas (Tools)

Capacidades que um agente de IA pode usar durante a execução do fluxo de trabalho. Ferramentas são configuradas no frontmatter e incluem operações do GitHub ([`github:`](/gh-aw/reference/github-tools/)), edição de arquivo (`edit:`), acesso à web (`web-fetch:`, `web-search:`), comandos shell (`bash:`), automação de navegador ([`playwright:`](/gh-aw/reference/playwright/)) e servidores MCP personalizados.

### Modo de Acesso ao GitHub (`tools.github.mode`)

Um campo `tools.github` que controla como o agente acessa APIs do GitHub. Três valores são suportados: `gh-proxy` (recomendado — fornece orientação de prompt da CLI `gh` pré-autenticada sem montar um servidor MCP do GitHub, substituindo a flag obsoleta `features.cli-proxy: true`), `local` (servidor MCP do GitHub baseado em Docker, o padrão legado) e `remote` (servidor MCP do GitHub hospedado em `api.githubcopilot.com`). Use `gh-proxy` para melhor desempenho; use `local` ou `remote` quando toolsets do GitHub baseados em MCP forem necessários. Veja [Referência de Ferramentas do GitHub](/gh-aw/reference/github-tools/).

## Segurança e Saídas

### Scripts MCP

Ferramentas MCP personalizadas definidas inline no frontmatter do fluxo de trabalho usando JavaScript ou scripts shell. Permite a criação leve de ferramentas sem dependências externas, mantendo acesso controlado a segredos. As ferramentas são geradas em tempo de execução e montadas como um servidor MCP com parâmetros de entrada tipados, valores padrão e variáveis de ambiente. Configurado via seção `mcp-scripts:`.

### SARIF

Static Analysis Results Interchange Format - um formato JSON padronizado para relatar resultados de ferramentas de análise estática. Usado pelo Code Scanning do GitHub para exibir vulnerabilidades de segurança e problemas de qualidade de código. Fluxos de trabalho podem gerar arquivos SARIF usando o safe output `create-code-scanning-alert`.

### Safe Outputs (Saídas Seguras)

Ações pré-aprovadas que a IA pode tomar sem permissões elevadas. A IA gera saída estruturada descrevendo o que criar (issues, comentários, pull requests), processada por jobs separados controlados por permissão. Configurado via seção `safe-outputs:`, permitindo que agentes de IA criem conteúdo do GitHub sem acesso direto de escrita.

### Pwn Request

Uma vulnerabilidade de segurança crítica que ocorre quando um fluxo de trabalho `pull_request_target` faz checkout e executa código de um PR de fork. Como `pull_request_target` é executado no contexto do branch de destino (base) com permissões totais de escrita e acesso a segredos do repositório, a execução de código de fork não confiável concede a um atacante a capacidade de exfiltrar segredos ou fazer alterações não autorizadas. O compilador emite um aviso (modo não estrito) ou um erro grave (modo estrito) quando `pull_request_target` é usado sem `checkout: false`. Adicione `checkout: false` para impedir o checkout inseguro; use `pull_request` em vez disso quando não precisar de acesso de escrita. Veja o [advisory do GitHub Security Lab sobre pwn requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/).

### Detecção de Ameaças (Threat Detection)

Análise de segurança automatizada que verifica a saída do agente e as alterações de código em busca de possíveis problemas de segurança antes da aplicação. Quando safe outputs são configurados, um job de detecção de ameaças é executado automaticamente entre o job do agente e o processamento de safe output para identificar tentativas de injeção de prompt, vazamentos de segredo e patches de código malicioso. Veja [Referência de Detecção de Ameaças](/gh-aw/reference/threat-detection/).

### Modo Staged (Staged Mode)

Um modo de visualização onde os fluxos de trabalho simulam ações sem fazer alterações. A IA gera saída mostrando o que aconteceria, mas nenhuma operação de escrita da API do GitHub é realizada. Use para testes antes de execuções em produção. Veja [Modo Staged](/gh-aw/reference/staged-mode/) para detalhes.

### Filtragem de Integridade

Um recurso de guardrail que controla qual conteúdo do GitHub um agente pode acessar, filtrando por confiança do autor e status de mesclagem. O conteúdo abaixo do limite de `min-integrity` configurado é silenciosamente removido antes que o motor de IA o veja. Os quatro níveis são `merged`, `approved`, `unapproved` e `none` (do mais restritivo ao menos restritivo). Para repositórios públicos, `min-integrity: approved` é aplicado automaticamente — restringindo o conteúdo a proprietários, membros e colaboradores — mesmo sem autenticação adicional. Defina `min-integrity: none` para permitir que todo o conteúdo passe para fluxos de trabalho projetados para processar entrada não confiável (ex: bots de triagem).

Três campos adicionais estendem a filtragem de integridade além do limite de nível: `trusted-users` eleva nomes de usuário específicos do GitHub para integridade `approved` independentemente da associação do autor; `blocked-users` nega incondicionalmente conteúdo de nomes de usuário listados independentemente do nível; e `approval-labels` promove itens que carregam qualquer label listada para integridade `approved`. Veja [Filtragem de Integridade](/gh-aw/reference/integrity/).

### Proxy DIFC (`tools.github.integrity-proxy`)

Controla a aplicação completa de proxy DIFC (Data Integrity and Flow Control). Quando `tools.github.min-integrity` é configurado, o compilador injeta passos de proxy ao redor do job do agente que aplicam isolamento de nível de integridade no limite da rede. O proxy é **habilitado por padrão** — defina `tools.github.integrity-proxy: false` para desabilitá-lo e confiar apenas na filtragem de nível de gateway MCP. Conteúdo filtrado é registrado como eventos `DIFC_FILTERED` em `gateway.jsonl` para inspeção posterior. Veja [Filtragem de Integridade](/gh-aw/reference/integrity/).

### Reações de Integridade (`features.integrity-reactions`)

Uma feature flag que habilita reações do GitHub (👍, ❤️, 👎, 😕) para promover ou rebaixar conteúdo passando pelo filtro de integridade, sem adicionar labels ou modificar o estado da issue. Disponível a partir do gh-aw v0.68.2.

```aw wrap
features:
  integrity-reactions: true
tools:
  github:
    min-integrity: approved
```

Quando definida, o compilador habilita automaticamente o proxy da CLI (necessário para identificar autores de reação) e injeta a configuração de reação padrão. Quando uma conta em ou acima de `endorser-min-integrity` adiciona uma reação de endosso a uma issue ou comentário, a integridade do item é promovida para `approved`. Uma reação de reprovação de tal conta define a integridade do item para `disapproval-integrity`.

Veja [Promovendo e rebaixando itens via reações](/gh-aw/reference/integrity/#promoting-and-demoting-items-via-reactions) na Referência de Filtragem de Integridade para detalhes completos de configuração.

### Status Comment

Um comentário postado na issue ou pull request disparador que mostra o status da execução do fluxo de trabalho (iniciado e concluído). Configurado via `status-comment: true` em `safe-outputs`. Padrão para `true` para triggers `slash_command` e `label_command`; deve ser explicitamente habilitado para outros tipos de trigger. Defina `status-comment: false` para desabilitar. Não agrupado automaticamente com `ai-reaction` — cada um deve ser configurado independentemente.

### Permissões

Controles de acesso que definem operações de fluxo de trabalho. Os fluxos de trabalho seguem o princípio do menor privilégio, começando com acesso de leitura apenas por padrão. Operações de escrita são tipicamente tratadas por meio de safe outputs.

### Mensagens de Safe Output

Templates de mensagem personalizáveis que os fluxos de trabalho podem exibir durante a execução. Configurado em `safe-outputs.messages` com tipos `run-started`, `run-success`, `run-failure` e `footer`. Suporta variáveis de contexto do GitHub como `{workflow_name}` e `{run_url}`.

### Relatório de Falha de Issue (`report-failure-as-issue:`)

Uma opção de `safe-outputs` que controla se falhas na execução do fluxo de trabalho são automaticamente relatadas como issues do GitHub. Padrão para `true` quando safe outputs são configurados. Defina como `false` para suprimir a criação de issue de falha para fluxos de trabalho onde falhas são esperadas ou tratadas externamente:

```yaml
safe-outputs:
  report-failure-as-issue: false
```

Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/).

### Repositório de Issue de Falha (`failure-issue-repo:`)

Uma opção de `safe-outputs` que redireciona issues de rastreamento de falha para um repositório diferente. Útil quando o repositório do fluxo de trabalho tem issues desativadas:

```yaml
safe-outputs:
  failure-issue-repo: github/docs-engineering
```

Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/).

### Upload de Ativos

Uma capacidade de safe output para fazer upload de arquivos gerados (screenshots, gráficos, relatórios) para um branch git órfão para armazenamento persistente. A IA chama a ferramenta `upload_asset` para registrar arquivos, que são comitados em um branch de ativos dedicado por um job separado controlado por permissão. Os ativos são acessíveis via URLs raw do GitHub. Comumente usado para artefatos de teste visual, visualizações de dados e documentação gerada.

### Base Branch

Campo de configuração no safe output `create-pull-request` que especifica qual branch o pull request deve atingir. Padrão para `github.base_ref || github.ref_name` se não especificado. Útil para pull requests entre repositórios que atingem branches não padrão.

### Minimizar Comentário

Uma capacidade de safe output para ocultar ou minimizar comentários do GitHub sem exigir permissões de escrita. Quando minimizados, os comentários são classificados como SPAM. Requer IDs de nó GraphQL para identificar comentários. Útil para fluxos de trabalho de moderação de conteúdo.

### Adicionar Labels (`add-labels:`)

Uma capacidade de safe output para adicionar labels a issues ou pull requests. Suporta uma lista `allowed` para restringir quais labels podem ser aplicadas, e uma lista `blocked` usando padrões glob para rejeitar labels específicas independentemente da lista de permissões — fornecendo proteção contra injeção de prompt via manipulação de label. Aceita `target` (`"triggering"`, `"*"`, ou um número específico), um limite `max` (padrão: 3) e configuração entre repositórios via `target-repo`. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#add-labels-add-labels).

### Remover Labels (`remove-labels:`)

Uma capacidade de safe output para remover labels de issues ou pull requests. Suporta `allowed` para restringir quais labels podem ser removidas e `blocked` para impedir a remoção de labels que correspondam a padrões glob. Pula silenciosamente labels não presentes no destino. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#remove-labels-remove-labels).

### Atribuir ao Agente

Uma capacidade de safe output (`assign-to-agent:`) que atribui programaticamente o agente de codificação GitHub Copilot a issues ou pull requests existentes. Automatiza o fluxo de trabalho padrão do GitHub para delegar tarefas de implementação ao Copilot. Suporta criação de PR entre repositórios via `pull-request-repo` e seleção de modelo de agente via `model`. Veja [Atribuir ao Copilot](/gh-aw/reference/assign-to-copilot/).

### GH_AW_AGENT_TOKEN

Um nome de segredo de repositório "mágico" reconhecido que o GitHub Agentic Workflows usa automaticamente como um token de acesso pessoal de fallback para operações `assign-to-agent`. Quando definido, nenhuma referência explícita de `github-token:` é necessária no frontmatter do fluxo de trabalho — o token é injetado automaticamente. Necessário porque tokens de instalação do GitHub App são rejeitados pela API de atribuição do Copilot. A cadeia de fallback do token é: `assign-to-agent.github-token` → `safe-outputs.github-token` → `GH_AW_AGENT_TOKEN` → `GH_AW_GITHUB_TOKEN` → `GITHUB_TOKEN`. Veja [Atribuir ao Copilot](/gh-aw/reference/assign-to-copilot/).

### Outras Saídas Seguras (Safe Outputs) Personalizadas

Um mecanismo de extensão para safe outputs que permite integração com serviços de terceiros além das operações internas do GitHub. Definido sob `safe-outputs.jobs:`, os safe outputs personalizados separam operações de leitura e escrita: agentes usam ferramentas MCP somente leitura para consultas, enquanto jobs personalizados executam operações de escrita com acesso a segredos após a conclusão do agente. Suporta serviços como Slack, Notion, Jira ou qualquer API externa. Veja [Safe Outputs Personalizados](/gh-aw/reference/custom-safe-outputs/).

### Repositório de Disparo (`dispatch_repository`)

Um tipo de safe output experimental que dispara eventos `repository_dispatch` em repositórios externos para orquestração entre repositórios. Cada chave sob `safe-outputs.dispatch_repository:` define uma ferramenta de disparo nomeada exposta ao agente. Uma ferramenta requer um identificador de `workflow` (encaminhado em `client_payload` para roteamento), um `event_type` e ou um slug de `repository` estático ou uma lista `allowed_repositories`. Expressões do GitHub Actions (`${{ ... }}`) são suportadas em campos de repositório e são passadas sem validação de formato. No momento da compilação, o compilador emite um aviso: `Using experimental feature: dispatch_repository`. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#repository-dispatch-dispatch_repository).

### Actions de Safe Output

Um mecanismo para montar qualquer GitHub Action pública como uma ferramenta MCP chamável uma única vez dentro do job de safe-outputs consolidado. Definido sob `safe-outputs.actions:`, cada action é especificada com um campo `uses` (correspondente à sintaxe do GitHub Actions) e uma descrição opcional. No momento da compilação, `gh aw compile` busca o `action.yml` da action para resolver suas entradas e fixa a referência a um SHA específico. Diferente de [Safe Outputs Personalizados](#custom-safe-outputs) (jobs separados) e [Scripts de Safe Output](#safe-output-scripts) (JavaScript inline), as actions são executadas como passos dentro do job de safe-outputs com acesso total a segredos via `env:`. Útil para reutilizar actions de marketplace existentes como ferramentas de agente. Veja [Safe Outputs Personalizados](/gh-aw/reference/custom-safe-outputs/#github-action-wrappers-safe-outputsactions).

### Scripts de Safe Output

Manipuladores de script JavaScript inline leves definidos sob `safe-outputs.scripts:` que são executados dentro do loop do manipulador de job de safe-outputs consolidado. Diferente de [Safe Outputs Personalizados](#custom-safe-outputs) (`safe-outputs.jobs`), que criam um job do GitHub Actions separado por chamada de ferramenta, os scripts são executados em-processo sem sobrecarga de agendamento de job. Scripts não têm acesso direto a segredos do repositório, tornando-os adequados para processamento e log leves. Cada script declara `description`, `inputs` e um corpo `script`; o compilador encapsula o corpo e registra o manipulador como uma ferramenta MCP disponível para o agente. Veja [Safe Outputs Personalizados](/gh-aw/reference/custom-safe-outputs/#inline-script-handlers-safe-outputsscripts).

### Dependências de Safe Outputs (`safe-outputs.needs:`)

Uma opção de `safe-outputs` que estende as dependências do job `safe_outputs` consolidado com jobs de fluxo de trabalho personalizados. `safe-outputs.needs` é mesclado com dependências embutidas (`agent`, `activation`, `detection` opcional, `unlock` opcional) e deduplicado. Útil para injetar jobs de busca de credencial ou provisionamento de segredo dos quais o job de safe-outputs depende. Os valores devem referenciar jobs personalizados definidos na seção `jobs:` de nível superior; nomes de job embutidos são recusados no momento da compilação com um erro acionável. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#safe-outputs-dependencies-needs).

### Atribuir ao Usuário (Unassign from User)

Uma capacidade de safe output para remover atribuições de usuário de issues ou pull requests. Suporta uma lista `allowed` para restringir quais usuários podem ser desatribuídos e uma lista `blocked` usando padrões glob para impedir a desatribuição de usuários específicos independentemente da lista de permissões. Configurado via `unassign-from-user:` em `safe-outputs`.

### ID Temporário

Um identificador de escopo de fluxo de trabalho (formato: `aw_` seguido por 3-8 caracteres alfanuméricos, ex: `aw_abc1`) que permite que um agente de IA referencie um recurso antes que ele seja criado. Ferramentas de safe output que suportam IDs temporários — incluindo `create_issue`, `create_discussion` e `add_comment` — aceitam um campo `temporary_id`. Referências como `#aw_abc1` em operações subsequentes são resolvidas automaticamente para números de recurso reais durante a execução. Útil para criar recursos interligados em uma única execução de fluxo de trabalho. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/).

### Mesclar Pull Request (`merge-pull-request:`)

Uma capacidade experimental de safe output para mesclar pull requests após a aprovação de gates controlados por política. Valida status checks, aprovações necessárias, threads de revisão resolvidas, restrições de label e branch e capacidade de mesclagem do GitHub antes de aplicar a mesclagem. Suporta métodos `merge`, `squash` e `rebase` e destinos entre repositórios. Compilar um fluxo de trabalho com `merge-pull-request` emite um aviso de funcionalidade experimental. Veja [Especificação de Safe Outputs](/gh-aw/reference/safe-outputs-specification/#type-merge_pull_request).

### Fechar Pull Request (`close-pull-request:`)

Uma capacidade de safe output para fechar pull requests sem mesclar, com um comentário opcional. Suporta filtragem via `required-labels` e `required-title-prefix` para evitar fechamentos não intencionais. Aceita `target` para identificar o PR (`"triggering"`, `"*"`, ou um número específico), configuração entre repositórios via `target-repo` e um limite `max` de fechamentos. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#close-pull-request-close-pull-request).

### Atualizar Issue

Uma capacidade de safe output (`update-issue:`) para modificar issues existentes sem criar novas. Cada campo atualizável (`status`, `title`, `body`) deve ser explicitamente habilitado. As atualizações de corpo aceitam um campo `operation`: `append` (padrão), `prepend`, `replace` ou `replace-island` (atualiza uma seção específica delimitada por comentários HTML). Suporta atualizações de issue entre repositórios. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#issue-updates-update-issue).

### Atualizar Pull Request (`update-pull-request:`)

Uma capacidade de safe output para modificar o `title` ou `body` de um pull request. Cada campo deve ser explicitamente habilitado (`true` ou `false`). O campo `operation` controla como as alterações de corpo são aplicadas: `append` (padrão), `prepend` ou `replace`. Aceita `target` (`"triggering"`, `"*"`, ou um número específico) e atualizações entre repositórios via `target-repo`. Quando `target: "*"` é usado, o agente deve fornecer `pull_request_number` na saída da ferramenta. O campo opcional `update-branch: true` sincroniza o branch do PR com as últimas alterações do branch base antes de aplicar outras atualizações. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#pull-request-updates-update-pull-request).

### Arquivos Protegidos

Um mecanismo de segurança em safe outputs `create-pull-request` e `push-to-pull-request-branch` que impede que agentes de IA modifiquem arquivos sensíveis do repositório. Por padrão, protege manifestos de dependência (ex: `package.json`, `go.mod`), arquivos de fluxo de trabalho do GitHub Actions e arquivos de bloqueio. Configurado via `protected-files:` com três políticas: `blocked` (padrão — falha com erro), `allowed` (sem restrição) ou `fallback-to-issue` (cria uma issue de revisão para inspeção humana em vez de aplicar alterações). Também aceita um formato de objeto `{ policy, exclude }` para remover arquivos específicos ou prefixos de caminho do conjunto protegido padrão enquanto mantém a proteção ativa para os arquivos restantes. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#protected-files).

### Permitir Fluxos de Trabalho (`allow-workflows:`)

Um campo em safe outputs `create-pull-request` e `push-to-pull-request-branch` que adiciona `workflows: write` às permissões do token do GitHub App. Necessário quando `allowed-files:` aponta para caminhos em `.github/workflows/`, porque a permissão `workflows` é uma permissão exclusiva do GitHub App e não pode ser concedida via `GITHUB_TOKEN`. Requer que `safe-outputs.github-app` seja configurado — o compilador recusa `allow-workflows: true` sem um. Este design de opt-in mantém a permissão elevada visível e auditável na fonte do fluxo de trabalho. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#allowing-workflow-file-changes-with-allow-workflows).

### Eventos Permitidos (`allowed-events:`)

Um campo em safe outputs `submit-pull-request-review:` que restringe quais tipos de evento de revisão de PR o agente pode enviar. Aceita um array de `APPROVE`, `COMMENT` e `REQUEST_CHANGES`. Quando definido, o manipulador de safe-outputs recusa qualquer tipo de evento de revisão não listado, fornecendo aplicação em nível de infraestrutura independentemente do que o agente tenta enviar. Se omitido, todos os três tipos de evento são permitidos. Padrão preferencial para revisões de bot: `allowed-events: [COMMENT]`. Exemplo: `allowed-events: [COMMENT, REQUEST_CHANGES]` impede que o agente aprove PRs. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#submit-pr-review-submit-pull-request-review).

### Substituir Revisões Antigas (`supersede-older-reviews:`)

Um campo em safe outputs `submit-pull-request-review:` que descarta revisões `REQUEST_CHANGES` antigas do mesmo fluxo de trabalho após postar uma revisão de substituição. Quando `supersede-older-reviews: true` é definido, o manipulador de safe-output busca revisões recentes, identifica revisões de `REQUEST_CHANGES` anteriores enviadas pela mesma chamada de fluxo de trabalho e as descarta antes que a nova revisão entre em vigor. Este é um comportamento de melhor esforço — falhas de descarte não bloqueiam a nova revisão. Útil quando um fluxo de trabalho é configurado com `allowed-events: [REQUEST_CHANGES]` e execuções repetidas acumulariam revisões de bloqueio. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#submit-pr-review-submit-pull-request-review).

### Deduplicar por Título (`deduplicate-by-title:`)

Um campo de safe-output `create-issue` que descarta issues duplicadas antes da criação comparando títulos. Aceita `true` para correspondência exata (após normalização) ou um número inteiro `0`–`100` para correspondência difusa dentro da distância de edição de Levenshtein fornecida (ex: `1` permite diferenças de um caractere). A deduplicação é executada no momento da chamada da ferramenta MCP (dentro da execução) e no momento da aplicação (contra issues de repositório abertas e fechadas recentemente). Itens descartados são registrados no resumo do safe-output com o título correspondente, distância de edição e origem. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#issue-creation-create-issue).

### Campos Permitidos (`create-issue:`)

Um campo de configuração em safe outputs `create-issue:` que restringe quais campos personalizados do GitHub Project o agente pode definir ao criar issues. Aceita um array de nomes de campo (ex: `[Priority, Iteration]`). Quando definido, o manipulador de safe-outputs recusa qualquer tentativa de popular um campo não listado. Quando omitido, todos os campos de projeto são permitidos. Exemplo: `allowed-fields: [Priority, Iteration]`. Veja [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/#issue-creation-create-issue).

### Arquivos Permitidos

Uma allowlist exclusiva para safe outputs `create-pull-request` e `push-to-pull-request-branch`. Quando `allowed-files:` é definido como uma lista de padrões glob, **apenas** arquivos correspondentes a esses padrões podem ser modificados — todos os outros arquivos (incluindo arquivos de origem normais) são recusados. Esta é uma restrição, não uma exceção: listar `.github/workflows/*` não permite adicionalmente arquivos de origem normais; ele os bloqueia. Executado independentemente da política de [Arquivos Protegidos](#protected-files): ambas as verificações devem passar. Para modificar um arquivo protegido, ele deve corresponder a `allowed-files` e ser permitido por `protected-files` (ex: `protected-files: allowed`). Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#restricting-changes-to-specific-files-with-allowed-files).

### Prefixo de Branch (`branch-prefix:`)

Um campo opcional em safe outputs `create-pull-request` que prepende uma string fixa ao nome do branch especificado pelo agente ou gerado automaticamente. Útil quando as políticas de repositório exigem que os branches sigam convenções de nomenclatura (ex: `signed/` para fluxos de trabalho de commit assinado). O prefixo padrão é `signed/`. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/).

### Preservar Nome de Branch (`preserve-branch-name:`)

Uma opção em safe outputs `create-pull-request` que omite o sufixo de sal hexadecimal aleatório normalmente anexado ao nome do branch especificado pelo agente. Útil quando o repositório de destino impõe convenções de nomenclatura, como chaves Jira em maiúsculas (ex: `bugfix/BR-329-red` em vez de `bugfix/br-329-red-cde2a954`). Caracteres inválidos são sempre substituídos por segurança, e o uso de maiúsculas/minúsculas é sempre preservado independentemente desta configuração. Padrão para `false`. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/).

### Patch Máximo de Arquivos (`max-patch-files:`)

Um campo de safe-output `create-pull-request` que define o número máximo de arquivos únicos permitidos no patch de um único PR. Padrão para `100`. Fluxos de trabalho que regeneram grandes conjuntos de arquivos (ex: esquemas de API por pacote) podem aumentar este limite. Se o limite for excedido, a criação do PR falha com um erro acionável mostrando a contagem exata de arquivos e o campo a configurar. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/).

### Recriar Ref (`recreate-ref:`)

Uma opção em safe outputs `create-pull-request` que força a exclusão e recriação do branch remoto quando o nome do branch fornecido pelo agente já existe no remoto. Requer `preserve-branch-name: true`. O manipulador faz um force-push do HEAD local do agente para o ref remoto obsoleto, permitindo a reutilização de branches reutilizáveis de longa duração cujo PR anterior foi mesclado. Sem `recreate-ref: true`, o comportamento padrão é fazer fallback (por exemplo, abrir uma issue quando `fallback-as-issue: true`) em vez de sobrescrever o ref remoto. Padrão para `false`. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/).

### Criar Comentário de Revisão de Pull Request (`create-pull-request-review-comment:`)

Uma capacidade de safe output para postar comentários de revisão inline em linhas específicas no diff de um pull request. Suporta comentários de linha única e multilinha com `side` configurável (`LEFT` ou `RIGHT`). Quando `target: "*"` é definido, o agente deve fornecer `pull_request_number` na chamada da ferramenta. Para cenários entre repositórios, o agente também pode fornecer `repo` (no formato `owner/repo`) correspondendo a `target-repo` ou `allowed-repos`. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#pr-review-comments-create-pull-request-review-comment).

### Responder a Comentário de Revisão de PR (`reply-to-pull-request-review-comment:`)

Uma capacidade de safe output para responder a comentários de revisão existentes em pull requests. Permite que o agente de IA responda a feedback do revisor, responda a perguntas ou reconheça comentários de revisão inline por seu ID de comentário numérico. Suporta um campo opcional `footer` (`always`, `none` ou `if-body`) para controlar a atribuição da IA. Configurado via `reply-to-pull-request-review-comment:` em `safe-outputs`. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#reply-to-pr-review-comment-reply-to-pull-request-review-comment).

### Resolver Thread de Revisão de PR (`resolve-pull-request-review-thread:`)

Uma capacidade de safe output para marcar threads de revisão de PR do GitHub como resolvidas. Usa a mutação GraphQL `resolveReviewThread` do GitHub, exigindo o ID de nó da thread. Permite que agentes de IA limpem comentários de revisão abordados após implementar feedback. Aceita as mesmas opções `target`, `target-repo` e `allowed-repos` que outros safe outputs de pull-request. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#resolve-pr-review-thread-resolve-pull-request-review-thread).

### Relatar Incompleto (`report_incomplete`)

Um sinal de safe output obrigatório que os agentes emitem quando uma tarefa não pode ser concluída devido a falhas de infraestrutura ou de ferramenta — por exemplo, uma falha de servidor MCP, autenticação ausente ou um repositório inacessível. Diferente de `noop` (que sinaliza que nenhuma ação era necessária), `report_incomplete` indica uma falha ativa que impediu a execução da tarefa. O manipulador de safe-outputs ativa o tratamento de falhas independentemente do código de saída do agente. Aceita um campo obrigatório `reason` (máximo 1024 caracteres) e um campo `details` opcional para contexto de diagnóstico estendido.

### Definir Tipo de Issue (`set-issue-type:`)

Uma capacidade de safe output para definir ou limpar o tipo de issue do GitHub em issues existentes. O agente chama `set_issue_type` para atribuir um tipo nomeado (ex: `Bug`, `Feature`) a uma issue. Uma lista `allowed` restringe quais tipos o agente pode definir; omiti-la permite qualquer tipo. Passar uma string vazia limpa o tipo atual. Suporta direcionamento entre repositórios via `target-repo` e `allowed-repos`. Configurado via `set-issue-type:` em `safe-outputs`.

### Definir Campo de Issue (`set-issue-field:`)

Uma capacidade de safe output para definir um valor de campo de issue em issues existentes. O agente chama `set_issue_field` com `value` e ou `field_name` (para descoberta por label de campo) ou `field_node_id` (para pular a descoberta). Nomes de campo desconhecidos retornam erros acionáveis listando campos disponíveis e sugerindo IDs explícitos. Suporta restrições opcionais de `allowed-fields` (incluindo o curinga `["*"]`) e direcionamento entre repositórios via `target-repo` e `allowed-repos`. Configurado via `set-issue-field:` em `safe-outputs`.

### Campos de Safe-Output Parametrizados

Um padrão para reutilização `workflow_call` onde a política de safe-output e campos de lista aceitam strings de expressão do GitHub Actions (ex: `${{ inputs.protected-files-policy }}`) além de valores literais. No momento da compilação, o compilador detecta a forma `${{...}}` e a passa sem alterações; o GitHub Actions avalia a expressão em tempo de execução antes que o manipulador seja executado. Campos de política com valor de enum como `protected-files` e `patch-format` validam valores literais no momento da compilação, mas adiam valores baseados em expressão para o tempo de execução (falhando ao fechar em entradas não reconhecidas). Campos de valor de lista como `labels`, `allowed-repos` e `allowed-base-branches` aceitam uma array YAML ou uma string de expressão única. Isso permite que um único fluxo de trabalho reutilizável atenda chamadores com diferentes configurações de restrição sem duplicar arquivos. Veja [Safe Outputs (Pull Requests)](/gh-aw/reference/safe-outputs-pull-requests/#parameterizing-policy-fields-in-reusable-workflows).

## Componentes de Fluxo de Trabalho

### Token de Ativação (`on.github-token:`, `on.github-app:`)

Token do GitHub personalizado ou GitHub App usado pelo job de ativação para postar reações e comentários de status no item disparador. Configurado via `github-token:` (para um PAT ou expressão de token) ou `github-app:` (para emitir um token de instalação de curta duração) dentro da seção `on:`. Afeta apenas o job de ativação — tokens do job do agente são configurados separadamente via `tools.github.github-token` ou `safe-outputs.github-app`. Veja [Referência de Autenticação](/gh-aw/reference/auth/).

### BYOK (Bring Your Own Key)

Um modo de motor Copilot que roteia solicitações de IA para um provedor LLM externo (como OpenAI, Anthropic ou uma instância auto-hospedada de Ollama/vLLM) em vez do backend padrão do GitHub Copilot. Ativado definindo `COPILOT_PROVIDER_BASE_URL` em `engine.env`. As três variáveis de credencial BYOK (`COPILOT_PROVIDER_BASE_URL`, `COPILOT_PROVIDER_API_KEY`, `COPILOT_PROVIDER_BEARER_TOKEN`) aceitam referências `${{ secrets.* }}` sob modo estrito e nunca são expostas ao container do agente. Use `COPILOT_MODEL` para especificar o modelo de destino. Veja [Referência de Motores de IA](/gh-aw/reference/engines/#copilot-bring-your-own-key-byok-mode).

### Cron Schedule

Um formato de trigger baseado em tempo. Use sintaxe curta como `daily` ou `weekly on monday` (recomendado com dispersão de tempo automática) ou expressões cron padrão para horários fixos. Itens de agenda baseados em cron aceitam um campo `timezone` opcional com qualquer [identificador de fuso horário IANA](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (ex: `America/New_York`) para interpretar a expressão em um fuso horário específico em vez de UTC. Veja também [Agendamento Difuso](#fuzzy-scheduling) e [Dispersão de Tempo](#time-scattering).

### Identificadores de Ecossistema

Referências abreviadas nomeadas para conjuntos de domínios predefinidos usados em `network.allowed` e `safe-outputs.allowed-domains`. Em vez de listar nomes de domínio individuais, identificadores de ecossistema expandem para conjuntos curados para um runtime de linguagem ou categoria de serviço. Identificadores comuns: `python` (PyPI/pip), `node` (npm), `go` (proxy.golang.org), `github` (domínios do GitHub), `dev-tools` (serviços de CI/CD como Codecov, Snyk, Shields.io), `local` (endereços de loopback) e `default-safe-outputs` (um conjunto composto combinando `defaults` + `dev-tools` + `github` + `local`, recomendado como base para `safe-outputs.allowed-domains`). Veja [Referência de Permissões de Rede](/gh-aw/reference/network/#ecosystem-identifiers).

### Engine

O sistema de IA que alimenta o fluxo de trabalho agentic - essencialmente "qual IA usar" para executar as instruções do fluxo de trabalho. O GitHub Agentic Workflows suporta sete motores: **Copilot** (padrão), **Claude**, **Codex**, **Gemini**, **Crush** (experimental), **OpenCode** (experimental) e **Pi** (experimental). Defina `engine:` no frontmatter para escolher; omita-o para usar o Copilot. Veja [Referência de Motores de IA](/gh-aw/reference/engines/).

### Endpoint de API Empresarial (`api-target`)

Um campo de configuração de `engine` especificando um hostname de endpoint de API personalizado para implantações do GitHub Enterprise Cloud (GHEC) ou GitHub Enterprise Server (GHES). Quando definido, o compilador adiciona automaticamente o domínio da API e o hostname base à lista `--allow-domains` do firewall AWF e à variável de ambiente `GH_AW_ALLOWED_DOMAINS`, eliminando a necessidade de configuração de rede manual após cada recompilação. O valor deve ser apenas um hostname — sem protocolo ou caminho (ex: `api.acme.ghe.com`). Veja [Referência de Motores](/gh-aw/reference/engines/#enterprise-api-endpoint-api-target).

```aw wrap
engine:
  id: copilot
  api-target: api.acme.ghe.com
```

### Definição de Motor Inline

Um formato de configuração de motor que especifica um adaptador de runtime e configurações de provedor opcionais diretamente no frontmatter do fluxo de trabalho, sem exigir uma entrada de catálogo nomeada. Usa um objeto `runtime` (com `id` e versão opcional) para identificar o adaptador e um objeto `provider` opcional para seleção de modelo, autenticação e formatação de solicitação. Útil para conectar a backends de IA auto-hospedados ou de terceiros.

```aw wrap
engine:
  runtime:
    id: codex
  provider:
    id: azure-openai
    model: gpt-4o
    auth:
      strategy: oauth-client-credentials
      token-url: https://auth.example.com/oauth/token
      client-id: AZURE_CLIENT_ID
      client-secret: AZURE_CLIENT_SECRET
    request:
      path-template: /openai/deployments/{model}/chat/completions
      query:
        api-version: "2024-10-01-preview"
```

Veja [Referência de Motores](/gh-aw/reference/engines/).

### Experimentos (`experiments:`)

Uma seção de frontmatter que habilita testes A/B de variantes de prompt de fluxo de trabalho entre execuções sucessivas. Cada chave no mapa `experiments:` nomeia um experimento; o valor é ou uma array simples de strings de variante ou um objeto rico com campos adicionais (`variants`, `description`, `hypothesis`, `metric`, `weight`, `min_samples`, `start_date`, `end_date`). Em tempo de execução, o job de ativação seleciona uma variante por experimento usando um contador round-robin balanceado e expõe a seleção como `${{ experiments.<name> }}` para uso em qualquer lugar no corpo do fluxo de trabalho.

O estado do experimento é persistido em branches git `experiments/<name>` dedicados no repositório do fluxo de trabalho. Use `gh aw experiments list` e `gh aw experiments analyze` para inspecionar a distribuição de variantes e a prontidão estatística (teste de qui-quadrado de equilíbrio, correção de Bonferroni, recomendação EXTEND / READY_FOR_ANALYSIS). Veja [Experimentos A/B](/gh-aw/practices/experiments/) e a [Especificação de Experimentos A/B](/gh-aw/practices/experiments-specification/).

```aw wrap
experiments:
  prompt_style: [concise, detailed]
---
Resuma esta issue de uma forma **${{ experiments.prompt_style }}**.
```

### Feature Flags (`features:`)

Uma seção de frontmatter que habilita comportamentos experimentais ou opcionais do compilador e do runtime como pares chave-valor. As feature flags fornecem acesso controlado a novos recursos antes que se tornem padrões ou sejam totalmente estabilizados. Flags comuns incluem `action-mode` (controla como as referências de ação personalizadas são compiladas), `copilot-requests` (habilita autenticação de token do GitHub Actions para Copilot; atualmente em **visualização privada** — não funcionará a menos que sua conta tenha sido integrada), `mcp-gateway` (habilita o proxy de gateway MCP), `integrity-reactions` (habilita promoção e demolição de integridade baseada em reação), `cli-proxy` (habilita modo de proxy CLI para aplicação de integridade no limite da rede) e `awf-diagnostic-logs` (habilita a coleta de diagnósticos operacionais do Docker AWF em caso de falha). `byok-copilot` está obsoleto porque o comportamento Copilot BYOK agora é o padrão para `engine: copilot`. Veja [Referência de Frontmatter](/gh-aw/reference/frontmatter/#feature-flags-features).

### Agendamento Difuso (Fuzzy Scheduling)

Sintaxe de agenda de linguagem natural que distribui automaticamente os horários de execução do fluxo de trabalho para evitar picos de carga. Em vez de especificar horários exatos com expressões cron, agendas difusas como `daily`, `weekly` ou `daily on weekdays` são convertidas pelo compilador em expressões cron determinísticas, porém dispersas. O compilador adiciona automaticamente o trigger `workflow_dispatch:` para execuções manuais. Exemplo: `schedule: daily on weekdays` compila para algo como `43 5 * * 1-5` com horários de execução variados entre diferentes fluxos de trabalho.

### Importações

Componentes de fluxo de trabalho reutilizáveis compartilhados entre múltiplos fluxos de trabalho. Especificados no campo `imports:`, podem incluir configurações de ferramenta, instruções comuns ou diretrizes de segurança. Arquivos compartilhados sem um campo `on:` são validados, mas não compilados no GitHub Actions — eles são apenas importáveis por outros fluxos de trabalho.

As importações suportam uma forma parametrizada usando a sintaxe `uses`/`with` quando o arquivo compartilhado declara um `import-schema`. O compilador valida os valores passados, substitui-os no frontmatter e no corpo do arquivo compartilhado antes do processamento. Veja [Referência de Importações](/gh-aw/reference/imports/).

### Passos Pré-Agente (`pre-agent-steps:`)

Passos injetados no job do agente após o download dos artefatos e antes da execução do motor. Definidos no campo de frontmatter `pre-agent-steps:` e componíveis via importações — passos pré-agente importados são prependidos aos passos do fluxo de trabalho principal na ordem de importação. Útil para tarefas de configuração, como instalar dependências ou configurar o ambiente antes que o motor de IA seja executado. Veja [Referência de Importações](/gh-aw/reference/imports/).

### Passos Pós-Execução (`post-steps:`)

Passos injetados no job do agente após o motor finalizar a execução. Definidos no campo de frontmatter `post-steps:` e componíveis via importações — passos pós-execução importados são anexados após os passos pós-execução do fluxo de trabalho principal na ordem de importação. Útil para limpeza, relatórios ou publicação de artefatos após a conclusão do motor de IA. Veja [Referência de Importações](/gh-aw/reference/imports/).

### Esquema de Importação (`import-schema`)

Um contrato de parâmetro tipado declarado em um arquivo de fluxo de trabalho compartilhado que permite aos chamadores passar valores via sintaxe `uses`/`with`. O compilador valida os valores `with` de cada chamador em relação ao esquema e os substitui no frontmatter e no corpo do arquivo compartilhado antes do processamento. Suporta campos tipados com padrões opcionais; campos obrigatórios sem padrões causam um erro de tempo de compilação se omitidos. Veja [Referência de Importações](/gh-aw/reference/imports/#import-schema-import-schema).

### Configurações do Gateway MCP (`engine.mcp`)

`engine.mcp` é o subconjunto da configuração `engine:` que controla o comportamento do gateway MCP — especificamente `tool-timeout` e `session-timeout`. Arquivos de fluxo de trabalho compartilhados podem exportar apenas essas configurações (sem especificar um identificador de motor), permitindo que os importadores herdem a configuração de timeout do MCP sem acoplar um componente compartilhado a um motor específico. As configurações `engine.mcp` do próprio fluxo de trabalho importador têm precedência; entre as importações, a estratégia primeiro-a-vencer é aplicada. Veja [Referência de Importações — Importando Configurações de Gateway MCP](/gh-aw/reference/imports/#importing-mcp-gateway-settings).

### Runtime Import (`{{#runtime-import}}`)

Uma diretiva em nível de corpo que injeta o conteúdo de texto de outro arquivo em um ponto específico no markdown do fluxo de trabalho. Diferente do campo `imports:` do frontmatter (que mescla a configuração), `{{#runtime-import filepath}}` une texto markdown bruto — útil para compartilhar trechos de prompt reutilizáveis, instruções de tom ou material de referência entre fluxos de trabalho. Use `{{#runtime-import? filepath}}` para uma inclusão opcional que pula silenciosamente um arquivo ausente. Os caminhos são resolvidos dentro da pasta `.github` com ou sem o prefixo `.github/`. Veja [Importações de Runtime](/gh-aw/reference/templating/#runtime-imports).

### Emoji (`emoji:`)

Um campo de frontmatter opcional que anexa um emoji para representar o fluxo de trabalho visualmente em listagens e superfícies de interface. Aceita um único caractere de emoji (ex: `"🤖"`). Veja [Referência de Frontmatter](/gh-aw/reference/frontmatter/).

### Atalho de Trigger de Label

Uma sintaxe compacta para triggers baseados em label: `on: issue labeled bug` ou `on: pull_request labeled needs-review`. O compilador expande o atalho para a sintaxe de trigger padrão do GitHub Actions e inclui automaticamente um trigger `workflow_dispatch` com um parâmetro `inputs.item_number`, permitindo o disparo manual para uma issue ou pull request específica. Suportado para eventos `issue`, `pull_request` e `discussion`. Veja [Padrões de LabelOps](/gh-aw/patterns/label-ops/).

### Labels

Metadados de fluxo de trabalho opcionais para categorização e organização. Permite filtrar fluxos de trabalho na CLI usando a flag `--label`.

### Alias de Modelo

Um nome curto amigável para humanos (como `sonnet` ou `mini`) que o gh-aw resolve para o melhor modelo concreto disponível no momento da compilação. Aliases são definidos como listas ordenadas de padrões glob com escopo de provedor; o primeiro padrão que corresponde a um modelo disponível vence. Meta-aliases referenciam outros aliases e são resolvidos recursivamente. Aliases de fornecedor embutidos e meta-aliases estão listados na [Referência de Aliases e Multiplicadores de Modelo](/gh-aw/reference/model-tables/). Aliases personalizados podem ser definidos no frontmatter do fluxo de trabalho usando a [Especificação de Formato de Alias de Modelo](/gh-aw/reference/model-alias-specification/).

### Orçamento de Effective Tokens (`max-effective-tokens`)

Um campo de frontmatter de nível superior que limita o orçamento total de effective-token (ET) que o proxy AWF gastará em uma única execução de fluxo de trabalho. Effective tokens são ponderados por multiplicadores de modelo e são o proxy de custo primário para o Copilot. Aplica-se a todos os motores e mapeia para `apiProxy.maxEffectiveTokens` no arquivo de bloqueio compilado. O padrão é `25000000` quando omitido. Aceita um número inteiro ou uma expressão do GitHub Actions que é resolvida para um número inteiro no tempo de execução. Exemplo:

```aw wrap
max-effective-tokens: 5000000
```

Veja [Especificação de Effective Tokens](/gh-aw/reference/effective-tokens-specification/) e [Gerenciamento de Custos](/gh-aw/reference/cost-management/).

### Máximo de Execuções (`max-runs`)

Um campo de frontmatter de nível superior que limita o número de vezes que o proxy AWF invocará o motor de IA em uma única execução de fluxo de trabalho. Aplica-se a todos os motores e mapeia para `apiProxy.maxRuns` no arquivo de bloqueio compilado. Substitui o campo obsoleto `engine.max-runs`. O padrão é `500` quando omitido. Aceita um número inteiro ou uma expressão do GitHub Actions que é resolvida para um número inteiro no tempo de execução. Exemplo:

```aw wrap
max-runs: 10
```

Veja [Referência de Motores](/gh-aw/reference/engines/).

### Permissões de Rede

Controles sobre domínios e serviços externos que um fluxo de trabalho pode acessar. Configurado via seção `network:` com opções: `defaults` (infraestrutura comum), listas de permissão personalizadas ou `{}` (sem acesso).

### Observabilidade (`observability.otlp`)

Um campo de frontmatter que habilita a exportação de rastreamento OpenTelemetry
de execuções de fluxo de trabalho. Suporta exportação OTLP de endpoint único e
endpoint múltiplo com cabeçalhos opcionais.

Veja [OpenTelemetry](/gh-aw/reference/open-telemetry/) para
detalhes completos de configuração, variáveis de runtime e
semântica de span.

### OTLP If-Missing (`observability.otlp.if-missing`)

Controla o comportamento quando os valores de endpoint ou cabeçalho OTLP são resolvidos para vazio no tempo de execução. Aceita `error` (padrão — falha na inicialização do fluxo de trabalho), `warn` (registra um aviso e pula a configuração OTLP do gateway MCP) ou `ignore` (pula silenciosamente a configuração OTLP do gateway MCP sem aviso). Útil em importações compartilhadas onde segredos OTLP podem estar ausentes em alguns repositórios — defina como `ignore` para tornar a observabilidade opcional sem quebrar fluxos de trabalho que carecem dos segredos. Veja [Referência de OpenTelemetry](/gh-aw/reference/open-telemetry/#fields).

### Passos Pré-Agente (`jobs.<job-id>.pre-steps`)

Passos injetados em uma posição de ciclo de vida específica dentro da sequência de passos de um job personalizado ou embutido: após o passo de configuração gerado pelo compilador e antes do primeiro checkout ou `steps` regulares. Definido sob `jobs.<job-id>.pre-steps` no frontmatter do fluxo de trabalho. Para jobs embutidos (`activation`, `pre_activation`), os pré-passos são inseridos após o passo `setup` e antes do primeiro passo `actions/checkout`. Quando tanto um fluxo de trabalho principal quanto um fluxo de trabalho importado definem `pre-steps` para o mesmo job, os pré-passos importados são executados primeiro. Isso é distinto do campo de nível superior `pre-steps`, que injeta passos apenas no job do agente. Veja [Jobs Personalizados](/gh-aw/reference/frontmatter/#custom-jobs-jobs).

### Dependências de Pré-Ativação (`on.needs:`)

Um campo de frontmatter que declara jobs personalizados dos quais os jobs embutidos `pre_activation` e `activation` dependem. Use isso quando credenciais ou segredos devem ser buscados por um job personalizado antes da ativação ser executada — por exemplo, quando tokens `on.github-app` vêm de um job de gerenciamento de segredos. Os valores devem referenciar jobs personalizados definidos na seção `jobs:` de nível superior; nomes de job embutidos são recusados no momento da compilação. Veja [Referência de Triggers](/gh-aw/reference/triggers/).

### Stop After

Um campo de configuração de fluxo de trabalho (`stop-after:`) que evita automaticamente novas execuções após um limite de tempo especificado. Aceita datas absolutas (`YYYY-MM-DD`, ISO 8601) ou deltas de tempo relativos (`+48h`, `+7d`). A granularidade mínima é de horas. Útil para períodos de teste, funcionalidades experimentais e agendas com controle de custos. Recompile com `gh aw compile --refresh-stop-time` para redefinir o prazo. Veja [Efêmeros](/gh-aw/reference/ephemerals/).

### Trigger `deployment_status`

Um trigger do GitHub Actions que dispara quando uma implantação externa muda de estado. Os estados suportados são `error`, `failure`, `pending`, `queued`, `in_progress`, `success`, `inactive` e `waiting`. O compilador gh-aw aceita um filtro `state:` opcional na definição do trigger e sintetiza uma condição `if:` de nível de job para que o agente seja executado apenas para os estados especificados. Um atalho de linguagem natural também é suportado — `on: "deployment failed"` expande para `deployment_status` com `state: [failure]`. Veja [Referência de Frontmatter](/gh-aw/reference/frontmatter/).

```aw wrap
on:
  deployment_status:
    state: [error, failure]
```

### Triggers

Eventos que fazem com que um fluxo de trabalho seja executado, definidos na seção `on:` do frontmatter. Inclui eventos de issue, pull requests, agendas, execuções manuais e comandos slash.

### Pular Associações de Autor (`on.skip-author-associations`)

Um mecanismo de gating de pré-ativação que pula a execução do fluxo de trabalho quando o autor do evento de disparo tem um valor específico de `author_association` (como `contributor`, `first_time_contributor` ou `none`). Configurado por evento no campo `on.skip-author-associations`. Compila para uma expressão `if` de nível de job — sem custo de passo de script de pré-ativação para execuções puladas. Os valores não distinguem maiúsculas de minúsculas no frontmatter e aceitam uma única string ou array de strings por chave de evento. Veja [Referência de Triggers](/gh-aw/reference/triggers/).

### Arquivo de Trigger

Um fluxo de trabalho do GitHub Actions simples (`.yml`) que separa as definições de trigger da lógica do fluxo de trabalho agentic. Chama um ponto de entrada `workflow_call` de um orquestrador compilado em resposta a qualquer evento do GitHub (issues, pushes, labels, despacho manual). Desacopla as alterações de trigger do ciclo de compilação — atualizar quando um orquestrador é executado requer editar apenas o arquivo de trigger, não recompilar o fluxo de trabalho agentic.

Os arquivos de trigger podem viver no **mesmo repositório** que o orquestrador ou em um **repositório diferente** (cross-repo `workflow_call`). O uso entre repositórios requer que o repositório do chamador seja público, interno ou tenha concedido acesso explícito a Actions. Ao usar `secrets: inherit`, os segredos do chamador são passados — incluindo `COPILOT_GITHUB_TOKEN`, que deve ser configurado no repositório do chamador. Veja [CentralRepoOps](/gh-aw/patterns/central-repo-ops/).

### Limite de Taxa do Usuário (`user-rate-limit`)

Um campo de frontmatter que impede que usuários individuais disparem um fluxo de trabalho com muita frequência. Configurado com `max-runs-per-window` (máximo de execuções por janela de tempo, 1–10), um `window` opcional em minutos (padrão 60, máximo 180), uma lista de `events` opcional para restringir quais tipos de trigger contam e uma lista `ignored-roles` opcional de funções isentas (padrão: `[admin, maintain, write]`). O job de pré-ativação verifica as execuções recentes e cancela a execução atual se o limite for excedido. Exemplo:

```aw wrap
user-rate-limit:
  max-runs-per-window: 5
  window: 60
  ignored-roles: []
```

Veja [Controles de Limitação de Taxa](/gh-aw/reference/rate-limiting-controls/).

### Alias de Taxa (Rate Limit)

Um alias legado para `user-rate-limit`. Prefira `user-rate-limit` com `max-runs-per-window`.

### Modo Estrito

Modo de validação de segurança aprimorado aplicando verificações de segurança adicionais e melhores práticas. Habilitado via `strict: true` no frontmatter ou flag `--strict` ao compilar.

### Timeout

Duração máxima que um fluxo de trabalho pode ser executado antes do cancelamento automático. Configurado via `timeout-minutes:` no frontmatter. O passo de execução do agente usa o padrão de 20 minutos; outros jobs (jobs personalizados, jobs de safe-output) usam o padrão da plataforma GitHub Actions de 360 minutos, a menos que definido explicitamente. Runners personalizados suportam timeouts mais longos além do limite do runner hospedado no GitHub.

### Toolsets

Coleções predefinidas de ferramentas MCP relacionadas habilitadas juntas. Usado com o servidor MCP do GitHub para agrupar capacidades como `repos`, `issues` e `pull_requests`. Configurado no campo `toolsets:`.

### Tracker ID

Um identificador único que permite monitoramento e coordenação externos sem acoplamento bidirecional. Fluxos de trabalho orquestradores usam IDs de rastreador para correlacionar execuções de trabalhadores e descobrir saídas enquanto os trabalhadores operam de forma independente.

### Inputs de Fluxo de Trabalho

Parâmetros fornecidos ao disparar manualmente um fluxo de trabalho com `workflow_dispatch`. Definidos na seção `on.workflow_dispatch.inputs` com tipo, descrição, valor padrão e status de obrigatoriedade.

## Padrões Operacionais

Padrões operacionais (sufixados com "-Ops") são arquiteturas de fluxo de trabalho estabelecidas para cenários de automação comuns. Cada padrão aborda casos de uso específicos com triggers, ferramentas e safe outputs recomendados.

### AgenticOps

Padrão de observabilidade em todo o repositório onde um fluxo de trabalho agendado inspeciona outros fluxos de trabalho agentic, classifica comportamentos notáveis e publica um relatório estruturado. Quando detecta falhas repetidas, consumo anormal de tokens ou outros padrões não saudáveis, escala as descobertas para issues para acompanhamento. Cria um registro operacional durável em vez de depender de inspeção ad hoc de execuções individuais. Veja [MonitorOps](/gh-aw/patterns/monitor-ops/).

### BatchOps

Padrão para processar grandes volumes de itens de trabalho de forma eficiente usando paginação em blocos (chunked), fan-out de matriz ou sub-agrupamento com reconhecimento de limite de taxa. BatchOps divide um backlog em blocos paralelos ou sequenciais, lida com falhas parciais com `fail-fast: false` e agrega resultados em um relatório consolidado. Use quando os itens são independentes e a ordem não importa. Veja [BatchOps](/gh-aw/patterns/batch-ops/).

### CentralRepoOps

Uma variante de implantação [MultiRepoOps](#multirepoops) onde um único repositório privado atua como plano de controle para coordenar operações em larga escala em muitos repositórios. Permite rollouts consistentes, atualizações de política e rastreamento centralizado usando safe outputs entre repositórios e autenticação segura. Veja [CentralRepoOps](/gh-aw/patterns/central-repo-ops/).

### CorrectionOps

Padrão para melhorar fluxos de trabalho a partir de correções humanas confiáveis sem treinar novamente o modelo subjacente. CorrectionOps armazena predições, compara-as com decisões humanas autoritativas posteriores e usa diffs agrupados para atualizar instruções, roteamento, limites ou política de rollout. Veja [CorrectionOps](/gh-aw/experimental/correction-ops/).

### ChatOps

Automação interativa acionada por comandos slash (`/review`, `/deploy`) em issues e pull requests, permitindo automação com intervenção humana onde desenvolvedores invocam assistência de IA sob demanda. Veja [ChatOps](/gh-aw/patterns/chat-ops/).

### DailyOps

Fluxos de trabalho agendados para melhorias diárias incrementais, automatizando o progresso em direção a grandes objetivos por meio de mudanças pequenas e gerenciáveis em agendas de dias úteis. Veja [DailyOps](/gh-aw/patterns/daily-ops/).

### DataOps

Padrão híbrido que combina extração de dados determinística em `steps:` com análise agentic no corpo do fluxo de trabalho. Comandos shell buscam e estruturam dados, então o agente de IA interpreta os resultados e produz insights. Veja [DeterministicOps](/gh-aw/patterns/deterministic-ops/).

### DispatchOps

Execução manual de fluxo de trabalho via UI ou CLI do GitHub Actions usando o trigger `workflow_dispatch`. Permite tarefas sob demanda, testes e fluxos de trabalho que exigem julgamento humano sobre o momento. Fluxos de trabalho podem aceitar parâmetros de entrada personalizados. Veja [DispatchOps](/gh-aw/patterns/dispatch-ops/).

### IssueOps

Gerenciamento automatizado de issues que analisa, categoriza e responde a issues quando criadas. Usa triggers de evento de issue com safe outputs para triagem automatizada segura sem exigir permissões de escrita para o job de IA. Veja [Exemplos de IssueOps](/gh-aw/patterns/issue-ops/).

### LabelOps

Fluxos de trabalho acionados por alterações de label em issues e pull requests. Usa labels como triggers, metadados e marcadores de estado com filtragem para adições ou remoções de labels específicas. Veja [Exemplos de LabelOps](/gh-aw/patterns/label-ops/).

### MemoryOps

Fluxos de trabalho com estado que persistem dados entre execuções usando `cache-memory` e `repo-memory`, permitindo rastreamento de progresso, retomada após interrupções e processamento incremental para evitar throttling de API. Veja [MemoryOps](/gh-aw/guides/memory-ops/).

### MultiRepoOps

Coordenação entre repositórios estendendo padrões de automação entre múltiplos repositórios. Usa autenticação segura e safe outputs entre repositórios para sincronizar funcionalidades, centralizar rastreamento e aplicar políticas em toda a organização. Veja [MultiRepoOps](/gh-aw/patterns/multi-repo-ops/).

### ProjectOps

Gerenciamento de board de Projetos do GitHub impulsionado por IA, automatizando a triagem de issue, roteamento e atualizações de campo. Analisa o conteúdo de issue/PR para tomar decisões inteligentes sobre atribuição de projeto, status, prioridade e campos personalizados usando o safe output `update-project`. Veja [ProjectOps](/gh-aw/patterns/project-ops/).

### SideRepoOps

Padrão de desenvolvimento onde fluxos de trabalho executam a partir de um repositório "side" separado direcionado à sua base de código principal. Mantém issues, comentários e execuções de fluxo de trabalho gerados por IA isolados do repositório principal para uma separação mais limpa entre a infraestrutura de automação e o código de produção. Veja [SideRepoOps](/gh-aw/patterns/side-repo-ops/).

### SpecOps

Mantendo e propagando especificações estilo W3C usando o agente `w3c-specification-writer`. Cria especificações formais com palavras-chave RFC 2119 e sincroniza automaticamente alterações para implementações consumidoras. Veja [SpecOps](/gh-aw/patterns/spec-ops/).

### ResearchPlanAssignOps

Estratégia de melhoria de código impulsionada por IA com quatro fases: agente de pesquisa investiga e publica descobertas, desenvolvedor revisa e invoca agente de planejamento para criar issues acionáveis, desenvolvedor atribui issues aprovadas ao Copilot para implementação automatizada, então revisa e mescla PRs. Mantém os desenvolvedores no controle com pontos de decisão claros em cada transição. Veja [ResearchPlanAssignOps](/gh-aw/patterns/research-plan-assign-ops/).

### TrialOps

Padrão de teste e validação executando fluxos de trabalho em repositórios de teste isolados antes da implantação em produção. Cria repositórios privados temporários onde fluxos de trabalho são executados com segurança, capturando safe outputs sem modificar sua base de código real. Veja [TrialOps](/gh-aw/experimental/trial-ops/).

### WorkQueueOps

Padrão para processar incrementalmente um backlog de itens de trabalho usando um backend de fila durável — checklists de issue, sub-issues, [cache-memory](#cache-memory) ou Discussões do GitHub. Cada execução continua de onde a última parou, tornando-a resiliente a interrupções e limites de taxa. Itens devem ser idempotentes e processáveis independentemente. Veja [WorkQueueOps](/gh-aw/patterns/workqueue-ops/).

## Documentação Relacionada

Para documentação detalhada sobre tópicos específicos, veja:

- [Referência de Frontmatter](/gh-aw/reference/frontmatter/)
- [Referência de Ferramentas](/gh-aw/reference/tools/)
- [Referência de Scripts MCP](/gh-aw/reference/mcp-scripts/)
- [Referência de Safe Outputs](/gh-aw/reference/safe-outputs/)
- [Guia de Uso de MCPs](/gh-aw/guides/mcps/)
- [Guia de Segurança](/gh-aw/introduction/architecture/)
- [Referência de Motores de IA](/gh-aw/reference/engines/)
