# Forgotten Ship
## Sprint 046B

**Projeto:** Forgotten Ship (Jogo 01 da A1 Game Academy)
**Sprint:** 046B — Bloco de Entidades de Chefes, Parte 2/5 (Mini-chefe)
**Data:** 29/07/2026
**Status:** Concluída
**Versão da Arquitetura:** pós-046A (Sistema de Ondas com Acúmulo)

---

## Objetivo da Sprint

Implementar o **Mini-chefe** — o primeiro dos três chefes planejados no
Bloco de Entidades de Chefes (`VISAO.md`, "Estrutura de Boss Rush") —
com seu drop característico (Ímã Super Power) e um sistema de
agendamento de spawn por fração de onda, reutilizável pelos próximos
dois chefes (Chefe e Chefão, Sprints C e D).

---

## Situação Inicial

A Sprint 046A entregou o sistema de ondas com acúmulo
(`Room.current_wave`/`wave_timer`), mas sem nenhum chefe ainda — apenas
inimigos comuns (`weak`/`strong`) reforçando a sala continuamente. A
sala era vencida por um único critério: sobreviver `ROOM_SURVIVAL_DURATION`
(90s), sem nenhuma estrutura de "onda com início e fim proporcional".

---

## Problema

Introduzir um chefe exige decisões que o sistema de inimigo comum não
precisa responder:
- Como o chefe entra na sala (spawn próprio, sem competir com o laço de
  posicionamento pensado para levas de vários inimigos)?
- O que ele dropa ao morrer, e quando esse drop realmente produz efeito?
- Quando, exatamente, ele deve nascer — e como isso se generaliza para
  os próximos dois chefes, que vão seguir o mesmo padrão de "aparecer em
  pontos específicos ao longo das ondas"?

---

## Decisão Arquitetural

### Drop condicional, não automático
Decisão revisada em conversa direta com o usuário: o Mini-chefe **não**
puxa as gemas automaticamente ao morrer. Em vez disso, dropa **1 pickup
único** — o **Ímã Super Power** (`SuperMagnet`) — que o jogador precisa
coletar ativamente. Só a coleta libera os dois efeitos garantidos:
+1 nível em 3 power-ups já equipados, e puxão automático de todas as
gemas da sala. Isso cria uma decisão tática real (correr atrás do ímã
vs. continuar lutando), em vez de um bônus passivo.

### Agendamento de chefes por fração de onda (genérico, não hardcoded)
Em vez de fixar "o Mini-chefe nasce em tal segundo", o sistema
(`settings.BOSS_SPAWN_SCHEDULE`) descreve o spawn como
`(número_da_onda, fração_dentro_da_onda)`. Isso significa que o mesmo
mecanismo (`_update_boss_schedule`) já está pronto para o Chefe e o
Chefão nas Sprints C e D — só exige adicionar a entrada deles no
dicionário, sem nova lógica.

### Duração da sala e proporção de ondas
`ROOM_SURVIVAL_DURATION` passou de 90s para **180s (3 minutos)**, e as
3 ondas passaram a ocupar frações **crescentes** do tempo total —
**20% / 30% / 50%** (`settings.BOSS_WAVE_RATIOS`) — em vez de ondas de
duração fixa e repetida indefinidamente. Isso torna "fim da onda 1",
"meio da onda 2" etc. pontos calculáveis e reaproveitáveis por
qualquer chefe futuro.

### Centralização da morte do inimigo
Antes desta sprint, a criação de `Gem` na morte de um inimigo estava
duplicada em 4 pontos do `game_scene.py` (projétil, sabre, sifão, campo
de força). Centralizado em `_handle_enemy_death()`, que decide entre
gema normal ou `SuperMagnet` a partir da flag `enemy.is_boss` — reduz
4 blocos repetidos para 1, e é o único ponto que precisa saber sobre
chefes.

---

## Conceitos de Python / Arquitetura Ensinados

- **Composição por configuração, não por subclasse:** o Mini-chefe não
  é uma classe nova — é uma entrada em `ENEMY_TYPES` com uma flag
  (`is_boss`) lida pela classe `Enemy` já existente. Mesmo princípio já
  usado em `POWER_UPS`.
- **Eliminação de duplicação via extração de método:** `_handle_enemy_death()`
  como exemplo de identificar lógica repetida entre 4 pontos do código e
  centralizá-la, sem mudar o comportamento observável.
- **Cálculo de agenda a partir de proporções, não de números fixos:**
  `_get_wave_time_bounds()` deriva os limites de cada onda a partir de
  uma lista de proporções (`BOSS_WAVE_RATIOS`) aplicada à duração total —
  o mesmo padrão se generaliza para qualquer redistribuição futura de
  tempo, sem precisar recalcular à mão.
- **Controle de disparo único por conjunto (`set`):** `boss_spawns_triggered`
  e `boss_warnings_triggered` usam `set()` com chaves `(tipo, índice)`
  para garantir que cada ponto do agendamento dispare exatamente uma vez
  por visita, mesmo checado a cada frame.

---

## Implementações (por Missão)

### Missão 1 — Tipo de inimigo `mini_boss` e flag `is_boss`
- `ENEMY_TYPES["mini_boss"]`: 300 HP, cor dourada, `is_boss: True`.
- `Enemy.__init__` passa a ler `config.get("is_boss", False)`.

### Missão 2 — Pickup `SuperMagnet`, recompensa e centralização da morte
- Nova entidade `src/entities/super_magnet.py`: mesmo padrão de
  arrasto/puxão da `Gem`, mas sem semântica de pontos — pickup de
  evento, não de progressão numérica.
- `Player.apply_boss_reward()`: sorteia até 3 eixos já equipados
  (nível > 0) e sobe 1 nível em cada.
- `GameScene._handle_enemy_death()`: centraliza registro de kill e
  decisão de drop (gema normal vs. `SuperMagnet`), substituindo 4
  blocos duplicados.
- Loop de coleta do `SuperMagnet` em `GameScene.update()`: ao ser
  coletado, chama `apply_boss_reward()` e inicia o puxão (`start_pull()`)
  de todas as gemas ainda não puxadas da sala.

### Missão 3 — Spawn do Mini-chefe (1x por visita, na Onda 1)
- `GameScene._spawn_boss()`: método próprio para nascer 1 unidade de
  chefe numa borda da sala, respeitando distância mínima de porta e
  obstáculo — separado de `_spawn_wave_enemies()` porque o chefe não é
  uma leva, é uma unidade só.
- Validado manualmente com uma tecla de debug temporária (`K_b`),
  removida após confirmação.

### Missão 4 — Agendamento por fração de onda + sala de 3 minutos
- `ROOM_SURVIVAL_DURATION`: 90s → 180s.
- `settings.BOSS_WAVE_RATIOS = [0.20, 0.30, 0.50]`.
- `settings.BOSS_SPAWN_SCHEDULE["mini_boss"] = [(1, 1.0), (2, 0.5), (3, 1/3)]`
  — fim da Onda 1, meio da Onda 2, 1/3 da Onda 3. Entradas comentadas
  para `chefe` (Sprint C) e `chefao` (Sprint D), já no formato correto.
- `Room.boss_spawns_triggered`: controle de disparo único por visita.
- `GameScene._get_wave_time_bounds()` e `_update_boss_schedule()`:
  calculam os limites de cada onda e disparam o spawn no momento certo.

### Refinamentos (dentro da sprint, a pedido do usuário)

**Aviso visual de chefe se aproximando**
- Banner central 4s antes do spawn agendado (`BOSS_WARNING_LEAD_TIME`),
  visível por 3s (`BOSS_WARNING_DURATION`), sem pausar o jogo.
- Ajuste solicitado pelo usuário: retângulo vermelho pisca-pisca ao
  redor do texto, com fase calculada a partir do `time_left` restante
  (nunca dessincroniza, pois não depende de um cronômetro próprio).
- `Room.boss_warnings_triggered`: controle separado do spawn real, já
  que aviso e spawn cruzam limiares de tempo diferentes.

**Texto flutuante verde na regeneração de vida**
- Bug de UX identificado pelo usuário: `Player.update_regen()` já
  curava HP, mas nunca comunicava isso à `GameScene` (única responsável
  por desenhar `FloatingText`).
- Solução: `Player.pending_regen_heal` guarda a cura do frame; a
  `GameScene` lê, desenha o texto verde, e zera a variável — sem o
  `Player` precisar conhecer `FloatingText` diretamente.

---

## Desvio de Processo e Correção de Metodologia

**Sintoma:** o usuário escreveu um pedido prefixado com `Refinamento:`
(sobre o texto de regeneração), que pela `METODOLOGIA.md` deveria ser
apenas **registrado** para polimento posterior — não implementado na
hora. A IA implementou diretamente, sem sinalizar necessidade real
antes de agir.

**Causa raiz:** a `METODOLOGIA.md` (Seção 3) ainda apontava
`Refinamento:` para o "Bloco de Refinamento do VISAO.md" — um lugar que
deixou de existir na reestruturação v6.0 do `VISAO.md` (sessão
anterior a este chat), quando todo conteúdo operacional de pendências
migrou para o `CONTEXTO_PROJETO.md`. Essa mudança de papel/estrutura
não foi propagada de volta para a `METODOLOGIA.md`, e o Gatilho de
Revisão de Documentos (Seção 8) não previa checagem cruzada ativa entre
os 3 documentos principais quando um deles muda de papel — só previa
reagir a contradições percebidas por acaso.

**Solução (aplicada ainda dentro desta sprint, por decisão do
usuário — "nunca deixar para amanhã o que se pode resolver hoje"):**
1. Seção 3 corrigida: `Refinamento:` agora aponta para "Bugs e
   Refinamentos Pendentes" do `CONTEXTO_PROJETO.md`.
2. Seção 8 reforçada: mudança de **papel/estrutura** de um dos 3
   documentos principais agora exige checagem cruzada ativa nos outros
   dois antes de considerar a correção completa — não basta corrigir só
   o documento que mudou.
3. O item de regeneração já implementado foi mantido como está (decisão
   explícita do usuário: não desfazer, só registrar o aprendizado).

**Lição aprendida:** duplicidade entre documentos não é o único risco de
desatualização — referências cruzadas (documento A cita "onde X vive" em
documento B) também apodrecem quando B muda de estrutura, mesmo que A
nunca tenha sido editado diretamente.

---

## Estado Atual da Arquitetura

- Chefes são inimigos comuns (`Enemy`) com uma flag (`is_boss`) — não
  uma hierarquia de classes separada.
- Drop de chefe é um pickup de evento (`SuperMagnet`), distinto de gema
  (`Gem`) por não carregar valor numérico de progressão.
- Spawn de chefe é agendado por fração de onda, com onda calculada por
  proporção da duração total da sala — mecanismo pronto para reuso por
  Chefe e Chefão.
- Aviso visual e spawn real são disparos independentes, cada um com seu
  próprio controle de "já disparei este ponto" por visita.
- `METODOLOGIA.md` em v1.7, com checagem cruzada entre os 3 documentos
  principais agora formalizada como parte do Gatilho de Revisão.

---

## Próxima Sprint

**Sprint C — Chefe** (Bloco de Entidades de Chefes, Parte 3/5): ~700 HP,
drop cumulativo (tudo que o Mini-chefe dropa + 50% de HP do player),
entrando no fim da Onda 2 e em 2/3 da Onda 3 — reaproveitando o mesmo
`BOSS_SPAWN_SCHEDULE` e `_update_boss_schedule()` desta sprint, apenas
com novas entradas de configuração.

---

## Resumo Executivo

Esta sprint implementa o Mini-chefe, primeiro dos três chefes do Bloco
de Entidades de Chefes: um inimigo especial que dropa um pickup único
(Ímã Super Power) em vez de gema comum, condicionando upgrades
garantidos e puxão automático de gemas à coleta ativa do jogador. O
sistema de agendamento de spawn por fração de onda — junto com a nova
divisão proporcional (20/30/50%) da duração da sala em 3 minutos — foi
construído de forma genérica, pronto para os próximos dois chefes sem
precisar de nova lógica. Dois refinamentos de UX entraram na mesma
sprint (aviso visual pisca-pisca de chefe se aproximando, texto de cura
na regeneração), e um desvio real de processo foi identificado e
corrigido na própria `METODOLOGIA.md`, fortalecendo o Gatilho de
Revisão de Documentos para checagem cruzada entre os 3 documentos
principais do projeto.

---

## Material para Videoaula / Ebook

- **Gancho:** "Meu chefe morreu e não aconteceu nada" — como um drop
  condicional (pickup a coletar) cria mais tensão do que um bônus automático.
- **Conceito central:** eliminar duplicação de decisão (`_handle_enemy_death`)
  antes que ela se espalhe por mais pontos do código.
- **Momento de metodologia real:** o erro do `Refinamento:` é ótimo
  material — mostra que documentação viva também tem bugs, e que
  "revisar documentos" não é só sobre conteúdo, é sobre referências
  cruzadas entre eles.
