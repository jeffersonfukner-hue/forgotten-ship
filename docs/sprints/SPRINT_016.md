# SPRINT_016.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 016
**Status:** Concluída
**Versão da Arquitetura:** HUD Expandida — Timer de Onda e Barra de HP Flutuante

---

## Objetivo da Sprint

Expandir a HUD introduzida na Sprint 015: mover o contador de sala/
visitas (até então desenhado dentro do mundo, afetado pela câmera)
para a interface fixa; adicionar um cronômetro de duração de onda; e
introduzir uma barra de HP flutuante sobre o próprio jogador, para
leitura rápida durante o combate sem precisar olhar para o canto da
tela.

---

## Situação Inicial

Ao final da Sprint 015, a HUD fixa exibia apenas HP e Vidas. O texto
de sala/visitas ainda era desenhado dentro de `Room.draw()`,
recebendo o deslocamento de câmera — uma inconsistência visual em
relação aos demais elementos de interface, que já eram fixos.

---

## Problema

Ter parte da informação de estado do jogo dentro do mundo (afetada
pela câmera) e parte fixa na tela cria uma experiência inconsistente
— o contador de visitas "flutuava" pela tela conforme o jogador se
movia, ao invés de permanecer em um local prático de leitura. Além
disso, não havia nenhuma forma de o jogador acompanhar quanto tempo
uma horda estava levando para ser derrotada, uma métrica já registrada
como relevante para o sistema de ranking (`VISAO.md`).

---

## Decisão Arquitetural

### Unificação de Toda Informação de Estado na HUD Fixa

O texto de sala/visitas foi removido de `Room.draw()` e recriado como
`draw_room_info()` em `GameScene`, seguindo o mesmo padrão dos demais
elementos de HUD (HP, Vidas). Isso consolida toda a informação de
estado do jogador e da sala em um único local visual, com ordem de
leitura lógica: HP, Sala/Visitas, Vidas, Timer de Onda.

### Rastreamento de Tempo por Horda

`Room` passou a registrar `horde_start_time` (quando a horda atual
começou) e `horde_clear_time` (quanto tempo levou para ser derrotada,
`None` enquanto ainda ativa). `spawn_horde()` reinicia esses valores a
cada nova horda — seja a primeira ou uma gerada por rejogabilidade
(Sprint 012).

### Barra de HP como Feedback de Combate Imediato

Diferente da barra de HP da HUD fixa (posição absoluta na tela), a
nova barra flutuante acompanha a posição do próprio jogador na tela,
seguindo a mesma câmera — reduzindo a necessidade de desviar o olhar
para o canto da tela durante o combate ativo.

---

## Conceitos de Python

- **Reaproveitamento de Fórmula Já Existente** — a barra de HP
  flutuante usa exatamente a mesma técnica de dois retângulos
  sobrepostos com proporção (`hp / max_hp`) já criada na Sprint 015
  para a barra fixa, aplicada agora em uma posição relativa ao
  jogador em vez de absoluta na tela.
- **`time.time()` para Medir Duração** — a duração de uma onda é
  calculada pela diferença entre o tempo atual e o momento de início
  registrado, uma técnica simples e direta para cronometragem sem
  bibliotecas adicionais.

---

## Conceitos de Arquitetura

- **Consistência de Camada Visual** — misturar elementos fixos e
  elementos afetados por câmera para o mesmo tipo de informação
  (estado do jogo) gera inconsistência perceptível; unificar tudo na
  mesma camada (HUD fixa) resolve isso de forma simples, sem exigir
  nova lógica — apenas reposicionamento do desenho existente.
- **Estado Efêmero vs. Persistente na Mesma Entidade** — `Room` já
  guardava estado persistente (`times_cleared`); o tempo de horda
  (`horde_start_time`/`horde_clear_time`) é efêmero, resetado a cada
  nova onda, mas convive na mesma classe sem conflito, pois cada
  atributo tem um ciclo de vida próprio e bem definido.

---

## Implementações

### Missão 1 — Remoção do Texto de Sala do Mundo

**Arquivo:** `room.py`

Removido o desenho de texto de `Room.draw()`, substituído por um
comentário indicando a migração para a HUD.

### Missão 2 — Reordenação e Expansão da HUD

**Arquivo:** `game_scene.py`

Adicionado `draw_room_info()` (sala/visitas) e `draw_wave_timer()`
(cronômetro de onda), reordenando `draw_ui()` para a sequência HP →
Sala/Visitas → Vidas → Timer de Onda.

### Missão 3 — Rastreamento de Tempo de Horda

**Arquivos:** `room.py`, `game_scene.py`

Adicionados `horde_start_time`/`horde_clear_time` a `Room`, atualizados
em `spawn_horde()` (início) e no momento de destravamento de portas em
`update()` (fim).

### Missão 4 — Barra de HP Flutuante

**Arquivo:** `player.py`

Adicionado `draw_hp_bar()` ao `Player`, desenhando uma barra fina
acima do retângulo do jogador, seguindo a câmera junto com ele.

---

## Bugs Encontrados

### Bug — `NameError: name 'random' is not defined`

**Sintoma:** o jogo falhava ao iniciar, com erro indicando que
`random` não estava definido dentro de `spawn_horde()`.

**Causa:** ao adicionar `import time` no início do método (para o
rastreamento de tempo de horda), o `import random` já existente desde
a Sprint 013 foi removido acidentalmente durante a edição manual.

**Investigação:** identificado ao revisar o método completo após o
erro, comparando com a versão esperada.

**Solução:** reintrodução do `import random` junto do `import time`,
ambos no início do método.

**Lição Aprendida:** ao adicionar uma nova linha de código próxima a
outras já existentes, vale conferir o trecho inteiro após a edição —
uma linha aparentemente não relacionada pode ser removida por engano
durante um recorte e substituição manual, sem gerar nenhum aviso até
a execução revelar o problema.

---

## Estado Atual da Arquitetura

```
GameScene.draw_ui()
 ├── draw_hp_bar()        — HP absoluto, canto da tela
 ├── draw_room_info()      — sala + visitas, canto da tela
 ├── draw_lives_counter()  — vidas, canto da tela
 └── draw_wave_timer()     — tempo da onda atual ou da ultima concluida

Room
 ├── horde_start_time
 └── horde_clear_time (None enquanto ativa)

Player.draw()
 └── draw_hp_bar() — barra flutuante, segue a camera junto ao jogador
```

Toda informação de estado do jogo agora vive consistentemente na HUD
fixa, com o cronômetro de onda fornecendo feedback adicional de
progresso durante o combate.

---

## O que o aluno aprendeu

Como consolidar elementos de interface espalhados entre diferentes
camadas de desenho (mundo vs. HUD) em um único local consistente. Como
implementar um cronômetro simples usando `time.time()`, e como
projetar atributos de ciclo de vida efêmero (resetados a cada onda)
convivendo com atributos persistentes na mesma classe. Como um erro
de edição aparentemente pequeno (remoção acidental de um `import`)
pode passar despercebido até a execução revelar a falha.

---

## Próxima Sprint

Sprint 017 — a definir entre: sistema de Reentradas Limitadas, avanço
na Progressão Espacial (ondas múltiplas por sala), ou barra de HP
flutuante também para os inimigos.

---

## Resumo Executivo

Esta Sprint consolida toda a informação de estado do jogo na HUD
fixa, elimina a inconsistência de um elemento visual sendo afetado
pela câmera enquanto os demais não eram, e adiciona dois recursos de
feedback: um cronômetro de duração de onda e uma barra de HP flutuante
sobre o jogador — reforçando a leitura visual do combate sem exigir
que o jogador desvie o olhar para o canto da tela.
