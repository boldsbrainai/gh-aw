# Sintaxe de Importação em Tempo de Execução (Runtime)

Este documento descreve a funcionalidade de sintaxe de importação em tempo de execução para os GitHub Agentic Workflows.

## Visão Geral

A sintaxe de importação em tempo de execução permite incluir conteúdo de arquivos e URLs diretamente nos seus prompts de fluxo de trabalho (workflow) durante a execução. Isso fornece uma maneira conveniente de referenciar conteúdo externo usando a macro `{{#runtime-import}}`.

**Importante:** Os caminhos de arquivo são resolvidos dentro da pasta `.github`. Os caminhos são validados para garantir que permaneçam dentro da raiz do repositório git por motivos de segurança.

## Segurança

**Validação de Caminho**: Todos os caminhos de arquivo são validados para garantir que permaneçam dentro da pasta `.github`:

- Os caminhos são normalizados para resolver componentes `.` e `..`.
- Após a normalização, o caminho resolvido deve estar dentro da pasta `.github`.
- Tentativas de sair da pasta (ex: `../../../etc/passwd`) são rejeitadas com um erro de segurança.
- Exemplo: `.github/a/b/../../c/file.txt` é permitido se for resolvido para `.github/c/file.txt`.

## Sintaxe

### Importação de Arquivo

**Arquivo Completo**: `{{#runtime-import caminho_do_arquivo}}`

- Inclui todo o conteúdo do arquivo a partir da pasta `.github`.
- O caminho pode ser especificado com ou sem o prefixo `.github/`.
- Exemplo: `{{#runtime-import docs/README.md}}` ou `{{#runtime-import .github/docs/README.md}}`

**Intervalo de Linhas**: `{{#runtime-import caminho_do_arquivo:inicio-fim}}`

- Inclui linhas específicas do arquivo (indexação baseada em 1, inclusiva).
- O início e o fim são números de linha.
- Exemplo: `{{#runtime-import src/main.go:10-20}}` inclui as linhas 10 a 20.

### Importação de URL

**URLs HTTP/HTTPS**: `{{#runtime-import https://exemplo.com/arquivo.txt}}`

- Busca o conteúdo da URL.
- O conteúdo é armazenado em cache por 1 hora para reduzir as solicitações de rede.
- O cache é armazenado em `/tmp/gh-aw/url-cache/`.
- Exemplo: `{{#runtime-import https://raw.githubusercontent.com/owner/repo/main/README.md}}`

## Funcionalidades

### Sanitização de Conteúdo

Todo o conteúdo importado é automaticamente sanitizado:

- **Remoção de Front Matter**: O front matter YAML (entre os delimitadores `---`) é removido.
- **Remoção de Comentários XML**: Comentários HTML/XML (`<!-- ... -->`) são removidos.
- **Detecção de Macros do GitHub Actions**: Conteúdo que contenha expressões `${{ ... }}` é rejeitado com um erro.

## Exemplos

### Exemplo 1: Incluir Documentação

```markdown
---
description: Fluxo de trabalho de revisão de código
on: pull_request
engine: copilot
---

# Agente de Revisão de Código

Por favor, revise as seguintes alterações de código.

## Diretrizes de Codificação

{{#runtime-import docs/coding-guidelines.md}}

## Resumo das Alterações

Revise as alterações e forneça feedback.
```

### Exemplo 2: Incluir Linhas Específicas

```markdown
---
description: Validador de correção de bug
on: pull_request
engine: copilot
---

# Validador de Correção de Bug

O código original com erro era:

{{#runtime-import src/auth.go:45-52}}

Verifique se a correção aborda o problema.
```

### Exemplo 3: Checklist Externo

```markdown
---
description: Revisão de segurança
on: pull_request
engine: copilot
---

# Revisão de Segurança

Siga este checklist de segurança:

{{#runtime-import https://raw.githubusercontent.com/org/security/main/checklist.md}}

Revise as alterações em busca de vulnerabilidades de segurança.
```

Verifique se a correção aborda o problema.
```

### Exemplo 3 (repetido/variante): Incluir Conteúdo Remoto

```markdown
---
description: Verificação de segurança
on: pull_request
engine: copilot
---

# Revisão de Segurança

Siga estas diretrizes de segurança:

@https://raw.githubusercontent.com/organization/security-guidelines/main/checklist.md

Revise todas as alterações de código em busca de vulnerabilidades de segurança.
```

## Ordem de Processamento

A inclusão (inlining) de arquivos e URLs ocorre como parte do sistema de importação em tempo de execução:

1. As referências `@./caminho` e `@url` são convertidas em macros `{{#runtime-import}}`.
2. Todas as macros `{{#runtime-import}}` são processadas (arquivos e URLs juntos).
3. Ocorre a interpolação de variáveis `${GH_AW_EXPR_*}`.
4. As condicionais de template `{{#if}}` são renderizadas.

A sintaxe `@` é puro açúcar sintático — ela simplesmente é convertida para `{{#runtime-import}}` antes do processamento.

## Tratamento de Erros

### Arquivo Não Encontrado

Se um arquivo referenciado não existir, o fluxo de trabalho falhará com um erro:
```
Failed to process runtime import for ./missing.txt: Runtime import file not found: ./missing.txt
```

### Intervalo de Linhas Inválido

Se os números das linhas estiverem fora dos limites, o fluxo de trabalho falhará:
```
Invalid start line 100 for file ./src/main.go (total lines: 50)
```

### Formato de Caminho Inválido

Se um caminho de arquivo não começar com `./` ou `../`, ele será ignorado:
```
@docs/file.md  # NÃO processado - permanece como texto simples
@./docs/file.md  # Processado corretamente
```

### Violação de Segurança de Caminho

Se um caminho tentar sair da raiz do git, o fluxo de trabalho falhará:
```
Security: Path ../../../etc/passwd resolves outside git root (/workspace)
```

### Falha na Busca de URL

Se uma URL não puder ser buscada, o fluxo de trabalho falhará:
```
Failed to process runtime import for https://example.com/file.txt: Failed to fetch URL https://example.com/file.txt: HTTP 404
```

### Macros do GitHub Actions

Se o conteúdo incluído contiver expressões do GitHub Actions, o fluxo de trabalho falhará:
```
File ./docs/template.md contains GitHub Actions macros (${{ ... }}) which are not allowed in runtime imports
```

## Limitações

- Os caminhos de arquivo DEVEM começar com `./` ou `../` — caminhos sem esses prefixos são ignorados.
- Os caminhos resolvidos devem permanecer dentro da raiz do repositório git (imposto via verificações de segurança).
- A normalização do caminho é realizada para resolver componentes `.` e `..` antes da validação.
- Os intervalos de linhas são aplicados ao conteúdo bruto do arquivo (antes da remoção do front matter).
- As URLs são armazenadas em cache por 1 hora; um cache mais longo requer a reexecução manual do fluxo de trabalho.
- Arquivos ou URLs grandes podem impactar o desempenho do fluxo de trabalho.
- Erros de rede para referências de URL farão o fluxo de trabalho falhar.

## Detalhes de Implementação

A funcionalidade é implementada usando um sistema de importação em tempo de execução unificado com validação de segurança:

1. **`convertInlinesToMacros()`**: Converte `@./caminho` e `@url` para macros `{{#runtime-import}}`.
2. **`processRuntimeImport()`**: Trata tanto arquivos quanto URLs com sanitização e verificações de segurança.
   - Para arquivos: Resolve e normaliza o caminho, valida se permanece dentro da raiz do git.
   - Para URLs: Busca o conteúdo com cache.
3. **`processRuntimeImports()`**: Processa todas as macros de importação em tempo de execução (assíncrono).

A sintaxe `@` é puro açúcar sintático que se converte em macros `{{#runtime-import}}`.

## Testes

A funcionalidade inclui uma cobertura de testes abrangente:

- Mais de 75 testes unitários em `runtime_import.test.cjs`.
- Testes para inclusão de arquivo completo com prefixos `./` e `../`.
- Testes para extração de intervalo de linhas.
- Testes para busca e cache de URL.
- Testes para condições de erro.
- Testes para filtragem de endereços de e-mail.
- Testes para sanitização de conteúdo.

## Documentação Relacionada

- Macros de Importação em Tempo de Execução: `{{#runtime-import caminho_do_arquivo}}`
- Interpolação de Variáveis: `${GH_AW_EXPR_*}`
- Condicionais de Template: `{{#if condicao}}`
