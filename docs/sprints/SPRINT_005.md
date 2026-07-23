# SPRINT_005.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 005
**Status:** Concluída
**Versão da Arquitetura:** Primeiro Inimigo, Dano e Inimigos por Sala

---

## Objetivo da Sprint

Introduzir o primeiro elemento de ameaça no jogo: um inimigo básico
que persegue o jogador e causa dano ao encostar nele. Esta Sprint
constrói o alicerce mínimo necessário para o Modo 1 (Horde Interna)
descrito em `VISAO.md` — vida, dano, e uma entidade inimiga capaz de
reagir ao jogador.

---

## Situação Inicial

Ao final da Sprint 004, o jogo possuía navegação sólida entre salas,
mas nenhuma fonte de perigo: o jogador podia se mover livremente, sem
nenhuma entidade hostil, sem sistema de vida, e sem nenhuma condição
de derrota.

---

## Problema

Sem inimigo, dano ou vida, não existe o núcleo de tensão que o gênero
Horde exige. Era necessário o primeiro passo mínimo: uma entidade que
ameace o jogador, e uma forma dele reagir a essa ameaça (perdendo
vida, podendo morrer).

---

## Decisão Arquitetural

### 1. Inimigos Pertencem à Sala, não à Cena

A primeira tentativa de implementação criou um único inimigo fixo,
guardado diretamente na `GameScene`, sem vínculo com nenhuma sala
específica. Isso se revelou um erro assim que o jogador trocou de
sala: o inimigo permanecia "preso" na sala anterior, mas continuava
sendo atualizado e causando dano, mesmo estando fora de vista.

A correção seguiu o mesmo princípio já usado para portas desde a
Sprint 003: cada `Room` guarda sua própria lista de inimigos
(`self.enemies`), criados dentro de `configure_room()` junto com as
portas daquela sala. Como as salas já são cacheadas (Sprint 003), os
inimigos herdam esse comportamento automaticamente — uma sala não
visitada não tem seus inimigos atualizados, e uma sala revisitada
retoma exatamente do estado em que ficou.

### 2. Sistema de Vida com Cooldown de Dano

O jogador ganhou atributos de vida (`hp`, `max_hp`) e um estado de
derrota (`is_dead`). Para evitar que o contato contínuo com um inimigo
zerasse a vida em uma fração de segundo, o dano só é aplicado a cada
intervalo de tempo (`damage_cooldown`), simulando um breve momento de
invencibilidade após ser atingido.

### 3. Inimigo com Perseguição Simples, Desacoplado do Player

O `Enemy` não guarda uma referência direta à classe `Player` — ele
recebe apenas coordenadas de destino (`target_x`, `target_y`) em seu
`update()`. Isso mantém a entidade genérica: qualquer coisa que
forneça uma posição pode ser o alvo, sem acoplar `Enemy` a detalhes
internos do jogador.

---

## Conceitos de Python

- **Composição por Referência Externa** — o `Enemy` não conhece o
  `Player`; a `GameScene` é quem intermedia, passando as coordenadas
  necessárias. Isso evita uma dependência circular entre os módulos.
- **Normalização de Vetores para Perseguição** — o mesmo princípio de
  normalização usado no movimento do jogador (Sprint 001) é reutilizado
  para calcular a direção do inimigo até o alvo.
- **Cooldown com Decremento por Delta Time** — `damage_cooldown` é
  decrementado a cada frame (`-= dt`), um padrão comum para qualquer
  temporizador de jogo que precisa ser independente da taxa de quadros.

---

## Conceitos de Arquitetura

- **Pertencimento de Entidades ao Contexto Correto** — a mesma lição
  da Sprint 004 (não tratar objetos como pontos) se repete aqui em
  outra forma: uma entidade específica de uma sala precisa pertencer
  a ela, não existir solta na cena. O sintoma (inimigo te esperando
  fora de vista) só apareceu ao testar trocando de sala — reforçando
  a importância de testar cenários que o código, sozinho, não deixa
  óbvios.
- **Efeito Colateral do Cache de Salas** — a decisão tomada na Sprint
  003 (reaproveitar instâncias de sala) automaticamente preservou o
  estado dos inimigos entre visitas, sem nenhum código adicional para
  isso — um bom exemplo de como uma boa decisão de arquitetura paga
  dividendos em funcionalidades futuras não previstas originalmente.

---

## Implementações

### Missão 1 — Entidade Enemy

**Arquivo:** `enemy.py`

Criada a classe `Enemy`, herdando de `Entity`, inicialmente parada
(sem movimento), apenas para validar sua presença visual em cena.

### Missão 2 — Sistema de Vida e Dano no Player

**Arquivo:** `player.py`

Adicionados `hp`, `max_hp`, `is_dead`, `damage_cooldown` e o método
`take_damage()`. Ao chegar a zero, `is_dead` é definido e o método
`update()` do jogador passa a ignorar qualquer input, travando-o.

### Missão 3 — Colisão e Condição de Derrota

**Arquivo:** `game_scene.py`

A cada frame, verifica-se colisão entre o jogador e os inimigos da
sala atual. Ao colidir (respeitando o cooldown), o jogador recebe
dano. Ao atingir zero, "GAME OVER" é registrado uma única vez — a
implementação de uma cena de derrota completa (menu, restart) fica
para a Fase 1 do `ROADMAP.md` do jogo.

### Missão 4 — Perseguição Simples

**Arquivo:** `enemy.py`

O `Enemy` passou a se mover em direção às coordenadas recebidas em
`update()`, usando o mesmo princípio de normalização de vetor de
movimento já usado no `Player` desde a Sprint 001.

### Missão 5 — Inimigos Pertencentes à Sala

**Arquivos:** `room.py`, `game_scene.py`

`Room` ganhou `add_enemy()` e `get_enemies()`. A criação de inimigos
migrou de `GameScene.__init__` para dentro de `configure_room()`,
associando cada inimigo à sala correta desde sua criação.

---

## Bugs Encontrados

### Bug — Inimigo Não Pertencia a Nenhuma Sala

**Sintoma:** ao trocar de sala, o inimigo permanecia "esquecido" na
sala anterior, mas continuava causando dano ao jogador caso ele
retornasse posteriormente.

**Causa:** o inimigo era criado uma única vez em `GameScene.__init__`,
sem nenhum vínculo com a sala em que deveria existir — diferente das
portas, que já pertenciam a salas específicas desde a Sprint 003.

**Investigação:** identificado ao testar deliberadamente a troca de
salas após a colisão inicial funcionar corretamente.

**Solução:** inimigos passaram a ser criados dentro de
`configure_room()`, pertencendo à instância de `Room` correspondente,
seguindo o mesmo padrão já validado para portas.

**Lição Aprendida:** toda nova entidade que existe dentro de uma sala
específica deve seguir o mesmo princípio de pertencimento já
estabelecido na arquitetura — não presumir que uma solução simples
("só criar o objeto uma vez") é suficiente sem testar contra o
comportamento já existente do sistema (neste caso, a troca de salas).

---

## Estado Atual da Arquitetura

```
Room
 ├── doors: list[Door]
 └── enemies: list[Enemy]   (novo)

Enemy
 ├── update(dt, target_x, target_y)  — persegue uma posição alvo
 └── draw()

Player
 ├── hp / max_hp / is_dead
 ├── damage_cooldown
 └── take_damage(amount)

GameScene.update()
 ├── atualiza inimigos da sala atual, passando posição do player
 └── verifica colisao jogador-inimigo, aplica dano
```

Um inimigo existe atualmente na Sala 1, perseguindo o jogador e
causando dano por contato. Inimigos não são atualizados nem desenhados
em salas que não são a atual.

---

## O que o aluno aprendeu

Como desacoplar uma entidade de IA simples (o inimigo) da entidade que
ela persegue, evitando dependência direta entre classes. Como um bug
só se manifesta ao testar um cenário específico (trocar de sala) que
o código, à primeira vista, não sugeria como problemático. Como uma
decisão de arquitetura tomada Sprints atrás (cache de salas) beneficia
funcionalidades futuras imprevistas no momento da decisão original.

---

## Próxima Sprint

Sprint 006 — a definir. Candidatos: múltiplos inimigos por sala,
diferenciação de tipos de inimigo, ou início da mecânica de restauração
de sistemas da nave (ver `VISAO.md` v2.0).

---

## Resumo Executivo

Esta Sprint introduz o primeiro elemento de ameaça do jogo: um
inimigo que persegue o jogador e causa dano por contato, com sistema
de vida e cooldown de dano no `Player`. A decisão arquitetural central
foi corrigir o pertencimento do inimigo — de solto na cena para
pertencente à sala, seguindo o mesmo padrão já validado para portas —
revelando como o cache de salas da Sprint 003 já preparava o terreno
para esse tipo de persistência de estado.
