# SPRINT_012.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 012
**Status:** Concluída
**Versão da Arquitetura:** Rejogabilidade — Hordas Crescentes por Revisita

---

## Objetivo da Sprint

Implementar a rejogabilidade descrita no `VISAO.md`: ao reentrar em
uma sala já limpa, uma nova horda — maior que a anterior — deve
surgir, com as portas voltando a se trancar até que essa nova horda
seja derrotada.

---

## Situação Inicial

Ao final da Sprint 011, uma sala limpa permanecia vazia para sempre —
o cache de salas (Sprint 003) preservava o estado sem inimigos
indefinidamente, permitindo ao jogador atravessar livremente qualquer
sala já vencida uma vez, sem risco algum.

---

## Problema

Sem hordas recorrentes, o jogo perde tensão em qualquer sala já
visitada — o "backtracking" natural do design de mapas conectados
(voltar para melhorar pontuação, ou buscar material faltante, como
descrito na Progressão Espacial) se tornaria trivial e sem risco,
contradizendo a visão de um jogo de sobrevivência.

---

## Decisão Arquitetural

### Contador de Limpezas por Sala

Cada `Room` passou a rastrear `times_cleared`, incrementado toda vez
que ela é esvaziada de inimigos. Esse contador determina o tamanho da
próxima horda ao reentrar, e também alimenta diretamente a estatística
"quantas vezes o jogador entrou nesta sala" já registrada no `VISAO.md`.

### Fórmula de Escala de Dificuldade

A quantidade de inimigos por horda segue uma fórmula simples:
`12 + (times_cleared * 6)` — a primeira horda já é robusta (12
inimigos, evitando a crítica válida de que "3 inimigos não é uma
horda, é um grupo de amigos"), crescendo de forma previsível a cada
revisita.

### Extração da Lógica de Spawn para Reutilização

A criação de inimigos, antes presa dentro de `configure_room()` e
usada apenas na criação inicial da sala, foi extraída para um método
próprio (`spawn_horde()`), reutilizável tanto na configuração inicial
quanto no respawn ao reentrar — evitando duplicar a lógica de sorteio
de posições nas bordas.

### Ciclo de "Limpa → Aguardando Reentrada → Nova Horda"

Uma sala passa por um ciclo de estados implícito, controlado por dois
atributos (`cleared` e `times_cleared`):

1. Sala com inimigos: portas trancadas.
2. Última inimigo eliminado: portas destrancadas, `cleared = True`,
   `times_cleared` incrementado.
3. Jogador sai e reentra: se `cleared` e sem inimigos, uma nova horda
   (maior) é gerada, portas trancam novamente, `cleared` volta a
   `False`.

O gatilho para a nova horda foi posicionado em `create_room()` — o
ponto natural em que uma sala já existente é "reaberta" — evitando
respawn indesejado enquanto o jogador ainda está dentro da sala.

---

## Conceitos de Python

- **Extração de Método (Refactoring)** — mover a lógica de criação de
  inimigos de dentro de um bloco condicional (`if room_id == 1`) para
  um método nomeado e reutilizável (`spawn_horde`) é um refactoring
  clássico: mesmo comportamento, melhor organização e reuso.
- **Fórmula Linear como Configuração de Dificuldade** — usar uma
  expressão simples (`base + incremento * contador`) em vez de valores
  fixos por caso, tornando o ajuste de balanceamento uma questão de
  mudar dois números, não reescrever lógica.

---

## Conceitos de Arquitetura

- **Estado Implícito via Combinação de Atributos** — o "ciclo" da sala
  (limpa → aguardando → nova horda) não é modelado como uma máquina de
  estados explícita (como a do `Player`, Sprint 002), mas como a
  combinação de dois valores simples (`cleared`, contagem de
  inimigos). Para a complexidade atual, isso é suficiente — mas é um
  candidato a virar uma máquina de estados formal se mais transições
  forem adicionadas no futuro (ex: ondas múltiplas).
- **Ponto de Gatilho Correto para Efeitos Colaterais** — decidir que o
  respawn acontece em `create_room()` (não em `update()`) evita o erro
  comum de disparar um efeito repetidamente enquanto uma condição
  permanece verdadeira; o gatilho certo é o evento de transição
  (reabrir a sala), não a verificação contínua.

---

## Implementações

### Missão 1 — Contadores na Room

**Arquivo:** `room.py`

Adicionados `times_cleared` e `cleared` ao `__init__`.

### Missão 2 — Extração de `spawn_horde()`

**Arquivo:** `game_scene.py`

Lógica de criação de inimigos extraída para `spawn_horde(room)`,
usando a fórmula de escala baseada em `room.times_cleared`.

### Missão 3 — Marcação de Sala Limpa

**Arquivo:** `game_scene.py`

O trecho de destravamento de portas (Sprint 010) passou a também
marcar `room.cleared = True` e incrementar `room.times_cleared`,
executando apenas uma vez por ciclo (verificação de `not room.cleared`
evita repetição a cada frame).

### Missão 4 — Respawn ao Reentrar

**Arquivo:** `game_scene.py`

`create_room()` passou a verificar, ao reabrir uma sala já em cache,
se ela está `cleared` e sem inimigos — gerando uma nova horda,
trancando as portas novamente, e resetando `cleared` para `False`.

---

## Decisões de Design Registradas para Sprints Futuras

Durante esta Sprint, uma série de decisões de design relacionadas
foram discutidas e registradas no `VISAO.md`, sem serem implementadas
ainda:

- **Salas trancadas nos dois sentidos:** confirmado que o mecanismo
  atual (trancar todas as portas da sala com inimigos) já cobre essa
  necessidade — nenhuma implementação adicional foi necessária.
- **Reentradas limitadas:** sistema de tentativas regenerável por
  tempo (ex: 5 reentradas, +1 por hora), com confirmação antes de
  consumir, para revisitas de salas já vencidas.
- **Sistema de Vidas:** distinto das Reentradas — limita quantas vezes
  o jogador pode continuar após morrer dentro de uma sessão de horda
  (1 vez via vídeo, depois recurso limitado e regenerável, ou compra
  com dinheiro real).
- **Saída antecipada com progresso parcial:** questão em aberto,
  dependente da decisão futura de ondas múltiplas por sala.

Essas três primeiras formam, junto da "Energia" já registrada
anteriormente, um conjunto de três sistemas de recurso do jogo com
estrutura semelhante mas propósitos distintos — consolidados em uma
nota específica no `VISAO.md` para evitar confusão futura entre eles.

---

## Estado Atual da Arquitetura

```
Room
 ├── times_cleared: int
 └── cleared: bool

GameScene
 ├── spawn_horde(room) — gera horda com tamanho baseado em times_cleared
 ├── update(): ao esvaziar a sala pela primeira vez no ciclo,
 │             destranca portas, marca cleared, incrementa times_cleared
 └── create_room(): ao reabrir sala já cleared e vazia,
                     gera nova horda, tranca portas, reseta cleared
```

Testado na Sala 1: primeira horda com 12 inimigos; ao reentrar após
limpar, uma nova horda de 18 inimigos surge, com as portas trancadas
novamente até vencê-la.

---

## O que o aluno aprendeu

Como extrair um bloco de lógica repetido em uma função reutilizável
(refactoring), preparando o código para múltiplos pontos de uso. Como
modelar um ciclo de estados simples através da combinação de poucos
atributos, sem necessariamente construir uma máquina de estados
formal, quando a complexidade não justifica ainda. Como identificar o
ponto correto no código para disparar um efeito colateral (respawn),
evitando repetição indesejada ao confundir "verificação contínua" com
"evento de transição".

---

## Próxima Sprint

Sprint 013 — a definir entre: sistema de Reentradas Limitadas, Sistema
de Vidas, ou avanço na Progressão Espacial (ondas múltiplas por sala
com material composto). Também candidato: extensão de inimigos para
todas as salas do jogo, não apenas a Sala 1.

---

## Resumo Executivo

Esta Sprint implementa a rejogabilidade do jogo: salas já vencidas
voltam a apresentar hordas — maiores a cada revisita — ao serem
reabertas, com portas se trancando novamente até a nova horda ser
derrotada. Uma rica discussão de design sobre sistemas de recurso
(Reentradas, Vidas, Energia) foi registrada no `VISAO.md` para
implementação futura, mantendo o escopo desta Sprint focado e conciso.
