---
title: "Conheça os Workflows: Relacionados à Segurança"
description: "Um tour curado de fluxos de trabalho de segurança e conformidade que impõem limites seguros"
authors:
  - dsyme
  - pelikhan
  - mnkiefer
date: 2026-01-13T08:00:00
sidebar:
  label: "Relacionados à Segurança"
prev:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-operations-release/
  label: "Workflows de Operações e Release"
next:
  link: /gh-aw/blog/2026-01-13-meet-the-workflows-creative-culture/
  label: "Workflows de Trabalho em Equipe e Cultura"
---

<img src="/gh-aw/peli.png" alt="Peli de Halleux" width="200" style="float: right; margin: 0 0 20px 20px; border-radius: 8px;" />

*Esplêndido!* Como é bom ter você de volta à [Fábrica de Agentes do Peli](/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/)! Agora, deixe-me mostrar a *câmara do guardião* - onde os protetores vigilantes montam guarda!

Em nossa [postagem anterior](/gh-aw/blog/2026-01-13-meet-the-workflows-operations-release/), exploramos fluxos de trabalho de operações e release que lidam com o processo crítico de envio de software - construir, testar, gerar notas de release e publicar. Esses fluxos de trabalho precisam ser extremamente confiáveis porque representam o momento em que nosso trabalho chega aos usuários.

Mas a confiabilidade por si só não é suficiente - também precisamos de *segurança*. Quando os agentes de IA podem acessar APIs, modificar código e interagir com serviços externos, a segurança torna-se primordial. Como garantimos que os agentes acessem apenas recursos autorizados? Como rastreamos vulnerabilidades e aplicamos prazos de conformidade? Como evitamos a exposição de credenciais? É aí que os fluxos de trabalho de segurança e conformidade tornam-se nossos mecanismos de proteção essenciais - os guardiões vigilantes que nos permitem dormir tranquilos à noite.

## Workflows relacionados à Segurança

Estes agentes são nossos guardas de segurança, mantendo a vigilância e aplicando as regras:

- **[Conformidade de Segurança (Security Compliance)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/security-compliance.md?plain=1)** - Executa campanhas de vulnerabilidade com rastreamento de prazos
- **[Firewall](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/firewall.md?plain=1)** - Testa a segurança da rede e valida regras - **59 discussões diárias de relatório de firewall**, **5 issues de teste de fumaça**
- **[Análise Diária de Segredos (Daily Secrets Analysis)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-secrets-analysis.md?plain=1)** - Escaneia em busca de credenciais expostas (sim, acontece)
- **[Scanner Diário de Código Malicioso (Daily Malicious Code Scan)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-malicious-code-scan.md?plain=1)** - Analisa mudanças recentes de código em busca de padrões suspeitos
- **[Relatório de Análise Estática (Static Analysis Report)](https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/static-analysis-report.md?plain=1)** - Varreduras de segurança diárias usando zizmor, poutine e actionlint - **57 discussões de análise** mais **12 relatórios de segurança Zizmor**

A Conformidade de Segurança gerencia campanhas de remediação de vulnerabilidades com rastreamento de prazos, garantindo que as issues de segurança sejam tratadas dentro de SLAs definidos - perfeito para aqueles momentos de pânico de "auditoria em 3 semanas".

O fluxo de trabalho de Firewall criou **59 discussões diárias de relatório de firewall** e **5 issues de teste de fumaça**, validando que nossos agentes não podem acessar recursos não autorizados - por exemplo, [#6943](https://github.com/github/gh-aw/discussions/6943) com a análise diária de firewall. É o segurança que aplica as regras de rede.

A Análise Diária de Segredos escaneia em busca de credenciais expostas em commits e discussões, fornecendo uma rede de segurança automatizada contra a exposição acidental de segredos - capturando aqueles momentos de "ops, commitei minha chave de API" antes que se tornem incidentes.

O Scanner Diário de Código Malicioso analisa mudanças recentes de código em busca de padrões suspeitos, adicionando uma camada de defesa automatizada contra ataques à cadeia de suprimentos.

O Relatório de Análise Estática criou **57 discussões de análise** mais **12 relatórios de segurança Zizmor**, executando auditorias de segurança diárias abrangentes usando ferramentas padrão da indústria - por exemplo, [#6973](https://github.com/github/gh-aw/discussions/6973) com as descobertas de análise estática mais recentes e [#3033](https://github.com/github/gh-aw/discussions/3033) com uma análise de segurança Zizmor. Isso mostra como as ferramentas de segurança tradicionais podem ser integradas em um fluxo de trabalho de agente de IA.

## Usando estes Workflows

Você pode adicionar esses fluxos de trabalho ao seu próprio repositório e remixá-los. Comece com nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/), depois execute um dos seguintes:

**Conformidade de Segurança:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/security-compliance.md
```

**Firewall:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/firewall.md
```

**Análise Diária de Segredos:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-secrets-analysis.md
```

**Scanner Diário de Código Malicioso:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/daily-malicious-code-scan.md
```

**Relatório de Análise Estática:**

```bash
gh aw add-wizard https://github.com/github/gh-aw/blob/v0.45.5/.github/workflows/static-analysis-report.md
```

Em seguida, edite e remixe as especificações do fluxo de trabalho para atender às suas necessidades, regenere o arquivo de bloqueio usando `gh aw compile` e envie para o seu repositório. Veja nosso [Início Rápido](https://github.github.com/gh-aw/setup/quick-start/) para obter mais instruções de instalação e configuração.

Você também pode [criar seus próprios fluxos de trabalho](/gh-aw/setup/creating-workflows/).

## Saiba mais

- **[GitHub Agentic Workflows](https://github.github.com/gh-aw/)** - A tecnologia por trás dos fluxos de trabalho
- **[Início Rápido](https://github.github.com/gh-aw/setup/quick-start/)** - Como escrever e compilar fluxos de trabalho

## Próximo: Workflows de Trabalho em Equipe e Cultura

Após toda essa conversa séria, vamos explorar o lado divertido: agentes que trazem alegria e constroem a cultura da equipe.

Continue lendo: [Workflows de Trabalho em Equipe e Cultura →](/gh-aw/blog/2026-01-13-meet-the-workflows-creative-culture/)

---

*Esta é a parte 11 de uma série de 19 partes explorando os fluxos de trabalho na Fábrica de Agentes do Peli.*
