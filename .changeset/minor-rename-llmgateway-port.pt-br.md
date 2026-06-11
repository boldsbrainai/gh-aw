---
"gh-aw": major
---
Renomeou-se o sinalizador `supportsLLMGateway` do mecanismo de fluxo de trabalho do agente para `llmGatewayPort`, tornou-se a porta do gateway obrigatória e validada, removeram-se os ganchos da interface `SupportsLLMGateway` e consolidaram-se os sinalizadores de fluxo de trabalho de proxy de API/acesso ao host.

**⚠️ Alteração compatibilidade**: O campo `supportsLLMGateway` foi renomeado para `llmGatewayPort` e agora é obrigatório (anteriormente era opcional). Os ganchos da interface `SupportsLLMGateway` foram removidos.

**Guia de migração:**
- Substitua `supportsLLMGateway: true` por `llmGatewayPort: <port>` na configuração do mecanismo, fornecendo o número de porta explícito
- Exemplo:
  ```yaml
  # Antes
  supportsLLMGateway: true

  # Depois
  llmGatewayPort: 8080
  ```
- Se você estava usando os hooks da interface `SupportsLLMGateway` em implementações personalizadas do mecanismo, migre para a nova configuração baseada em `llmGatewayPort`
- O campo `llmGatewayPort` agora é obrigatório ao habilitar o suporte ao gateway LLM
