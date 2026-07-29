# SPRINT_046A.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 046A (Bloco de Entidades de Chefes — Parte 1 de 5)
**Status:** Concluída
**Versão da Arquitetura:** Sistema de Ondas com Acúmulo

---

## Objetivo da Sprint

Implementar a mecânica base de ondas sequenciais dentro de uma visita
de sala: cada onda tem um countdown próprio para a **próxima** onda
começar (não para a atual acabar); se o jogador demorar, a onda
seguinte soma-se aos inimigos remanescentes, nunca substitui nem
espera limpar tudo. Primeira das 5 Sprints planejadas para o Bloco de
Entidades de Chefes, deliberadamente sem nenhum chefe ainda.

---

## Situação Inicial

Ao final da Sprint 045, a sala tinha reabastecimento gradual (gatilho
de 20%) e piso de inimigos crescente por reentrada, mas nenhuma noção
de "onda" — era um piso contínuo único, sem estrutura sequencial.

---

## Problema

Introduzir "ondas" exigia um comportamento específico e não óbvio:
diferente de sistemas de onda tradicionais (onde a próxima só começa
quando a atual é derrotada), aqui o design pedia o oposto — a próxima
onda chega de qualquer forma após um tempo fixo, **somando-se** ao que
sobrou da anterior. Isso cria pressão real para não procrastinar,
mesmo sem depender de eliminar todos os inimigos.

---

## Decisão Arquitetural

### Onda Soma, Nunca Substitui

`current_wave` e `wave_timer` foram adicionados a `Room`. Quando
`wave_timer` chega a zero, `_spawn_wave_enemies()` é chamado somando
`HORDE_ENEMIES_PER_VISIT` novos inimigos aos já vivos — não há remoção
nem reset dos que sobraram da onda anterior.

### Sistema de Ondas Roda em Paralelo ao Critério de Vitória Existente,
Não o Substitui Ainda

Por decisão deliberada, esta Sprint não mexeu em como a sala é
considerada "limpa" (`ROOM_SURVIVAL_DURATION`, ainda o mesmo critério
de sempre). O sistema de ondas roda seu próprio relógio ao lado do
relógio de sobrevivência — a integração completa (sala só limpa após
todas as ondas + chefão) fica para a Sprint E.

### Bug de Acoplamento Descoberto no Teste: Dois Relógios Coincidentes

Ao testar, a 3ª onda não aparecia — porque o gate do sistema de ondas
incluía `not self.room.time_expired`, e `ROOM_SURVIVAL_DURATION` (30s)
por coincidência expirava exatamente quando a 2ª onda (`WAVE_DURATION`
15s × 2) deveria dar lugar à 3ª. Não era um bug de lógica errada, era
dois sistemas independentes compartilhando timing coincidente demais
para serem distinguidos no teste. Resolvido temporariamente aumentando
`ROOM_SURVIVAL_DURATION` para 90s — suficiente para observar 3+ ondas
livremente antes do critério de vitória antigo interferir. Mantido em
90s por decisão do criador do jogo, não revertido ao valor original.

### Duração Total por Sala Inspirada em Referências de Mercado — Registrado
para a Sprint E

Durante o teste, o criador do jogo trouxe uma referência de outros
jogos do gênero: duração total da sala/nível de **~5 minutos**,
dividida **proporcionalmente** entre as ondas (ex: onda 1 = 20%, onda 2
= 30%, onda 3 = 50% — os percentuais exatos ainda a ajustar por
sensação de jogo, não fixos). Isso refina a estrutura de "~5 minutos"
que já constava no `VISAO.md` desde a Estrutura de Boss Rush original,
tornando-a concreta. Registrado para implementação na Sprint E, quando
a duração de cada onda deixará de ser uniforme (`WAVE_DURATION` fixo)
e passará a ser calculada como fração do tempo total da sala.

---

## Conceitos de Python

- **Cronômetro Regressivo Reiniciado ao Disparar** — `wave_timer -= dt`
  seguido de reset para `WAVE_DURATION` ao chegar a zero é o mesmo
  padrão já usado em cooldowns de armas, aplicado agora ao ritmo de
  progressão de onda.

---

## Conceitos de Arquitetura

- **Dois Sistemas Independentes Podem Parecer Acoplados por
  Coincidência de Timing** — o bug da 3ª onda não vinha de uma
  dependência real entre o sistema de ondas e o critério de
  sobrevivência antigo, mas de os dois relógios coincidirem
  numericamente no teste. Isso reforça a importância de isolar
  variáveis ao testar um sistema novo — usar valores bem distintos
  (90s vs. 15s) evita confundir coincidência com dependência real.
- **Implementar a Mecânica Nova ao Lado da Antiga, Sem Substituir
  Ainda** — rodar o sistema de ondas em paralelo ao critério de
  vitória existente, sem integrá-los, permitiu validar o
  comportamento de acúmulo isoladamente antes de comprometer a
  condição de vitória da sala (que já funcionava e já havia sido
  testada extensivamente antes).

---

## Implementações

### Missão Única — Ondas com Acúmulo

**Arquivos:** `settings.py`, `room.py`, `game_scene.py`

Adicionada `WAVE_DURATION` (15s). Criados `current_wave` e
`wave_timer` em `Room`, reiniciados a cada `spawn_horde()`. Bloco novo
no `update()` da `GameScene`: decrementa `wave_timer`, e ao zerar,
incrementa `current_wave`, reinicia o timer, e soma
`HORDE_ENEMIES_PER_VISIT` novos inimigos via `_spawn_wave_enemies()`.
Adicionado `_build_wave_line()` ao painel de debug, mostrando onda
atual e countdown para a próxima.

### Refinamento — Padronização de `room.py`

**Arquivo:** `systems/room.py`

Adicionada docstring de classe — o restante do arquivo já estava
organizado em seções com cabeçalho, sem necessidade de mudança
adicional.

---

## Bugs Encontrados

Nenhum bug de lógica — o problema encontrado foi de acoplamento
acidental de timing entre dois sistemas independentes (detalhado
acima), não um erro de implementação.

---

## Refinamentos Registrados para Sprint Futura

### Duração Proporcional por Onda (Sprint E)

Duração total da sala/nível ~5 minutos, dividida proporcionalmente
entre as ondas (percentuais a ajustar, ex: 20/30/50), substituindo o
`WAVE_DURATION` fixo atual — refina o que já constava no `VISAO.md`
desde a Estrutura de Boss Rush.

---

## Estado Atual da Arquitetura

```
settings.py
 └── WAVE_DURATION (15s, valor de referencia inicial)

Room
 ├── current_wave: int — reinicia a cada spawn_horde()
 └── wave_timer: float — countdown ate a PROXIMA onda ser somada

GameScene
 └── update() — decrementa wave_timer; ao zerar, soma HORDE_ENEMIES_PER_VISIT
      novos inimigos aos remanescentes, sem esperar limpar a onda atual
```

Testado: com `ROOM_SURVIVAL_DURATION` temporariamente em 90s (mantido
assim por decisão do criador do jogo), múltiplas ondas se acumulando
corretamente — inimigos remanescentes de uma onda somados aos da
próxima, sem espera e sem substituição.

---

## O que o aluno aprendeu

Como implementar uma mecânica de acúmulo (onda soma, não substitui),
distinta do padrão tradicional de "espera limpar para avançar". Como
identificar que um bug aparente pode ser coincidência de timing entre
dois sistemas independentes, não uma dependência real — e como isolar
essa possibilidade usando valores de teste bem distintos. Como
implementar uma mecânica nova rodando ao lado de uma antiga, sem
comprometer o que já funcionava, antes de integrá-las de vez.

---

## Próxima Sprint

Sprint B do Bloco de Entidades de Chefes: Mini-chefe (~300 HP, escala
por reentrada e por nível de sala; drop de 3 upgrades garantidos +
puxão automático de gemas ao morrer).

---

## Resumo Executivo

Esta Sprint implementa a mecânica base de ondas com acúmulo — cada onda
soma inimigos aos remanescentes após um tempo fixo, sem esperar a
anterior ser derrotada. Rodando deliberadamente em paralelo ao
critério de vitória existente (não integrado ainda), a Sprint permitiu
validar isoladamente o comportamento de acúmulo. Um aparente bug (3ª
onda não aparecendo) revelou-se coincidência de timing entre dois
relógios independentes, resolvido ajustando a duração de teste. O
criador do jogo trouxe uma referência de mercado (duração total ~5
minutos, dividida proporcionalmente entre ondas), registrada para
implementação na Sprint E, quando o sistema de ondas será integrado de
vez ao critério de vitória da sala.
