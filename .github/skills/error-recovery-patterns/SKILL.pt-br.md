---
description: Projete fluxos de manipulação de erro, retry, recuperação e depuração de gh-aw.
---

# Habilidade de Padrões de Recuperação de Erro

Use esta habilidade para tratamento de erros, estratégias de recuperação e depuração no gh-aw.

## Propósito

Implemente padrões de recuperação robustos para:

- Reduzir loops de retry em sessões de agente (meta: <10% vs 23% atual)
- Implementar disjuntores (circuit breakers) para evitar loops de retry infinitos
- Adicionar recuperação proativa para falhas de instalação, dependência e API
- Melhorar o log de depuração para tentativas de recuperação

## Quando Usar Esta Habilidade

Use esta habilidade quando:

- Implementar lógica de retry para operações de rede, instalações ou chamadas de API
- Depurar problemas de loop de retry em fluxos de trabalho ou sessões de agente
- Adicionar padrões de recuperação de erro a código novo ou existente
- Entender a classificação de erros transientes vs. não transientes
- Implementar disjuntores ou exponential backoff
- Adicionar log de depuração para tentativas de recuperação

## Conceitos Chave Cobertos

### 1. Padrão de Disjuntor (Circuit Breaker)
- Limites máximos de retry (padrão: 3 tentativas)
- Estratégias de backoff exponencial
- Falha rápida (fail-fast) em erros não transientes
- Implementação em JavaScript, Shell e Go

### 2. Recuperação de Falha de Instalação
- Instalação NPM com limpeza de cache e fallbacks de registro
- Instalação Python pip com alternativas de espelho (mirror)
- Pull de imagem Docker com retry e tratamento de limite de taxa
- Instalação da CLI Copilot com retry de rede

### 3. Tratamento de Tempo Limite e Limite de Taxa de API
- Detecção de limite de taxa da API do GitHub e backoff
- Padrões de detecção de erro transiente
- Configuração de retry personalizada para diferentes APIs
- Estratégias de retry específicas para limite de taxa

### 4. Log de Depuração para Recuperação
- Uso do pacote de logger para tentativas de retry
- Convenções de nomenclatura de categoria (pkg:filename)
- Padrões de variável de ambiente DEBUG
- Log de custo zero quando desabilitado

### 5. Categorização de Erro
- Erros transientes vs. não transientes
- Erros de rede, padrões de tempo limite
- Códigos de erro HTTP (502, 503, 504)
- Erros específicos do GitHub (limites de taxa, detecção de abuso)

## Anti-Padrões a Evitar

Esta habilidade descreve explicitamente anti-padrões a evitar:
- ❌ Loops de retry infinitos sem limites máximos
- ❌ Retentar erros de validação que não se corrigirão sozinhos
- ❌ Nenhum atraso de backoff entre tentativas
- ❌ Retries silenciosos sem registro (log)
- ❌ Retentar erros não transientes

## Exemplos de Código Fornecidos

A habilidade inclui exemplos prontos para produção para:
- Retry JavaScript com função `withRetry()`
- Loops de retry em script shell com backoff exponencial
- Padrões de retry em Go com contexto e tempo limite
- Recuperação de instalação NPM/pip/docker
- Tratamento de limite de taxa da API do GitHub
- Log de depuração para todas as tentativas de recuperação

## Habilidades Relacionadas

- **error-messages** - Formatação de mensagens de erro e guia de estilo
- **error-pattern-safety** - Diretrizes de segurança para regex de padrão de erro
- **developer** - Diretrizes gerais de desenvolvimento e convenções

## Documentação Completa

Documentação completa disponível em: `../../scratchpad/error-recovery-patterns.md`

Esta habilidade referencia o documento abrangente de padrões de recuperação de erro que inclui:
- Requisitos de formatação de console
- Padrões de encapsulamento (wrapping) de erro
- Cenários de erro comuns com resolução passo a passo
- Modelos de mensagem de erro
- Runbook de depuração
- Árvores de decisão de categorização de erro
- Estratégias de métricas e monitoramento
---
