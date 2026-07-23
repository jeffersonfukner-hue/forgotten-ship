# SPRINT_010.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 010
**Status:** Concluída
**Versão da Arquitetura:** Portas Trancadas por Condição de Sala Limpa

---

## Objetivo da Sprint

Implementar a base da Progressão Espacial descrita no `VISAO.md`:
portas começam trancadas em salas com inimigos, e destravam
automaticamente quando todos os inimigos daquela sala são eliminados.

---

## Situação Inicial

Ao final da Sprint 009, todas as portas do jogo estavam sempre
disponíveis, independentemente de haver inimigos vivos na sala — o
jogador podia atravessar livremente mesmo com uma horda inteira ainda
ativa.

---

## Problema

Sem a condição de "sala limpa" para destravar portas, o combate não
tem consequência espacial: o jogador pode simplesmente ignorar os
inimigos e seguir em frente, o que contradiz a visão central do jogo
(restaurar sistemas para progredir, não apenas atravessar o mapa).

---

## Decisão Arquitetural

### Estado `locked` Independente do Estado Visual Existente

`Door` já possuía um estado `open`/`closed`, usado para indicar
visualmente a passagem do jogador (Sprint 004). Foi adicionado um novo
atributo, `locked`, independente desse estado — uma porta pode estar
`closed` (visualmente) e `locked` (funcionalmente) ao mesmo tempo. Essa
separação evita sobrecarregar um único atributo com dois significados
diferentes (aparência de transição vs. permissão de uso).

### Trancamento Automático na Configuração da Sala

Em vez de marcar manualmente quais portas devem começar trancadas,
`configure_room()` tranca automaticamente **todas** as portas de
qualquer sala que termine com inimigos configurados. Isso elimina a
necessidade de configuração redundante — a regra "sala com inimigo
começa trancada" é inferida a partir dos próprios dados, seguindo o
mesmo princípio de inferência já usado na câmera (Sprint 008).

### Destravamento por Verificação Contínua

A cada frame, após remover inimigos mortos, a `GameScene` verifica se
a sala atual ficou sem nenhum inimigo — em caso positivo, todas as
portas daquela sala são destravadas. Essa verificação é simples e
direta, mas suficiente para o estágio atual do jogo (uma condição por
sala, sem ondas múltiplas ainda).

---

## Conceitos de Python

- **Atributo Booleano Independente vs. Reutilização de Estado
  Existente** — a decisão de criar `locked` como um novo atributo,
  em vez de sobrecarregar `state`, ilustra quando vale a pena separar
  conceitos que parecem relacionados, mas representam coisas
  diferentes (aparência vs. permissão).

---

## Conceitos de Arquitetura

- **Inferência de Regra a partir de Dados, não Configuração Manual** —
  assim como a câmera decide seu comportamento observando o tamanho da
  sala (Sprint 008), o trancamento de portas é inferido observando se
  a sala tem inimigos — reduzindo a chance de esquecer de configurar
  uma porta manualmente.
- **Separação de Responsabilidade entre Aparência e Comportamento** —
  o feedback visual (cor da porta) e a lógica de bloqueio (`locked`)
  são independentes: um pode ser refinado sem afetar o outro.

---

## Implementações

### Missão 1 — Estado `locked` em Door

**Arquivo:** `door.py`

Adicionado `self.locked`, com os métodos `lock()`/`unlock()`. O método
`collides()` passou a retornar `False` imediatamente quando a porta
está trancada, independentemente da posição do jogador.

### Missão 2 — Trancamento Automático ao Configurar Salas com Inimigos

**Arquivo:** `game_scene.py`

Ao final de `configure_room()`, se a sala resultante possui algum
inimigo, todas as suas portas são trancadas automaticamente.

### Missão 3 — Destravamento ao Limpar a Sala

**Arquivo:** `game_scene.py`

A cada frame, após `remove_dead_enemies()`, se a lista de inimigos da
sala atual estiver vazia, todas as portas da sala são destravadas.

### Missão 4 — Feedback Visual de Porta Trancada

**Arquivo:** `door.py`

O método `draw()` passou a exibir uma cor distinta (vermelho escuro)
quando a porta está trancada, antes mesmo de considerar seu estado
`open`/`closed` — o jogador percebe visualmente a diferença entre uma
porta disponível e uma porta bloqueada pela horda.

---

## Estado Atual da Arquitetura

```
Door
 ├── locked: bool
 ├── lock() / unlock()
 └── collides() retorna False se locked, sem checar trigger

GameScene
 ├── configure_room(): tranca portas se a sala tiver inimigos
 └── update(): destranca portas quando a sala fica sem inimigos
```

Testado na Sala 1 (Área de Carga): a porta permanece trancada e
inacessível até os 3 inimigos serem eliminados, destravando
corretamente em seguida.

---

## Pendências Registradas para Próximas Sprints

- **Rejogabilidade:** ao sair e voltar a uma sala já limpa, ela
  permanece vazia para sempre (cache de sala sem novo spawn). Próxima
  Sprint deve implementar respawn de horda mais desafiadora ao
  reentrar em sala já limpa, e avaliar se vale estender inimigos para
  todas as salas (não apenas a Sala 1).
- **Ondas múltiplas e material composto:** o refinamento de "várias
  ondas por sala, cada uma dropando uma peça de material, com
  destravamento só ao reunir todas as peças" (registrado no `VISAO.md`)
  fica para uma Sprint futura — pode ser incorporado junto da
  rejogabilidade ou tratado isoladamente, a depender da complexidade
  observada ao implementar a rejogabilidade primeiro.
- **Padrão visual de fundo/paredes:** hoje o piso e as paredes são
  cor sólida uniforme, o que torna o movimento em áreas grandes ou
  corredores longos visualmente pouco perceptível (falta de referência
  de movimento). Um padrão (textura, grade, ou marcação repetida) deve
  ser adicionado como melhoria prioritária, independente das demais
  pendências.

---

## O que o aluno aprendeu

Como implementar uma condição de bloqueio (portas trancadas) de forma
inferida a partir dos dados existentes, em vez de configuração manual
redundante. Como separar dois conceitos que parecem relacionados
(estado visual de transição vs. permissão funcional de uso) em
atributos independentes, evitando sobrecarregar um único valor com
múltiplos significados.

---

## Próxima Sprint

Sprint 011 — implementar rejogabilidade (respawn de horda mais
desafiadora ao reentrar em sala já limpa), avaliando se inimigos devem
passar a existir em todas as salas do jogo, não apenas na Sala 1.

---

## Resumo Executivo

Esta Sprint implementa a base da Progressão Espacial: portas trancadas
automaticamente em salas com inimigos, destravadas ao eliminar toda a
horda, com feedback visual claro (cor distinta). Três pendências foram
conscientemente adiadas e registradas: rejogabilidade, o refinamento de
ondas múltiplas com material composto, e a necessidade de um padrão
visual de fundo para tornar o movimento perceptível em áreas grandes.
