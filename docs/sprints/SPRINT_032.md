# SPRINT_032.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 032
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Sifão de Energia

---

## Objetivo da Sprint

Implementar o Sifão de Energia (reskin temático de "Fang"): uma arma
independente que drena energia do inimigo, causando dano e convertendo
uma fração dele em reparo (cura) para o jogador — com cadência própria
e mirando um alvo diferente do tiro principal, para evitar
sobreposição de alvo entre as duas armas.

---

## Situação Inicial

Ao final da Sprint 031, o jogo tinha 2 armas reais (tiro principal e
Sabre Giratório) e 2 passivos de atributo único (ímã, regeneração). O
Sifão seria a primeira arma a levantar uma pergunta nova: se ele
mirasse o mesmo inimigo que o tiro principal já está atacando, seu
efeito na prática seria quase invisível (dano redundante em um alvo
que já ia morrer de qualquer forma).

---

## Problema

Sem uma estratégia de distribuição de alvo, adicionar uma segunda arma
automática correria o risco de nunca ser percebida como uma arma
própria — apenas um multiplicador oculto de dano no mesmo inimigo já
visado. Além disso, `find_closest_enemy()` só retornava um único
inimigo (o mais próximo), sem estrutura nenhuma para "o segundo mais
próximo" ou qualquer posição além da primeira.

---

## Decisão Arquitetural

### Distribuição de Alvo por Ordem de Proximidade

Ideia proposta pelo criador do jogo: cada arma mira uma posição
diferente na fila de proximidade — o tiro principal mira o inimigo
mais próximo (índice 0), o Sifão mira o segundo mais próximo
(índice 1). Se não houver um segundo inimigo dentro do alcance, o
Sifão simplesmente não dispara naquele ciclo — sem erro, sem
substituição de alvo.

### Generalização de `find_closest_enemy()` em `get_enemies_by_distance()`

Em vez de duplicar a lógica de filtro (alcance + linha de visão) para
cada arma que precisasse de um alvo diferente, a função foi generalizada
para retornar **todos** os inimigos válidos, já ordenados por
distância. `find_closest_enemy()` foi mantida como um atalho fino sobre
essa nova função (retorna o índice 0), preservando 100% de
compatibilidade com o disparo automático já existente. Qualquer arma
futura que precise mirar o 3º, 4º inimigo mais próximo reaproveita a
mesma lista, sem lógica nova.

### Raio Extrator: Efeito Instantâneo, Não Projétil

Por sugestão do criador do jogo ("raio extrator"), o Sifão não usa a
classe `Projectile` (que simula um objeto viajando pelo espaço) — o
dano e a cura são aplicados no instante do disparo, e o feedback visual
é apenas uma linha desenhada por uma fração de segundo
(`SIPHON_BEAM_DURATION`) entre o player e o alvo. Escolha
deliberadamente mais simples que replicar o sistema de projéteis: o
conceito de "drenar energia" combina melhor com um feixe instantâneo
do que com algo que viaja e pode ser esquivado.

### Cadência Própria, Independente do Tiro Principal

O Sifão tem seu próprio cooldown (`siphon_cooldown`/`siphon_interval`),
mais lento que o tiro principal por padrão — permite balancear a arma
de forma independente, sem acoplar sua frequência de disparo à do tiro
base.

### Pré-requisito Entre os Dois Eixos do Sifão

Mesmo padrão já usado no Sabre: `siphon_conversao` (fração de cura) só
aparece como opção de upgrade depois que `siphon_dano` atingir nível 1
— evita a mesma armadilha já corrigida antes (escolher um efeito que
ainda não tem base pra funcionar, porque a arma sequer causa dano
ainda).

---

## Conceitos de Python

- **Ordenação com `list.sort(key=...)` e Tupla `(distância, objeto)`**
  — `get_enemies_by_distance()` monta uma lista de pares
  `(distancia, enemy)` e ordena por `key=lambda pair: pair[0]`,
  extraindo só o inimigo no final — técnica padrão para ordenar uma
  coisa por um critério calculado de outra.
- **Fatiar por Índice para "N-ésimo mais próximo"** — `ordered[1]` é
  simplesmente o segundo elemento de uma lista já ordenada; não exige
  nenhuma lógica de busca nova, só um índice diferente sobre a mesma
  estrutura de dados.
- **`round()` vs `int()` para Arredondamento** — `int()` trunca sempre
  para baixo (`int(1.9)` vira `1`), enquanto `round()` arredonda para o
  mais próximo (`round(1.9)` vira `2`) — a escolha errada aqui foi a
  causa direta do bug de cura invisível em níveis baixos.

---

## Conceitos de Arquitetura

- **Generalizar uma Função Existente ao Invés de Duplicar Lógica
  Parecida** — em vez de escrever uma segunda função de busca de alvo
  só para o Sifão, a função original foi ampliada para cobrir o caso
  geral (lista ordenada), e o caso específico antigo (mais próximo)
  virou um atalho sobre o caso geral. Isso evita duas fontes de verdade
  sobre "o que conta como inimigo válido para mira" (alcance + linha de
  visão).
- **Efeito Instantâneo como Alternativa Deliberada a Projétil** — nem
  toda arma precisa da mesma representação técnica; escolher a
  abordagem mais simples que ainda comunica o conceito certo (feixe
  instantâneo, não objeto viajando) evitou complexidade desnecessária.
- **`max(1, valor_calculado)` para Garantir um Piso Mínimo Perceptível**
  — quando um efeito de jogo depende de multiplicação de frações
  pequenas (dano × conversão), garantir um mínimo absoluto evita que o
  resultado numérico "suma" silenciosamente por arredondamento, mesmo
  que a mecânica esteja tecnicamente ativa.

---

## Implementações

### Missão 1 — Dados e Cadência do Sifão

**Arquivos:** `settings.py`, `player.py`

Adicionados `siphon_dano` e `siphon_conversao` em `PASSIVE_POWERUPS`,
agrupados sob a categoria `"sifao"` em `CATEGORY_GROUPS`, com
pré-requisito de `siphon_conversao` sobre `siphon_dano` nível 1.
Criados `siphon_cooldown`/`siphon_interval` e os métodos
`ready_to_siphon()`/`confirm_siphon()` no `Player`, decrementados a
cada frame em `update()`.

### Missão 2 — Distribuição de Alvo por Proximidade

**Arquivo:** `game_scene.py`

Criada `get_enemies_by_distance()`, generalizando o filtro de alcance e
linha de visão já existente para retornar a lista ordenada completa.
`find_closest_enemy()` revisada para ser um atalho sobre essa nova
função, sem mudança de comportamento para o tiro principal.

### Missão 3 — Disparo, Dano, Cura e Feixe Visual

**Arquivo:** `game_scene.py`

Adicionado o bloco de update do Sifão: mira o índice 1 da lista
ordenada, aplica dano instantâneo, calcula cura via
`get_passive_value("siphon_conversao")`, e registra um feixe visual
temporário (`self.siphon_beam`) desenhado em `draw_world()`.

### Ajuste — Feedback Visual de Cura

**Arquivo:** `game_scene.py`

Criado `spawn_heal_text()`, reaproveitando `FloatingText` (que já
aceitava cor customizada sem nenhuma mudança de classe) para exibir
"+X" em verde sobre o player a cada cura aplicada.

### Correção — Padronização de `floating_text.py`

**Arquivo:** `entities/floating_text.py`

Adicionada docstring de classe e cabeçalhos de seção
(`ATUALIZACAO POR FRAME`, `DESENHO`), alinhando o arquivo ao padrão
já usado em `Enemy`, `Player` e `Saber` — revisão de organização, sem
mudança de comportamento.

---

## Bugs Encontrados

### Bug — Cura Invisível em Níveis Baixos de Conversão

**Sintoma:** com `siphon_conversao` em nível 1 ou 2, o "+X" de cura
nunca aparecia na tela, mesmo com a mecânica tecnicamente ativa
(HP do player efetivamente não subia).

**Causa:** `healed = int(siphon_damage * conversion)` truncava para
baixo; com valores baixos de dano e fração de conversão (ex:
`4 * 0.1 = 0.4`), o resultado ficava abaixo de 1 e virava `0`
silenciosamente — sem erro, sem indicação de que algo estava
"funcionando, mas invisível".

**Solução:** substituído por `max(1, round(siphon_damage * conversion))`
— garante que qualquer conversão ativa (`> 0`) sempre cure pelo menos
1 HP, eliminando o truncamento silencioso.

**Lição Aprendida:** operações de arredondamento em cálculos de jogo
podem "funcionar" tecnicamente (sem crash, sem exceção) e ainda assim
produzir um resultado zero que o jogador percebe como "não está
funcionando" — vale sempre considerar um piso mínimo perceptível
quando o cálculo envolve multiplicação de frações pequenas.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ siphon_dano, siphon_conversao)
 ├── CATEGORY_GROUPS (+ siphon_dano/siphon_conversao -> "sifao")
 ├── UPGRADE_PREREQUISITES (+ siphon_conversao -> siphon_dano nivel 1)
 └── SIPHON_INTERVAL / SIPHON_BEAM_DURATION

Player
 ├── siphon_cooldown / siphon_interval
 └── ready_to_siphon() / confirm_siphon()

GameScene
 ├── get_enemies_by_distance(enemies) — lista ordenada por proximidade
 ├── find_closest_enemy(enemies) — atalho: indice 0 da lista ordenada
 ├── siphon_beam: tuple | None — (inicio, fim, tempo_restante) do feixe visual
 ├── spawn_heal_text(x, y, amount) — texto verde "+X", reaproveitando FloatingText
 └── update() — dispara sifao mirando indice 1, aplica dano + cura (com piso minimo)
```

Testado extensivamente: tiro principal continua mirando o inimigo mais
próximo sem mudança perceptível; Sifão mirando o segundo mais próximo
com cadência independente (mais lenta); sem segundo inimigo no raio, o
Sifão não dispara; cura visível com "+X" verde a partir do primeiro
nível de conversão, incluindo valores baixos que antes truncavam para
zero.

---

## O que o aluno aprendeu

Como generalizar uma função existente para um caso mais amplo,
preservando compatibilidade total com quem já a usava, em vez de
duplicar lógica parecida em uma função nova. Como decidir entre
representar uma arma como entidade viajante (projétil) ou efeito
instantâneo, escolhendo a abordagem mais simples que ainda comunica o
conceito pretendido. Por que `int()` e `round()` não são
intercambiáveis em cálculos de jogo, e como um arredondamento
"tecnicamente correto" pode ainda assim quebrar a experiência do
jogador ao fazer um efeito ativo parecer que não está funcionando.

---

## Próxima Sprint

Continuação do Bloco de Power-ups — próximo item a definir entre
Phasers (Phaser Leve / Canhão de Plasma / Metralhadora de Pulso) ou
Escudo Deflector.

---

## Resumo Executivo

Esta Sprint implementa o Sifão de Energia, a terceira arma real do
jogo, resolvendo o problema de sobreposição de alvo com o tiro
principal através de distribuição por proximidade (tiro mira o 1º mais
próximo, Sifão mira o 2º) — generalizando `find_closest_enemy()` numa
função reutilizável para qualquer arma futura. O Sifão foi implementado
como efeito instantâneo (raio extrator) em vez de projétil, com
cadência própria e cura proporcional ao dano causado. Um bug de
arredondamento (cura truncando para zero em níveis baixos) foi
identificado e corrigido com um piso mínimo de 1 HP. Aproveitada a
oportunidade para padronizar a organização de `floating_text.py`,
alinhando-o ao restante do código.
