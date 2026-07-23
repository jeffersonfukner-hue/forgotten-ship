# SPRINT_008.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 008
**Status:** Concluída
**Versão da Arquitetura:** Sistema de Câmera (Primeiro Passo da Re-arquitetura Espacial)

---

## Objetivo da Sprint

Implementar o primeiro passo da Re-arquitetura Espacial registrada no
`VISAO.md`: um sistema de câmera que segue o jogador, permitindo salas
maiores que a tela. Esta Sprint isola deliberadamente a câmera como
prova de conceito, sem ainda alterar a estrutura de múltiplas salas
por nível ou a transição cinematográfica — mudanças maiores que ficam
para Sprints futuras.

---

## Situação Inicial

Até esta Sprint, toda posição desenhada na tela era idêntica à posição
no mundo — não existia distinção entre "onde algo está" e "onde algo
aparece desenhado". Isso limitava cada sala a caber inteiramente
dentro da janela do jogo (800x600), o que não é adequado ao formato
16:9 predominante em dispositivos móveis, nem permite salas grandes
com obstáculos e itens espalhados, como planejado na visão do jogo.

---

## Problema

Sem separar posição de mundo e posição de tela, salas maiores que a
janela simplesmente não caberiam — parte do conteúdo ficaria sempre
fora de vista, sem nenhuma forma do jogador vê-lo ou alcançá-lo. Era
necessário desacoplar essas duas noções antes de qualquer expansão de
tamanho de sala fazer sentido.

---

## Decisão Arquitetural

### Câmera como Offset de Desenho

Foi adicionado um par de valores (`camera_x`, `camera_y`) à
`GameScene`, recalculado a cada frame (`update_camera()`). Todo método
de desenho do jogo passou a aceitar esse offset como parâmetro
opcional (padrão `0`, para não quebrar nenhum código que não o utilize
ainda), subtraindo-o da posição real antes de desenhar.

A posição no mundo (usada para movimento e colisão) permanece
inalterada — apenas o desenho é afetado. Isso preserva toda a lógica
de jogo já existente (movimento, colisão de portas, combate),
alterando somente a camada de renderização.

### Comportamento Duplo: Centralizar vs. Seguir

A câmera se comporta de forma diferente dependendo do tamanho da sala
em relação à janela, em cada eixo independentemente:

- **Sala menor ou igual à janela:** a câmera centraliza a sala na
  tela — comportamento equivalente ao que existia antes da mudança,
  preservando a aparência de salas já existentes.
- **Sala maior que a janela:** a câmera segue o jogador, mantendo-o
  centralizado, com limites (clamp) para nunca revelar área fora dos
  limites da sala.

Essa distinção permite que salas de tamanhos variados coexistam sem
necessidade de configuração manual por sala — o comportamento correto
é inferido a partir do próprio tamanho da sala.

---

## Conceitos de Python

- **Parâmetros com Valor Padrão para Compatibilidade Retroativa** —
  todo `draw(screen, camera_x=0, camera_y=0)` aceita chamadas antigas
  sem quebrar, um padrão útil ao introduzir uma mudança que afeta
  muitos métodos ao mesmo tempo.
- **Atribuição Encadeada Acidental (`a = b = c`)** — um erro real
  encontrado nesta Sprint: `self.camera_x = float = 0.0` é sintaxe
  válida em Python (atribuição encadeada), mas criava uma variável de
  instância chamada `float`, sobrescrevendo o tipo nativo dentro
  daquele objeto — um lembrete de que código sintaticamente válido
  nem sempre faz o que a leitura rápida sugere.

---

## Conceitos de Arquitetura

- **Separação entre Posição de Mundo e Posição de Tela** — o conceito
  central desta Sprint. Toda a lógica de jogo (movimento, colisão)
  opera em coordenadas de mundo; apenas o desenho é transformado para
  coordenadas de tela, através do offset de câmera.
- **Inferência de Comportamento a partir de Dados Existentes** — a
  câmera não precisa de uma flag manual "esta sala segue o jogador";
  ela decide isso comparando o tamanho da sala com o tamanho da janela
  — reduzindo configuração manual e risco de inconsistência.

---

## Implementações

### Missão 1 — Cálculo do Offset de Câmera

**Arquivo:** `game_scene.py`

Adicionado `update_camera()`, calculando `camera_x`/`camera_y` a cada
frame, com o comportamento duplo (centralizar/seguir) descrito acima.

### Missão 2 — Aplicação do Offset em Todos os Desenhos

**Arquivos:** `room.py`, `door.py`, `player.py`, `enemy.py`,
`projectile.py`, `entity_manager.py`

Todo método `draw()` do jogo passou a aceitar `camera_x`/`camera_y`
como parâmetros opcionais, subtraindo-os da posição antes de desenhar.

### Missão 3 — Validação com Sala Maior que a Tela

**Arquivo:** `game_scene.py`

A Sala 1 foi temporariamente configurada com dimensões maiores que a
janela (1280x960, aproximadamente 4x a área anterior), validando que a
câmera realmente segue o jogador quando necessário — não apenas
centraliza, como ocorre nas demais salas, ainda do tamanho original.

---

## Bugs Encontrados

### Bug 1 — Projétil Desenhado Duas Vezes

**Sintoma:** um segundo "eco" visual do projétil aparecia ligeiramente
deslocado do projétil real.

**Causa:** durante a edição de `draw_world()`, uma linha antiga
(`projectile.draw(screen)`, sem os parâmetros de câmera) permaneceu
junto da nova chamada correta (`projectile.draw(screen, camera_x,
camera_y)`) — o projétil era desenhado duas vezes por frame, uma com
offset correto e outra com offset zero (desatualizado desde que a
câmera deixou de ser sempre zero).

**Solução:** remoção da chamada antiga duplicada.

**Lição Aprendida:** ao editar um método adicionando uma nova
chamada, revisar se uma chamada antiga equivalente não permaneceu
esquecida logo abaixo — duplicações desse tipo não geram erro, apenas
um efeito visual sutil e fácil de atribuir à causa errada.

### Bug 2 — Sala Deslocada para o Canto Superior Esquerdo

**Sintoma:** ao implementar a primeira versão de `update_camera()`, a
sala (menor que a janela) passou a aparecer no canto superior
esquerdo, perdendo a centralização que existia antes da mudança.

**Causa:** a lógica inicial de câmera presumia que a sala sempre teria
o mesmo tamanho da janela — quando menor, o cálculo de limites
("clamp") travava a câmera na borda da sala, em vez de centralizá-la.

**Solução:** `update_camera()` passou a verificar, por eixo, se a sala
é menor ou igual à janela — nesse caso, centraliza a sala; caso
contrário, segue o jogador com os limites apropriados.

**Lição Aprendida:** ao migrar de "sem câmera" para "com câmera", é
fácil presumir implicitamente que todo conteúdo terá um tamanho
relacionado à tela — validar o comportamento em ambos os cenários
(menor e maior que a janela) evita regressões visuais silenciosas.

### Bug 3 — Métodos Aninhados por Erro de Indentação

**Sintoma:** `TypeError: Entity.draw() takes 2 positional arguments
but 4 were given`, mesmo após `Enemy.draw()` ter sido corretamente
implementado com a nova assinatura.

**Causa:** ao colar o novo método `draw()` em `Enemy`, ele ficou
aninhado dentro do método `update()` por um nível de indentação a
mais — tornando-o uma função local de `update`, não um método da
classe. Python, nesse caso, recorria ao `draw()` da classe base
(`Entity`), com a assinatura antiga.

**Solução:** correção da indentação, posicionando `draw()` no mesmo
nível que os demais métodos da classe.

**Lição Aprendida:** em Python, a indentação define a estrutura —
um método colado com indentação incorreta não gera erro de sintaxe
necessariamente, mas muda silenciosamente seu significado (de "método
da classe" para "função aninhada", por exemplo). Erros desse tipo se
manifestam de forma indireta, frequentemente na classe base, o que
pode confundir a investigação inicial.

---

## Estado Atual da Arquitetura

```
GameScene
 ├── camera_x / camera_y — recalculados a cada frame
 └── update_camera()
      ├── sala <= janela: centraliza a sala
      └── sala > janela: segue o jogador, com limites

Todo Entity/Room/Door.draw(screen, camera_x=0, camera_y=0)
 └── posição de desenho = posição de mundo - offset de câmera
```

A Sala 1 já é maior que a tela e a câmera a segue corretamente. As
demais salas permanecem do tamanho original, com a câmera centralizando
normalmente. Portas dentro da Sala 1 ainda estão nas posições antigas,
não ajustadas ao novo tamanho — pendência para a próxima etapa da
Re-arquitetura Espacial.

---

## O que o aluno aprendeu

Como implementar uma câmera 2D simples através de um offset de
desenho, mantendo a lógica de jogo em coordenadas de mundo intactas.
Como inferir comportamento (centralizar vs. seguir) a partir de dados
já existentes, em vez de configuração manual redundante. Como erros de
indentação em Python podem produzir falhas que se manifestam de forma
indireta e confusa, exigindo atenção ao nível exato de aninhamento do
código, não apenas ao seu conteúdo.

---

## Próxima Sprint

Continuação da Re-arquitetura Espacial: reposicionamento das portas
dentro da Sala 1 (adequando-as ao novo tamanho), e planejamento da
estrutura de múltiplas salas conectadas por nível, conforme descrito
no `VISAO.md`.

---

## Resumo Executivo

Esta Sprint implementa o primeiro passo da Re-arquitetura Espacial: um
sistema de câmera que segue o jogador em salas maiores que a tela, e
centraliza salas menores — preservando a aparência de todo o jogo
existente enquanto habilita o crescimento futuro do mundo jogável.
Três bugs foram encontrados e corrigidos, todos ligados a erros sutis
de edição (duplicação de chamada, presunção implícita de tamanho, e
indentação incorreta) — reforçando a importância de testar
cuidadosamente mudanças que tocam múltiplos arquivos de uma só vez.
