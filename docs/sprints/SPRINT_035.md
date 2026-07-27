# SPRINT_035.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 035
**Status:** Concluída
**Versão da Arquitetura:** HUD — Pontuação Fixa em Tela

---

## Objetivo da Sprint

Adicionar um elemento de HUD permanente mostrando a pontuação da sala
atual e a pontuação total da sessão, atualizando em tempo real — base
visual para o futuro Modo de Sobrevivência e, mais adiante, para
exibição de posição em ranking.

---

## Situação Inicial

Ao final da Sprint 034 (reorganização do painel de debug), o jogo não
tinha nenhum elemento de HUD mostrando pontuação diretamente — o dado
existia (`room.points_by_type`, `player.points_by_type`), mas só era
visível dentro do painel de debug expandido via `TAB`, misturado a
estatísticas por tipo de inimigo.

---

## Problema

A pontuação precisava ficar sempre visível, sem depender do painel de
debug (que é uma ferramenta de desenvolvimento, não elemento de jogo
final), com dois números de propósito distinto: quanto o jogador está
fazendo *nesta* sala especificamente, e quanto já acumulou na sessão
inteira — cada um resetando (ou não) em momentos diferentes.

---

## Decisão Arquitetural

### Reaproveitar Dados Já Existentes, Sem Nova Estrutura

Nenhuma variável nova de acumulação foi criada: `sum(self.room.points_by_type.values())`
e `sum(self.player.points_by_type.values())` já continham exatamente
os dois valores necessários — o primeiro reseta a cada nova visita de
sala (`Room.kills_by_type`/`points_by_type` já são zerados em
`spawn_horde()`), o segundo acumula por toda a sessão de jogo
(`Player.points_by_type`, nunca resetado). A Sprint inteira foi
essencialmente uma tarefa de desenho, não de nova lógica de dados.

### Hierarquia Visual: Sala em Destaque, Total Discreto

Por decisão do criador do jogo, "Sala: X pts" usa fonte maior e branco
puro (informação mais relevante durante o combate ativo), enquanto
"Total: Y pts" usa fonte menor e cinza (contexto de fundo, sempre
visível mas sem competir visualmente com o número imediato).

### Elemento Novo e Independente, Não Reaproveitando "Level"

Por decisão explícita, a pontuação não substitui a linha "Level X" já
existente ao lado da barra de progresso — vira um bloco visual próprio,
posicionado no topo da tela, acima de todos os outros elementos de HUD.

### Reposicionamento em Cascata dos Elementos Existentes

Como o novo bloco ocupa o topo da tela (as posições Y mais baixas,
mais próximas de zero), todos os elementos que já existiam abaixo dele
precisaram descer 26 pixels cada, mantendo o espaçamento relativo
entre eles: barra de HP, barra de progresso, linha de Room/Vidas, e o
painel de debug (cujo `panel_y` também precisou do mesmo ajuste, para
não sobrepor a linha de Room/Vidas logo acima dele).

---

## Conceitos de Python

- **`sum()` sobre `.values()` de um Dicionário** — tanto o total da
  sala quanto o total da sessão são calculados da mesma forma:
  somar os valores de um dicionário que já agrega pontos por tipo de
  inimigo, sem precisar de uma variável acumuladora redundante mantida
  à parte.
- **Duas Fontes (`pygame.font.Font`) de Tamanhos Diferentes na Mesma
  Tela** — usar tamanhos de fonte distintos (24 para a sala, 18 para o
  total) é a forma mais simples de pygame de estabelecer hierarquia
  visual entre dois textos relacionados, sem precisar de bibliotecas
  de estilo mais complexas.

---

## Conceitos de Arquitetura

- **Preferir Reaproveitar Dado Existente a Criar Novo Estado Paralelo**
  — como os totais já eram calculados e mantidos corretamente em outro
  lugar do sistema (para o painel de debug), a Sprint não precisou de
  nenhuma nova fonte de verdade — apenas uma nova forma de exibir o
  que já existia, evitando o risco de duas variáveis divergirem com o
  tempo.
- **Reposicionamento em Cascata como Custo de Adicionar Elementos ao
  Topo de um HUD Empilhado** — quando elementos de UI são posicionados
  por coordenadas absolutas (não por um sistema de layout automático),
  inserir algo no topo exige ajustar manualmente a posição de tudo que
  vem depois — um lembrete de que HUDs baseados em coordenadas fixas
  têm esse custo de manutenção, mesmo sendo mais simples de implementar
  inicialmente.

---

## Implementações

### Missão Única — Elemento de Pontuação + Reposicionamento

**Arquivo:** `game_scene.py`

Criado `draw_score()`, desenhando "Sala: X pts" (fonte 24, branco) e
"Total: Y pts" (fonte 18, cinza) no topo da tela. Reposicionados
`draw_hp_bar()` (y=46), `draw_progress_bar()` (y=72),
`draw_room_and_lives()` (y=88) e `draw_debug_panel()` (`panel_y=118`),
cada um descendo 26px para abrir espaço ao novo elemento.

---

## Bugs Encontrados

### Bug — Corpo do Método `draw_hp_bar()` Esvaziado Durante a Edição

**Sintoma:** a barra de HP do jogador parou de aparecer completamente
na tela, embora nenhum erro tenha sido lançado durante a execução.

**Causa:** ao aplicar a mudança de reposicionamento (`bar_y` de `20`
para `46`), o corpo inteiro do método — cálculo de `hp_ratio`, os três
`pygame.draw.rect()` (fundo, preenchimento proporcional, borda) e o
texto "HP: X/Y" — foi perdido na edição, restando apenas as quatro
linhas de definição de posição/tamanho. O método continuava sendo
chamado normalmente por `draw_ui()`, mas não desenhava mais nada.

**Solução:** restaurado o corpo completo do método, mantendo a nova
posição (`bar_y = 46`).

**Lição Aprendida:** um método que não lança exceção nem afeta o fluxo
do programa pode ainda assim estar "vazio por dentro" — sem uma
verificação visual direta (rodar o jogo e olhar a tela), esse tipo de
regressão passa despercebido, já que Python não reclama de um método
que simplesmente faz menos do que deveria.

---

## Estado Atual da Arquitetura

```
GameScene
 ├── draw_score() — "Sala: X pts" (topleft 20,2) + "Total: Y pts" (topleft 20,20)
 ├── draw_hp_bar() — bar_y=46 (restaurado apos o bug)
 ├── draw_progress_bar() — bar_y=72
 ├── draw_room_and_lives() — topleft (20, 88)
 └── draw_debug_panel() — panel_y=118

Fontes de dado (ja existentes, sem alteracao):
 ├── room.points_by_type — reseta a cada nova visita (spawn_horde)
 └── player.points_by_type — acumula por toda a sessao
```

Testado e confirmado: pontuação da sala e total exibidas corretamente
no topo da tela; "Sala" reseta ao entrar numa sala nova; "Total"
continua acumulando entre salas; nenhum elemento de HUD sobreposto após
o reposicionamento em cascata; barra de HP restaurada e funcionando
normalmente após a correção do bug.

---

## O que o aluno aprendeu

Como reaproveitar dados já existentes em vez de criar uma nova fonte de
verdade paralela, evitando risco de divergência entre dois lugares que
deveriam sempre concordar. Como estabelecer hierarquia visual simples
entre dois textos relacionados usando apenas tamanho de fonte e cor.
Por que HUDs posicionados por coordenadas absolutas exigem
reposicionamento manual em cascata ao inserir elementos no topo. E uma
lição de atenção: um método pode ficar "vazio por dentro" durante uma
edição de código sem gerar erro algum — só uma verificação visual
direta revela esse tipo de regressão silenciosa.

---

## Próxima Sprint

Retomar o Bloco de Power-ups com o Tiro Múltiplo — próximo item da
Lista Consolidada de Power-ups.

---

## Resumo Executivo

Esta Sprint adiciona um elemento de HUD permanente de pontuação
(sala + total), reaproveitando dados já existentes sem criar nova
lógica de acumulação. A implementação exigiu reposicionar em cascata
todos os elementos de HUD já existentes, para abrir espaço no topo da
tela. Um bug real ocorreu durante a edição — o corpo do método
`draw_hp_bar()` foi perdido, fazendo a barra de HP desaparecer
silenciosamente, sem qualquer erro — corrigido restaurando a lógica de
desenho completa. Testado e validado: pontuação da sala resetando por
visita, total acumulando pela sessão, e todos os elementos de HUD sem
sobreposição.
