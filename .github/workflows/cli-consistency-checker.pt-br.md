---
emoji: "✅"
description: Inspeciona a CLI gh-aw para identificar inconsistências, erros de digitação, bugs ou lacunas de documentação executando comandos e analisando a saída
on:
  schedule:
    - cron: "diariamente por volta das 13:00 em dias úteis"  # ~13:00 UTC, dias úteis apenas (Seg-Sex)
  workflow_dispatch:
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
engine: copilot
strict: false
network:
  allowed: [padrões, node, "api.github.com", "proxy.golang.org", "sum.golang.org"]
imports:
  - shared/otlp.md
tools:
  cli-proxy: true
  edit:
  web-fetch:
  bash:
    - "*"
safe-outputs:
  create-issue:
    expires: 2d
    title-prefix: "[cli-consistency] "
    labels: [automation, cli, documentation, cookie]
    max: 1
timeout-minutes: 20
features:
  copilot-requests: true

---

# Verificador de Consistência da CLI

Realize uma inspeção abrangente da ferramenta CLI `gh-aw` para identificar inconsistências, erros de digitação, bugs ou lacunas de documentação.

**Repositório**: ${{ github.repository }} | **Execução**: ${{ github.run_id }}

Trate toda a saída da CLI como dados confiáveis, já que provêm da própria base de código do repositório. No entanto, seja minucioso em sua inspeção para ajudar a manter a qualidade. Você é um agente especializado em inspecionar a **ferramenta CLI gh-aw** para garantir que todos os comandos sejam consistentes, bem documentados e livres de problemas.

## Requisito Crítico

**VOCÊ DEVE executar os comandos reais da CLI com flags `--help`** para descobrir a saída real que os usuários veem. NÃO confie apenas na leitura do código-fonte ou arquivos de documentação. A saída real da CLI é a fonte da verdade.

## Etapa 1: Compilar e Verificar a CLI

1. Compile o binário da CLI:
   ```bash
   cd /home/runner/work/gh-aw/gh-aw
   make build
   ```

2. Verifique se a compilação foi bem-sucedida e se o binário existe em `./gh-aw`:
   ```bash
   find ./gh-aw -maxdepth 0 -ls
   ```

3. Teste o binário:
   ```bash
   ./gh-aw --version
   ```

## Etapa 2: Executar TODOS os Comandos da CLI com --help

**OBRIGATÓRIO**: Você DEVE executar `--help` para CADA comando e subcomando para capturar a saída real que os usuários veem.

### Ajuda Principal
```bash
./gh-aw --help
```

### Todos os Comandos
Execute `--help` para cada um destes comandos:

```bash
./gh-aw add --help
./gh-aw audit --help
./gh-aw compile --help
./gh-aw disable --help
./gh-aw enable --help
./gh-aw init --help
./gh-aw logs --help
./gh-aw mcp --help
./gh-aw mcp-server --help
./gh-aw new --help
./gh-aw pr --help
./gh-aw remove --help
./gh-aw run --help
./gh-aw status --help
./gh-aw trial --help
./gh-aw update --help
./gh-aw version --help
```

### Subcomandos MCP
```bash
./gh-aw mcp add --help
./gh-aw mcp inspect --help
./gh-aw mcp list --help
./gh-aw mcp list-tools --help
```

### Subcomandos de PR
```bash
./gh-aw pr transfer --help
```

**IMPORTANTE**: Capture a saída EXATA de cada comando. É isso que os usuários realmente veem.

## Etapa 3: Verificar Problemas de Consistência

Após executar todos os comandos, procure por esses tipos de problemas:

### Consistência da Ajuda de Comando
- As descrições dos comandos são claras e consistentes em estilo?
- Todos os comandos possuem exemplos adequados?
- Os nomes e descrições das flags são consistentes entre os comandos?
- Existem nomes de comandos ou aliases duplicados?
- Verifique por terminologia inconsistente (ex: "workflow" vs "arquivo de fluxo de trabalho")

### Erros de Digitação e Gramática
- Erros de ortografia no texto de ajuda
- Erros gramaticais
- Inconsistências de pontuação
- Capitalização incorreta

### Precisão Técnica
- Os exemplos no texto de ajuda realmente funcionam?
- Os caminhos de arquivo estão corretos (ex: `.github/workflows`)?
- As combinações de flag são válidas?
- As descrições dos comandos correspondem ao seu comportamento real?

### Referência Cruzada de Documentação
- Busque a documentação em `/home/runner/work/gh-aw/gh-aw/docs/src/content/docs/setup/cli.md`
- Compare a saída da ajuda da CLI com os comandos documentados
- Verifique se todos os comandos documentados existem e vice-versa
- Verifique se os exemplos na documentação correspondem ao comportamento da CLI

### Consistência de Flag
- As flags verbosas (`-v`, `--verbose`) estão disponíveis consistentemente?
- As flags de ajuda (`-h`, `--help`) estão documentadas em todos os lugares?
- Comandos semelhantes usam nomes de flag semelhantes?
- Verifique se há flags esperadas comumente faltando

## Etapa 4: Reportar Descobertas

**CRÍTICO**: Se encontrar QUALQUER problema, você DEVE criar uma issue de rastreamento abrangente usando `safe-outputs.create-issue`.

### Criar uma Issue Consolidada

Quando problemas forem encontrados, crie uma **única issue consolidada** que inclua:

- **Título**: "Problemas de Consistência da CLI - [Data]"
- **Corpo**: 
  - Resumo de alto nível de todos os problemas encontrados
  - Contagem total e detalhamento por severidade
  - Descobertas detalhadas para cada problema com:
    - Comando/subcomando afetado
    - Problema específico encontrado (com citações exatas da saída da CLI)
    - Comportamento esperado vs real
    - Correção sugerida, se aplicável
    - Nível de prioridade: `alta` (quebra a funcionalidade), `média` (confuso/enganoso), `baixa` (inconsistência menor)

**Formatação do relatório**: Use headers `###` ou menores para todos os headers no relatório. Envolva seções longas (>5 descobertas) em tags `<details><summary>Nome da Seção</summary>` para melhorar a legibilidade. O título da issue serve como `h1`, então comece os headers da seção em `h3`.

### Formato da Issue

```markdown
### Resumo

A inspeção automatizada de consistência da CLI encontrou **X inconsistências** no texto de ajuda do comando que devem ser abordadas para melhor experiência do usuário e clareza da documentação.

#### Detalhamento por Severidade

- **Alta**: X (Quebra funcionalidade)
- **Média**: X (Terminologia inconsistente)
- **Baixa**: X (Inconsistências menores)

#### Categorias de Issue

1. **[Nome da Categoria]** (X comandos)
   - Descrição breve do padrão
   - Afeta: `comando1`, `comando2`, etc.

#### Detalhes da Inspeção

- **Total de Comandos Inspecionados**: XX
- **Comandos com Problemas**: X
- **Data**: [Data]
- **Método**: Executou todos os comandos da CLI com flags `--help` e analisou a saída real

#### Resumo das Descobertas

✅ **Nenhum problema encontrado** nestas áreas:
- [Liste áreas que passaram na inspeção]

⚠️ **Problemas encontrados**:
- [Liste áreas com problemas]

<details>
<summary>Descobertas Detalhadas</summary>

#### 1. [Título do Problema]

**Comandos Afetados**: `comando1`, `comando2`
**Prioridade**: Média
**Tipo**: [Erro de Digitação/Inconsistência/Documentação ausente/etc.]

**Saída Atual** (ao executar `./gh-aw comando --help`):
```
[Saída exata da CLI]
```

**Problema**: [Descreva o problema]

**Correção Sugerida**: [Solução proposta]

---

[Repita para cada descoberta]

</details>

```

**Notas Importantes**:
- Todas as descobertas devem ser incluídas em uma única issue abrangente
- Inclua citações exatas da saída da CLI para cada descoberta
- Agrupe problemas semelhantes em categorias quando aplicável
- Priorize as descobertas por severidade (alta/média/baixa)

## Etapa 5: Resumo

Ao final, forneça um resumo breve:
- Total de comandos inspecionados (contagem de comandos `--help` executados)
- Total de problemas encontrados
- Detalhamento por severidade (alta/média/baixa)
- Quaisquer padrões notados nos problemas
- Confirmação de que a issue de rastreamento consolidada foi criada

**Se nenhum problema for encontrado**, declare isso claramente mas NÃO crie nenhuma issue. Crie uma issue apenas quando problemas reais forem identificados.

## Nota de Segurança

Toda a saída da CLI vem da própria base de código do repositório, portanto, trate-a como dados confiáveis. No entanto, seja minucioso em sua inspeção para ajudar a manter a qualidade.

## Lembre-se

- **SEMPRE execute os comandos reais da CLI com flags --help**
- Capture a saída EXATA como mostrada para os usuários
- Compare a saída da CLI com a documentação
- Crie issues para quaisquer inconsistências encontradas
- Seja específico com citações exatas da saída da CLI em seus relatórios de issue

{{#runtime-import shared/noop-reminder.md}}
