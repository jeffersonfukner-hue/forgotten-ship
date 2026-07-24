# SPRINT_015.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 015
**Status:** Concluída
**Versão da Arquitetura:** HUD Básica — Barra de HP e Contador de Vidas

---

## Objetivo da Sprint

Implementar os primeiros elementos de interface fixa (HUD) do jogo:
uma barra visual de HP e um contador de vidas, ambos sempre visíveis
na tela, independentemente da posição da câmera — tornando visível na
tela o que, até então, só era possível acompanhar pelo console.

---

## Situação Inicial

Ao final da Sprint 014, o Sistema de Vidas e o HP do jogador
funcionavam corretamente, mas só eram visíveis através de mensagens no
terminal (`print`). Não havia nenhum elemento gráfico na tela
informando o estado atual do jogador durante a partida.

---

## Problema

Sem retorno visual na tela, o jogador não tem como acompanhar seu
próprio estado (vida restante, vidas disponíveis) sem olhar para o
console — inviável para qualquer versão jogável real, e também
dificultava a própria validação de testes, já que exigia alternar
entre a janela do jogo e o terminal constantemente.

---

## Decisão Arquitetural

### HUD Desenhada por Último, Sem Deslocamento de Câmera

`draw_ui()` já existia desde a Sprint 001 como método vazio,
chamado por último em `draw()` — depois do fundo e do mundo
(`draw_background`, `draw_world`). Isso já garantia, por construção,
que qualquer elemento desenhado ali apareceria por cima de tudo, na
posição literal da tela, sem receber o offset de câmera (diferente de
tudo que é desenhado em `draw_world`/`draw_background`, que recebe
`camera_x`/`camera_y`).

### Barra de HP como Retângulos Sobrepostos

A barra de HP foi implementada com dois retângulos: um de fundo
(vermelho escuro, representando vida perdida) e um de preenchimento
(verde, com largura proporcional ao HP restante) desenhado por cima.
Essa é a técnica mais simples e comum para barras de progresso em
jogos 2D, sem exigir nenhuma imagem ou asset externo.

---

## Conceitos de Python

- **Proporção como Multiplicador de Largura** — `bar_width * hp_ratio`
  calcula a largura do preenchimento da barra a partir de uma razão
  simples (`hp / max_hp`), uma técnica reutilizável para qualquer
  barra de progresso futura (energia, barra de drops, etc.).

---

## Conceitos de Arquitetura

- **Separação entre Mundo e Interface por Ordem de Desenho** — a HUD
  não precisou de nenhum mecanismo novo para ignorar a câmera; a
  arquitetura já separava `draw_ui()` das camadas afetadas por
  `camera_x`/`camera_y` desde a Sprint 001, quando o método foi
  originalmente criado (ainda vazio). Isso ilustra como uma decisão
  estrutural simples, tomada cedo, pode facilitar uma funcionalidade
  muito posterior sem exigir retrabalho.

---

## Implementações

### Missão 1 — Barra de HP

**Arquivo:** `game_scene.py`

Adicionado `draw_hp_bar()`, desenhando fundo, preenchimento
proporcional ao HP atual, contorno e texto numérico (`HP: X/Y`).

### Missão 2 — Contador de Vidas

**Arquivo:** `game_scene.py`

Adicionado `draw_lives_counter()`, exibindo o texto `Vidas: X/Y`
abaixo da barra de HP.

### Missão 3 — Conexão em `draw_ui`

**Arquivo:** `game_scene.py`

`draw_ui()`, antes vazio, passou a chamar os dois métodos acima.

---

## Estado Atual da Arquitetura

```
GameScene.draw()
 ├── draw_background()  — afetado pela camera
 ├── draw_world()        — afetado pela camera
 └── draw_ui()            — fixo na tela, sem offset de camera
      ├── draw_hp_bar()
      └── draw_lives_counter()
```

Testado com um ciclo completo de dano e revive: a barra de HP reage
corretamente a cada golpe, e o contador de vidas decrementa
visivelmente a cada morte, confirmando a sincronia entre a lógica
(Sprint 014) e sua representação visual.

---

## O que o aluno aprendeu

Como implementar uma barra de progresso simples usando dois
retângulos sobrepostos, sem depender de imagens. Como a ordem de
desenho, decidida desde a fundação do projeto (Sprint 001), já
preparava o terreno para uma HUD fixa, independente de câmera, sem
exigir nenhuma mudança estrutural nesta Sprint.

---

## Próxima Sprint

Sprint 016 — a definir entre: mover o contador de sala/visitas (hoje
texto de debug dentro do mundo, afetado pela câmera) para um elemento
fixo de HUD; sistema de Reentradas Limitadas; ou avanço na Progressão
Espacial (ondas múltiplas por sala).

---

## Resumo Executivo

Esta Sprint implementa os primeiros elementos de HUD do jogo: uma
barra visual de HP e um contador de vidas, ambos fixos na tela e
imunes ao deslocamento da câmera — uma consequência natural de uma
decisão estrutural tomada já na Sprint 001, quando `draw_ui()` foi
posicionado como a última camada de desenho do jogo.
