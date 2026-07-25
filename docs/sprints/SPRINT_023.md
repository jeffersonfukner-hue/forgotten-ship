# SPRINT_023.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 023
**Status:** Concluída
**Versão da Arquitetura:** Sistema de Drops, Upgrades Automáticos e Ondas Antecipadas

---

## Objetivo da Sprint

Implementar o núcleo do sistema de progressão descrito no `VISAO.md`:
inimigos eliminados concedem pontos proporcionais ao seu poder,
acumulados até desbloquear um upgrade automático de dano — provando o
ciclo completo "matar → progredir → ficar mais forte" antes de
introduzir a tela de escolha de skills (adiada para Sprint futura).
Também foram corrigidos dois problemas identificados durante testes:
dano do inimigo não diferenciado por tipo, e a condição de disparo de
onda ignorando quando o jogador eliminava a onda atual antes do tempo
calculado.

---

## Situação Inicial

Ao final da Sprint 022, o jogo possuía dois tipos de inimigo (fraco e
forte) e um sistema de ondas por pressão de tempo, mas nenhuma forma
do jogador evoluir com base em seu desempenho — eliminar inimigos não
tinha nenhuma recompensa além de progredir na sala atual. O dano
causado pelo inimigo ao jogador também era um valor fixo, ignorando
a diferenciação já existente entre tipos.

---

## Problema

Sem um sistema de progressão, o jogador permanece com a mesma
capacidade de combate do início ao fim, tornando ondas mais difíceis
puramente uma questão de resistência, sem contrapartida de evolução —
contradizendo a visão de um jogo onde o jogador cresce em poder ao
longo da partida.

---

## Decisão Arquitetural

### Pontuação Proporcional ao Poder do Inimigo

Em vez de valores de pontuação fixos por tipo, cada `Enemy` calcula seu
próprio `drop_value` a partir de `(hp + damage) / ENEMY_POINTS_DIVISOR`
— uma fórmula que deriva a pontuação da força real do inimigo, e que
automaticamente atribui valores coerentes a qualquer tipo futuro sem
exigir decisão manual por tipo.

### Limiar de Upgrade Crescente

Cada upgrade conquistado aumenta o limiar necessário para o próximo
(`points_to_upgrade *= UPGRADE_THRESHOLD_GROWTH`), seguindo a mesma
filosofia de crescimento proporcional já usada para o tamanho das
ondas — evitando que upgrades fiquem triviais de obter conforme a
partida avança.

### Upgrade Automático como Prova de Conceito

Nesta Sprint, atingir o limiar aplica automaticamente um incremento
fixo de dano (`shoot_damage += UPGRADE_DAMAGE_INCREMENT`), sem
apresentar nenhuma escolha ao jogador. Essa simplificação deliberada
prova o ciclo de progressão isoladamente, antes de introduzir a
complexidade da tela de escolha de 3 opções (registrada no Backlog).

### Dano do Inimigo Passa a Ser um Atributo de Tipo

Assim como HP, velocidade e tamanho, o dano causado por contato
passou a fazer parte da configuração de cada tipo em `ENEMY_TYPES` —
eliminando a inconsistência de um inimigo visualmente mais forte
causar o mesmo dano que um mais fraco.

### Onda Antecipada por Conclusão, não Apenas por Tempo

A condição de disparo da próxima onda passou a considerar dois
gatilhos independentes: o tempo calculado ter se esgotado, **ou** a
onda atual já ter sido completamente eliminada antes disso. Essa
correção evita que um jogador que já eliminou toda a ameaça seja
forçado a esperar um cronômetro que não reflete mais sua capacidade
de combate atual.

---

## Conceitos de Python

- **Fórmula Derivada em vez de Tabela de Valores Fixos** — calcular
  `drop_value` a partir de atributos já existentes do inimigo, em vez
  de uma tabela de pontuação por tipo, é um exemplo de preferir
  computação a duplicação de dados — qualquer tipo futuro herda uma
  pontuação coerente automaticamente.
- **Ponto Flutuante para Progressão Fracionária** — `drop_points` e
  `points_to_upgrade` passaram de inteiros a `float`, permitindo que
  pontuações fracionárias (como a de um inimigo forte, que pode não
  resultar em número inteiro) se acumulem com precisão.
- **`TYPE_CHECKING` para Anotações sem Import Circular Real** —
  resolvido um alerta do analisador de tipos (Pylance) sobre `Room` e
  `Door` não estarem "definidos" em `player.py`, usando o padrão
  oficial `if TYPE_CHECKING:` para importar apenas durante análise
  estática, sem risco de import circular em tempo de execução.

---

## Conceitos de Arquitetura

- **Provar o Ciclo Antes de Complexificar a Interface** — implementar
  o upgrade automático (sem escolha) antes da tela de seleção de 3
  opções valida a mecânica central (drop → progresso → mais poder)
  isoladamente, reduzindo o risco de depurar dois sistemas novos
  (progressão e UI de escolha) ao mesmo tempo.
- **Consistência de Atributos entre Tipos Relacionados** — uma vez que
  HP, velocidade e tamanho já variavam por tipo de inimigo, dano
  também deveria variar — a ausência dessa consistência foi
  identificada em teste real, reforçando a importância de revisar
  atributos relacionados quando um novo é adicionado.
- **Gatilhos Múltiplos para uma Mesma Transição de Estado** — a
  correção do disparo de onda (tempo OU conclusão) ilustra que uma
  transição de estado pode ter mais de uma condição de disparo válida;
  considerar apenas uma delas cobre o caso "esperado", mas pode
  produzir experiência ruim em casos legítimos não antecipados
  (jogador mais forte que o previsto).

---

## Implementações

### Missão 1 — Correção de Alertas de Tipo (Pylance)

**Arquivo:** `player.py`

Adicionado bloco `if TYPE_CHECKING:` para importar `Room` e `Door`
apenas durante análise estática, resolvendo os dois alertas
`reportUndefinedVariable` sem introduzir import circular real.

### Missão 2 — Configuração de Progressão em `settings.py`

**Arquivo:** `settings.py`

Adicionadas `POINTS_PER_UPGRADE`, `UPGRADE_DAMAGE_INCREMENT`,
`UPGRADE_THRESHOLD_GROWTH`, `ENEMY_POINTS_DIVISOR`, e `damage` em cada
entrada de `ENEMY_TYPES`.

### Missão 3 — Progressão no Player

**Arquivo:** `player.py`

Adicionados `level`, `drop_points`, `points_to_upgrade`,
`shoot_damage` (que passou a viver no `Player`, não mais lido
diretamente de `settings` pelo `Projectile`), e os métodos
`add_drop_point()` e `apply_automatic_upgrade()`.

### Missão 4 — Pontuação e Dano por Tipo no Enemy

**Arquivo:** `enemy.py`

Adicionados `damage` e `drop_value`, ambos calculados a partir da
configuração do tipo em `settings.ENEMY_TYPES`.

### Missão 5 — Conexão do Ciclo Completo

**Arquivo:** `game_scene.py`

Ao eliminar um inimigo, `player.add_drop_point(enemy.drop_value)` é
chamado. O disparo do projétil passou a usar `player.shoot_damage`.
Colisão inimigo-jogador passou a usar `enemy.damage`, em vez do valor
fixo anterior.

### Missão 6 — Barra de Progresso Visual

**Arquivo:** `game_scene.py`

Adicionado `draw_progress_bar()` à HUD fixa, exibindo uma barra fina
abaixo do HP com o progresso rumo ao próximo upgrade e o "Level"
atual do jogador. O painel de debug foi simplificado para mostrar
apenas o dano atual, já que a barra visual substitui a representação
textual anterior.

### Missão 7 — Correção do Disparo de Onda Antecipado

**Arquivo:** `game_scene.py`

A condição de disparo de nova onda passou a considerar tanto o tempo
esgotado quanto a onda atual já estar vazia, dependendo apenas de
`current_wave < total_waves` como limite superior.

---

## Estado Atual da Arquitetura

```
Enemy
 ├── damage — por tipo, configurado em settings.ENEMY_TYPES
 └── drop_value — calculado: (hp + damage) / ENEMY_POINTS_DIVISOR

Player
 ├── level / drop_points / points_to_upgrade (cresce a cada upgrade)
 ├── shoot_damage — usado pelo Projectile, aumenta com upgrades
 ├── add_drop_point(amount) — acumula e verifica limiar
 └── apply_automatic_upgrade() — incrementa shoot_damage (temporario, sem escolha)

GameScene
 ├── ao eliminar inimigo: player.add_drop_point(enemy.drop_value)
 ├── colisao inimigo-player usa enemy.damage
 └── disparo de onda: tempo esgotado OU onda atual ja vazia
```

Testado com ciclo completo: dano do tiro aumentando visivelmente a
cada upgrade, barra de progresso e level corretos na HUD, inimigo forte
causando mais dano de contato que o fraco, e onda 2 disparando
imediatamente ao eliminar toda a onda 1 antes do tempo calculado.

---

## Pendência Registrada para Sprint Futura

Durante os testes, foi identificada uma limitação de design mais
profunda: o crescimento de dificuldade por reentrada não deveria vir
principalmente do aumento de quantidade de inimigos (crescimento
geométrico rapidamente torna partidas inviáveis), e sim de uma
numeração contínua de ondas por sala (não reiniciada a cada
reentrada) combinada com um teto de volume e composição de tipos cada
vez mais desafiadora. Esta mudança de arquitetura foi registrada em
detalhe no `VISAO.md` e adiada para uma Sprint dedicada.

---

## O que o aluno aprendeu

Como derivar um valor de jogo (pontuação) a partir de atributos já
existentes, em vez de mantê-lo como uma tabela separada sujeita a
inconsistência. Como resolver alertas de analisador de tipos sem
comprometer a arquitetura, usando importação condicional para fins
apenas de tipagem. Como identificar, através de teste real, que uma
transição de estado (disparo de onda) precisa considerar múltiplos
gatilhos válidos, não apenas o caminho originalmente previsto.

---

## Próxima Sprint

Sprint 024 — refinamento de continuidade de ondas por sala: numeração
contínua entre reentradas, teto de volume de inimigos, e composição
de tipos crescentemente desafiadora, conforme detalhado no `VISAO.md`.

---

## Resumo Executivo

Esta Sprint implementa o núcleo do sistema de progressão do jogador:
pontos de drop proporcionais ao poder do inimigo eliminado, upgrade
automático de dano ao atingir um limiar crescente, e uma barra de
progresso visual com indicador de level. Dois problemas identificados
em teste real foram corrigidos: dano de contato não diferenciado por
tipo de inimigo, e a condição de disparo de onda ignorando quando o
jogador eliminava toda a ameaça antes do tempo calculado — reforçando
a importância de testar múltiplos caminhos de execução, não apenas o
esperado.
