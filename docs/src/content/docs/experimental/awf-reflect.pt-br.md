---
title: Rota AWF Reflect
description: Use a rota AWF /reflect para descobrir endpoints de inferência de gateway e modelos disponíveis em tempo de execução.
sidebar:
  order: 1355
---

Dentro da rede de tempo de execução AWF, o proxy de API AWF expõe `GET /reflect` em `http://api-proxy:10000/reflect`.

Use esta rota ao construir fluxos de trabalho, ferramentas ou extensões compartilhados que precisam de roteamento de modelo em tempo de execução.

## Por que usar `/reflect`

`/reflect` retorna os provedores de inferência configurados atualmente e sua disponibilidade de modelo para a execução ativa. Isso permite que um fluxo de trabalho ou ferramenta compartilhada:

- Descubra quais endpoints de gateway estão disponíveis
- Verifique se cada endpoint está configurado
- Leia ou atualize a disponibilidade do modelo
- Selecione um provedor/modelo dinamicamente em tempo de execução

> [!IMPORTANT]
> Não codifique URLs de API de modelo upstream diretas na lógica de fluxo de trabalho compartilhado. Todas as solicitações de inferência devem passar pelo gateway AWF para que o uso permaneça controlável e observável para controle de custos, rastreamento e otimização.

## Forma de resposta

A resposta inclui um array `endpoints` e um sinalizador `models_fetch_complete`:

- `endpoints[].provider`: identificador do provedor (ex: `openai`, `anthropic`, `copilot`, `gemini`)
- `endpoints[].base_url`: URL base do gateway para chamadas de inferência
- `endpoints[].configured`: se credenciais/configuração estão presentes para aquele provedor
- `endpoints[].models`: IDs de modelo descobertos, ou `null` quando a descoberta de modelo ainda não estiver completa
- `endpoints[].models_url`: URL do gateway usada para consultar modelos para aquele provedor
- `models_fetch_complete`: se a descoberta de modelo na inicialização está completa

## Fluxo de seleção recomendado para ferramentas compartilhadas

1. Consulte `/reflect` no início da execução.
2. Filtre os endpoints para `configured: true`.
3. Prefira endpoints com uma lista `models` não vazia.
4. Combine os aliases/padrões de modelo solicitados com os modelos disponíveis.
5. Roteie a inferência para o `base_url` do endpoint selecionado.
6. Se `models` for `null`, tente novamente a descoberta com backoff limitado (por exemplo, a cada 3 segundos até 5 tentativas) antes de falhar.

Isso mantém as ferramentas compartilhadas portáveis entre repositórios e ambientes onde os provedores disponíveis diferem.

## Exemplo de solicitação

```bash
curl -s http://api-proxy:10000/reflect
```

## Documentação Relacionada

- [Gateway MCP](/gh-aw/reference/mcp-gateway/)
- [Gerenciamento de Custos](/gh-aw/reference/cost-management/)
- [Aliases & Multiplicadores de Modelo](/gh-aw/reference/model-tables/)
