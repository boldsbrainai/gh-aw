---
"gh-aw": patch
---

O direcionamento de tokens (`apiProxy.enableTokenSteering`) agora está habilitado por padrão; a chave de frontmatter `firewall.effective-token-steering` foi removida. Defina `max-effective-tokens` com um valor negativo para desabilitar tanto a imposição de limite quanto o direcionamento de tokens.
