# SPRINT_011.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 011
**Status:** Concluída
**Versão da Arquitetura:** Grid Visual, Raio de Percepção/Alcance e Alcance de Projétil

---

## Objetivo da Sprint

Resolver duas pendências registradas na Sprint 010: a ausência de
referência visual de movimento em áreas grandes (padrão de piso), e a
implementação real do raio de percepção/alcance que limitava a mira
automática do jogador — substituindo a decisão original de "tiro
persiste até atingir algo" por um alcance máximo configurável,
compartilhado entre percepção e alcance de tiro.

---

## Situação Inicial

Ao final da Sprint 010, o piso das salas era uma cor sólida uniforme,
tornando o movimento pouco perceptível em áreas grandes (a Sala 1) ou
corredores longos (a Sala 2). Além disso, o disparo automático do
jogador mirava qualquer inimigo da sala, sem nenhum limite de alcance
— e o projétil, criado na Sprint 007, viajava indefinidamente até
atingir algo ou sair dos limites da sala.

---

## Problema

Sem referência visual repetida no piso, a câmera (Sprint 008) — por
mais correta que estivesse tecnicamente — não *parecia* estar
funcionando ao olhar a tela: faltava um ponto de comparação para
perceber o deslocamento. Já a ausência de limite de alcance no tiro
tornava o combate pouco tático (o jogador atirava em qualquer inimigo
da sala, incluindo os fora da tela) e o percurso do projétil, sem
limite, era inconsistente com a visão de upgrades de alcance
registrada no `VISAO.md`.

---

## Decisão Arquitetural

### Grid de Piso como Referência de Movimento

Foi adicionado um padrão de grade sutil (linhas finas, discretas, com
espaçamento fixo de 64px) sobre o piso de cada sala, desenhado a
partir das mesmas coordenadas já deslocadas pela câmera. Isso não
introduz nenhuma lógica nova de posicionamento — apenas reutiliza as
coordenadas de desenho já calculadas para o piso e paredes.

### Raio Único de Percepção e Alcance

Ao invés de dois valores independentes, o jogador possui um único
`range_radius`, usado tanto para decidir quais inimigos são elegíveis
à mira automática quanto para definir a distância máxima que um
projétil percorre antes de desaparecer. Essa decisão consciente
(documentada no `VISAO.md`) prioriza previsibilidade para o jogador:
o círculo visível ao redor dele representa exatamente o que será
afetado, sem exceções ocultas.

### Indicador Visual Sempre Presente

Diferente da ideia original registrada no Backlog ("círculo aparece só
quando um inimigo entra no raio"), o indicador passou a ficar **sempre
visível**, com opacidade baixa — uma revisão consciente de design,
priorizando clareza constante sobre economia visual condicional.

### Alcance Máximo e Preparação para Penetração

O `Projectile` passou a rastrear a distância percorrida, marcando-se
para remoção ao atingir `max_range` — substituindo a decisão anterior
de "persistir até atingir algo". Adicionalmente, foi introduzido o
atributo `pierce` (quantos impactos o projétil ainda suporta antes de
morrer), com valor padrão `1` — preservando o comportamento atual
(morre no primeiro impacto), mas já preparado para o futuro upgrade de
Penetração, sem exigir reestruturação quando essa Sprint chegar.

---

## Conceitos de Python

- **Reutilização de Coordenadas Já Calculadas** — o grid de piso não
  recalcula nada: usa as mesmas variáveis `rl`/`rt` (posição da sala já
  deslocada pela câmera) que o restante do método `draw()` já
  utilizava, evitando duplicação de lógica de transformação de
  coordenadas.
- **Vetor com Método `.length()` para Acúmulo de Distância** — o
  `Projectile` acumula `distance_traveled` somando o comprimento do
  vetor de deslocamento a cada frame (`step.length()`), uma forma
  direta de medir distância percorrida sem armazenar posições
  anteriores.
- **Parâmetro com Valor Padrão Preservando Comportamento Existente** —
  `pierce: int = 1` garante que todo código que já criava um
  `Projectile` sem especificar esse parâmetro continue funcionando
  exatamente como antes.

---

## Conceitos de Arquitetura

- **Decisão de Design Documentada Antes de Implementada** — tanto a
  escolha de raio único (vs. dois valores independentes) quanto a de
  indicador sempre visível (vs. condicional) foram registradas no
  `VISAO.md` como decisões conscientes antes de codificadas — preservando
  o motivo da escolha para consulta futura, não apenas o resultado.
- **Preparação Antecipada para Funcionalidade Futura** — adicionar
  `pierce` ao `Projectile` antes de o upgrade de Penetração existir de
  fato é um exemplo de desenhar uma estrutura pensando em uma extensão
  já conhecida, evitando retrabalho quando ela for implementada.

---

## Implementações

### Missão 1 — Grid Visual de Piso

**Arquivo:** `room.py`

Adicionado `draw_floor_grid()`, desenhando linhas horizontais e
verticais espaçadas em 64px sobre o piso, chamado logo após o
desenho do piso em `draw()`.

### Missão 2 — Raio de Percepção/Alcance no Player

**Arquivo:** `player.py`

Adicionado `range_radius` e `draw_range_indicator()`, exibindo um
círculo translúcido, sempre visível, ao redor do jogador.

### Missão 3 — Mira Automática Respeitando o Raio

**Arquivo:** `game_scene.py`

`find_closest_enemy()` passou a ignorar inimigos fora de
`player.range_radius`, antes de considerá-los na busca pelo mais
próximo.

### Missão 4 — Alcance Máximo e Estrutura de Penetração no Projétil

**Arquivos:** `projectile.py`, `game_scene.py`

`Projectile` ganhou `max_range`, `distance_traveled` e `pierce`,
substituindo a lógica de "persiste até atingir algo" por uma distância
máxima configurável. A criação do projétil na `GameScene` passou a
usar `player.range_radius` como `max_range`, e a colisão com inimigos
passou a chamar `projectile.register_hit()` em vez de marcar
`is_dead = True` diretamente.

---

## Estado Atual da Arquitetura

```
Room.draw()
 └── draw_floor_grid() — grade de referência visual sobre o piso

Player
 ├── range_radius — raio único de percepção e alcance
 └── draw_range_indicator() — círculo sempre visível, opacidade baixa

GameScene.find_closest_enemy()
 └── ignora inimigos com distância > player.range_radius

Projectile
 ├── max_range / distance_traveled — desaparece ao atingir o limite
 ├── pierce — impactos restantes antes de morrer (padrão: 1)
 └── register_hit() — decrementa pierce, marca is_dead quando chega a 0
```

O jogador percebe visualmente seu alcance de ação (grid + círculo), e
o combate passou a ter limite espacial real — tanto na mira quanto no
percurso do projétil.

---

## O que o aluno aprendeu

Como um padrão visual simples e repetido (grid) pode resolver um
problema de percepção sem exigir nenhuma mudança de lógica de jogo.
Como decisões de design (raio único vs. independente, indicador
sempre visível vs. condicional) merecem ser documentadas com seu
motivo, não apenas implementadas silenciosamente. Como preparar uma
estrutura de dados para uma funcionalidade futura conhecida
(Penetração), evitando retrabalho ao chegar a hora de implementá-la de
fato.

---

## Próxima Sprint

Sprint 012 — implementar rejogabilidade: respawn de horda mais
desafiadora ao reentrar em uma sala já limpa, avaliando se inimigos
devem passar a existir em todas as salas do jogo, não apenas na Sala 1.

---

## Resumo Executivo

Esta Sprint resolve duas pendências visuais e de combate: um grid
sutil no piso que torna o movimento perceptível em áreas grandes, e um
raio único de percepção/alcance que limita e torna previsível a mira
automática do jogador, com o projétil já preparado para o futuro
upgrade de Penetração sem exigir reestruturação futura.
