# SPRINT_014.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 014
**Status:** Concluída
**Versão da Arquitetura:** Sistema de Vidas (Núcleo Funcional)

---

## Objetivo da Sprint

Implementar o núcleo funcional do Sistema de Vidas descrito no
`VISAO.md`: ao morrer, o jogador consome uma vida e revive
automaticamente, até esgotar o limite disponível — substituindo o
"game over" silencioso e definitivo que existia desde a Sprint 007.

---

## Situação Inicial

Ao final da Sprint 013, a morte do jogador travava o personagem
permanentemente, sem nenhuma chance de continuar — mesmo que o jogo
já tivesse toda a arquitetura de combate, salas e progressão
funcionando, uma única derrota encerrava a sessão sem retorno.

---

## Problema

Um jogo de sobrevivência sem chance de recuperação após a morte é
frustrante e desincentiva a experimentação — o jogador não tem margem
para aprender com um erro tático. Além disso, a ausência de qualquer
sistema de vidas impede a validação, ainda que parcial, de um dos
pilares de monetização já registrados na visão do jogo.

---

## Decisão Arquitetural

### Núcleo Simples Antes da Experiência Completa

A visão completa do Sistema de Vidas (registrada no `VISAO.md`) prevê
distinção entre "continuar via vídeo, uma vez por morte" e "vida como
recurso persistente regenerável por tempo", além de compra com
dinheiro real e confirmação via interface. Esta Sprint implementa
deliberadamente apenas o núcleo mais simples — consumir uma vida e
reviver automaticamente — adiando as nuances de UI e regras de
monetização para quando uma tela de interface existir de fato.

Essa decisão segue o mesmo princípio já aplicado em Sprints anteriores
(por exemplo, a câmera na Sprint 008): provar o mecanismo central
primeiro, refinar depois.

### Revive Restaura Estado, não Posição

Ao reviver, o jogador recupera o HP máximo e o estado `is_dead` volta
a `False` — mas permanece na mesma posição em que morreu, na mesma
sala, com os mesmos inimigos ainda vivos ao redor. Essa decisão
(implícita, por simplicidade) mantém o risco imediato: reviver não é
um "recomeço seguro", é uma segunda chance na mesma situação de
perigo.

---

## Conceitos de Python

- **Métodos Pequenos e Nomeados para Cada Responsabilidade** —
  `revive()`, `has_lives_left()` e `consume_life()` são três métodos
  curtos, cada um com uma única responsabilidade clara, seguindo o
  mesmo padrão já estabelecido por `take_damage()` desde a Sprint 005.

---

## Conceitos de Arquitetura

- **Adiar Complexidade de Interface sem Adiar o Mecanismo Central** —
  a lógica de vidas funciona plenamente sem nenhuma tela de UI; a
  interface (barra de vidas, confirmação de continuar, tela de compra)
  pode ser construída depois, sobre uma base já funcional — evitando
  que a ausência de UI bloqueie o progresso da lógica de jogo.
- **Documentar a Lacuna entre Implementação Parcial e Visão Completa**
  — ao invés de deixar implícito que "o sistema de vidas está pronto",
  o `VISAO.md` foi atualizado com uma nota explícita do que falta,
  evitando a suposição futura (por qualquer pessoa lendo o documento)
  de que a funcionalidade está mais completa do que realmente está.

---

## Implementações

### Missão 1 — Atributos de Vida no Player

**Arquivo:** `player.py`

Adicionados `max_lives` e `lives` ao `__init__`.

### Missão 2 — Métodos de Revive e Consumo de Vida

**Arquivo:** `player.py`

Adicionados `revive()` (restaura HP e estado), `has_lives_left()`
(verifica se ainda há vidas) e `consume_life()` (decrementa o
contador).

### Missão 3 — Conexão no Ciclo de Morte

**Arquivo:** `game_scene.py`

Ao detectar `player.is_dead`, o fluxo agora consome uma vida e
verifica se ainda restam vidas: em caso positivo, reviva o jogador; em
caso negativo, mantém o comportamento anterior de "game over
definitivo".

---

## Estado Atual da Arquitetura

```
Player
 ├── max_lives / lives
 ├── revive() — restaura HP, is_dead = False
 ├── has_lives_left() — bool
 └── consume_life() — decrementa lives

GameScene.update()
 └── ao morrer: consume_life() -> revive() se houver vidas, senão game over definitivo
```

Testado o ciclo completo: 4 revives consecutivos (5 vidas → 0),
culminando corretamente em "game over definitivo" na última morte.

---

## O que o aluno aprendeu

Como implementar o núcleo funcional de um sistema antes de qualquer
interface, validando a lógica isoladamente. Como documentar
explicitamente a diferença entre uma implementação parcial e a visão
completa de uma funcionalidade, para que a lacuna fique visível e
rastreável, não escondida atrás de um recurso aparentemente "pronto".

---

## Próxima Sprint

Sprint 015 — a definir entre: sistema de Reentradas Limitadas
(estrutura similar ao de Vidas, reutilizável), avanço na Progressão
Espacial (ondas múltiplas por sala), ou início de uma tela de UI
básica (HP, vidas, contador de sala) para dar suporte visual aos
sistemas já implementados.

---

## Resumo Executivo

Esta Sprint implementa o núcleo funcional do Sistema de Vidas: o
jogador consome uma vida e revive automaticamente ao morrer, até
esgotar o limite disponível, substituindo o antigo "game over"
definitivo e silencioso. A implementação foi deliberadamente mantida
simples, adiando UI e regras de monetização, com a lacuna entre o que
foi implementado e a visão completa documentada explicitamente no
`VISAO.md`.
