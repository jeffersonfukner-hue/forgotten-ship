# SPRINT_034.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 034
**Status:** Concluída
**Versão da Arquitetura:** Reorganização do Painel de Debug

---

## Objetivo da Sprint

Reorganizar o painel de debug, que acumulou volume crescente ao longo
das Sprints do Bloco de Power-ups (8+ linhas, a maioria "nível 0
(inativo)" sem utilidade imediata) — prioridade elevada durante os
testes da Sprint 033, ao ficar visualmente evidente que o painel não
escalava bem com o número de power-ups configurados.

---

## Situação Inicial

Ao final da Sprint 033, o painel de debug desenhava incondicionalmente
uma linha por eixo de power-up configurado (8 linhas: ímã, regen,
3 do Sabre, 2 do Sifão, mais o Escudo somando 3), seguidas de
estatísticas totais e o histórico completo de todas as salas e visitas
já registradas — tudo sempre visível, sem distinção entre o que o
jogador precisa decidir agora e o que é apenas histórico acumulado.

---

## Problema

Nem todo dado do painel tem o mesmo propósito: HP, level e slots são
informação de decisão imediata; power-ups ainda não adquiridos são
ruído; o histórico de visitas por sala é valioso para fins didáticos
(estatística real, não dataset de tutorial) mas não precisa competir
por espaço de tela durante o combate ativo.

---

## Decisão Arquitetural

### Resumo Compacto por Sigla, Só do que Está Equipado

Em vez de uma linha por eixo (incluindo os que ainda estão em nível 0),
o painel passou a mostrar uma única linha resumida, com uma sigla por
categoria de power-up equipada, seguida do maior nível entre seus
eixos (ex: `Power-ups: I-2 S-3 ED-1`). Para armas com múltiplos eixos
independentes (Sabre, Sifão, Escudo), o maior nível serve como
indicador rápido de "quão fundo o jogador já investiu" naquela arma,
sem detalhar cada eixo individualmente na visão padrão.

### Histórico Expansível via Tecla, Não Descartado

O bloco de estatísticas totais e histórico por sala/visita continua
sendo calculado e armazenado exatamente como antes — nenhum dado foi
removido da lógica do jogo. A mudança é puramente de exibição: esse
bloco só é desenhado quando o jogador pressiona `TAB`, alternando um
estado de expansão (`debug_expanded`) que persiste até ser pressionado
de novo.

### `TAB` Capturado Independente da Tela de Escolha de Upgrade

`handle_event()` foi reestruturado para checar `K_TAB` antes de checar
se a tela de escolha de upgrade está ativa — o toggle do debug funciona
a qualquer momento do jogo, diferente das teclas 1/2/3 (que só têm
efeito durante uma escolha de upgrade pendente).

---

## Conceitos de Python

- **Maior Valor de um Subconjunto Filtrado (`max()` com Compreensão de
  Lista)** — `get_category_max_level()` filtra os níveis de todos os
  eixos que pertencem a uma categoria e aplica `max()` sobre o
  resultado, obtendo "o eixo mais evoluído daquela arma" sem laço
  manual de comparação.
- **Estado Booleano como Toggle Persistente** — `self.debug_expanded = not self.debug_expanded`
  alterna entre dois estados a cada pressionar de tecla, mantendo o
  valor entre frames (diferente de um estado momentâneo que só dura um
  frame).
- **Early Return para Bifurcar um Método em Dois Modos** — `_build_debug_lines()`
  usa `if not self.debug_expanded: return lines` no meio do método,
  cortando a execução antes do bloco de histórico quando o modo
  compacto está ativo, sem precisar de uma estrutura if/else separada
  envolvendo o restante do método inteiro.

---

## Conceitos de Arquitetura

- **Separar "o que decidir agora" de "o que é histórico"** — a mesma
  fonte de dados (estatísticas por sala, por tipo de inimigo) pode
  servir dois propósitos diferentes: apoio à decisão em tempo real, ou
  registro para análise posterior. Nem sempre os dois precisam ocupar
  o mesmo espaço de tela ao mesmo tempo.
- **Reduzir Exibição sem Reduzir Dado** — a reorganização desta Sprint
  não removeu nenhuma informação do sistema; apenas mudou quando e como
  ela é desenhada. Isso preserva o valor didático do projeto (dados
  reais acumulados, prontos para uma futura tela de estatísticas ou
  análise de dados) sem sacrificar a legibilidade do painel ao vivo.

---

## Implementações

### Missão Única — Resumo Compacto + Histórico Expansível

**Arquivos:** `settings.py`, `player.py`, `game_scene.py`

Adicionado `CATEGORY_LABELS` (sigla por categoria) em `settings.py`.
Criado `get_category_max_level()` no `Player`. Em `GameScene`:
adicionado `debug_expanded` (estado do toggle), captura de `K_TAB` em
`handle_event()`, `_build_powerup_summary_line()` substituindo o antigo
`_build_powerup_lines()`, e `_build_debug_lines()` reestruturado com
early return para bifurcar entre modo compacto e expandido.

---

## Bugs Encontrados

Nenhum bug registrado nesta Sprint — validado via prints em duas
partidas distintas: painel compacto mostrando `Power-ups: R-1 S-3 ED-1`
e, em outra sessão, `Power-ups: R-1 S-5 SF-1`; `TAB` expandindo
corretamente o histórico completo (estatísticas totais, salas, visitas
por sala) sem perda de nenhum dado já acumulado.

---

## Refinamento Registrado para Sprint Futura

### Registro de Build por Visita de Sala (Data Science Aplicada)

Ideia levantada durante esta Sprint: quando o banco de dados persistente
existir, cada visita a uma sala deveria registrar a build de power-ups
que o jogador tinha equipada naquele momento — não apenas o resultado
agregado (pontos, tempo), mas a build específica que gerou aquele
resultado. Isso permitiria comparar builds diferentes objetivamente
(qual gerou melhor desempenho) e gerar gráficos de decisão, conectando
diretamente com a seção já existente no `VISAO.md` ("Ranking por
Qualidade de Escolha" e "Estatísticas Detalhadas por Jogador"), agora
com um caso de uso concreto de ciência de dados aplicada ao próprio
jogo — alinhado ao propósito didático da Academia.

### Pontuação Fixa em Tela (Sala + Geral, Tempo Real)

Ideia levantada ao final desta Sprint, mas **não implementada** por
ser uma feature nova e distinta de "reorganizar debug" — registrada
como próxima Sprint dedicada (Sprint 035), antes de retomar o Bloco de
Power-ups: um elemento de HUD permanente mostrando pontos da sala atual
e pontos totais, atualizando em tempo real, servindo de base visual
para o futuro Modo de Sobrevivência e, mais adiante, para exibição de
posição em ranking.

---

## Estado Atual da Arquitetura

```
settings.py
 └── CATEGORY_LABELS: dict — sigla por categoria (I, R, S, SF, ED)

Player
 └── get_category_max_level(category) — maior nivel entre os eixos de uma categoria

GameScene
 ├── debug_expanded: bool — toggle persistente do historico detalhado
 ├── handle_event() — captura K_TAB independente da tela de upgrade
 ├── _build_powerup_summary_line() — resumo compacto "Power-ups: X-N Y-N"
 └── _build_debug_lines() — bifurca em compacto/expandido via early return
```

---

## O que o aluno aprendeu

Como separar dados de decisão imediata de dados históricos dentro da
mesma estrutura de painel, sem duplicar a lógica de coleta. Como usar
um estado booleano simples como toggle persistente controlado por
tecla. Como usar `max()` sobre uma lista filtrada para obter o "melhor"
valor de um subconjunto de dados relacionados. Por que reorganizar a
exibição de informação não precisa (e geralmente não deve) descartar
o dado subjacente, especialmente quando esse dado tem valor futuro
para análise ou ensino.

---

## Próxima Sprint

Sprint 035 — Pontuação em Tela Fixa: elemento de HUD permanente com
pontos da sala atual e pontos totais, atualizando em tempo real,
preparando terreno visual para o Modo de Sobrevivência e futura
exibição de ranking.

Depois: retomar o Bloco de Power-ups com o Tiro Múltiplo.

---

## Resumo Executivo

Esta Sprint reorganiza o painel de debug, que havia crescido para 8+
linhas de power-up (a maioria inativa) mais um histórico extenso
sempre visível. A solução separa o painel em dois modos: um resumo
compacto sempre visível (sigla + maior nível por categoria equipada) e
um histórico detalhado expansível via tecla `TAB`, sem descartar
nenhum dado já coletado. Validado com prints de duas sessões de jogo
distintas, confirmando o resumo compacto e a expansão/recolhimento
funcionando corretamente. Duas ideias foram registradas para o futuro:
registro de build por visita de sala (ciência de dados aplicada) e uma
Sprint dedicada de pontuação fixa em tela, priorizada antes de retomar
o Bloco de Power-ups.
