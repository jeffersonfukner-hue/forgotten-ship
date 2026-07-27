# SPRINT_033.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 033
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Escudo Deflector

---

## Objetivo da Sprint

Implementar o Escudo Deflector: o power-up com a progressão mais
diferente do backlog, descrita no `VISAO.md` como "troca de mecânica
por nível" — redefinida nesta Sprint, em conversa com o criador do
jogo, como **3 camadas cumulativas** que se somem progressivamente,
em vez de se substituírem.

---

## Situação Inicial

Ao final da Sprint 032, o jogo tinha 4 power-ups reais (dano, ímã,
regeneração, Sabre, Sifão), todos com uma única forma de efeito por
eixo. O Escudo era o último item do backlog original a ter mecânica
indefinida, registrado no `VISAO.md` apenas como conceito de "trocar
de mecânica" sem detalhamento de comportamento entre as fases.

---

## Problema

A primeira leitura do `VISAO.md` (redução % → barreira → bloqueio,
substituindo uma pela outra) entrava em conflito direto com uma
intenção mais ampla do criador do jogo: "não é só pra substituir, é
pra ficar mais forte com novidades" — ou seja, cada tier deveria
adicionar poder, não trocar uma mecânica antiga por uma nova de
eficiência parecida.

---

## Decisão Arquitetural

### De "Troca de Mecânica" para "Acúmulo de Camadas"

Após discussão direta, a decisão final inverteu a leitura original do
`VISAO.md`: as 3 mecânicas (redução %, barreira, bloqueio) passam a
coexistir simultaneamente, cada uma desbloqueada em sequência via
pré-requisito — mesmo mecanismo já usado no Sabre e no Sifão, agora
encadeado em 3 elos ao invés de 2. Um jogador no nível máximo do
Escudo tem as 3 camadas ativas ao mesmo tempo: redução percentual,
barreira absorvendo o restante, e bloqueio total periódico por cima
de tudo.

### Ordem de Aplicação do Dano: Bloqueio → Redução → Barreira → HP

`take_damage()` foi inteiramente reescrito para processar as camadas
nessa ordem específica: primeiro verifica se há um bloqueio total
disponível (mais forte, checado primeiro); se não, aplica a redução
percentual sobre o valor bruto; o resultado então é absorvido pela
barreira até seu limite; e só o que sobrar depois de todas as camadas
chega ao HP real do player.

### Barreira com Transbordo, Não Descarte

Por decisão explícita do criador do jogo, dano que excede o HP restante
da barreira não é descartado — o excesso "vaza" para o HP do player.
Uma barreira com 5 HP restantes recebendo um golpe de 20 absorve 5 e
deixa 15 atingirem o player normalmente, em vez de zerar a barreira e
descartar os 15 pontos de dano excedente (o que tornaria a barreira
uma proteção quase absoluta contra qualquer golpe, mesmo no fio do
esgotamento).

### Regeneração da Barreira com Delay, Não Contínua

A barreira só recomeça a regenerar depois de um período sem levar
dano (`SHIELD_REGEN_DELAY`), reiniciado a cada novo golpe recebido.
Sem esse delay, contra uma horda contínua de inimigos a barreira
nunca teria chance real de esgotar, tornando a mecânica pouco sensível
ao ritmo de combate.

### `take_damage()` Retorna Tupla, Não Mais `None`

O método passou a retornar `(dano_real_no_hp, foi_bloqueado)`, permitindo
à `GameScene` decidir o feedback visual correto sem duplicar a lógica
de cálculo de dano: número reduzido no texto flutuante normal, ou o
texto especial "Bloqueado!" quando o bloqueio total foi acionado.

---

## Conceitos de Python

- **Retorno de Tupla para Múltiplos Resultados** — `return damage_taken, False`
  permite ao chamador desempacotar dois valores relacionados
  (`damage_taken, was_blocked = self.player.take_damage(...)`) sem
  precisar de um objeto ou dicionário para carregar os dois dados.
- **Early Return em Cadeia para Priorizar Camadas** — a checagem do
  bloqueio total usa `return` imediato assim que aciona, evitando que
  o código de redução/barreira seja avaliado desnecessariamente
  quando o dano já foi zerado por completo.
- **Delay Reiniciado a Cada Evento** — `self.shield_regen_timer = 0.0`
  dentro de `take_damage()` é a técnica clássica de "temporizador que
  reseta a cada gatilho", usada tanto aqui quanto (por analogia) no
  cooldown de dano do player já existente desde Sprints anteriores.

---

## Conceitos de Arquitetura

- **Inverter uma Decisão de Design Já Registrada Quando a Intenção
  Real Diverge** — o `VISAO.md` descrevia "troca de mecânica", mas a
  intenção verdadeira do criador (mais poder a cada nível, não apenas
  mecânica diferente) só ficou clara em conversa direta. Isso reforça
  a importância de validar a leitura de um documento antigo antes de
  implementar, especialmente quando o conceito é ambíguo o suficiente
  para admitir duas interpretações razoáveis.
- **Camadas de Defesa Aplicadas em Pipeline Ordenado** — o dano passa
  por uma sequência fixa de transformações (bloqueio, depois redução,
  depois absorção, depois HP), cada camada operando sobre o resultado
  da anterior — um padrão comum em sistemas de combate com múltiplas
  fontes de mitigação.
- **Transbordo Como Escolha Consciente de Balanceamento** — decidir que
  dano excedente "vaza" em vez de ser descartado é uma escolha de
  design com consequência direta na sensação de risco: sem transbordo,
  uma barreira quase vazia ainda seria proteção total; com transbordo,
  ela protege proporcionalmente ao que resta.

---

## Implementações

### Missão 1 — Dados e Lógica de Dano em Camadas

**Arquivos:** `settings.py`, `player.py`

Adicionados `escudo_reducao`, `escudo_barreira`, `escudo_bloqueio` em
`PASSIVE_POWERUPS`, agrupados sob a categoria `"escudo"`, com cadeia de
pré-requisitos (`escudo_barreira` exige `escudo_reducao` nível 2;
`escudo_bloqueio` exige `escudo_barreira` nível 2). `take_damage()`
reescrito com a lógica de 3 camadas e retorno de tupla. Criado
`update_shield()`, chamado a cada frame, cuidando do delay/regeneração
da barreira e do cooldown do bloqueio.

### Missão 2 — Integração na GameScene

**Arquivo:** `game_scene.py`

Ajustado o ponto de chamada de `take_damage()` para capturar a tupla de
retorno; criado `spawn_block_text()` (texto azul "Bloqueado!",
reaproveitando `FloatingText`), disparado quando `was_blocked` é
verdadeiro em vez do texto de dano normal.

### Missão 3 — Feedback Visual da Barreira

**Arquivo:** `player.py`

Adicionada uma segunda barra (azul), empilhada acima da barra de HP já
existente sobre o sprite do player, mostrando a proporção atual de
`shield_hp` sobre o máximo do nível — só desenhada quando
`escudo_barreira` já foi adquirido (nível > 0).

---

## Bugs Encontrados

Nenhum bug registrado nesta Sprint — as 3 camadas foram testadas em
conjunto (redução nível 2, barreira nível 2, bloqueio nível 1, todas
ativas simultaneamente) sem comportamento inesperado, incluindo
confirmação visual da barra azul esvaziando/regenerando e do texto
"Bloqueado!" aparecendo corretamente.

---

## Refinamentos Registrados para Sprint Futura

### Elevada a Prioridade: Reorganização do Painel de Debug

Durante o teste desta Sprint, ficou visualmente evidente que o painel
de debug já acumula 8+ linhas de power-up, a maioria mostrando "nível 0
(inativo)" sem utilidade imediata para o jogador em teste. O item já
registrado (Tela de Estatísticas dedicada) teve sua prioridade elevada
para logo após o próximo item de power-up implementado — não mais
"algum momento futuro", dado o volume real observado em tela.

### Dano Zero Sem Indicação Textual

Quando redução percentual e barreira absorvem 100% de um golpe, o
texto flutuante mostra "-0" em vez de alguma indicação mais clara de
que o golpe foi neutralizado (mas não por bloqueio total). Registrado
como possível ajuste visual futuro, não bloqueante.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ escudo_reducao, escudo_barreira, escudo_bloqueio)
 ├── CATEGORY_GROUPS (+ os 3 eixos -> "escudo")
 ├── UPGRADE_PREREQUISITES (+ cadeia: reducao -> barreira -> bloqueio)
 └── SHIELD_REGEN_DELAY / SHIELD_REGEN_RATE / SHIELD_BLOCK_COOLDOWN

Player
 ├── shield_hp / shield_regen_timer / block_cooldown
 ├── take_damage(amount) -> (dano_real, foi_bloqueado) — pipeline de 3 camadas
 ├── update_shield(dt) — regenera barreira (com delay) e decrementa cooldown de bloqueio
 └── draw_hp_bar() — barra azul da barreira empilhada sobre a barra de HP

GameScene
 ├── spawn_block_text(x, y) — texto azul "Bloqueado!"
 └── update() — captura tupla de take_damage(), decide texto de dano ou bloqueio
```

Testado extensivamente: redução percentual reduzindo o dano recebido
(confirmado nos números do texto flutuante); barreira absorvendo dano
com transbordo, barra azul visível esvaziando e regenerando após o
delay; bloqueio total periódico exibindo "Bloqueado!" e respeitando o
cooldown de 8s; as 3 camadas ativas simultaneamente sem conflito.

---

## O que o aluno aprendeu

Como questionar e revisar a própria leitura de um documento de design
quando a intenção real do criador diverge da primeira interpretação
escrita. Como estruturar múltiplas camadas de mitigação de dano em
pipeline ordenado, cada uma operando sobre o resultado da anterior.
Como retornar múltiplos valores relacionados de uma função via tupla,
permitindo ao chamador tomar decisões diferentes (texto de dano vs.
texto de bloqueio) sem duplicar lógica de cálculo. Por que "transbordo"
versus "descarte" em sistemas de absorção de dano é uma escolha de
balanceamento consciente, não um detalhe técnico neutro.

---

## Próxima Sprint

Bloco de Power-ups: restam as armas de fogo (Phaser Leve, Canhão de
Plasma, Metralhadora de Pulso) e o tiro múltiplo como últimos itens da
Lista Consolidada.

Prioridade elevada, a atacar logo em seguida: reorganização do painel
de debug / Tela de Estatísticas dedicada.

---

## Resumo Executivo

Esta Sprint implementa o Escudo Deflector como 3 camadas cumulativas de
defesa (redução percentual, barreira com transbordo, bloqueio total
periódico), revertendo a leitura original do `VISAO.md` ("troca de
mecânica") após esclarecer a intenção real do criador do jogo
("progressivamente mais forte, não apenas diferente"). `take_damage()`
foi reescrito como um pipeline ordenado de mitigação, retornando uma
tupla para permitir feedback visual diferenciado (dano reduzido vs.
bloqueio total). Testado extensivamente com as 3 camadas ativas ao
mesmo tempo, sem bugs. O volume crescente de linhas no painel de debug,
evidenciado durante os testes desta Sprint, elevou a prioridade da
Tela de Estatísticas dedicada para a próxima etapa do projeto.
