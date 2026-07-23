# SPRINT_004.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 004
**Status:** Concluída
**Versão da Arquitetura:** Navegação Orientada a Dados, com Portas e Transições Refinadas

---

## Objetivo da Sprint

Consolidar a arquitetura orientada a dados introduzida na Sprint 003
(`room_data` / `door_data`), eliminar métodos remanescentes da
arquitetura anterior, e corrigir bugs reais de navegação encontrados
durante o desenvolvimento — incluindo um bug crítico de loop infinito
de transição entre salas.

---

## Situação Inicial

Ao final da Sprint 003, a arquitetura já separava `room_data` (IDs de
portas por sala) de `door_data` (dados completos de cada porta,
incluindo `target_door`). No entanto, restavam pendências:

- `Room.get_spawn()` ainda existia e ainda era usado para o spawn
  inicial do jogador, duplicando a responsabilidade que já deveria
  pertencer a `Door.get_spawn_position()`.
- Nunca havia sido testada a navegação em um mapa com mais de 3 salas.
- Um bug antigo, já identificado (mas não corrigido) na Sprint 003 —
  o jogador reaparecendo em cima da área de colisão de outra porta —
  continuava presente.

---

## Problema

Ao investigar a fundo, o problema de navegação se revelou mais sério
do que o registro original da Sprint 003 sugeria: em determinadas
condições, o jogo entrava em um **loop infinito de transições**,
alternando automaticamente entre duas salas sem qualquer input do
jogador.

Além disso, ao corrigir esse problema, surgiram dois problemas visuais
relacionados à física da entrada em portas: o jogador atravessando
"torto" ao tocar a porta pela quina, e uma sobreposição visual pouco
polida entre o corpo do jogador e a parede durante a travessia.

---

## Decisão Arquitetural

### 1. Unificação do Spawn

O spawn inicial do jogador passou a vir da mesma fonte de dados que
qualquer transição de sala: `room_data[room_id]["spawn"]`. Isso
eliminou `Room.get_spawn()` e o atributo `self.spawn` calculado
automaticamente dentro de `Room` — a posição de entrada de uma sala
agora é sempre um dado explícito, nunca um cálculo implícito da
própria sala.

### 2. Navegação Porta-a-Porta, com Sincronização de Posição Corrigida

O `Player` guarda sua posição em dois formatos: coordenadas float
(`self.x`, `self.y`, usadas no cálculo de movimento) e um `pygame.Rect`
(usado para desenho e colisão). A troca de sala atualizava apenas o
`rect`, deixando as coordenadas float presas à posição da sala
anterior — no frame seguinte, o movimento recalculava o `rect` a
partir dessas coordenadas antigas, fazendo o jogador "voltar" para a
posição de antes da transição. Como várias portas compartilham
coordenadas de tela entre salas diferentes, essa posição fantasma
frequentemente coincidia com o trigger de outra porta, dando origem ao
loop infinito.

A correção sincroniza `self.x`/`self.y` com o `rect` sempre que a
posição é definida externamente (spawn inicial e troca de sala).

### 3. Distância de Spawn Considerando o Corpo do Jogador

`SPAWN_OFFSET` definia a distância do **centro** do jogador até a
porta, mas não considerava que o jogador é um retângulo de 32x32px,
não um ponto. Mesmo com o offset corrigido para escapar do centro do
trigger, a borda do corpo do jogador ainda podia invadi-lo. O offset
final (40px) considera: metade da espessura do trigger da porta, mais
metade do corpo do jogador, com margem de segurança.

### 4. Entrada em Duas Etapas (Alinhamento + Travessia)

Ao tocar o trigger de uma porta a partir de um ângulo (por exemplo,
pela quina), guiar o jogador diretamente ao ponto de entrada causava
um movimento diagonal visualmente estranho. A solução divide o
trajeto guiado em duas etapas: primeiro alinhar o eixo perpendicular
ao movimento com o centro da porta, depois avançar em linha reta para
dentro dela.

### 5. Fade Proporcional à Espessura Real da Porta

O jogador passa a ficar progressivamente transparente durante a etapa
final de travessia, com a transparência calculada em proporção à
distância percorrida em relação à espessura real da porta (não um
valor arbitrário) — garantindo que ele esteja completamente invisível
exatamente quando atravessa a parede, independentemente do tamanho da
porta.

---

## Conceitos de Python

- **Listas como Filas de Trajeto (`path`)** — o trajeto de entrada em
  duas etapas é implementado como uma lista de pontos a percorrer, com
  `pop(0)` avançando para o próximo assim que o atual é alcançado.
- **`pygame.Surface` com `SRCALPHA`** — usada para desenhar o jogador
  com transparência variável, criando uma superfície separada com
  canal alfa em vez de desenhar diretamente na tela.
- **Métodos de Cálculo Puro** — `get_alignment_point`,
  `get_entry_target`, `get_thickness` calculam posições e distâncias
  sem modificar estado, mantendo `Door` como uma fonte confiável de
  informação geométrica.

---

## Conceitos de Arquitetura

- **Fonte Única de Verdade para Posição** — quando uma entidade guarda
  a mesma informação (posição) em mais de um formato, todo ponto de
  escrita precisa atualizar todos os formatos, ou eles saem de
  sincronia de forma silenciosa e difícil de depurar.
- **Cálculos Geométricos Não Devem Ignorar o Tamanho do Objeto** —
  tratar uma entidade como um ponto (em vez de um retângulo com
  dimensão real) foi a causa raiz de três bugs distintos nesta Sprint
  (spawn, alinhamento diagonal, sobreposição visual).
- **Arquitetura Orientada a Dados Validada em Escala** — a expansão do
  mapa de 3 para 5 salas, incluindo portas em todos os quatro lados
  (`TOP`, `BOTTOM`, `LEFT`, `RIGHT`), não exigiu nenhuma mudança de
  lógica — apenas novas entradas em `room_data` e `door_data`,
  confirmando o benefício da decisão tomada na Sprint 003.

---

## Implementações

### Missão 1 — Remoção de `Room.get_spawn()`

**Arquivos:** `room.py`, `game_scene.py`

Removidos `self.spawn` e `get_spawn()` de `Room`. Adicionado
`"spawn": (x, y)` em `room_data` para a sala inicial. O spawn do
jogador passou a ser lido diretamente de `room_data`.

### Missão 2 — Correção do Loop Infinito de Transição

**Arquivos:** `game_scene.py`

Ao definir a posição do jogador após uma transição de sala,
`self.x`/`self.y` passaram a ser sincronizados junto com o `rect`:

```python
self.player.x = spawn_x - self.player.width / 2
self.player.y = spawn_y - self.player.height / 2
self.player.rect.center = (spawn_x, spawn_y)
```

Combinado ao ajuste de `SPAWN_OFFSET` (16 → 40, em `door.py`),
eliminou completamente o loop de transições automáticas.

### Missão 3 — Entrada em Duas Etapas

**Arquivos:** `door.py`, `player.py`, `game_scene.py`

Adicionado `Door.get_alignment_point()`, calculando o ponto de
alinhamento perpendicular ao movimento. O `Player` passou a receber
uma lista de waypoints (`start_door_sequence`), percorrendo cada um em
sequência antes de solicitar a troca de sala.

### Missão 4 — Fade de Transparência na Travessia

**Arquivos:** `door.py`, `player.py`

Adicionado `Door.get_thickness()`, retornando a profundidade real da
porta. O `Player` calcula a distância percorrida na etapa final do
trajeto e converte essa proporção em transparência (`alpha`),
desenhando-se com `pygame.Surface(..., pygame.SRCALPHA)` quando
parcialmente transparente.

### Missão 5 — Debug Visual de Salas e Validação em Mapa Maior

**Arquivos:** `room.py`, `game_scene.py`

Adicionado `room_id` a `Room`, exibido na tela para facilitar debug
visual (complementando o ID de porta já existente desde a Sprint 003).
O mapa foi temporariamente expandido de 3 para 5 salas, incluindo
portas `LEFT`/`RIGHT` (nunca testadas antes), para validar a
escalabilidade da arquitetura orientada a dados. O mapa de 5 salas foi
mantido como base para a próxima Sprint.

---

## Bugs Encontrados

### Bug 1 — Loop Infinito de Transição entre Salas

**Sintoma:** ao trocar de sala, o jogo por vezes disparava
automaticamente uma nova transição, entrando em ciclo repetido entre
duas salas sem input do jogador.

**Causa:** a troca de sala atualizava `player.rect`, mas não
`player.x`/`player.y` — as coordenadas reais usadas no cálculo de
movimento a cada frame. No frame seguinte, a posição antiga
sobrescrevia o spawn correto. Como várias portas compartilham
coordenadas de tela entre salas diferentes, a posição fantasma
coincidia com o trigger de outra porta.

**Investigação:** identificado ao analisar o log de transições, que
mostrava trocas de sala não correspondentes às ações do jogador.

**Solução:** sincronizar `player.x`/`player.y` com `rect` em toda
definição externa de posição; aumentar `SPAWN_OFFSET` de 16 para 40,
considerando a espessura do trigger somada a metade do corpo do
jogador.

**Lição Aprendida:** quando uma entidade guarda posição em mais de um
formato, toda escrita de posição precisa manter ambos sincronizados.

### Bug 2 — Alinhamento Diagonal ao Entrar em Porta pela Quina

**Sintoma:** ao tocar uma porta fora do centro, o jogador era guiado
em diagonal até o ponto de entrada, atravessando visualmente "torto".

**Causa:** `get_alignment_point` e `get_entry_target` calculavam a
coordenada perpendicular de formas inconsistentes entre si — um
descontava metade da largura do jogador, o outro não.

**Investigação:** reproduzido entrando na porta deliberadamente pela
quina, e confirmado comparando os dois cálculos lado a lado.

**Solução:** ambos os métodos passaram a descontar consistentemente
metade das dimensões do jogador.

**Lição Aprendida:** cálculos geométricos relacionados (dois pontos do
mesmo trajeto) precisam usar a mesma referência de origem — inconsistências
sutis entre métodos aparentemente independentes produzem bugs difíceis
de enxergar no código, mas óbvios ao jogar.

---

## Estado Atual da Arquitetura

```
GameScene
 ├── room_data (IDs de portas + spawn por sala)
 ├── door_data (dados completos + porta destino)
 ├── rooms: dict[int, Room]  (cache)
 └── configure_room() monta Room + Door a partir dos dados

Room
 ├── room_id (debug visual)
 └── get_door_by_id()

Door
 ├── self.id
 ├── target_door
 ├── get_spawn_position()
 ├── get_alignment_point()
 ├── get_entry_target()
 └── get_thickness()

Player
 ├── path: list[Vector2]  (trajeto de entrada em etapas)
 ├── alpha (transparência durante travessia)
 └── x/y sincronizados com rect em toda definição externa de posição
```

Mapa atual: 5 salas conectadas, incluindo portas em todos os quatro
lados (`TOP`, `BOTTOM`, `LEFT`, `RIGHT`), validadas sem bugs de
navegação.

---

## O que o aluno aprendeu

Como um bug aparentemente aleatório (loop infinito) pode ter uma causa
determinística e simples (dessincronia entre duas representações de
posição). Como cálculos geométricos que ignoram o tamanho real de um
objeto — tratando-o como um ponto — produzem bugs sutis em cascata.
Como validar a escalabilidade de uma arquitetura orientada a dados na
prática, não apenas por inspeção do código.

---

## Próxima Sprint

Sprint 005 — a definir. Candidatos: reverter/consolidar o mapa de 5
salas em definitivo, ou iniciar a implementação dos primeiros sistemas
do novo direcionamento do jogo (ver `VISAO.md` v2.0): mecânica de
restauração de sistemas da nave e primeiro protótipo do Modo 1 (Horde
Interna).

---

## Resumo Executivo

Esta Sprint fecha a arquitetura de navegação iniciada na Sprint 003:
remove a última duplicidade de responsabilidade (`Room.get_spawn()`),
corrige um bug crítico de loop infinito de transições (causado por
dessincronia de posição do jogador), refina visualmente a entrada em
portas (alinhamento em duas etapas, fade proporcional à espessura da
porta), e valida a escalabilidade da arquitetura orientada a dados em
um mapa de 5 salas com portas em todos os lados.
