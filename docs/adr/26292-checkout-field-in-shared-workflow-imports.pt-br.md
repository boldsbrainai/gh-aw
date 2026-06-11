# ADR-26292: Suporte ao campo `checkout` em Workflows Compartilhados Importáveis com Semântica de Mesclagem Append-After-Main

**Data**: 2026-04-14
**Status**: Rascunho
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O compilador do GitHub Agentic Workflows (gh-aw) permite que arquivos de workflow compartilhados sejam importados por workflows principais, permitindo configuração reutilizável para passos, ferramentas, permissões e campos similares. No entanto, o campo `checkout` — usado para configurar checkouts de repositório adicionais para workflows SideRepoOps — só podia ser declarado no arquivo de workflow principal. Isso forçava cada workflow que precisava fazer checkout de um repositório alvo compartilhado a duplicar um bloco `checkout:` idêntico, tornando os workflows compartilhados menos autossuficientes e violando o princípio DRY em muitos padrões SideRepoOps na base de código.

### Decisão

Permitiremos que o campo `checkout` seja declarado em arquivos de workflow compartilhados importáveis. As entradas de checkout importadas são anexadas *após* as entradas de checkout do workflow principal, de modo que a lógica de deduplicação do `CheckoutManager` existente — que usa o par de chaves `(repositório, caminho)` e uma estratégia de "primeiro visto vence"— naturalmente dá às entradas do workflow principal precedência incondicional sobre qualquer valor importado. Se o workflow principal definir `checkout: false`, toda a configuração de checkout, incluindo quaisquer entradas originadas de arquivos importados, é suprimida inteiramente. Internamente, as configs de checkout importadas são acumuladas como valores JSON separados por nova linha (um por arquivo importado) em um novo campo `MergedCheckout` em `ImportsResult`, então parseadas e anexadas no orquestrador do compilador.

### Alternativas Consideradas

#### Alternativa 1: Continuar exigindo que o workflow principal declare toda a config de checkout (Status Quo)

Cada workflow principal consumindo um padrão SideRepoOps compartilhado deve repetir o mesmo bloco `checkout:`. Esta é a implementação mais simples, mas contradiz o objetivo de tornar os workflows compartilhados totalmente autossuficientes e cria risco de drift quando o repositório alvo ou branch muda entre múltiplos workflows consumidores.

#### Alternativa 2: Estratégia de "First-Import-Wins" (Como `github-app`)

Aceitar apenas o primeiro `checkout:` encontrado em todos os arquivos importados e descartar quaisquer subsequentes. Isso espelha a estratégia usada para `github-app`. Foi rejeitada porque `checkout` é um campo de lista que pode legitimamente agregar entradas de repositório distintas de múltiplos imports independentes (ex.: um workflow compartilhado contribui repo-a, outro contribui repo-b). Descartar todos, exceto o primeiro import, descartaria silenciosamente configurações válidas.

#### Alternativa 3: Erro em pares `(repositório, caminho)` duplicados entre Imports (Como `env`)

Exibir um erro de compilação rígido quando dois arquivos importados definem um checkout para o mesmo par de chaves `(repositório, caminho)`. Isso foi considerado para consistência com a semântica de mesclagem de `env`, mas rejeitado porque a deduplicação "primeiro visto vence" existente do `CheckoutManager` já é o contrato documentado e testado para mesclagem de checkout. Adicionar um erro aqui restringiria casos de uso válidos (ex.: um import que por acaso duplica um checkout já presente no workflow principal) e é desnecessário, dado que o workflow principal já tem autoridade clara de override.

#### Alternativa 4: Introduzir um campo `shared-checkout:` dedicado

Adicionar um campo de frontmatter separado (ex.: `shared-checkout:` ou `imported-checkout:`) para evitar conflitar a intenção de checkout local com a herdada. Foi rejeitada porque introduz complexidade de nomenclatura desnecessária, exigiria mudanças na documentação e no parser para um novo campo, e o nome do campo `checkout:` já carrega o significado semântico correto, independentemente da origem.

### Consequências

#### Positivas
- Arquivos de workflow compartilhados para padrões SideRepoOps agora podem centralizar o bloco `checkout:`, eliminando repetição em todo workflow consumidor.
- O workflow principal retém autoridade total de override: suas entradas sempre têm precedência via deduplicação `(repositório, caminho)` do `CheckoutManager` (primeiro visto vence), consistente com o invariante "workflow principal é a fonte da verdade" estabelecido para outros campos mesclados.
- `checkout: false` no workflow principal continua a atuar como uma supressão rígida, desabilitando todo checkout, independentemente do que os imports definem.
- A implementação reutiliza a convenção de serialização JSON separada por nova linha já usada para outros campos mesclados de múltiplos imports (`MergedJobs`, `MergedEnv`, etc.).

#### Negativas
- A semântica de mesclagem (anexar após o principal, deduplicação silenciosa) é mais sutil do que um simples override ou um erro explícito — autores de workflow devem entender que pares `(repositório, caminho)` duplicados de imports são descartados silenciosamente, não sinalizados.
- `checkout: false` agora suprime entradas de checkout importadas, o que pode ser surpreendente para autores que esperam que o `checkout: false` do workflow principal afete apenas sua própria config declarada localmente.
- `ImportsResult`, `importAccumulator` e o orquestrador do compilador ganham novos campos e lógica, aumentando a superfície estrutural do pipeline do compilador.

#### Neutras
- O novo comportamento é aditivo: workflows existentes sem `checkout:` em seus imports compartilhados não são afetados; nenhuma migração é necessária.
- O padrão de acumulação JSON-por-linha em `MergedCheckout` é consistente com `MergedJobs` e `MergedCaches`, mantendo a abordagem interna de serialização uniforme.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Autorização do Campo Checkout em Imports Compartilhados

1. Imports de workflows compartilhados **DEVEM** ter permissão para declarar um campo `checkout:`; o compilador **NÃO DEVE** tratar `checkout` como um campo proibido em arquivos de workflow compartilhados.
2. A chave `checkout` **NÃO DEVE** aparecer em `SharedWorkflowForbiddenFields`.
3. O campo `checkout:` de um workflow compartilhado **MAY** ser um único objeto ou um array de objetos; o extrator **DEVE** lidar com ambas as formas.
4. Um valor `checkout: false` de um workflow compartilhado **DEVE** ser ignorado silenciosamente pelo extrator de import (a semântica de supressão `false` aplica-se apenas à declaração do workflow principal).

### Semântica de Mesclagem de Checkout

1. Entradas de checkout importadas **DEVEM** ser anexadas após as entradas de checkout do workflow principal em `workflowData.CheckoutConfigs` de modo que a deduplicação de pares `(repositório, caminho)` do `CheckoutManager` (primeiro visto vence) dê precedência incondicional às entradas do workflow principal.
2. Quando o workflow principal declara `checkout: false`, o compilador **NÃO DEVE** anexar quaisquer entradas de checkout importadas; `workflowData.CheckoutDisabled` **DEVE** permanecer `true` independentemente do que os arquivos importados definem.
3. Quando o workflow principal não declara `checkout: false`, as entradas de checkout importadas **DEVEM** ser parseadas e anexadas ao `workflowData.CheckoutConfigs` após as entradas do workflow principal, na ordem em que aparecem nos imports.
4. Pares `(repositório, caminho)` duplicados entre imports **DEVEM** ser resolvidos pela lógica de deduplicação do `CheckoutManager` existente (primeiro visto vence); o compilador **NÃO DEVE** retornar um erro para tais duplicatas.

### Modelo de Dados Interno

1. `ImportsResult` **DEVE** expor um campo `MergedCheckout string` contendo valores de checkout codificados em JSON separados por nova linha acumulados de todos os arquivos importados.
2. A struct `importAccumulator` **DEVE** manter uma slice `checkouts []string`, onde cada elemento é o JSON bruto de um único valor `checkout:` importado (objeto ou array).
3. Implementações **DEVEM** serializar `MergedCheckout` como `strings.Join(acc.checkouts, "\n")`, consistente com a convenção de JSON separado por nova linha usada para outros campos acumulados de múltiplos imports.
4. Implementações **NÃO DEVEM** incluir valores JSON `"null"` ou `"false"` na slice `checkouts`; tais valores de arquivos importados **DEVEM** ser pulados silenciosamente.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. Especificamente: o campo `checkout` é aceito em imports compartilhados sem aviso; `checkout: false` em um import compartilhado é ignorado silenciosamente; entradas de checkout importadas são anexadas após as entradas do workflow principal para que o workflow principal tenha precedência; `checkout: false` no workflow principal suprime todas as entradas de checkout importadas; e a representação interna usa JSON separado por nova linha em `ImportsResult.MergedCheckout`. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um ADR de RASCUNHO gerado pelo workflow [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24424945242) workflow. O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
