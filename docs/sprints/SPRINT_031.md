# SPRINT_031.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 031
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Sabre Giratório + Sistema de Slots

---

## Objetivo da Sprint

Implementar o Sabre Giratório (arma com 3 eixos independentes de
upgrade) e, junto dele, o sistema de **limite de armas simultâneas
equipadas** já registrado no `VISAO.md` como "a definir" — decidido
nesta Sprint como 5 slots no teto, crescendo com o nível do jogador
(2 → 3 → 4 → 5), mesclando ativos e passivos sem separação por
enquanto.

---

## Situação Inicial

Ao final da Sprint 030, o sistema de escolha de upgrades funcionava
para itens de eixo único (dano, ímã, regeneração), todos ocupando
"1 opção = 1 upgrade". O Sabre seria o primeiro power-up com múltiplos
eixos independentes (quantidade de lâminas, velocidade de giro, dano
por lâmina) — e também o primeiro caso real de "arma" versus "passivo
de atributo único", expondo a necessidade de um conceito que ainda não
existia: quantos *itens diferentes* (não eixos) o jogador pode ter
equipados ao mesmo tempo.

---

## Problema

Duas perguntas de design precisavam de resposta antes de qualquer
código: (1) os 3 eixos do Sabre contam como 3 power-ups separados para
fins de limite de slots, ou como 1 arma só? (2) upgrades acumulam
livremente pelo tempo todo, ou existe algum tipo de restrição de
progressão entre eixos de uma mesma arma?

---

## Decisão Arquitetural

### Slots Contam por Categoria (Arma), Não por Eixo

Os 3 eixos do Sabre (`sabre_quantidade`, `sabre_velocidade`,
`sabre_dano`) foram agrupados sob uma única categoria lógica
(`"sabre"`) via `settings.CATEGORY_GROUPS` — um dicionário que mapeia
cada chave de eixo para o nome da arma à qual pertence. Uma categoria
conta como "1 slot ocupado" assim que qualquer um de seus eixos atinge
nível > 0; itens sem entrada em `CATEGORY_GROUPS` (ímã, regeneração)
são sua própria categoria — continuam ocupando 1 slot cada, como já
era o caso.

### Slots Crescem com o Nível, Não São Fixos

`POWERUP_SLOTS_BY_LEVEL` é uma lista de pares (nível mínimo, slots),
com o jogador começando com 2 slots (nível 0-4) e subindo até 5
(nível 15+) — decisão de que o primeiro nível do jogo, mais fácil, não
deveria sobrecarregar o jogador com muita escolha simultânea desde o
início. `Player.get_max_powerup_slots()` varre a lista e retorna o
maior valor cujo nível mínimo já foi atingido.

### "Dano do Tiro" Não Ocupa Slot

Por ser a arma inicial do jogo (equivalente ao chicote inicial de
referências do gênero), `"damage"` foi deliberadamente excluído da
contagem de slots — sempre disponível como opção, independente de
quantos slots estão ocupados.

### Pré-requisito Entre Eixos de uma Mesma Arma

Ao testar, ficou evidente um problema de design: como cada eixo do
Sabre é independente, era possível escolher "Velocidade de Giro" ou
"Dano por Lâmina" **antes** de "Quantidade de Lâminas" — resultando em
um upgrade aplicado a uma arma que ainda não existe fisicamente em
jogo (zero lâminas na tela). Corrigido com `UPGRADE_PREREQUISITES`: um
dicionário genérico que mapeia um eixo a `(eixo_do_qual_depende,
nivel_minimo)`. Eixos com pré-requisito não aparecem no pool de
escolha até a condição ser satisfeita. Além de resolver o problema
imediato, isso vira uma ferramenta reutilizável para o objetivo mais
amplo já expresso pelo criador do jogo: liberar features de uma arma
progressivamente, criando sensação de novidade a cada nível, em vez de
tudo disponível de uma vez.

### Sabre Como Entidade Própria, Sincronizada por Quantidade

`Saber` é uma entidade independente (herda de `Entity`, mesmo padrão
de `Enemy`), representando **uma única lâmina**. A `GameScene` mantém
uma lista de instâncias e a sincroniza a cada frame via
`sync_sabers()`, comparando a quantidade atual da lista contra
`get_passive_value("sabre_quantidade")`.

### Recriar Todas as Lâminas ao Mudar de Quantidade (Não Só Adicionar)

Primeira versão de `sync_sabers()` só adicionava lâminas novas mantendo
as antigas com o ângulo original — resultando em espaçamento desigual
ao ganhar uma lâmina (ex: 2 lâminas em 0°/180°, ganhar a 3ª resultava
em 0°/180°/240°, não um triângulo equilátero). Corrigido recriando a
lista inteira a cada mudança de quantidade, redistribuindo os ângulos
uniformemente (`360 / quantidade` entre cada lâmina), preservando
apenas a fase de rotação atual (ângulo da primeira lâmina) para evitar
um "pulo" visual brusco no instante do upgrade.

---

## Conceitos de Python

- **Categoria via Dicionário de Mapeamento (`CATEGORY_GROUPS`)** — em
  vez de codificar "esses 3 eixos são a mesma arma" na lógica, um
  dicionário simples faz esse mapeamento, mantendo a mesma filosofia de
  configuração centralizada já usada em `ENEMY_TYPES` e
  `PASSIVE_POWERUPS`.
- **Compreensão de Conjunto (`set comprehension`)** — `get_equipped_categories()`
  usa `{categoria for key, level in ... if level > 0}`, coletando
  categorias únicas automaticamente (um `set` nunca duplica), sem
  precisar checar manualmente se uma categoria já foi contada.
- **`math.cos()`/`math.sin()` para Posição Orbital** — a posição de
  cada lâmina é calculada a partir de um ângulo em graus, convertido
  para radianos (`math.radians()`), multiplicado pelo raio de órbita —
  técnica clássica de movimento circular em jogos 2D.
- **List Comprehension para Reconstrução Completa de Estado** — em vez
  de mutar a lista de lâminas existente (`append`/`remove`),
  `sync_sabers()` reconstrói a lista inteira numa única expressão
  (`[Saber(...) for i in range(target_count)]`) sempre que a
  quantidade muda — mais simples de raciocinar do que tentar preservar
  parte do estado antigo corretamente.

---

## Conceitos de Arquitetura

- **Categoria como Camada Acima da Chave de Configuração** — o sistema
  de power-ups já tinha uma "chave" (`magnet`, `regen`, etc.) como
  unidade atômica de progressão. Este Sprint introduziu uma segunda
  camada de agrupamento (categoria) por cima dela, sem quebrar nada do
  que já existia — chaves sem grupo continuam se comportando
  exatamente como antes.
- **Pré-requisito como Dado, Não Como Condicional Hardcoded** — em vez
  de escrever `if key == "sabre_velocidade" and player.passive_levels["sabre_quantidade"] < 1: continue`
  diretamente no código, o pré-requisito vira uma entrada de
  configuração (`UPGRADE_PREREQUISITES`) que qualquer eixo futuro pode
  usar, sem exigir uma nova condicional por item.
- **Comentar uma Linha de Controle de Fluxo Sem Ajustar a Indentação é
  um Bug Silencioso** — o bug mais sério desta Sprint (inimigos
  parados) não gerou nenhum erro ou crash: o Python aceitou o código
  perfeitamente válido, só que aninhado no bloco errado. Reforça que
  comentar um `if` não é uma operação neutra — o corpo dele precisa ser
  reavaliado (des-indentado ou removido) para o programa continuar
  fazendo o que fazia antes.

---

## Implementações

### Missão 1 — Dados de Slots, Categorias e Debug Generalizado

**Arquivos:** `settings.py`, `player.py`, `game_scene.py`

Adicionados os 3 eixos do Sabre em `PASSIVE_POWERUPS`, `CATEGORY_GROUPS`
(agrupa os eixos do Sabre sob a categoria `"sabre"`),
`POWERUP_SLOTS_BY_LEVEL` (curva de slots por nível). Criados no
`Player`: `get_category()`, `get_equipped_categories()`,
`get_max_powerup_slots()`, e `get_available_upgrades()` revisado para
respeitar slots e agrupamento. Painel de debug generalizado
(`_build_powerup_lines()`) substituindo os métodos hardcoded por
item.

### Missão 2 — Entidade Saber

**Arquivos novos:** `saber.py`; revisado: `entity.py` (organização de
comentários, fora de padrão desde antes desta Sprint)

Criada a classe `Saber`, com posição orbital calculada por ângulo e
raio configuráveis, e cooldown de dano por inimigo individual
(`_hit_cooldowns`), evitando dano em todo frame de sobreposição.

### Missão 3 — Integração na GameScene

**Arquivo:** `game_scene.py`

Adicionados `sync_sabers()` (cria/recria lâminas conforme o nível de
quantidade muda), chamada de `update()`/dano no loop principal, e
desenho das lâminas em `draw_world()`.

### Ajuste — Pré-requisito Entre Eixos do Sabre

**Arquivos:** `settings.py`, `player.py`

Adicionado `UPGRADE_PREREQUISITES`, condicionando `sabre_velocidade` e
`sabre_dano` a exigirem `sabre_quantidade` nível 1 antes de aparecerem
como opção — motivado por teste real onde o jogador escolheu
velocidade de giro antes de qualquer lâmina existir.

### Correção — Espaçamento das Lâminas ao Mudar de Quantidade

**Arquivo:** `game_scene.py`

`sync_sabers()` revisado para recriar todas as lâminas (recalculando
ângulos uniformemente) a cada mudança de quantidade, em vez de só
adicionar a nova mantendo as antigas em ângulo desatualizado.

---

## Bugs Encontrados

### Bug 1 — Inimigos Paralisados Desde o Início da Partida

**Sintoma:** inimigos nasciam e ficavam completamente parados no lugar
de spawn, mesmo com o jogo rodando normalmente (player se movendo,
tiro automático funcionando). O movimento voltava a funcionar somente
após o jogador escolher o primeiro upgrade do Sabre.

**Causa:** a linha `if not self.player.is_dead:` (que guarda todo o
bloco de movimento de inimigo, colisão com obstáculo, e dano ao
player) foi comentada durante um teste anterior, mas o corpo do bloco
manteve sua indentação original de 12 espaços — fazendo o Python
interpretá-lo como pertencente ao bloco anterior (`if self.sabers:`),
que só passou a ter conteúdo (`self.sabers` não-vazio) após o primeiro
upgrade do Sabre ser escolhido.

**Solução:** descomentada a linha `if not self.player.is_dead:`,
restaurando o bloco ao nível de indentação correto (fora do `if
self.sabers:`).

**Lição Aprendida:** comentar uma linha de controle de fluxo
(`if`/`for`/`while`) nunca é uma operação isolada — o corpo dependente
dela precisa ser reavaliado, porque o Python não detecta "blocos
órfãos"; ele simplesmente aninha o código no escopo válido mais
próximo, resultando em bugs silenciosos sem erro nem crash.

### Bug 2 — Lâminas Desigualmente Espaçadas ao Ganhar Nova Lâmina

**Sintoma:** com 2 lâminas corretamente opostas (0°/180°), ganhar a 3ª
lâmina resultava em ângulos 0°/180°/240° — não um triângulo
equilátero.

**Causa:** `sync_sabers()` original só adicionava a lâmina nova com o
ângulo recalculado (`360/3`), sem atualizar o ângulo das lâminas já
existentes, que permaneciam nos valores calculados para a quantidade
anterior.

**Solução:** `sync_sabers()` revisado para recriar a lista completa de
lâminas sempre que a quantidade muda, redistribuindo todos os ângulos
uniformemente a partir da fase de rotação atual.

---

## Refinamentos Registrados para Sprint Futura

Não implementados nesta Sprint, por não fazerem parte do escopo do
Sabre:

- **Tela de Estatísticas dedicada:** o painel de debug atual mistura
  dados imediatos (HP, slots, level) com histórico acumulado (visitas
  por sala, estatísticas por tipo de inimigo, `visit_history`
  completo) — planejado migrar o histórico para uma estrutura salva
  (possivelmente banco de dados), deixando o painel ao vivo só com o
  essencial, mantendo todos os dados atuais preservados no processo
  (nenhuma informação será perdida, só reorganizada de exibição).
- **Configuração via JSON ao invés de dicionário Python:** registrado
  como tópico de estudo (não decisão de implementação) — dicionários
  Python oferecem comentários inline, type hints e zero código de
  parsing; JSON valeria a pena se surgir necessidade de edição por
  não-programador, hot-reload, ferramenta externa, ou modding. Nenhuma
  dessas pressões existe ainda no projeto; fica como possível Sprint
  de conteúdo didático dentro do Bloco de Refinamento.
- Consumíveis de efeito único, vida extra rara, bugs de obstáculo
  (spawn sobre porta, margem de parede, fixos faltando) — já
  registrados nas Sprints 029/030, seguem na mesma fila.

---

## Estado Atual da Arquitetura

```
settings.py
 ├── PASSIVE_POWERUPS: dict (+ sabre_quantidade, sabre_velocidade, sabre_dano)
 ├── CATEGORY_GROUPS: dict — eixo -> nome da arma (agrupa para contagem de slots)
 ├── UPGRADE_PREREQUISITES: dict — eixo -> (eixo_base, nivel_minimo)
 ├── POWERUP_SLOTS_BY_LEVEL: list[(nivel_minimo, slots)]
 └── SABER_ORBIT_RADIUS / SABER_HIT_COOLDOWN

Player
 ├── get_category(key) / get_equipped_categories()
 ├── get_max_powerup_slots()
 └── get_available_upgrades() — respeita teto, pre-requisito, categoria e slots

Saber (nova entidade, entities/saber.py)
 ├── angle, _hit_cooldowns
 ├── update(dt, player, rotation_speed) — orbita via math.cos/sin
 └── can_hit(enemy) / register_hit(enemy) — cooldown por inimigo

GameScene
 ├── sabers: list[Saber]
 ├── sync_sabers() — recria lista inteira a cada mudanca de quantidade
 └── update() — aplica movimento, colisao e dano do sabre nos inimigos
```

Testado extensivamente ao longo de múltiplas partidas até nível 6:
inimigos se movendo normalmente desde o início; Sabre aparecendo como
3 opções distintas, com velocidade/dano escondidos até quantidade
nível 1; lâminas se espaçando uniformemente (2 = opostas, 3 =
triângulo); dano e velocidade de giro refletindo corretamente cada
upgrade escolhido; slots respeitando a curva por nível.

---

## O que o aluno aprendeu

Como agrupar múltiplos eixos de dados sob uma categoria lógica comum,
sem alterar o comportamento de itens que não pertencem a grupo nenhum.
Como implementar pré-requisitos entre opções de escolha como dado de
configuração, reutilizável para qualquer eixo futuro, em vez de
condicional hardcoded. Como calcular posição orbital com trigonometria
básica (seno e cosseno). Por que comentar uma linha de controle de
fluxo em Python pode causar um bug completamente silencioso, sem
nenhum erro reportado — e por que a indentação em Python não é só
estilo, é a própria estrutura lógica do programa.

---

## Próxima Sprint

Continuação do Bloco de Power-ups — próximo item a definir entre Sifão
de Energia, Phasers (Phaser Leve / Canhão de Plasma / Metralhadora de
Pulso), ou Escudo Deflector.

---

## Resumo Executivo

Esta Sprint implementa o Sabre Giratório, primeira arma com múltiplos
eixos de upgrade independentes, e junto dele o sistema de limite de
slots por categoria (2 a 5, crescendo com o nível), finalmente dando
um número concreto ao "limite de armas simultâneas" que estava pendente
no `VISAO.md`. Também introduz pré-requisitos entre eixos de uma mesma
arma, motivado por teste real — uma ferramenta genérica que poderá
liberar features de qualquer arma progressivamente no futuro. Dois
bugs foram corrigidos: inimigos completamente paralisados por uma
linha de controle de fluxo comentada sem ajuste de indentação
(silencioso, sem erro), e lâminas desigualmente espaçadas ao aumentar
de quantidade. Testado extensivamente em múltiplas partidas até nível
6, sem problemas remanescentes.
