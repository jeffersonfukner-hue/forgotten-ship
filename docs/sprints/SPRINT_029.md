# SPRINT_029.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 029
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Regeneração de Vida (segundo passivo)

---

## Objetivo da Sprint

Implementar o segundo item do Bloco de Power-ups: **Regeneração de
Vida**, um power-up passivo que recupera HP ao longo do tempo,
reaproveitando a estrutura genérica de power-ups passivos criada na
Sprint 028 (ímã).

---

## Situação Inicial

Ao final da Sprint 028, o sistema de power-ups passivos existia e
funcionava para um único item (ímã). A generalização por dicionário
(`PASSIVE_POWERUPS`) tinha sido feita antecipando múltiplos power-ups,
mas ainda não havia sido testada com um segundo item de verdade.

---

## Problema

Regeneração de vida tem uma diferença estrutural em relação ao ímã: em
vez de um valor lido diretamente (raio), ela precisa **acumular**
fração de HP a cada frame (`dt`) e aplicar cura inteira só quando o
acumulado atingir 1.0 — sem isso, arredondamento por frame faria a
regeneração perder efeito ou nunca aplicar nada.

---

## Decisão Arquitetural

### Acumulador de Fração Separado do Sistema de Nível

Foi criado `_regen_accumulator` (float, privado) no `Player`, que
acumula `regen_per_second * dt` a cada frame e aplica cura inteira
(`int(accumulator)`) quando cruza 1.0, preservando o resto fracionário
para o próximo frame. Isso mantém a taxa de regeneração precisa
independente do framerate.

### Correção Retroativa: Upgrade Automático Genérico de Verdade

Ao integrar a regeneração, ficou evidente que `apply_automatic_upgrade()`
ainda chamava `self.upgrade_passive("magnet")` de forma hardcoded —
funcionava na Sprint 028 porque "magnet" era o único item existente,
mas quebrava silenciosamente para "regen" (o nível nunca subia, apesar
do player upar de level normalmente). Corrigido substituindo a chamada
única por um laço sobre `settings.PASSIVE_POWERUPS`, fazendo jus à
generalização que a Sprint 028 já tinha proposto na teoria, mas não
tinha testado na prática com um segundo item.

> Esta correção é um exemplo direto do padrão "Sistemas que Interagem
> de Forma Não Óbvia" já registrado na Sprint 027: a generalização
> parecia completa, mas só a chegada de um segundo caso de uso real
> revelou a lacuna.

---

## Conceitos de Python

- **Acumulador de Fração (Sub-integer Accumulation)** — padrão comum em
  jogos com taxa de tempo real (`dt` variável): guardar o resto
  fracionário entre frames evita que arredondamentos repetidos
  "percam" uma taxa de mudança pequena (ex: 1 HP/s a 60 FPS é 0.0166
  HP por frame — aplicar `int()` direto a cada frame resultaria em
  zero regeneração).
- **Laço sobre Chaves de Dicionário para Generalizar uma Chamada
  Hardcoded** — `for key in settings.PASSIVE_POWERUPS: self.upgrade_passive(key)`
  substitui uma chamada fixa por uma que se adapta automaticamente a
  quantos itens existirem no dicionário de configuração, sem precisar
  editar este método de novo ao adicionar o terceiro power-up.

---

## Conceitos de Arquitetura

- **Generalização Só é Provada pelo Segundo Caso Real** — a Sprint 028
  criou uma estrutura genérica na teoria, mas o hardcode de `"magnet"`
  sobreviveu porque nunca havia sido posto à prova por um segundo
  item. Isso reforça que "genérico" precisa ser validado com pelo
  menos dois casos de uso antes de ser considerado correto.

---

## Implementações

### Missão 1 — Regeneração de Vida

**Arquivos:** `settings.py`, `player.py`

Adicionada a entrada `"regen"` em `PASSIVE_POWERUPS`. Criado
`_regen_accumulator` e `update_regen()` no `Player`, chamado a cada
frame em `update()`. Corrigido `apply_automatic_upgrade()` para
iterar sobre todos os power-ups passivos configurados, em vez de
upar apenas o ímã.

### Missão 2 — Feedback Visual no Painel de Debug

**Arquivo:** `game_scene.py`

Adicionada `_build_regen_line()`, mostrando "Regen: nivel 0 (inativo)"
antes do primeiro upgrade, e a taxa em HP/s a partir do nível 1 —
mesmo padrão já usado por `_build_magnet_line()`.

---

## Bugs Encontrados

### Bug 1 — Regeneração Nunca Subia de Nível

**Sintoma:** player upava de level normalmente (ímã subindo junto),
mas "Regen" permanecia travado no nível 0 mesmo após múltiplos
upgrades.

**Causa:** `apply_automatic_upgrade()` chamava `upgrade_passive("magnet")`
de forma hardcoded, sem generalizar para os demais power-ups
configurados em `PASSIVE_POWERUPS`.

**Solução:** substituída a chamada única por um laço sobre todas as
chaves do dicionário de power-ups passivos.

**Lição Aprendida:** uma estrutura "genérica" só é validada de verdade
quando testada com mais de um caso — o primeiro item pode mascarar
lacunas que só aparecem no segundo.

---

## Bugs e Refinamentos Registrados para Sprint Futura (Obstáculos)

Não corrigidos nesta Sprint, por decisão explícita de não misturar
correção de obstáculos com a feature de power-ups em andamento:

- **Bug:** obstáculo destrutível pode nascer sobre a posição de
  entrada de uma porta, prendendo o player sem chance de escapar do
  dano até um inimigo destruir o bloco.
- **Refinamento:** obstáculos destrutíveis nascem sem margem mínima
  da parede da sala, permitindo um inimigo ficar preso no vão entre
  parede e obstáculo.
- **Pendência de conteúdo:** obstáculos fixos definidos apenas na
  Sala 1 (`obstacle_data`); Salas 2 e 3 ainda não têm nenhum.

---

## Estado Atual da Arquitetura

```
settings.py
 └── PASSIVE_POWERUPS: dict
      ├── "magnet": {base_value, increment, max_level}
      └── "regen": {base_value, increment, max_level}

Player
 ├── passive_levels: dict[str, int]
 ├── _regen_accumulator: float
 ├── upgrade_passive(key) / get_passive_value(key)
 ├── apply_automatic_upgrade() — laco sobre PASSIVE_POWERUPS (generico, corrigido)
 └── update_regen(dt) — acumula fracao de HP, aplica cura inteira ao cruzar 1.0

GameScene._build_debug_lines()
 ├── _build_magnet_line()
 └── _build_regen_line()
```

Testado extensivamente: ciclo completo de regeneração (nível 0 inativo
até nível upado, HP subindo sozinho até o teto de `max_hp`); ímã
continua funcionando normalmente após a correção do laço genérico.

---

## O que o aluno aprendeu

Como acumular uma taxa fracionária de mudança ao longo de múltiplos
frames sem perder precisão por arredondamento. Como uma estrutura
pensada para ser genérica pode esconder um hardcode residual que só
se revela ao adicionar o segundo caso de uso real — e por que isso não
é motivo de vergonha, é o funcionamento esperado do processo de
generalização (nenhuma abstração é validada sem pelo menos dois casos
concretos testados). Como manter o foco sequencial mesmo diante de um
bug novo, registrando-o para uma Sprint futura de correção em vez de
misturá-lo com o trabalho em andamento.

---

## Próxima Sprint

Antes de prosseguir para os próximos itens do Bloco de Power-ups (Fang,
armas de fogo, tiro múltiplo, sabre giratório, escudo), consultar
referências externas sobre boas práticas validadas de power-up em
jogos de horde survival — buscando o que já demonstrou bom efeito de
engajamento em jogadores, em vez de decidir só por intuição de design.

Bugs e refinamentos de obstáculos (spawn sobre porta, margem de parede,
fixos faltando nas Salas 2 e 3) ficam registrados para uma Sprint
futura de correção, a definir quando entrar na fila.

---

## Resumo Executivo

Esta Sprint implementa o segundo item do Bloco de Power-ups:
Regeneração de Vida, usando acumulador de fração para precisão
independente de framerate. No processo, foi corrigido um bug
retroativo da Sprint 028 — o upgrade automático só subia o ímã de
forma hardcoded, e não generalizava de fato para outros power-ups
passivos, apesar da estrutura ter sido desenhada para isso. Três
itens de obstáculos (um bug de spawn sobre porta, um refinamento de
margem de parede, e conteúdo faltando nas Salas 2 e 3) foram
registrados para correção futura, sem interromper o foco desta
Sprint.
