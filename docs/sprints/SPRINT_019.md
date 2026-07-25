# SPRINT_019.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 019
**Status:** Concluída
**Versão da Arquitetura:** Tuning Centralizado e Regra de Feedback Visual

---

## Objetivo da Sprint

Centralizar constantes de balanceamento e ajuste — antes espalhadas
por múltiplos arquivos — em uma seção dedicada de `settings.py`,
permitindo testes rápidos sem precisar localizar valores dentro da
lógica do jogo. Formalizar, na metodologia do projeto, duas práticas
já observadas como necessárias: feedback visual por padrão para toda
regra nova, e centralização de constantes de tuning.

---

## Situação Inicial

Ao final da Sprint 018, valores como quantidade de inimigos por horda,
raio de percepção do jogador, intervalo de disparo e limite de
reentradas estavam definidos diretamente dentro da lógica de cada
classe (`Player`, `Room`, `GameScene`). Ajustar qualquer um deles para
fins de teste exigia localizar o arquivo e a linha exatos — um
processo lento durante sessões de teste intensivas, como as vividas na
Sprint 018.

---

## Problema

Testar e balancear um jogo exige ajustar valores numéricos com
frequência — velocidade, quantidade, tempo, alcance. Sem um local
único para esses valores, cada ajuste se torna uma pequena caçada pelo
código, aumentando o atrito de iteração exatamente no momento em que
mais se precisa de agilidade (testes e ajustes de balanceamento).

---

## Decisão Arquitetural

### Seção de Tuning em `settings.py`

Uma seção claramente demarcada foi adicionada a `settings.py`,
agrupando por categoria (Player, Horda, Reentradas) todas as
constantes ajustáveis identificadas até o momento. Cada classe
(`Player`, `Room`, `GameScene`) passou a ler seus valores iniciais a
partir dessas constantes, em vez de defini-los diretamente.

### Duas Novas Regras de Metodologia

Durante a Sprint 018, ficou evidente que a ausência de feedback visual
(a informação de reentradas só existia em `print()`) contribuiu para a
dificuldade de diagnosticar o comportamento do sistema. Da mesma
forma, a dispersão de constantes dificultou os testes rápidos que a
própria investigação exigiu. Essas duas observações foram promovidas a
regras formais da metodologia: toda regra de jogo nova nasce com
algum feedback visual (não apenas console), e toda constante de
balanceamento vive centralizada em `settings.py`.

---

## Conceitos de Python

- **Configuração como Módulo Importável** — `settings.py`, já usado
  desde a Sprint 001 para dimensões de janela, se expande naturalmente
  para acomodar constantes de gameplay, sem exigir nenhuma estrutura
  nova — apenas um módulo Python comum, importado onde necessário.
- **Inicialização a partir de Configuração Externa** — atributos como
  `self.max_hp = settings.PLAYER_MAX_HP` desacoplam o valor de sua
  origem: a classe não precisa saber que o valor "12" existe em algum
  lugar específico, apenas que ele vem de uma fonte de configuração.

---

## Conceitos de Arquitetura

- **Separação entre Configuração e Lógica** — mesmo em um projeto
  pequeno, distinguir "o que pode mudar por ajuste de design" (tuning)
  de "como o sistema funciona" (lógica) reduz o custo de iteração —
  uma prática que escala bem conforme o número de sistemas cresce.
- **Promoção de Observação em Prática para Regra Formal** — as duas
  novas regras de metodologia não foram definidas antecipadamente:
  emergiram de uma necessidade real, sentida durante a investigação de
  bugs da Sprint anterior. Formalizá-las evita que a mesma dificuldade
  se repita silenciosamente em Sprints futuras.

---

## Implementações

### Missão 1 — Seção de Tuning em `settings.py`

**Arquivo:** `settings.py`

Adicionadas as constantes: `PLAYER_MAX_HP`, `PLAYER_MAX_LIVES`,
`PLAYER_SHOOT_INTERVAL`, `PLAYER_RANGE_RADIUS`,
`PLAYER_KNOCKBACK_FORCE`, `HORDE_BASE_ENEMIES`,
`HORDE_ENEMIES_PER_VISIT`, `SAFE_SPAWN_DISTANCE`,
`ROOM_MAX_REENTRIES`, `ROOM_REGEN_INTERVAL`.

### Missão 2 — Conexão do Player

**Arquivo:** `player.py`

`__init__` reorganizado em seções comentadas (movimento/navegação,
fade de portas, vida/vidas, cooldowns, combate), lendo os valores
iniciais a partir de `settings`.

### Missão 3 — Conexão da Room

**Arquivo:** `room.py`

`__init__` reorganizado em seções comentadas (geometria, rejogabilidade,
reentradas, cronômetro de horda), lendo `max_reentries` e
`regen_interval` a partir de `settings`. Extraído `_now()` como
método auxiliar para centralizar `time.time()`, evitando repetir o
`import time` em múltiplos métodos.

### Missão 4 — Conexão da GameScene

**Arquivo:** `game_scene.py`

`spawn_horde()` e a constante `SAFE_DISTANCE_FROM_DOOR` passaram a
usar `settings.HORDE_BASE_ENEMIES`, `settings.HORDE_ENEMIES_PER_VISIT`
e `settings.SAFE_SPAWN_DISTANCE`.

### Missão 5 — Formalização das Regras de Metodologia

**Arquivo:** `METODOLOGIA.md` (repositório institucional)

Adicionadas duas regras à Seção 4 (Regras de Execução): feedback
visual por padrão para regras de jogo novas, e centralização de
constantes de tuning em `settings.py`.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── (configuracao de janela, ja existente)
 └── TUNING / DESENVOLVIMENTO
      ├── PLAYER_* (HP, vidas, tiro, alcance, knockback)
      ├── HORDE_* (inimigos base, incremento por visita)
      ├── SAFE_SPAWN_DISTANCE
      └── ROOM_* (reentradas, intervalo de regeneracao)

Player.__init__() / Room.__init__() / GameScene (constantes de classe)
 └── leem seus valores iniciais de settings, nao mais hardcoded
```

Testado com ajustes reais durante a própria Sprint: o desenvolvedor
alterou `HORDE_BASE_ENEMIES` para `1` e `PLAYER_RANGE_RADIUS` para
`300` diretamente em `settings.py`, sem tocar em nenhum outro arquivo,
confirmando o objetivo da centralização.

---

## O que o aluno aprendeu

Como separar configuração ajustável de lógica de funcionamento,
mesmo em um projeto ainda pequeno — antecipando a dor de manutenção
que a dispersão de constantes causaria conforme o jogo crescesse. Como
promover uma dificuldade real, sentida durante o desenvolvimento
(Sprint 018), a uma regra formal de processo, evitando que a mesma
lição precise ser reaprendida silenciosamente mais adiante.

---

## Próxima Sprint

Sprint 020 — a definir entre: avanço na Progressão Espacial (ondas
múltiplas por sala com material composto), ou reversão consciente dos
valores de teste (`HORDE_BASE_ENEMIES`, `PLAYER_RANGE_RADIUS`) para os
valores de produção, quando os testes atuais forem concluídos.

---

## Resumo Executivo

Esta Sprint centraliza constantes de balanceamento — antes espalhadas
por `Player`, `Room` e `GameScene` — em uma seção dedicada de
`settings.py`, permitindo ajustes rápidos sem caçar valores pelo
código. Duas práticas observadas como necessárias durante a
investigação de bugs da Sprint 018 foram promovidas a regras formais
de metodologia: feedback visual por padrão para regras de jogo novas,
e centralização de constantes de tuning.
