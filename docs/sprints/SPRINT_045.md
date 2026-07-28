# SPRINT_045.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 045
**Status:** Concluída
**Versão da Arquitetura:** Reabastecimento Gradual + Dificuldade Escalável por Reentrada

---

## Objetivo da Sprint

Substituir o reabastecimento instantâneo de inimigos (reposição 1:1 a
cada morte, sem respiro real) por um reabastecimento gradual com
gatilho de 20% de baixa populacional, e conectar
`HORDE_ENEMIES_PER_VISIT` (já existente, nunca usado) para que o piso
de inimigos cresça a cada reentrada — tornando cada revisita de sala
mais difícil que a anterior.

---

## Situação Inicial

Ao final da Sprint 044, `spawn_horde()` sempre usava
`HORDE_BASE_ENEMIES` fixo (12), independente de quantas vezes a sala já
havia sido vencida. O reabastecimento no `update()` repunha inimigos
assim que `missing > 0` — na prática, assim que um único inimigo
morria, um novo já nascia no mesmo frame, sem nenhuma folga real na
pressão de combate.

---

## Problema

O criador do jogo observou que o reabastecimento instantâneo tornava o
combate uma reposição constante sem alívio perceptível — e queria
diferenciar dois conceitos: reposição **gradual** (o padrão normal do
jogo, um inimigo de cada vez, com pequeno intervalo) vs. reposição **em
massa** (reservada para uma futura mecânica de dificuldade, "swarm" —
todos de uma leva chegando simultaneamente, usada só em ocasiões
específicas como as ondas de chefes).

---

## Decisão Arquitetural

### Gatilho de 20% Antes de Iniciar o Reabastecimento

Em vez de repor assim que `missing > 0`, o reabastecimento só começa
quando a quantidade de inimigos faltantes atinge
`HORDE_REINFORCEMENT_TRIGGER_RATIO` (20%) do piso total da sala — dando
uma janela real de respiro antes da pressão retomar.

### Reposição Individual com Intervalo, Não em Massa

Uma vez atingido o gatilho, `_spawn_wave_enemies()` é chamado com
quantidade `1` por vez, com `HORDE_REINFORCEMENT_INTERVAL` (1 segundo)
de intervalo entre cada reposição — reforçando visualmente a diferença
entre "reforço gradual" (o padrão) e "chegada em massa" (reservado para
o futuro modo swarm, explicitamente não implementado agora).

### Piso de Inimigos Escala com `room.times_cleared`

`spawn_horde()` agora calcula
`HORDE_BASE_ENEMIES + HORDE_ENEMIES_PER_VISIT * room.times_cleared` —
a primeira visita usa o piso base; cada reentrada soma mais
`HORDE_ENEMIES_PER_VISIT` (6) ao piso, tornando a horda maior a cada
revisita. Como o gatilho de reabastecimento é uma fração do piso, ele
cresce proporcionalmente junto.

### Tempo por Onda Deliberadamente Fora de Escopo

Por decisão do criador do jogo, `ROOM_SURVIVAL_DURATION` não foi
alterado nesta Sprint — a ideia de tempos diferentes por onda foi
registrada para quando a estrutura de ondas com mini-chefes/chefes/
swarms (Bloco de Entidades de Chefes) for implementada, já que só faz
sentido nesse contexto mais amplo.

---

## Conceitos de Python

- **`round()` com `max(1, ...)` para Garantir um Gatilho Mínimo
  Sensato** — `trigger_count = max(1, round(total * ratio))` evita que
  o gatilho vire zero em pisos muito pequenos (ex: piso de 2, 20%
  arredondaria pra 0), garantindo que sempre haja pelo menos 1 inimigo
  de folga antes do gatilho disparar.
- **Cronômetro Decrescente Controlando Cadência de Eventos Discretos**
  — `reinforcement_timer`, decrementado a cada frame e resetado após
  cada reposição, é o mesmo padrão já usado em cooldowns de armas
  (Sifão, Phaser, etc.), aplicado agora ao ritmo de spawn de inimigos.

---

## Conceitos de Arquitetura

- **Distinguir "Reposição Gradual" de "Chegada em Massa" como Conceitos
  de Design Distintos, Não Só de Implementação** — a mudança não foi
  apenas técnica (adicionar um cronômetro); ela nomeia e separa dois
  comportamentos que antes eram indistinguíveis no código, preparando
  terreno para o futuro modo swarm ser uma escolha deliberada de
  dificuldade, não uma variação acidental do reabastecimento normal.
- **Adiar Escopo Relacionado que Só Faz Sentido num Contexto Maior** —
  tempo por onda foi conscientemente deixado de fora, reconhecendo que
  implementá-lo isoladamente agora exigiria retrabalho quando a
  estrutura completa de ondas (chefes, swarms) chegasse.

---

## Implementações

### Missão 1 — Reabastecimento Gradual com Gatilho de 20%

**Arquivos:** `settings.py`, `game_scene.py`

Adicionadas `HORDE_REINFORCEMENT_TRIGGER_RATIO` e
`HORDE_REINFORCEMENT_INTERVAL`. Criado `reinforcement_timer` na
`GameScene`, zerado a cada nova horda. Bloco de reabastecimento no
`update()` reescrito para checar o gatilho de 20% e repor 1 inimigo por
vez, respeitando o intervalo.

### Missão 2 — Piso Crescente por Reentrada

**Arquivo:** `game_scene.py`

`spawn_horde()` revisado para calcular o piso a partir de
`room.times_cleared`, conectando `HORDE_ENEMIES_PER_VISIT` pela
primeira vez desde que a constante foi criada.

### Correção — Inimigos Nascendo Presos em Obstáculos

**Arquivo:** `game_scene.py`

Identificado durante o teste desta Sprint: `_spawn_wave_enemies()`
nunca verificava colisão com obstáculos (fixos ou destrutíveis) ao
sortear posição, diferente de `_spawn_destructible_obstacles()`, que já
fazia essa checagem. Um inimigo podia nascer preso dentro de um
obstáculo fixo, incapaz de se mover — só alcançável pelo Campo de
Força (que ignora posição física). Corrigido adicionando checagem de
`colliderect()` contra todos os obstáculos da sala, usando o tamanho do
maior tipo de inimigo (`strong`, 18×18) como margem de segurança
independente do tipo sorteado.

---

## Bugs Encontrados

### Bug — Inimigos Nascendo Presos Dentro de Obstáculos Fixos

**Sintoma:** alguns inimigos nasciam sobrepostos a um obstáculo fixo e
ficavam fisicamente presos ali, impossíveis de eliminar exceto com
Campo de Força — em salas sem essa arma, o jogador ficava preso sem
poder limpar a sala.

**Causa:** `_spawn_wave_enemies()` checava apenas distância de portas
ao sortear posição, nunca colisão com obstáculos.

**Solução:** adicionada checagem de `colliderect()` contra
`room.get_obstacles()` na mesma lógica de tentativas já existente.

**Lição Aprendida:** duas funções que sorteiam posição na mesma sala
(`_spawn_wave_enemies` e `_spawn_destructible_obstacles`) tinham
critérios de validação diferentes — uma verificava obstáculos, a outra
não. Vale revisar funções irmãs que fazem tarefas parecidas para
garantir que compartilhem as mesmas checagens de segurança básicas.

---

## Refinamentos Registrados para Sprint Futura

### Redesenho do Sabre Giratório: Lâmina em Vez de Bola

Ideia registrada pelo criador do jogo: o Sabre hoje é desenhado como um
círculo; a proposta é uma lâmina fina (2px de largura), curta como uma
adaga no início, com um **novo eixo de upgrade** (`sabre_tamanho` ou
equivalente) aumentando o comprimento — e, por consequência, o raio de
ataque. Implica também revisar a colisão (hoje `colliderect` simples),
provavelmente para um retângulo fino e comprido rotacionado junto com o
ângulo de giro. Não implementado nesta Sprint — fica registrado no
Bloco de Power-ups / Refinamentos Visuais.

### Estrutura de Ondas com Swarms e Chefes (Detalhamento Registrado)

Estrutura detalhada pelo criador do jogo para o futuro Bloco de
Entidades de Chefes: Onda 1 (normal, 1 swarm central + 1 mini-chefe),
Onda 2 (normal, 2 swarms divididos + 1 mini-chefe central + 1 chefe),
Onda 3/final (normal, 3 swarms + 2 mini-chefes + 1 chefe + o chefão) —
cada onda com tempo próprio diferente, e um contador grande de
countdown até o chefão, visível na tela. "Swarm" definido como chegada
de toda uma leva de inimigos simultaneamente (diferente do
reabastecimento gradual desta Sprint, que é sempre 1 por vez).

---

## Estado Atual da Arquitetura

```
settings.py
 ├── HORDE_REINFORCEMENT_TRIGGER_RATIO (0.2)
 └── HORDE_REINFORCEMENT_INTERVAL (1.0s)

GameScene
 ├── reinforcement_timer — cronometro entre reposicoes individuais
 ├── spawn_horde() — piso = BASE + PER_VISIT * room.times_cleared
 ├── update() — gatilho de 20%, reposicao de 1 por vez
 └── _spawn_wave_enemies() — agora tambem evita colisao com obstaculos
```

Testado extensivamente: reabastecimento só inicia após ~20% do piso
morrer, repondo visivelmente 1 de cada vez com ~1s de intervalo; sala
revisitada nascendo com piso maior que a visita anterior; nenhum
inimigo nascendo mais preso em obstáculo, mesmo nas 3 salas (todas já
com obstáculos fixos desde a Sprint 044).

---

## O que o aluno aprendeu

Como diferenciar dois comportamentos de spawn conceitualmente distintos
(reposição gradual vs. chegada em massa) através de um gatilho de
proporção e um cronômetro, preparando terreno para uma futura mecânica
de dificuldade sem misturar os dois agora. Como conectar uma constante
que existia mas nunca foi usada, revisando o cálculo que a torna
efetiva. Como revisar funções irmãs que fazem tarefas parecidas (duas
funções de sorteio de posição) para garantir que compartilhem os
mesmos critérios básicos de segurança, evitando um bug que só aparece
quando as duas divergem silenciosamente.

---

## Próxima Sprint

Bloco de Entidades de Chefes — estrutura de ondas com swarms,
mini-chefes, chefe e chefão, já detalhada pelo criador do jogo nesta
Sprint, incluindo tempo por onda e contador de countdown.

Registrado para mais adiante: redesenho do Sabre Giratório (lâmina +
eixo de tamanho/alcance).

---

## Resumo Executivo

Esta Sprint substitui o reabastecimento instantâneo de inimigos por um
sistema gradual (gatilho de 20% de baixa populacional, reposição de 1
por vez com intervalo), e conecta pela primeira vez
`HORDE_ENEMIES_PER_VISIT`, fazendo o piso de inimigos crescer a cada
reentrada de sala. Durante o teste, foi identificado e corrigido um bug
real: inimigos nascendo presos dentro de obstáculos fixos, por falta de
checagem de colisão em `_spawn_wave_enemies()` — corrigido replicando a
mesma validação já usada na função irmã de spawn de obstáculos. Duas
ideias foram registradas para o futuro: redesenho visual/funcional do
Sabre Giratório, e a estrutura detalhada de ondas com swarms e chefes
para a próxima Sprint.
