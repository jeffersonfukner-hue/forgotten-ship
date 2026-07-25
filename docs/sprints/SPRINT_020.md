# SPRINT_020.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 020
**Status:** Concluída
**Versão da Arquitetura:** Contador de Inimigos e Painel de Debug de Reentradas

---

## Objetivo da Sprint

Adicionar à HUD um contador de inimigos restantes na horda atual
(pendência esquecida de uma Sprint anterior), corrigir um bug de
"regeneração preguiçosa" nas Reentradas (o valor exibido não
atualizava sem interação do jogador), e construir um painel de debug
mostrando o estado de reentradas de todas as salas já visitadas
simultaneamente.

---

## Situação Inicial

Ao final da Sprint 019, a HUD mostrava HP, sala/visitas, vidas e
tempo de onda, mas não indicava quantos inimigos restavam na horda
atual — obrigando o jogador a contar visualmente. Além disso, o
contador de reentradas da sala atual só era recalculado quando o
jogador tentava atravessar uma porta, deixando a informação exibida
"congelada" caso ele permanecesse parado, mesmo com o tempo real
avançando.

---

## Problema

Sem contador de inimigos, o jogador não tem uma métrica objetiva de
progresso dentro da horda, além de observar a diminuição visual dos
inimigos na tela — que se torna imprecisa em hordas grandes. Sem
recalcular a regeneração de reentradas a cada frame, testar o
comportamento de regeneração por tempo exigia interação artificial
(tocar a porta) apenas para forçar o cálculo, mascarando um
comportamento que deveria ser automático e visível.

---

## Decisão Arquitetural

### Tamanho da Horda Registrado no Momento da Criação

`Room` passou a guardar `horde_total_enemies`, atribuído no momento em
que `spawn_horde()` calcula a quantidade de inimigos a gerar. Isso
permite à HUD exibir "X/Y" (restantes / total original), já que a
lista de inimigos viva (`get_enemies()`) só reflete o "X" — o "Y"
precisa ser preservado separadamente, pois os inimigos são removidos
da lista ao morrer.

### Regeneração de Reentradas Deixa de Ser Sob Demanda

O cálculo de regeneração (`regen_reentries()`) era, até esta Sprint,
executado apenas dentro de `has_reentries_left()` — chamado somente
quando o jogador tentava atravessar uma porta. Isso significava que a
HUD exibia um valor desatualizado sempre que o jogador permanecesse
parado ou em outra sala, mesmo com tempo suficiente decorrido para
regenerar. A correção faz `draw_room_info()` (e o novo painel de
debug) chamarem `regen_reentries()` a cada frame, garantindo que o
valor exibido reflita sempre o estado real, independente de qualquer
interação do jogador com portas.

### Painel de Debug Multi-Sala

Foi adicionado um método que itera sobre todas as salas já criadas
(`self.rooms`), exibindo reentradas e tempo restante até a próxima
regeneração de cada uma — permitindo observar o comportamento de
regeneração em paralelo, sem precisar visitar fisicamente cada sala
para verificar seu estado.

---

## Conceitos de Python

- **Preservar um Valor Antes que Ele Seja Consumido** — `horde_total_enemies`
  ilustra a necessidade de guardar um dado (o tamanho original da
  horda) antes que o processo natural do jogo (inimigos morrendo)
  destrua a informação de onde ele partiu.
- **Avaliação Sob Demanda ("Lazy") vs. Avaliação Contínua** — o bug de
  regeneração ilustra a diferença entre calcular algo apenas quando
  solicitado (lazy) e recalcular a cada frame: a primeira abordagem
  economiza processamento, mas pode produzir a impressão de um valor
  "parado" quando a interface não força o recálculo com a frequência
  necessária.
- **Operador Módulo para Calcular Tempo Restante em um Ciclo** —
  `time_until_next_regen()` usa `elapsed % regen_interval` para
  encontrar quanto tempo já se passou dentro do intervalo de
  regeneração atual, subtraindo do intervalo total para obter o
  tempo restante.

---

## Conceitos de Arquitetura

- **A Interface Pode Revelar Bugs de Lógica Adormecidos** — o bug de
  regeneração preguiçosa só se tornou perceptível quando o
  desenvolvedor tentou observar o comportamento de forma passiva
  (esperando sem interagir) — reforçando que testar múltiplos padrões
  de interação (não apenas o caminho "feliz" esperado) revela
  problemas que passariam despercebidos.
- **Debug Multi-Entidade como Ferramenta de Investigação** — em vez de
  visitar cada sala individualmente para inspecionar seu estado, um
  painel que itera sobre todas as instâncias simultaneamente acelera
  drasticamente a validação de sistemas com múltiplas instâncias
  independentes (como Reentradas por sala, Sprint 018).

---

## Implementações

### Missão 1 — Tamanho da Horda Registrado

**Arquivos:** `room.py`, `game_scene.py`

Adicionado `horde_total_enemies` a `Room`, preenchido em
`spawn_horde()` no momento do cálculo de `enemy_count`.

### Missão 2 — Contador de Inimigos na HUD

**Arquivo:** `game_scene.py`

Adicionado `draw_enemy_counter()`, exibindo "Inimigos: X/Y" com base em
`len(room.get_enemies())` e `room.horde_total_enemies`.

### Missão 3 — Correção da Regeneração Preguiçosa

**Arquivo:** `game_scene.py`

`draw_room_info()` passou a chamar `room.regen_reentries()` antes de
exibir o valor, garantindo atualização a cada frame.

### Missão 4 — Tempo Restante até a Próxima Regeneração

**Arquivo:** `room.py`

Adicionado `time_until_next_regen()`, calculando quanto falta para o
próximo incremento de reentrada usando o operador módulo sobre o
tempo decorrido.

### Missão 5 — Painel de Debug Multi-Sala

**Arquivo:** `game_scene.py`

Adicionado `draw_all_rooms_debug()`, listando reentradas e tempo
restante de todas as salas em `self.rooms`, atualizado a cada frame.

---

## Bugs Encontrados

### Bug — Regeneração de Reentradas Não Atualizava Sem Interação

**Sintoma:** o jogador permaneceu parado em uma sala com reentradas
esgotadas por vários minutos, e o valor exibido na HUD continuou em
"0/5", sem regenerar como esperado.

**Causa:** `regen_reentries()` só era executado dentro de
`has_reentries_left()`, chamado exclusivamente ao detectar colisão com
uma porta — nenhum outro ponto do código disparava esse cálculo.

**Investigação:** confirmada ao esclarecer, com o desenvolvedor, que
nenhuma porta havia sido tocada durante o período de espera — isolando
a causa para a ausência de qualquer gatilho de recálculo.

**Solução:** o desenho da HUD (`draw_room_info()`) passou a chamar
`regen_reentries()` a cada frame, garantindo que o valor exibido
sempre reflita o tempo real decorrido, independente de interação.

**Lição Aprendida:** um cálculo "sob demanda" é eficiente, mas pode
criar uma discrepância perceptível entre o estado real de um sistema e
o que é mostrado ao usuário, se a interface não garantir que a demanda
seja feita com frequência suficiente — especialmente em sistemas
baseados em tempo real.

---

## Estado Atual da Arquitetura

```
Room
 ├── horde_total_enemies — tamanho original da horda, preservado
 └── time_until_next_regen() — tempo restante ate a proxima regeneracao

GameScene.draw_ui()
 ├── draw_enemy_counter() — "Inimigos: X/Y" da sala atual
 ├── draw_room_info() — forca regen_reentries() a cada frame
 └── draw_all_rooms_debug() — lista todas as salas, reentradas e timer
```

Testado com o jogador parado em uma sala sem tocar portas: a
regeneração de reentradas passou a refletir corretamente o tempo
decorrido, visível tanto na sala atual quanto no painel de debug
multi-sala.

---

## O que o aluno aprendeu

Como preservar um valor original antes que o estado natural do jogo o
sobrescreva ou remova. Como a diferença entre avaliação sob demanda e
avaliação contínua pode gerar comportamento aparentemente incorreto,
mesmo quando a lógica matemática está correta. Como um painel de debug
multi-instância acelera a validação de sistemas que existem em
paralelo (múltiplas salas), evitando a necessidade de visitar cada uma
fisicamente para observar seu estado.

---

## Próxima Sprint

Sprint 021 — a definir entre: avanço na Progressão Espacial (ondas
múltiplas por sala com material composto), ou reversão consciente dos
valores de teste ainda pendentes (`HORDE_BASE_ENEMIES`,
`PLAYER_RANGE_RADIUS`) para os valores de produção.

---

## Resumo Executivo

Esta Sprint adiciona um contador de inimigos à HUD (pendência resgatada
de uma Sprint anterior) e corrige um bug real de regeneração
"preguiçosa" no sistema de Reentradas — o valor exibido não atualizava
sem interação do jogador com uma porta. Um painel de debug multi-sala
foi construído para acelerar a validação desse e de futuros sistemas
que existem em múltiplas instâncias simultâneas.
