---
"gh-aw": patch
---

Certifique-se de que o diretório `/home/runner/.copilot` seja criado e que seus proprietários sejam alterados de volta para `runner:runner` antes de instalar a CLI do Copilot, para que execuções repetidas do chroot não saiam do diretório de propriedade do root e causem erros EACCES.
