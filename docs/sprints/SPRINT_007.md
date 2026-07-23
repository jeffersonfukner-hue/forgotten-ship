# SPRINT_007.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 007
**Status:** Concluída
**Versão da Arquitetura:** Ataque Automático, Projétil e Morte de Inimigos

---

## Objetivo da Sprint

Fechar o primeiro ciclo completo de combate do Modo 1 (Horde Interna):
o jogador passa a atacar automaticamente, mirando sempre o inimigo
mais próximo, e os inimigos passam a poder ser eliminados. Esta Sprint
é o primeiro passo da Ordem de Implementação Sugerida registrada no
Backlog Detalhado do `VISAO.md`.

---

## Situação Inicial

Ao final da Sprint 006, múltiplos inimigos perseguiam o jogador,
causando dano por contato, mas nada no jogo permitia ao jogador
revidar. Os inimigos eram efetivamente imortais.

---

## Problema

Sem uma forma de eliminar inimigos, não existe ciclo de combate — o
jogador só pode fugir ou apanhar, nunca vencer. Era necessário o
primeiro passo mínimo do sistema de ataque descrito na visão do jogo:
um projétil automático, mirando o inimigo mais próximo, capaz de
causar dano suficiente para eliminá-lo.

---

## Decisão Arquitetural

### 1. Ataque Totalmente Automático

Conforme definido no Backlog Detalhado, o jogador não possui controle
manual de mira ou disparo — o `Player` apenas sinaliza quando está
pronto para atirar (`ready_to_shoot()`), e a `GameScene` decide o alvo
e cria o projétil. Essa divisão de responsabilidade mantém o `Player`
desacoplado da lista de inimigos, seguindo o mesmo princípio já usado
para o `Enemy` na Sprint 005.

### 2. Projétil como Entidade Independente

Foi criada a classe `Projectile`, herdando de `Entity`. Ela viaja em
linha reta na direção definida no momento da criação, sem depender de
nenhuma outra classe do jogo — sua única responsabilidade é se mover e
sinalizar quando deve ser removida (`is_dead`), seja por colisão ou
por sair da área jogável.

### 3. Vida e Morte no Inimigo

`Enemy` ganhou `hp` e `is_dead`, seguindo exatamente o mesmo padrão já
estabelecido no `Player` desde a Sprint 005 (`take_damage()` com
proteção contra dano duplicado após a morte). A `Room` ganhou
`remove_dead_enemies()`, filtrando inimigos eliminados antes de
processar a sala a cada frame.

---

## Conceitos de Python

- **Retorno de Objeto vs. Retorno de `None`** — `find_closest_enemy()`
  precisa lidar corretamente com o caso em que nenhum inimigo é
  encontrado (embora, nesta Sprint, isso só ocorra se a lista já
  estivesse vazia — protegido por `if target is not None:`).
- **List Comprehension para Filtragem** — `remove_dead_enemies()` usa
  `[e for e in self.enemies if not e.is_dead]`, um padrão idiomático
  de Python para reconstruir uma lista excluindo itens que atendem a
  uma condição.
- **Criação Silenciosa de Variável por Erro de Digitação** — o bug
  central desta Sprint (ver abaixo) ilustra um risco específico do
  Python: atribuir a um nome digitado incorretamente não gera erro,
  apenas cria uma variável nova, nunca utilizada.

---

## Conceitos de Arquitetura

- **Intermediação para Manter Baixo Acoplamento** — nem o `Player` nem
  o `Enemy` se conhecem diretamente; a `GameScene` atua como
  intermediária, decidindo o alvo e criando o `Projectile`. Esse
  padrão já apareceu na perseguição de inimigos (Sprint 005) e se
  repete aqui de forma consistente.
- **Reaproveitamento de Padrão Já Validado** — o sistema de vida e
  morte do `Enemy` é uma cópia direta do padrão já usado no `Player`
  (Sprint 005), reforçando o valor de estabelecer bons padrões cedo,
  para reutilizá-los sem redesenhar a lógica do zero.

---

## Implementações

### Missão 1 — Vida e Morte do Inimigo

**Arquivo:** `enemy.py`

Adicionados `hp`, `is_dead` e `take_damage()`, seguindo o mesmo padrão
já usado no `Player`.

### Missão 2 — Remoção de Inimigos Mortos da Sala

**Arquivos:** `room.py`, `game_scene.py`

Adicionado `Room.remove_dead_enemies()`, chamado a cada frame antes de
processar a sala atual.

### Missão 3 — Entidade Projectile

**Arquivo:** `projectile.py`

Criada a classe `Projectile`, com movimento em linha reta, dano
configurável, e sinalização de remoção (`is_dead`) por colisão ou
saída da área jogável.

### Missão 4 — Disparo Automático do Jogador

**Arquivo:** `player.py`

Adicionados `shoot_cooldown`, `shoot_interval`, `ready_to_shoot()` e
`confirm_shot()` — o `Player` apenas informa se está pronto para
atirar, sem conhecer os inimigos.

### Missão 5 — Mira, Criação e Colisão de Projéteis

**Arquivo:** `game_scene.py`

Adicionado `find_closest_enemy()`, chamado a cada frame quando o
jogador está pronto para atirar. Projéteis são criados na direção do
alvo, atualizados, verificados contra colisão com inimigos (aplicando
dano e sendo removidos ao acertar), e removidos ao sair dos limites da
sala.

---

## Bugs Encontrados

### Bug — `find_closest_enemy` Sempre Retornava `None`

**Sintoma:** nenhum projétil era criado, mesmo com inimigos presentes
na sala e o jogador pronto para atirar (`ready_to_shoot()` sempre
`True`, nunca alternando para `False` como esperado após um disparo).

**Causa:** dentro do loop de comparação, a linha `colsest = enemy`
continha um erro de digitação (deveria ser `closest = enemy`). Como
Python não impede a criação de uma variável nova, `colsest` era criada
e nunca utilizada, enquanto `closest` permanecia `None` até o fim do
método.

**Investigação:** isolada por instrumentação progressiva — prints
sucessivos em cada camada da lógica (contagem de inimigos, prontidão
para atirar, resultado de `find_closest_enemy`, vetor de direção),
até restringir o problema à comparação de nomes dentro do loop.

**Solução:** correção do nome da variável (`colsest` → `closest`).

**Lição Aprendida:** um bug que não gera nenhum erro, apenas um
resultado incorreto e silencioso, costuma indicar uma variável nova
sendo criada por engano em vez de atualizar a variável esperada — uma
armadilha comum em linguagens que não exigem declaração prévia de
variáveis. Instrumentar cada camada da lógica com prints temporários,
de fora para dentro, é uma estratégia eficaz para isolar esse tipo de
bug sem precisar adivinhar a causa de antemão.

---

## Estado Atual da Arquitetura

```
Player
 ├── shoot_cooldown / shoot_interval
 ├── ready_to_shoot() / confirm_shot()

GameScene.update()
 ├── find_closest_enemy(enemies) — decide o alvo
 ├── cria Projectile na direção do alvo, quando pronto para atirar
 ├── atualiza projéteis, verifica colisão com inimigos
 └── remove projéteis fora da área jogável

Projectile
 ├── update(dt) — movimento em linha reta
 └── is_dead — sinaliza remoção (colisão ou saída da sala)

Enemy
 ├── hp / is_dead
 └── take_damage(amount)

Room
 └── remove_dead_enemies() — filtra inimigos eliminados
```

O ciclo básico de combate está fechado: o jogador atira
automaticamente no inimigo mais próximo, o projétil causa dano, e o
inimigo pode ser eliminado, sumindo da sala.

---

## O que o aluno aprendeu

Como implementar um sistema de mira automática simples, calculando a
distância a múltiplos alvos e escolhendo o menor. Como um erro de
digitação em uma única letra pode causar uma falha completamente
silenciosa, sem nenhum traceback — e como isolar esse tipo de bug
através de instrumentação progressiva com prints, testando uma camada
de cada vez até restar apenas o ponto exato da falha.

---

## Próxima Sprint

Sprint 008 — refinamentos do sistema de combate recém-criado (a
definir com mais detalhe ao início da Sprint). Candidatos do Backlog
Detalhado: condição de "sala limpa" e portas danificadas/trancadas
(base da Progressão Espacial), sistema de drops e barra de progresso.

---

## Resumo Executivo

Esta Sprint fecha o primeiro ciclo completo de combate do jogo: ataque
automático mirando o inimigo mais próximo, projéteis como entidades
independentes, e inimigos capazes de morrer. Um bug real — um erro de
digitação silencioso (`colsest` em vez de `closest`) — ilustrou um
risco importante do Python e uma técnica eficaz de depuração:
instrumentação progressiva, isolando a falha camada por camada até
restar apenas a causa exata.
