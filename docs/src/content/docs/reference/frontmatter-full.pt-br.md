---
title: Referência Completa de Frontmatter
description: Referência completa baseada em esquema JSON para todas as opções de configuração de frontmatter do GitHub Agentic Workflows com exemplos YAML.
sidebar:
  order: 201
---

Este documento fornece uma referência abrangente para todas as opções de configuração de frontmatter disponíveis no GitHub Agentic Workflows. Os exemplos abaixo são gerados a partir do Esquema JSON e incluem comentários inline descrevendo cada campo.

> [!NOTE]
> Esta documentação é gerada automaticamente a partir do Esquema JSON. Para um guia mais amigável, veja [Frontmatter](/gh-aw/reference/frontmatter/).

## Descrição do Esquema

Esquema JSON para validar a configuração de frontmatter do fluxo de trabalho agentic

## Referência Completa de Frontmatter

```yaml wrap
---
# Nome do fluxo de trabalho que aparece na interface do GitHub Actions. Se não
# especificado, assume como padrão o nome do arquivo sem extensão.
# (opcional)
name: "Meu Fluxo de Trabalho"

# Descrição opcional do fluxo de trabalho que é renderizada como um comentário no
# arquivo YAML do GitHub Actions gerado (.lock.yml)
# (opcional)
description: "Descrição do fluxo de trabalho"

# Emoji opcional para representar o fluxo de trabalho visualmente em listagens e
# superfícies de interface.
# (opcional)
emoji: "valor-exemplo"

# Referência de origem opcional indicando de onde este fluxo de trabalho foi adicionado.
# Formato: owner/repo/path@ref (ex: githubnext/agentics/workflows/ci-doctor.md@v1.0.0).
# Renderizado como um comentário no arquivo de bloqueio gerado.
# (opcional)
source: "valor-exemplo"

# Redirecionamento de localização de fluxo de trabalho opcional para atualizações.
# Formato: especificação de fluxo de trabalho ou URL do GitHub (ex: owner/repo/path@ref
# ou https://github.com/owner/repo/blob/main/path.md). Quando presente, a atualização
# segue esta localização e reescreve a origem.
# (opcional)
redirect: "valor-exemplo"

# Identificador de rastreador opcional para marcar todos os ativos criados (issues,
# discussões, comentários, pull requests). Deve ter pelo menos 8 caracteres e conter
# apenas caracteres alfanuméricos, hifens e sublinhados. Este identificador será
# inserido no corpo/descrição de todos os ativos criados para permitir a busca e a
# recuperação de ativos associados a este fluxo de trabalho.
# (opcional)
tracker-id: "valor-exemplo"

# Array opcional de labels para categorizar e organizar fluxos de trabalho. Labels
# podem ser usadas para filtrar fluxos de trabalho em comandos de status/lista.
# (opcional)
labels: []
  # Array de strings

# Campo de metadados opcional para armazenar pares chave-valor personalizados
# compatíveis com a especificação de agente personalizado. Nomes de chave são
# limitados a 64 caracteres e valores são limitados a 1024 caracteres.
# (opcional)
metadata:
  {}

# Especificações de fluxo de trabalho para importar. Suporta forma de array (lista
# de caminhos) ou forma de objeto com subcampo 'aw' (caminhos de fluxo de trabalho
# agentic). Resolução de caminho: (1) caminhos relativos (ex: 'shared/file.md') são
# resolvidos em relação ao diretório do fluxo de trabalho; (2) caminhos começando
# com '.github/' ou '/' são resolvidos a partir da raiz do repositório
# (relativo à raiz do repo); (3) caminhos correspondendo a 'owner/repo/path@ref' são
# buscados do GitHub no momento da compilação (entre repositórios).
# (opcional)
# Formatos aceitos:

# Formato 1: Array de especificações de fluxo de trabalho para importar. Três
# formatos de caminho são suportados: caminhos relativos ('shared/file.md'), caminhos
# relativos à raiz do repo ('.github/agents/my-agent.md') e caminhos entre
# repositórios ('owner/repo/path@ref'). Quaisquer arquivos markdown no diretório
# .github/agents são tratados como arquivos de agente personalizados e apenas um
# arquivo de agente é permitido por fluxo de trabalho.
imports: []
  # Itens de array: indefinido

# Formato 2: Forma de objeto de importações com subcampo 'aw' para caminhos de fluxo
# de trabalho agentic compartilhados.
imports:
  # Array de especificações de fluxo de trabalho agentic compartilhadas para importar.
  # Formato: owner/repo/path@ref ou caminhos relativos.
  # (opcional)
  aw: []

# Lista opcional de arquivos adicionais de fluxo de trabalho ou ação que devem ser
# buscados juntamente com este fluxo de trabalho ao executar 'gh aw add'. As
# entradas são caminhos relativos (do mesmo diretório que este fluxo de trabalho no
# repositório de origem) para arquivos .md de fluxo de trabalho agentic ou arquivos
# .yml/.yaml do GitHub Actions. Sintaxe de expressão do GitHub Actions (${{) não é
# permitida em caminhos de recurso.
# (opcional)
resources: []
  # Itens de array: Caminho relativo para um arquivo .md de fluxo de trabalho ou
  # arquivo .yml/.yaml de action. Deve ser um caminho estático; sintaxe de
  # expressão do GitHub Actions (${{) não é permitida.

# Se true, insere todas as importações (incluindo aquelas sem entradas) no momento da
# compilação no lock.yml gerado, em vez de usar macros de importação de runtime.
# Quando habilitado, o hash do frontmatter cobre todo o corpo markdown, portanto,
# qualquer alteração no conteúdo invalidará o hash.
# (opcional)
inlined-imports: true

# Triggers de fluxo de trabalho que definem quando o fluxo de trabalho agentic deve
# ser executado. Suporta eventos de trigger padrão do GitHub Actions mais triggers
# de comando especiais para /commands (obrigatório)
# Formatos aceitos:

# Formato 1: Nome do evento de trigger simples (ex: 'push', 'issues',
# 'pull_request', 'discussion', 'schedule', 'fork', 'create', 'delete', 'public',
# 'watch', 'workflow_call'), atalho de agenda (ex: 'daily', 'weekly') ou atalho de
# comando slash (ex: '/my-bot' expande para slash_command + workflow_dispatch)
on: "valor-exemplo"

# Formato 2: Configuração de trigger complexa com filtros e opções específicas de
# evento
on:
  # Trigger de comando slash especial para fluxos de trabalho /command (ex:
  # '/my-bot' em comentários de issue). Cria condições para corresponder comandos
  # slash automaticamente. Nota: Pode ser combinado com eventos issues/pull_request
  # se esses eventos usarem apenas tipos 'labeled' ou 'unlabeled'.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Configuração de comando nula - assume como padrão o uso do nome do
  # arquivo de fluxo de trabalho (sem a extensão .md) como o nome do comando
  slash_command: null

  # Formato 2: Nome do comando como uma string (formato de atalho, ex: 'customname'
  # para triggers '/customname'). Nomes de comando não devem começar com '/' já que a
  # barra é adicionada automaticamente ao corresponder comandos.
  slash_command: "valor-exemplo"

  # Formato 3: Objeto de configuração de comando com nome de comando personalizado
  slash_command:
    # Nome do comando slash que dispara o fluxo de trabalho (ex: '/help',
    # '/analyze'). Usado para ativação de fluxo de trabalho baseada em comentário.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de comando único para comandos slash (ex: 'helper-bot' para
    # triggers '/helper-bot'). Nomes de comando não devem começar com '/' já que a
    # barra é adicionada automaticamente ao corresponder comandos. Assume como padrão
    # o nome do arquivo de fluxo de trabalho sem a extensão .md se não especificado.
    name: "Meu Fluxo de Trabalho"

    # Formato 2: Array de nomes de comando que disparam este fluxo de trabalho (ex:
    # ['cmd.add', 'cmd.remove'] para triggers '/cmd.add' e '/cmd.remove'). Cada nome
    # de comando não deve começar com '/'.
    name: []
      # Itens de array: Nome do comando sem barra inicial

    # Eventos onde o comando deve estar ativo. O padrão é todos os eventos
    # relacionados a comentários ('*'). Use nomes de eventos do GitHub Actions.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de evento único ou '*' para todos os eventos. Use nomes de
    # eventos do GitHub Actions: 'issues', 'issue_comment', 'pull_request_comment',
    # 'pull_request', 'pull_request_review_comment', 'discussion',
    # 'discussion_comment'.
    events: "*"

    # Formato 2: Array de nomes de eventos onde o comando deve estar ativo (requer
    # pelo menos um). Use nomes de eventos do GitHub Actions.
    events: []
      # Itens de array: Nome do evento do GitHub Actions.

    # Estratégia de compilação de trigger de comando slash. 'inline' (padrão)
    # compila ouvintes de comentário diretos neste fluxo de trabalho. 'centralized'
    # compila este fluxo de trabalho como workflow_dispatch-centric e roteia eventos
    # slash via o fluxo de trabalho de trigger central gerado.
    # (opcional)
    strategy: "inline"

  # OBSOLETO: Use 'slash_command' em vez disso. Trigger de comando especial para
  # fluxos de trabalho /command (ex: '/my-bot' em comentários de issue). Cria
  # condições para corresponder comandos slash automaticamente.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Configuração de comando nula - assume como padrão o uso do nome do
  # arquivo de fluxo de trabalho (sem a extensão .md) como o nome do comando
  command: null

  # Formato 2: Nome do comando como uma string (formato de atalho, ex: 'customname'
  # para triggers '/customname'). Nomes de comando não devem começar com '/' já que a
  # barra é adicionada automaticamente ao corresponder comandos.
  command: "valor-exemplo"

  # Formato 3: Objeto de configuração de comando com nome de comando personalizado
  command:
    # Nome do comando slash que dispara o fluxo de trabalho (ex: '/deploy', '/test').
    # Usado para ativação de fluxo de trabalho baseada em comando.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de comando personalizado para comandos slash (ex: 'helper-bot'
    # para triggers '/helper-bot'). Nomes de comando não devem começar com '/' já que
    # a barra é adicionada automaticamente ao corresponder comandos. Assume como
    # padrão o nome do arquivo de fluxo de trabalho sem a extensão .md se não
    # especificado.
    name: "Meu Fluxo de Trabalho"

    # Formato 2: Array de nomes de comando que disparam este fluxo de trabalho (ex:
    # ['cmd.add', 'cmd.remove'] para triggers '/cmd.add' e '/cmd.remove'). Cada nome
    # de comando não deve começar com '/'.
    name: []
      # Itens de array: Nome do comando sem barra inicial

    # Eventos onde o comando deve estar ativo. O padrão é todos os eventos
    # relacionados a comentários ('*'). Use nomes de eventos do GitHub Actions.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de evento único ou '*' para todos os eventos. Use nomes de
    # eventos do GitHub Actions: 'issues', 'issue_comment', 'pull_request_comment',
    # 'pull_request', 'pull_request_review_comment', 'discussion',
    # 'discussion_comment'.
    events: "*"

    # Formato 2: Array de nomes de eventos onde o comando deve estar ativo (requer
    # pelo menos um). Use nomes de eventos do GitHub Actions.
    events: []
      # Itens de array: Nome do evento do GitHub Actions.

  # Trigger de comando On Label: dispara quando uma label específica é adicionada a
  # uma issue, pull request ou discussão. A label disparadora é removida
  # automaticamente no início do fluxo de trabalho para que possa ser aplicada
  # novamente para disparar novamente. Use o campo 'events' para restringir quais
  # tipos de item (issues, pull_request, discussion) ativam o trigger.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Nome da label como uma string (formato de atalho). O fluxo de trabalho
  # dispara quando esta label é adicionada a qualquer tipo de item suportado (issue,
  # pull request ou discussão).
  label_command: "valor-exemplo"

  # Formato 2: Objeto de configuração de comando de label com nome(s) de label e
  # filtragem de evento opcional.
  label_command:
    # Nome(s) da(s) label(s) que disparam o fluxo de trabalho quando adicionadas a
    # uma issue, pull request ou discussão.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de label único que atua como um comando (ex: 'deploy' dispara o
    # fluxo de trabalho quando a label 'deploy' é adicionada).
    name: "Meu Fluxo de Trabalho"

    # Formato 2: Array de nomes de label — qualquer uma dessas labels disparará o
    # fluxo de trabalho.
    name: []
      # Itens de array: Um nome de label

    # Alternativa para 'name': nome(s) da(s) label(s) que disparam o fluxo de
    # trabalho.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de label único.
    names: "valor-exemplo"

    # Formato 2: Array de nomes de label — qualquer uma dessas labels disparará o
    # fluxo de trabalho.
    names: []
      # Itens de array: Um nome de label

    # Tipos de item onde o trigger de label-command deve estar ativo. O padrão é todos
    # os tipos suportados: issues, pull_request, discussion.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Tipo de item único ou '*' para todos os tipos.
    events: "*"

    # Formato 2: Array de tipos de item onde o trigger está ativo.
    events: []
      # Itens de array: Tipo de item.

    # Se deve remover automaticamente a label disparadora após o início do fluxo de
    # trabalho. Padrão para true. Defina como false para manter a label no item e pular
    # o passo de remoção de label. Quando false, as permissões issues:write e
    # discussions:write necessárias para remoção de label também são omitidas.
    # (opcional)
    remove_label: true

    # Estratégia de compilação de trigger de comando de label. 'inline' (padrão)
    # compila ouvintes rotulados diretos neste fluxo de trabalho. 'decentralized'
    # compila este fluxo de trabalho como workflow_dispatch-centric e roteia eventos
    # rotulados via o fluxo de trabalho agentic_commands.yml gerado.
    # (opcional)
    strategy: "inline"

  # Trigger de evento de push que executa o fluxo de trabalho quando o código é
  # enviado para o repositório
  # (opcional)
  push:
    # Branches para filtrar
    # (opcional)
    branches: []
      # Array de strings

    # Branches para ignorar
    # (opcional)
    branches-ignore: []
      # Array de strings

    # Caminhos para filtrar
    # (opcional)
    paths: []
      # Array de strings

    # Caminhos para ignorar
    # (opcional)
    paths-ignore: []
      # Array de strings

    # Lista de nomes ou padrões de tag git para incluir em eventos de push (suporta
    # curingas)
    # (opcional)
    tags: []
      # Array de strings

    # Lista de nomes ou padrões de tag git para excluir de eventos de push (suporta
    # curingas)
    # (opcional)
    tags-ignore: []
      # Array de strings

  # Trigger de evento de pull request que executa o fluxo de trabalho quando pull
  # requests são criados, atualizados ou fechados
  # (opcional)
  pull_request:
    # Tipos de eventos de pull request para disparar. Nota: 'converted_to_draft' e
    # 'ready_for_review' representam transições de estado (eventos) em vez de
    # estados. Embora tecnicamente válido ouvir ambos, considere se você precisa lidar
    # com ambas as transições ou apenas uma.
    # (opcional)
    types: []
      # Array de strings

    # Branches para filtrar
    # (opcional)
    branches: []
      # Array of strings

    # Branches para ignorar
    # (opcional)
    branches-ignore: []
      # Array of strings

    # Caminhos para filtrar
    # (opcional)
    paths: []
      # Array of strings

    # Caminhos para ignorar
    # (opcional)
    paths-ignore: []
      # Array of strings

    # Filtrar pelo estado de pull request draft. Defina como false para excluir PRs
    # draft, true para incluir apenas drafts, ou omita para incluir ambos
    # (opcional)
    draft: true

    # Quando true, permite que o fluxo de trabalho seja executado em pull requests de
    # repositórios forkados. Consideração de segurança: PRs de fork têm permissões
    # limitadas.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Padrão de fork único (ex: '*' para todos os forks, 'org/*' para glob
    # de org, 'org/repo' para correspondência exata)
    forks: "valor-exemplo"

    # Formato 2: Lista de repositórios fork permitidos com suporte a glob (ex:
    # 'org/repo', 'org/*', '*' para todos os forks)
    forks: []
      # Itens de array: Padrão de repositório com suporte a glob opcional

    # Array de nomes de tipo de pull request que disparam o fluxo de trabalho. Filtra
    # a execução do fluxo de trabalho para categorias de PR específicas.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de label único para filtrar eventos labeled/unlabeled (ex: 'bug')
    names: "valor-exemplo"

    # Formato 2: Lista de nomes de label para filtrar eventos labeled/unlabeled.
    # Aplica-se apenas quando 'labeled' ou 'unlabeled' está na array types
    names: []
      # Itens de array: Nome da label

  # Trigger de evento de issues que é executado quando issues do repositório são
  # criadas, atualizadas ou gerenciadas
  # (opcional)
  issues:
    # Tipos de eventos de issue
    # (opcional)
    types: []
      # Array de strings

    # Array de nomes de tipo de issue que disparam o fluxo de trabalho. Filtra a
    # execução do fluxo de trabalho para categorias de issue específicas.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Nome de label único para filtrar eventos labeled/unlabeled (ex: 'bug')
    names: "valor-exemplo"

    # Formato 2: Lista de nomes de label para filtrar eventos labeled/unlabeled.
    # Aplica-se apenas quando 'labeled' ou 'unlabeled' está na array types
    names: []
      # Itens de array: Nome da label

    # Se deve bloquear a issue para o agente quando o fluxo de trabalho é executado
    # (impede modificações simultâneas)
    # (opcional)
    lock-for-agent: true

  # Trigger de evento de comentário de issue
  # (opcional)
  issue_comment:
    # Tipos de eventos de comentário de issue
    # (opcional)
    types: []
      # Array de strings

    # Se deve bloquear a issue pai para o agente quando o fluxo de trabalho é
    # executado (impede modificações simultâneas)
    # (opcional)
    lock-for-agent: true

  # Trigger de evento de discussão que executa o fluxo de trabalho quando
  # discussões de repositório são criadas, atualizadas ou gerenciadas
  # (opcional)
  discussion:
    # Tipos de eventos de discussão
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de comentário de discussão que executa o fluxo de trabalho
  # quando comentários em discussões são criados, atualizados ou excluídos
  # (opcional)
  discussion_comment:
    # Tipos de eventos de comentário de discussão
    # (opcional)
    types: []
      # Array de strings

  # Eventos de trigger agendados usando agendas difusas ou expressões cron padrão.
  # Suporta notação de string abreviada (ex: 'daily', 'daily around 2pm') ou array
  # de objetos de agenda. Agendas difusas distribuem automaticamente os horários de
  # execução para evitar picos de carga.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: String de agenda abreviada usando formato difuso ou cron. Exemplos:
  # 'daily', 'daily around 14:00', 'daily between 9:00 and 17:00', 'weekly',
  # 'weekly on monday', 'weekly on friday around 5pm', 'hourly', 'every 2h', 'every
  # 10 minutes', '0 9 * * 1'. Agendas difusas distribuem os horários de execução
  # para evitar picos de carga. Para horários fixos, use sintaxe cron padrão. O
  # intervalo mínimo é de 5 minutos.
  schedule: "valor-exemplo"

  # Formato 2: Array de objetos de agenda com expressões cron (cron padrão ou formato
  # difuso)
  schedule: []
    # Itens de array: objeto

  # Trigger de despacho de fluxo de trabalho manual
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de despacho de fluxo de trabalho simples
  workflow_dispatch: null

  # Formato 2: objeto
  workflow_dispatch:
    # Parâmetros de entrada para despacho manual
    # (opcional)
    inputs:
      {}

  # Trigger de execução de fluxo de trabalho
  # (opcional)
  workflow_run:
    # Lista de fluxos de trabalho para disparar
    # (optional)
    workflows: []
      # Array de strings

    # Tipos de eventos de execução de fluxo de trabalho
    # (optional)
    types: []
      # Array de strings

    # Branches para filtrar
    # (optional)
    branches: []
      # Array de strings

    # Branches para ignorar
    # (optional)
    branches-ignore: []
      # Array de strings

  # Trigger de evento de release
  # (opcional)
  release:
    # Tipos de eventos de release
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de comentário de revisão de pull request
  # (opcional)
  pull_request_review_comment:
    # Tipos de eventos de comentário de revisão de pull request
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de regra de proteção de branch que é executado quando as
  # regras de proteção de branch são alteradas
  # (opcional)
  branch_protection_rule:
    # Tipos de eventos de regra de proteção de branch
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de check run que é executado quando um check run é criado,
  # rerequisitado, concluído ou tem uma ação solicitada
  # (opcional)
  check_run:
    # Tipos de eventos de check run
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de check suite que é executado quando a atividade de check
  # suite ocorre
  # (opcional)
  check_suite:
    # Tipos de eventos de check suite
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento create que é executado quando uma referência Git (branch ou
  # tag) é criada
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento create simples
  create: null

  # Formato 2: objeto
  create:
    {}

  # Trigger de evento delete que é executado quando uma referência Git (branch ou
  # tag) é excluída
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento delete simples
  delete: null

  # Formato 2: objeto
  delete:
    {}

  # Trigger de evento de implantação que é executado quando uma implantação é
  # criada
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento de implantação simples
  deployment: null

  # Formato 2: objeto
  deployment:
    {}

  # Trigger de evento de status de implantação que é executado quando um status de
  # implantação é atualizado
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento de status de implantação simples
  deployment_status: null

  # Formato 2: objeto
  deployment_status:
    # Filtrar para estados de implantação específicos (compilados em condição if).
    # Use uma string para um estado ou uma array para múltiplos estados.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: string
    state: "error"

    # Formato 2: array
    state: []
      # Itens de array: string

  # Trigger de evento de fork que é executado quando alguém faz fork do repositório
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento de fork simples
  fork: null

  # Formato 2: objeto
  fork:
    {}

  # Trigger de evento gollum que é executado quando alguém cria ou atualiza uma
  # página Wiki
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento gollum simples
  gollum: null

  # Formato 2: objeto
  gollum:
    {}

  # Trigger de evento de label que é executado quando uma label é criada, editada
  # ou excluída
  # (opcional)
  label:
    # Tipos de eventos de label
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de merge group que é executado quando um pull request é
  # adicionado a uma fila de merge
  # (opcional)
  merge_group:
    # Tipos de eventos de merge group
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de milestone que é executado quando um milestone é criado,
  # fechado, aberto, editado ou excluído
  # (opcional)
  milestone:
    # Tipos de eventos de milestone
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento page build que é executado quando alguém faz push para um
  # branch de fonte de publicação do GitHub Pages
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento page build simples
  page_build: null

  # Formato 2: objeto
  page_build:
    {}

  # Trigger de evento public que é executado quando um repositório muda de privado
  # para público
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento public simples
  public: null

  # Formato 2: objeto
  public:
    {}

  # Trigger de evento de pull request target que é executado no contexto do
  # repositório base (seguro para PRs de fork)
  # (opcional)
  pull_request_target:
    # Lista de tipos de evento de destino de pull request para disparar
    # (opcional)
    types: []
      # Array de strings

    # Branches para filtrar
    # (opcional)
    branches: []
      # Array de strings

    # Branches para ignorar
    # (opcional)
    branches-ignore: []
      # Array de strings

    # Caminhos para filtrar
    # (opcional)
    paths: []
      # Array de strings

    # Caminhos para ignorar
    # (opcional)
    paths-ignore: []
      # Array de strings

    # Filtrar pelo estado de pull request draft
    # (opcional)
    draft: true

    # Quando true, permite que o fluxo de trabalho seja executado em pull requests de
    # repositórios forkados com permissões de escrita. Consideração de segurança: use
    # com cautela, pois PRs de fork são executados com permissões do repositório base.
    # (opcional)
    # Formatos aceitos:

    # Formato 1: Padrão de fork único
    forks: "valor-exemplo"

    # Formato 2: Lista de repositórios fork permitidos com suporte a glob
    forks: []
      # Itens de array: string

  # Trigger de evento de revisão de pull request que é executado quando uma
  # revisão de pull request é submetida, editada ou descartada
  # (opcional)
  pull_request_review:
    # Tipos de eventos de revisão de pull request
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de pacote de registro que é executado quando um pacote é
  # publicado ou atualizado
  # (opcional)
  registry_package:
    # Tipos de eventos de pacote de registro
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de despacho de repositório para eventos webhook personalizados
  # (opcional)
  repository_dispatch:
    # Tipos de evento personalizados para disparar
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de status que é executado quando o status de um commit Git
  # muda
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento de status simples
  status: null

  # Formato 2: objeto
  status:
    {}

  # Trigger de evento watch que é executado quando alguém estrela o repositório
  # (opcional)
  watch:
    # Tipos de eventos de watch
    # (opcional)
    types: []
      # Array de strings

  # Trigger de evento de chamada de fluxo de trabalho que permite que este fluxo de
  # trabalho seja chamado por outro fluxo de trabalho
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Trigger de evento de chamada de fluxo de trabalho simples
  workflow_call: null

  # Formato 2: objeto
  workflow_call:
    # Parâmetros de entrada que podem ser passados para o fluxo de trabalho quando
    # ele é chamado
    # (opcional)
    inputs:
      {}

    # Segredos que podem ser passados para o fluxo de trabalho quando ele é chamado
    # (opcional)
    secrets:
      {}

  # Hora em que o fluxo de trabalho deve parar de ser executado. Suporta múltiplos
  # formatos: datas absolutas (YYYY-MM-DD HH:MM:SS, June 1 2025, 1st June 2025,
  # 06/01/2025 etc.) ou deltas de tempo relativos (+25h, +3d, +1d12h30m). Valores
  # máximos para deltas de tempo: 12mo, 52w, 365d, 8760h (365 dias). Nota: Unidade
  # de minuto 'm' não é permitida para stop-after; a unidade mínima é horas 'h'.
  # (opcional)
  stop-after: "valor-exemplo"

  # Condicionalmente pular a execução do fluxo de trabalho quando uma consulta de
  # busca do GitHub tiver correspondências. Pode ser uma string (apenas consulta,
  # implica max=1) ou um objeto com campos 'query', 'max' opcional e 'scope'. Use
  # on.github-token ou on.github-app de nível superior para autenticação
  # personalizada.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: String de consulta de busca do GitHub para verificar antes de
  # executar o fluxo de trabalho (implica max=1). Se a busca retornar quaisquer
  # resultados, o fluxo de trabalho será pulado. A consulta é automaticamente
  # escopada ao repositório atual. Exemplo: 'is:issue is:open label:bug'
  skip-if-match: "valor-exemplo"

  # Formato 2: Objeto de configuração skip-if-match com query, contagem máxima de
  # correspondência e escopo opcional. Para autenticação personalizada, use os campos
  # on.github-token ou on.github-app de nível superior.
  skip-if-match:
    # String de consulta de busca do GitHub para verificar antes de executar o fluxo
    # de trabalho. A consulta é automaticamente escopada ao repositório atual.
    query: "valor-exemplo"

    # Número máximo de itens que devem ser correspondidos para que o fluxo de
    # trabalho seja pulado. Assume como padrão 1 se não especificado. Suporta número
    # inteiro ou expressão do GitHub Actions (ex. '${{ inputs.max }}').
    # (opcional)
    # Formatos aceitos:

    # Format 1: integer
    max: 1

    # Format 2: GitHub Actions expression that resolves to an integer at runtime
    max: "valor-exemplo"

    # Escopo para a consulta de busca. Defina como 'none' para desabilitar o
    # escopo automático 'repo:owner/repo', permitindo consultas em toda a
    # organização ou entre repositórios.
    # (opcional)
    scope: "none"

  # Condicionalmente pular a execução do fluxo de trabalho quando uma consulta de
  # busca do GitHub não tiver correspondências (ou menos que o mínimo). Pode ser uma
  # string (apenas consulta, implica min=1) ou um objeto com campos 'query', 'min'
  # opcional e 'scope'. Use on.github-token ou on.github-app de nível superior para
  # autenticação personalizada.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: String de consulta de busca do GitHub para verificar antes de
  # executar o fluxo de trabalho (implica min=1). Se a busca não retornar resultados,
  # o fluxo de trabalho será pulado. A consulta é automaticamente escopada ao
  # repositório atual. Exemplo: 'is:pr is:open label:ready-to-deploy'
  skip-if-no-match: "valor-exemplo"

  # Formato 2: Objeto de configuração skip-if-no-match com query, contagem mínima de
  # correspondência e escopo opcional. Para autenticação personalizada, use os campos
  # on.github-token ou on.github-app de nível superior.
  skip-if-no-match:
    # String de consulta de busca do GitHub para verificar antes de executar o fluxo
    # de trabalho. A consulta é automaticamente escopada ao repositório atual.
    query: "valor-exemplo"

    # Número mínimo de itens que devem ser correspondidos para que o fluxo de
    # trabalho prossiga. Assume como padrão 1 se não especificado.
    # (opcional)
    min: 1

    # Escopo para a consulta de busca. Defina como 'none' para desabilitar o
    # escopo automático 'repo:owner/repo', permitindo consultas em toda a
    # organização ou entre repositórios.
    # (opcional)
    scope: "none"

  # Pular a execução do fluxo de trabalho se quaisquer checks de CI no branch de
  # destino estiverem falhando ou pendentes. Aceita true (verificar todos) ou um
  # objeto para filtrar checks específicos por nome e opcionalmente especificar um
  # branch ou permitir checks pendentes.
  # (opcional)
  # Formatos aceitos:

  # Format 1: Chave nua sem valor — equivalente a true. Pula a execução do fluxo de
  # trabalho se quaisquer checks de CI no branch de destino estiverem falhando
  # atualmente.
  skip-if-check-failing: null

  # Format 2: Pular a execução do fluxo de trabalho se quaisquer checks de CI no
  # branch de destino estiverem falhando atualmente. Para eventos pull_request,
  # verifica o branch base. Para outros eventos, verifica o ref atual.
  skip-if-check-failing: true

  # Format 3: Objeto de configuração skip-if-check-failing com listas de filtro
  # include/exclude opcionais, um nome de branch opcional e uma flag allow-pending.
  skip-if-check-failing:
    # Lista de nomes de check para avaliar. Quando especificado, apenas estes checks
    # nomeados são considerados. Se omitido, todos os checks são avaliados.
    # (opcional)
    include: []
      # Array de strings

    # Lista de nomes de check para ignorar. Checks nesta lista não são considerados
    # ao determinar se o fluxo de trabalho deve ser pulado.
    # (opcional)
    exclude: []
      # Array de strings

    # Nome do branch para verificar checks de CI com falha. Quando omitido, assume
    # como padrão o branch base de um evento pull_request ou o ref atual para outros
    # eventos.
    # (opcional)
    branch: "valor-exemplo"

    # Quando true, checks pendentes ou em andamento não são tratados como falhando.
    # Por padrão (false), qualquer check que ainda não foi concluído é tratado como
    # falhando e bloqueará o fluxo de trabalho.
    # (opcional)
    allow-pending: true

  # Pular a execução do fluxo de trabalho para usuários com funções de repositório
  # específicas. Útil para fluxos de trabalho que devem ser executados apenas para
  # contribuidores externos ou níveis de permissão específicos.
  # (opcional)
  # Formatos aceitos:

  # Format 1: Função única para pular o fluxo de trabalho (ex: 'admin'). Se o
  # usuário que disparou tiver essa função, o fluxo de trabalho será pulado.
  skip-roles: "valor-exemplo"

  # Format 2: Lista de funções para pular o fluxo de trabalho (ex: ['admin',
  # 'maintainer', 'write']). Se o usuário que disparou tiver qualquer uma dessas
  # funções, o fluxo de trabalho será pulado.
  skip-roles: []
    # Itens de array: string

  # Pular a execução do fluxo de trabalho para usuários específicos do GitHub.
  # Útil para impedir que fluxos de trabalho sejam executados para contas
  # específicas (ex: bots, membros específicos da equipe).
  # (opcional)
  # Formatos aceitos:

  # Format 1: Nome de usuário único do GitHub para pular o fluxo de trabalho (ex:
  # 'user1'). Se o usuário que disparou corresponder, o fluxo de trabalho será
  # pulado.
  skip-bots: "valor-exemplo"

  # Format 2: Lista de nomes de usuário do GitHub para pular o fluxo de trabalho
  # (ex: ['user1', 'user2']). Se o usuário que disparou estiver nesta lista, o fluxo
  # de trabalho será pulado.
  skip-bots: []
    # Itens de array: string

  # Pular a execução do fluxo de trabalho quando um campo author_association de
  # payload específico do evento (por exemplo:
  # github.event.comment.author_association,
  # github.event.issue.author_association,
  # github.event.pull_request.author_association) corresponde a associações
  # configuradas para eventos específicos. As chaves são nomes de eventos (por
  # exemplo: issue_comment, pull_request_review_comment, issues, pull_request). Os
  # valores aceitam uma única string ou uma array de strings. Valores de associação
  # não diferenciam maiúsculas de minúsculas no frontmatter.
  # (opcional)
  skip-author-associations:
    {}

  # Funções de permissão de repositório necessárias para disparar fluxos de trabalho
  # agentic. O padrão é ['admin', 'maintainer', 'write'] para segurança. Use 'all'
  # para permitir qualquer usuário autenticado (⚠️ consideração de segurança).
  # (opcional)
  # Formatos aceitos:

  # Format 1: Nível de permissão de repositório único que pode disparar o fluxo de
  # trabalho. Use 'all' para permitir qualquer usuário autenticado (⚠️ desativa a
  # verificação de permissão inteiramente - use com cautela)
  roles: "admin"

  # Format 2: Lista de níveis de permissão de repositório que podem disparar o fluxo
  # de trabalho. Verificações de permissão são aplicadas automaticamente a triggers
  # potencialmente inseguros.
  roles: []
    # Itens de array: Nível de permissão de repositório: 'admin' (acesso total),
    # 'maintainer'/'maintain' (gerenciamento de repositório), 'write' (acesso de
    # push), 'triage' (gerenciamento de issue), 'read' (acesso somente leitura)

  # Lista de permissão de identificadores de bot que podem disparar o fluxo de
  # trabalho mesmo se eles não atenderem às permissões de função necessárias. Quando
  # o ator está nesta lista, o bot deve estar ativo (instalado) no repositório para
  # disparar o fluxo de trabalho.
  # (opcional)
  bots: []
    # Itens de array: Identificador/nome do Bot (ex: 'dependabot[bot]',
    # 'renovate[bot]', 'github-actions[bot]')

  # Filtrar fluxos de trabalho disparados por pull_request_target (ou outros
  # eventos rotulados) para disparar apenas quando a label disparadora corresponder a
  # um desses nomes. Gera uma condição if: em nível de job no job de pré-ativação,
  # para que eventos de label sem correspondência sejam mostrados como Skipped (⊘) em
  # vez de Failed (❌).
  # (opcional)
  # Formatos aceitos:

  # Format 1: Nome de label único que deve corresponder à label disparadora (ex:
  # 'panel-review')
  labels: "valor-exemplo"

  # Format 2: Lista de nomes de label; o fluxo de trabalho dispara quando a label
  # disparadora corresponde a qualquer entrada.
  labels: []
    # Itens de array: indefinido

  # Permitir o padrão bot-posted-menu / user-checks-box: quando um fluxo de trabalho
  # posta um comentário de menu de checkbox como um bot de aplicativo do GitHub e um
  # mantenedor humano o edita para marcar uma caixa (issue_comment:edited onde ator
  # ≠ comment.user.login), trate isso como seguro e pule a verificação de
  # confused-deputy. Quando false (padrão), a verificação se aplica a todos os
  # eventos issue_comment. O vetor de ataque confused-deputy do Dependabot
  # (issue_comment:created) não é afetado.
  # (opcional)
  allow-bot-authored-trigger-comment: true

  # Nome do ambiente que requer aprovação manual antes que o fluxo de trabalho possa
  # ser executado. Deve corresponder a um ambiente válido configurado nas
  # configurações do repositório.
  # (opcional)
  manual-approval: "valor-exemplo"

  # Reação de IA para adicionar/remover no item disparador. A forma escalar aceita
  # um de: +1, -1, laugh, confused, heart, hooray, rocket, eyes, none. A forma de
  # objeto implica reações habilitadas e suporta campos opcionais `issues`,
  # `pull-requests` e `discussions` para controlar grupos de trigger de forma
  # independente; use `type` para escolher o emoji de reação (padrão para `eyes`
  # quando omitido). Use 'none' para desabilitar reações.
  # (opcional)
  # Formatos aceitos:

  # Format 1: string
  reaction: "+1"

  # Format 2: YAML analisa +1 e -1 sem aspas como inteiros. Eles são convertidos
  # para strings +1 e -1 respectivamente.
  reaction: 1

  # Format 3: objeto
  reaction:
    # Tipo de reação. Padrão para 'eyes' quando omitido.
    # (opcional)
    # Formatos aceitos:

    # Format 1: string
    type: "+1"

    # Format 2: YAML analisa +1 e -1 sem aspas como inteiros. Eles são convertidos
    # para strings +1 e -1 respectivamente.
    type: 1

    # Se reações são permitidas para triggers de issue (issues, issue_comment).
    # (opcional)
    issues: true

    # Se reações são permitidas para triggers de pull request (pull_request,
    # pull_request_review_comment).
    # (opcional)
    pull-requests: true

    # Se reações são permitidas para triggers de discussão e discussion_comment.
    # (opcional)
    discussions: true

  # Se deve postar comentários de status (iniciado/concluído) no item disparador. A
  # forma booleana habilita/desabilita comentários de status globalmente. A forma de
  # objeto implica comentários de status habilitados e suporta campos opcionais
  # `issues`, `pull-requests` e `discussions` para controlar grupos de trigger de
  # forma independente. Habilitado automaticamente para triggers slash_command e
  # label_command quando não configurado explicitamente.
  # (opcional)
  # Formatos aceitos:

  # Format 1: booleano
  status-comment: true

  # Format 2: objeto
  status-comment:
    # Se comentários de status são permitidos para triggers de issue (issues,
    # issue_comment).
    # (opcional)
    issues: true

    # Se comentários de status são permitidos para triggers de pull request
    # (pull_request, pull_request_review_comment).
    # (opcional)
    pull-requests: true

    # Se comentários de status são permitidos para triggers de discussão e
    # discussion_comment.
    # (opcional)
    discussions: true

  # Token do GitHub personalizado para reações de pré-ativação, comentários de
  # status de ativação e consultas de busca skip-if. Quando especificado, substitui
  # o GITHUB_TOKEN padrão para essas operações.
  # (opcional)
  github-token: "${{ secrets.GITHUB_TOKEN }}"

  # Configuração do GitHub App para emitir um token usado em reações de
  # pré-ativação, comentários de status de ativação e consultas de busca skip-if.
  # Quando configurado, um único token de acesso de instalação do GitHub App é
  # emitido e compartilhado entre todas essas operações em vez de usar o
  # GITHUB_TOKEN padrão. Pode ser definido em um fluxo de trabalho agentic
  # compartilhado e herdado por fluxos de trabalho importados.
  # (opcional)
  github-app:
    # Alias obsoleto para client-id. ID do GitHub App/client ID (ex: '${{ vars.APP_ID
    # }}').
    # (opcional)
    app-id: "valor-exemplo"

    # Client ID do GitHub App (ex: '${{ vars.APP_ID }}'). Necessário para emitir um
    # token do GitHub App.
    # (opcional)
    client-id: "valor-exemplo"

    # Chave privada do GitHub App (ex: '${{ secrets.APP_PRIVATE_KEY }}'). Necessário
    # para emitir um token do GitHub App.
    # (opcional)
    private-key: "valor-exemplo"

    # Proprietário opcional da instalação do GitHub App (assume como padrão o
    # proprietário do repositório atual se não especificado)
    # (opcional)
    owner: "valor-exemplo"

    # Lista opcional de repositórios para conceder acesso (assume como padrão o
    # repositório atual se não especificado)
    # (opcional)
    repositories: []
      # Itens de array: string

    # Permissões extras opcionais exclusivas do GitHub App para mesclar no token
    # emitido. Entra em vigor para tools.github.github-app e
    # safe-outputs.github-app; ignorado em on.github-app e no fallback github-app de
    # nível superior. Use para adicionar escopos exclusivos do GitHub App (ex:
    # membros, administração de organização) não expressáveis por meio de declarações
    # de manipulador padrão.
    # (opcional)
    permissions:
      # Nível de permissão para administração de repositório (leitura/nenhuma; "write"
      # é recusado pelo compilador). Permissão exclusiva do GitHub App para
      # administração de repositório.
      # (opcional)
      administration: "read"

      # Nível de permissão para Codespaces (leitura/nenhuma; "write" é recusado pelo
      # compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      codespaces: "read"

      # Nível de permissão para administração do ciclo de vida do Codespaces
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      codespaces-lifecycle-admin: "read"

      # Nível de permissão para metadados do Codespaces (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      codespaces-metadata: "read"

      # Nível de permissão para endereços de e-mail de usuário (leitura/nenhuma;
      # "write" é recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      email-addresses: "read"

      # Nível de permissão para ambientes de repositório (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      environments: "read"

      # Nível de permissão para assinatura git (leitura/nenhuma; "write" é recusado
      # pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      git-signing: "read"

      # Nível de permissão para membros da organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Necessário para chamadas de API de associação de
      # equipe da organização.
      # (opcional)
      members: "read"

      # Nível de permissão para administração da organização (leitura/nenhuma; "write"
      # é recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-administration: "read"

      # Nível de permissão para banners de anúncio da organização (leitura/nenhuma;
      # "write" é recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-announcement-banners: "read"

      # Nível de permissão para Codespaces da organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-codespaces: "read"

      # Nível de permissão para Copilot da organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-copilot: "read"

      # Nível de permissão para funções personalizadas de organização da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-custom-org-roles: "read"

      # Nível de permissão para propriedades personalizadas da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-custom-properties: "read"

      # Nível de permissão para funções de repositório personalizadas da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-custom-repository-roles: "read"

      # Nível de permissão para eventos de organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-events: "read"

      # Nível de permissão para webhooks de organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-hooks: "read"

      # Nível de permissão para gerenciamento de membros da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-members: "read"

      # Nível de permissão para pacotes da organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-packages: "read"

      # Nível de permissão para solicitações de token de acesso pessoal da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-personal-access-token-requests: "read"

      # Nível de permissão para tokens de acesso pessoal da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-personal-access-tokens: "read"

      # Nível de permissão para plano da organização (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-plan: "read"

      # Nível de permissão para runners auto-hospedados da organização
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      organization-self-hosted-runners: "read"

      # Nível de permissão para bloqueio de usuário da organização (leitura/nenhuma;
      # "write" é recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      organization-user-blocking: "read"

      # Nível de permissão para propriedades personalizadas do repositório
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      repository-custom-properties: "read"

      # Nível de permissão para webhooks do repositório (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      repository-hooks: "read"

      # Nível de permissão para acesso a arquivo único (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      single-file: "read"

      # Nível de permissão para discussões de equipe (leitura/nenhuma; "write" é
      # recusado pelo compilador). Permissão exclusiva do GitHub App.
      # (opcional)
      team-discussions: "read"

      # Nível de permissão para alertas de vulnerabilidade do Dependabot
      # (leitura/nenhuma; "write" é recusado pelo compilador). Também disponível como
      # um escopo GITHUB_TOKEN. Quando usado com um GitHub App, encaminhado como
      # entrada permission-vulnerability-alerts.
      # (opcional)
      vulnerability-alerts: "read"

      # Nível de permissão para arquivos de fluxo de trabalho do GitHub Actions
      # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
      # GitHub App.
      # (opcional)
      workflows: "read"

  # Jobs de fluxo de trabalho personalizados explícitos adicionais dos quais
  # pre_activation e activation devem depender.
  # (opcional)
  needs: []
    # Itens de array: string

  # Passos para injetar no job de pré-ativação. Estes passos são executados após
  # todas as verificações integradas (associação, stop-time, skip-if etc.) e seus
  # resultados são expostos como saídas de pré-ativação. Use 'id' nos passos para
  # referenciar seus resultados via needs.pre_activation.outputs.<id>_result.
  # (opcional)
  steps: []
    # Itens de array:
      # Nome opcional para o passo
      # (opcional)
      name: "Meu Fluxo de Trabalho"

      # ID do passo opcional. Quando definido, o resultado do passo é exposto como
      # needs.pre_activation.outputs.<id>_result
      # (opcional)
      id: "valor-exemplo"

      # Comando shell para executar
      # (opcional)
      run: "valor-exemplo"

      # Action a ser usada (ex: 'actions/checkout@v4')
      # (opcional)
      uses: "valor-exemplo"

      # Parâmetros de entrada para a action
      # (opcional)
      with:
        {}

      # Variáveis de ambiente para o passo
      # (opcional)
      env:
        {}

      # Expressão condicional para o passo
      # (opcional)
      if: "valor-exemplo"

      # Se deve continuar se o passo falhar
      # (opcional)
      continue-on-error: true

  # Permissões adicionais para o job de pré-ativação. Use para declarar escopos
  # extras exigidos por on.steps (ex: issues: read para chamadas de API do GitHub em
  # passos).
  # (opcional)
  # Mapa de escopo de permissão para nível
  # (opcional)
  permissions:
    # (opcional)
    actions: "read"

    # (opcional)
    checks: "read"

    # (opcional)
    contents: "read"

    # (opcional)
    deployments: "read"

    # (opcional)
    discussions: "read"

    # (opcional)
    issues: "read"

    # (opcional)
    packages: "read"

    # (opcional)
    pages: "read"

    # (opcional)
    pull-requests: "read"

    # (opcional)
    repository-projects: "read"

    # (opcional)
    security-events: "read"

    # (opcional)
    statuses: "read"

  # Quando definido como false, desativa o passo de verificação de hash do
  # frontmatter no job de ativação. O padrão é true (verificação está habilitada).
  # Útil quando os arquivos de origem do fluxo de trabalho são gerenciados fora do
  # contexto padrão do repositório GitHub (ex: rulesets de organização entre
  # repositórios) e a verificação de obsoleto não é necessária.
  # (opcional)
  stale-check: true

# Permissões de token do GitHub para o fluxo de trabalho. Controla o que o
# GITHUB_TOKEN pode acessar durante a execução. Use o princípio do menor privilégio
# - conceda apenas as permissões mínimas necessárias.
# (opcional)
# Formatos aceitos:

# Formato 1: String de permissões simples: 'read-all' (todas as permissões de
# leitura) ou 'write-all' (todas as permissões de escrita)
permissions: "read-all"

# Formato 2: Objeto de permissões detalhado com controle granular sobre escopos
# específicos da API do GitHub
permissions:
  # Permissão para fluxos de trabalho e execuções do GitHub Actions (read: visualizar
  # fluxos de trabalho, write: gerenciar fluxos de trabalho, none: sem acesso)
  # (opcional)
  actions: "read"

  # Permissão para atestados de artefato (read: visualizar atestados, write: criar
  # atestados, none: sem acesso)
  # (optional)
  attestations: "read"

  # Permissão para verificações de repositório e verificações de status (read:
  # visualizar verificações, write: criar/atualizar verificações, none: sem acesso)
  # (opcional)
  checks: "read"

  # Permissão para conteúdos de repositório (read: visualizar arquivos, write:
  # modificar arquivos/branches, none: sem acesso)
  # (opcional)
  contents: "read"

  # Permissão para implantações de repositório (read: visualizar implantações,
  # write: criar/atualizar implantações, none: sem acesso)
  # (opcional)
  deployments: "read"

  # Permissão para discussões de repositório (read: visualizar discussões, write:
  # criar/atualizar discussões, none: sem acesso)
  # (opcional)
  discussions: "read"

  # Nível de permissão para solicitações de token OIDC (apenas write/none - read não
  # é suportado). Permite que fluxos de trabalho solicitem tokens JWT para
  # autenticação de provedor de nuvem.
  # (opcional)
  id-token: "write"

  # Permissão para issues de repositório (read: visualizar issues, write:
  # criar/atualizar/fechar issues, none: sem acesso)
  # (opcional)
  issues: "read"

  # Permissão para modelos do GitHub Copilot (read: acesso a modelos de IA para
  # fluxos de trabalho agentic, none: sem acesso)
  # (opcional)
  models: "read"

  # Permissão para metadados de repositório (read: visualizar informações do
  # repositório, write: atualizar metadados do repositório, none: sem acesso)
  # (opcional)
  metadata: "read"

  # Nível de permissão para pacotes do GitHub (read/write/none). Controla o acesso
  # para publicar, modificar ou excluir pacotes.
  # (opcional)
  packages: "read"

  # Nível de permissão para GitHub Pages (read/write/none). Controla o acesso para
  # implantar e gerenciar sites do GitHub Pages.
  # (opcional)
  pages: "read"

  # Nível de permissão para pull requests (read/write/none). Controla o acesso para
  # criar, editar, revisar e gerenciar pull requests.
  # (opcional)
  pull-requests: "read"

  # Nível de permissão para projetos de repositório (read/write/none). Controla o
  # acesso para gerenciar boards de Projetos do GitHub em nível de repositório.
  # (opcional)
  repository-projects: "read"

  # Nível de permissão para projetos de organização (read/write/none). Controla o
  # acesso para gerenciar boards de Projetos do GitHub em nível de organização.
  # (opcional)
  organization-projects: "read"

  # Nível de permissão para eventos de segurança (read/write/none). Controla o acesso
  # para visualizar e gerenciar alertas de verificação de código e descobertas de
  # segurança.
  # (opcional)
  security-events: "read"

  # Nível de permissão para status de commit (read/write/none). Controla o acesso
  # para criar e atualizar verificações de status de commit.
  # (opcional)
  statuses: "read"

  # Nível de permissão para alertas de vulnerabilidade do Dependabot
  # (read/write/none). Permite que fluxos de trabalho acessem a API de alertas do
  # Dependabot via GITHUB_TOKEN em vez de exigir um PAT ou GitHub App.
  # (opcional)
  vulnerability-alerts: "read"

  # Nível de permissão para arquivos de fluxo de trabalho do GitHub Actions
  # (leitura/nenhuma; "write" é recusado pelo compilador). Permissão exclusiva do
  # GitHub App.
  # (opcional)
  workflows: "read"

  # Atalho de permissão que aplica acesso de leitura a todos os escopos de
  # permissão. Pode ser combinado com permissões de escrita específicas para
  # substituir escopos individuais. 'write' não é permitido para todos.
  # (opcional)
  all: "read"

# Nome personalizado para execuções de fluxo de trabalho que aparece na interface
# do GitHub Actions (suporta expressões do GitHub como ${{
# github.event.issue.title }})
# (opcional)
run-name: "valor-exemplo"

# Agrupa todos os jobs que são executados no fluxo de trabalho
# (opcional)
jobs:
  {}

# Tipo de runner para execução de fluxo de trabalho (campo padrão do GitHub
# Actions). Suporta múltiplos formatos: string simples para label de runner único
# (ex: 'ubuntu-latest'), array para seleção de runner com fallbacks ou objeto para
# grupos de runner hospedados no GitHub com labels específicas. Para fluxos de
# trabalho agentic, a seleção de runner importa quando cargas de trabalho de IA
# exigem recursos de computação específicos ou ao usar runners auto-hospedados com
# capacidades especializadas. Tipicamente configurado no nível de job em vez disso.
# Veja
# https://docs.github.com/en/actions/using-jobs/choosing-the-runner-for-a-job
# (opcional)
# Formatos aceitos:

# Formato 1: Label de runner simples. Use para runners padrão hospedados no
# GitHub (ex: 'ubuntu-latest', 'windows-latest', 'macos-latest') ou labels de
# runner auto-hospedados. Forma mais comum para fluxos de trabalho agentic.
runs-on: "valor-exemplo"

# Formato 2: Array de labels de runner para seleção com fallbacks. O GitHub Actions
# usará o primeiro runner disponível que corresponder a qualquer label na array.
# Útil para configurações de alta disponibilidade ou quando múltiplos tipos de
# runner são aceitáveis.
runs-on: []
  # Itens de array: string

# Formato 3: Configuração de grupo de runner para runners hospedados no GitHub.
# Use este formato para direcionar grupos de runner específicos (ex: runners maiores
# com mais CPU/memória) ou pools de runner auto-hospedados com requisitos de label
# específicos. Fluxos de trabalho agentic podem se beneficiar de runners maiores
# para tarefas complexas de processamento de IA.
runs-on:
  # Nome do grupo de runner para runners auto-hospedados ou grupos de runner
  # hospedados no GitHub
  # (opcional)
  group: "valor-exemplo"

  # Lista de labels de runner para runners auto-hospedados ou seleção de runner
  # hospedado no GitHub
  # (opcional)
  labels: []
    # Array de strings

# Runner para todos os jobs de framework/gerados (ativação, pré-ativação,
# safe-outputs, desbloqueio, APM etc.). Fornece uma substituição estável para
# compilação para runners de job gerados sem exigir uma seção safe-outputs.
# Substituído por safe-outputs.runs-on quando ambos estão definidos. Padrão para
# 'ubuntu-slim'. Use isso quando sua infraestrutura não fornecer o runner padrão ou
# quando precisar de seleção de runner consistente em todos os jobs.
# (opcional)
runs-on-slim: "valor-exemplo"

# Timeout do fluxo de trabalho em minutos (campo padrão do GitHub Actions). O padrão
# é 20 minutos para fluxos de trabalho agentic. Possui padrões sensíveis e pode
# tipicamente ser omitido. Runners personalizados suportam timeouts mais longos
# além do limite do runner hospedado no GitHub. Suporta expressões do GitHub
# Actions (ex. '${{ inputs.timeout }}') para fluxos de trabalho workflow_call
# reutilizáveis.
# (opcional)
# Formatos aceitos:

# Formato 1: inteiro
timeout-minutes: 1

# Formato 2: Expressão do GitHub Actions que resolve para um inteiro (ex. '${{
# inputs.timeout }}')
timeout-minutes: "valor-exemplo"

# Controle de simultaneidade para limitar execuções de fluxo de trabalho
# simultâneas (campo padrão do GitHub Actions). Suporta duas formas: string simples
# para isolamento de grupo básico, ou objeto com opção cancel-in-progress para
# controle avançado. Fluxos de trabalho agentic melhoram isso com políticas de
# simultaneidade por motor automáticas (padrão para job único por motor em todos os
# fluxos de trabalho) e limitação de taxa baseada em token. Comportamento padrão:
# fluxos de trabalho no mesmo grupo enfileiram sequencialmente a menos que
# cancel-in-progress seja true. Veja
# https://docs.github.com/en/actions/using-jobs/using-concurrency
# (opcional)
# Formatos aceitos:

# Formato 1: Nome do grupo de simultaneidade simples para impedir múltiplas
# execuções no mesmo grupo. Use expressões como '${{ github.workflow }}' para
# isolamento por fluxo de trabalho ou '${{ github.ref }}' para isolamento por
# branch. Fluxos de trabalho agentic geram automaticamente políticas de
# simultaneidade aprimoradas usando 'gh-aw-{engine-id}' como o grupo padrão para
# limitar cargas de trabalho de IA simultâneas em todos os fluxos de trabalho que
# usam o mesmo motor.
concurrency: "valor-exemplo"

# Formato 2: Objeto de configuração de simultaneidade com isolamento de grupo e
# controle de cancelamento. Use a forma de objeto quando precisar de controle
# refinado sobre cancelar ou não execuções em andamento. Para fluxos de trabalho
# agentic, isso é útil para impedir que múltiplos agentes de IA sejam executados
# simultaneamente e consumam recursos ou cotas de API excessivas.
concurrency:
  # Identificador do grupo de simultaneidade. Fluxos de trabalho no mesmo grupo não
  # podem ser executados simultaneamente. Suporta expressões do GitHub Actions para
  # nomes de grupo dinâmicos com base em branch, fluxo de trabalho ou outro contexto.
  # (opcional)
  group: "valor-exemplo"

  # Se deve cancelar fluxos de trabalho em andamento no mesmo grupo de
  # simultaneidade quando um novo é iniciado. Padrão: false (fila novas
  # execuções). Defina como true para fluxos de trabalho agentic onde apenas a
  # execução mais recente importa (ex: análise de PR que se torna obsoleta quando
  # novos commits são enviados).
  # (opcional)
  cancel-in-progress: true

  # Comportamento da fila de execução pendente para este grupo de simultaneidade.
  # 'single' (padrão) permite uma execução pendente e substitui execuções pendentes
  # mais antigas. 'max' permite até 100 execuções pendentes em ordem FIFO.
  # (opcional)
  queue: "single"

  # Expressão discriminadora adicional anexada a grupos de simultaneidade de nível
  # de job gerados pelo compilador (agente, jobs de saída). Use isso quando múltiplas
  # instâncias de fluxo de trabalho são despachadas simultaneamente com entradas
  # diferentes (padrão fan-out) para impedir que grupos de simultaneidade de nível de
  # job colidam. Por exemplo, '${{ inputs.finding_id }}' garante que cada execução
  # despachada obtenha um grupo de nível de job único. Suporta expressões do GitHub
  # Actions. Este campo é removido do arquivo de bloqueio compilado (é uma extensão
  # gh-aw, não um campo do GitHub Actions).
  # (opcional)
  job-discriminator: "valor-exemplo"

# Variáveis de ambiente para o fluxo de trabalho
# (opcional)
# Formatos aceitos:

# Formato 1: objeto
env:
  {}

# Formato 2: string
env: "valor-exemplo"

# Interruptor obsoleto para suporte a sub-agente inline. Sub-agentes inline são
# habilitados por padrão. Definir isso como false não é suportado e causa erro de
# compilação.
# (opcional)
inline-sub-agents: true

# Feature flags e opções de configuração para recursos experimentais ou opcionais no
# fluxo de trabalho. Cada recurso pode ser uma flag booleana ou um valor de string.
# O recurso 'action-tag' (string) especifica a tag ou SHA a ser usada ao referenciar
# actions/setup em fluxos de trabalho compilados (apenas para fins de teste).
# (opcional)
features:
  {}

# Definições de alias de modelo nomeadas com listas de fallback ordenadas,
# resolvidas recursivamente pelo AWF. Cada chave é um nome de alias (use string
# vazia "" para a política padrão). Cada valor é uma lista ordenada de padrões glob
# de fornecedor/modelid ou outros nomes de alias para tentar em sequência. As
# entradas definidas aqui são mescladas sobre os aliases embutidos; o arquivo de
# fluxo de trabalho principal sempre vence sobre os aliases importados. Aliases
# embutidos incluem: sonnet, haiku, opus, gpt-5, gpt-5-mini, gpt-5-codex,
# gemini-flash, gemini-pro, small, mini, large, auto.
# (opcional)
models:
  {}

# Experimentos de teste A/B. Cada chave é um nome de experimento; o valor é ou uma
# array de duas ou mais strings de variante (forma de array simples) ou um objeto
# com um campo 'variants' mais campos de metadados opcionais (descrição, métrica,
# peso, issue, data_início, data_término, hipótese, métricas_secundárias,
# métricas_de_guardrail, min_amostras). A chave reservada 'storage' controla como o
# estado do experimento é persistido: 'repo' (padrão) comita o estado para um
# branch git chamado 'experiments/{sanitizedWorkflowID}' (workflow ID minúsculo com
# hifens removidos) para durabilidade; 'cache' usa cache do GitHub Actions. Em
# tempo de execução, o job de ativação escolhe uma variante e persiste os
# contadores atualizados. Use ${{ experiments.<name> }} no prompt do fluxo de
# trabalho para referenciar a variante selecionada. Quando múltiplos experimentos
# são declarados, as atribuições são estatisticamente balanceadas usando um
# contador de menos-usado que faz round-robin entre variantes (ou ponderado quando
# 'weight' é fornecido); empates são resolvidos aleatoriamente para que nenhuma
# variante seja favorecida sistematicamente na primeira execução.
# (opcional)
experiments:
  # Backend de armazenamento para o estado do experimento. 'repo' (padrão) persiste
  # o estado para um branch git chamado 'experiments/{sanitizedWorkflowID}'
  # (workflow ID minúsculo com hifens removidos, ex: 'my-workflow' ->
  # 'experiments/myworkflow') para durabilidade entre despejos de cache. 'cache' usa
  # cache do GitHub Actions (comportamento legado). O armazenamento em repo é
  # recomendado porque os dados do experimento são valiosos e mais duráveis que o
  # cache.
  # (opcional)
  storage: "cache"

# OBSOLETO: Use 'disable-model-invocation' em vez disso. Controla se o agente
# personalizado deve inferir contexto adicional da conversa. Este campo é mantido
# para compatibilidade retroativa com arquivos de agente personalizados existentes.
# (opcional)
infer: true

# Controla se o agente personalizado deve desativar a invocação do modelo. Quando
# definido como true, o agente não fará chamadas de modelo adicionais. Este é o nome
# de campo preferido para arquivos de agente personalizados (substitui o campo
# obsoleto 'infer').
# (opcional)
disable-model-invocation: true

# Valores de segredo passados para a execução do fluxo de trabalho. Segredos podem
# ser definidos como strings simples (expressões do GitHub Actions) ou objetos com
# propriedades 'value' e 'description'. Tipicamente usados para fornecer segredos
# para servidores MCP ou motores personalizados. Nota: Para passar segredos para
# fluxos de trabalho reutilizáveis, use o campo jobs.<job_id>.secrets em vez disso.
# (opcional)
secrets:
  {}

# Ambiente que o job referencia (para ambientes protegidos e implantações)
# (opcional)
# Formatos aceitos:

# Formato 1: Nome do ambiente como uma string
environment: "valor-exemplo"

# Formato 2: Objeto de ambiente com nome e URL opcional
environment:
  # O nome do ambiente configurado no repo
  name: "Meu Fluxo de Trabalho"

  # Uma URL de implantação
  # (opcional)
  url: "valor-exemplo"

# Container para executar os passos do job
# (opcional)
# Formatos aceitos:

# Formato 1: Nome da imagem Docker (ex: 'node:18', 'ubuntu:latest')
container: "valor-exemplo"

# Formato 2: Objeto de configuração de container
container:
  # A imagem Docker a ser usada como container
  image: "valor-exemplo"

  # Credenciais para registros privados
  # (opcional)
  credentials:
    # Nome de usuário para autenticação de registro Docker ao puxar imagens de
    # container privadas.
    # (opcional)
    username: "valor-exemplo"

    # Senha ou token de acesso para autenticação de registro Docker. Deve usar a
    # sintaxe de segredos: ${{ secrets.DOCKER_PASSWORD }}
    # (opcional)
    password: "valor-exemplo"

  # Variáveis de ambiente para o container
  # (opcional)
  env:
    {}

  # Portas para expor no container
  # (opcional)
  ports: []

  # Volumes para o container
  # (opcional)
  volumes: []
    # Array de strings

  # Opções adicionais de container Docker
  # (opcional)
  options: "valor-exemplo"

# Containers de serviço para o job
# (opcional)
services:
  {}

# Controle de acesso à rede para motores de IA usando identificadores de
# ecossistema e listas de permissão de domínio. Suporta padrões curinga como
# '*.example.com' para corresponder a qualquer subdomínio. Controla capacidades de
# web fetch e pesquisa. IMPORTANTE: Para fluxos de trabalho que constroem/instalam/
# testam código, inclua sempre o identificador de ecossistema da linguagem
# juntamente com 'defaults' — 'defaults' sozinho cobre apenas infraestrutura
# básica, não registros de pacote. Identificadores de ecossistema por runtime:
# 'dotnet' (.NET/NuGet), 'python' (pip/PyPI), 'node' (npm/yarn), 'go' (go
# modules), 'java' (Maven/Gradle), 'ruby' (Bundler), 'rust' (Cargo), 'swift'
# (Swift PM). Exemplo: um projeto .NET precisa de network: { allowed: [defaults,
# dotnet] }.
# (opcional)
# Formatos aceitos:

# Formato 1: Use permissões de rede padrão (infraestrutura básica: certificados,
# esquema JSON, Ubuntu etc.)
network: "defaults"

# Formato 2: Configuração de acesso à rede personalizado com identificadores de
# ecossistema e domínios específicos
network:
  # Lista de domínios permitidos ou identificadores de ecossistema (ex: 'defaults',
  # 'python', 'node', '*.example.com'). Padrões curinga correspondem a qualquer
  # subdomínio E ao domínio base.
  # (opcional)
  allowed: []
    # Itens de array: Nome de domínio ou identificador de ecossistema. Suporta
    # curingas como '*.example.com' (corresponde a sub.example.com,
    # deep.nested.example.com e o próprio example.com). Identificadores de
    # ecossistema por runtime: 'dotnet' (.NET/NuGet), 'python' (pip/PyPI), 'node'
    # (npm/yarn), 'go' (go modules), 'java' (Maven/Gradle), 'ruby' (RubyGems),
    # 'rust' (Cargo), 'swift' (Swift PM), 'php' (Composer), 'dart' (pub.dev),
    # 'haskell' (Hackage), 'perl' (CPAN), 'containers' (Docker/GHCR), 'github'
    # (domínios do GitHub), 'terraform' (HashiCorp), 'linux-distros' (apt/yum),
    # 'playwright' (teste de navegador), 'defaults' (infraestrutura básica).

  # Lista de domínios bloqueados ou identificadores de ecossistema (ex: 'python',
  # 'node', 'tracker.example.com'). Domínios bloqueados têm precedência sobre
  # domínios permitidos.
  # (opcional)
  blocked: []
    # Itens de array: Nome de domínio ou identificador de ecossistema para bloquear.
    # Suporta curingas como '*.example.com' (corresponde a sub.example.com,
    # deep.nested.example.com e o próprio example.com) e nomes de ecossistema como
    # 'python', 'node'.

# Configuração de sandbox para motores de IA. Controla o sandbox do agente (AWF) e
# o gateway MCP. O gateway MCP é sempre habilitado e não pode ser desabilitado.
# (opcional)
# Formatos aceitos:

# Formato 1: Formato de string para tipo de sandbox: 'default' para sem sandbox,
# 'awf' para Agent Workflow Firewall. Nota: Valores legados 'srt' e
# 'sandbox-runtime' são migrados automaticamente para 'awf'
sandbox: "default"

# Formato 2: Formato de objeto para configuração de sandbox completa com agente e
# opções de mcp
sandbox:
  # Campo de tipo de sandbox legado (use agent em vez disso). Nota: Valores legados
  # 'srt' e 'sandbox-runtime' são migrados automaticamente para 'awf'
  # (opcional)
  type: "default"

  # Tipo de sandbox do agente: 'awf' usa AWF (Agent Workflow Firewall), ou false para
  # desabilitar o sandbox do agente. Assume como padrão 'awf' se não especificado.
  # Nota: Desabilitar o sandbox do agente (false) remove a proteção de firewall, mas
  # mantém o gateway MCP habilitado.
  # (opcional)
  # Formatos aceitos:

  # Formato 1: Defina como false para desabilitar o sandbox do agente (firewall).
  # Aviso: Isso remove a proteção de firewall, mas mantém o gateway MCP habilitado.
  # Não permitido no modo estrito.
  agent: true

  # Formato 2: Tipo de sandbox: 'awf' para Agent Workflow Firewall
  agent: "awf"

  # Formato 3: Configuração de runtime de sandbox personalizada
  agent:
    # Identificador do agente (substitui o campo 'type' no novo formato): 'awf' para
    # Agent Workflow Firewall
    # (opcional)
    id: "awf"

    # Legado: Tipo de sandbox a ser usado (use 'id' em vez disso)
    # (opcional)
    type: "awf"

    # Substituição de versão do AWF usada para instalar e executar a versão do
    # firewall correspondente.
    # (opcional)
    version: "valor-exemplo"

    # Montagens de container para adicionar ao usar AWF. Cada montagem é especificada
    # usando a sintaxe de montagem do Docker: 'source:destination:mode' onde mode
    # pode ser 'ro' (somente leitura) ou 'rw' (leitura e escrita). Exemplo:
    # '/host/path:/container/path:ro'
    # (opcional)
    mounts: []
      # Itens de array: Especificação de montagem no formato
      # 'source:destination:mode'

    # Limite de memória para o container AWF (ex: '4g', '8g'). Passado como
    # --memory-limit para o AWF. Se não especificado, o limite de memória padrão do
    # AWF é usado.
    # (opcional)
    memory: "valor-exemplo"

    # Configuração de runtime de sandbox personalizada. Nota: A configuração de rede
    # é controlada pelo campo 'network' de nível superior, não aqui.
    # (opcional)
    config:
      # Configuração de controle de acesso ao sistema de arquivos para o agente dentro
      # do sandbox. Controla permissões de leitura/escrita e restrições de caminho.
      # (opcional)
      filesystem:
        # Lista de caminhos para negar acesso de leitura
        # (opcional)
        denyRead: []
          # Array de strings

        # Lista de caminhos para permitir acesso de escrita
        # (opcional)
        allowWrite: []
          # Array de strings

        # Lista de caminhos para negar acesso de escrita
        # (opcional)
        denyWrite: []
          # Array de strings

      # Mapa de padrões de comando para caminhos que devem ignorar violações
      # (opcional)
      ignoreViolations:
        {}

      # Habilitar modo de sandbox aninhado mais fraco (recomendado: true para acesso
      # ao Docker)
      # (opcional)
      enableWeakerNestedSandbox: true

  # Configuração de Runtime de Sandbox personalizada legada (use agent.config em vez
  # disso). Nota: A configuração de rede é controlada pelo campo 'network' de nível
  # superior, não aqui.
  # (opcional)
  config:
    # Configuração de controle de acesso ao sistema de arquivos para fluxos de
    # trabalho sandboxed. Controla permissões de leitura/escrita e restrições de
    # caminho para operações de arquivo.
    # (opcional)
    filesystem:
      # Array de padrões de caminho que negam acesso de leitura no ambiente
      # sandboxed. Tem precedência sobre outras permissões de leitura.
      # (opcional)
      denyRead: []
        # Array de strings

      # Array de padrões de caminho que permitem acesso de escrita no ambiente
      # sandboxed. Caminhos fora desses padrões são somente leitura.
      # (opcional)
      allowWrite: []
        # Array de strings

      # Array de padrões de caminho que negam acesso de escrita no ambiente
      # sandboxed. Tem precedência sobre outras permissões de escrita.
      # (opcional)
      denyWrite: []
        # Array de strings

    # Quando true, registra violações de sandbox sem bloquear a execução. Útil para
    # depuração e aplicação gradual de políticas de sandbox.
    # (opcional)
    ignoreViolations:
      {}

    # Quando true, permite que processos de sandbox aninhados sejam executados com
    # restrições relaxadas. Necessário para certas ferramentas containerizadas que
    # geram subprocessos.
    # (opcional)
    enableWeakerNestedSandbox: true

  # Configuração do Gateway MCP para rotear chamadas de servidor MCP por meio de um
  # gateway HTTP unificado. Requer que a feature flag 'mcp-gateway' esteja habilitada.
  # De acordo com a Especificação do Gateway MCP v1.0.0: Apenas execução baseada em
  # container é suportada.
  # (opcional)
  mcp:
    # Montagens de volume para o container do gateway MCP. Cada montagem é
    # especificada usando a sintaxe de montagem do Docker: 'source:destination:mode'
    # onde mode pode ser 'ro' (somente leitura) ou 'rw' (leitura e escrita). Exemplo:
    # '/host/data:/container/data:ro'
    # (opcional)
    mounts: []
      # Itens de array: Especificação de montagem no formato
      # 'source:destination:mode'

    # Variáveis de ambiente para gateway MCP
    # (opcional)
    env:
      {}

    # Número da porta para o servidor HTTP do gateway MCP (padrão: 8080)
    # (opcional)
    port: 1

    # Chave de API para autenticação com o gateway MCP (suporta sintaxe ${{
    # secrets.* }})
    # (opcional)
    api-key: "valor-exemplo"

    # Domínio do gateway para geração de URL (padrão: 'host.docker.internal' quando o
    # agente está habilitado, 'localhost' quando desabilitado)
    # (opcional)
    domain: "localhost"

    # Intervalo de ping keepalive em segundos para backends MCP HTTP. Envia pings
    # periódicos para impedir a expiração da sessão durante tarefas de agente de
    # longa duração. Defina como -1 para desabilitar pings keepalive. Não definido ou
    # 0 usa o padrão do gateway (1500 segundos = 25 minutos).
    # (opcional)
    keepalive-interval: 1

# Expressão de execução condicional
# (opcional)
if: "valor-exemplo"

# Passos de fluxo de trabalho personalizados
# (opcional)
# Formatos aceitos:

# Format 1: objeto
steps:
  {}

# Format 2: array
steps: []
  # Itens de array: indefinido

# Passos de fluxo de trabalho personalizados para executar bem no início do job do
# agente, antes do checkout e de quaisquer outros passos embutidos. Use pré-passos
# para emitir tokens de curta duração ou realizar qualquer configuração que deva
# ocorrer antes que o repositório seja verificado (check out). As saídas dos passos
# estão disponíveis via ${{ steps.<id>.outputs.<name> }} e podem ser referenciadas
# em checkout.token para evitar problemas de limite de fronteira de job cruzado de
# valor mascarado.
# (opcional)
# Formatos aceitos:

# Format 1: objeto
pre-steps:
  {}

# Format 2: array
pre-steps: []
  # Itens de array: indefinido

# Passos de fluxo de trabalho personalizados para executar imediatamente antes da
# execução da IA, após todos os passos de inicialização e configuração no job do
# agente.
# (opcional)
# Formatos aceitos:

# Format 1: objeto
pre-agent-steps:
  {}

# Format 2: array
pre-agent-steps: []
  # Itens de array: indefinido