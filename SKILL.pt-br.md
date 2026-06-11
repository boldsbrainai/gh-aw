# gh-aw Prompt Surface

Este repositório compila o **gh-aw** (GitHub Agentic Workflows), uma extensão da CLI do GitHub para escrever fluxos de trabalho em Markdown e compilá-los para o GitHub Actions.

## O que esta interface faz

- Converte especificações de fluxo de trabalho em Markdown (`.md`) em arquivos de bloqueio compilados (`.lock.yml`)
- Suporta vários mecanismos de IA (`copilot`, `claude`, `codex`, `custom`)
- Integra ferramentas, incluindo servidores GitHub MCP e ferramentas de saída segura
- Fornece comandos CLI para compilar, executar, inspecionar e auditar fluxos de trabalho

## Conceitos-chave

1. **Compilação de fluxos de trabalho**: edite o Markdown do fluxo de trabalho e, em seguida, recompile os arquivos lock
2. **Seleção de mecanismo**: defina `engine` no frontmatter para controlar o comportamento do agente de tempo de execução
3. **Ferramentas MCP**: configure conjuntos de ferramentas GitHub/MCP no frontmatter para operações no repositório
4. **Saídas seguras**: caminhos e restrições de saída de issues/comentários seguros para o fluxo de trabalho

## Exemplos representativos de uso

```bash
# Compilar workflows em Markdown para gerar arquivos de bloqueio
gh aw compile

# Executar um workflow manualmente
gh aw run .github/workflows/daily-skill-optimizer.md

# Inspecionar o uso do servidor MCP nos workflows
gh aw mcp list
gh aw mcp inspect daily-skill-optimizer

# Auditar a execução de um workflow
gh aw audit 24814681146
```

## Onde encontrar mais informações neste repositório

- `/AGENTS.md` para convenções de fluxos de trabalho de desenvolvimento/agente
- `/skills/*/SKILL.md` para orientações específicas por domínio (GitHub MCP, documentação, erros, etc.)
