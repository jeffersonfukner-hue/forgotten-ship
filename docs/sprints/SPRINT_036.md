# SPRINT_036.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 036
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Tiro Múltiplo

---

## Objetivo da Sprint

Implementar o Tiro Múltiplo: três variantes de padrão de disparo
(Diagonal, Paralelo, Quadrantes) que formam um **grupo de
exclusividade** — a primeira escolhida especializa o Tiro base
permanentemente, as outras duas somem da lista de opções para sempre.
Último item pendente do Bloco de Power-ups original.

---

## Situação Inicial

Ao final da Sprint 035, o jogo tinha 5 power-ups reais, todos
independentes entre si (escolher um nunca afetava a disponibilidade de
outro). O Tiro Múltiplo introduziria pela primeira vez um mecanismo
diferente: **exclusividade permanente** entre ramos de uma mesma
categoria — já registrado como conceito no `VISAO.md` desde antes, mas
nunca implementado.

---

## Problema

O sistema de pré-requisitos (usado no Sabre, Sifão e Escudo) resolve
"eixo B só aparece depois que eixo A atinge nível X" — mas não resolve
"escolher o ramo A bloqueia os ramos B e C para sempre, mesmo que eles
nunca tenham sido escolhidos". Era necessário um mecanismo novo,
distinto de pré-requisito.

---

## Decisão Arquitetural

### Grupos de Exclusividade via Configuração, Não Condicional Hardcoded

Criado `EXCLUSIVE_CATEGORIES` (um `set` de categorias onde a regra se
aplica) e `FREE_CATEGORIES` (categorias que nunca ocupam slot, porque
são consideradas parte do Tiro base, não uma arma nova). Em
`get_available_upgrades()`, ao avaliar uma chave que pertence a uma
categoria exclusiva, o sistema verifica se algum "irmão" da mesma
categoria já tem nível > 0 — se sim, a chave avaliada é escondida
permanentemente, mesmo que ela mesma ainda esteja em nível 0.

### Tiro Múltiplo Não Ocupa Slot

Por ser parte do Tiro base (a arma inicial, que já não ocupa slot via
`"damage"`), as 3 variantes de Múltiplo foram adicionadas a
`FREE_CATEGORIES` — escolher uma delas não consome um dos slots
limitados de armas/passivos equipados.

### Revisão de Design: Quadrantes ao Vivo, Corrigindo uma Primeira
Versão Confusa

A primeira implementação de "Quatro Direções" (reto + trás + cima +
baixo, todos como direções fixas do mundo, disparando cegamente mesmo
sem inimigo ali) foi testada e rejeitada pelo criador do jogo em tempo
real — a sensação era de "mistura com Diagonal/Paralelo", sem
identidade própria. Revisado para **Quadrantes**: o espaço ao redor do
player é dividido em 4 fatias de 90° (direita, baixo, esquerda, cima);
cada direção liberada por nível busca e mira seu próprio inimigo mais
próximo **dentro da sua fatia específica**, só disparando se encontrar
alguém ali. A fatia "Direita" nunca tem upgrade dedicado — ela é
sempre coberta pelo comportamento padrão do Tiro (Frente), que
**exclui dinamicamente** as fatias já reivindicadas por tiros
dedicados, cobrindo apenas o que sobrar.

### Progressão de 3 Níveis para Quadrantes, Não 5

Por decisão do criador do jogo, Quadrantes tem apenas 3 níveis
(nível 1 = Trás, nível 2 = +Cima, nível 3 = +Baixo) — os upgrades
globais de força e velocidade já existentes se aplicam a todos os
tiros da variante, sem precisar de eixos próprios de intensidade.

---

## Conceitos de Python

- **`set` para Testar Pertencimento a um Grupo** — `EXCLUSIVE_CATEGORIES`
  e `FREE_CATEGORIES` são conjuntos, e a checagem `category in settings.EXCLUSIVE_CATEGORIES`
  é O(1), independente de quantas categorias existirem no futuro.
- **`any()` com Generator Expression para "Existe Algum Irmão Escolhido?"**
  — a checagem de exclusividade usa `any(...)` sobre uma expressão
  geradora que percorre `CATEGORY_GROUPS.items()`, parando assim que
  encontra o primeiro irmão com nível > 0, sem precisar montar uma
  lista intermediária.
- **`math.atan2()` para Classificar um Vetor em Quadrante Angular** —
  `atan2(dy, dx)` retorna o ângulo de um vetor em relação à origem,
  já lidando corretamente com todos os quadrantes do plano (diferente
  de `atan()` simples, que teria ambiguidade de sinal); usado para
  decidir em qual das 4 fatias de 90° um inimigo se encontra.
- **`next(..., None)` para "Primeiro Item que Bate a Condição, ou
  Nenhum"** — usado tanto para achar o alvo dedicado de uma fatia
  quanto o alvo da Frente (primeiro inimigo fora das fatias já
  reivindicadas), evitando laços `for` com `break` manual.

---

## Conceitos de Arquitetura

- **Distinguir "Pré-requisito" de "Exclusividade Permanente"** — são
  dois mecanismos parecidos na superfície (ambos escondem opções
  baseado no estado de outro eixo) mas semanticamente diferentes:
  pré-requisito é sobre "ainda não é hora" (reversível conceitualmente,
  já que depende só de nível), enquanto exclusividade é sobre "essa
  porta se fechou para sempre" assim que outra foi escolhida. Modelar
  os dois como conceitos de dados separados (`UPGRADE_PREREQUISITES`
  vs. `EXCLUSIVE_CATEGORIES`) evita forçar um a se comportar como o
  outro.
  Uma categoria pode ser "livre" (não ocupa slot) sem precisar
  pertencer também a um grupo de exclusividade, e vice-versa — os dois
  conceitos (`FREE_CATEGORIES`, `EXCLUSIVE_CATEGORIES`) foram mantidos
  como estruturas de dados independentes, mesmo colidindo na mesma
  categoria (`tiro_multiplo`) neste caso específico.
- **Revisar em Tempo Real Quando o Resultado Não Confere com a
  Intenção** — a primeira versão de "Quatro Direções" era tecnicamente
  correta (fazia exatamente o que a especificação dizia), mas a
  experiência de jogo não correspondia à intenção original. Testar e
  ouvir o resultado prático — não só validar contra o documento
  escrito — foi o que revelou a necessidade da reformulação para
  Quadrantes.

---

## Implementações

### Missão 1 — Dados e Grupo de Exclusividade

**Arquivos:** `settings.py`, `player.py`

Adicionados `tiro_diagonal`, `tiro_quadrantes` (revisado de
"tiro_quatro_direcoes"), `tiro_paralelo` em `PASSIVE_POWERUPS`,
agrupados sob `"tiro_multiplo"` em `CATEGORY_GROUPS`. Criados
`EXCLUSIVE_CATEGORIES` e `FREE_CATEGORIES`. `get_available_upgrades()`
revisado para esconder ramos irmãos permanentemente após a primeira
escolha, e para não contar categorias livres no teto de slots.

### Missão 2 — Lógica de Disparo: Diagonal e Paralelo

**Arquivo:** `player.py`

Criado `get_shot_vectors()`, retornando uma lista de vetores de
disparo (direção + deslocamento de posição) conforme a variante ativa.
Sem nenhuma variante escolhida, retorna apenas o tiro reto original,
preservando o comportamento anterior sem regressão.

### Missão 3 — Lógica de Disparo: Quadrantes (Revisão em Campo)

**Arquivo:** `game_scene.py`

Implementado `_get_quadrant()` (classifica um vetor em uma das 4
fatias via `atan2`), e o bloco de disparo bifurcado: quando Quadrantes
está ativo, cada fatia liberada busca seu próprio alvo mais próximo
dentro dela mesma (`get_enemies_by_distance()` reaproveitado), e a
Frente cobre dinamicamente o que sobrar fora das fatias já
reivindicadas.

---

## Bugs Encontrados

Nenhum bug de código nesta Sprint — o único problema encontrado foi
de design (Quatro Direções misturando visualmente com outras
variantes), resolvido com revisão de conceito, não correção de erro.

---

## Refinamentos Registrados para Sprint Futura

### Bloco de Eixos do Tiro Base (próxima prioridade)

Durante esta Sprint, ficou claro que o Tiro base tem 4 eixos
planejados desde o `VISAO.md` original, mas só 1 implementado até
agora:

- **Poder** — já implementado (`UPGRADE_DAMAGE_INCREMENT`)
- **Velocidade do projétil** — ainda não implementado
- **Penetração** — conceito já existia desde a v2.9 do `VISAO.md`
  (`Projectile` já foi construído tecnicamente prevendo múltiplos
  impactos antes de desaparecer); ainda não exposto como upgrade
- **Rajada (Burst)** — nova ideia registrada nesta Sprint: nível 1 =
  2 disparos por gatilho, nível 2 = 3, até nível 5 = 6 — eixo
  **temporal** (múltiplos disparos em sequência), diferente do Múltiplo
  (que é **espacial** — vários projéteis simultâneos em direções/
  posições diferentes)

Também registrado: **Alcance como power-up passivo** —
`PLAYER_RANGE_RADIUS` hoje é uma constante fixa; deve virar um eixo
em `PASSIVE_POWERUPS` (mesmo padrão do ímã), calculado via
`get_passive_value("range")` em vez de valor estático, cumprindo o que
já estava planejado desde a v2.9 do `VISAO.md`.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ tiro_diagonal, tiro_quadrantes, tiro_paralelo)
 ├── CATEGORY_GROUPS (+ os 3 -> "tiro_multiplo")
 ├── EXCLUSIVE_CATEGORIES: set — categorias com bloqueio permanente entre ramos
 └── FREE_CATEGORIES: set — categorias que nunca ocupam slot (tiro_multiplo)

Player
 └── get_shot_vectors(base_direction) — lista de {direction, offset} conforme variante ativa
      ├── Diagonal: N pares angulados, abrindo mais a cada nivel
      └── Paralelo: N tiros lado a lado, espacados perpendicularmente

GameScene
 ├── _get_quadrant(dx, dy) — classifica vetor em direita/baixo/esquerda/cima via atan2
 └── update() — bifurca disparo: Quadrantes (mira por fatia + Frente dinamica) vs. demais variantes
```

Testado extensivamente: Diagonal com leque abrindo corretamente por
nível; Paralelo com tiros lado a lado, quantidade crescendo até 6;
Quadrantes com Trás/Cima/Baixo cada um mirando seu próprio alvo dentro
da fatia certa, Frente cobrindo dinamicamente o que sobra; grupo de
exclusividade confirmado — escolher uma variante remove as outras duas
permanentemente da lista de opções, em qualquer level up seguinte.

---

## O que o aluno aprendeu

Como modelar exclusividade permanente entre opções como dado de
configuração (`set` de categorias), distinto de pré-requisito por
nível. Como usar `atan2()` para classificar direções em setores
angulares. Como revisar uma implementação tecnicamente correta quando
o resultado prático não confere com a intenção de design — testar em
campo revela problemas que a leitura do documento sozinha não
mostraria. Como usar `next()` com valor padrão para buscas de "primeiro
que bate a condição" sem laços explícitos.

---

## Próxima Sprint

Bloco de Eixos do Tiro Base: Velocidade do projétil, Penetração,
Rajada, e Alcance como power-up passivo — completando os upgrades do
Tiro planejados desde o `VISAO.md` original antes de partir para
qualquer arma nova adicional.

---

## Resumo Executivo

Esta Sprint implementa o Tiro Múltiplo com suas 3 variantes (Diagonal,
Paralelo, Quadrantes), introduzindo o conceito de grupo de
exclusividade permanente entre ramos de uma mesma categoria — distinto
do pré-requisito por nível já usado em Sprints anteriores. A primeira
versão de "Quatro Direções" foi revisada em tempo real após teste
prático revelar que a mecânica, apesar de tecnicamente correta,
misturava visualmente com as outras variantes; a versão final
(Quadrantes) resolve isso fazendo cada direção buscar seu próprio alvo
dentro de uma fatia angular específica. Encerrado o Bloco de Power-ups
original da Lista Consolidada; registrado um novo bloco de eixos
pendentes do Tiro base (velocidade, penetração, rajada, alcance como
passivo) como próxima prioridade.
