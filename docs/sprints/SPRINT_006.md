# SPRINT_006.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 006
**Status:** Concluída
**Versão da Arquitetura:** Múltiplos Inimigos, Separação e Knockback

---

## Objetivo da Sprint

Expandir de um único inimigo para múltiplos inimigos simultâneos na
mesma sala, validando que a arquitetura de inimigos por sala (Sprint
005) já suporta essa escala sem mudanças estruturais. Além disso,
refinar o comportamento visual e físico dos inimigos: nascimento nas
bordas da sala, separação entre eles (evitando sobreposição), e reação
física do jogador ao ser atingido (knockback).

---

## Situação Inicial

Ao final da Sprint 005, existia um único inimigo, criado em uma
posição fixa dentro da sala, perseguindo o jogador sem nenhuma
interação com outros inimigos (pois só havia um) e sem nenhuma reação
física do jogador ao sofrer dano além da perda de vida.

---

## Problema

Um jogo de sobrevivência do gênero Horde depende de volume de
inimigos simultâneos para gerar tensão — um único inimigo não
representa desafio real. Além disso, posições fixas de nascimento não
escalam (cada inimigo novo exigiria uma coordenada escrita à mão), e
sem separação entre eles, múltiplos inimigos se sobrepõem visualmente,
ocupando o mesmo espaço de forma pouco natural.

---

## Decisão Arquitetural

### 1. Validação de Escala (sem mudança estrutural)

O primeiro teste foi o mais simples possível: adicionar múltiplos
`Enemy` na mesma sala, reutilizando a lista já existente desde a
Sprint 005 (`Room.enemies`). Nenhuma mudança de arquitetura foi
necessária — a lista, o loop de atualização e a checagem de colisão
já suportavam múltiplos itens desde a criação.

### 2. Spawn Aleatório nas Bordas

Em vez de coordenadas fixas, os inimigos passaram a nascer em posições
aleatórias ao longo das quatro bordas internas da sala (usando
`Room.get_bounds()`, já existente desde a Sprint 002). Isso aproxima o
jogo do padrão visual esperado do gênero: inimigos "invadindo" a partir
das paredes, não aparecendo do nada no meio do espaço jogável.

### 3. Separação entre Inimigos (Steering Simples)

Inimigos que colidem entre si agora se afastam levemente, somando um
vetor de "empurrão" (na direção oposta ao inimigo sobreposto) ao vetor
de perseguição do jogador. Isso é uma versão simplificada de uma
técnica comum em IA de jogos (comportamento de separação, parte dos
"steering behaviors" clássicos), suficiente para evitar sobreposição
sem exigir um sistema de física completo.

### 4. Knockback no Jogador

Ao sofrer dano, o jogador agora é empurrado uma pequena distância na
direção oposta ao inimigo que o atingiu. Isso dá uma resposta física
imediata ao dano, além de criar um pequeno espaço entre jogador e
inimigo — reduzindo a chance de dano repetido instantâneo mesmo com o
cooldown já existente.

---

## Conceitos de Python

- **`random.randint()` para Posições Aleatórias** — usado para
  escolher tanto a borda de nascimento quanto a posição ao longo dela.
- **Soma de Vetores para Combinar Comportamentos** — o vetor de
  perseguição e o vetor de separação são somados e depois
  renormalizados, uma técnica comum para combinar múltiplas influências
  de movimento em uma única direção final.
- **Iteração com Auto-Referência (`if other is self: continue`)** —
  ao iterar sobre a lista de inimigos para calcular separação, cada
  inimigo precisa pular a si mesmo na comparação, usando `is` (identidade
  de objeto) em vez de `==` (igualdade de valor).

---

## Conceitos de Arquitetura

- **Escala Validando Decisões Anteriores** — o fato de múltiplos
  inimigos funcionarem sem nenhuma mudança estrutural é a prova de que
  a decisão da Sprint 005 (inimigos pertencerem à sala, em uma lista)
  foi a decisão correta — o mesmo padrão de validação já visto na
  Sprint 004, quando o mapa cresceu de 3 para 5 salas sem exigir
  mudanças de lógica.
- **Comportamentos Combináveis (Steering)** — em vez de um `if/elif`
  decidindo entre "perseguir" ou "se separar", os dois comportamentos
  coexistem como vetores somáveis — uma abordagem que escala melhor
  conforme mais comportamentos forem adicionados no futuro (ex: fugir
  de projéteis, manter formação).

---

## Implementações

### Missão 1 — Múltiplos Inimigos

**Arquivo:** `game_scene.py`

Adicionadas múltiplas chamadas a `room.add_enemy()` dentro de
`configure_room()`, validando que a arquitetura já suportava a
mudança de escala sem ajustes.

### Missão 2 — Spawn nas Bordas

**Arquivo:** `game_scene.py`

Substituídas as coordenadas fixas por um sorteio de borda (topo, base,
esquerda, direita) e uma posição aleatória ao longo dela, usando os
limites reais da sala (`get_bounds()`).

### Missão 3 — Separação entre Inimigos

**Arquivo:** `enemy.py`

O método `update()` do `Enemy` passou a receber a lista completa de
inimigos da sala, calculando um vetor de afastamento para qualquer
inimigo colidindo com ele, somado ao vetor de perseguição do jogador.

### Missão 4 — Knockback no Jogador

**Arquivo:** `player.py`

Adicionado `apply_knockback()`, aplicando um deslocamento instantâneo
na direção oposta à origem do dano, chamado junto com `take_damage()`
no momento da colisão.

---

## Estado Atual da Arquitetura

```
GameScene.configure_room()
 └── gera N inimigos em posições aleatórias nas bordas da sala

Enemy.update(dt, target_x, target_y, others)
 ├── persegue o alvo (jogador)
 └── se afasta de outros inimigos colidindo (separação)

Player
 ├── take_damage(amount)
 └── apply_knockback(from_x, from_y)  — empurrão ao sofrer dano
```

Múltiplos inimigos convivem na mesma sala sem se sobrepor visualmente,
perseguindo o jogador de forma independente. O jogador reage
fisicamente ao contato, sendo empurrado para longe do inimigo que o
atingiu.

---

## O que o aluno aprendeu

Como validar que uma decisão de arquitetura escala, simplesmente
testando com mais itens — sem presumir que "vai funcionar", mas
efetivamente rodando o teste. Como combinar múltiplos comportamentos
de movimento (perseguição e separação) somando vetores, em vez de
alternar entre eles com condicionais. Como usar `is` para comparação
de identidade de objeto, distinguindo-a de `==` (igualdade de valor).

---

## Próxima Sprint

Sprint 007 — sistema de ataque automático do jogador (mirando o
inimigo mais próximo) e capacidade dos inimigos de morrer, primeiro
passo do ciclo de combate completo descrito no Backlog Detalhado do
Modo 1 (`VISAO.md`).

---

## Resumo Executivo

Esta Sprint expande o jogo de um único inimigo estático para múltiplos
inimigos dinâmicos: nascendo aleatoriamente nas bordas da sala,
evitando sobreposição entre si através de um comportamento de
separação, e provocando uma reação física real no jogador (knockback)
ao causar dano. A escala validou, mais uma vez, que as decisões de
arquitetura tomadas em Sprints anteriores (inimigos por sala) foram
soluções corretas e duradouras.
