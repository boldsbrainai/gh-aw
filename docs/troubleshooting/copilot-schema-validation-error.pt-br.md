# Erro de Validação de Esquema (Schema) do Copilot

## Descrição do Problema

**Mensagem de Erro:**
```
Model call failed: Invalid schema for function 'safeoutputs-add_labels': In context=(), object schema missing properties.
```

**Fluxos de Trabalho (Workflows) Afetados:** AI Moderator e outros workflows que usam safe-outputs com `add-labels`.

**Status:** Problema intermitente conhecido no Copilot CLI v0.0.384.

## Sintomas

- As execuções do workflow falham com o erro "Invalid schema for function".
- O erro menciona "object schema missing properties" (esquema de objeto com propriedades ausentes).
- A falha é intermitente — algumas execuções têm sucesso com o esquema idêntico.
- Afeta as ferramentas de safe-outputs expostas através do gateway MCP.

## Causa Raiz

Este é um bug intermitente de validação de esquema no GitHub Copilot CLI versão 0.0.384. O esquema da ferramenta está formatado corretamente e inclui todos os campos obrigatórios, incluindo `properties`, mas o validador do Copilot CLI ocasionalmente o rejeita.

### Detalhes da Investigação

1. **Verificação de Esquema**: O esquema da ferramenta `add_labels` em `actions/setup/js/safe_outputs_tools.json` está formatado corretamente:
   ```json
   {
     "name": "add_labels",
     "inputSchema": {
       "type": "object",
       "required": ["labels"],
       "properties": {
         "labels": { "type": "array", "items": { "type": "string" } },
         "item_number": { "type": "number" }
       },
       "additionalProperties": false
     }
   }
   ```

2. **Sem Problemas de Transformação**: 
   - A compilação em Go preserva o esquema exatamente.
   - O servidor MCP passa o esquema inalterado.
   - O gateway MCP encaminha o esquema sem modificação.

3. **Natureza Intermitente**: A análise de execuções recentes de workflow mostra tanto sucessos quanto falhas com o esquema idêntico, confirmando que este não é um problema de configuração.

## Soluções Alternativas (Workarounds)

### Opção 1: Repetir Execuções com Falha
A solução alternativa mais simples é repetir manualmente as execuções de workflow que falharam. Como o problema é intermitente, uma nova tentativa provavelmente terá sucesso.

### Opção 2: Usar um Modelo Alternativo
Tente mudar para um modelo diferente no frontmatter do workflow:
```yaml
engine:
  id: copilot
  model: gpt-4o  # Em vez de gpt-5-mini
```

### Opção 3: Aguardar Atualização do Copilot CLI
Monitore os lançamentos do Copilot CLI em busca de uma correção na lógica de validação de esquema. Este problema deve ser resolvido em uma versão futura.

## Impacto

- **Severidade**: Baixa — O problema é intermitente e a repetição geralmente funciona.
- **Frequência**: Ocasional — aparece em ~10-20% das execuções.
- **Solução Alternativa Disponível**: Sim — repetição manual.

## Arquivos Relacionados

- Definição de esquema: `actions/setup/js/safe_outputs_tools.json`
- Geração de esquema: `pkg/workflow/safe_outputs_config_generation.go`
- Servidor MCP: `actions/setup/js/safe_outputs_mcp_server.cjs`
- Workflow afetado: `.github/workflows/ai-moderator.md`

## Atualizações de Status

- **18/01/2026**: Problema identificado e documentado.
- **Versão do Copilot CLI**: 0.0.384
- **Resolução Esperada**: Aguardando atualização do Copilot CLI.

## Referências

- Exemplo de execução de workflow: https://github.com/github/gh-aw/actions/runs/21110741074
- Os logs de erro mostram 6 tentativas de reexecução antes da falha final.
- Tempo total de espera de repetição: ~93 segundos.
