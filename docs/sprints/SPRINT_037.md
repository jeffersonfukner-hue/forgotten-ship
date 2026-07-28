# SPRINT_037.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 037
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Eixos do Tiro Base

---

## Objetivo da Sprint

Completar os 4 eixos de upgrade do Tiro base planejados desde o
`VISAO.md` original, mas nunca implementados: Velocidade do projétil,
Penetração, Rajada (Burst) e Alcance como power-up passivo.

---

## Situação Inicial

Ao final da Sprint 036, o Tiro base tinha apenas 1 eixo real (Poder,
via `UPGRADE_DAMAGE_INCREMENT`) mais o Tiro Múltiplo (variantes
espaciais). `Projectile` já tinha `pierce` como parâmetro desde
Sprints anteriores, mas `speed` estava hardcoded em `400` dentro do
`__init__`, e `PLAYER_RANGE_RADIUS` era uma constante fixa nunca
conectada ao sistema de power-ups passivos.

---

## Problema

Rajada era estruturalmente diferente dos demais eixos: não é "um valor
que aumenta" (como velocidade ou alcance), é uma **repetição temporal**
de disparos — múltiplos ciclos de tiro em sequência rápida, sem
re-mirar entre eles (mirar de novo a cada tiro da rajada tornaria a
mecânica instável, já que o alvo poderia mudar no meio da rajada).

---

## Decisão Arquitetural

### Velocidade e Penetração como Parâmetros Existentes do Projectile

`Projectile.speed` (antes hardcoded) e `Projectile.pierce` (já era
parâmetro) passaram a ser alimentados por `get_passive_value("tiro_velocidade")`
e `get_passive_value("tiro_penetracao")` no momento da criação, via
`_create_projectiles()` — um método novo que centraliza a criação de
projéteis, usado tanto pelo tiro direto quanto pela rajada.

### Alcance Recalculado a Cada Frame, Não Mais Constante

`self.player.range_radius`, que antes era atribuído uma única vez no
`__init__`, passou a ser recalculado todo frame em `update()` a partir
do nível atual do power-up `"range"` — o mesmo padrão de "valor
calculado sob demanda" já usado desde o ímã na Sprint 028, aplicado
agora a um atributo que até então era estático.

### Rajada como Fila de Disparos Pendentes, Não Novo Ciclo de Mira

Ao disparar (seja o tiro reto, seja qualquer variante do Múltiplo), a
lista de "vetores de disparo" já calculada é guardada como cópias
repetidas em `pending_burst_shots` — uma fila que o `update()` da
`GameScene` consome a cada `BURST_SHOT_DELAY` segundos, sem nunca
recalcular direção ou re-mirar. O cooldown normal do tiro
(`confirm_shot()`) só é aplicado depois que a última repetição da
rajada é consumida — ou seja, uma rajada de 4 tiros ocupa o tempo de
"4 disparos rápidos" antes do intervalo normal entre ciclos de tiro
recomeçar a contar.

### Todos os 4 Eixos Não Ocupam Slot

Por serem parte do Tiro base (mesma lógica já aplicada ao Tiro
Múltiplo na Sprint anterior), `tiro_velocidade`, `tiro_penetracao`,
`tiro_rajada` e `range` foram todos adicionados a `FREE_CATEGORIES` —
nenhum consome um dos slots limitados de armas/passivos equipados.

---

## Conceitos de Python

- **Parâmetro com Valor Padrão Preservando Comportamento Anterior** —
  `speed: float = 400` no `Projectile` mantém o valor antigo como
  padrão, então qualquer código que ainda não passe `speed`
  explicitamente continua funcionando exatamente como antes.
- **Lista Usada como Fila via `list.pop(0)`** — `pending_burst_shots.pop(0)`
  consome o próximo item pendente na ordem em que foi inserido (FIFO),
  técnica simples o suficiente para o volume pequeno de disparos por
  rajada (no máximo 6, no teto do eixo).
- **Multiplicação de Lista para Repetir um Valor N Vezes** — `[shots] * repeats`
  cria `repeats` referências à mesma lista `shots`, uma forma direta de
  preparar N repetições idênticas sem laço explícito.

---

## Conceitos de Arquitetura

- **Centralizar a Criação de Projétil em um Método Único** — antes desta
  Sprint, a criação de `Projectile` estava duplicada em dois lugares
  (tiro normal e o ramo de Quadrantes). `_create_projectiles()` unifica
  isso, garantindo que velocidade e penetração sejam aplicadas de forma
  consistente não importa qual caminho de disparo estiver ativo.
- **Repetição Temporal vs. Repetição Espacial** — Rajada (múltiplos
  disparos em sequência, no tempo) e Múltiplo (vários projéteis
  simultâneos, no espaço) são conceitos ortogonais que precisaram
  compor juntos: a rajada repete a *mesma* lista de vetores de disparo
  (que pode já ter vários projéteis simultâneos, se Diagonal/Paralelo/
  Quadrantes estiver ativo), em vez de tratar os dois como mutuamente
  exclusivos.
- **Fila de Estado Pendente para Ações que se Estendem por Múltiplos
  Frames** — como uma rajada não pode ser resolvida num único frame
  (precisa de um pequeno delay entre cada tiro), o estado precisou
  "esperar" entre frames — resolvido com uma fila simples no `Player`,
  consumida pela `GameScene` a cada frame até esvaziar.

---

## Implementações

### Missão 1 — Velocidade e Penetração

**Arquivos:** `projectile.py`, `settings.py`, `game_scene.py`

`Projectile.__init__` ganhou o parâmetro `speed`. Adicionados
`tiro_velocidade` e `tiro_penetracao` em `PASSIVE_POWERUPS`. Criado
`_create_projectiles()` na `GameScene`, aplicando os dois valores a
partir do nível atual do jogador.

### Missão 2 — Alcance como Passivo

**Arquivos:** `settings.py`, `player.py`

Adicionado `range` em `PASSIVE_POWERUPS` (valor base igual à antiga
constante, sem regressão). `Player.update()` passou a recalcular
`self.range_radius` a cada frame via `get_passive_value("range")`.

### Missão 3 — Rajada

**Arquivos:** `settings.py`, `player.py`, `game_scene.py`

Adicionado `tiro_rajada` em `PASSIVE_POWERUPS` e `BURST_SHOT_DELAY`
em `settings.py`. Criados `pending_burst_shots`, `burst_timer`,
`queue_burst()`, `has_pending_burst()`, `pop_burst_shots()` no
`Player`. O bloco de disparo da `GameScene` foi reestruturado para
checar rajada pendente antes de iniciar um novo ciclo de mira,
consumindo a fila a cada `BURST_SHOT_DELAY` segundos.

---

## Bugs Encontrados

Nenhum bug registrado nesta Sprint — os 4 eixos foram testados
individualmente e em conjunto (rajada funcionando corretamente com
Quadrantes e com as variantes de Múltiplo ativas) sem comportamento
inesperado.

---

## Refinamento Identificado Durante a Sprint

### Campo de Força Ainda Não Implementado

Ao revisar a Lista Consolidada de Power-ups do `VISAO.md` para
confirmar se restava algum item pendente, foi identificado que o
**Campo de Força** (item #2 da lista original, dano em área contínuo)
nunca foi implementado — havia sido registrado apenas as armas de fogo
como pendência no `CONTEXTO_PROJETO.md`, deixando o Campo de Força fora
por engano. Corrigido no fechamento desta Sprint.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ tiro_velocidade, tiro_penetracao, tiro_rajada, range)
 ├── FREE_CATEGORIES (+ os 4 novos eixos)
 └── BURST_SHOT_DELAY

Projectile
 └── __init__(..., speed=400) — velocidade agora parametrizavel, sem regressao

Player
 ├── range_radius — recalculado a cada frame via get_passive_value("range")
 ├── pending_burst_shots / burst_timer
 └── queue_burst() / has_pending_burst() / pop_burst_shots()

GameScene
 ├── _create_projectiles(shots) — centraliza criacao, aplica velocidade e penetracao
 └── update() — bifurca: consome rajada pendente OU inicia novo ciclo de disparo
```

Testado extensivamente: Velocidade aumentando visivelmente a rapidez
dos projéteis por nível; Penetração atravessando mais inimigos antes
de desaparecer; Rajada disparando 2 a 6 tiros em sequência rápida,
mesma direção, cooldown completo só após a última repetição; Alcance
expandindo o círculo de percepção em tempo real; Rajada testada em
conjunto com Quadrantes e variantes de Múltiplo, repetindo corretamente
o padrão completo de tiros a cada repetição, não apenas um projétil.

---

## O que o aluno aprendeu

Como transformar um valor hardcoded em parâmetro configurável sem
quebrar quem já chamava o código, usando valor padrão. Como distinguir
repetição temporal (rajada) de repetição espacial (múltiplos tiros
simultâneos) e fazer as duas composição juntas. Como usar uma fila
simples (lista com `pop(0)`) para representar uma ação que se estende
por múltiplos frames, quando o estado não pode ser resolvido de uma
vez só. Como recalcular um atributo a cada frame a partir de um nível
de progressão, em vez de fixá-lo uma única vez na criação do objeto.

---

## Próxima Sprint

Campo de Força — item pendente identificado nesta Sprint, encerrando
de vez a Lista Consolidada original de Power-ups (restando só as armas
de fogo depois dele).

Também registrado para próxima Sprint dedicada de UI: tempo de jogo
(hh:mm:ss) e número total de salas limpas, exibidos permanentemente na
tela.

---

## Resumo Executivo

Esta Sprint completa os 4 eixos pendentes do Tiro base (velocidade,
penetração, rajada, alcance), todos sem ocupar slot de power-up. Rajada
foi o item mais complexo, exigindo uma fila de disparos pendentes
consumida ao longo de múltiplos frames, testada com sucesso em
combinação com Quadrantes e as variantes de Tiro Múltiplo. Durante a
revisão da Lista Consolidada, identificou-se que o Campo de Força
nunca havia sido implementado — corrigido o registro de pendências, que
antes só mencionava as armas de fogo.
