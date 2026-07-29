# Forgotten Ship
## VISAO.md

> **Versao:** 6.0
> **Projeto:** Jogo 01 da A1 Game Academy
>
> **Papel deste documento (redefinido na v6.0):** VISAO.md registra o
> CONCEITO do jogo e as DECISOES DE DESIGN JA FECHADAS, com o raciocinio
> por tras de cada uma -- e' o material que explica "o que e esse jogo
> e por que ele e assim", util tanto para retomar o projeto quanto para
> o material didatico do curso. Ele NAO e' mais um checklist operacional
> de pendencias -- isso agora vive exclusivamente em CONTEXTO_PROJETO.md
> (o "onde estamos agora"), evitando duplicacao entre os dois documentos.

---

# Proposito

Este documento descreve a visao do jogo **Forgotten Ship**.
Ele complementa o PROJETO_MESTRE.md, que define as regras da academia.

> **Nota de mudanca de direcao (v2.0):** a visao original (v1.0) descrevia
> um jogo relaxante, sem combate. Esta versao substitui esse conceito por
> um jogo de sobrevivencia estilo Horde, mantendo a restauracao da nave
> como mecanica central de defesa.

---

# Conceito

Forgotten Ship e' um jogo de sobrevivencia ambientado em uma nave espacial
abandonada, a deriva e sob ataque constante.

O jogador restaura os sistemas da nave -- e cada sistema restaurado se torna
parte da defesa contra as ondas de inimigos. Restaurar nao e' uma atividade
paralela a sobrevivencia: **e' a forma de sobreviver**.

---

# Experiencia

O objetivo e' transmitir:

- Tensao crescente (ondas de inimigos)
- Satisfacao estrategica ao decidir o que restaurar e o que evoluir primeiro
- Sensacao de poder crescente, tanto do jogador quanto da propria nave
- Progresso tangivel e **permanente** entre partidas

---

# Protagonista

Um alienigena encontra uma nave abandonada, a deriva em territorio hostil,
e precisa restaura-la para sobreviver -- tanto as ondas de ameacas quanto
ao abandono da propria nave.

---

# Mecanica Principal

O jogo alterna entre dois modos de combate, cada um com sua propria
progressao permanente.

## Modo 1 -- Horde Interna (a pe, dentro da nave)

O jogador enfrenta ondas de inimigos dentro da nave. Inimigos derrotados
dropam pontos, que acumulados sobem o **nivel do jogador**.

Ao subir de nivel, o jogador escolhe entre 3 upgrades (sistema de
escolha real, nao mais upgrade automatico -- decisao validada por
pesquisa de mercado do genero horde survivor/bullet heaven: jogos bem
avaliados usam escolha entre opcoes como principal gerador de
"profundidade de build", enquanto upgrade automatico entrega progressao
sem nenhuma decisao real do jogador).

Upgrades do jogador sao **permanentes** entre partidas, aumentando a
dificuldade proporcionalmente para manter o desafio.

Restaurar sistemas da nave nesta fase gera dois tipos de beneficio:

- **Defesa ativa** -- o sistema passa a agir sozinho (ex: uma torreta
  automatica na sala).
- **Fortalecimento do jogador** -- o sistema melhora diretamente as
  capacidades do jogador (ex: mais HP).

## Modo 2 -- Horde de Nave (combate espacial)

A cada 10 ondas da Horde Interna, a cena muda: a nave passa a ser atacada
por naves menores em combate espacial. Progressao separada da
progressao do jogador (progresso da nave).

## Progressao Dupla e Permanente

- **Progresso do Jogador** -- upgrades pessoais, ganhos no Modo 1.
- **Progresso da Nave** -- upgrades da nave, ganhos no Modo 2.

---

# Fora do Escopo do MVP Atual

- Multiplayer
- Mundo aberto / exploracao de planetas
- Venda e troca de naves
- **Modo de Sobrevivencia**: modo alternativo sem teto de power-ups,
  dificuldade escalando com o tempo; desbloqueado apos restaurar a
  primeira nave; jogador escolhe entre naves ja exploradas (variacao de
  cor/estilo) para jogar nesse modo.

---

# Impacto na Arquitetura Existente

As Sprints 001-004 construiram o sistema de Room e Door pensando em
navegacao calma entre salas, sem nocao de inimigos, restauracao,
progressao persistente ou combate espacial. A mudanca de direcao (v2.0)
exigiu novas Sprints dedicadas a esses sistemas -- a arquitetura de
Room/Door continua util como base de navegacao do Modo 1, estendida
progressivamente conforme cada bloco tematico avanca.

---

# Decisoes de Design Fechadas -- Bloco de Power-ups

## Distribuicao de Alvo Entre Armas Automaticas

Cada arma automatica mira uma posicao diferente na fila de proximidade
ao player -- Tiro base=1o mais proximo, Sifao de Energia=2o, Phaser
Leve=3o, Canhao de Plasma=4o, Metralhadora de Pulso=5o. Decisao tomada
para que cada arma tenha presenca tatica propria em combate, em vez de
todas mirarem o mesmo alvo (o que tornaria armas adicionais
redundantes). Todas resilientes a poucos alvos: miram o mais distante
disponivel em vez de ficarem mudas quando a horda esta pequena --
justamente o cenario onde concentrar fogo mais importa.

## Sistema de Escolha de 3 Opcoes (Substitui Upgrade Automatico)

Ao subir de nivel, o jogo pausa e sorteia 3 upgrades entre os
disponiveis, com regras de arquitetura proprias:

- **Grupos de exclusividade permanente:** algumas categorias (ex:
  Tiro Multiplo) tem ramos irmaos que se excluem mutuamente apos a
  primeira escolha -- escolher "Diagonal" remove "Paralelo" e
  "Quadrantes" da lista de opcoes para sempre, especializando aquela
  arma permanentemente.
- **Pre-requisitos em cadeia:** um eixo so aparece como opcao depois
  que o eixo base atingir um nivel minimo -- cria sensacao de
  progresso e novidade a cada nivel, em vez de toda a arma disponivel
  de uma vez.
- **Slots crescentes por nivel:** o jogador comeca com poucos slots de
  armas/passivos simultaneos, e libera mais conforme sobe de nivel --
  early game mais simples, late game com mais opcoes simultaneas.
  Categorias consideradas parte do "Tiro base" (Tiro Multiplo e os
  eixos soltos de Velocidade/Penetracao/Rajada/Alcance) nao ocupam
  slot, do mesmo jeito que o Dano do Tiro nunca ocupou.

## Escudo Deflector: Camadas Cumulativas, Nao Substitutivas

Decisao revisada apos questionamento direto sobre a intencao real: em
vez de "trocar de mecanica por nivel" (ideia original), as 3 camadas
sao cumulativas -- reducao percentual, depois barreira com HP proprio
(dano excedente vaza para o HP do player em vez de ser descartado),
depois bloqueio periodico total -- todas ativas simultaneamente no
nivel maximo. O motivo: o criador do jogo queria que o power-up "ficasse
mais forte com novidades", nao apenas diferente.

## Sabre Giratorio: Nome e Design Temático

Renomeado de "Espada Giratoria" para manter consistencia tematica
espacial (sem espadas medievais). Redesenho futuro planejado: de
circulo para lamina fina, com eixo de tamanho/alcance -- ainda nao
implementado.

## Sifao de Energia: Reskin de "Fang"

O conceito original de arma vampirica ("Fang", roubo de vida) foi
mantido mecanicamente mas renomeado para consistencia tematica --
"Sifao de Energia" drena energia do inimigo e converte parte do dano
em reparo para o jogador, encaixando na estetica de nave espacial em
vez de fantasia/vampiro.

## Tiro Multiplo: Quadrantes Substituindo "Quatro Direcoes"

A primeira versao planejada ("Quatro Direcoes": reto+atras+cima+baixo,
todas fixas do mundo, disparando cegamente mesmo sem inimigo ali) foi
testada e revisada apos o criador do jogo notar que a mecanica nao
tinha identidade propria -- misturava visualmente com Diagonal e
Paralelo. A versao final (Quadrantes) faz cada direcao buscar seu
proprio alvo dentro de uma fatia angular de 90 graus, so disparando se
encontrar um inimigo ali -- a fatia "Frente" nunca tem upgrade proprio,
cobrindo dinamicamente o que sobrar fora das fatias ja reivindicadas.

## Armas de Fogo: Papel Tatico por Configuracao, Nao por Logica Nova

Phaser Leve, Canhao de Plasma e Metralhadora de Pulso compartilham a
mesma estrutura de municao/recarga -- a diferenca de "arma agil contra
hordas" (Phaser) vs. "dano concentrado contra ameacas fortes" (Plasma)
vs. "volume alto, dano baixo" (Pulso) vem inteiramente dos valores de
configuracao, nao de codigo duplicado ou especial por arma.

---

# Decisoes de Design Fechadas -- Estrutura de Boss Rush

A sala nao e' vencida por "sobreviver a um timer" isoladamente, mas por
**derrotar o chefao** ao final de uma sequencia de combate de
aproximadamente 5 minutos, dividida em 3 ondas com composicao
crescente:

- **Onda 1:** 1 swarm central + 1 mini-chefe.
- **Onda 2:** 2 swarms divididos + 1 mini-chefe central + 1 chefe.
- **Onda 3/final:** 3 swarms + 2 mini-chefes + 1 chefe + o chefao.

Cada onda tem um countdown proprio **para a proxima onda comecar**
(nao para a atual acabar) -- se o jogador demorar, a proxima onda
soma-se aos inimigos remanescentes, nunca espera limpar tudo. "Swarm" =
chegada de toda uma leva de inimigos simultaneamente, mecanica de pico
de dificuldade distinta do reabastecimento gradual padrao do jogo.

Duracao total ~5 minutos, dividida proporcionalmente entre as 3 ondas
(referencia de mercado de outros jogos do genero) -- percentuais
exatos a calibrar por sensacao de jogo, nao fixos.

## Os Tres Chefes

- **Mini-chefe:** fraco (~300 HP). Drop: 3 upgrades garantidos para
  aquela sala (+1 nivel em power-ups ja adquiridos, sem exigir video
  simulado -- recompensa garantida por progresso). Puxa
  automaticamente todas as gemas da sala ao morrer.
- **Chefe:** normal (~700 HP). Drop cumulativo: tudo que o Mini-chefe
  dropa + recupera 50% do HP do player. Tambem puxa gemas
  automaticamente.
- **Chefao:** forte (~2000 HP). Ataque de projetil sequencial: ~12
  tiros lentos e desviaveis, cada um mirando a posicao do player no
  momento do disparo (nao perseguicao continua) -- o 1o tiro mira onde
  o player esta naquele instante, o player se move, o 2o mira a ultima
  posicao registrada, e assim por diante. Chefes de retorno de sala
  podem reaproveitar esse padrao, alem de uma variacao "raio" que
  persegue o player por um tempo -- chefoes variam de tipo entre si.
  Drop cumulativo dos dois anteriores + especifico dele.

A energia dos 3 chefes escala proporcionalmente tanto por reentrada
quanto por mudanca de nivel de sala -- ambos os eixos de dificuldade
crescente se aplicam aos chefes, nao so a quantidade de inimigos
comuns.

## Ondas Somam, Nunca Substituem

Diferente de sistemas de onda tradicionais (onde a proxima so comeca
apos a atual ser derrotada), aqui a proxima onda chega de qualquer
forma apos um tempo fixo, somando-se ao que sobrou da anterior -- cria
pressao real para nao procrastinar, mesmo sem depender de eliminar
todos os inimigos.

> Observacao de gameplay emergente (validada em teste): o tamanho
> fisico da sala afeta naturalmente essa pressao, mesmo sem ajuste
> manual -- em salas grandes, inimigos levam mais tempo para alcancar
> o jogador, entao a onda seguinte tende a se acumular com sobras da
> anterior; em salas pequenas, o jogador consegue eliminar toda a onda
> antes da proxima comecar.

## Dificuldade por Composicao, Nao So por Quantidade

A numeracao de ondas deve ser continua entre visitas de uma sala (nao
reiniciar a cada reentrada). A quantidade de inimigos tem um teto
(~18-20 por onda) -- crescimento geometrico de quantidade rapidamente
torna o jogo inviavel. A partir dali, a dificuldade sobe via
composicao: proporcao de inimigos fortes (e tipos mais perigosos)
aumenta a cada onda, mesmo com o total estabilizado.

---

# Decisoes de Design Fechadas -- Sistemas de Recurso

O jogo tem tres sistemas de recurso com estrutura parecida (limite +
regeneracao por tempo + video/compra), mas propositos distintos --
importante nao confundi-los:

- **Energia** -- reduz a qualidade das skills enquanto baixa; nao
  limita tentativas, so desempenho.
- **Reentradas** -- limita quantas vezes o jogador pode revisitar uma
  sala ja vencida.
- **Vidas** -- limita quantas vezes o jogador pode continuar apos
  morrer dentro de uma sessao de horda.

## Salas Trancadas nos Dois Sentidos

Uma sala com inimigos vivos tranca todas as suas portas -- nao apenas
a que leva adiante, mas tambem a que permite recuar. O jogador que
entra precisa limpa-la antes de poder sair por qualquer direcao.

---

# Decisoes de Design Fechadas -- Percepcao e Combate

## Raio Unico de Percepcao e Alcance

Percepcao do jogador (o que ele mira) e alcance do tiro compartilham o
mesmo valor de raio -- decisao consciente para que o jogador consiga
prever exatamente quais inimigos serao afetados ao ver o indicador
visual, sem surpresas. O raio e' sempre visivel, nao condicional.

## Distribuicao de Alvo Como Padrao Extensivel

A tecnica de "mirar o Nº mais proximo, com fallback para o mais
distante disponivel" foi generalizada em uma unica funcao reutilizavel
desde a segunda arma automatica implementada -- qualquer arma futura
que precise mirar um alvo distinto reaproveita a mesma logica, sem
duplicar codigo de busca de alvo.

---

# Visao de Longo Prazo (Fora do Escopo Atual, Registrado)

- **Re-arquitetura Espacial: Mapas Continuos por Nivel.** Camera
  seguindo o jogador (nao salas como tela fixa), salas maiores que a
  tela, crescimento de complexidade por nivel (nivel N = N salas
  conectadas), transicao cinematografica entre regioes do mapa.
  Marcada como a maior mudanca estrutural desde o inicio do projeto --
  mais ampla que a propria virada para o genero Horde -- por afetar a
  fundacao espacial (Room/Door). Tratada como Sprint isolada e
  dedicada quando chegar sua vez.
- **Narrativa Historica e Area de Membros.** Usar o historico de
  stardates e estatisticas do jogador para gerar uma narrativa
  pessoal, publicavel como pagina individual -- parte de uma futura
  area de membros pagantes. Horizonte distante, sem dependencia
  tecnica imediata.
- **Progressao Espacial: Portas Danificadas e Reparo em Cadeia.**
  Conceito central do Bloco de Restauracao da Nave -- portas
  trancadas ate serem reparadas com material dropado por inimigos,
  cada sala nova conquistada tanto abrindo caminho adiante quanto
  reforcando a defesa de salas ja visitadas. Depende de estado novo em
  Door (danificada/reparada) e vinculo entre material dropado e qual
  porta/sala ele afeta.
- **Minigames de Reparo.** Cada sistema restaurado poderia se
  manifestar como um puzzle especifico (Sudoku, Match 3, Pac-Man,
  Tetris) em vez de reparo instantaneo -- horizonte distante, depende
  da base de combate e restauracao estarem maduras.
- **Taxonomia Completa de Inimigos.** Alem de Terrestres (unico tipo
  implementado), planejados: Aereos (vulneraveis so a projetil/campo
  de forca), Ativos (ataque a distancia, cuspe venenoso com dano
  continuo), Residual (poca de gosma pos-morte). Implementacao
  incremental, uma categoria de cada vez.
- **Progressao Vitalicia vs. de Partida, Moeda do Jogo, Dois Rankings
  (Honesto vs. VIP).** Sistemas de meta-progressao e economia,
  registrados como visao mas dependentes de infraestrutura de dados
  (banco de dados) ainda nao construida.

---

# Pesquisa de Referencia: Genero Horde Survivor / Bullet Heaven

Pesquisa de mercado conduzida para embasar decisoes de design, com
fontes reais do genero (Vampire Survivors e sucessores) -- principios
validados e ja incorporados as decisoes acima:

- Piso continuo de inimigos, sem vazio entre ondas.
- Risco real de escalar dificuldade so por quantidade (ponto de
  ruptura conhecido do genero) -- confirma a decisao de escalar por
  composicao, nao so volume.
- Escolha real entre opcoes gera "profundidade de build" comparavel a
  deckbuilding -- upgrade automatico nao gera decisao real nenhuma.
- XP/pontos como objeto fisico coletavel (gema), nao instantaneo.
- Sinergia entre power-ups mais valiosa que empilhar numero isolado.

---

# Historico

## v6.0
- **Reestruturacao de proposito do documento:** VISAO.md deixa de ser
  um checklist operacional de pendencias (isso agora vive
  exclusivamente em CONTEXTO_PROJETO.md) e passa a registrar apenas
  CONCEITO do jogo e DECISOES DE DESIGN JA FECHADAS com o raciocinio
  por tras de cada uma. Motivo: as duas versões anteriores (v4.9 e
  v5.0) vinham duplicando conteudo entre VISAO.md e
  CONTEXTO_PROJETO.md, criando risco de desatualizacao quando so um
  dos dois era atualizado.
- Consolidadas todas as decisões de design do Bloco de Power-ups
  (completo desde a Sprint 042) em secoes de "decisao + porque",
  removendo o formato de lista de status "implementado/pendente" —
  esse status vive no Contexto.
- Consolidada a Estrutura de Boss Rush com o desenho completo de
  chefes, ondas e drops.
- Criada secao "Visao de Longo Prazo" para ideias de escopo distante
  (Re-arquitetura Espacial, Narrativa Historica, Minigames de Reparo,
  Taxonomia de Inimigos, etc.) — mantidas aqui por serem visao de
  design, nao pendencia operacional de curto prazo.
- Historico de versoes anteriores (v1.0 a v5.0) preservado apenas via
  controle de versao Git — resumo: mudanca de direcao para genero
  Horde (v2.0), backlog detalhado do Modo 1, pesquisa de generos,
  Power-ups Passivos, Boss Rush inicial, renomeacoes tematicas (Fang→
  Sifao, Revolver→Phaser, etc.), Bloco de Power-ups completo (v5.0).
