# Forgotten Ship
## VISAO.md

> **Versão:** 2.8
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

- Upgrade de raio de percepção: aumenta a distância em que o jogador
  "nota" inimigos.
- Feedback visual: um círculo discreto ao redor do jogador, visível
  apenas quando um inimigo está dentro desse raio (não fica sempre
  visível).

## Comportamento de Projétil (Tiro Base)

- Um projétil não desaparece sozinho após uma distância fixa: ele
  persiste até atingir um inimigo ou colidir com uma parede.

## Upgrades do Tiro (até 5 níveis cada, upgrades independentes entre si)

- Velocidade do projétil
- Tamanho do projétil
- Penetração (atinge 1 alvo → 2 alvos → 3 alvos, etc.)
- Quantidade de projéteis simultâneos, com padrões de disparo distintos
  (ex: dois tiros retos em paralelo, ou um reto + dois em diagonal,
  ou um reto + um para cima + um para baixo)
- Intervalo entre disparos (cadência de tiro)

## Campo de Força (Arma 2)

- Causa dano contínuo a inimigos dentro de sua área, a cada meio
  segundo.
- Dois upgrades independentes, até 5 níveis cada:
  - Área do campo (raio)
  - Dano causado

## Espada Giratória (Arma 3)

- Uma ou mais espadas orbitando o jogador.
- Três upgrades independentes, até 5 níveis cada:
  - Quantidade de espadas
  - Velocidade de giro
  - Dano por espada

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

## Interface de Usuário (UI) — Visão Geral

Elementos a exibir visualmente, conectando os sistemas acima:
- Barra de HP do jogador.
- Indicadores por skill (ex: "Skill X — Nível 3"), mostrando o nível
  atual de cada upgrade adquirido.
- Barra de progresso de drops (rumo à próxima escolha de skill).
- Indicador de energia (afetando visualmente a qualidade das skills
  quando baixa).

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

---

# Histórico

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
