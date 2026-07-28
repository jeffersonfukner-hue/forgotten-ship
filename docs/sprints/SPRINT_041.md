# SPRINT_041.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 041
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Canhão de Plasma + Correção de Distribuição de Alvo

---

## Objetivo da Sprint

Implementar o Canhão de Plasma, segunda arma de fogo (carregador maior,
dano concentrado, reload mais lento) — e corrigir um problema de
gameplay identificado durante o teste: armas automáticas ficavam mudas
quando não havia inimigos suficientes para alcançar seu índice de
mira.

---

## Situação Inicial

Ao final da Sprint 040, o Phaser Leve validou o padrão de munição/
recarga, mirando o 3º inimigo mais próximo. Sifão de Energia (2º mais
próximo) e Phaser Leve (3º mais próximo) exigiam, respectivamente, ao
menos 2 e 3 inimigos no raio para sequer disparar.

---

## Problema

Relatado pelo criador do jogo: com poucos inimigos (especialmente
fortes, quando concentrar fogo mais importa), Sifão e Phaser ficavam
completamente inativos por falta de um alvo "exclusivo" no índice
desejado — exatamente o cenário onde essas armas deveriam ajudar mais,
não menos.

---

## Decisão Arquitetural

### Mira o Mais Distante Disponível, Não Falha por Índice Inexistente

Corrigido antes de implementar o Canhão de Plasma (para ele já nascer
correto): em vez de checar `len(ordered_enemies) >= N` como condição
para disparar, cada arma agora usa `ordered_enemies[min(N-1, len(ordered_enemies) - 1)]`
— se há inimigos suficientes, mira exatamente o N-ésimo desejado; se
há menos, mira o mais distante que existir. Com 1 único inimigo na
sala, todas as armas automáticas convergem fogo nele; com 2, o Sifão
mira o 2º e o Phaser (que queria o 3º) também mira o 2º, por falta de
um 3º.

### Canhão de Plasma: Quarto na Fila de Distribuição

Mantendo a progressão já estabelecida (tiro=1º, Sifão=2º, Phaser=3º),
o Canhão de Plasma mira o **4º mais próximo** — cada arma automática
continua tendo presença tática distinta, agora sem nenhuma ficar muda
por escassez de alvos.

### Números de Balanceamento: Dano Concentrado, Cadência Lenta

Por decisão do criador do jogo, o Canhão de Plasma foi calibrado para
o papel de "dano concentrado contra ameaças fortes": carregador de 12
tiros (vs. 5 do Phaser), dano inicial de 15 por tiro (vs. 5 do Phaser),
reload de 3.5s (vs. 2s do Phaser), cadência de 0.6s entre tiros (vs.
0.3s do Phaser) — um perfil deliberadamente mais lento e pesado,
coerente com a descrição do `VISAO.md` ("especialmente útil contra
chefões").

### Cor de Projétil Própria

Seguindo o padrão já estabelecido com o Phaser Leve (azul claro), o
Canhão de Plasma dispara projéteis roxo/lilás — cada arma automática
agora tem identidade visual distinta em combate (amarelo, azul, roxo).

---

## Conceitos de Python

- **`min(desejado, disponível - 1)` para Buscar Índice "o Melhor
  Possível" em uma Lista** — em vez de falhar quando o índice desejado
  não existe, `min()` garante que o índice usado nunca ultrapasse o
  último elemento disponível, degradando graciosamente para "o mais
  distante que existir" em vez de "nenhum".

---

## Conceitos de Arquitetura

- **Corrigir a Base Antes de Replicar o Padrão** — o bug de "arma muda
  por falta de alvo" foi corrigido em Sifão e Phaser antes de
  implementar o Canhão de Plasma, garantindo que a nova arma já
  nascesse com o comportamento correto, em vez de repetir o mesmo erro
  uma terceira vez e precisar de três correções separadas depois.
- **Distinção de Papel Tático por Números, Não por Mecânica Nova** —
  Phaser e Plasma compartilham exatamente a mesma estrutura de código
  (munição, cooldown, reload) — a diferença de "arma ágil contra
  hordas" vs. "arma pesada contra ameaças concentradas" vem inteiramente
  dos valores de configuração, não de lógica duplicada ou especial.

---

## Implementações

### Correção — Distribuição de Alvo Resiliente a Poucos Inimigos

**Arquivo:** `game_scene.py`

Ajustados os blocos de disparo do Sifão de Energia e do Phaser Leve
para usar `ordered_enemies[min(N-1, len(ordered_enemies) - 1)]` em vez
de exigir uma quantidade mínima de inimigos para disparar.

### Missão 1 — Dados e Estado de Munição do Plasma

**Arquivos:** `settings.py`, `player.py`

Adicionados `plasma_capacidade`, `plasma_dano`, `plasma_reload` em
`PASSIVE_POWERUPS`, agrupados sob `"plasma"`, com pré-requisitos de
dano e reload sobre capacidade nível 1. Criados `plasma_ammo`,
`plasma_fire_cooldown`, `plasma_reload_timer`, `ready_to_fire_plasma()`,
`confirm_plasma_shot()` — espelhando exatamente a estrutura já criada
para o Phaser Leve. `apply_upgrade()` estendido para encher o
carregador do Plasma também.

### Missão 2 — Disparo e Feedback Visual

**Arquivo:** `game_scene.py`

Adicionado o bloco de disparo do Canhão de Plasma, mirando o 4º
inimigo mais próximo (já com a correção de distribuição resiliente),
projéteis em cor roxo/lilás. Adicionado feedback de munição/recarga em
`draw_room_and_lives()`, mesmo padrão do Phaser.

---

## Bugs Encontrados

### Bug — Armas Automáticas Mudas com Poucos Inimigos no Raio

**Sintoma:** Sifão de Energia e Phaser Leve paravam de disparar
completamente quando a quantidade de inimigos no raio caía abaixo do
índice que cada um mirava (2 e 3, respectivamente) — justamente o
cenário de poucos inimigos fortes, onde concentrar fogo seria mais
valioso.

**Causa:** a condição de disparo checava `len(ordered_enemies) >= N`
como pré-requisito, em vez de degradar para o alvo mais distante
disponível quando o índice exato não existia.

**Solução:** substituída a checagem de quantidade mínima por
`ordered_enemies[min(N-1, len(ordered_enemies) - 1)]`, garantindo que
qualquer arma automática sempre dispare enquanto houver ao menos 1
inimigo no raio.

**Lição Aprendida:** um sistema de distribuição de alvo que funciona
bem com muitos alvos disponíveis pode falhar silenciosamente (sem
erro, só "não faz nada") justamente no cenário oposto — poucos alvos —
que costuma ser o mais crítico. Vale testar deliberadamente os extremos
(muitos alvos, poucos alvos, nenhum alvo) de qualquer lógica de mira.

---

## Refinamentos Registrados para Sprint Futura

### Refactor: `PASSIVE_POWERUPS` → `POWER_UPS` com Campo `"type"`

Ideia proposta pelo criador do jogo: renomear a estrutura central de
configuração e adicionar um campo `"type": "active"/"passive"` a cada
entrada, preparando terreno para estatísticas de eficiência por tipo
de power-up escolhido — e uma futura área de simulação/comparação de
builds, possivelmente como feature paga do jogo. Não implementado
nesta Sprint por tocar `settings.py`, `player.py` e `game_scene.py`
em múltiplos pontos simultaneamente — registrado como Sprint dedicada.

### Revisão de Comentários em `settings.py`

Identificado que vários comentários do arquivo ficaram desatualizados
conforme ele cresceu ao longo das Sprints — a fazer junto do refactor
acima, já que renomear a estrutura central exige revisar cada bloco de
qualquer forma.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS (+ plasma_capacidade, plasma_dano, plasma_reload)
 ├── CATEGORY_GROUPS (+ os 3 -> "plasma")
 ├── UPGRADE_PREREQUISITES (+ dano e reload -> capacidade nivel 1)
 └── PLASMA_FIRE_RATE

Player
 ├── plasma_ammo / plasma_fire_cooldown / plasma_reload_timer
 ├── ready_to_fire_plasma() / confirm_plasma_shot() — espelha o Phaser
 └── apply_upgrade() — enche carregador do Plasma tambem

GameScene
 └── update() — Sifao/Phaser/Plasma usam min(N-1, len-1) para mirar
      o mais distante disponivel, nunca ficando mudos por falta de alvo
```

Testado extensivamente: Canhão de Plasma disparando com carregador de
12, dano bem mais alto que o Phaser, cadência mais lenta, reload mais
demorado, projéteis roxos; Sifão, Phaser e Plasma continuando a disparar
mesmo com a horda reduzida a 1-2 inimigos, concentrando fogo em vez de
ficarem mudos.

---

## O que o aluno aprendeu

Como um padrão de mira que funciona bem no caso comum (muitos alvos)
pode falhar silenciosamente no caso extremo (poucos alvos) — e por que
vale testar deliberadamente os limites de qualquer lógica de seleção.
Como usar `min()` para degradar graciosamente um índice desejado para
o melhor disponível, em vez de simplesmente falhar. Como replicar uma
estrutura já validada (Phaser) para uma nova arma (Plasma) variando
apenas os números de configuração, sem duplicar lógica.

---

## Próxima Sprint

Metralhadora de Pulso — terceira e última arma de fogo do backlog
(cadência muito alta, carregador intermediário), encerrando por
completo o bloco de armas de fogo.

Também registrado: refactor de `PASSIVE_POWERUPS` → `POWER_UPS` com
campo de tipo, e revisão de comentários de `settings.py`.

---

## Resumo Executivo

Esta Sprint implementa o Canhão de Plasma, segunda arma de fogo,
reaproveitando integralmente a estrutura de munição/recarga validada
no Phaser Leve — a diferença de papel tático (dano concentrado vs.
ágil) vem inteiramente de configuração, não de lógica nova. Um bug
real foi identificado e corrigido antes da implementação: armas
automáticas ficavam mudas quando havia poucos inimigos no raio,
justamente no cenário onde concentrar fogo seria mais valioso —
corrigido com uma técnica de degradação graciosa de índice
(`min(desejado, disponível-1)`), aplicada retroativamente ao Sifão e
Phaser antes do Canhão de Plasma nascer com o comportamento correto.
Registrado um refactor futuro significativo: renomear a estrutura
central de power-ups e adicionar classificação por tipo, preparando
terreno para estatísticas de eficiência e uma futura ferramenta de
comparação de builds.
