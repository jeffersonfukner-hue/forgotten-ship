# SPRINT_025.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 025
**Status:** Concluída
**Versão da Arquitetura:** Histórico por Visita e Composição Evolutiva de Inimigos

---

## Objetivo da Sprint

Resolver a pendência registrada na Sprint 024 (histórico detalhado por
visita individual de sala), adiantar parte do planejamento da Sprint
026 (composição de tipos de inimigo evoluindo com o tempo dentro da
sala), e corrigir um bug de longa data: inimigos nunca respeitavam os
limites físicos da sala, podendo atravessar paredes.

---

## Situação Inicial

Ao final da Sprint 024, o painel de debug exibia apenas o estado atual
acumulado de cada sala (visitas, reentradas, estatísticas), sem
nenhum registro de visitas individuais anteriores. Todos os inimigos
gerados eram do tipo `"weak"`, independentemente do tempo de
permanência na sala. Adicionalmente, `Enemy.update()` nunca clampava
sua posição aos limites da sala — diferente do `Player`, que já
respeitava esses limites desde a Sprint 001.

---

## Problema

Sem histórico por visita, era impossível comparar o desempenho do
jogador entre diferentes sessões na mesma sala — informação
explicitamente desejada para alimentar futuros rankings e análises
estatísticas. Sem composição evolutiva de tipos, a única fonte de
dificuldade crescente dentro de uma sala era a quantidade normal do
piso contínuo, sem a variedade qualitativa planejada na pesquisa de
gênero (Sprint 024). O bug de colisão com paredes, embora presente
desde o início do projeto, só se tornou perceptível com salas grandes
e inimigos permanecendo vivos por mais tempo (piso contínuo).

---

## Decisão Arquitetural

### Histórico como Lista de Registros Imutáveis

`Room` passou a manter `visit_history`, uma lista de dicionários — um
por visita concluída, capturando `clear_time`, `kills_by_type`,
`points_by_type` e `total_points` no momento exato da conclusão. Os
dicionários de estatística são copiados (`dict(...)`) ao registrar,
evitando que o reset de estatísticas da próxima visita afete
retroativamente o histórico já salvo.

### Reset de Estatísticas ao Reabrir a Sala

`kills_by_type`/`points_by_type` da `Room` passaram a ser reiniciados
no início de cada nova visita (`spawn_horde`), já que o histórico
preserva os dados da visita anterior separadamente — evitando que
estatísticas de sessões diferentes se misturem no mesmo acumulador.

### Chance de Inimigo Forte Crescendo com o Tempo

Cada inimigo gerado (tanto na criação inicial quanto no
reabastecimento contínuo) tem seu tipo escolhido individualmente por
`_pick_enemy_type()`: a chance de ser do tipo `"strong"` cresce
linearmente com o tempo decorrido na sala, até um teto configurável —
substituindo a atribuição de um único tipo fixo por toda uma leva de
inimigos.

### Limites de Sala Aplicados ao Inimigo

`Enemy.update()` passou a receber os limites da sala (`bounds`) como
parâmetro, aplicando o mesmo clamp de posição já usado pelo `Player`
desde a fundação do projeto.

---

## Conceitos de Python

- **Cópia Defensiva de Dicionários (`dict(...)`)** — ao registrar uma
  entrada de histórico, copiar o dicionário de estatísticas evita que
  ele continue sendo a mesma referência que será posteriormente
  modificada (ou resetada) pela lógica da próxima visita — um erro
  sutil que só se manifestaria ao inspecionar entradas antigas do
  histórico depois de uma nova visita começar.
- **Interpolação Linear Limitada por `min()`** — `_pick_enemy_type()`
  calcula `progress = min(1.0, elapsed / ramp_time)`, um padrão comum
  para crescer um valor de forma linear até um teto, sem ultrapassá-lo.
- **Parâmetro Adicional Propagado por Toda a Cadeia de Chamada** — a
  correção do bug de paredes exigiu passar `bounds` não apenas para
  `Enemy.update()`, mas também ajustar o ponto de chamada em
  `GameScene.update()` — um lembrete de que corrigir uma assinatura de
  método exige rastrear todos os lugares que o invocam.

---

## Conceitos de Arquitetura

- **Snapshot Imutável vs. Estado Corrente** — a distinção entre
  `kills_by_type` (estado corrente, mutável, reiniciado a cada visita)
  e as entradas de `visit_history` (snapshots imutáveis do passado) é
  um padrão fundamental para preservar histórico sem duplicar
  complexidade de sincronização.
- **Escolha Individual vs. Escolha em Lote** — migrar de "todos os
  inimigos de uma leva são do mesmo tipo" para "cada inimigo escolhe
  seu próprio tipo" é uma mudança pequena em código, mas
  qualitativamente importante: permite composições mistas emergirem
  naturalmente da probabilidade, sem precisar calcular proporções
  exatas manualmente.
- **Bugs que Escalam com o Ambiente** — o bug de colisão com paredes
  existia desde a Sprint 001, mas só se tornou visível quando salas
  grandes (Sprint 008) e inimigos de vida longa (piso contínuo,
  Sprint 024) se combinaram — reforçando que alguns bugs permanecem
  latentes até que mudanças em outras partes do sistema exponham suas
  consequências.

---

## Implementações

### Missão 1 — Histórico de Visitas na Room

**Arquivo:** `room.py`

Adicionado `visit_history: list[dict]`.

### Missão 2 — Registro de Visita ao Concluir a Sala

**Arquivo:** `game_scene.py`

Ao marcar `room.cleared = True`, uma entrada é adicionada a
`visit_history` com os dados daquela sessão específica.

### Missão 3 — Reset de Estatísticas por Visita

**Arquivo:** `game_scene.py`

`spawn_horde()` passou a reiniciar `kills_by_type`/`points_by_type`
da sala a cada nova visita.

### Missão 4 — Exibição do Histórico no Painel de Debug

**Arquivo:** `game_scene.py`

O painel de debug passou a listar, sob cada sala, as visitas já
concluídas (mais recente primeiro), incluindo a quebra por tipo de
inimigo de cada uma.

### Missão 5 — Composição Evolutiva de Tipos

**Arquivo:** `game_scene.py`

Adicionado `_pick_enemy_type()`, usado por `_spawn_wave_enemies()`
para escolher o tipo de cada inimigo individualmente, com chance de
`"strong"` crescendo linearmente com o tempo de sala.

### Missão 6 — Correção de Colisão com Paredes

**Arquivos:** `enemy.py`, `game_scene.py`

`Enemy.update()` passou a receber e respeitar os limites da sala,
aplicando o mesmo clamp de posição já usado pelo `Player`.

---

## Bugs Encontrados

### Bug — Cronômetro de Sobrevivência Continuava Após Game Over Definitivo

**Sintoma:** ao esgotar todas as vidas do jogador (game over
definitivo), o painel de debug continuava exibindo o tempo de
sobrevivência avançando indefinidamente, mesmo com o jogador travado
e sem nenhuma ação possível.

**Causa:** o cálculo de tempo decorrido (`time.time() -
survival_start_time`) não verificava se o jogador ainda estava
"jogando" — tanto no cálculo interno de `update()` quanto,
separadamente, no método de exibição do painel de debug
(`_build_survival_line`), que recalculava o tempo de forma
independente, sem saber do estado de game over.

**Investigação:** a primeira correção (no `update()`) não resolveu o
problema visualmente — revelando que o método de exibição fazia seu
próprio cálculo duplicado, em vez de reutilizar o valor já corrigido.

**Solução:** ambos os pontos de cálculo passaram a verificar
`player.is_dead and not player.has_lives_left()`, congelando a
exibição em vez de continuar contando.

**Lição Aprendida:** quando um mesmo dado é calculado em mais de um
lugar do código (lógica de jogo e lógica de exibição), corrigir apenas
um dos pontos deixa o outro com o comportamento antigo — vale
verificar todos os locais que replicam um cálculo, não assumir que uma
única correção cobre todos eles.

---

## Estado Atual da Arquitetura

```
Room
 ├── visit_history: list[dict]  — snapshots imutaveis de visitas concluidas
 └── kills_by_type / points_by_type — resetados a cada nova visita

GameScene
 ├── _pick_enemy_type(room) — chance de "strong" cresce com o tempo
 ├── _spawn_wave_enemies() — escolhe tipo individualmente por inimigo
 └── ao concluir sala: registra entrada em room.visit_history

Enemy.update(dt, target_x, target_y, others, bounds)
 └── respeita os limites da sala, como o Player ja fazia
```

Testado extensivamente: histórico de múltiplas visitas exibido
corretamente por sala, com quebra por tipo; inimigos fortes aparecendo
misturados aos fracos conforme o tempo avança dentro da sala; nenhum
inimigo mais atravessando paredes.

---

## O que o aluno aprendeu

Como distinguir entre estado corrente mutável e snapshots imutáveis de
histórico, evitando que resets futuros corrompam dados já registrados.
Como migrar de atribuição em lote para escolha individual permite
comportamento emergente (composições mistas) sem cálculo manual de
proporções. Como bugs de longa data podem permanecer invisíveis até
que mudanças em partes aparentemente não relacionadas do sistema
(tamanho de sala, duração de vida dos inimigos) os tornem perceptíveis.

---

## Próxima Sprint

Sprint 026 — drops físicos coletáveis (gemas visuais) e power-up de
ímã, conforme planejado na pesquisa de referência de gênero, agora com
uma lista ampliada de armas e power-ups registrada no `VISAO.md`
(Fang, armas de fogo com munição, padrões de tiro múltiplo, sabre
giratório, escudo) para guiar decisões futuras de upgrade.

---

## Resumo Executivo

Esta Sprint adiciona histórico detalhado por visita a cada sala
(preservando estatísticas de sessões anteriores como snapshots
imutáveis), introduz composição evolutiva de tipos de inimigo (chance
de inimigos fortes crescendo com o tempo de permanência na sala), e
corrige um bug de longa data onde inimigos atravessavam paredes —
latente desde a fundação do projeto, mas só exposto pela combinação de
salas grandes e piso contínuo de inimigos vivos por mais tempo.
