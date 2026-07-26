# Forgotten Ship
## VISAO.md

> **Versão:** 4.8
> **Status:** Em desenvolvimento — mudança de direção
> **Projeto:** Jogo 01 da A1 Game Academy

---

# Índice

- [Propósito](#propósito)
- [Conceito](#conceito)
- [Experiência](#experiência)
- [Protagonista](#protagonista)
- [Mecânica Principal](#mecânica-principal)
- [Objetivo do MVP](#objetivo-do-mvp)
- [Fora do Escopo do MVP Atual](#fora-do-escopo-do-mvp-atual)
- [Impacto na Arquitetura Existente](#impacto-na-arquitetura-existente)
- [Estado Atual](#estado-atual)
- [🆕 Pendências por Tema (Índice Rápido)](#pendências-por-tema-índice-rápido)
- [Backlog Detalhado — Modo 1](#backlog-detalhado--modo-1-horde-interna)
  - [Ataque](#ataque)
  - [Drops e Progressão](#drops-e-progressão)
  - [Progressão Espacial: Portas e Reparo em Cadeia](#progressão-espacial-portas-danificadas-e-reparo-em-cadeia)
  - [Rejogabilidade](#rejogabilidade-hordas-mais-desafiadoras-a-cada-retorno)
  - [Visão de Longuíssimo Prazo](#visão-de-longuíssimo-prazo-narrativa-histórica-e-área-de-membros)
  - [Re-arquitetura Espacial: Mapas Contínuos por Nível](#re-arquitetura-espacial-mapas-contínuos-por-nível)
  - [Percepção e Alcance de Tiro](#percepção-de-inimigos-e-alcance-de-tiro-raio-único)
  - [Comportamento de Projétil](#comportamento-de-projétil-tiro-base)
  - [Upgrades do Tiro](#upgrades-do-tiro-até-5-níveis-cada-upgrades-independentes-entre-si)
  - [Campo de Força (Arma 2)](#campo-de-força-arma-2)
  - [Sabre Giratório (Arma 3)](#sabre-giratório-arma-3--tema-espacial)
  - [Arma Vampírica ("Fang")](#arma-vampírica-fang)
  - [Armas de Fogo com Munição](#sistema-de-armas-de-fogo-com-munição-e-recarga)
  - [Padrões de Tiro Múltiplo](#padrões-de-tiro-múltiplo-escolha-do-jogador)
  - [Escudo](#escudo)
  - [Padronização de Eixos de Upgrade](#padronização-de-eixos-de-upgrade-decisão-de-arquitetura-pendente)
  - [Tipos de Inimigo (Taxonomia)](#tipos-de-inimigo-taxonomia)
  - [Penalidade por Dano Recebido](#penalidade-por-dano-recebido)
  - [Energia Afetando Skills](#energia-afetando-qualidade-das-skills)
  - [Power-ups Passivos](#power-ups-passivos)
  - [Coleta Automática de Gemas](#coleta-automática-de-gemas-remanescentes)
  - [Interface de Usuário (UI)](#interface-de-usuário-ui--visão-geral)
  - [Ranking por Qualidade de Escolha](#ranking-por-qualidade-de-escolha)
  - [Progressão Vitalícia vs. de Partida](#dois-tipos-de-progressão-vitalícia-vs-de-partida)
  - [Moeda do Jogo](#moeda-do-jogo)
  - [Rankings Honesto vs. VIP](#dois-rankings-distintos-honesto-vs-vip)
  - [Estatísticas Detalhadas por Jogador](#estatísticas-detalhadas-por-jogador)
  - [Ordem de Implementação Sugerida](#ordem-de-implementação-sugerida)
  - [Pesquisa de Referência de Gênero](#pesquisa-de-referência-gênero-horde-survivor--bullet-heaven)
  - [Plano Consolidado — Blocos Temáticos](#plano-consolidado--blocos-temáticos-pós-sprint-026)
- [Histórico de Versões](#histórico)

---

# Pendências por Tema (Índice Rápido)

> Visão consolidada do que já foi registrado neste documento mas ainda
> **não implementado**, organizada por bloco temático (ver Plano
> Consolidado, mais abaixo). Atualizado a cada nova pendência
> registrada — consulte aqui antes de perguntar "o que falta?".

### 🔧 Bloco de Obstáculos (em andamento)
- [ ] Obstáculo destrutível (só o fixo existe até agora)
- [ ] Geração automática de obstáculos a partir do Nível 11

### ⚡ Bloco de Power-ups (não iniciado)
- [ ] Ímã (raio de coleta de gemas ampliado)
- [ ] Regeneração de vida passiva
- [ ] Arma "Fang" (vampírica, roubo de vida)
- [ ] Armas de fogo com munição/recarga (revólver, pesada, metralhadora)
- [ ] Padrões de tiro múltiplo (diagonal, linha reta, quatro cantos)
- [ ] Sabre giratório
- [ ] Escudo (mecânica ainda não definida)
- [ ] Padronização de eixos de upgrade entre armas
- [ ] Tela de escolha de skill (1 ou 3 via vídeo simulado) — hoje é só upgrade automático

### 👹 Bloco de Entidades de Chefes (não iniciado)
- [ ] Mini-chefes (drop garantido, sem vídeo)
- [ ] Chefão com barra de vida em fases coloridas + atordoamento
- [ ] Tipos de inimigo: Aéreo, Ativo (cuspe venenoso), Residual (gosma)
- [ ] Comportamentos de perseguição estilo Pac-Man
- [ ] Formação de grupo (meia-lua) para inimigos à distância
- [ ] Dificuldade adaptativa por desempenho real

### 🚀 Bloco de Restauração da Nave (não iniciado)
- [ ] Portas danificadas/trancadas até reparo
- [ ] Material de reparo dropado por inimigos, vinculado a porta específica
- [ ] Ondas com material composto (quebra-cabeça de montagem)
- [ ] Minigames de reparo (Sudoku, Match 3, Pac-Man, Tetris)

### 🎨 Bloco de Refinamento Geral (reservado para o final)
- [ ] Sprites reais substituindo placeholders geométricos
- [ ] Balanceamento fino geral
- [ ] Polimento de UX
- [ ] Revisar todo feedback visual de dano/HP: preferir efeitos que não
      dependam de barra de HP quando possível (ex: encolhimento,
      mudança de cor/opacidade), como já adotado para o obstáculo
      destrutível — mais imersivo que barras sobrepostas ao sprite

### 📊 Sistemas Transversais (não encaixam em um bloco só)
- [ ] Sistema de Vidas completo (vídeo 1x, regeneração por tempo, compra)
- [ ] UI de confirmação de Reentradas (hoje só cor da porta)
- [ ] Moeda do jogo
- [ ] Dois rankings (Honesto vs. VIP)
- [ ] Coleta automática de gemas remanescentes (auto-ímã, mini-ímã esporádico)
- [ ] UI final substituindo o painel de debug
- [ ] Transição cinematográfica ao entrar em sala/nível novo
- [ ] Estrutura de N salas por nível, além do que já existe (Nível 1 e 2)

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

# Backlog Detalhado — Modo 1 (Horde Interna)

Visão completa do sistema de combate e progressão do Modo 1, capturada
para referência futura. Implementação ocorre de forma incremental,
Sprint a Sprint — esta seção não representa escopo de uma única Sprint.

## Ataque

- Automático: o jogador apenas se move (evitando inimigos); o ataque
  mira sempre o inimigo mais próximo, sem necessidade de mira manual.
- Armas se acumulam ao longo da partida (não substituem umas às
  outras): tiro simples → espada giratória → campo de força → e assim
  por diante. Cada arma nova se soma às anteriores.

## Drops e Progressão

- Inimigos derrotados soltam drops, que enchem uma barra de progresso.
- Ao atingir um número de drops (10 no início), o jogador escolhe uma
  skill para melhorar — ou, alternativamente, um combo de múltiplas
  skills de uma vez (mecanismo similar ao "vídeo simulado" já descrito
  na mecânica geral de upgrades do jogo).
- Drops de inimigos também alimentam a restauração da nave: peças que
  os inimigos soltam são usadas para restaurar sistemas (conectando
  com a mecânica de restauração central do jogo).

## Progressão Espacial: Portas Danificadas e Reparo em Cadeia

Conceito central que estrutura o ritmo do Modo 1, conectando combate,
drops e restauração em um único ciclo:

- O jogador começa em uma sala inicial com portas **danificadas/
  trancadas** — não é possível avançar até repará-las.
- Uma primeira horda surge de imediato na sala inicial. Ao ser
  derrotada, dropa material suficiente para reparar **uma** das portas
  da sala (a sala inicial pode ter mais de uma porta, cada uma levando
  a uma sala diferente).
- Reparada a porta, o jogador acessa a próxima sala, onde uma nova
  horda aguarda. Essa horda dropa material para: (a) reparar a porta
  de acesso a uma sala seguinte, e (b) reforçar a defesa de uma sala
  **já visitada** (por exemplo, uma torreta ou sistema na sala
  anterior).
- O ciclo se repete: cada sala nova conquistada tanto abre caminho
  adiante quanto retroalimenta a defesa do que já foi conquistado —
  criando uma progressão onde avançar e fortalecer o que já foi feito
  acontecem em paralelo, não em sequência isolada.

Este conceito depende de:
- Estado de porta "danificada/trancada" vs. "reparada/aberta" — uma
  extensão do estado atual de `Door` (hoje só `open`/`closed`).
- Uma condição de "sala limpa" (todos os inimigos da horda eliminados)
  como gatilho de drop de material de reparo — hoje as portas já abrem
  livremente, sem essa condição.
- Vínculo entre o material dropado e **qual** porta/sala ele repara ou
  reforça — provavelmente um dado adicional em `door_data`.

### Estrutura de Boss Rush (Refinamento da Condição de Vitória)

Baseado em estruturas clássicas e validadas do gênero Horde: a sala
não é vencida por "sobreviver a um timer" isoladamente, mas por
**derrotar o chefão** que chega ao final de uma sequência de combate
de aproximadamente 5 minutos, dividida em ondas com mini-chefes:

- **Onda 1 (normal):** inimigos comuns, com um **mini-chefe** ao
  final. Ao ser derrotado, dropa diretamente cerca de 3 skills, **sem
  exigir vídeo simulado** — recompensa garantida por progresso, não
  por monetização.
- **Onda 2:** repete o padrão (inimigos comuns + mini-chefe), mas com
  um mini-chefe mais forte que o da onda 1, dropando algo
  especialmente valioso ao ser derrotado.
- **Onda final (mais curta que as anteriores):** o chefão surge, com
  uma **barra de vida grande no topo da tela**.
  - A barra muda de cor conforme o dano é recebido (ex: começa
    vermelha).
  - Ao esvaziar, o chefão fica **atordoado**, abrindo uma janela para
    o jogador maximizar dano.
  - **Progressão de dificuldade do chefão (entre visitas/reentradas):**
    o chefão da revisita seguinte começa com uma barra de cor
    diferente (ex: marrom em vez de vermelha), indicando um chefão
    mais resistente/poderoso que o anterior — cada barra derrotada
    dá lugar a uma nova barra de cor distinta, até o chefão cair de
    vez.

> Esta estrutura é a evolução natural da condição de vitória simples
> ("sobreviver X segundos") implementada como primeiro passo na
> Sprint 024. O timer de sobrevivência inicial é, na prática, o
> precursor da contagem regressiva até a chegada do chefão — a versão
> completa substitui "aguentar o tempo" por "aguentar até o chefão
> chegar, e então derrotá-lo". Depende de: sistema de mini-chefes (um
> novo tipo de inimigo, mais forte que "strong" mas mais fraco que o
> chefão), UI de barra de vida de chefe com múltiplas fases coloridas,
> e mecânica de atordoamento (stagger).

### Minigames de Reparo (Ideia Registrada, Escopo Distante)

O ato de reparar um sistema da nave (porta, torreta, sistema de
suporte) não precisa ser instantâneo ao coletar o material — pode se
manifestar como um minigame de puzzle específico para aquele sistema,
dando variedade e um "respiro" mecânico diferente do combate. Lista
inicial de referências conhecidas para inspirar tipos de puzzle (não
fechada, apenas ponto de partida):

- Sudoku
- Match 3
- Pac-Man (labirinto simples)
- Tetris / encaixe de blocos
- Outros a definir conforme o desenvolvimento avançar

> Esta ideia pertence a um horizonte de desenvolvimento distante —
> depende de toda a base de combate, drops e Progressão Espacial já
> estarem maduras antes de fazer sentido investir em minigames de
> puzzle. Registrada aqui para não se perder, sem nenhum compromisso
> de implementação em Sprints próximas.

### Ondas Múltiplas e Material Composto (Refinamento)

Uma sala pode exigir mais de uma onda de inimigos antes de destravar
sua porta, não apenas uma horda única:

- Cada onda, ao ser derrotada, dropa uma peça de material específica
  (ex: uma engrenagem).
- A porta só destrava quando **todas** as peças necessárias tiverem
  sido coletadas — completando, na prática, uma espécie de
  quebra-cabeça de montagem (reunir as peças do reparo).
- Isso pode exigir, inclusive, retornar a salas já visitadas para obter
  material adicional faltante, reforçando a mecânica de idas e vindas
  já prevista no conceito de Reparo em Cadeia.

#### Ondas por Pressão de Tempo, não por Conclusão

A transição entre ondas não espera o jogador eliminar todos os
inimigos da onda atual — ela ocorre em um tempo calculado, e a nova
onda se soma aos inimigos remanescentes da anterior, criando pressão
real para não procrastinar o combate.

- **Cálculo do tempo por onda:** baseado na quantidade de tiros
  necessários para eliminar cada inimigo da onda (HP do inimigo /
  dano do tiro do jogador), multiplicado pelo intervalo entre
  disparos — não um valor fixo arbitrário. Isso faz o tempo de onda
  se ajustar automaticamente conforme o jogador evolui (mais dano,
  mais velocidade de tiro), sem exigir uma fórmula nova a cada
  upgrade implementado.
- **Feedback visual obrigatório:** contagem regressiva na UI
  ("Próxima onda em: Xs"), para que o jogador sinta a urgência e não
  fuja do combate.

> **Observação de gameplay emergente (validada em teste):** o tamanho
> físico da sala afeta naturalmente a dificuldade da pressão de tempo,
> mesmo sem nenhum ajuste manual — em salas grandes (ex: Área de
> Carga), inimigos levam mais tempo para alcançar o jogador, então a
> onda seguinte tende a se acumular com sobras da anterior; em salas
> pequenas (Corredor, Engenharia), o jogador consegue eliminar toda a
> onda antes da próxima começar. Esse efeito não foi projetado
> deliberadamente — surgiu da combinação entre o cálculo de tempo por
> onda e a geometria de cada sala, e vale ser considerado (e talvez
> aproveitado de propósito) ao desenhar futuras salas.

#### Ondas Mistas (dependência: tipos de inimigo)

Ondas posteriores devem misturar inimigos de diferentes níveis de
resistência (ex: onda 1 com inimigos de HP 20-30; onda 2 combinando
HP 30 e 40), refletindo tanto a evolução natural de dificuldade
quanto os upgrades que o jogador já teria adquirido até aquele ponto
(mais dano, velocidade, escudo, campo de força). Esta parte depende da
introdução de múltiplos tipos de inimigo (ver "Tipos de Inimigo" mais
abaixo neste documento) — não implementada nesta fase, que ainda usa
um único tipo de inimigo com HP fixo.

#### Continuidade de Ondas Entre Visitas e Teto de Volume (Refinamento Futuro)

Ao reentrar em uma sala, a numeração de ondas não deveria "reiniciar"
do zero — a sequência de ondas é contínua ao longo da vida da sala:
a primeira visita usa as ondas 1 e 2, a segunda visita (reentrada) usa
as ondas 3 e 4, e assim por diante. Cada número de onda é mais difícil
que o anterior, mas a dificuldade crescente **não deve vir
principalmente de mais inimigos** — crescimento geométrico de
quantidade rapidamente torna o jogo inviável (partidas muito longas ou
efetivamente impossíveis).

- **Quantidade de inimigos tem um teto** (ex: ~18-20 por onda), a
  partir do qual para de crescer em volume.
- **Dificuldade continua subindo via composição**: a proporção de
  inimigos fortes (e, no futuro, outros tipos mais perigosos) aumenta
  a cada onda, mesmo com o total de inimigos estabilizado. Exemplo
  ilustrativo: onda 3 com 15 inimigos (12 fracos + 3 fortes); onda 4
  com 18 inimigos (12 fracos + 6 fortes); onda 5 substituindo parte
  dos fracos por um tipo ainda mais perigoso (ex: os que atiram).
- **Contrapeso reconhecido:** a introdução de múltiplas armas (espada
  giratória, campo de força) deve aumentar a velocidade de eliminação
  do jogador ao longo do tempo — a curva de dificuldade de composição
  precisa ser calibrada considerando esse ganho de poder, não apenas a
  força bruta dos inimigos.

> Esta funcionalidade exige uma mudança de arquitetura: um contador de
> onda contínuo por sala (não reiniciado a cada `spawn_horde()`), e uma
> fórmula de composição que decida a mistura de tipos a partir desse
> número absoluto de onda, com teto de volume. Registrada para
> implementação cuidadosa em Sprint dedicada, não encaixada de forma
> apressada.

### Primeira Vez vs. Revisita

A condição de destravamento **muda** dependendo se é a primeira vez
que a sala é destravada, ou uma revisita posterior:

- **Primeira vez:** a condição completa se aplica — múltiplas ondas,
  coleta de material, montagem do quebra-cabeça de reparo.
- **Revisitas subsequentes:** a porta já está fisicamente reparada;
  a única condição para reabri-la é derrotar a horda (mais desafiadora,
  ver "Rejogabilidade" abaixo) presente naquele momento — sem repetir a
  coleta de material ou montagem.

## Rejogabilidade: Hordas Mais Desafiadoras a Cada Retorno

Ao retornar a uma sala já visitada, o jogador deve enfrentar uma horda
mais desafiadora que a anterior naquela mesma sala — tornando cada
partida única mesmo dentro do mesmo nível, e incentivando o jogador a
não "farmar" segurança revisitando salas fracas repetidamente.

Estatísticas a registrar para sustentar isso (conectando com a seção
de Estatísticas Detalhadas por Jogador, acima):
- Quantas vezes o jogador entrou em cada sala, por nível.
- Pontos totais obtidos naquela sala, e pontos por visita individual.
- **Stardate** de cada visita (data/hora real do jogador), usada para
  construir uma narrativa histórica da progressão do jogador ao longo
  do tempo — não apenas números, mas uma linha do tempo jogável.

### Salas Trancadas nos Dois Sentidos

Uma sala com inimigos vivos tranca **todas** as suas portas — não
apenas a que leva adiante, mas também a que permite recuar. O jogador
que entra em uma sala precisa limpá-la antes de poder sair por
qualquer direção. Essa regra deve ser comunicada claramente ao jogador
(mensagem explicativa), já que cria um compromisso obrigatório ao
entrar.

### Reentradas Limitadas (Sistema de Tentativas)

Reentrar em uma sala já visitada consome uma **reentrada**, um recurso
limitado e regenerável com o tempo — distinto da "Energia" que afeta a
qualidade das skills (ver seção de Upgrades):

- Limite máximo de reentradas acumuláveis (exemplo de referência: 5).
- Regeneração de +1 reentrada a cada intervalo de tempo real (exemplo
  de referência: 1 hora), até o teto máximo.
- Ao esgotar as reentradas disponíveis, o jogador precisa aguardar a
  regeneração para reentrar em uma sala já visitada.
- **Entrar em uma sala/nível pela primeira vez não consome reentrada**
  — o custo se aplica apenas a visitas repetidas.
- Antes de consumir uma reentrada, o jogo deve **confirmar com o
  jogador** (ele pode ter entrado sem intenção de fato reentrar),
  evitando desperdício acidental de um recurso escasso.

> Este sistema é conceitualmente parecido com mecanismos de "energia/
> vidas" comuns em jogos mobile (ex: Candy Crush), aplicado aqui
> especificamente a revisitas de salas — não à ação de jogar em si.

### Sistema de Vidas (Continuar Após Morrer)

Ao morrer (HP zerado) dentro de uma sala com inimigos vivos, o jogador
tem a opção de continuar de onde parou:

- **Continuar via vídeo simulado:** disponível apenas **uma vez** por
  sessão de morte. Se morrer novamente logo em seguida, essa opção não
  está mais disponível — precisa reiniciar a sala/nível.
- **Vidas como recurso limitado:** limite máximo de vidas acumuláveis
  (exemplo de referência: 5), regenerando +1 a cada intervalo de tempo
  real (exemplo de referência: 1 hora), mesmo esquema das Reentradas.
- **Compra com dinheiro real:** vidas extras (além do limite gratuito)
  podem ser adquiridas diretamente com dinheiro real — um dos pontos
  de monetização do jogo.
- **Motivação:** sem essa regra, um jogador quase morto poderia sempre
  escapar pela porta (mesmo que a porta de saída também exija sala
  limpa) como forma de evitar o risco real de morte — o sistema de
  vidas garante que a ameaça de sofrer uma derrota tenha peso real.

> **Status de implementação (Sprint 014):** o núcleo funcional está
> implementado — `Player` possui `lives`/`max_lives`, consome uma vida
> por morte, e revive automaticamente (HP restaurado) enquanto houver
> vidas disponíveis, travando de vez ("game over definitivo") ao
> esgotá-las. **Ainda não implementado:** a distinção entre "vídeo
> simulado, 1 vez por sessão de morte" e "vida como recurso
> persistente" — hoje toda morte simplesmente consome uma vida e
> reviva, sem diferenciar a primeira tentativa (via vídeo) das
> seguintes. Também pendentes: regeneração por tempo real, compra com
> dinheiro real, e qualquer interface de confirmação — dependem de uma
> tela de UI ainda não construída.

> **Nota de consolidação:** o jogo passa a ter três sistemas de
> recurso com estrutura parecida (limite + regeneração por tempo +
> vídeo/compra), mas propósitos distintos — vale manter essa distinção
> clara ao implementar, para não confundir os três em uma única
> variável:
> - **Energia** — reduz a qualidade das skills enquanto baixa; não
>   limita tentativas, apenas desempenho.
> - **Reentradas** — limita quantas vezes o jogador pode revisitar uma
>   sala já vencida.
> - **Vidas** — limita quantas vezes o jogador pode continuar após
>   morrer dentro de uma sessão de horda.

### Saída Antecipada com Progresso Parcial (Ideia em Aberto)

Questão ainda não decidida: se o jogador quiser sair de uma sala antes
de completá-la (aceitando perder o progresso daquela sessão), ele
deveria poder fazê-lo, ficando apenas com os itens já coletados até o
momento da saída — em vez de ficar preso até vencer toda a horda.
Depende da decisão de "ondas múltiplas por sala" (ver Progressão
Espacial) e de como o progresso de sessão é definido — fica registrado
como questão em aberto, a decidir junto da progressão de ondas.

## Visão de Longuíssimo Prazo: Narrativa Histórica e Área de Membros

Ideia de horizonte distante, fora de qualquer escopo próximo: usar o
histórico de stardates e estatísticas do jogador para gerar uma
narrativa pessoal (uma "história de vida" dentro do jogo, no espírito
de simuladores de vida como The Sims), publicável como uma página HTML
individual do jogador — parte de uma futura área de membros pagantes
(assinatura mensal), criando vínculo de longo prazo entre jogador e
jogo.

> Esta ideia está muitos passos além do Modo 1 e da Fase 2 do
> `ROADMAP.md` — registrada aqui apenas para não se perder, sem
> nenhuma dependência técnica imediata. Vale revisitá-la quando o
> jogo já tiver uma base sólida de jogadores e dados reais.

- Inimigos fracos e fortes, variando em resistência.
- Inimigo especial: aparece uma vez por onda, demora mais para matar,
  e concede uma recompensa maior (3 skills bônus) ao ser derrotado.
- Nos primeiros níveis, nenhum inimigo ataca à distância — apenas
  contato direto.
- Em níveis mais avançados, inimigos à distância são introduzidos,
  com tiros **lentos e desviáveis**. A dificuldade pretendida vem do
  **volume e posicionamento** de tiros simultâneos, não da velocidade
  individual de cada projétil.

## Re-arquitetura Espacial: Mapas Contínuos por Nível

Mudança de direção fundamental na estrutura espacial do jogo — visão
original do criador, ajustada agora com mais clareza após revisão.
Substitui o conceito de "sala como tela fixa" por salas maiores que a
tela, conectadas em um mapa contínuo por nível.

### Câmera Seguindo o Jogador

O jogador permanece centralizado na tela; é o mundo (salas, paredes,
portas, inimigos, projéteis) que se desloca visualmente ao redor dele.
Isso permite salas maiores que a tela, adequadas ao formato 16:9
predominante em celulares, com obstáculos e itens espalhados pelo
espaço a ser explorado — não apenas uma sala vista inteira de uma vez.

### Crescimento de Complexidade por Nível

- **Nível 1:** uma única sala, várias vezes maior que o tamanho atual
  de uma sala (referência: 4x o tamanho atual), com uma porta levando
  ao Nível 2.
- **Nível 2:** duas salas conectadas entre si, mais uma porta levando
  ao Nível 3.
- **Padrão geral:** o nível N possui N salas conectadas, com uma porta
  adicional levando ao nível seguinte.
- **A partir do Nível 11:** geração procedural (já registrada na
  Fase 2B do `ROADMAP.md`), com o conceito de jogador "fundador" de
  cada novo nível gerado.

### Transição Cinematográfica Entre Regiões do Mapa

Ao atravessar a porta que leva a uma nova sala/nível, uma cena breve
mostra a nova área em seu estado destruído/danificado, antes de
devolver o controle normal ao jogador — reforçando narrativamente a
mecânica de restauração (o jogador vê o "antes" do que vai reconstruir).

### Impacto na Arquitetura Existente

Esta é a maior mudança estrutural desde o início do projeto — mais
ampla que a virada para o gênero Horde, pois afeta a fundação espacial
(`Room`/`Door`) construída desde a Sprint 002:

- O conceito atual de sala como "tela fixa com 4 paredes visíveis por
  completo" é substituído por salas maiores que a tela, exigindo um
  sistema de câmera/scroll inexistente até aqui.
- A relação entre `Room` e `Door` permanece conceitualmente válida
  (portas ainda conectam espaços), mas a navegação deixa de ser
  "trocar completamente de tela" e passa a ser "revelar uma nova
  região do mesmo mapa contínuo".
- Esta mudança será tratada como uma Sprint dedicada e isolada, por
  seu tamanho e risco — não um ajuste incremental sobre o que já
  existe.

## Percepção de Inimigos e Alcance de Tiro (Raio Único)

Percepção do jogador (o que ele mira) e alcance do tiro (distância que
o projétil percorre antes de desaparecer, mesmo sem atingir nada)
compartilham **o mesmo valor de raio** — decisão consciente para que o
jogador consiga prever exatamente quais inimigos serão afetados ao
ver o indicador visual, sem surpresas.

- O raio é **sempre visível** ao redor do jogador (não apenas quando um
  inimigo entra nele) — feedback claro e constante, mais simples de
  entender do que um indicador condicional.
- Upgrade de raio: aumenta esse valor único (afetando percepção e
  alcance de tiro simultaneamente), até 5 níveis, como os demais
  upgrades de tiro.

## Comportamento de Projétil (Tiro Base)

- **Decisão revisada:** o projétil possui uma distância máxima de
  alcance (ligada ao raio único acima), desaparecendo ao percorrê-la
  mesmo sem atingir nada — substituindo a decisão anterior de "persiste
  até atingir um inimigo ou colidir com uma parede".
- **Nota técnica para implementação:** o projétil deve ser construído
  já prevendo o upgrade futuro de Penetração (abaixo) — ou seja, a
  lógica de colisão não deve simplesmente marcar o projétil como morto
  no primeiro impacto, e sim permitir configurá-lo para sobreviver a
  múltiplos impactos antes de desaparecer, mesmo que o valor inicial
  (sem upgrade) seja "1 impacto".

## Upgrades do Tiro (até 5 níveis cada, upgrades independentes entre si)

- Velocidade do projétil
- Tamanho do projétil
- Penetração (atinge 1 alvo → 2 alvos → 3 alvos, etc.)
- Quantidade de projéteis simultâneos, com padrões de disparo distintos
  (ex: dois tiros retos em paralelo, ou um reto + dois em diagonal,
  ou um reto + um para cima + um para baixo)
- Intervalo entre disparos (cadência de tiro)
- Alcance (raio único de percepção/tiro, ver seção acima)

## Campo de Força (Arma 2)

- Causa dano contínuo a inimigos dentro de sua área, a cada meio
  segundo.
- Dois upgrades independentes, até 5 níveis cada:
  - Área do campo (raio)
  - Dano causado

## Sabre Giratório (Arma 3 — Tema Espacial)

- Uma ou mais lâminas orbitando o jogador (renomeado de "Espada
  Giratória" para manter coerência temática de nave espacial — sem
  espadas medievais; inspirado em sabres de luz).
- Três upgrades independentes, até 5 níveis cada:
  - Quantidade de lâminas
  - Velocidade de giro
  - Dano por lâmina

## Arma Vampírica ("Fang")

Arma nova, ainda a definir em detalhe: dano vinculado a roubo de vida
— parte do dano causado ao inimigo é convertida em cura para o
jogador. Upgrades aumentam tanto o dano causado quanto a fração de
vida roubada (dois eixos independentes).

## Sistema de Armas de Fogo com Munição e Recarga

Diferente do tiro automático de munição infinita já implementado,
armas de fogo temáticas teriam capacidade de pente limitada e tempo de
recarga:

- **Revólver:** poucos tiros por carregamento (5 ou 6 — número exato
  ainda a decidir), reload rápido.
- **Arma pesada:** carregamento maior (ex: 12 tiros), dano por tiro
  mais alto, reload mais lento.
- **Metralhadora:** cadência de disparo muito alta, carregamento
  intermediário.
- Armas mais lentas/pesadas seriam especialmente úteis contra
  chefões (dano concentrado), enquanto armas rápidas seriam melhores
  contra hordas numerosas — diferenciação tática por tipo de ameaça.

## Padrões de Tiro Múltiplo (Escolha do Jogador)

Diferente do disparo automático simples atual (sempre mira o inimigo
mais próximo em linha reta), upgrades futuros permitiriam escolher um
padrão de disparo:

- Diagonal (múltiplos tiros se abrindo em ângulo)
- Linha reta (múltiplos tiros na mesma direção, um atrás do outro ou
  em paralelo)
- Quatro cantos (tiros simultâneos em direções ortogonais)

## Escudo

Item de defesa a detalhar — registrado como conceito, sem mecânica
definida ainda (ex: pode ser um bloqueio de dano temporário, uma
barreira com HP próprio, ou redução percentual de dano recebido).

## Padronização de Eixos de Upgrade (Decisão de Arquitetura Pendente)

Cada arma/skill deveria seguir um conjunto padronizado de eixos de
upgrade possíveis (não necessariamente todos aplicáveis a toda arma),
para manter consistência de dados e reduzir a necessidade de inventar
uma estrutura nova a cada arma:

- Quantidade (de projéteis, lâminas, etc.)
- Força/Dano
- Velocidade (de disparo, de movimento do projétil/lâmina, ou de giro)
- Raio/Alcance
- Eixos específicos de uma arma (ex: fração de roubo de vida do Fang,
  capacidade de pente e tempo de reload das armas de fogo)

> Definir essa padronização antes de implementar o sistema de escolha
> de skills evita retrabalho — cada arma nova poderia reaproveitar a
> mesma estrutura de dados de upgrade, preenchendo apenas os eixos que
> fizerem sentido para ela.

## Tipos de Inimigo (Taxonomia)

Categorias de inimigo planejadas, cada uma com regras próprias de
vulnerabilidade a armas e/ou comportamento de ataque:

- **Terrestres** — o tipo padrão atual. Recebem dano de qualquer arma
  (tiro, espada giratória, campo de força).
- **Aéreos** — vulneráveis apenas a projétil ou campo de força; imunes
  a armas de contato/melee (ex: espada giratória não os afeta).
- **Ativos** — atacam à distância. Um padrão de ataque específico é o
  "cuspe venenoso": um projétil que, ao atingir o jogador, gruda nele e
  causa dano contínuo (não instantâneo) por alguns segundos.
- **Residual (morto-vivo)** — causa dano por contato normalmente
  enquanto vivo (como um Terrestre comum); ao ser derrotado, deixa uma
  poça de gosma no chão que também causa dano por contato — o perigo
  não termina com a morte do inimigo, apenas muda de forma.

> Esta taxonomia é maior que o escopo de qualquer Sprint isolada.
> Implementação planejada de forma incremental: primeiro dois tipos
> simples dentro da categoria Terrestre (fraco/forte, diferindo apenas
> em HP/tamanho/cor), depois expandindo para as demais categorias
> conforme os sistemas de armas (espada, campo de força) e de dano ao
> longo do tempo forem implementados.

> **Nota sobre nomenclatura:** hoje os tipos usam chaves técnicas
> (`"weak"`, `"strong"`) como identificador em `settings.ENEMY_TYPES` —
> um placeholder deliberado. Nomear os inimigos de verdade (ex: um
> nome próprio para cada criatura) é uma tarefa futura de identidade
> visual/narrativa, não uma mudança de arquitetura: como o tipo já é
> uma chave de dicionário, trocar `"weak"` por um nome próprio no
> futuro não exige alterar nenhuma lógica de código, apenas a
> configuração — as estatísticas, o histórico por visita, e todo o
> resto já registram e exibem por essa chave, prontos para a
> nomenclatura definitiva quando ela existir.

## Penalidade por Dano Recebido

Ao ser atingido, o jogador perde uma pequena porcentagem dos pontos
acumulados (ex: 0,01%) — o valor da penalidade varia por tipo de
inimigo, assim como os pontos ganhos ao eliminá-lo variam por tipo.
Isso adiciona uma dimensão de risco/recompensa às estatísticas já
descritas acima, incentivando o jogador a evitar dano, não apenas
acumular eliminações.

## Energia Afetando Qualidade das Skills

Uma reserva de energia diminui com o uso das habilidades e regenera
com o tempo. Enquanto a energia está baixa, a qualidade/potência das
skills é proporcionalmente reduzida, voltando ao normal conforme a
energia regenera. Isso introduz um ritmo de "gerenciamento de recurso"
à jogabilidade, além do combate direto.

## Power-ups Passivos

Upgrades que não afetam diretamente o dano ou alcance de ataque, mas
melhoram a experiência/eficiência geral do jogador:

- **Ímã:** atrai drops coletáveis dentro de um raio próprio, distinto
  do raio de percepção/alcance de tiro já existente — reduz a
  necessidade de andar até cada drop individualmente. Upgradável em
  níveis, aumentando o raio de atração.
- **Regeneração de vida:** recupera uma pequena quantidade de HP ao
  longo do tempo, de forma passiva, sem depender de itens ou fontes de
  cura específicas. Upgradável em níveis, aumentando a taxa de
  regeneração.

## Coleta Automática de Gemas Remanescentes

Duas ideias complementares para lidar com gemas de pontos não
coletadas durante o combate:

- **Ao vencer a sala sem morrer:** todas as gemas ainda não coletadas
  são puxadas automaticamente até o jogador no momento da vitória —
  uma recompensa por sobreviver de forma limpa, sem deixar valor
  "perdido" no chão.
- **Mini-ímã esporádico:** um item raro que aparece ocasionalmente
  pela sala durante o combate; se o jogador passar por cima dele,
  todas as gemas próximas são recolhidas de uma vez — uma variação de
  curto prazo do power-up de ímã permanente, sem exigir upgrade.

> Ambas as ideias dependem da existência de drops físicos coletáveis
> no mundo (Sprint 026) — a versão inicial desta Sprint entrega apenas
> a gema básica (círculo proporcional ao valor, coleta por
> proximidade, permanece na tela até ser coletada). As duas mecânicas
> de coleta automática ficam registradas para uma Sprint futura.

## Interface de Usuário (UI) — Visão Geral

Elementos a exibir visualmente, conectando os sistemas acima:
- Barra de HP do jogador.
- Indicadores por skill (ex: "Skill X — Nível 3"), mostrando o nível
  atual de cada upgrade adquirido.
- Barra de progresso de drops (rumo à próxima escolha de skill).
- Indicador de energia (afetando visualmente a qualidade das skills
  quando baixa).
- **Contador de visitas por sala (fixo na versão final):** exibido ao
  lado do nome da sala, mostrando o total de vezes que o jogador já a
  visitou. Ao tocar/clicar nesse contador, expande uma lista com as
  **5 melhores pontuações** obtidas naquela sala, uma por visita (ex:
  "4.500 pontos", "8.568 pontos"), permitindo ao jogador comparar seu
  próprio desempenho histórico naquele ambiente especificamente.

> Esta versão final substitui o texto de debug atual ("Room X" +
> contador simples), que serve por enquanto como validação técnica
> antes da UI definitiva ser construída.

Builds diferentes de upgrade (ex: priorizar cadência de tiro vs.
priorizar divisão de tiros) devem gerar resultados mensuravelmente
diferentes — tempo para completar uma horde, pontos obtidos, inimigos
eliminados — permitindo comparar jogadores não apenas por "quem venceu",
mas por qualidade da estratégia escolhida (similar a rankings de nível
em jogos como Angry Birds, baseados em performance dentro do nível, não
apenas em conclusão).

## Ranking por Qualidade de Escolha

Builds diferentes de upgrade (ex: priorizar cadência de tiro vs.
priorizar divisão de tiros) devem gerar resultados mensuravelmente
diferentes — tempo para completar uma horde, pontos obtidos, inimigos
eliminados — permitindo comparar jogadores não apenas por "quem venceu",
mas por qualidade da estratégia escolhida (similar a rankings de nível
em jogos como Angry Birds, baseados em performance dentro do nível, não
apenas em conclusão).

## Dois Tipos de Progressão: Vitalícia vs. de Partida

- **Progressão vitalícia (permanente):** melhorias ganhas apenas ao
  completar um nível **pela primeira vez**. Revisitar um nível já
  concluído não concede mais essas melhorias — apenas a chance de
  melhorar a pontuação/placar daquela sessão específica.
- **Progressão de partida:** pontos obtidos por drops de inimigos
  dentro de uma sessão de horda, usados para desbloquear upgrades
  temporários (via barra de progresso) e alimentar o ranking daquele
  nível/sala — não necessariamente permanentes.

## Moeda do Jogo

Ganha ao completar um nível pela primeira vez (não ao revisitar).
Utilizada para comprar itens na loja (armadura, armas, etc.) de forma
"honesta" — sem depender de vídeos simulados ou compras com dinheiro
real.

## Dois Rankings Distintos: Honesto vs. VIP

- **Ranking Honesto:** apenas jogadores que não utilizaram o
  mecanismo de "vídeo simulado" (considerado cheat para fins de
  ranking) nem compras de pacotes de benefício. Missões específicas
  podem recompensar essa consistência (ex: completar os 3 primeiros
  níveis sem usar vídeo/compra concede moeda extra).
- **Ranking VIP:** inclui jogadores que utilizam o recurso de vídeo ou
  compram pacotes de benefício com dinheiro real.

> Esta separação evita o problema comum em jogos com atalhos pagos: um
> único ranking misturando os dois grupos desmotiva quem joga de forma
> honesta. Mantê-los distintos preserva competitividade justa para
> ambos os públicos.

## Estatísticas Detalhadas por Jogador

Além do resultado agregado (pontos totais, tempo de conclusão), o jogo
deve registrar estatísticas granulares por partida: quantos inimigos de
cada tipo foram eliminados, quantos pontos cada tipo rendeu, por nível
ou onda. Esse detalhamento tem duplo propósito:

- **Para o jogo:** alimenta o ranking por qualidade de escolha (acima)
  com dados reais de desempenho, não apenas o placar final.
- **Para a Academia:** os próprios dados do jogo se tornam material
  didático de ciência de dados e análise de dados — os alunos podem
  aprender a analisar estatísticas reais geradas pelo jogo que eles
  mesmos constroem, em vez de datasets genéricos de tutorial.

> **Dependência de dados (consolidada):** tanto o ranking por qualidade
> de escolha quanto as estatísticas detalhadas dependem da mesma
> estrutura de registro de partida — build escolhida, inimigos
> eliminados por tipo, pontos por tipo, por nível/onda, tempo de
> conclusão. Vale desenhar essa estrutura de dados já pensando nas
> duas necessidades desde a primeira Sprint de progressão/persistência,
> mesmo que a implementação completa (ranking, dashboards de análise)
> só aconteça na Fase 2B do `ROADMAP.md`.

> **Primeira implementação concreta (Sprint 024):** contador fixo, por
> tipo de inimigo, de quantos foram eliminados e quantos pontos cada
> tipo gerou (ex: "Fracos: 10 mortos, 15 pts | Fortes: 3 mortos, 12
> pts"), exibido inicialmente no painel de debug — futuramente
> migrando para uma tela dedicada de estatísticas, à medida que mais
> dados forem acumulados.

## Ordem de Implementação Sugerida

1. Ataque automático mirando o inimigo mais próximo + inimigos podendo
   morrer (fundação mínima).
2. Condição de "sala limpa" (todos os inimigos eliminados) + portas
   danificadas/trancadas até então — base da Progressão Espacial.
3. Sistema de drops e barra de progresso.
4. Escolha de skill (1 ou combo).
5. Vínculo de material dropado a reparo de porta específica e reforço
   de defesa em salas já visitadas (Progressão Espacial completa).
6. Segunda arma (espada giratória) provando o sistema de acumulação.
7. Diferenciação de inimigos (fraco/forte/especial).
8. Inimigos à distância (fase avançada).

## Pesquisa de Referência: Gênero Horde Survivor / Bullet Heaven

Pesquisa de mercado conduzida para embasar as próximas decisões de
design (Sprints 024-026), com fontes reais do gênero:

- **Piso contínuo de inimigos, não ondas discretas com vazio entre
  elas:** Vampire Survivors define uma quantidade mínima de inimigos
  vivos por onda; se cair abaixo do mínimo, novos inimigos são
  gerados até repor a cota — garantindo que sempre haja ação, sem
  momentos "mortos". Adotado como base da Sprint 024, substituindo o
  modelo de 2 ondas discretas por um piso mantido continuamente, com
  dificuldade crescendo pela composição de tipos, não pela quantidade.
- **Risco real de crescimento descontrolado:** desenvolvedores
  relataram publicamente o mesmo problema já intuído pelo criador
  deste jogo — escalonar dificuldade apenas por quantidade cria um
  ponto de ruptura ("massa crítica") após o qual o jogo vira fácil
  demais ou impossível cedo demais. Confirma a decisão de já
  registrada de nunca escalar dificuldade só por volume.
- **Dificuldade adaptativa por desempenho real:** sistemas de wave
  design mais sofisticados ajustam quantidade, HP, velocidade e dano
  dos inimigos com base na taxa de sobrevivência do próprio jogador
  (ex: sobrevivência acima de 80% aumenta a dificuldade; abaixo de
  30% reduz), usando curvas configuráveis (linear, exponencial, ou em
  degraus). Planejado para a Sprint 026.
- **Progressão de upgrades como motor real do jogo:** análises do
  gênero apontam que o sucesso do jogador depende mais de quais
  upgrades ele escolheu e como os combinou do que de habilidade
  mecânica (reflexo, precisão) — reforçando a importância do sistema
  de drops e escolha de skills já em desenvolvimento.
- **XP/pontos como objeto físico coletável, não instantâneo:** a
  mecânica mais definidora do gênero é o inimigo derrotado soltar um
  objeto no mundo (gema, pedra brilhante) que o jogador precisa
  encostar para coletar — diferente do sistema atual (pontos vão
  direto ao contador). Planejado para a Sprint 025, junto de um
  power-up de ímã (raio de atração de itens, independente do raio de
  percepção/tiro já existente).
- **Comportamento de movimento como eixo pouco explorado:** inspirado
  nos fantasmas de Pac-Man — cada um com uma regra de perseguição
  diferente (Blinky: perseguição direta; Pinky: emboscada, mirando à
  frente da direção do jogador; Inky: usa a posição de outro inimigo
  combinada à do jogador; Clyde: persegue de longe, foge de perto) —
  planejado como diferenciação de comportamento por tipo de inimigo
  na Sprint 026, além da diferenciação por atributos já existente.
- **Formação de grupo para inimigos à distância:** inimigos do tipo
  Ativo (os que atiram) não avançam até o contato — ao atingir uma
  distância-alvo do jogador, param e se organizam em uma formação
  (ex: meia-lua), mantendo essa posição enquanto disparam. Isso
  distingue mecanicamente inimigos de contato (que avançam sempre) de
  inimigos à distância (que buscam manter alcance ideal), e cria
  variedade tática real no combate. Planejado para a Sprint 026, junto
  dos demais comportamentos de perseguição diferenciados.

### Plano Consolidado — Blocos Temáticos (Pós-Sprint 026)

> Atualização: o plano anterior (por número de Sprint) ficou
> desatualizado conforme o desenvolvimento avançou além do previsto.
> A partir daqui, o planejamento passa a ser por **bloco temático**
> (ver Seção 5 do `METODOLOGIA.md` — Agrupamento Temático de Sprints),
> sem fixar quantas Sprints cada bloco vai exigir — cada bloco se
> divide em Sprints específicas conforme a necessidade for aparecendo
> durante o desenvolvimento.

**Ordem definida (25/07/2026):**

1. **Bloco de Obstáculos de Sala** — elementos físicos dentro das
   salas, hoje inexistentes (o piso é vazio). Dois tipos coexistindo:
   - **Fixos:** bloqueiam movimento e linha de tiro, servindo de
     cobertura tática, sem poder ser destruídos.
   - **Destrutíveis:** podem ser eliminados pelo jogador (atirando),
     revelando espaço livre e possivelmente concedendo recompensa
     (gema, material) ao serem destruídos.
   - Motivação: o espaço de jogo hoje é "vazio" demais; obstáculos
     também tornam os power-ups futuros (ímã, padrões de tiro)
     mecanicamente mais interessantes, ao interagir com o ambiente.

2. **Bloco de Power-ups** — começando pelo ímã (já conectado ao
   sistema de gemas da Sprint 026), expandindo para os demais itens já
   registrados neste documento (regeneração de vida, Fang, armas de
   fogo com munição, padrões de tiro múltiplo, sabre giratório,
   escudo), um de cada vez, conforme a demanda for aparecendo.

3. **Bloco de Entidades de Chefes** — mini-chefes, chefes e chefões,
   implementando a Estrutura de Boss Rush já detalhada neste
   documento (barra de fases coloridas, mecânica de atordoamento,
   drops garantidos de mini-chefes sem exigir vídeo).

4. **Bloco de Restauração da Nave** — início da mecânica central de
   "Reparo em Cadeia" (Progressão Espacial), ainda não iniciada:
   portas danificadas, material de reparo, vínculo entre drops e
   sistemas específicos da nave.

5. **Bloco de Refinamento Geral** — ao final dos blocos anteriores,
   uma ou mais Sprints dedicadas a revisar e polir o que já foi
   construído em modo protótipo: ajustes de sprite/visual definitivo
   (hoje tudo é placeholder geométrico), balanceamento fino,
   comportamentos de linha de visão/obstáculo mais sofisticados,
   polimento geral de UX. Registrado desde já porque o volume de itens
   "funcional, mas ainda protótipo" tende a crescer conforme os blocos
   anteriores avançam — nem tudo precisa ser perfeito na primeira
   implementação, mas nada deve ser esquecido de revisar depois.

Esta ordem prioriza primeiro tornar o espaço de jogo mais rico
(obstáculos) antes de expandir a variedade de combate (power-ups e
chefes), deixando a mecânica narrativa central (restauração) para
depois que a base de combate estiver mais madura, e reservando um
momento explícito de polimento geral ao final.

---

# Histórico

## v4.8
- Revisado o conceito de Obstáculo Destrutível: corroído apenas por
  inimigos (não pelo tiro do jogador), encolhendo visualmente até
  sumir, sem soltar recompensa ao jogador — funciona como defesa
  temporária, não como alvo de destruição pelo próprio jogador.
- Adicionada observação de refinamento: preferir feedback visual sem
  barra de HP quando possível (encolhimento, cor, opacidade).

## v4.7
- Adicionado Índice navegável no topo do documento e seção
  "Pendências por Tema (Índice Rápido)", consolidando o que já foi
  registrado mas ainda não implementado, organizada por bloco.
- Adicionado 5º bloco ao Plano Consolidado: "Bloco de Refinamento
  Geral" (sprites reais, balanceamento fino, polimento de UX),
  reservado para o final dos demais blocos.
- Registrada implementação de linha de visão bloqueada por obstáculo
  na mira automática (`_has_line_of_sight`, via `Rect.clipline`) —
  jogador deixa de "enxergar através de paredes" ao escolher alvo.

## v4.6
- Substituído plano consolidado desatualizado (por número de Sprint)
  por novo plano de 4 Blocos Temáticos: Obstáculos de Sala (fixos e
  destrutíveis), Power-ups, Entidades de Chefes, e Restauração da
  Nave — nessa ordem, sem fixar quantidade de Sprints por bloco.

## v4.5
- Adicionada seção de Coleta Automática de Gemas Remanescentes: auto-
  ímã ao vencer sala sem morrer, e mini-ímã esporádico durante o
  combate. Registrado como dependente da versão básica de drops
  físicos (Sprint 026).

## v4.4
- Renomeada "Espada Giratória" para "Sabre Giratório", mantendo tema
  espacial (sem espadas medievais). Adicionadas: arma vampírica
  ("Fang", roubo de vida), sistema de armas de fogo com munição/reload
  (revólver, pesada, metralhadora), padrões de tiro múltiplo
  escolhíveis (diagonal, linha reta, quatro cantos), conceito de
  escudo, e nota de padronização de eixos de upgrade entre armas.

## v4.3
- Adicionada seção de Power-ups Passivos: ímã (raio de atração
  próprio, distinto do raio de percepção/tiro) e regeneração de vida
  passiva, ambos upgradáveis em níveis.

## v4.2
- Adicionada nota sobre nomenclatura de inimigos: chaves técnicas
  atuais ("weak"/"strong") são placeholder deliberado; nomear os
  inimigos de verdade no futuro é apenas mudança de configuração, não
  de arquitetura, já que todo o sistema de estatísticas já opera por
  chave de dicionário.

## v4.1
- Adicionada Estrutura de Boss Rush: ~5 minutos de combate com
  mini-chefes ao final da onda 1 e 2 (drops garantidos, sem vídeo),
  culminando em chefão com barra de fases coloridas e mecânica de
  atordoamento. Registrado como evolução natural do timer de
  sobrevivência simples implementado na Sprint 024.

## v4.0
- Adicionada ideia de Minigames de Reparo: cada sistema restaurado
  poderia se manifestar como um puzzle específico (Sudoku, Match 3,
  Pac-Man, Tetris, etc.), lista inicial não fechada. Registrado como
  horizonte distante, sem compromisso de implementação próxima.

## v3.9
- Adicionado padrão de formação de grupo (meia-lua) para inimigos à
  distância: param a uma distância-alvo e se organizam em formação
  enquanto atacam, em vez de avançar até o contato. Planejado para a
  Sprint 026, junto dos demais comportamentos de perseguição.

## v3.8
- Adicionada pesquisa de referência do gênero Horde Survivor/Bullet
  Heaven (Vampire Survivors e outros), validando decisões já tomadas
  (evitar crescimento por quantidade) e trazendo novos conceitos:
  piso contínuo de inimigos, drops físicos coletáveis, ímã como
  power-up, dificuldade adaptativa por desempenho, e comportamentos
  de perseguição diferenciados por tipo (inspirados em Pac-Man).
  Consolidado plano das Sprints 024-026.

## v3.7
- Adicionado refinamento futuro: continuidade de numeração de ondas
  entre visitas de uma sala (não reiniciar a cada reentrada), com teto
  de volume de inimigos e dificuldade crescente via composição de
  tipos, não via crescimento geométrico de quantidade. Registrado
  como Sprint dedicada, não implementado ainda.

## v3.6
- Adicionada a Taxonomia de Tipos de Inimigo: Terrestres (dano de
  qualquer arma), Aéreos (só projétil/campo de força, imunes a
  melee), Ativos (ataque a distância, incluindo cuspe venenoso com
  dano contínuo), e Residual (poça de gosma pós-morte, dano por
  contato). Registrada implementação incremental, começando por dois
  tipos simples de Terrestre.

## v3.5
- Registrada observação de gameplay emergente: tamanho da sala afeta
  a dificuldade da pressão de tempo entre ondas (salas grandes
  acumulam sobras da onda anterior; salas pequenas permitem limpar
  antes da próxima começar) — não projetado deliberadamente, validado
  em teste real.

## v3.4
- Detalhado o mecanismo de Ondas por Pressão de Tempo: transição
  ocorre em tempo calculado (tiros necessários × intervalo de disparo),
  não por conclusão da onda atual — inimigos se acumulam se o jogador
  demorar. Registrada dependência de Ondas Mistas em múltiplos tipos
  de inimigo (ainda não implementados).

## v3.3
- Adicionado status de implementação ao Sistema de Vidas: núcleo
  funcional implementado (Sprint 014), com nota explícita do que
  ainda falta (distinção vídeo-1x vs. vida persistente, regeneração
  por tempo, compra, UI de confirmação).

## v3.2
- Adicionado à UI: contador de visitas por sala (fixo na versão
  final), expansível ao toque para mostrar as 5 melhores pontuações
  daquela sala.

## v3.1
- Adicionado Sistema de Vidas (continuar após morrer, 1 vez via vídeo,
  limite regenerável por tempo, compra com dinheiro real) — evita que
  o jogador escape pela porta como forma de negar risco de morte.
- Adicionada nota de consolidação distinguindo os três sistemas de
  recurso do jogo: Energia (qualidade de skills), Reentradas (limite
  de revisitas), e Vidas (limite de continuar após morrer).

## v3.0
- Adicionadas: regra de Salas Trancadas nos Dois Sentidos (jogador
  precisa limpar a sala para sair, não só para avançar), sistema de
  Reentradas Limitadas (recurso regenerável por tempo, distinto da
  Energia de skills, com confirmação antes de consumir), e questão em
  aberto sobre Saída Antecipada com Progresso Parcial.

## v2.9
- Revisado: percepção de inimigo e alcance de tiro passam a
  compartilhar um único raio (jogador prevê exatamente quem é afetado),
  com indicador visual sempre visível (não mais condicional).
- Revisado: projétil passa a ter distância máxima de alcance
  (desaparece ao percorrê-la), substituindo a decisão anterior de
  persistir até atingir algo. Registrada nota técnica: implementar já
  prevendo o upgrade futuro de Penetração (múltiplos impactos antes
  de desaparecer).

## v2.8
- Expandida a Progressão Espacial: ondas múltiplas por sala com
  material composto (quebra-cabeça de reparo), e distinção explícita
  entre condição de destravamento na primeira vez (ondas + material)
  vs. revisitas subsequentes (apenas derrotar a horda).

## v2.7
- Adicionadas as seções: Dois Tipos de Progressão (vitalícia vs. de
  partida), Moeda do Jogo, e Dois Rankings Distintos (Honesto vs.
  VIP) — separando claramente progressão permanente (ganha só na
  primeira conclusão de nível) de progressão de sessão, e evitando
  misturar jogadores que usam atalhos pagos com os que não usam no
  mesmo ranking.

## v2.6
- Adicionada a seção "Re-arquitetura Espacial: Mapas Contínuos por
  Nível" — câmera seguindo o jogador, salas maiores que a tela,
  crescimento de complexidade por nível (nível N = N salas), e
  transição cinematográfica entre regiões do mapa. Marcada como
  mudança estrutural de maior impacto desde o início do projeto,
  a ser tratada como Sprint dedicada e isolada.
- Adicionadas Penalidade por Dano Recebido, Energia afetando Skills,
  e visão geral de UI ao backlog de upgrades.

## v2.5
- Adicionada seção de Rejogabilidade (hordas mais desafiadoras a cada
  retorno à mesma sala) e registro de Stardate por visita.
- Registrada visão de longuíssimo prazo: narrativa histórica do
  jogador e área de membros pagantes com página individual — sem
  dependência técnica imediata.

## v2.4
- Adicionada a seção "Progressão Espacial: Portas Danificadas e
  Reparo em Cadeia" — conceito central conectando combate, drops e
  restauração: portas trancadas até a sala ser limpa, material
  dropado reparando a próxima porta e reforçando salas já visitadas.
  Reordenada a Ordem de Implementação Sugerida para refletir essa
  dependência.

## v2.3
- Adicionadas Estatísticas Detalhadas por Jogador ao backlog: registro
  granular de inimigos eliminados por tipo/nível, com duplo propósito
  (alimentar ranking e servir de material didático de ciência de
  dados para a Academia). Consolidada a nota de dependência de dados
  do ranking e das estatísticas em um único ponto.

## v2.2
- Expandido o Backlog Detalhado do Modo 1: upgrades independentes de
  tiro (velocidade, tamanho, penetração, quantidade, cadência), campo
  de força e espada giratória (5 níveis cada atributo), percepção de
  inimigos com feedback visual, e conceito de ranking por qualidade de
  escolha de build (com nota de dependência de dados).

## v2.1
- Adicionado Backlog Detalhado do Modo 1: sistema de ataque automático,
  armas acumulativas, drops/progressão, tipos de inimigo, e ordem de
  implementação sugerida.

## v2.0
- Mudança de direção: de jogo relaxante para jogo de sobrevivência
  estilo Horde, com dois modos de combate (interno e espacial) e
  progressão dupla e permanente (jogador e nave).
- Registrado impacto na arquitetura já construída (Sprints 001-004).

## v1.0
- Documento criado.
- Definida a visão inicial do Forgotten Ship (jogo relaxante).
