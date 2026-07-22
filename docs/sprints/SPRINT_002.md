# SPRINT_002.md
### Forgotten Ship — A1 Game Academy

> **Nota sobre esta versão:** esta Sprint foi reescrita para servir como
> material didático estruturado, contando a evolução da arquitetura de
> forma clara e pedagógica — não como um relato histórico literal do
> processo original de desenvolvimento. O objetivo é ensinar bem, não
> documentar cada passo em vão.

**Sprint:** 002
**Status:** Concluída
**Versão da Arquitetura:** Uma Sala, Uma Porta

---

## Objetivo da Sprint

Dar ao jogador um espaço com limites reais (uma sala) e uma primeira
porta funcional, permitindo a primeira transição entre dois ambientes.
Esta Sprint introduz o conceito de "sala" e "porta" na forma mais
simples possível — antes de qualquer preocupação com múltiplas salas
ou dados reutilizáveis.

---

## Situação Inicial

Ao final da Sprint 001, o jogador se movia livremente pela tela, sem
limites e sem nenhum conceito de ambiente. Não havia paredes, não havia
transição entre espaços — só um retângulo controlável no vazio.

---

## Problema

Um jogo precisa de espaço com limites e de uma forma de ir de um lugar
a outro. Sem isso, não existe progressão nem exploração — só um
personagem flutuando numa tela infinita.

---

## Decisão Arquitetural

Duas novas classes entram na arquitetura:

```
Room
 ├── define os limites jogáveis (paredes)
 └── contém uma ou mais Door

Door
 ├── sabe sua posição e lado (top/bottom/left/right)
 ├── detecta colisão com o Player
 └── sabe para onde o Player deve ir ao atravessá-la
```

Nesta versão inicial, cada `Room` guarda suas portas **diretamente**,
sem nenhuma estrutura de dados externa — a sala simplesmente contém
objetos `Door` já prontos. Essa simplicidade é proposital: entender o
conceito antes de otimizar a arquitetura (essa otimização virá na
Sprint 003).

O `Player` ganha uma pequena máquina de estados, para separar o
comportamento de "andar livremente" do comportamento de "atravessar
uma porta":

- **`walking`** — comportamento padrão, responde ao teclado.
- **`entering_door`** — o jogador é guiado automaticamente até um
  ponto-alvo dentro da porta, sem input do teclado, até a transição
  se completar.

---

## Conceitos de Python

- **Múltiplos Estados como Strings** — `self.state: str = "walking"`,
  comparado com `if/elif` para decidir qual comportamento executar.
  Uma forma simples de máquina de estados, sem precisar de bibliotecas
  externas.
- **Listas de Objetos** — `Room` guarda suas portas em
  `self.doors: list[Door] = []`, e itera sobre elas para desenhar e
  checar colisão.
- **`pygame.Rect` e `collideRect`** — usados tanto para os limites da
  sala quanto para a área de detecção (`trigger`) de cada porta.

---

## Conceitos de Arquitetura

- **Separação de Responsabilidades** — a `Room` sabe desenhar paredes
  e conter portas; a `Door` sabe sua própria posição, colisão e ponto
  de entrada. Nenhuma das duas sabe como o `Player` se move.
- **Máquina de Estados** — usar estados explícitos (`walking`,
  `entering_door`) em vez de flags booleanas soltas (`is_entering = True`)
  deixa o comportamento do Player mais fácil de seguir e de expandir
  no futuro (por exemplo, um estado `stunned` mais adiante).

---

## Implementações

### Missão 1 — A Sala com Limites

**Arquivo:** `room.py`

Criada a `Room`, com um retângulo de piso, quatro retângulos de parede
(desenhados separadamente para dar volume visual), e um método
`get_bounds()` que devolve os limites internos jogáveis (descontando a
espessura da parede).

```python
def get_bounds(self) -> tuple[int, int, int, int]:
    return (self.rect.left + self.wall,
            self.rect.top + self.wall,
            self.rect.right - self.wall,
            self.rect.bottom - self.wall)
```

O `Player` passa a respeitar esses limites, travando (`clamp`) sua
posição dentro deles a cada frame.

**Resultado:** o jogador não atravessa mais paredes — fica contido
dentro da sala.

### Missão 2 — A Porta e sua Área de Colisão

**Arquivo:** `door.py`

Criada a `Door`, com posição, tamanho e lado (`top`, `bottom`, `left`,
`right`). Cada porta calcula sua própria área de **trigger** — uma
região um pouco além do retângulo visual da porta, usada para detectar
quando o jogador está prestes a atravessá-la:

```python
if self.side == TOP:
    return pygame.Rect(self.rect.left, self.rect.bottom,
                        self.rect.width, self.trigger_height)
```

A porta também sabe calcular um **ponto de entrada** (`get_entry_target`)
— um pouco além do centro da porta, na direção correta — para onde o
jogador deve ser guiado ao entrar nela.

### Missão 3 — Transição de Sala

**Arquivos:** `player.py`, `game_scene.py`

Quando o jogador colide com o trigger de uma porta enquanto está
`walking`, ele muda para o estado `entering_door` e é guiado
automaticamente até o ponto de entrada calculado pela porta. Ao
alcançar esse ponto, o jogador sinaliza que uma troca de sala foi
solicitada:

```python
if direction.length() < 2:
    self.room_change_requested = True
    self.state = "walking"
```

A `GameScene` verifica esse sinal a cada frame e, quando ativo, troca
a sala atual e reposiciona o jogador na sala de destino.

**Resultado:** o jogador consegue atravessar uma porta e aparecer em
outra sala, de forma suave e automática.

---

## Estado Atual da Arquitetura

```
GameScene
 ├── Room (limites, paredes)
 │    └── Door (posição, colisão, ponto de entrada)
 └── Player
      ├── estado: walking | entering_door
      └── respeita os limites da Room atual
```

Existem duas salas conectadas por uma porta simples. A transição
funciona, mas cada porta ainda é criada "à mão" dentro da `GameScene`
— sem nenhuma estrutura de dados reutilizável ainda.

---

## O que o aluno aprendeu

Como representar um espaço jogável com limites reais em Pygame. Como
detectar a intenção do jogador de atravessar uma porta usando uma área
de colisão maior que o objeto visual (o "trigger"). Como usar uma
máquina de estados simples para separar comportamento controlado pelo
jogador de comportamento automático (a transição suave até a porta).

---

## Próxima Sprint

Expandir de uma porta isolada para múltiplas salas conectadas,
eliminando a criação manual de cada porta dentro do código e
substituindo por uma arquitetura orientada a dados (`room_data` e
`door_data`).

---

## Resumo Executivo

Esta Sprint introduz `Room` e `Door` na forma mais simples possível:
uma sala com limites físicos, uma porta com área de colisão e ponto de
entrada, e uma máquina de estados no Player para guiar a transição
entre ambientes. É a base conceitual sobre a qual a arquitetura
orientada a dados da Sprint 003 será construída.
