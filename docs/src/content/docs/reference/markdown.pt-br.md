---
title: Markdown
description: Aprenda sobre o conteúdo markdown de fluxos de trabalho agentic
sidebar:
  order: 300
---

O corpo markdown é a parte mais importante do seu fluxo de trabalho agentic, contendo instruções em linguagem natural para o agente de IA. O markdown segue o frontmatter e é carregado em tempo de execução, permitindo que você edite as instruções diretamente no GitHub.com sem recompilação. Por exemplo:

```aw wrap
---
...frontmatter...
---

# Triagem de Issue

Leia a issue #${{ github.event.issue.number }}. Adicione um comentário à issue listando recursos e links úteis.
```

## Escrevendo Instruções Eficazes

Escreva as instruções como se estivesse explicando a tarefa para um novo membro da equipe. Seja específico, forneça contexto sobre seu projeto e restrições e estruture as instruções com cabeçalhos para orientar o fluxo de trabalho do agente.

```aw wrap
# Bom: Específico e acionável
Analise a issue #${{ github.event.issue.number }} e adicione labels apropriadas a partir da lista de labels do repositório. Foque em categorizar o tipo de issue (bug, funcionalidade, documentação) e nível de prioridade (alta, média, baixa).

# Contexto do Projeto
Este repositório segue versionamento semântico e GitHub Flow. Ao revisar pull requests, certifique-se de que todos os testes passem, a documentação esteja atualizada para mudanças na API e as mudanças que quebram a compatibilidade (breaking changes) estejam claramente marcadas.

# Relatório de Pesquisa Semanal

## Áreas de Pesquisa
Foque na análise da concorrência, tendências emergentes de desenvolvimento de IA e feedback da comunidade para ${{ github.repository }}.

## Formato de Saída
Crie um relatório estruturado com resumo executivo, principais descobertas por área e ações recomendadas.
```

Use linguagem orientada a ação com verbos claros (analisar, criar, atualizar, triar) e especifique os resultados esperados. Ajude os agentes a tomar decisões consistentes fornecendo critérios e exemplos:

```aw wrap
# Critérios de Labeling de Issue
Aplique labels: `bug` (comportamento incorreto com passos de reprodução), `enhancement` (novas funcionalidades), `question` (pedidos de ajuda), `documentation` (docs/exemplos). Prioridade: `high-priority` (segurança/bugs críticos), `medium-priority` (funcionalidades/bugs não críticos), `low-priority` (melhorias desejáveis).
```

Antecipe situações incomuns e condições de erro. Se um fluxo de trabalho falhar, documente a falha em uma issue com mensagens de erro e contexto, marque-a com 'workflow-failure' e saia normalmente sem alterações parciais.

## Organização de Conteúdo

Use listas numeradas para processos de várias etapas, declarações condicionais para tomada de decisão e templates para saída consistente:

```aw wrap
# Processo de Revisão de Código
1. Verifique se os checks de CI estão passando e se o PR tem título/descrição apropriados
2. Verifique problemas de qualidade de código e valide tratamento de erros/log
3. Crie comentários construtivos e resuma a avaliação

# Lógica de Triagem de Issue
Se mensagens de erro/stack traces: marque 'bug', verifique issues semelhantes, solicite informações se necessário
Se pedido de funcionalidade: marque 'enhancement', avalie escopo e complexidade
Caso contrário: marque 'question'/'discussion', forneça recursos

# Template de Relatório de Status
## Resumo: [atividades da semana]
## Principais Métricas: PRs mesclados, issues resolvidas, novos contribuidores
## Destaques: [conquistas, decisões]
## Próxima Semana: [prioridades planejadas]
```

## Armadilhas Comuns

Evite complexidade excessiva (mantenha as instruções focadas), assumir conhecimento (explique as convenções do projeto), formatação inconsistente, falta de tratamento de erros e critérios de sucesso vagos. Antes de implantar, leia as instruções em voz alta para verificar a clareza, revise os exemplos quanto à precisão e considere casos de borda (edge cases).

## Templating

O markdown agentic suporta substituições de expressão do GitHub Actions e templating condicional para conteúdo. Veja [Templating e Substituições](/gh-aw/reference/templating/) para detalhes.

## Edição e Iteração

Veja [Editando Fluxos de Trabalho](/gh-aw/guides/editing-workflows/) para orientação completa sobre quando a recompilação é necessária versus quando você pode editar diretamente.

## Escaneamento de Markdown

O corpo markdown dos fluxos de trabalho (excluindo frontmatter) é verificado automaticamente em busca de conteúdo malicioso ao ser adicionado via `gh aw add`, durante o modo de teste e no momento da compilação para arquivos importados. O scanner recusa fluxos de trabalho que contenham: abuso de Unicode (caracteres de largura zero, substituições bidirecionais), conteúdo oculto (comentários HTML suspeitos, elementos ocultos por CSS), links ofuscados (URIs de dados, URLs `javascript:`, URLs baseadas em IP, encurtadores de URL), tags HTML perigosas (`<script>`, `<iframe>`, `<object>`, `<form>`, manipuladores de eventos), conteúdo executável incorporado (scripts SVG, URIs de dados MIME executáveis) e padrões de engenharia social (injeção de prompt, comandos codificados em base64, padrões pipe-to-shell). Essas verificações não podem ser substituídas.

## Sub-Agentes Inline

Você pode definir sub-agentes diretamente dentro de um arquivo de fluxo de trabalho usando um delimitador de cabeçalho de nível 2:

```markdown
## agent: `name`
---
model: claude-haiku-4.5
description: Descrição curta do agente
---
Instruções do agente aqui.
```

Cada bloco de sub-agente termina no próximo cabeçalho `##` ou EOF. Em tempo de execução, os blocos são extraídos para `.agents/agents/<name>.agent.md`, onde a CLI do Copilot descobre e os invoca pelo nome.

Veja [Sub-Agentes Inline](/gh-aw/reference/inline-sub-agents/) para a referência completa de sintaxe.

## Documentação Relacionada

- [Editando Fluxos de Trabalho](/gh-aw/guides/editing-workflows/) - Quando recompilar vs editar diretamente
- [Estrutura do Fluxo de Trabalho](/gh-aw/reference/workflow-structure/) - Organização geral do arquivo de fluxo de trabalho
- [Frontmatter](/gh-aw/reference/frontmatter/) - Opções de configuração YAML
- [Sub-Agentes Inline](/gh-aw/reference/inline-sub-agents/) - Definindo sub-agentes dentro de um arquivo de fluxo de trabalho
- [Guia de Segurança](/gh-aw/introduction/architecture/) - Orientação de segurança abrangente
