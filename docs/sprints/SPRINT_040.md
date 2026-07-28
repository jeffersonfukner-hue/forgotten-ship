# SPRINT_040.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 040
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Phaser Leve

---

## Objetivo da Sprint

Implementar o Phaser Leve, a primeira das três armas de fogo do
backlog original — introduzindo o conceito de munição limitada e
recarga, nunca usado em nenhuma arma anterior do jogo.

---

## Situação Inicial

Ao final da Sprint 039, a Lista Consolidada original de Power-ups
estava 100% completa (8 de 8 itens). Restavam apenas as armas de fogo
(Phaser Leve, Canhão de Plasma, Metralhadora de Pulso) como extensão
do backlog. Por decisão do criador do jogo, a implementação seria
feita uma arma por vez, começando pelo Phaser Leve, para validar o
conceito de munição/recarga antes de replicá-lo.

---

## Problema

Nenhuma arma anterior precisou gerenciar um estado de "recurso
consumível que se esgota e precisa de tempo para recarregar" — Sabre,
Sifão e Campo de Força disparam indefinidamente, limitados apenas por
cooldown de tempo entre ações. O Phaser Leve precisava de: capacidade
de carregador, cadência entre tiros dentro do mesmo carregador, e um
tempo de recarga distinto do cooldown normal.

---

## Decisão Arquitetural

### Mira o 3º Inimigo Mais Próximo, Mantendo a Distribuição de Alvo

Seguindo o padrão já estabelecido (tiro principal mira o 1º mais
próximo, Sifão mira o 2º), o Phaser Leve mira o **3º mais próximo**,
via `get_enemies_by_distance()[2]` — evita sobreposição de alvo entre
as três armas automáticas, cada uma com presença própria em combate.

### Três Estados Distintos de Munição

`ready_to_fire_phaser()` verifica três condições simultâneas: munição
disponível (`phaser_ammo > 0`), cadência de tiro liberada
(`phaser_fire_cooldown <= 0`), e fora do período de recarga
(`phaser_reload_timer <= 0`). Ao disparar o último tiro do carregador,
`confirm_phaser_shot()` automaticamente inicia o cronômetro de
recarga; ao zerar esse cronômetro, o `update()` do `Player` recarrega
o carregador por completo.

### Carregador Cheio ao Adquirir ou Upar Capacidade

Por decisão explícita, `apply_upgrade()` foi ajustado para, sempre que
`phaser_capacidade` sobe de nível (incluindo a primeira escolha da
arma), encher o carregador imediatamente e zerar qualquer recarga em
andamento — evita a experiência ruim de escolher "mais capacidade" e a
arma continuar com a munição antiga (menor) até o próximo reload
natural.

### Pré-requisito de Dano e Reload sobre Capacidade

Mesmo padrão já usado em todas as armas com múltiplos eixos: `phaser_dano`
e `phaser_reload` só aparecem como opção depois que `phaser_capacidade`
atingir nível 1 — sem capacidade, a arma não existe fisicamente, então
upar dano ou velocidade de recarga não teria efeito perceptível.

### Cor do Projétil Parametrizada, Não Mais Fixa

Ao testar, ficou evidente que o Phaser Leve precisava de identidade
visual própria — `Projectile` tinha a cor do círculo hardcoded
(amarelo). Adicionado o parâmetro `color` com valor padrão igual à cor
antiga (zero regressão para o tiro principal), permitindo o Phaser
Leve disparar projéteis azul claro, visualmente distinguíveis em
combate.

---

## Conceitos de Python

- **Múltiplas Condições Booleanas Combinadas em um Método de Consulta**
  — `ready_to_fire_phaser()` combina três verificações com `and`,
  centralizando a "regra completa" de quando a arma pode disparar em
  um único ponto, em vez de espalhar as três checagens no código
  chamador.
- **Efeito Colateral Condicional Dentro de um Método Genérico** —
  `apply_upgrade()` continua sendo o ponto único de aplicação de
  upgrades, mas ganhou uma checagem extra (`if key == "phaser_capacidade"`)
  para um efeito colateral específico dessa arma — mostra como um
  método genérico pode acomodar uma regra especial sem perder sua
  função central.
- **Parâmetro com Valor Padrão para Introduzir Variação sem Quebrar
  Quem Já Chama** — `color: tuple = (255, 220, 80)` no `Projectile`
  segue o mesmo padrão já usado para `speed` na Sprint 037: adicionar
  capacidade nova sem exigir que código existente seja atualizado.

---

## Conceitos de Arquitetura

- **Recurso Consumível com Recarga como Padrão Distinto de Cooldown
  Simples** — cooldown de tempo (Sifão, Campo de Força) e munição com
  recarga (Phaser Leve) parecem similares na superfície ("esperar antes
  de agir de novo"), mas têm semânticas diferentes: cooldown é sempre
  previsível e constante; munição depende de quantos tiros já foram
  disparados, criando um ritmo de "rajada + pausa" em vez de "cadência
  uniforme".
- **Efeito Colateral de Upgrade Corrigindo uma Experiência Ruim
  Potencial** — encher o carregador ao upar capacidade não era
  estritamente necessário para a lógica funcionar (o próximo reload
  natural resolveria sozinho), mas evita um momento de confusão ("por
  que meu carregador não ficou maior?") — um exemplo de decisão de
  design motivada pela experiência do jogador, não só pela corretude
  técnica.

---

## Implementações

### Missão 1 — Dados e Estado de Munição

**Arquivos:** `settings.py`, `player.py`

Adicionados `phaser_capacidade`, `phaser_dano`, `phaser_reload` em
`PASSIVE_POWERUPS`, agrupados sob `"phaser"`, com pré-requisitos de
dano e reload sobre capacidade nível 1. Criados `phaser_ammo`,
`phaser_fire_cooldown`, `phaser_reload_timer` no `Player`, além de
`ready_to_fire_phaser()` e `confirm_phaser_shot()`. `apply_upgrade()`
ajustado para encher o carregador ao upar `phaser_capacidade`.

### Missão 2 — Disparo e Feedback Visual de Munição

**Arquivo:** `game_scene.py`

Adicionado o bloco de disparo do Phaser Leve no `update()`, mirando o
3º inimigo mais próximo via `get_enemies_by_distance()`. Adicionado
feedback de munição/recarga em `draw_room_and_lives()` — mostra
"Phaser: N/capacidade" ou "Phaser: recarregando..." conforme o estado,
só quando a arma já foi adquirida.

### Ajuste — Cor de Projétil Diferenciada

**Arquivos:** `projectile.py`, `game_scene.py`

`Projectile` ganhou o parâmetro `color`, com o tiro principal mantendo
amarelo (valor padrão) e o Phaser Leve disparando em azul claro.

---

## Bugs Encontrados

Nenhum bug de código nesta Sprint — o único ajuste foi de identidade
visual (cor do projétil), levantado durante o teste e corrigido em
seguida.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ phaser_capacidade, phaser_dano, phaser_reload)
 ├── CATEGORY_GROUPS (+ os 3 -> "phaser")
 ├── UPGRADE_PREREQUISITES (+ dano e reload -> capacidade nivel 1)
 └── PHASER_FIRE_RATE

Player
 ├── phaser_ammo / phaser_fire_cooldown / phaser_reload_timer
 ├── ready_to_fire_phaser() — municao > 0 AND cadencia liberada AND fora de reload
 ├── confirm_phaser_shot() — consome municao, inicia reload se zerar
 └── apply_upgrade() — enche carregador ao upar phaser_capacidade

Projectile
 └── __init__(..., color=(255, 220, 80)) — cor parametrizavel, sem regressao

GameScene
 ├── update() — dispara Phaser mirando o 3o mais proximo, cor azul claro
 └── draw_room_and_lives() — feedback de municao/recarga, condicional a arma adquirida
```

Testado extensivamente: Phaser Leve nascendo com carregador cheio ao
ser escolhido pela primeira vez; munição diminuindo visivelmente no
HUD a cada tiro; entrando em "recarregando..." ao esvaziar; carregador
voltando cheio após o tempo de reload; dano e velocidade de recarga
aparecendo como opção só após capacidade nível 1; projétil do Phaser
visualmente distinto (azul claro) do tiro principal (amarelo).

---

## O que o aluno aprendeu

Como modelar um recurso consumível com recarga, distinto de um simples
cooldown de tempo — a diferença de ritmo que cada padrão cria na
jogabilidade. Como um método central de aplicação de upgrades pode
acomodar um efeito colateral específico de uma arma sem perder sua
função genérica. Como parametrizar um valor antes hardcoded (cor)
usando valor padrão, permitindo variação sem quebrar código existente.
Como pequenos ajustes de experiência (encher o carregador ao upar
capacidade) podem ser tão importantes quanto a lógica central para a
sensação de progressão fazer sentido.

---

## Próxima Sprint

Canhão de Plasma — segunda arma de fogo, reaproveitando o padrão de
munição/recarga validado nesta Sprint (carregador maior, dano mais
alto, reload mais lento).

---

## Resumo Executivo

Esta Sprint implementa o Phaser Leve, validando o conceito de munição
limitada e recarga pela primeira vez no jogo — um padrão distinto de
cooldown simples, com estado de três condições (munição, cadência,
recarga) centralizado em `ready_to_fire_phaser()`. A arma mira o 3º
inimigo mais próximo, mantendo a distribuição de alvo já usada pelas
demais armas automáticas. Um ajuste de experiência (encher o
carregador ao upar capacidade) e um ajuste visual (cor de projétil
parametrizada, Phaser em azul claro) completaram a implementação, sem
bugs de lógica.
