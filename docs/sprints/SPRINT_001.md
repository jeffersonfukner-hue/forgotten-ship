# SPRINT_001.md
### Forgotten Ship — A1 Game Academy

> **Nota sobre esta versão:** esta Sprint foi reescrita para servir como
> material didático estruturado, contando a evolução da arquitetura de
> forma clara e pedagógica — não como um relato histórico literal do
> processo original de desenvolvimento (que envolveu conversas
> desorganizadas e retrabalho). O objetivo é ensinar bem, não documentar
> cada passo em vão.

**Sprint:** 001
**Status:** Concluída
**Versão da Arquitetura:** Fundação (pré-Room/Door)

---

## Objetivo da Sprint

Construir o esqueleto mínimo de um jogo em Pygame: uma janela, um loop
de jogo rodando, e um personagem que se move na tela. Sem salas, sem
portas, sem inimigos — só o "coração batendo" do jogo.

---

## Situação Inicial

Não havia nada. Esta é a primeira Sprint do projeto.

---

## Decisão Arquitetural

O jogo é organizado em três camadas, cada uma com uma responsabilidade
única:

```
Game
 └── Scene (a cena atual do jogo)
      └── EntityManager
           └── Entity (Player, e futuras entidades)
```

- **`Game`** cuida só do essencial de infraestrutura: abrir a janela,
  rodar o loop principal, controlar o tempo (`delta time`), e repassar
  eventos para a cena atual.
- **`Scene`** é uma classe base vazia (por enquanto), pensada para que
  o jogo possa ter várias cenas no futuro (menu, jogo, game over) sem
  que o `Game` precise saber os detalhes de cada uma.
- **`Entity`** é a classe base de qualquer "coisa" que existe no jogo
  e precisa ser atualizada e desenhada — hoje só o `Player`, mas essa
  base evita duplicar código quando outras entidades (inimigos, itens)
  aparecerem.
- **`EntityManager`** centraliza a atualização e o desenho de todas as
  entidades, para que a cena não precise gerenciar uma lista manualmente.

---

## Conceitos de Python

- **Classes e Herança** — `Player` herda de `Entity`, reaproveitando
  `rect`, posição e tamanho sem reescrever.
- **Métodos que não fazem nada (`pass`)** — usados propositalmente em
  `Scene` e `Entity` como classes base, para serem sobrescritos por
  quem herda delas.
- **Type Hints** — todos os atributos e métodos têm tipos declarados
  (`self.speed: int = 250`), facilitando entender o que cada coisa é
  sem precisar rodar o código.
- **Delta Time (`dt`)** — o movimento do jogador é multiplicado pelo
  tempo entre frames (`self.clock.tick(FPS) / 1000`), garantindo que o
  jogo se comporte igual independente da taxa de quadros da máquina.

---

## Conceitos de Arquitetura

- **Responsabilidade Única** — `Game` não sabe desenhar um jogador,
  `Player` não sabe abrir uma janela. Cada classe faz uma coisa.
- **Composição** — `Game` *tem* uma `Scene`, que *tem* um `EntityManager`,
  que *tem* uma lista de `Entity`. Nenhuma classe herda da outra nessa
  cadeia; elas se combinam.
- **Baixo Acoplamento via Classe Base** — `EntityManager` não sabe se
  está atualizando um `Player` ou qualquer outra coisa — ele só sabe
  que é uma `Entity`.

---

## Implementações

### Missão 1 — Estrutura e Loop Principal

**Arquivos:** `game.py`, `settings.py`

Criado o `Game`, responsável por inicializar o Pygame, abrir a janela
com dimensões e título definidos em `settings.py`, e rodar o loop
principal: capturar eventos, atualizar a cena, desenhar a cena, e
repetir — até o evento `pygame.QUIT`.

```python
while running:
    dt = self.clock.tick(settings.FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        self.scene.handle_event(event)
    self.scene.update(dt)
    self.scene.draw(self.screen)
    pygame.display.flip()
```

**Resultado:** uma janela abre, roda a 60 FPS, e fecha corretamente
ao clicar no X.

### Missão 2 — Classes Base (Scene e Entity)

**Arquivos:** `scene.py`, `entity.py`

Criadas as classes base `Scene` e `Entity`, ambas com métodos vazios
(`handle_event`, `update`, `draw`) pensados para serem sobrescritos.
Isso define um "contrato": qualquer cena ou entidade futura sabe quais
métodos precisa implementar.

### Missão 3 — Player e Movimento

**Arquivos:** `entity.py`, `player.py`, `entity_manager.py`

`Player` herda de `Entity` e implementa movimento em 8 direções via
teclado (setas ou WASD), com normalização do vetor de direção — para
que mover na diagonal não seja mais rápido que mover reto.

```python
if direction.length_squared() > 0:
    direction = direction.normalize()
```

**Resultado:** o jogador se move suavemente em qualquer direção, na
mesma velocidade.

---

## Bugs Encontrados

Nenhum bug crítico registrado nesta reconstrução da Sprint. O texto
original (versão anterior deste documento) mencionava ajustes de
indentação e ordem de operações durante o desenvolvimento — esses
detalhes de processo foram omitidos aqui por não agregarem valor
didático à versão final da arquitetura.

---

## Estado Atual da Arquitetura

```
Game
 └── Scene
      └── EntityManager
           └── Player (Entity)
```

Jogo abre, roda, e o jogador se move livremente na tela. Ainda não
existem salas, limites de movimento, portas ou outras entidades.

---

## O que o aluno aprendeu

Como estruturar um jogo em Pygame usando camadas com responsabilidades
separadas, em vez de colocar tudo dentro de um único loop principal.
Como normalizar um vetor de movimento para evitar o clássico bug de
"diagonal mais rápida". Como usar Delta Time para desacoplar a lógica
do jogo da taxa de quadros da máquina.

---

## Próxima Sprint

Introduzir o conceito de sala (`Room`) com limites, e uma primeira
porta (`Door`) conectando duas salas — permitindo a primeira navegação
do jogador entre ambientes.

---

## Resumo Executivo

Esta Sprint constrói a fundação do Forgotten Ship: uma janela, um loop
de jogo funcional, e um personagem que se move livremente na tela,
usando uma arquitetura em camadas (Game → Scene → EntityManager →
Entity) que vai sustentar todo o crescimento futuro do projeto.
