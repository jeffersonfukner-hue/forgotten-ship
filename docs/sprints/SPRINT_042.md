# SPRINT_042.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 042
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Metralhadora de Pulso (Encerramento do Bloco)

---

## Objetivo da Sprint

Implementar a Metralhadora de Pulso, terceira e última arma de fogo do
backlog — encerrando por completo o Bloco de Power-ups, tanto a Lista
Consolidada original do `VISAO.md` quanto sua extensão de armas de
fogo.

---

## Situação Inicial

Ao final da Sprint 041, Phaser Leve e Canhão de Plasma validaram o
padrão de munição/recarga com 3 eixos cada (capacidade, dano, reload),
ambos usando uma cadência de tiro fixa definida em `settings.py`
(`PHASER_FIRE_RATE`, `PLASMA_FIRE_RATE`).

---

## Problema

A Metralhadora de Pulso precisava de um 4º eixo que as duas armas
anteriores não tinham: cadência de tiro como característica upável da
própria arma, não uma constante fixa — é o diferencial central do
conceito ("metralhadora" = disparo muito rápido, que deveria melhorar
ainda mais com investimento em upgrade).

---

## Decisão Arquitetural

### Cadência como Eixo de `PASSIVE_POWERUPS`, Não Constante Fixa

Diferente de `PHASER_FIRE_RATE` e `PLASMA_FIRE_RATE` (valores únicos em
`settings.py`, nunca mudam com o nível), `pulso_cadencia` foi adicionado
como um eixo completo em `PASSIVE_POWERUPS`, com `base_value` e
`increment` negativo (cada nível reduz ainda mais o intervalo entre
tiros). `confirm_pulso_shot()` lê esse valor via `get_passive_value()`
a cada disparo, em vez de usar uma constante — a única das três armas
de fogo onde a cadência é parte da progressão do jogador.

### Perfil de Balanceamento: Volume Alto, Dano Baixo por Tiro

Coerente com a identidade da arma, a Metralhadora foi calibrada com
carregador grande (20 tiros), dano baixo por tiro (3, o menor das três
armas de fogo), reload rápido (1s) e cadência inicial já agressiva
(0.12s entre tiros, acelerando ainda mais por nível) — o oposto do
perfil do Canhão de Plasma (poucos tiros, dano alto, lento).

### Quinto na Fila de Distribuição de Alvo

Mantendo a progressão já estabelecida (tiro=1º, Sifão=2º, Phaser=3º,
Plasma=4º), a Metralhadora de Pulso mira o **5º mais próximo**, já
nascendo com a correção de distribuição resiliente (`min(4, len-1)`)
aplicada desde o início — nenhuma arma automática do jogo fica muda
por falta de alvos, mesmo com a lista de armas completa.

### Quarta Cor de Projétil, Completando o Conjunto Visual

Projéteis da Metralhadora saem em laranja, completando a paleta visual
de identificação por arma: amarelo (tiro principal), azul claro
(Phaser), roxo (Plasma), laranja (Pulso) — cada arma automática
visualmente distinguível em combate, mesmo com todas ativas
simultaneamente.

---

## Conceitos de Python

- **Valor Calculado por Nível Substituindo Constante Fixa** — o mesmo
  princípio já usado desde o ímã (Sprint 028) foi aplicado agora à
  cadência de disparo: em vez de um número fixo em `settings.py`, o
  valor vem de `get_passive_value()`, tornando-o parte natural da
  progressão do jogador.

---

## Conceitos de Arquitetura

- **Nem Toda Arma do Mesmo "Tipo" Precisa da Mesma Estrutura Exata** —
  Phaser, Plasma e Pulso compartilham o padrão geral de munição/
  recarga, mas a Metralhadora quebrou a simetria ao ter cadência como
  eixo upável — mostra que replicar um padrão não significa copiá-lo
  identicamente; cada arma pode ter sua própria variação sobre a
  estrutura base, conforme sua identidade pedir.
- **Encerramento de um Bloco Planejado desde o Início do Projeto** —
  esta Sprint fecha por completo tanto a Lista Consolidada original de
  8 power-ups (Sprint 038) quanto sua extensão natural de 3 armas de
  fogo (Sprints 040-042) — o backlog de combate do `VISAO.md` está
  agora implementado em sua totalidade original, restando apenas
  refinamentos e blocos temáticos distintos (Chefes, Restauração da
  Nave) para o próximo horizonte de desenvolvimento.

---

## Implementações

### Missão 1 — Dados e Estado de Munição da Metralhadora

**Arquivos:** `settings.py`, `player.py`

Adicionados `pulso_capacidade`, `pulso_dano`, `pulso_reload`,
`pulso_cadencia` em `PASSIVE_POWERUPS`, agrupados sob `"pulso"`, com
pré-requisitos dos três eixos secundários sobre capacidade nível 1.
Criados `pulso_ammo`, `pulso_fire_cooldown`, `pulso_reload_timer`,
`ready_to_fire_pulso()`, `confirm_pulso_shot()` (usando
`get_passive_value("pulso_cadencia")` em vez de constante fixa).
`apply_upgrade()` estendido para encher o carregador da Metralhadora
também.

### Missão 2 — Disparo e Feedback Visual

**Arquivo:** `game_scene.py`

Adicionado o bloco de disparo da Metralhadora de Pulso, mirando o 5º
inimigo mais próximo (com distribuição resiliente já aplicada desde o
início), projéteis em cor laranja. Adicionado feedback de munição/
recarga em `draw_room_and_lives()`, mesmo padrão das duas armas
anteriores.

---

## Bugs Encontrados

Nenhum bug registrado nesta Sprint — testado extensivamente sem
comportamento inesperado.

---

## Estado Atual da Arquitetura

```
settings.py
 └── PASSIVE_POWERUPS (+ pulso_capacidade, pulso_dano, pulso_reload, pulso_cadencia)
      └── pulso_cadencia: unico eixo de cadencia upavel entre as 3 armas de fogo
           (Phaser/Plasma usam PHASER_FIRE_RATE/PLASMA_FIRE_RATE fixos)

Player
 ├── pulso_ammo / pulso_fire_cooldown / pulso_reload_timer
 ├── ready_to_fire_pulso() / confirm_pulso_shot()
 │    └── cadencia lida via get_passive_value("pulso_cadencia"), nao constante
 └── apply_upgrade() — enche carregador da Metralhadora tambem

GameScene
 └── update() — Metralhadora mira o 5o mais proximo, projeteis laranja
```

**Estado do Bloco de Power-ups (completo):**

| Arma/Passivo | Sprint | Eixos |
|---|---|---|
| Tiro (base) | 037 | Dano, Velocidade, Penetração, Rajada, Alcance |
| Tiro Múltiplo | 036 | Diagonal, Paralelo, Quadrantes (exclusivos) |
| Ímã | 028 | Raio de atração |
| Regeneração | 029 | HP/s |
| Sabre Giratório | 031 | Quantidade, Velocidade, Dano |
| Sifão de Energia | 032 | Dano, Conversão |
| Escudo Deflector | 033 | Redução, Barreira, Bloqueio (cumulativos) |
| Campo de Força | 038 | Área, Dano |
| Phaser Leve | 040 | Capacidade, Dano, Reload |
| Canhão de Plasma | 041 | Capacidade, Dano, Reload |
| Metralhadora de Pulso | 042 | Capacidade, Dano, Reload, Cadência |

Testado extensivamente: Metralhadora disparando em cadência
visivelmente mais rápida que Phaser/Plasma; upgrade de "Cadência"
acelerando ainda mais os disparos por nível; carregador de 20 tiros
esvaziando e recarregando rapidamente; projéteis laranja distintos das
demais armas.

---

## O que o aluno aprendeu

Como um eixo de upgrade pode substituir uma constante fixa, mesmo
quando outras armas parecidas usam a constante — a escolha depende da
identidade que aquele atributo específico deveria ter na progressão do
jogador. Como replicar um padrão de código para uma nova arma sem
copiá-lo identicamente, ajustando a estrutura onde a identidade da
arma exige algo diferente. Uma visão de conjunto do que significa
"fechar um bloco planejado" — revisar o backlog original inteiro e
confirmar, item por item, que tudo foi implementado.

---

## Próxima Sprint

Bloco de Power-ups encerrado por completo. Próximos passos possíveis,
a decidir: Bloco de Entidades de Chefes (mini-bosses, boss com fases),
Bloco de Restauração da Nave (mecânica narrativa central), refactor de
`PASSIVE_POWERUPS` → `POWER_UPS` com campo de tipo (já registrado),
ou os bugs/refinamentos de obstáculos e consumíveis ainda pendentes
desde Sprints anteriores.

---

## Resumo Executivo

Esta Sprint implementa a Metralhadora de Pulso, terceira e última arma
de fogo, introduzindo cadência de tiro como eixo upável (diferente do
Phaser e Plasma, que usam constante fixa) — coerente com a identidade
da arma como "a que fica mais rápida com investimento". Com esta
Sprint, o Bloco de Power-ups planejado desde o início do projeto está
100% completo: 11 armas/sistemas implementados, cobrindo a Lista
Consolidada original de 8 itens e a extensão de 3 armas de fogo.
Nenhum bug foi encontrado; o próximo passo é uma decisão em aberto
entre os múltiplos blocos temáticos e refinamentos já registrados no
backlog.
