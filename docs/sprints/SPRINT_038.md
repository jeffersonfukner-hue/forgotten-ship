# SPRINT_038.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 038
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Campo de Força

---

## Objetivo da Sprint

Implementar o Campo de Força: dano contínuo em área ao redor do
player, aplicado em tiques periódicos — item #2 da Lista Consolidada
de Power-ups original, identificado na Sprint 037 como esquecido do
registro de pendências.

---

## Situação Inicial

Ao final da Sprint 037, o Tiro base estava completo (dano, velocidade,
penetração, rajada, alcance) e o Tiro Múltiplo também. O Campo de
Força, apesar de listado desde a v2.2 do `VISAO.md`, nunca havia sido
implementado nem tinha entrada correspondente em `PASSIVE_POWERUPS`.

---

## Problema

Diferente das armas anteriores (Sabre com posição orbital, Sifão com
efeito instantâneo pontual), o Campo de Força precisava de uma decisão
de arquitetura simples mas importante: ele merece ser uma entidade
própria (como `Saber`), ou pode ser resolvido como um cálculo direto no
loop principal, já que sempre fica centrado no player e nunca se move
independentemente dele?

---

## Decisão Arquitetural

### Sem Entidade Própria — Cálculo Direto no Loop Principal

Por decisão do criador do jogo, confirmada antes da implementação: o
Campo de Força não precisa de uma classe própria. Diferente do Sabre
(que orbita, tem múltiplas instâncias e posição própria), o Campo é
sempre um único círculo centrado no player, sem posição independente —
um cálculo de distância direto no `update()` da `GameScene` é
suficiente e mais simples, sem sacrificar corretude.

### Dano em Tique Periódico Único, Não Cooldown por Inimigo

Diferente do Sabre (cooldown de dano individual por inimigo, via
`_hit_cooldowns`), o Campo de Força usa um único cronômetro
(`force_field_timer`) compartilhado — a cada `FORCE_FIELD_TICK_INTERVAL`
segundos (0.5s, conforme já especificado no `VISAO.md`), **todos** os
inimigos dentro do raio recebem dano simultaneamente. Essa diferença
reflete a natureza do power-up: é uma "pulsação de área" (todos afetados
juntos a cada batida), não um "corte por contato individual" como o
Sabre.

### `campo_dano` com Pré-requisito de `campo_area` Nível 1

Mesmo padrão já usado em Sabre e Sifão: o eixo de dano só aparece como
opção depois que a área (que define se o campo existe fisicamente)
atingir nível 1 — evita a possibilidade de escolher "mais dano" numa
arma que ainda não tem raio nenhum para causar efeito algum.

### Ajuste de Balanceamento: Raio Inicial Elevado para 40px

Por decisão do criador do jogo durante o teste, o incremento de
`campo_area` foi ajustado de 20 para 40 pixels por nível — o raio
mínimo perceptível no nível 1 precisava ser maior para o campo ter
presença visual e tática desde a primeira escolha.

---

## Conceitos de Python

- **Cronômetro Único Compartilhado vs. Cronômetro por Item** — a
  escolha entre um único `force_field_timer` (Campo de Força) e um
  dicionário de cooldowns por inimigo (`_hit_cooldowns` do Sabre)
  ilustra como a mesma necessidade geral ("não aplicar dano toda vez
  que colide") pode ter soluções de dado diferentes, dependendo se o
  efeito é "todos afetados juntos periodicamente" ou "cada alvo tem seu
  próprio intervalo".
- **Cálculo de Distância Direto (`pygame.Vector2(...).length()`) sem
  Colisão de Retângulo** — como o Campo de Força é circular por
  natureza (raio, não retângulo), a checagem usa distância euclidiana
  entre centros em vez de `colliderect()`, mais apropriado para uma
  área circular de efeito.

---

## Conceitos de Arquitetura

- **Nem Todo Power-up Precisa de uma Entidade Própria** — decidir se
  um elemento de jogo merece uma classe dedicada depende de suas
  características reais (posição independente, múltiplas instâncias,
  movimento próprio), não de "todo power-up visual deveria ter uma
  entidade" por padrão. O Sabre precisava (órbita, várias lâminas); o
  Campo de Força não (sempre 1, sempre centrado no player).
- **Ajuste de Balanceamento como Parte Legítima do Ciclo de
  Desenvolvimento** — o incremento de área foi corrigido em tempo real
  durante o teste, sem exigir revisão de arquitetura — a estrutura de
  dados (`base_value`/`increment`/`max_level`) já foi desenhada
  justamente para permitir esse tipo de ajuste rápido, sem tocar em
  lógica.

---

## Implementações

### Missão Única — Dados, Dano em Área e Feedback Visual

**Arquivos:** `settings.py`, `player.py`, `game_scene.py`

Adicionados `campo_area` e `campo_dano` em `PASSIVE_POWERUPS`,
agrupados sob a categoria `"campo"`, com pré-requisito de
`campo_dano` sobre `campo_area` nível 1. Criado `force_field_timer` no
`Player`, decrementado a cada frame. Na `GameScene`, adicionado o bloco
de pulso de dano em área (percorre todos os inimigos, aplica dano aos
que estão dentro do raio, a cada tique do cronômetro). Criado
`draw_force_field()` no `Player`, desenhando um círculo translúcido
laranja/vermelho (visualmente distinto do azul já usado no raio de
percepção), reaproveitando o mesmo padrão de `draw_range_indicator`.

---

## Bugs Encontrados

Nenhum bug de código nesta Sprint — apenas um ajuste de balanceamento
(incremento de área de 20 para 40px), identificado e corrigido durante
o próprio teste.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ campo_area, campo_dano)
 ├── CATEGORY_GROUPS (+ os 2 -> "campo")
 ├── UPGRADE_PREREQUISITES (+ campo_dano -> campo_area nivel 1)
 └── FORCE_FIELD_TICK_INTERVAL

Player
 ├── force_field_timer — cronometro compartilhado do proximo tique
 └── draw_force_field() — circulo translucido, visivel so com campo_area > 0

GameScene
 └── update() — a cada FORCE_FIELD_TICK_INTERVAL segundos, aplica campo_dano
      a todos os inimigos dentro de campo_area (distancia euclidiana)
```

Testado: círculo laranja translúcido aparecendo ao redor do player
assim que "Campo de Força - Área" é escolhido pela primeira vez;
inimigos dentro do raio recebendo dano a cada 0.5s; ajuste de raio
inicial (40px) confirmado no painel de debug e visualmente perceptível.

---

## O que o aluno aprendeu

Como decidir se um elemento de jogo precisa de uma entidade própria ou
pode ser resolvido como cálculo direto, baseado em suas características
reais (posição independente, quantidade de instâncias, movimento). Como
um cronômetro único compartilhado difere de cooldowns individuais por
alvo, e quando cada abordagem é apropriada. Como ajustes de
balanceamento fazem parte natural do desenvolvimento, sem exigir
mudança de arquitetura quando a estrutura de dados já foi desenhada
para ser facilmente ajustável.

---

## Próxima Sprint

Encerrada de vez a Lista Consolidada original de Power-ups (todos os 8
itens implementados). Restam as armas de fogo (Phaser Leve, Canhão de
Plasma, Metralhadora de Pulso) como extensão registrada depois da lista
original.

Também pendente: Sprint de UI (tempo de jogo + salas limpas), já
registrada desde a Sprint 037.

---

## Resumo Executivo

Esta Sprint implementa o Campo de Força, encerrando por completo a
Lista Consolidada original de Power-ups do `VISAO.md`. Diferente das
armas anteriores, não precisou de entidade própria — resolvido como
cálculo direto de distância no loop principal, com um único cronômetro
compartilhado aplicando dano periódico a todos os inimigos dentro do
raio simultaneamente. Um ajuste de balanceamento (raio inicial de 40px
em vez de 20px) foi feito durante o próprio teste, sem exigir mudança
estrutural.
