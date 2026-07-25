# SPRINT_021.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 021
**Status:** Concluída
**Versão da Arquitetura:** Ondas por Pressão de Tempo e Painel de Debug

---

## Objetivo da Sprint

Implementar o primeiro passo real da Progressão Espacial (`VISAO.md`):
salas com múltiplas ondas de inimigos, onde a transição entre ondas
ocorre por **pressão de tempo** — calculada dinamicamente a partir da
capacidade de combate do jogador — e não pela simples eliminação de
todos os inimigos da onda atual. A Sprint também conectou o dano do
projétil a `settings.py` (pendência da Sprint 019) e consolidou toda a
informação de debug em um painel visual único, translúcido e
compacto.

---

## Situação Inicial

Ao final da Sprint 020, cada sala possuía uma única horda; ao ser
completamente eliminada, a sala era considerada limpa. Não havia
conceito de múltiplas ondas dentro do mesmo ciclo de combate, e o dano
do projétil (`Projectile.damage`) ainda era um valor fixo no próprio
construtor, não conectado à centralização de tuning da Sprint 019.

---

## Problema

Uma única onda por sala, por maior que seja, ainda permite ao jogador
uma abordagem sem urgência real — não há motivo para não recuar,
reagrupar e voltar no próprio ritmo. A visão do jogo exige uma
estrutura de ondas múltiplas com pressão temporal, forçando decisões
mais imediatas.

---

## Decisão Arquitetural

### Tempo de Onda Calculado, não Arbitrário

O tempo até a próxima onda é calculado a partir do HP do inimigo e do
dano do disparo do jogador — `tiros_necessários = HP / dano`,
multiplicado pelo intervalo entre disparos, multiplicado pela
quantidade de inimigos da onda. Essa decisão (registrada no `VISAO.md`
antes da implementação) garante que o tempo de onda se ajuste
automaticamente conforme o jogador evolua (mais dano, mais velocidade
de disparo), sem exigir uma fórmula nova a cada upgrade futuro.

### Ondas se Acumulam, não Substituem

A nova onda é gerada **independentemente** de quantos inimigos da onda
anterior ainda estão vivos — os inimigos remanescentes permanecem, e
os novos se somam a eles. Essa é a diferença central entre "pressão de
tempo" e "conclusão de onda": o jogador que demora é penalizado com
mais inimigos simultâneos, não apenas com uma nova onda "limpa".

### Extração de `_spawn_wave_enemies`

O sorteio de posições nas bordas da sala, antes exclusivo de
`spawn_horde()`, foi extraído para um método próprio
(`_spawn_wave_enemies`), reutilizado tanto pela primeira onda quanto
pelas ondas subsequentes — evitando duplicar a lógica de
posicionamento seguro em relação às portas.

### Consolidação do Debug em Painel Único

Toda informação de debug (visitas, reentradas, tempo de onda, contador
de inimigos, countdown da próxima onda, e o estado de todas as salas
já visitadas) foi reunida em um único painel translúcido, com fonte
menor — separado das informações essenciais sempre visíveis (HP,
sala atual, vidas), que permanecem como elementos de HUD definitivos.

---

## Conceitos de Python

- **Extração de Método para Reuso entre Contextos Semelhantes** —
  `_spawn_wave_enemies` segue o mesmo princípio já aplicado em Sprints
  anteriores: identificar lógica repetida entre dois pontos de uso
  (primeira onda e ondas seguintes) e isolá-la em um método próprio.
- **Construção de Texto em Lista, Desenhado em Lote** — o painel de
  debug monta uma lista de strings (`_build_debug_lines`) antes de
  desenhar, separando a lógica de "o que mostrar" do "como desenhar"
  — facilitando adicionar ou remover linhas sem tocar na lógica de
  posicionamento do painel.
- **Superfície com Canal Alfa para Fundo Translúcido** — o painel usa
  `pygame.Surface(..., pygame.SRCALPHA)` com `fill()` em uma cor com
  componente alfa, a mesma técnica já usada para o fade do jogador
  (Sprint 004) e do círculo de percepção (Sprint 011), aplicada agora
  a um elemento de interface.

---

## Conceitos de Arquitetura

- **Fórmulas Dinâmicas em vez de Constantes Fixas** — calcular o tempo
  de onda a partir de variáveis reais do jogo (HP do inimigo, dano do
  jogador) em vez de um número fixo é uma decisão que absorve mudanças
  futuras automaticamente, evitando retrabalho quando o balanceamento
  do combate evoluir.
- **Efeitos Emergentes como Sinal de Sistema Bem Construído** — a
  observação de que salas grandes acumulam mais pressão que salas
  pequenas não foi projetada deliberadamente; ela emergiu da interação
  entre dois sistemas independentes (geometria da sala e cálculo de
  tempo de onda) — um indicativo de que os sistemas estão suficientemente
  desacoplados para produzir comportamento interessante sem
  coordenação explícita entre eles.
- **Separação entre Informação Essencial e Informação de Debug** — a
  divisão entre HUD permanente (HP, sala, vidas) e painel de debug
  (todo o resto) reconhece que nem toda informação exibida hoje fará
  parte da experiência final do jogo — uma distinção explícita evita
  confundir "o que o jogador final verá" com "o que o desenvolvedor
  precisa ver agora para testar".

---

## Implementações

### Missão 1 — Conexão do Dano do Projétil a `settings.py`

**Arquivos:** `settings.py`, `projectile.py`

Adicionada `PLAYER_SHOOT_DAMAGE`; `Projectile` passou a usar esse
valor como padrão quando `damage` não é explicitamente informado.

### Missão 2 — Estrutura de Ondas na Room

**Arquivo:** `room.py`

Adicionados `current_wave`, `total_waves` (fixo em 2, por decisão de
escopo desta Sprint) e `next_wave_time`.

### Missão 3 — Cálculo de Tempo por Onda

**Arquivo:** `game_scene.py`

Adicionado `calculate_wave_time()`, calculando o tempo total da onda a
partir de tiros necessários por inimigo e do intervalo de disparo do
jogador.

### Missão 4 — Geração e Agendamento de Ondas

**Arquivo:** `game_scene.py`

`spawn_horde()` foi reestruturado para gerar apenas a primeira onda e
agendar a próxima via `next_wave_time`. Extraído `_spawn_wave_enemies()`
para reutilização entre ondas.

### Missão 5 — Disparo da Próxima Onda por Tempo

**Arquivo:** `game_scene.py`

Adicionada, no início de `update()`, a verificação de `next_wave_time`
— ao vencer o prazo, uma nova onda (50% maior que a anterior) é gerada
e somada aos inimigos remanescentes, sem removê-los.

### Missão 6 — Painel de Debug Consolidado

**Arquivo:** `game_scene.py`

Substituídos os métodos de desenho individuais (`draw_room_info`,
`draw_lives_counter`, `draw_wave_timer`, `draw_enemy_counter`,
`draw_next_wave_countdown`, `draw_all_rooms_debug`) por
`draw_room_and_lives()` (elemento essencial) e `draw_debug_panel()`
(painel translúcido único, construído a partir de
`_build_debug_lines()`).

---

## Estado Atual da Arquitetura

```
Room
 ├── current_wave / total_waves
 └── next_wave_time — timestamp da proxima onda, None quando esgotadas

GameScene
 ├── calculate_wave_time(enemy_count) — tiros necessarios x intervalo
 ├── spawn_horde() — gera onda 1, agenda a onda 2
 ├── _spawn_wave_enemies(room, count) — reutilizado entre ondas
 └── update(): dispara nova onda ao vencer next_wave_time, soma aos
     inimigos remanescentes; sala so e considerada limpa com todas as
     ondas disparadas e lista de inimigos vazia

HUD
 ├── draw_hp_bar() — essencial, sempre visivel
 ├── draw_room_and_lives() — essencial, "Room X | Vidas: Y/Z"
 └── draw_debug_panel() — painel translucido, toda informacao de teste
```

Testado em três salas de tamanhos distintos: em salas grandes, ondas
se acumulam por conta do tempo de deslocamento dos inimigos; em salas
pequenas, o jogador consegue eliminar a onda antes da seguinte — efeito
emergente registrado no `VISAO.md`.

---

## O que o aluno aprendeu

Como calcular um valor de balanceamento (tempo de onda) dinamicamente
a partir de variáveis reais do jogo, em vez de fixá-lo arbitrariamente
— absorvendo mudanças futuras de dano e cadência sem exigir ajuste
manual. Como um sistema pode produzir comportamento emergente
interessante simplesmente pela interação entre partes independentes
(geometria de sala e tempo de onda), sem que isso tenha sido projetado
deliberadamente. Como separar informação essencial de interface de
informação de debug, usando técnicas já dominadas (superfícies com
canal alfa) em um novo contexto (painel de UI).

---

## Próxima Sprint

Sprint 022 — a definir entre: implementação de tipos de inimigo
(pré-requisito para Ondas Mistas, já registrada no `VISAO.md`), ou
início do sistema de drops e barra de progresso de upgrades.

---

## Resumo Executivo

Esta Sprint implementa o mecanismo central da Progressão Espacial:
ondas de inimigos disparadas por pressão de tempo, calculada
dinamicamente a partir da capacidade real de combate do jogador, com
inimigos remanescentes se acumulando com os da nova onda. Um painel de
debug translúcido consolida toda informação de teste em um único
lugar, e uma observação de gameplay emergente — o tamanho da sala
afetando naturalmente a dificuldade da pressão de tempo — foi
registrada como validação de que os sistemas do jogo estão
suficientemente desacoplados para produzir comportamento interessante
por conta própria.
