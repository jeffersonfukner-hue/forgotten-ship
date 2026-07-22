# SPRINT_003.md
### Forgotten Ship — A1 Game Academy

> **Nota sobre esta versão:** esta Sprint foi reescrita para servir como
> material didático estruturado, contando a evolução da arquitetura de
> forma clara e pedagógica — não como um relato histórico literal do
> processo original de desenvolvimento. O objetivo é ensinar bem, não
> documentar cada passo em vão.

**Sprint:** 003
**Status:** Concluída
**Versão da Arquitetura:** Múltiplas Salas, Orientada a Dados

---

## Objetivo da Sprint

Expandir de uma única porta isolada para um mapa com múltiplas salas
conectadas, eliminando a criação manual de cada porta dentro do código.
Em vez disso, salas e portas passam a ser descritas por **estruturas de
dados**, e o código passa a *ler* essas estruturas para montar o mundo
do jogo.

---

## Situação Inicial

Ao final da Sprint 002, existiam duas salas e uma porta, mas a porta
era criada diretamente dentro da `GameScene`, com seus valores escritos
à mão no código:

```python
door = Door(x=340, y=520, width=40, height=20, side=BOTTOM, ...)
room.add_door(door)
```

Isso funciona para uma porta, mas não escala: adicionar a quinta ou
décima sala exigiria repetir esse bloco de código várias vezes,
misturando "o que existe no jogo" com "como o jogo é montado".

---

## Problema

Criar cada sala e porta manualmente no código torna qualquer expansão
do mapa trabalhosa e arriscada — cada nova sala é mais código repetido,
e qualquer ajuste (mover uma porta, mudar uma conexão) exige editar
lógica de programação em vez de apenas um dado.

Também não havia nenhum reaproveitamento: se o jogador voltasse a uma
sala já visitada, uma nova instância seria criada do zero, perdendo
qualquer estado que a sala pudesse ter no futuro (portas destrancadas,
itens coletados, etc.).

---

## Decisão Arquitetural

Duas mudanças estruturais resolvem isso:

### 1. Cache de Salas

A `GameScene` passa a guardar todas as salas já criadas em um
dicionário. Uma sala só é criada na primeira visita; nas visitas
seguintes, a mesma instância é reaproveitada.

```python
self.rooms: dict[int, Room] = {}

def create_room(self, room_id: int) -> Room:
    if room_id in self.rooms:
        return self.rooms[room_id]
    room = Room(...)
    self.configure_room(room, room_id)
    self.rooms[room_id] = room
    return room
```

### 2. Dados Separados de Sala e de Porta

Em vez de cada `Room` guardar portas completas, dois dicionários
independentes descrevem o mundo:

- **`room_data`** — para cada sala, apenas os **IDs** das portas que
  pertencem a ela.
- **`door_data`** — para cada porta, todos os seus dados completos:
  posição, tamanho, lado, e para qual **porta** (não sala) ela leva.

```python
room_data = {
    1: {"doors": [1, 2]},
    2: {"doors": [3]},
}

door_data = {
    1: {"room": 1, "x": 340, "y": 60, ..., "target": 3},
}
```

Um método `configure_room()` lê `room_data`, busca cada porta
correspondente em `door_data`, e monta os objetos `Door` reais.

### Por que "porta destino" e não "sala destino"

Cada porta agora conhece **outra porta** (`target_door`), não uma sala
diretamente. Isso pode parecer um passo extra, mas resolve um problema
real: a porta de destino já sabe exatamente sua própria posição e seu
próprio `get_spawn_position()` — então a navegação nunca precisa
perguntar "onde nessa sala o jogador deveria aparecer?" separadamente.
A resposta já vem de graça, porque veio da porta certa.

---

## Conceitos de Python

- **Dicionários Aninhados** — `room_data` e `door_data` são dicionários
  cujos valores também são dicionários, um padrão comum para descrever
  "tabelas" de configuração em Python.
- **Cache com Dicionário** — usar `dict[int, Room]` como memória de
  objetos já criados, evitando recriação desnecessária.
- **Separação entre Dados e Lógica** — os dados (`room_data`,
  `door_data`) vivem soltos, e o código (`configure_room`) apenas os
  interpreta — uma mudança de mentalidade importante em relação a
  escrever tudo direto em código.

---

## Conceitos de Arquitetura

- **Arquitetura Orientada a Dados** — descrever o mundo do jogo como
  dados estruturados, não como sequências de código imperativo. Isso
  aproxima o projeto de features futuras como salvar/carregar mapas ou
  gerar salas proceduralmente.
- **Baixo Acoplamento entre Room e Door** — a `Room` não precisa saber
  os detalhes de cada porta antecipadamente; ela só conhece IDs, e
  busca os detalhes quando necessário via `get_door_by_id()`.
- **Cache de Objetos** — nem sempre recriar um objeto é a abordagem
  certa; preservar instâncias existentes economiza processamento e
  abre caminho para estado persistente por sala no futuro.

---

## Implementações

### Missão 1 — Cache de Salas

**Arquivo:** `game_scene.py`

Implementado `self.rooms: dict[int, Room]` e o método `create_room()`,
que verifica o cache antes de criar uma nova sala.

**Resultado:** revisitar uma sala já visitada reaproveita a mesma
instância, em vez de recriar do zero.

### Missão 2 — Separação de room_data e door_data

**Arquivo:** `game_scene.py`

Criadas as estruturas `room_data` (IDs de portas por sala) e
`door_data` (dados completos de cada porta, incluindo `target`, que
aponta para outra porta). O método `configure_room()` passou a ler
essas estruturas e montar os objetos `Door` dinamicamente.

**Resultado:** adicionar uma nova sala ou porta passa a ser uma questão
de adicionar entradas nos dicionários, sem tocar na lógica de criação.

### Missão 3 — Door com ID Próprio e Busca por ID

**Arquivos:** `door.py`, `room.py`

`Door` ganhou um identificador próprio (`self.id`), permitindo
localizar qualquer porta independentemente de qual sala a contém.
`Room` ganhou o método `get_door_by_id()`, usado durante a navegação
para encontrar a porta de destino exata.

### Missão 4 — Navegação Porta-a-Porta

**Arquivo:** `game_scene.py`

O fluxo de transição de sala passou a seguir a cadeia: porta atual →
`target_door` → sala dessa porta → spawn dessa porta.

```python
target_door_id = self.player.current_door.target_door
self.current_room_id = self.door_data[target_door_id]["room"]
self.room = self.create_room(self.current_room_id)
target_door = self.room.get_door_by_id(target_door_id)
spawn_x, spawn_y = target_door.get_spawn_position()
```

**Resultado:** três salas conectadas em ciclo (Room 1 → 2 → 3 → 1),
navegando corretamente entre elas usando apenas os dados.

---

## Estado Atual da Arquitetura

```
GameScene
 ├── room_data (IDs de portas por sala)
 ├── door_data (dados completos + porta destino)
 ├── rooms: dict[int, Room]  (cache)
 └── configure_room() monta Room + Door a partir dos dados

Room
 └── get_door_by_id()

Door
 ├── self.id
 └── target_door (aponta para outra porta, não outra sala)
```

Esta é a arquitetura atual do projeto — a mesma sobre a qual as
próximas Sprints (a partir da 004) continuam evoluindo.

---

## O que o aluno aprendeu

Como transformar código repetitivo em dados estruturados, e por que
isso facilita expandir um projeto. Como implementar um cache simples
com dicionário para evitar recriar objetos desnecessariamente. Como
desacoplar duas entidades relacionadas (Room e Door) para que cada
uma conheça apenas o que precisa, delegando o resto a buscas por ID.

---

## Próxima Sprint

Refinar pendências da arquitetura orientada a dados: remover
definitivamente `Room.get_spawn()` (substituído por
`Door.get_spawn_position()`), revisar métodos remanescentes da
arquitetura anterior, e validar a navegação em mapas maiores.

---

## Resumo Executivo

Esta Sprint transforma um mapa de salas criadas manualmente em uma
arquitetura orientada a dados: `room_data` e `door_data` descrevem o
mundo do jogo como estruturas simples, um cache evita recriação de
salas já visitadas, e a navegação passa a acontecer entre portas — não
mais entre salas diretamente. É a arquitetura que sustenta o projeto
até hoje.
