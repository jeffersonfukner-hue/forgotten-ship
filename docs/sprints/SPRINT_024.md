# SPRINT_024.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 024
**Status:** Concluída
**Versão da Arquitetura:** Piso Contínuo de Inimigos e Estatísticas por Tipo

---

## Objetivo da Sprint

Substituir o modelo de ondas discretas (Sprint 021-023) por um **piso
contínuo de inimigos**, seguindo padrões validados do gênero Horde
Survivor/Bullet Heaven (pesquisa registrada no `VISAO.md`): a sala
mantém uma quantidade mínima de inimigos vivos, reabastecendo
continuamente, com a condição de vitória baseada em **sobreviver** um
tempo determinado — não mais em eliminar completamente uma sequência
fixa de ondas. A Sprint também introduziu estatísticas de mortos e
pontos por tipo de inimigo, tanto por sala quanto acumuladas na
partida inteira.

---

## Situação Inicial

Ao final da Sprint 023, cada sala gerava exatamente 2 ondas
(`current_wave`/`total_waves`), disparadas por tempo calculado ou
conclusão antecipada. Esse modelo, embora funcional, divergia do
padrão consolidado do gênero: pesquisa de mercado (Vampire Survivors e
outros) mostrou que jogos do gênero mantêm uma quantidade mínima de
inimigos vivos continuamente, sem "vazios" entre ondas discretas, com
a condição de vitória centrada em sobreviver a um período de tempo.

---

## Problema

O modelo de ondas discretas cria uma estrutura artificial de
"fases" que não reflete a experiência real do gênero de referência, e
ainda carregava a pendência já identificada (Sprint 023) de
crescimento de dificuldade insustentável por reentrada. Adicionalmente,
não havia nenhum registro de desempenho do jogador por tipo de
inimigo — dado valioso tanto para o jogo (rankings futuros) quanto
para os objetivos didáticos de ciência de dados do projeto.

---

## Decisão Arquitetural

### Piso Contínuo, não Ondas Discretas

`Room` passou a manter um piso fixo de inimigos (`horde_total_enemies`,
lido de `settings.HORDE_BASE_ENEMIES`). A cada frame, `GameScene`
verifica se a contagem atual está abaixo do piso e reabastece a
diferença — eliminando o conceito de "onda numerada" em favor de uma
ameaça constante, seguindo o padrão do gênero.

### Condição de Vitória por Sobrevivência, não por Eliminação

Cada sala possui `survival_duration` (tempo que o jogador precisa
resistir). Ao expirar, o reabastecimento **para** (`time_expired`),
mas a sala só é considerada `cleared` quando, além do tempo esgotado,
não houver mais nenhum inimigo vivo — união de duas condições, não uma
substituindo a outra. Isso preserva a garantia já estabelecida
(Sprint 010) de que uma sala com inimigos vivos nunca destrava suas
portas, mesmo que o cronômetro de sobrevivência já tenha se esgotado.

### Estatísticas em Dois Níveis: Sala e Partida

Tanto `Room` quanto `Player` passaram a registrar `kills_by_type` e
`points_by_type` — a primeira reiniciando a cada nova sala/visita, a
segunda acumulando ao longo de toda a sessão de jogo. Essa duplicação
deliberada permite comparar desempenho por ambiente (útil para
rejogabilidade e ranking futuro) e visualizar o progresso geral do
jogador simultaneamente.

---

## Conceitos de Python

- **Reabastecimento por Diferença (`missing = piso - atual`)** — o
  cálculo de quantos inimigos faltam para atingir o piso é feito por
  subtração simples a cada frame, um padrão comum em sistemas de spawn
  contínuo, evitando lógica condicional complexa.
- **Flag Booleana como Interruptor de Comportamento (`time_expired`)**
  — um único atributo booleano controla se o reabastecimento deve
  continuar ou parar, sem exigir uma máquina de estados formal para
  uma transição simples e unidirecional dentro do ciclo de vida da
  sala.
- **Dicionários Aninhados por Categoria** — `kills_by_type` e
  `points_by_type` seguem o mesmo padrão de dicionário-como-tabela já
  usado em `ENEMY_TYPES` e `ROOM_SIZES`, desta vez para acumular dados
  em vez de configurar comportamento.

---

## Conceitos de Arquitetura

- **Aderência a Padrões de Gênero Validados** — a decisão de adotar
  piso contínuo em vez de ondas discretas não foi uma preferência
  arbitrária, mas resultado direto de pesquisa de mercado sobre como
  jogos bem-sucedidos do gênero resolvem o mesmo problema — evitando
  redescobrir, por tentativa e erro, soluções já conhecidas.
- **Duas Condições Independentes para uma Transição de Estado** — a
  sala só é vencida com tempo esgotado **e** ausência de inimigos,
  reforçando o princípio já registrado na Sprint 023: transições de
  estado podem depender de múltiplos gatilhos, e ignorar um deles
  produz comportamento incorreto mesmo que a lógica pareça completa à
  primeira vista.
- **Escopo Consciente ao Adiar Refinamento** — o pedido de histórico
  detalhado por visita individual (não apenas o estado atual) foi
  identificado como maior que o escopo desta Sprint e adiado
  deliberadamente, evitando expandir o trabalho já concluído com uma
  funcionalidade que merece atenção própria.

---

## Implementações

### Missão 1 — Piso Contínuo na Room

**Arquivo:** `room.py`

Substituídos `current_wave`/`total_waves`/`next_wave_time` por
`survival_start_time`, `survival_duration` e `time_expired`.

### Missão 2 — Reabastecimento e Condição de Vitória

**Arquivo:** `game_scene.py`

`spawn_horde()` simplificado para preencher o piso inicial e iniciar o
cronômetro de sobrevivência. `update()` passou a reabastecer
continuamente (respeitando `time_expired`), e a condição de sala
vencida passou a exigir tempo esgotado **e** ausência de inimigos.

### Missão 3 — Estatísticas por Tipo (Sala e Partida)

**Arquivos:** `room.py`, `player.py`, `game_scene.py`

Adicionados `kills_by_type`/`points_by_type` e `register_kill()` em
ambas as classes. Ao eliminar um inimigo, o registro é feito tanto na
sala atual quanto no jogador.

### Missão 4 — Painel de Debug Reescrito

**Arquivo:** `game_scene.py`

Painel de debug consolidado para refletir o novo modelo: tempo de
sobrevivência (com contagem regressiva ou tempo final), contagem de
inimigos vivos vs. piso, estatísticas totais da partida, e
estatísticas por sala aninhadas na lista de salas já existente.

---

## Bugs Encontrados

### Bug — Timestamp Bruto Exibido como Tempo Decorrido

**Sintoma:** o painel de debug exibia um número absurdamente grande
(ex: "1784987914.0s") no lugar do tempo de onda.

**Causa:** métodos de exibição antigos (`_build_wave_timer_line`)
ainda referenciavam `horde_start_time`, um atributo do modelo anterior
de ondas que nunca foi definido no novo fluxo de `spawn_horde()` —
resultando em `time.time() - 0`, ou seja, o timestamp Unix atual por
inteiro.

**Investigação:** identificado através de captura de tela durante
teste, comparando o valor absurdo com a hipótese de referência a um
atributo desatualizado.

**Solução:** reescrita completa dos métodos de construção do painel de
debug, eliminando toda referência a atributos do modelo de ondas
descontinuado.

**Lição Aprendida:** ao substituir um modelo de dados por outro,
revisar todos os pontos de leitura (não apenas os de escrita) é
essencial — um atributo removido silenciosamente ainda "funciona" sem
erro de execução se o valor padrão (zero) produzir um resultado
numérico válido, mesmo que sem sentido.

### Bug — Porta Destrancava com Inimigos Ainda Vivos

**Sintoma:** ao esgotar o tempo de sobrevivência, a porta destrancava
imediatamente mesmo com inimigos remanescentes na sala.

**Causa:** a condição original de "sala vencida" dependia apenas do
tempo esgotado, sem verificar a ausência de inimigos — uma regressão
em relação à garantia já estabelecida na Sprint 010.

**Solução:** separação em duas verificações: `time_expired` (para o
reabastecimento) e a condição completa de `cleared` (exige tempo
esgotado **e** lista de inimigos vazia).

**Lição Aprendida:** ao introduzir uma nova condição de transição de
estado, é necessário revisitar e preservar explicitamente as garantias
já estabelecidas por Sprints anteriores, não apenas validar o
comportamento novo isoladamente.

---

## Pendência Registrada para Sprint Futura

Histórico detalhado por visita individual de cada sala (tempo de
conclusão, mortos, pontos de cada sessão específica, não apenas o
estado atual acumulado) — permitindo comparar desempenho entre
diferentes visitas à mesma sala. Identificado como parte da visão de
"5 melhores pontuações por sala" já registrada no `VISAO.md`, mas maior
que o escopo desta Sprint.

---

## Estado Atual da Arquitetura

```
Room
 ├── survival_start_time / survival_duration / time_expired
 └── kills_by_type / points_by_type / register_kill()

Player
 └── kills_by_type / points_by_type / register_kill()

GameScene.update()
 ├── reabastece inimigos ate o piso, exceto se time_expired
 ├── ao esgotar o tempo: para reabastecimento (time_expired = True)
 └── sala so "cleared" com tempo esgotado E lista de inimigos vazia

Painel de Debug
 ├── tempo de sobrevivencia (contagem regressiva ou tempo final)
 ├── inimigos vivos vs. piso
 ├── estatisticas totais da partida
 └── estatisticas por sala, aninhadas na lista de salas
```

Testado extensivamente: piso mantido corretamente, reabastecimento
parando ao esgotar o tempo, porta permanecendo trancada até eliminar
os inimigos remanescentes, e estatísticas por tipo acumulando
corretamente em ambos os níveis (sala e partida).

---

## O que o aluno aprendeu

Como pesquisar e adotar padrões de mercado validados em vez de
redescobrir soluções por tentativa e erro. Como uma mudança de modelo
de dados pode deixar "resíduos" em pontos de leitura não revisados,
produzindo bugs silenciosos que não geram erro de execução. Como
preservar garantias arquiteturais já estabelecidas ao introduzir uma
nova condição de transição de estado, evitando regressões sutis.

---

## Próxima Sprint

Sprint 025 — drops físicos coletáveis (substituindo a pontuação
instantânea atual) e power-up de ímã com raio de atração próprio,
conforme planejado na pesquisa de referência registrada no `VISAO.md`.
Candidato adicional: histórico detalhado por visita individual de
sala.

---

## Resumo Executivo

Esta Sprint substitui o modelo de ondas discretas por um piso contínuo
de inimigos, alinhado a padrões validados do gênero Horde Survivor,
com condição de vitória baseada em sobrevivência — não mais em
eliminação completa de uma sequência fixa. Dois bugs foram corrigidos
durante o desenvolvimento: um resíduo de atributo do modelo anterior
gerando um valor sem sentido na interface, e uma regressão na garantia
de que salas com inimigos vivos nunca destrancam suas portas.
Estatísticas de mortos e pontos por tipo de inimigo foram introduzidas
em dois níveis — por sala e por partida — lançando as bases para
análises de desempenho mais ricas em Sprints futuras.
