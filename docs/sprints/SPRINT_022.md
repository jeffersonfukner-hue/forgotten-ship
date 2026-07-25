# SPRINT_022.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 022
**Status:** Concluída
**Versão da Arquitetura:** Primeiros Tipos de Inimigo (Terrestre Fraco/Forte)

---

## Objetivo da Sprint

Implementar o primeiro passo da Taxonomia de Tipos de Inimigo
registrada no `VISAO.md`: dois tipos dentro da categoria Terrestre
(fraco e forte), diferindo em HP, tamanho e cor — servindo como base
estrutural para a introdução futura das demais categorias (Aéreo,
Ativo, Residual) e para as Ondas Mistas já planejadas.

---

## Situação Inicial

Ao final da Sprint 021, existia apenas um tipo de inimigo, com
valores fixos (HP, velocidade, tamanho, cor) definidos diretamente no
construtor de `Enemy` — nunca conectados à centralização de tuning
introduzida na Sprint 019, apesar de serem candidatos naturais a isso.

---

## Problema

Sem múltiplos tipos de inimigo, o combate carece de variedade tática
— toda ameaça tem a mesma resistência e aparência, tornando as ondas
posteriores apenas "mais do mesmo", em vez de progressivamente mais
desafiadoras de forma qualitativa. Além disso, os valores do inimigo
fixos no construtor contrariavam a prática já estabelecida (Sprint
019) de centralizar constantes de balanceamento em `settings.py`.

---

## Decisão Arquitetural

### Configuração por Tipo via Dicionário, não Subclasses

Em vez de criar subclasses (`WeakEnemy`, `StrongEnemy`), foi adotado
um único dicionário de configuração (`ENEMY_TYPES`) em `settings.py`,
mapeando cada tipo a seus atributos (HP, velocidade, dimensões, cor).
`Enemy` passou a receber um parâmetro `enemy_type` e ler sua
configuração a partir desse dicionário. Essa abordagem foi escolhida
por não haver, neste momento, diferença de **comportamento** entre os
tipos — apenas de atributos numéricos e visuais — tornando subclasses
um overhead desnecessário. Se tipos futuros (Aéreo, Ativo) exigirem
comportamento distinto, a decisão poderá ser revisitada.

### Onda 1 Fraca, Onda 2 Forte

Como primeiro teste do sistema, a Onda 1 de cada sala continua usando
o tipo `"weak"` (idêntico ao inimigo único anterior), enquanto a Onda
2 (disparada por pressão de tempo, Sprint 021) passou a usar o tipo
`"strong"` — provando a diferenciação sem ainda misturar tipos dentro
da mesma onda (Ondas Mistas, adiado para uma Sprint futura).

---

## Conceitos de Python

- **Dicionário como Tabela de Configuração por Categoria** — `ENEMY_TYPES`
  segue o mesmo padrão já usado para `ROOM_SIZES` (Sprint 009):
  associar uma chave (o tipo) a um conjunto de valores relacionados,
  em vez de replicar `if/elif` para cada variação.
- **Consistência com Prática Já Estabelecida** — a regra de
  centralizar constantes de tuning em `settings.py` (Sprint 019) foi
  seguida de forma consistente ao expandir o sistema de inimigos.

---

## Conceitos de Arquitetura

- **Composição por Configuração vs. Herança** — a escolha de um
  dicionário de configuração em vez de subclasses reflete um princípio
  de design: usar herança quando o comportamento difere, e composição/
  parametrização quando apenas os dados diferem. Antecipar corretamente
  qual abordagem cabe evita tanto uma hierarquia de classes desnecessária
  quanto um acoplamento rígido demais se comportamento distinto for
  necessário no futuro.
- **Extensibilidade por Adição, não Modificação** — adicionar um
  terceiro tipo de inimigo no futuro exigirá apenas uma nova entrada em
  `ENEMY_TYPES`, sem qualquer mudança na classe `Enemy` — uma
  característica desejável de um sistema bem configurável.

---

## Implementações

### Missão 1 — Configuração de Tipos em `settings.py`

**Arquivo:** `settings.py`

Adicionado `ENEMY_TYPES`, com as entradas `"weak"` (HP 20, 14x14,
vermelho) e `"strong"` (HP 40, 18x18, roxo escuro, levemente mais
lento).

### Missão 2 — Enemy Reescrito com Base em Configuração

**Arquivo:** `enemy.py`

`__init__` passou a receber `enemy_type` (padrão `"weak"`) e ler HP,
velocidade, dimensões e cor a partir de `settings.ENEMY_TYPES`.
Reorganizado em seções comentadas (Combate, Atualização, Desenho).

### Missão 3 — Conexão com o Sistema de Ondas

**Arquivo:** `game_scene.py`

`_spawn_wave_enemies()` passou a aceitar um parâmetro `enemy_type`,
repassado ao criar cada `Enemy`. A geração da Onda 2 (disparada por
`next_wave_time`) passou a solicitar explicitamente o tipo `"strong"`.

---

## Estado Atual da Arquitetura

```
settings.py
 └── ENEMY_TYPES = {
        "weak":   {hp, speed, width, height, color},
        "strong": {hp, speed, width, height, color},
     }

Enemy.__init__(x, y, enemy_type="weak")
 └── le hp/speed/width/height/color de settings.ENEMY_TYPES[enemy_type]

GameScene._spawn_wave_enemies(room, count, enemy_type="weak")
 └── repassa o tipo para cada Enemy criado

GameScene.update() — ao disparar a Onda 2, usa enemy_type="strong"
```

Testado visualmente: Onda 1 com inimigos vermelhos pequenos (fraco),
Onda 2 com inimigos roxos maiores (forte), cada um exigindo mais tiros
para eliminar, refletido corretamente na barra de HP individual já
existente desde a Sprint 017.

---

## O que o aluno aprendeu

Como decidir entre herança (subclasses) e composição por configuração
(dicionário de dados) ao introduzir variações de uma entidade — a
decisão correta depende de existir, ou não, diferença de comportamento
entre as variações, não apenas de valores. Como um sistema de tipos
bem configurável permite adicionar novas variações por simples adição
de dados, sem modificar a lógica existente.

---

## Próxima Sprint

Sprint 023 — a definir entre: expansão da taxonomia (tipo Aéreo,
exigindo distinção de arma-alvo), ou início do sistema de drops e
barra de progresso de upgrades, agora que múltiplos tipos de inimigo
existem para diferenciar recompensas.

---

## Resumo Executivo

Esta Sprint introduz os dois primeiros tipos de inimigo do jogo —
Terrestre fraco e forte — usando um dicionário de configuração em vez
de subclasses, por não haver ainda diferença de comportamento entre
eles. A Onda 1 de cada sala usa o tipo fraco, a Onda 2 usa o tipo
forte, provando visualmente e mecanicamente a diferenciação, e
preparando o terreno estrutural para a expansão futura da taxonomia
completa (Aéreo, Ativo, Residual) registrada no `VISAO.md`.
