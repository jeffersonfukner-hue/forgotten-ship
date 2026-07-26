# SPRINT_026.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 026
**Status:** Concluída
**Versão da Arquitetura:** Drops Físicos Coletáveis com Efeito de Arrasto

---

## Objetivo da Sprint

Substituir a pontuação instantânea ao eliminar inimigos por drops
físicos coletáveis (gemas) no mundo do jogo, conforme padrão
consolidado do gênero Horde Survivor (pesquisa registrada na Sprint
024): o jogador precisa se aproximar de cada gema para coletá-la, com
um efeito visual de atração progressiva — a gema começa parada,
acelera em direção ao jogador ao entrar em seu raio de proximidade, e
é efetivamente coletada ao alcançá-lo.

---

## Situação Inicial

Ao final da Sprint 025, eliminar um inimigo concedia pontos de
progressão instantaneamente, sem nenhuma representação física no
mundo — o jogador não via nem precisava buscar nada, os pontos apenas
apareciam no contador.

---

## Problema

A pontuação instantânea, embora funcional, contraria a mecânica mais
definidora do gênero de referência: inimigos derrotados devem soltar
um objeto físico coletável, criando uma camada adicional de
posicionamento tático (arriscar-se para coletar valor vs. manter
distância segura) que o sistema anterior não oferecia.

---

## Decisão Arquitetural

### Gema como Entidade Independente

Foi criada a classe `Gem`, com tamanho proporcional ao valor do drop
(dentro de limites mínimo/máximo para nunca ficar imperceptível ou
excessivamente grande). Gemas não coletadas permanecem no mundo
indefinidamente — não desaparecem sozinhas por tempo, uma decisão
deliberada que preserva valor "perdido" no chão até ser buscado ou até
uma mecânica futura de coleta automática (registrada no `VISAO.md`).

### Efeito de Arrasto em Duas Fases

Em vez de coleta binária (dentro do raio = coletado instantaneamente),
a gema entra em um estado de "sendo puxada" ao cruzar o raio de
proximidade, e passa a se mover em direção ao jogador com velocidade
crescente (aceleração constante até um teto de velocidade máxima) —
só sendo efetivamente coletada ao alcançar uma distância mínima do
jogador. Esse efeito de "devagar no início, rápido ao se aproximar"
foi identificado, através de teste, como significativamente mais
satisfatório visualmente do que uma coleta instantânea.

### Raio de Coleta como Constante Isolada e Ajustável

`GEM_PICKUP_RADIUS` foi mantido como constante independente em
`settings.py`, já pensando na futura implementação do power-up de
ímã: aumentar esse raio por upgrade será uma simples alteração de
valor no `Player`, sem exigir mudança na lógica de atração já
implementada.

### Cálculo de Distância por Centro, não por Canto

Um erro de referência de coordenadas foi identificado durante o
teste: `Entity.x`/`Entity.y` representam o canto superior-esquerdo do
retângulo, não seu centro — usar essas coordenadas diretamente para
calcular distância de proximidade produzia um raio efetivo bem menor
que o configurado. A correção usa `rect.centerx`/`rect.centery` de
ambas as entidades envolvidas.

---

## Conceitos de Python

- **Estado Interno como Interruptor de Comportamento (`being_pulled`)**
  — a gema só se move quando esse atributo é `True`, seguindo o mesmo
  padrão já usado em `Room.time_expired` (Sprint 024): uma flag
  booleana simples controlando se uma lógica de atualização deve ou
  não ser executada.
- **Aceleração Progressiva com Teto (`min(max_speed, ...)`)** — a
  velocidade da gema cresce a cada frame (`pull_speed += acceleration
  * dt`), limitada por `min()` ao valor máximo configurado — o mesmo
  padrão de "crescimento limitado" já usado em `_pick_enemy_type()`
  (Sprint 025), agora aplicado a uma velocidade em vez de uma
  probabilidade.
- **Ponto Central vs. Ponto de Origem de um Retângulo** — a
  diferença entre `rect.x`/`rect.y` (canto) e `rect.centerx`/
  `rect.centery` (centro) é uma fonte comum de erros sutis em cálculos
  de distância — a Sprint reforça a importância de sempre confirmar
  qual referência está sendo usada ao comparar posições de entidades
  de tamanhos diferentes.

---

## Conceitos de Arquitetura

- **Separação entre "Estatística Registrada" e "Recompensa Concedida"**
  — ao eliminar um inimigo, a estatística de morte é registrada
  imediatamente (`register_kill`), mas o ponto de progressão só é
  efetivamente concedido na coleta da gema (`add_drop_point`) — uma
  distinção que separa "o que aconteceu" de "o que o jogador ganhou",
  preparando o terreno para mecânicas onde nem todo drop é
  necessariamente coletado.
- **Preparar Constantes para Upgrades Futuros** — manter o raio de
  coleta como uma constante isolada, mesmo antes do power-up de ímã
  existir, é um exemplo de desenhar a configuração pensando na
  extensão futura, sem acoplar a lógica atual a um valor fixo demais
  para ser ajustado depois.

---

## Implementações

### Missão 1 — Entidade Gem

**Arquivo:** `gem.py` (novo)

Criada a classe `Gem`, com tamanho proporcional ao valor, estado de
arrasto (`being_pulled`, `pull_speed`), e os métodos `start_pull()` e
`update_pull()`.

### Missão 2 — Substituição de Pontuação Instantânea por Drop Físico

**Arquivo:** `game_scene.py`

Ao eliminar um inimigo, `add_drop_point()` deixou de ser chamado
imediatamente — em seu lugar, uma `Gem` é criada na posição do
inimigo derrotado.

### Missão 3 — Coleta por Proximidade com Efeito de Arrasto

**Arquivo:** `game_scene.py`

Adicionada lógica de detecção de proximidade (`GEM_PICKUP_RADIUS`),
disparando `start_pull()` e `update_pull()` a cada frame enquanto a
gema está sendo atraída, concedendo o ponto de progressão apenas ao
alcançar `GEM_COLLECT_DISTANCE`.

### Missão 4 — Constantes de Configuração

**Arquivo:** `settings.py`

Adicionadas `GEM_PICKUP_RADIUS`, `GEM_COLLECT_DISTANCE`,
`GEM_PULL_ACCELERATION`, `GEM_PULL_MAX_SPEED`.

---

## Bugs Encontrados

### Bug — Raio de Coleta Efetivamente Menor que o Configurado

**Sintoma:** o jogador precisava estar quase exatamente sobre a gema
para coletá-la, apesar do raio configurado ser maior que isso.

**Causa:** o cálculo de distância usava `gem.x`/`self.player.x`
(coordenadas de canto superior-esquerdo), não os centros dos
retângulos — subestimando a proximidade real percebida visualmente,
especialmente considerando o tamanho do corpo do jogador (32x32).

**Solução:** o cálculo passou a usar `rect.centerx`/`rect.centery` de
ambas as entidades.

**Lição Aprendida:** ao comparar posições de entidades de tamanhos
diferentes, é essencial confirmar se o cálculo está usando o canto ou
o centro de cada uma — a mesma distância numérica pode representar
proximidades visuais bem diferentes dependendo dessa escolha.

---

## Estado Atual da Arquitetura

```
Gem (Entity)
 ├── value / is_dead
 ├── being_pulled / pull_speed
 ├── start_pull()
 └── update_pull(dt, target_x, target_y, acceleration, max_speed)

GameScene
 ├── ao eliminar inimigo: cria Gem(x, y, drop_value), sem conceder ponto ainda
 └── update(): detecta proximidade (por centro), inicia arrasto,
     concede ponto ao alcançar distancia minima
```

Testado e ajustado: raio de proximidade calibrado (60px, após ajuste
manual a partir do padrão inicial de 40px), efeito de arrasto
confirmado como visualmente satisfatório, gemas não coletadas
permanecendo corretamente no mundo após a sala ser vencida.

---

## Pendências Registradas para Sprint Futura

Duas ideias de coleta automática de gemas remanescentes foram
registradas no `VISAO.md`, mas não implementadas nesta Sprint: puxar
automaticamente todas as gemas ao vencer a sala sem morrer, e um item
raro de "mini-ímã" esporádico que recolhe gemas próximas ao ser
tocado.

---

## O que o aluno aprendeu

Como separar o registro de um evento (estatística de morte) da
concessão de sua recompensa (ponto de progressão), útil quando nem
toda recompensa é necessariamente obtida. Como implementar um efeito
de atração progressiva usando aceleração limitada por um teto de
velocidade. Como um erro sutil de referência de coordenadas (canto vs.
centro) pode produzir um comportamento "quase certo, mas
perceptivelmente errado" — o tipo de bug mais difícil de notar porque
o sistema não falha catastroficamente, apenas produz uma experiência
pior que a esperada.

---

## Próxima Sprint

Bloco de Power-ups — a ser dividido em múltiplas Sprints específicas
(uma por funcionalidade: ímã, regeneração de vida, arma Fang, sistema
de munição/recarga, padrões de tiro múltiplo, sabre giratório,
escudo), seguindo a nova prática de Agrupamento Temático de Sprints
registrada no `METODOLOGIA.md` — cada Sprint correspondendo a um
vídeo de até ~10 minutos.

---

## Resumo Executivo

Esta Sprint substitui a pontuação instantânea por drops físicos
coletáveis: inimigos eliminados deixam gemas no mundo, que o jogador
precisa buscar, com um efeito de arrasto progressivo (devagar no
início, acelerando ao se aproximar) identificado como visualmente mais
satisfatório que a coleta binária original. Um bug de referência de
coordenadas (canto vs. centro do retângulo) foi corrigido durante o
teste, e o raio de coleta foi mantido como constante isolada,
preparado para a futura implementação do power-up de ímã.
