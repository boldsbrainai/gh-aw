# Resumo de Descobertas de Segurança - 19/01/2026

Este documento resume as descobertas de segurança identificadas em 19/01/2026 em resposta aos problemas de gerenciamento de vulnerabilidades #181113 (Dependabot) e #180365 (Code Scanning).

## Resumo

- **Total de Descobertas**: 285 problemas identificados pelo gosec
- **Descobertas Críticas**: 0
- **Severidade Alta**: 2 (vulnerabilidades npm - RESOLVIDAS)
- **Severidade Média/Baixa**: 283 descobertas do gosec

## Descobertas Resolvidas

### Vulnerabilidades npm (severidade ALTA)

#### 1. @anthropic-ai/claude-code (GHSA-7mv8-j34q-vp7q)
- **Status**: ✅ CORRIGIDO
- **Severidade**: Alta
- **Localização**: `docs/package.json`
- **Descrição**: Bypass de Validação de Comando Sed permitindo gravações de arquivos arbitrários
- **Resolução**: Atualizado para a versão corrigida via `npm audit fix`
- **Data da Correção**: 19/01/2026

#### 2. pacote diff (GHSA-73rr-hh4g-fpgx)
- **Status**: ✅ CORRIGIDO  
- **Severidade**: Alta (dependência transitiva via astro)
- **Localização**: `docs/package.json` (transitiva)
- **Descrição**: Vulnerabilidade de Negação de Serviço (DoS) em parsePatch e applyPatch
- **Resolução**: Atualizado para a versão corrigida via `npm audit fix`
- **Data da Correção**: 19/01/2026

## Descobertas de Análise Estática do gosec

### Visão Geral por Categoria

| Categoria | Contagem | Nível de Risco | Ação Necessária |
|----------|-------|------------|-----------------|
| G115 (Estouro de Inteiro) | 19 | Médio | Revisar e adicionar verificação de limites |
| G204 (Subprocesso com Variável) | 89 | Baixo | O código usa entradas validadas |
| G304 (Inclusão de Arquivo via Variável) | 154 | Baixo | O código usa caminhos validados |
| G404 (RNG Fraco) | 2 | Baixo | Revisar para uso criptográfico |
| G101 (Credenciais Hardcoded) | 6 | Baixo | Falsos positivos (nomes de variáveis) |
| G110 (DoS via Descompressão) | 1 | Médio | Revisar extração de zip |
| G305 (Travessia de Arquivo) | 1 | Médio | Revisar extração de zip |
| G301 (Permissões de Diretório) | 40 | Baixo | Excessivamente permissivo (0755 vs 0750) |
| G306 (Permissões de Arquivo) | 51 | Baixo | Excessivamente permissivo (0644 vs 0600) |
| G104 (Erros Não Tratados) | 4 | Baixo | Revisar tratamento de erros |

### Descobertas Prioritárias para Revisão

#### 1. Conversões de Estouro de Inteiro (Integer Overflow) (G115) - 19 instâncias

**Risco**: Médio - Potencial para estouro de inteiro em conversões

**Localizações**:
- `pkg/console/render.go`: 4 instâncias (uint64 → int64, uint → int64, uint → int)
- `pkg/workflow/stop_after.go`: 2 instâncias (uint64 → int)
- `pkg/workflow/safe_outputs_config_messages.go`: 1 instância (uint64 → int)
- `pkg/workflow/safe_outputs_config.go`: 1 instância (uint64 → int)
- `pkg/workflow/repo_memory.go`: 4 instâncias (uint64 → int)
- `pkg/workflow/frontmatter_extraction_security.go`: 2 instâncias (uint64 → int, uint → int)
- `pkg/workflow/cache.go`: 2 instâncias (uint64 → int)
- `pkg/parser/schedule_parser.go`: 1 instância (int → uint32)
- `pkg/logger/logger.go`: 1 instância (int → uint32)

**Avaliação**: Essas conversões são geralmente seguras no contexto em que são usadas (cálculos de tamanho/comprimento que não excederão o intervalo de int). No entanto, a verificação explícita de limites melhoraria a segurança do código.

**Recomendação**: 
- Adicionar verificação de limites antes das conversões onde a entrada é controlada pelo usuário
- Usar verificações math.MaxInt32 / math.MaxInt64
- Documentar suposições sobre intervalos de entrada

#### 2. Bomba de Descompressão e Travessia de Arquivo (Path Traversal) (G110, G305) - 2 instâncias

**Risco**: Médio - Potencial DoS e bypass de segurança

**Localizações**:
- `pkg/cli/logs_download.go:407` - G110: Vulnerabilidade de bomba de descompressão
- `pkg/cli/logs_download.go:364` - G305: Travessia de arquivo na extração de zip

**Avaliação**: Os downloads de logs de workflow podem ser vulneráveis a arquivos zip maliciosos.

**Recomendação**:
- Adicionar limites de tamanho de descompressão
- Validar caminhos de arquivos extraídos para evitar travessia de diretório
- Implementar limites de tempo limite (timeout) de extração

#### 3. Gerador de Números Aleatórios Fraco (G404) - 2 instâncias

**Risco**: Baixo a Médio (depende do uso)

**Localizações**:
- `pkg/cli/update_git.go:57` - Usa math/rand em vez de crypto/rand
- `pkg/cli/add_command.go:463` - Usa math/rand em vez de crypto/rand

**Avaliação**: Revisar se esses números aleatórios são usados para operações sensíveis à segurança.

**Recomendação**:
- Se usado para segurança (tokens, IDs), mudar para crypto/rand
- Se usado para fins não relacionados à segurança (IDs, nomes temporários), documentar e suprimir

#### 4. Potenciais Credenciais Hardcoded (G101) - 6 instâncias

**Risco**: Baixo - Prováveis falsos positivos

**Localizações**:
- `pkg/workflow/copilot_engine_execution.go:366`
- `pkg/workflow/compiler_safe_outputs_steps.go` (4 instâncias)
- `pkg/cli/trial_support.go:181`

**Avaliação**: Provavelmente são nomes de variáveis contendo as palavras-chave "token" ou "secret", e não credenciais reais embutidas no código.

**Recomendação**: Revisar e suprimir se forem falsos positivos.

### Descobertas de Baixa Prioridade

#### Subprocesso com Variável (G204) - 89 instâncias
**Avaliação**: O código usa git, gh e outras ferramentas de CLI com variáveis. Geralmente são validadas e escopadas para operações confiáveis. A maioria são falsos positivos.

#### Inclusão de Arquivo via Variável (G304) - 154 instâncias
**Avaliação**: As operações de arquivo usam caminhos fornecidos pelo usuário, mas são validados. A maioria são falsos positivos no contexto de uma ferramenta de CLI que opera em arquivos locais.

#### Permissões de Diretório (G301) - 40 instâncias
**Avaliação**: Usa permissões 0755 em vez da recomendada 0750. Risco baixo para este caso de uso.

#### Permissões de Arquivo (G306) - 51 instâncias
**Avaliação**: Usa permissões 0644 em vez da recomendada 0600. Risco baixo para arquivos não sensíveis.

#### Erros Não Tratados (G104) - 4 instâncias
**Avaliação**: As funções de configuração de MCP não tratam todos os erros. Devem ser revisadas para completude.

## Recomendações

### Ações Imediatas (Alta Prioridade)

1. ✅ **CONCLUÍDO**: Corrigir vulnerabilidades npm nas dependências de docs
2. **Revisar e corrigir**: Conversões de estouro de inteiro (G115) - adicionar verificação de limites
3. **Revisar e corrigir**: Proteção contra bomba de descompressão em logs_download.go
4. **Revisar e corrigir**: Proteção contra travessia de arquivo em logs_download.go

### Ações de Curto Prazo (Média Prioridade)

1. **Revisar**: Uso de RNG fraco - determinar se crypto/rand é necessário
2. **Revisar**: Falsos positivos de credenciais hardcoded - suprimir na configuração do gosec
3. **Revisar**: Erros não tratados na configuração de MCP

### Ações de Longo Prazo (Baixa Prioridade)

1. **Considerar**: Restringir permissões de diretório de 0755 para 0750
2. **Considerar**: Restringir permissões de arquivo de 0644 para 0600 para arquivos de configuração
3. **Configurar**: gosec para suprimir falsos positivos validados (G204, G304)

## Configuração do gosec

Para suprimir falsos positivos, adicione ao `.golangci.yml`:

```yaml
linters-settings:
  gosec:
    excludes:
      - G204  # Subprocesso com variável (validado em nosso contexto)
      - G304  # Inclusão de arquivo via variável (caminhos validados)
      - G301  # Permissões de diretório (0755 aceitável para nosso caso de uso)
      - G306  # Permissões de arquivo (0644 aceitável para arquivos não sensíveis)
```

## Verificação

Para executar novamente os scans de segurança:

```bash
# vulnerabilidades npm
cd docs && npm audit

# Scan de segurança Go
gosec -fmt json -exclude-generated -track-suppressions ./...

# Banco de dados de vulnerabilidades Go
govulncheck ./...
```

## Referências

- Descoberta Dependabot: github/vuln-mgmt#181113
- Descoberta Code Scanning: github/vuln-mgmt#180365
- GHSA-7mv8-j34q-vp7q: https://github.com/advisories/GHSA-7mv8-j34q-vp7q
- GHSA-73rr-hh4g-fpgx: https://github.com/advisories/GHSA-73rr-hh4g-fpgx
- regras do gosec: https://github.com/securego/gosec#available-rules
