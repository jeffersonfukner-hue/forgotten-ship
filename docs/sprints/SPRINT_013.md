# SPRINT_013.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 013
**Status:** Concluída
**Versão da Arquitetura:** Hordas em Todas as Salas, com Spawn Seguro

---

## Objetivo da Sprint

Estender o sistema de hordas — até então restrito à Sala 1 — para
todas as salas do jogo, validando que a arquitetura de spawn,
trancamento de portas e rejogabilidade (Sprints 010-012) generaliza
corretamente para ambientes de tamanhos e formatos distintos (Corredor
e Engenharia, introduzidos na Sprint 009).

---

## Situação Inicial

Ao final da Sprint 012, apenas a Sala 1 (Área de Carga) possuía
inimigos configurados — o Corredor e a Engenharia permaneciam vazios e
sem risco algum, tornando o Nível 2 uma travessia sem desafio.

---

## Problema

Um jogo de sobrevivência com apenas uma sala de risco real não sustenta
a tensão pretendida — o restante do mapa vira um corredor de passagem
inofensivo. Além disso, ao testar a extensão, dois problemas de
adequação de escala surgiram: inimigos do tamanho original (28x28)
ocupavam proporção excessiva da largura do Corredor (300px), e o
sorteio de posições nas bordas podia colocar inimigos coincidindo com
a área de uma porta — arriscando dano injusto ao jogador no instante
em que ele ainda não tem controle pleno da cena.

---

## Decisão Arquitetural

### Generalização do Spawn de Horda

A restrição `if room_id == 1` em `configure_room()` foi removida —
toda sala passa a receber uma horda ao ser configurada, através do
mesmo `spawn_horde()` já existente desde a Sprint 012, sem nenhuma
duplicação de lógica.

### Redução de Escala do Inimigo

O tamanho do `Enemy` foi reduzido de 28x28 para 14x14 — metade da área
original — melhorando a proporção em ambientes estreitos como o
Corredor, sem exigir nenhuma mudança na lógica de perseguição,
separação ou colisão (todas já operam sobre `self.rect`, que se ajusta
automaticamente ao novo tamanho).

### Distância Mínima de Segurança em Relação às Portas

O sorteio de posição de cada inimigo passou a considerar a posição de
todas as portas da sala, rejeitando posições dentro de uma distância
mínima (`SAFE_DISTANCE_FROM_DOOR`). Como o ponto exato de entrada do
jogador varia (spawn inicial vs. entrada por porta específica),
optou-se por uma solução mais robusta: afastar os inimigos de
**qualquer** porta da sala, cobrindo os dois casos sem precisar
identificar qual será usado a cada vez.

O sorteio tenta até 20 posições antes de aceitar a última tentativa,
evitando loop infinito em salas muito pequenas ou com muitas portas
próximas entre si.

---

## Conceitos de Python

- **Compreensão de Lista com `all()`** — a verificação de distância
  mínima usa `all(... for dx, dy in door_positions)`, uma forma
  concisa de garantir que uma condição vale para **todas** as portas
  simultaneamente, sem um loop explícito com flag booleana.
- **Limite de Tentativas para Evitar Loop Infinito** — o sorteio com
  até 20 tentativas é um padrão comum ao rejeitar amostras aleatórias
  por uma condição: sem um limite, uma configuração de sala
  particularmente restritiva poderia travar o jogo indefinidamente.

---

## Conceitos de Arquitetura

- **Generalização Validada por Diversidade de Ambientes** — remover a
  restrição a uma única sala e testar em ambientes de proporções bem
  diferentes (grande e quadrado vs. longo e estreito) é a mesma
  estratégia de validação já usada para a câmera (Sprint 008) e para o
  tamanho de sala (Sprint 009): a confiança na arquitetura vem de
  testá-la contra casos diversos, não apenas o caso original.
- **Segurança de Spawn como Requisito de Design, não Apenas Estético**
  — evitar que um inimigo nasça sobre uma porta não é só uma questão
  visual; é uma garantia de que o jogador sempre tem uma janela mínima
  de reação ao entrar em um novo espaço.

---

## Implementações

### Missão 1 — Hordas em Todas as Salas

**Arquivo:** `game_scene.py`

Removida a restrição `if room_id == 1`; `spawn_horde()` passou a ser
chamado incondicionalmente para toda sala configurada.

### Missão 2 — Redução de Tamanho do Inimigo

**Arquivo:** `enemy.py`

Dimensões alteradas de 28x28 para 14x14.

### Missão 3 — Spawn com Distância Mínima das Portas

**Arquivo:** `game_scene.py`

Adicionado `SAFE_DISTANCE_FROM_DOOR` (120px) e lógica de tentativa
repetida (até 20 vezes) na escolha de posição de cada inimigo,
rejeitando posições próximas demais de qualquer porta da sala.

---

## Estado Atual da Arquitetura

```
GameScene.SAFE_DISTANCE_FROM_DOOR = 120

GameScene.spawn_horde(room)
 ├── calcula posicoes de todas as portas da sala
 ├── para cada inimigo: tenta ate 20 vezes achar posicao segura
 └── aceita a ultima tentativa se nao encontrar uma ideal

configure_room(room, room_id)
 └── chama spawn_horde(room) para toda sala, sem excecao
```

Testado nas três salas existentes (Área de Carga, Corredor,
Engenharia): hordas presentes em todas, inimigos com tamanho adequado
ao espaço, e nenhum spawn ocorrendo sobre uma porta.

---

## O que o aluno aprendeu

Como remover uma restrição condicional temporária (`if room_id == 1`)
de forma segura, apoiando-se em testes contra ambientes diversos para
validar a generalização. Como usar `all()` com uma expressão geradora
para verificar uma condição contra múltiplos itens de forma concisa.
Como aplicar um limite de tentativas ao rejeitar amostras aleatórias,
prevenindo loops infinitos em cenários restritivos.

---

## Próxima Sprint

Sprint 014 — a definir entre: sistema de Reentradas Limitadas, Sistema
de Vidas, ou avanço na Progressão Espacial (ondas múltiplas por sala
com material composto).

---

## Resumo Executivo

Esta Sprint estende o sistema de hordas para todas as salas do jogo,
validando a arquitetura de spawn e trancamento de portas contra
ambientes de proporções bem diferentes. Dois ajustes de qualidade
foram feitos durante a validação: redução do tamanho do inimigo para
melhor caber em espaços estreitos, e uma distância mínima de segurança
entre o ponto de spawn dos inimigos e qualquer porta da sala, evitando
dano injusto ao jogador logo ao entrar em um ambiente novo.
