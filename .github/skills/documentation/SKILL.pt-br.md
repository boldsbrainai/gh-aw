---
name: documentation
description: Escreva documentação Diataxis concisa para gh-aw com convenções markdown Starlight.
---

### Documentação

A documentação reside em `docs/`, usa Markdown compatível com GitHub, renderiza com Astro Starlight e segue o Diátaxis.

## Estrutura Diátaxis

Organize a documentação em quatro tipos de Diátaxis:

### 1. Tutoriais (Orientado ao Aprendizado)
**Propósito**: Guiar iniciantes na conquista de um resultado específico para construir confiança.

- Comece com o que o usuário vai construir ou alcançar
- Forneça um caminho claro e passo a passo do início ao fim
- Inclua exemplos concretos e código funcional
- Assuma conhecimento prévio mínimo
- Foque no caminho feliz (evite casos extremos e alternativas)
- Termine com um resultado funcional que o usuário possa ver e usar
- Use modo imperativo: "Crie um arquivo", "Execute o comando"

**Evite**: Explicar conceitos em profundidade, múltiplas opções, depuração

### 2. Guias de "Como fazer" (Orientado a Objetivo)
**Propósito**: Mostrar como resolver um problema específico do mundo real ou realizar uma tarefa específica.

- Formato do título: "Como [alcançar objetivo específico]"
- Assuma que o usuário conhece o básico
- Foque em passos práticos para resolver um problema
- Inclua o contexto necessário, mas mantenha-se focado
- Mostre múltiplas abordagens apenas quando genuinamente útil
- Termine quando o objetivo for alcançado
- Use modo imperativo: "Configure a definição", "Adicione o seguinte"

**Evite**: Ensinar fundamentos, explicar todos os detalhes, ser exaustivo

### 3. Referência (Orientado à Informação)
**Propósito**: Fornecer descrições técnicas precisas e completas do sistema.

- Organizado por estrutura (comandos da CLI, opções de configuração, endpoints de API)
- Abrangente e autoritativo
- Formato consistente em todas as entradas
- A precisão técnica é primordial
- Inclua todos os parâmetros, opções e valores de retorno
- Use modo descritivo: "O comando aceita", "Retorna uma string"
- Narrativa ou explicação mínima

**Evite**: Instruções, tutoriais, opiniões sobre uso

### 4. Explicação (Orientado à Compreensão)
**Propósito**: Clarificar e iluminar tópicos para aprofundar a compreensão.

- Discuta o porquê das coisas serem como são
- Explique decisões de design e compensações (trade-offs)
- Forneça contexto e histórico
- Conecte conceitos para ajudar a formar modelos mentais
- Discuta alternativas e suas implicações
- Use modo indicativo: "Esta abordagem fornece", "A engine usa"

**Evite**: Instruções passo a passo, material de referência exaustivo

## Diretrizes Gerais de Estilo

- **Tom**: Neutro, técnico, não promocional
- **Voz**: Evite "nós", "nosso" (use "a ferramenta", "este comando")
- **Cabeçalhos**: Use sintaxe de cabeçalho markdown, não texto em negrito como cabeçalhos
- **Listas**: Evite longas listas com marcadores; prefira prosa com estrutura
- **Amostras de código**: Mínimas e focadas; exclua campos opcionais, a menos que relevantes
- **Tag de linguagem**: Use `aw` para trechos de fluxo de trabalho agentic com frontmatter YAML

**Exemplo de bloco de código de fluxo de trabalho**:
```aw wrap
on: push
# Suas etapas de fluxo de trabalho aqui
```

## Sintaxe Markdown Compatível com GitHub

Arquivos de documentação usam markdown compatível com GitHub com Astro Starlight para renderização. Elementos de sintaxe chave:

### Frontmatter
Cada página de documentação deve ter frontmatter:
```markdown
title: Título da Página
description: Breve descrição para SEO e navegação
```

### Alertas do GitHub
Use a sintaxe de alerta do GitHub para notas, dicas, avisos e cuidados:
```markdown
> [!NOTE]
> Informação importante que o leitor deve notar.

> [!TIP]
> Conselho útil para o leitor.

> [!WARNING]
> Aviso sobre possíveis problemas ou armadilhas.

> [!CAUTION]
> Aviso crítico sobre operações perigosas.

> [!IMPORTANT]
> Informação chave que os usuários precisam saber.
```

### Blocos de Código
- Use realce de sintaxe com tags de linguagem
- Adicione atributo `title` para nomes de arquivos: ` ```yaml title=".github/workflows/example.yml" `
- Use linguagem `aw` para arquivos de fluxo de trabalho agentic com frontmatter YAML
- Adicione `wrap` para quebra de linha: ` ```aw wrap `

### Links
- Links internos: Use caminhos relativos entre páginas de documentação
- Links externos: Abrir em nova aba automaticamente
- Texto do link: Use texto descritivo, evite "clique aqui"

### Abas (Tabs)
Use abas para mostrar alternativas (por exemplo, linguagens diferentes, plataformas):
```markdown
import { Tabs, TabItem } from '@astrojs/starlight/components';

<Tabs>
  <TabItem label="npm">
    ```bash
    npm install package
    ```
  </TabItem>
  <TabItem label="yarn">
    ```bash
    yarn add package
    ```
  </TabItem>
</Tabs>
```

### Cards
Use cards para navegação ou destaque de múltiplas opções:
```markdown
import { Card, CardGrid } from '@astrojs/starlight/components';

<CardGrid>
  <Card title="Introdução" icon="rocket">
    Introdução rápida ao básico.
  </Card>
  <Card title="Uso Avançado" icon="setting">
    Mergulho profundo em funcionalidades avançadas.
  </Card>
</CardGrid>
```

**Lembre-se**: Mantenha os componentes mínimos. Prefira markdown padrão quando possível.

## Conteúdo a Evitar

- Seções de "Principais Funcionalidades"
- Linguagem de marketing ou argumentos de venda
- Listas excessivas com marcadores (prefira prosa estruturada)
- Exemplos excessivamente verbosos com todos os parâmetros opcionais
- Misturar tipos de documentação (por exemplo, tutoriais que se tornam referência)

## Evitando Inchaço na Documentação (Documentation Bloat)

O inchaço na documentação reduz a clareza e torna o conteúdo mais difícil de navegar. Tipos comuns de inchaço incluem:

### Tipos de Inchaço na Documentação

1. **Conteúdo duplicado**: Mesma informação repetida em diferentes seções
2. **Listas excessivas com marcadores**: Listas longas que poderiam ser condensadas em prosa ou tabelas
3. **Exemplos redundantes**: Múltiplos exemplos mostrando o mesmo conceito
4. **Descrições verbosas**: Explicações excessivamente prolixas que poderiam ser mais concisas
5. **Estrutura repetitiva**: O mesmo padrão "O que faz" / "Por que é valioso" sobrecarregado

### Escrevendo Documentação Concisa

Ao editar a documentação, foque em:

**Consolidar listas com marcadores**:
- Converta longas listas de marcadores em prosa concisa ou tabelas
- Remova pontos redundantes que dizem a mesma coisa de forma diferente

**Eliminar duplicatas**:
- Remova informações repetidas
- Consolide seções semelhantes

**Condensar texto verboso**:
- Torne as descrições mais diretas e concisas
- Remova palavras e frases de preenchimento
- Mantenha a precisão técnica reduzindo a contagem de palavras

**Padronizar estrutura**:
- Reduza padrões repetitivos de "O que faz" / "Por que é valioso"
- Use linguagem variada e natural

**Simplificar amostras de código**:
- Remova complexidade desnecessária de exemplos de código
- Foque em demonstrar o conceito central claramente
- Elimine código boilerplate ou de configuração, a menos que essencial para a compreensão
- Mantenha exemplos mínimos, porém completos
- Use cenários realistas, mas simples

### Exemplo: Antes e Depois

**Antes (Inchado)**:
```markdown
### Nome da Ferramenta
Descrição da ferramenta.

- **O que faz**: Esta ferramenta faz X, Y e Z
- **Por que é valioso**: É valioso porque A, B e C
- **Como usar**: Você a usa fazendo os passos 1, 2, 3, 4, 5
- **Quando usar**: Use-a quando precisar de X
- **Benefícios**: Obtém benefício A, benefício B, benefício C
- **Saiba mais**: [Link](url)
```

**Depois (Conciso)**:
```markdown
### Nome da Ferramenta
Descrição da ferramenta que faz X, Y e Z para alcançar A, B e C.

Use-a quando precisar de X seguindo os passos 1-5. [Saiba mais](url)
```

### Diretrizes de Qualidade da Documentação

1. **Preservar significado**: Nunca perca informações importantes
2. **Ser cirúrgico**: Faça edições precisas, não reescreva tudo
3. **Manter o tom**: Mantenha o tom neutro e técnico
4. **Testar localmente**: Verifique se links e formatação ainda estão corretos

## Estrutura por Tipo de Arquivo

- **Introdução (Getting Started)**: Formato de tutorial
- **Guias de "Como fazer"**: Orientado a objetivo, uma tarefa por guia
- **Referência CLI**: Formato de referência, documentação completa do comando
- **Conceitos**: Formato de explicação, construindo entendimento
- **Referência da API**: Formato de referência, documentação completa da API
