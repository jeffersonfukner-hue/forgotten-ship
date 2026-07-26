# SPRINT_028.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 028
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Ímã (primeiro passivo)

---

## Objetivo da Sprint

Implementar o primeiro item do Bloco de Power-ups planejado (`VISAO.md`,
Plano Consolidado): o **Ímã**, um power-up passivo que amplia o raio de
atração de gemas, junto com a estrutura genérica de power-ups passivos
que vai sustentar os próximos itens do bloco (regeneração de vida, e
outros ainda não detalhados).

---

## Situação Inicial

Ao final da Sprint 027, o jogo tinha obstáculos fixos e destrutíveis
funcionando, mas nenhum power-up existia ainda — a única progressão do
jogador era o upgrade automático de dano de tiro, aplicado a cada
patamar de pontos de drop.

---

## Problema

Adicionar um único power-up (o ímã) sem pensar à frente criaria uma
solução descartável assim que o segundo power-up passivo (regeneração
de vida) entrasse — cada novo item exigiria duplicar atributos e
lógica de upgrade no `Player`. Como o backlog já prevê múltiplos
power-ups passivos, e o próprio roadmap do jogo prevê geração
procedural de levels a partir do Level 10 (exigindo sistemas que
escalem sem intervenção manual), a estrutura precisava nascer genérica
desde o primeiro item.

---

## Decisão Arquitetural

### Configuração por Dicionário, Mesmo Padrão de `Enemy` e `Obstacle`

Em vez de um atributo fixo `magnet_radius` no `Player`, foi criado
`PASSIVE_POWERUPS` em `settings.py` — um dicionário onde cada chave é
um power-up passivo, com `base_value`, `increment` e `max_level`
próprios. O `Player` guarda apenas `passive_levels` (nível atual de
cada um) e calcula o valor efetivo sob demanda via
`get_passive_value(key)`. Adicionar um novo power-up passivo no futuro
(regeneração de vida, por exemplo) não exige nenhuma mudança na lógica
do `Player` — só uma nova entrada no dicionário.

### Sem Escolha de Upgrade Ainda — Sobe Junto com o Automático

Por decisão explícita (seguindo o que já estava fechado no
`CONTEXTO_PROJETO.md`), o ímã não introduz um sistema de escolha entre
opções de upgrade — ele sobe de nível automaticamente, no mesmo
gatilho que já aumenta o dano de tiro (`apply_automatic_upgrade`). A
escolha de 3 opções por upgrade, já sinalizada como pendente no código
desde a Sprint anterior, continua para uma Sprint futura.

### Raio de Atração Substitui o Pickup Fixo, Não Coexiste com Ele

Em vez de o ímã ser um raio adicional separado do pickup normal de
gemas, o gatilho de puxão passou a usar o maior valor entre
`GEM_PICKUP_RADIUS` (pickup base, sem ímã) e o raio calculado do ímã —
via `max()`. No nível 0, os dois valores coincidem (60px), preservando
o comportamento anterior sem regressão; a partir do nível 1, o raio do
ímã passa a dominar.

### Feedback Visual via Painel de Debug, Não Círculo na Tela

Como o painel de debug do HUD é sempre desenhado (sem toggle
liga/desliga), o feedback visual do ímã foi implementado como uma
linha de texto no próprio painel (`Ima: nivel X (raio Ypx)`), em vez
de um círculo desenhado no mundo — mantendo consistência com o padrão
de debug já em uso, sem introduzir um novo tipo de elemento visual
fora de escopo desta Sprint.

---

## Conceitos de Python

- **Dicionário como Tabela de Configuração Genérica** — mesma técnica
  já vista em `ENEMY_TYPES`, aplicada agora a power-ups: uma única
  estrutura de dados decide o comportamento de múltiplas variações,
  sem precisar de uma classe ou atributo por variação.
- **Compreensão de Dicionário (`dict comprehension`)** — `passive_levels`
  é inicializado com `{key: 0 for key in PASSIVE_POWERUPS}`, gerando
  automaticamente uma entrada de nível zero para cada power-up
  configurado, sem listar as chaves manualmente.
- **`max()` para Combinar Dois Raios Concorrentes** — em vez de uma
  condicional (`if magnet_radius > pickup_radius: usa magnet_radius`),
  `max(settings.GEM_PICKUP_RADIUS, magnet_radius)` resolve a
  comparação em uma linha, e naturalmente preserva o comportamento
  antigo quando os dois valores são iguais.

---

## Conceitos de Arquitetura

- **Generalizar Antes do Segundo Caso de Uso, Quando o Backlog Já
  Confirma que Ele Vem** — normalmente vale esperar o segundo caso
  antes de generalizar (evitar abstração prematura), mas aqui o
  backlog já lista múltiplos power-ups passivos e a geração
  procedural de levels já exige escala automática — o custo de
  generalizar agora era baixo e o de não generalizar seria retrabalho
  garantido.
- **Valor Calculado Sob Demanda vs. Atributo Armazenado** — em vez de
  guardar `magnet_radius` como um número que precisaria ser atualizado
  toda vez que o nível mudasse, `get_passive_value()` calcula o valor
  a partir do nível atual sempre que chamado — elimina a possibilidade
  de o valor armazenado ficar dessincronizado do nível real.

---

## Implementações

### Missão 1 — Sistema de Power-ups Passivos

**Arquivos:** `settings.py`, `player.py`

Criado `PASSIVE_POWERUPS` (dicionário de configuração) e, no `Player`,
`passive_levels` (nível atual de cada power-up), `upgrade_passive()`
(incrementa nível respeitando `max_level`) e `get_passive_value()`
(calcula valor efetivo a partir do nível).

### Missão 2 — Atração da Gema pelo Ímã

**Arquivo:** `game_scene.py`

O gatilho de `gem.start_pull()` passou a comparar a distância contra
`max(settings.GEM_PICKUP_RADIUS, magnet_radius)`, em vez de apenas
`GEM_PICKUP_RADIUS` fixo. Adicionada `_build_magnet_line()` ao painel
de debug, mostrando nível e raio atual do ímã.

### Missão 3 — Upgrade Automático do Ímã

**Arquivo:** `player.py`

`apply_automatic_upgrade()` passou a chamar `self.upgrade_passive("magnet")`
junto com o incremento de dano já existente, no mesmo gatilho de
pontos de drop.

---

## Bugs Encontrados

Nenhum bug registrado nesta Sprint — implementação testada em ciclo
completo (nível 0 até nível 5, teto de `max_level` respeitado) sem
comportamento inesperado.

---

## Estado Atual da Arquitetura

```
settings.py
 └── PASSIVE_POWERUPS: dict
      └── "magnet": {base_value, increment, max_level}

Player
 ├── passive_levels: dict[str, int]
 ├── upgrade_passive(key) — incrementa nivel, respeita max_level
 ├── get_passive_value(key) — calcula valor efetivo a partir do nivel
 └── apply_automatic_upgrade() — dano + upgrade_passive("magnet"), mesmo gatilho

GameScene.update()
 └── gemas: pull_trigger_radius = max(GEM_PICKUP_RADIUS, get_passive_value("magnet"))

GameScene._build_debug_lines()
 └── _build_magnet_line() — "Ima: nivel X (raio Ypx)"
```

Testado extensivamente: pickup de gema no nível 0 idêntico ao
comportamento pré-Sprint (sem regressão); raio de atração crescendo
visivelmente a cada upgrade automático; upgrade parando corretamente
no nível 5 (teto configurado); painel de debug refletindo nível e
raio em tempo real.

---

## O que o aluno aprendeu

Como generalizar uma estrutura de dados (dicionário de configuração)
antes de existir um segundo caso de uso, quando há evidência forte de
que ele vem — e como isso difere de abstrair cedo demais sem
necessidade real. Como calcular um valor sob demanda a partir de um
estado (nível) em vez de armazenar o valor calculado, evitando
dessincronia. Como combinar dois valores concorrentes (raio de pickup
normal e raio de ímã) com `max()` em vez de condicional explícita, e
por que isso preserva comportamento anterior automaticamente quando os
dois valores coincidem.

---

## Próxima Sprint

Continuação do Bloco de Power-ups — próximo item a definir (conforme
`VISAO.md`, candidatos: regeneração de vida, arma Fang, armas de fogo).

---

## Resumo Executivo

Esta Sprint implementa o primeiro item do Bloco de Power-ups: o Ímã,
junto com uma estrutura genérica de power-ups passivos (configuração
por dicionário, mesmo padrão já usado em `Enemy` e `Obstacle`) pensada
para sustentar os próximos itens do bloco sem retrabalho. O raio de
atração de gemas cresce automaticamente junto com o upgrade de dano já
existente, sem introduzir escolha entre opções (isso permanece como
Sprint futura). Testado em ciclo completo, do nível 0 ao teto de nível
5, sem bugs.
