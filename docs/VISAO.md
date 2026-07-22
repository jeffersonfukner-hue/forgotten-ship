# Forgotten Ship
## VISAO.md

> **Versão:** 2.0
> **Status:** Em desenvolvimento — mudança de direção
> **Projeto:** Jogo 01 da A1 Game Academy

---

# Propósito

Este documento descreve a visão do jogo **Forgotten Ship**.
Ele complementa o `PROJETO_MESTRE.md`, que define as regras da academia.

> **Nota de mudança de direção (v2.0):** a visão original (v1.0) descrevia
> um jogo relaxante, sem combate. Esta versão substitui esse conceito por
> um jogo de sobrevivência estilo Horde, mantendo a restauração da nave
> como mecânica central de defesa. Essa mudança impacta arquitetura já
> construída nas Sprints 001-004 (ver "Impacto na Arquitetura Existente").

---

# Conceito

Forgotten Ship é um jogo de sobrevivência ambientado em uma nave espacial
abandonada, à deriva e sob ataque constante.

O jogador restaura os sistemas da nave — e cada sistema restaurado se torna
parte da defesa contra as ondas de inimigos. Restaurar não é uma atividade
paralela à sobrevivência: **é a forma de sobreviver**.

---

# Experiência

O objetivo é transmitir:

- Tensão crescente (ondas de inimigos)
- Satisfação estratégica ao decidir o que restaurar e o que evoluir primeiro
- Sensação de poder crescente, tanto do jogador quanto da própria nave
- Progresso tangível e **permanente** entre partidas

---

# Protagonista

Um alienígena encontra uma nave abandonada, à deriva em território hostil,
e precisa restaurá-la para sobreviver — tanto às ondas de ameaças quanto
ao abandono da própria nave.

---

# Mecânica Principal

O jogo alterna entre dois modos de combate, cada um com sua própria
progressão permanente.

## Modo 1 — Horde Interna (a pé, dentro da nave)

O jogador enfrenta ondas de inimigos dentro da nave. Inimigos derrotados
dropam pontos, que acumulados sobem o **nível do jogador**.

Ao subir de nível, o jogador escolhe entre 3 upgrades — ou pode "assistir
a um vídeo" (simulado na implementação, sem anúncio real) para receber
os 3 upgrades de uma vez.

Upgrades do jogador são **permanentes** entre partidas, aumentando a
dificuldade proporcionalmente para manter o desafio.

Restaurar sistemas da nave nesta fase gera dois tipos de benefício
(um sistema pode gerar um ou ambos):

- **Defesa ativa** — o sistema passa a agir sozinho (ex: uma torreta
  automática na sala).
- **Fortalecimento do jogador** — o sistema melhora diretamente as
  capacidades do jogador (ex: mais HP).

## Modo 2 — Horde de Nave (combate espacial)

A cada 10 ondas da Horde Interna, a cena muda: a nave passa a ser atacada
por naves menores em combate espacial.

Inimigos (naves) derrotados dropam pontos, que acumulados geram 3
powerups — escolhidos 1 ou 3 (via vídeo simulado), da mesma forma que
no Modo 1.

Powerups deste modo melhoram e persistem o **poder da nave** (progressão
separada da progressão do jogador).

Após o combate espacial, o jogo retorna ao Modo 1, reiniciando o ciclo
com dificuldade maior.

## Progressão Dupla e Permanente

Existem duas trilhas de progressão independentes, ambas permanentes
entre partidas:

- **Progresso do Jogador** — upgrades pessoais, ganhos no Modo 1.
- **Progresso da Nave** — upgrades da nave, ganhos no Modo 2.

Ambas alimentam a dificuldade proporcional dos inimigos nas partidas
seguintes.

---

# Objetivo do MVP

Ver `ROADMAP.md` do projeto para as fases de desenvolvimento planejadas.

---

# Fora do Escopo do MVP Atual

Ideias que existem, mas que não fazem parte do desenvolvimento agora —
para não cair em planejamento eterno, ficam registradas e pausadas até
que o jogo atual atinja maturidade suficiente para justificá-las.

- Multiplayer
- Mundo aberto / exploração de planetas
- Venda e troca de naves

---

# Impacto na Arquitetura Existente

As Sprints 001-004 construíram o sistema de `Room` e `Door` pensando em
navegação calma entre salas, sem noção de:

- inimigos, spawns de ameaças ou dano;
- estado "restaurado / não restaurado" por sala ou sistema;
- comportamento ativo de sistemas restaurados (torretas, buffs);
- progressão persistente do jogador e da nave (provavelmente exigirá
  banco de dados, não apenas estado em memória);
- um segundo modo de jogo (combate espacial), com sua própria cena e
  regras.

Essa mudança de direção exigirá novas Sprints dedicadas a esses sistemas.
A arquitetura de Room/Door provavelmente continua útil como base de
navegação do Modo 1, mas precisará ser estendida — isso será avaliado
quando o desenvolvimento de código for retomado.

---

# Estado Atual

Visão redefinida. Aguardando definição do roadmap interno do jogo
(fases de desenvolvimento) antes de retomar o código.

---

# Histórico

## v2.0
- Mudança de direção: de jogo relaxante para jogo de sobrevivência
  estilo Horde, com dois modos de combate (interno e espacial) e
  progressão dupla e permanente (jogador e nave).
- Registrado impacto na arquitetura já construída (Sprints 001-004).

## v1.0
- Documento criado.
- Definida a visão inicial do Forgotten Ship (jogo relaxante).
