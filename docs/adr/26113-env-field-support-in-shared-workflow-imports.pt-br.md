# ADR-26113: Suporte ao campo `env` em Imports de Workflows Compartilhados com Semântica de Erro de Conflito

**Data**: 2026-04-14
**Status**: Rascunho
**Decisores**: pelikhan, Copilot

---

## Parte 1 — Narrativa (Amigável)

### Contexto

O compilador do GitHub Agentic Workflows (gh-aw) suporta arquivos de workflow compartilhados que são importados por workflows principais. Esses arquivos compartilhados permitem que as equipes extraiam passos reutilizáveis, ferramentas, permissões e outras configurações para fragmentos componíveis. Antes desta mudança, o campo `env` era explicitamente listado em `SharedWorkflowForbiddenFields`, significando que qualquer bloco `env:` em um import compartilhado era silenciosamente descartado com um aviso. Isso impedia que workflows compartilhados declarassem variáveis de ambiente no nível do workflow (ex.: `TARGET_REPOSITORY`, `SHARED_CONFIG`), forçando os autores dos workflows a duplicar essas declarações em cada workflow principal consumidor — violando o princípio DRY (Don't Repeat Yourself) e tornando os workflows compartilhados menos autossuficientes.

### Decisão

Removeremos a restrição do `env` de imports de workflows compartilhados e implementaremos um modelo de precedência de três níveis: (1) as variáveis `env` do workflow principal sempre vencem qualquer valor importado, (2) conflitos de import-import no mesmo nome de variável são um erro de compilação rígido com uma mensagem acionável, e (3) quando não há conflito, variáveis de ambiente importadas são mescladas no arquivo de lock compilado. Adicionalmente, o cabeçalho do arquivo de lock listará todas as variáveis de ambiente com atribuição de origem (`(main workflow)` ou o caminho do arquivo de import) para auxiliar na auditabilidade. Este modelo torna o workflow principal o ponto de override autoritativo único enquanto impõe a resolução explícita de conflitos entre imports.

### Alternativas Consideradas

#### Alternativa 1: Estratégia de "Last-Write-Wins" entre Imports

A ordem de importação poderia determinar a precedência quando dois arquivos compartilhados definem a mesma variável de ambiente (ordem topológica de largura do grafo de importação). Isso evitaria exibir um erro, mas tornaria o comportamento silenciosamente dependente da ordem de declaração de importação, criando bugs sutis e difíceis de depurar quando arquivos compartilhados são reordenados ou quando um novo import compartilhado é adicionado que por acaso define a mesma variável.

#### Alternativa 2: Estratégia de "First-Write-Wins" entre Imports

Similar ao "last-write-wins", mas mais previsível na prática (o primeiro import declarado "possui" a variável). Ainda sofre da mesma dependência silenciosa de ordenação; as equipes não teriam sinal visível de que dois imports conflitam, levando a comportamento inesperado quando a lista de imports é editada.

#### Alternativa 3: Manter `env` Proibido em Imports Compartilhados (Status Quo)

Manter a restrição atual é simples e evita a complexidade da resolução de conflitos inteiramente. No entanto, força cada consumidor de um workflow compartilhado a redeclarar manualmente variáveis de ambiente que logicamente pertencem à preocupação compartilhada, tornando os workflows compartilhados menos reutilizáveis e aumentando o risco de drift entre cópias.

#### Alternativa 4: Permitir todos os Overrides Sem Atribuição de Origem

A mesclagem poderia ser feita sem rastrear qual import contribuiu para qual variável. Isso simplifica a implementação, mas sacrifica a transparência: quando um workflow compilado contém um valor de variável de ambiente inesperado, não há como determinar de onde ele veio sem reler cada arquivo importado.

### Consequências

#### Positivas
- Arquivos de workflow compartilhados são mais autossuficientes; variáveis de ambiente que logicamente pertencem a uma preocupação reutilizável podem ser colocadas junto com o resto da configuração compartilhada.
- Conflitos de import-import falham ruidosamente em tempo de compilação com uma mensagem de erro clara e acionável, em vez de produzir silenciosamente comportamento incorreto.
- Cabeçalhos de arquivo de lock agora listam todas as variáveis de ambiente com atribuição de origem, melhorando a auditabilidade de workflows compilados.
- O workflow principal retém autoridade de override incondicional, preservando o invariante "workflow principal é a fonte da verdade" já estabelecido para outros campos mesclados.

#### Negativas
- Autores de workflow que acidentalmente duplicaram a mesma variável de ambiente em dois imports compartilhados agora obterão um erro de compilação que devem resolver antes que seu workflow compile.
- A struct `importAccumulator` ganha dois novos campos (`envBuilder`, `envSources`) e os tipos `ImportsResult` e `WorkflowData` ganham novos campos, aumentando a complexidade estrutural.
- O cabeçalho do arquivo de lock cresce pelo número de variáveis de ambiente, o que pode aumentar ligeiramente o tamanho do arquivo gerado.

#### Neutras
- A abordagem de mesclagem de env (objetos JSON separados por nova linha) segue a mesma convenção interna de serialização já usada para outros campos mesclados (ex.: `MergedJobs`).
- Workflows existentes sem `env:` em seus imports compartilhados não são afetados; nenhuma migração é necessária.
- A atualização da lista de supressão `include_processor.go` (adicionando `"env"` aos campos de frontmatter de workflow válidos) remove um aviso espúrio que os usuários veriam se tivessem `env:` em um arquivo incluído.

---

## Parte 2 — Especificação Normativa (RFC 2119)

> As palavras-chave **DEVEM**, **NÃO DEVEM**, **OBRIGATÓRIO**, **SHALL**, **SHALL NOT**, **RECOMENDADO**, **MAY** e **OPCIONAL** nesta seção devem ser interpretadas conforme descrito em [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Autorização do Campo Env

1. Imports de workflows compartilhados **DEVEM** ter permissão para declarar um campo `env:`; o compilador **NÃO DEVE** tratar `env` como um campo proibido em arquivos de workflow compartilhados.
2. A chave `env` **NÃO DEVE** aparecer em `SharedWorkflowForbiddenFields`.
3. O campo `env` **NÃO DEVE** aparecer como um campo de frontmatter de não-workflow válido no processador de inclusão para suprimir avisos espúrios de campo desconhecido.

### Precedência de Mesclagem de Env

1. Variáveis de ambiente declaradas no workflow principal **DEVEM** ter precedência sobre qualquer variável de ambiente de um arquivo importado com a mesma chave; a saída compilada **DEVE** usar o valor do workflow principal.
2. Quando dois arquivos importados diferentes declaram a mesma chave de variável de ambiente, o compilador **DEVE** retornar um erro de compilação antes de produzir qualquer saída.
3. O erro de compilação para conflitos de import-import **DEVE** identificar o nome da variável conflitante e ambos os caminhos de arquivo de import, e **DEVE** incluir orientação sobre como resolver o conflito (ex.: mover a variável para o workflow principal ou removê-la de um import).
4. Variáveis de ambiente importadas que não conflitam entre si e não são sobrescritas pelo workflow principal **DEVEM** ser mescladas no bloco `env:` do workflow compilado.

### Atribuição de Origem

1. O cabeçalho do arquivo de lock compilado **DEVE** incluir uma seção `# Env variables:` listando toda variável de ambiente presente no bloco env mesclado.
2. Cada entrada na seção de variáveis de ambiente **DEVE** ser anotada com sua origem: `(main workflow)` se a variável originar do arquivo de workflow principal, ou o caminho do arquivo de import (relativo à raiz do repositório) se ela originar de um import compartilhado.
3. Chaves na seção de cabeçalho das variáveis de ambiente **DEVEM** ser emitidas em ordem ordenada (lexicográfica ascendente) para saída determinística.

### Modelo de Dados

1. `ImportsResult` **DEVE** expor um campo `MergedEnv string` contendo o JSON acumulado de variáveis de ambiente de todos os imports, e um campo `MergedEnvSources map[string]string` mapeando cada chave de variável de ambiente para seu caminho de import de origem.
2. `WorkflowData` **DEVE** expor um campo `EnvSources map[string]string` mapeando cada chave de variável de ambiente para seu rótulo de origem final (`(main workflow)` ou caminho de import) para uso na geração do cabeçalho do arquivo de lock.
3. Implementações **NÃO DEVEM** armazenar o blob env mesclado em qualquer formato que não seja objetos JSON separados por nova linha, consistente com a convenção existente para outros campos mesclados de múltiplos imports.

### Conformidade

Uma implementação é considerada em conformidade com este ADR se satisfizer todos os requisitos **DEVEM** e **NÃO DEVEM** acima. Especificamente: o campo `env` é aceito em imports compartilhados sem aviso, conflitos de import-import causam um erro de compilação rígido com uma mensagem informativa, variáveis de ambiente do workflow principal sempre sobrescrevem valores importados e o cabeçalho do arquivo de lock compilado lista todas as variáveis de ambiente com atribuição de origem em ordem ordenada. A falha em atender a qualquer requisito **DEVE** ou **NÃO DEVE** constitui não conformidade.

---

*Este é um ADR de RASCUNHO gerado pelo workflow [Design Decision Gate](https://github.com/github/gh-aw/actions/runs/24374798953). O autor do PR deve revisar, completar e finalizar este documento antes que o PR possa ser mesclado.*
