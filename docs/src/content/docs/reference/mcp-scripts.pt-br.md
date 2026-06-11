---
title: Scripts MCP
description: Defina ferramentas MCP personalizadas inline como JavaScript ou scripts shell com acesso a segredos, proporcionando criação leve de ferramentas sem dependências externas.
sidebar:
  order: 750
---

O elemento [`mcp-scripts:`](/gh-aw/reference/glossary/#mcp-scripts) permite que você defina ferramentas [MCP](/gh-aw/reference/glossary/#mcp-model-context-protocol) (Model Context Protocol) personalizadas diretamente no seu [frontmatter](/gh-aw/reference/glossary/#frontmatter) de fluxo de trabalho usando JavaScript, scripts shell ou Python. Essas ferramentas são geradas em tempo de execução e executadas como um servidor MCP HTTP **no runner do GitHub Actions, fora do container do agente**. O agente acessa o servidor via `host.docker.internal`, mantendo a execução da ferramenta isolada do sandbox de IA, enquanto ainda fornece acesso controlado a segredos.

> [!CAUTION]
> **Scripts MCP executam fora do sandbox do agente e devem implementar apenas operações de LEITURA.**
>
> Como Scripts MCP executam diretamente no host do runner do GitHub Actions — não dentro do container do agente isolado — eles podem acessar o sistema de arquivos, rede e ambiente do runner sem as restrições de segurança do sandbox. Implementar **operações de escrita** (criar arquivos, realizar pushes de commits, chamar APIs de mutação etc.) em Scripts MCP contorna a trilha de auditoria e os gates de aprovação que protegem seu repositório.
>
> - ✅ **Use Scripts MCP para**: ler dados, consultar APIs, buscar informações, realizar cálculos.
> - ❌ **Não use Scripts MCP para**: gravar arquivos, criar issues/PRs, modificar conteúdo do repositório ou qualquer outra ação de mutação.
>
> Para operações de escrita, use [Safe Output Jobs](/gh-aw/reference/safe-outputs/) ou [Custom Safe Output Jobs](/gh-aw/reference/custom-safe-outputs/) em vez disso. Esses são executados em um passo controlado e auditável separado da execução do agente de IA.

## Início Rápido

```yaml wrap
mcp-scripts:
  greet-user:
    description: "Cumprimentar um usuário pelo nome"
    inputs:
      name:
        type: string
        required: true
    script: |
      return { message: `Hello, ${name}!` };
```

O agente agora pode chamar `greet-user` com um parâmetro `name`.

## Definição de Ferramenta

Cada ferramenta mcp-script requer um nome único e configuração:

```yaml wrap
mcp-scripts:
  tool-name:
    description: "O que a ferramenta faz"  # Obrigatório
    inputs:                                # Parâmetros opcionais
      param1:
        type: string
        required: true
        description: "Descrição do parâmetro"
      param2:
        type: number
        default: 10
    script: |                          # Implementação JavaScript
      // Seu código aqui
    env:                               # Variáveis de ambiente
      API_KEY: "${{ secrets.API_KEY }}"
    timeout: 120                       # Opcional: timeout em segundos (padrão: 60)
```

Cada ferramenta requer `description:` e exatamente uma de `script:`, `run:`, `py:` ou `go:`.

## Ferramentas JavaScript (`script:`)

Ferramentas JavaScript encapsulam seu `script:` em `async function execute(inputs)` com entradas desestruturadas. Acesse segredos via `process.env`:

```yaml wrap
mcp-scripts:
  fetch-data:
    description: "Buscar dados da API"
    inputs:
      endpoint:
        type: string
        required: true
    script: |
      const apiKey = process.env.API_KEY;
      const response = await fetch(`https://api.example.com/${endpoint}`, {
        headers: { Authorization: `Bearer ${apiKey}` }
      });
      return await response.json();
    env:
      API_KEY: "${{ secrets.API_KEY }}"
```

## Ferramentas Shell (`run:`)

Scripts shell são executados em bash com entradas como variáveis de ambiente (ex: `repo` → `INPUT_REPO`):

```yaml wrap
mcp-scripts:
  list-prs:
    description: "Listar pull requests"
    inputs:
      repo:
        type: string
        required: true
      state:
        type: string
        default: "open"
    run: |
      gh pr list --repo "$INPUT_REPO" --state "$INPUT_STATE" --json number,title
    env:
      GH_TOKEN: "${{ secrets.GITHUB_TOKEN }}"
```

**Ferramenta gh CLI compartilhada**: Importe `shared/gh.md` para uma ferramenta gh reutilizável que aceita qualquer comando da CLI via parâmetro args.

## Ferramentas Python (`py:`)

Ferramentas Python são executadas usando `python3` com entradas disponíveis como um dicionário. Acesse entradas via `inputs.get('name')`, segredos via `os.environ` e retorne resultados imprimindo JSON para stdout:

```yaml wrap
mcp-scripts:
  analyze-data:
    description: "Analisar dados com Python"
    inputs:
      numbers:
        type: string
        description: "Números separados por vírgula"
        required: true
    py: |
      import json

      numbers_str = inputs.get('numbers', '')
      numbers = [float(x.strip()) for x in numbers_str.split(',') if x.strip()]

      result = {
          "count": len(numbers),
          "sum": sum(numbers),
          "average": sum(numbers) / len(numbers) if numbers else 0
      }

      print(json.dumps(result))
```

Python 3.10+ está disponível com módulos da biblioteca padrão. Instale pacotes adicionais inline usando pip se necessário.

## Ferramentas Go (`go:`)

Ferramentas Go são executadas usando `go run` com entradas fornecidas como um `map[string]any` analisado de stdin. Importações da biblioteca padrão (`encoding/json`, `fmt`, `io`, `os`) são incluídas automaticamente:

```yaml wrap
mcp-scripts:
  calculate:
    description: "Realizar cálculos com Go"
    inputs:
      a:
        type: number
        required: true
      b:
        type: number
        required: true
    go: |
      a := inputs["a"].(float64)
      b := inputs["b"].(float64)
      result := map[string]any{
          "sum": a + b,
          "product": a * b,
      }
      json.NewEncoder(os.Stdout).Encode(result)
```

Seu código Go recebe `inputs map[string]any` de stdin e deve enviar JSON para stdout. O código é encapsulado em um `package main` com uma função `main()` que lida com a análise de entrada.

Acesse segredos via `os.Getenv("VAR_NAME")` (veja [Variáveis de Ambiente](#environment-variables-env) para o campo `env:`).

## Parâmetros de Entrada

Defina parâmetros tipados com validação:

```yaml wrap
mcp-scripts:
  example-tool:
    description: "Exemplo com todas as opções de entrada"
    inputs:
      required-param:
        type: string
        required: true
        description: "Este parâmetro é obrigatório"
      optional-param:
        type: number
        default: 42
        description: "Este possui um valor padrão"
      choice-param:
        type: string
        enum: ["option1", "option2", "option3"]
        description: "Limitado a valores específicos"
```

## Configuração de Timeout

Defina o timeout de execução com o campo `timeout:` (padrão: 60 segundos):

```yaml wrap
mcp-scripts:
  slow-processing:
    description: "Processar grande conjunto de dados"
    timeout: 300  # 5 minutos (padrão: 60)
    py: |
      import json
      import time
      time.sleep(120)
      print(json.dumps({"status": "complete"}))
```

Aplicado para ferramentas shell (`run:`) e Python (`py:`). Ferramentas JavaScript (`script:`) são executadas em-processo sem aplicação de timeout.

## Variáveis de Ambiente (`env:`)

Passe segredos e configuração via `env:` (disponível em JavaScript via `process.env`, shell via `$VAR_NAME`):

```yaml wrap
mcp-scripts:
  secure-tool:
    description: "Ferramenta com múltiplos segredos"
    script: |
      const { API_KEY, API_SECRET } = process.env;
      // Use segredos...
    env:
      API_KEY: "${{ secrets.SERVICE_API_KEY }}"
      API_SECRET: "${{ secrets.SERVICE_API_SECRET }}"
```

Segredos usando `${{ secrets.* }}` são mascarados nos logs.

## Manipulação de Saída Grande

Quando a saída excede 500 caracteres, ela é salva em um arquivo. O agente recebe o caminho do arquivo, tamanho e uma visualização de esquema JSON (se aplicável).

## Importando Scripts MCP

Importe ferramentas de fluxos de trabalho compartilhados usando `imports:`. Definições de ferramenta locais substituem as importadas em caso de conflito de nomes:

```yaml wrap
imports:
  - shared/github-tools.md
```

## Exemplo Completo

```yaml wrap
---
on: workflow_dispatch
engine: copilot
imports:
  - shared/pr-data-mcp-script.md
mcp-scripts:
  analyze-text:
    description: "Analisar texto e retornar estatísticas"
    inputs:
      text:
        type: string
        required: true
    script: |
      const words = text.split(/\s+/).filter(w => w.length > 0);
      return {
        word_count: words.length,
        char_count: text.length,
        avg_word_length: (text.length / words.length).toFixed(2)
      };
safe-outputs:
  create-discussion:
    category: "General"
---

Analise o texto fornecido usando a ferramenta `analyze-text` e crie uma discussão com os resultados.
```

## Considerações de Segurança

Ferramentas Scripts MCP são executadas no **runner do GitHub Actions** — fora do container do agente — portanto, elas podem acessar o sistema de arquivos e ambiente do runner, mas estão isoladas do próprio ambiente de execução da IA. As ferramentas também fornecem isolamento de segredo (apenas env vars especificadas são encaminhadas), isolamento de processo (execução separada) e sanitização de saída (saídas grandes salvas em arquivos). Apenas ferramentas predefinidas estão disponíveis para os agentes.

## Comparação com Outras Opções

| Funcionalidade | Scripts MCP | Servidores MCP Personalizados | Ferramenta Bash |
|---------|-------------|-------------------|-----------|
| Setup | Inline no frontmatter | Serviço externo | Comandos simples |
| Linguagens | JavaScript, Shell, Python | Qualquer linguagem | Apenas Shell |
| Acesso a Segredo | Controlado via `env:` | Acesso total | Env do fluxo de trabalho |
| Isolamento | Nível de processo | Nível de serviço | Nenhum |

## Troubleshooting

- **Ferramenta Não Encontrada**: Verifique se o nome da ferramenta corresponde exatamente
- **Erros de Script**: Verifique os logs do fluxo de trabalho quanto a erros de sintaxe
- **Segredo Não Disponível**: Confirme o nome do segredo nas configurações do repositório/org
- **Saída Grande**: Agente lê o caminho do arquivo da resposta

## Documentação Relacionada

- [Especificação de Scripts MCP](/gh-aw/reference/mcp-scripts-specification/) - Especificação formal
- [Ferramentas](/gh-aw/reference/tools/) - Outras opções de configuração de ferramenta
- [Importações](/gh-aw/reference/imports/) - Importando fluxos de trabalho compartilhados
- [Safe Outputs](/gh-aw/reference/safe-outputs/) - Detalhes de configuração de safe output
- [MCPs](/gh-aw/guides/mcps/) - Integração de servidor MCP externo
- [Custom Safe Output Jobs](/gh-aw/reference/custom-safe-outputs/) - Jobs customizados pós-fluxo de trabalho
