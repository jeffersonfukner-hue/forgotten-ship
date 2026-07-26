# SPRINT_027.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 027
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Obstáculos — Fixos e Destrutíveis

---

## Objetivo da Sprint

Implementar o primeiro Bloco Temático planejado (`VISAO.md`, Plano
Consolidado): obstáculos dentro das salas, até então inexistentes — o
piso era completamente vazio. Dois tipos coexistindo: fixos
(indestrutíveis, bloqueiam movimento e linha de tiro) e destrutíveis
(corroídos apenas por inimigos, funcionando como defesa temporária do
jogador, não como alvo de ataque).

---

## Situação Inicial

Ao final da Sprint 026, as salas do jogo eram espaços completamente
vazios, sem nenhum elemento físico além de paredes, portas e piso —
limitando o espaço tático do combate a "correr e atirar", sem
cobertura ou variação de terreno.

---

## Problema

Um espaço de combate sem obstáculos carece de profundidade tática, e
também tornaria os power-ups futuros (especialmente padrões de tiro e
comportamentos de perseguição de inimigos) menos interessantes, por
não haver nada com que interagir além do próprio jogador e inimigos.

---

## Decisão Arquitetural

### Um Único Tipo `Obstacle`, Configurável por Parâmetro

Seguindo o mesmo padrão já usado para `Enemy` (Sprint 022), foi criada
uma única classe `Obstacle` com um parâmetro `destructible`, em vez de
subclasses separadas — a diferença entre os dois tipos está inteira em
dados (cor, presença de HP), não em comportamento fundamentalmente
distinto o suficiente para justificar herança.

### Obstáculo Destrutível como Defesa, não como Alvo do Jogador

Uma reformulação de conceito ocorreu durante o desenvolvimento: a
primeira implementação permitia ao jogador destruir obstáculos com
tiros para obter recompensa. Essa decisão foi revertida — obstáculos
destrutíveis passaram a ser corroídos **apenas por inimigos**, agindo
como uma barreira temporária que protege o jogador, mas que se
deteriora sob ataque constante. O tiro do jogador continua sendo
bloqueado por qualquer obstáculo (fixo ou destrutível), sem causar
dano a ele.

### Feedback Visual por Encolhimento, não por Barra de HP

Por decisão explícita, o obstáculo destrutível não exibe uma barra de
vida — em vez disso, encolhe fisicamente conforme perde HP, até
desaparecer. Essa escolha foi registrada como preferência geral de
design para revisão futura de outros elementos do jogo (Bloco de
Refinamento).

### Posicionamento: Manual para Fixos, Aleatório para Destrutíveis

Obstáculos fixos são posicionados manualmente por sala
(`obstacle_data`, no mesmo padrão de `door_data`), dando controle
total de design sobre cobertura tática. Obstáculos destrutíveis nascem
em posições aleatórias, evitando sobreposição com obstáculos fixos e
com a área central da sala (onde o jogador tipicamente aparece).

### Mira Automática Respeita Linha de Visão

A mira automática do jogador passou a considerar se existe um
obstáculo bloqueando a linha reta até cada inimigo candidato — usando
`pygame.Rect.clipline()` para detectar interseção — evitando que o
jogador "enxergue através de paredes" e desperdice tiros contra
obstáculos ao tentar atingir um inimigo escondido atrás deles.

---

## Conceitos de Python

- **Configuração por Parâmetro Booleano (`destructible`)** — a mesma
  técnica já usada em `Enemy` (tipo via string-chave) aparece aqui em
  forma mais simples: um único booleano decide o conjunto de atributos
  ativados no `__init__`.
- **`pygame.Rect.clipline()` para Interseção Linha-Retângulo** — um
  método nativo do pygame que verifica se um segmento de linha cruza
  um retângulo, evitando implementar geometria de interseção
  manualmente.
- **`pygame.Rect.inflate()` para Área de Detecção Ampliada** — usado
  para criar uma "zona de ataque" maior que o obstáculo real,
  contornando uma limitação identificada em teste (ver Bugs).

---

## Conceitos de Arquitetura

- **Reversão Consciente de Decisão de Design** — a mudança de "jogador
  destrói obstáculos por recompensa" para "obstáculos protegem o
  jogador, corroídos por inimigos" ilustra que decisões tomadas no
  calor da implementação podem (e devem) ser revisadas quando uma
  ideia melhor surge — o código já escrito para a primeira versão foi
  descartado sem hesitação em favor do conceito mais interessante.
- **Sistemas que Interagem de Forma Não Óbvia** — o sistema "não
  atravessar obstáculo" (bloqueio de movimento) interferiu
  silenciosamente com o sistema "detectar contato para causar dano"
  (corrosão), porque o primeiro impede exatamente a condição
  (sobreposição de retângulos) que o segundo verifica. Isso ilustra
  como duas funcionalidades aparentemente independentes podem se
  cancelar mutuamente de forma sutil.
- **Formalização do Padrão de Triagem por Prefixo** — a convenção
  "Refinamento:" foi generalizada para qualquer prefixo seguido de
  dois-pontos, reconhecendo que o padrão de "classificar antes de
  implementar" é mais amplo do que um único caso de uso.

---

## Implementações

### Missão 1 — Entidade Obstacle

**Arquivo:** `obstacle.py` (novo)

Criada a classe `Obstacle`, com o parâmetro `destructible` controlando
HP, cor, e comportamento de encolhimento.

### Missão 2 — Obstáculos Fixos por Sala

**Arquivos:** `game_scene.py`, `room.py`

Adicionado `obstacle_data` (posicionamento manual), com `Room`
armazenando e desenhando a lista de obstáculos.

### Missão 3 — Colisão com Jogador, Inimigo e Projétil

**Arquivos:** `player.py`, `enemy.py`, `game_scene.py`

Ambas as entidades móveis passaram a reverter posição por eixo ao
colidir com um obstáculo (permitindo "deslizar" ao longo dele em vez
de travar). Projéteis são bloqueados por qualquer obstáculo,
independente do tipo.

### Missão 4 — Obstáculos Destrutíveis Aleatórios

**Arquivo:** `game_scene.py`

Adicionado `_spawn_destructible_obstacles()`, gerando uma quantidade
configurável por sala, evitando sobreposição com obstáculos fixos e
com a área central da sala.

### Missão 5 — Corrosão por Inimigo, Encolhimento Visual

**Arquivos:** `obstacle.py`, `game_scene.py`

`Obstacle.take_damage()` e `update()` implementam a corrosão (com
cooldown) e o encolhimento proporcional ao HP restante. A checagem de
contato inimigo-obstáculo foi adicionada ao loop de atualização de
inimigos.

### Missão 6 — Linha de Visão na Mira Automática

**Arquivo:** `game_scene.py`

Adicionado `_has_line_of_sight()`, usado por `find_closest_enemy()`
para descartar inimigos bloqueados por obstáculo.

### Missão 7 — Reorganização de `settings.py`

**Arquivo:** `settings.py`

Separadas as constantes de "Player: combate" das de "Player:
progressão" e "Gemas", em seções próprias — corrigindo uma mistura de
temas identificada durante revisão solicitada pelo desenvolvedor.

---

## Bugs Encontrados

### Bug 1 — Jogador Preso Dentro de Obstáculo Após Knockback

**Sintoma:** ao ser empurrado por um inimigo (knockback), o jogador
podia ficar fisicamente preso dentro ou muito próximo de um obstáculo
fixo, incapaz de se mover.

**Causa:** `apply_knockback()` respeitava os limites da sala, mas
nunca verificava colisão com obstáculos — permitindo que o empurrão
posicionasse o jogador sobrepondo um obstáculo, situação da qual a
lógica normal de movimento (que reverte para a posição anterior ao
colidir) não conseguia se recuperar, pois a "posição anterior" já
estava dentro do obstáculo.

**Solução:** `apply_knockback()` passou a aplicar a mesma lógica de
reversão por eixo já usada em `update_walking()`.

**Lição Aprendida:** toda forma de alterar a posição de uma entidade
(não apenas o movimento "normal" controlado pelo jogador) precisa
respeitar as mesmas restrições de colisão — um padrão que já havia
aparecido antes com limites de sala (Sprint 006) e se repete agora com
obstáculos.

### Bug 2 — Corrosão de Obstáculo Nunca Disparava

**Sintoma:** inimigos visivelmente parados encostados em um obstáculo
destrutível, sem nunca causar dano a ele, mesmo com prints de debug
confirmando que a verificação estava sendo executada a cada frame.

**Causa:** o próprio sistema de bloqueio de movimento (que impede o
inimigo de atravessar o obstáculo) reverte a posição do inimigo assim
que detecta sobreposição — na prática, isso impede que os retângulos
de inimigo e obstáculo alguma vez fiquem realmente sobrepostos o
suficiente para `colliderect()` retornar `True`, mesmo com o inimigo
visualmente "encostado".

**Investigação:** confirmada por depuração incremental — prints
temporários mostraram `colliding=False` de forma consistente, mesmo
com confirmação visual direta de que o inimigo estava parado contra o
obstáculo.

**Solução:** a checagem de corrosão passou a usar uma versão "inflada"
do retângulo do obstáculo (`Rect.inflate()`), criando uma margem de
detecção maior que a área de bloqueio físico real.

**Lição Aprendida:** dois sistemas que parecem independentes (bloqueio
de movimento e detecção de contato para dano) podem se cancelar
mutuamente de forma não óbvia quando ambos dependem da mesma condição
geométrica (sobreposição de retângulos) — a solução exigiu desacoplar
a área usada para cada finalidade.

---

## Estado Atual da Arquitetura

```
Obstacle (Entity)
 ├── destructible: bool
 ├── hp / max_hp (so relevante se destructible)
 ├── damage_cooldown
 ├── take_damage(amount) — so afeta destrutiveis
 └── update(dt) — decrementa cooldown, encolhe conforme hp restante

Room
 ├── obstacles: list[Obstacle]
 └── add_obstacle() / get_obstacles()

GameScene
 ├── obstacle_data — posicionamento manual de fixos, por sala
 ├── _spawn_destructible_obstacles(room) — geracao aleatoria, evita sobreposicao
 ├── _has_line_of_sight(start, end) — usa Rect.clipline()
 └── update():
      ├── projetil bloqueado por qualquer obstaculo (sem causar dano)
      ├── inimigo corroi obstaculo destrutivel (area inflada de deteccao)
      ├── jogador/inimigo bloqueados por obstaculo, revertendo por eixo
      └── mira automatica ignora inimigos sem linha de visao livre
```

Testado extensivamente: obstáculos fixos bloqueando todos os tipos de
movimento e projéteis; destrutíveis corroídos apenas por inimigos,
encolhendo até sumir; jogador não mais preso após knockback próximo a
obstáculo; mira automática corretamente "cega" para inimigos atrás de
obstáculos.

---

## O que o aluno aprendeu

Como reverter uma decisão de design no meio da implementação sem
hesitação, quando uma ideia mais interessante surge durante o
desenvolvimento. Como dois sistemas aparentemente independentes podem
interferir um no outro de forma sutil, quando compartilham a mesma
condição de verificação geométrica. Como usar métodos nativos do
pygame (`clipline`, `inflate`) para resolver problemas de geometria
sem implementar cálculos manuais. Como formalizar um padrão de
comunicação (o prefixo `Palavra:` para triagem) observado repetidas
vezes ao longo do desenvolvimento.

---

## Próxima Sprint

Bloco de Power-ups — início pelo Ímã, conforme planejado no `VISAO.md`.

---

## Resumo Executivo

Esta Sprint implementa o primeiro Bloco Temático planejado: obstáculos
de sala, fixos e destrutíveis. Uma reformulação de conceito ocorreu
durante o desenvolvimento — obstáculos destrutíveis passaram a
funcionar como defesa temporária corroída por inimigos, não como alvo
de destruição pelo jogador. Dois bugs foram identificados e corrigidos
através de teste cuidadoso: knockback sem verificação de colisão com
obstáculos, e uma interferência sutil entre o sistema de bloqueio de
movimento e a detecção de contato para corrosão. O padrão de
comunicação "Palavra:" foi formalizado como sinal geral de triagem na
metodologia do projeto.
