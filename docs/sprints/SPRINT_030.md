# SPRINT_030.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 030
**Status:** Concluída
**Versão da Arquitetura:** Bloco de Power-ups — Sistema de Escolha de Upgrades

---

## Objetivo da Sprint

Substituir o upgrade 100% automático (`apply_automatic_upgrade()`) por
uma tela de escolha entre 3 opções sorteadas a cada level up — mudança
recomendada pela pesquisa de design da Sprint 029 (`VISAO.md` v4.9,
"Referências Externas de Design") como pré-requisito antes de adicionar
novos power-ups automáticos ao jogo.

---

## Situação Inicial

Ao final da Sprint 029, o jogo tinha três upgrades funcionais (dano de
tiro, ímã, regeneração de vida), todos aplicados automaticamente e
simultaneamente a cada level up, sem nenhuma decisão do jogador. O
`GameScene.handle_event()` nunca havia processado input algum — todo
o jogo, até aqui, rodava sem exigir nenhuma tecla além de movimento.

---

## Problema

Introduzir escolha exigia duas mudanças que o jogo nunca tinha feito
antes: capturar input de teclado fora do movimento, e pausar
completamente a simulação (inimigos, projéteis, câmera, cronômetro de
sobrevivência) enquanto aguarda uma decisão do jogador — sem isso, o
jogador poderia levar dano ou mesmo morrer enquanto lê as opções na
tela.

---

## Decisão Arquitetural

### Sinalização via Flag, Não Chamada Direta

Em vez de `add_drop_point()` chamar diretamente uma tela de escolha
(o que misturaria lógica de progressão com lógica de UI/cena),
`Player` apenas seta `level_up_pending = True`. É a `GameScene`, no
próprio `update()`, quem detecta a flag, sorteia as opções e assume o
controle da pausa — mantendo o `Player` sem conhecimento nenhum de
como a escolha é apresentada na tela.

### Pausa Total via Early Return

A pausa foi implementada da forma mais simples possível: quando
`self.upgrade_choices` não é `None`, o método `update()` retorna
imediatamente, antes de processar entidades, projéteis, câmera ou
qualquer cronômetro. Isso garante que absolutamente nada avança
enquanto a escolha está pendente, sem precisar de um novo estado de
jogo (`GameState.PAUSED`) ou máquina de estados formal — a cena
inteira já tinha um único método de atualização central o suficiente
para essa pausa ser só uma guarda no topo dele.

### Único Ponto que Sabe Aplicar Cada Upgrade

`apply_upgrade(key)` centraliza toda a lógica de "o que fazer" com
cada chave de upgrade escolhida — a UI (`handle_event`) só precisa
saber qual tecla virou qual índice, e delega a aplicação real para
esse método único no `Player`. Isso evita que a lógica de upgrade
vaze para dentro da `GameScene`.

### Teclado (1/2/3), Não Mouse

Optado por capturar teclas numéricas em vez de clique de mouse — mais
simples de implementar e testar nesta primeira versão, sem exigir
detecção de hitbox nem cursor. Trade-off registrado: a versão final de
UI (fora de escopo desta Sprint) provavelmente vai querer suporte a
mouse/toque, já que o jogo é pensado para celular.

---

## Conceitos de Python

- **`random.sample()` para Sorteio Sem Repetição** — evita que a
  mesma opção apareça duas vezes entre as 3 sorteadas, sem precisar
  de laço manual removendo itens já escolhidos.
- **Dicionário de Mapeamento Tecla → Índice** — `key_to_index = {pygame.K_1: 0, ...}`
  transforma a tecla física pressionada em posição na lista de opções,
  desacoplando o valor da tecla do índice usado no array.
- **Guarda de Early Return para Pausar um Sistema Inteiro** — em vez
  de espalhar `if not paused:` por dezenas de linhas de `update()`,
  um único `if self.upgrade_choices is not None: return` no topo do
  método pausa tudo que vem depois dele de uma vez.

---

## Conceitos de Arquitetura

- **Sinalização (Flag) Desacopla Quem Detecta de Quem Decide o Quê
  Fazer** — `Player` não sabe (nem precisa saber) que existe uma tela
  de escolha; ele só expõe um fato ("preciso de um upgrade agora") e
  deixa a `GameScene` decidir a apresentação. Esse desacoplamento
  facilita trocar a UI no futuro (ex: mouse em vez de teclado) sem
  tocar em `Player`.
- **Remoção de Código Morto Após Substituição Completa** — assim que
  `apply_upgrade()` provou cobrir os mesmos casos de
  `apply_automatic_upgrade()` (dano + todos os passivos), o método
  antigo foi removido por completo, em vez de deixado comentado ou
  "por precaução" — reduz superfície de manutenção e evita confusão
  sobre qual caminho está realmente ativo.

---

## Implementações

### Missão 1 — Estrutura de Dados do Pool de Upgrades

**Arquivo:** `player.py`

Criados `get_available_upgrades()` (lista upgrades ainda não no teto
de nível), `choose_random_upgrades()` (sorteia até 3, sem repetição,
via `random.sample`), e `apply_upgrade(key)` (único ponto que aplica
de fato cada tipo de upgrade).

### Missão 2 — Pausa e Tela de Escolha

**Arquivos:** `player.py`, `settings.py`, `game_scene.py`

Adicionada a flag `level_up_pending` no `Player` (setada por
`add_drop_point`, no lugar da chamada direta ao upgrade automático).
Criado `UPGRADE_LABELS` em `settings.py` para nomes amigáveis de
exibição. `GameScene` ganhou `upgrade_choices`, detecção da flag em
`update()`, captura de teclas 1/2/3 em `handle_event()`, e
`draw_upgrade_choices()` desenhando um overlay semitransparente com as
3 opções sobre o jogo pausado.

### Missão 3 — Remoção do Upgrade Automático

**Arquivo:** `player.py`

Removido `apply_automatic_upgrade()` por completo, já validado que
`apply_upgrade()` cobre os mesmos casos (dano + todos os power-ups
passivos configurados).

---

## Bugs Encontrados

Nenhum bug registrado nesta Sprint — implementação testada em ciclo
completo (level up → pausa → escolha via teclado → aplicação correta
→ retomada do jogo) sem comportamento inesperado.

---

## Refinamentos Registrados para Sprint Futura (Consumíveis e Obstáculos)

Não implementados nesta Sprint, por decisão explícita de não misturar
com o sistema de escolha em andamento:

- **Nova categoria: Consumíveis de efeito único** — diferente dos
  power-ups passivos (que acumulam nível permanente), consumíveis têm
  efeito só no momento em que são coletados, sem persistir. Primeiro
  caso de uso: o drop do obstáculo destrutível, ainda pendente de
  definição, cogitado como um entre: recarga instantânea de energia
  (ex: 50%), "puxão total" (recolhe todas as gemas da sala de uma
  vez), sorteado aleatoriamente entre os consumíveis disponíveis.
- **Vida extra como drop raro:** aumenta `max_lives` permanentemente
  (ex: 5 → 6 → 7), com taxa de drop bem menor que os demais
  consumíveis — introduz o conceito de **raridade ponderada** entre
  itens do mesmo pool (ex: a cada 3 drops comuns, 1 chance do raro),
  mecanismo de peso ainda em aberto.
- Bugs/refinamentos de obstáculos já registrados na Sprint 029 (spawn
  sobre porta, margem de parede, fixos faltando nas Salas 2 e 3)
  continuam pendentes, mesma fila de espera.

---

## Estado Atual da Arquitetura

```
Player
 ├── level_up_pending: bool — sinaliza que GameScene deve pausar e sortear
 ├── get_available_upgrades() — filtra por max_level ja atingido
 ├── choose_random_upgrades(count=3) — random.sample, sem repeticao
 └── apply_upgrade(key) — unico ponto que aplica cada upgrade (damage ou passivo)

settings.py
 └── UPGRADE_LABELS: dict — chave -> texto amigavel para exibicao

GameScene
 ├── upgrade_choices: list[str] | None — None = jogo roda normal, lista = pausado
 ├── update() — guarda de early return quando upgrade_choices ativo
 ├── handle_event() — captura teclas 1/2/3, aplica escolha via player.apply_upgrade()
 └── draw_upgrade_choices() — overlay semitransparente com as 3 opcoes
```

Testado extensivamente: level up pausando o jogo por completo (sem
dano, sem movimento de inimigo, sem avanço de cronômetro); as 3 opções
exibidas corretamente com nomes amigáveis; escolha via tecla aplicando
o upgrade certo (confirmado no painel de debug); jogo retomando
normalmente após a escolha; power-ups no teto de nível deixando de
aparecer como opção.

---

## O que o aluno aprendeu

Como desacoplar "detectar que algo precisa acontecer" de "decidir como
apresentar isso ao jogador", usando uma flag simples em vez de uma
chamada direta entre sistemas que não deveriam se conhecer. Como
pausar um sistema inteiro com uma única guarda de early return, em vez
de espalhar verificações de estado por todo o código. Como remover
código morto com confiança, uma vez que o substituto já foi validado
cobrindo os mesmos casos.

---

## Próxima Sprint

Bloco de Power-ups continua: implementar o próximo item da Lista
Consolidada (Sifão de Energia, Sabre Giratório, ou Phasers) — agora já
se conectando de verdade ao sistema de escolha real, em vez de upgrade
automático.

Refinamentos registrados (consumíveis, vida extra rara, bugs/
refinamentos de obstáculos) seguem na fila para uma Sprint futura
dedicada de Refinamento.

---

## Resumo Executivo

Esta Sprint substitui o upgrade 100% automático por uma tela de
escolha entre 3 opções no level up, recomendação direta da pesquisa de
design da Sprint 029. A implementação introduziu pausa total do jogo
via early return, captura de input de teclado (primeira vez no
projeto), e um ponto único de aplicação de upgrades desacoplado da
lógica de progressão. O upgrade automático antigo foi removido por
completo após validação. Registrados para Sprint futura: uma nova
categoria de itens (consumíveis de efeito único, incluindo vida extra
rara com raridade ponderada) e os bugs/refinamentos de obstáculos já
pendentes desde a Sprint 029.
