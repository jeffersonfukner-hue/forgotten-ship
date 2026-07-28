# SPRINT_043.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 043
**Status:** Concluída
**Versão da Arquitetura:** Refactor — POWER_UPS com Classificação por Tipo

---

## Objetivo da Sprint

Renomear `PASSIVE_POWERUPS` para `POWER_UPS` em `settings.py`,
adicionar um campo `"type"` (`"active"`/`"passive"`) a cada entrada, e
propagar a mudança para `player.py` e `game_scene.py` — preparando
terreno para estatísticas de eficiência por tipo de power-up escolhido
e uma futura ferramenta de comparação de builds, sem alterar nenhum
comportamento de jogo.

---

## Situação Inicial

Ao final da Sprint 042, o Bloco de Power-ups estava 100% completo (11
armas/sistemas), todos configurados sob `PASSIVE_POWERUPS` — nome que
já não refletia a realidade da estrutura, já que ela cobria tanto
efeitos passivos (ímã, regeneração) quanto armas ativas (Sabre, Sifão,
armas de fogo) desde a Sprint 031.

---

## Problema

Renomear uma estrutura de dados usada em ~30 entradas e referenciada em
`settings.py`, `player.py` (mais de 15 pontos) e `game_scene.py` (mais
de 10 pontos) exigia uma abordagem diferente do padrão usual de "Trocar:
/ por:" em trechos pequenos — o volume de mudança tornaria os diffs
picados difíceis de acompanhar e propensos a inconsistência entre
arquivos.

---

## Decisão Arquitetural

### Arquivos Completos em Vez de Diffs Picados

Por decisão do criador do jogo, dado o volume do refactor, os três
arquivos afetados foram reescritos por inteiro e entregues completos,
um de cada vez, em vez do padrão usual de trechos "Trocar: / por:" —
avaliado como mais seguro e claro para uma mudança que toca a maior
parte do arquivo.

### Campo `"type"` como Metadado, Sem Afetar Lógica

Cada entrada de `POWER_UPS` ganhou `"type": "active"` ou
`"type": "passive"` — um campo puramente informativo, não consultado
por nenhuma lógica de jogo existente. Serve como preparação para
análises futuras (comparação de eficiência entre builds ativas vs.
passivas), sem introduzir nenhum comportamento novo nesta Sprint.

### Critério de Classificação

`"active"`: armas/sistemas que causam dano por conta própria — Sabre,
Sifão, Campo de Força, todas as armas de fogo, e as três variantes do
Tiro Múltiplo. `"passive"`: eixos que modificam um atributo sem agir
por si só — Ímã, Regeneração, os três eixos do Escudo Deflector, e os
eixos soltos do Tiro base (Velocidade, Penetração, Rajada, Alcance).

### Renomeação em Cadeia dos Métodos Relacionados

Ao ser questionado sobre por que só o dicionário mudaria de nome
enquanto os métodos que o consultam continuariam com nomenclatura
"passiva" (`passive_levels`, `get_passive_value()`, `upgrade_passive()`),
a decisão foi propagar a renomeação por completo: `passive_levels` →
`power_up_levels`, `get_passive_value()` → `get_power_up_value()`,
`upgrade_passive()` → `increase_power_up_level()` — mantendo a
nomenclatura do código consistente com a nova estrutura de dados,
evitando o cenário de "dicionário genérico, métodos com nome
desatualizado".

### Revisão Completa dos Comentários

Aproveitando que o arquivo `settings.py` seria reescrito por inteiro,
os comentários foram revisados: o cabeçalho de `POWER_UPS` passou a
explicar o campo `"type"` e seu critério; `PLAYER_RANGE_RADIUS` ganhou
nota explícita de que é sobrescrito a cada frame; `HORDE_ENEMIES_PER_VISIT`
ganhou nota de que existe mas não está conectada (referenciando o
backlog); Phaser/Plasma ganharam nota diferenciando sua cadência fixa
da cadência upável da Metralhadora de Pulso.

---

## Conceitos de Python

- **Renomeação em Cadeia Mantendo Consistência Semântica** — quando um
  nome deixa de refletir a realidade de uma estrutura (`passive` num
  dicionário que hoje é genérico), a inconsistência se propaga para
  todo código que o consulta — corrigir só a origem sem revisar os
  consumidores deixa o código com nomenclatura conflitante.
- **Campo de Metadado Sem Uso Funcional Imediato** — `"type"` foi
  adicionado antes de existir qualquer código que o leia — uma prática
  válida quando o campo é barato de manter e a necessidade futura
  (estatísticas de eficiência) já está claramente registrada, evitando
  precisar voltar e adicionar retroativamente a ~30 entradas depois.

---

## Conceitos de Arquitetura

- **Reescrever Arquivo Inteiro como Estratégia Válida para Refactors
  de Alto Volume** — o padrão usual de diffs localizados (`Trocar: /
  por:`) funciona bem para mudanças pontuais, mas quando a mudança toca
  a maioria das linhas de um arquivo, entregar o arquivo completo é
  mais seguro (menos risco de diffs se sobrepondo ou saindo de
  sincronia) e mais fácil de revisar de uma vez.
- **Erro no Fluxo de Trabalho: Aplicar Mudança Parcial Sem Perguntar**
  — na primeira tentativa desta Sprint, o assistente devolveu o
  `player.py` com o dicionário renomeado mas os métodos relacionados
  mantidos com nome antigo, sem antes perguntar se a renomeação em
  cadeia era desejada — um erro de processo corrigido imediatamente
  após o criador do jogo apontar a falha.

---

## Implementações

### Missão Única — Refactor Completo em 3 Arquivos

**Arquivos:** `settings.py`, `player.py`, `game_scene.py`

`PASSIVE_POWERUPS` renomeado para `POWER_UPS`, campo `"type"` adicionado
a todas as ~30 entradas, comentários revisados. `passive_levels` →
`power_up_levels`, `get_passive_value()` → `get_power_up_value()`,
`upgrade_passive()` → `increase_power_up_level()`, propagados em todos
os pontos de uso em `player.py` e `game_scene.py`.

---

## Bugs Encontrados

### Bug — Referência Não Atualizada Durante a Aplicação Manual

**Sintoma:** `AttributeError: 'Player' object has no attribute 'power_up_levels'`
ao rodar o jogo pela primeira vez após aplicar as mudanças.

**Causa:** o `game_scene.py` já usava o nome novo (`power_up_levels`),
mas o `player.py` salvo em disco ainda continha o nome antigo
(`passive_levels`) — indicando que a versão completa do arquivo
fornecida não havia sido salva corretamente por cima do arquivo
existente.

**Solução:** o criador do jogo confirmou e salvou novamente o
`player.py` completo, resolvendo o erro.

**Lição Aprendida:** em refactors que tocam múltiplos arquivos com
nomes interdependentes, um erro de sincronização entre "o que foi
gerado" e "o que foi de fato salvo" produz um erro imediato e óbvio
(`AttributeError`) assim que o jogo roda — o tipo de refactor onde
testar a aplicação logo após colar os arquivos é essencial, já que a
falha não fica escondida.

---

## Estado Atual da Arquitetura

```
settings.py
 └── POWER_UPS: dict (ex-PASSIVE_POWERUPS)
      └── cada entrada com "type": "active" | "passive"

Player
 ├── power_up_levels: dict (ex-passive_levels)
 ├── get_power_up_value(key) (ex-get_passive_value)
 └── increase_power_up_level(key) (ex-upgrade_passive)

GameScene
 └── todas as referencias atualizadas para os novos nomes
```

Testado: jogo rodando integralmente sem nenhuma mudança de
comportamento perceptível — sistema de escolha de upgrade, todas as 11
armas/sistemas, painel de debug, pontuação, tudo funcionando
identicamente a antes do refactor.

---

## O que o aluno aprendeu

Como avaliar quando um refactor de alto volume justifica reescrever
arquivos completos em vez de diffs localizados. Como propagar uma
renomeação de forma consistente por toda a cadeia de código relacionada
(estrutura de dados → atributos → métodos), evitando deixar
nomenclatura conflitante pela metade. Como um campo de metadado pode
ser adicionado antes de qualquer código consumi-lo, quando a
necessidade futura já está clara. A importância de testar imediatamente
após aplicar um refactor de múltiplos arquivos, já que erros de
sincronia entre arquivos aparecem rápido e de forma óbvia.

---

## Próxima Sprint

Bugs de obstáculos (spawn sobre porta, margem de parede, fixos
faltando nas Salas 2/3), já registrados desde as Sprints 029/030.

Depois: Bloco de Entidades de Chefes, seguido de Bloco de Restauração
da Nave.

---

## Resumo Executivo

Esta Sprint executa um refactor estrutural de `PASSIVE_POWERUPS` para
`POWER_UPS`, adicionando classificação por tipo (`"active"`/`"passive"`)
em todas as ~30 entradas — preparação para futuras estatísticas de
eficiência e comparação de builds. Dado o alto volume de referências
tocadas (3 arquivos, dezenas de pontos), a Sprint adotou entrega de
arquivos completos em vez de diffs localizados. A renomeação foi
propagada em cadeia para os métodos relacionados no `Player`, corrigindo
uma primeira tentativa incompleta apontada pelo criador do jogo. Um
erro de sincronização entre arquivos gerou um `AttributeError` imediato
ao testar, resolvido ao re-salvar o arquivo correto — sem impacto na
lógica final, o jogo roda de forma idêntica a antes do refactor.
