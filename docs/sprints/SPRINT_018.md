# SPRINT_018.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 018
**Status:** Concluída
**Versão da Arquitetura:** Reentradas por Sala, Feedback Visual e Reorganização de Código

---

## Objetivo da Sprint

Implementar o sistema de Reentradas Limitadas descrito no `VISAO.md`,
com uma decisão de design importante lapidada durante o desenvolvimento:
o limite é **por sala**, não um recurso global do jogador — permitindo
ao jogador continuar explorando salas diferentes mesmo que uma
específica esteja temporariamente esgotada. A Sprint também corrigiu
dois bugs reais encontrados durante testes extensivos, adicionou
feedback visual antecipado (cor da porta) e reorganizou o código de
dois arquivos centrais em seções comentadas.

---

## Situação Inicial

Ao final da Sprint 017, não existia nenhum limite para revisitar salas
já vencidas — o jogador podia entrar e sair livremente de qualquer
sala, quantas vezes quisesse, sem nenhuma restrição além da horda
(cada vez maior) que o aguardava.

---

## Problema

Sem limite de revisitas, não há nenhuma pressão para o jogador
avançar — ele pode "girar" indefinidamente entre duas salas já
dominadas. Era necessário introduzir uma restrição que desincentive
esse comportamento sem, no entanto, impedir o jogador de continuar
jogando normalmente (indo para salas novas) enquanto aguarda a
regeneração de uma sala específica.

---

## Decisão Arquitetural

### Reentradas por Sala, não Globais

A primeira implementação (descartada ainda dentro desta Sprint)
colocava o contador de reentradas no `Player`, compartilhado entre
todas as salas. Isso se revelou incorreto ao testar: esgotar
reentradas em uma sala bloqueava, na prática, o acesso a **qualquer**
sala que exigisse reentrada — mesmo que essa outra sala nunca tivesse
sido visitada tantas vezes. A correção moveu o contador para dentro da
própria `Room` (`reentries`, `max_reentries`), tornando cada sala
independente das demais.

### Regeneração Ancorada no Consumo Mais Recente

`consume_reentry()` inicialmente só registrava `last_regen_time` na
primeira chamada (`if self.last_regen_time == 0.0`), o que fazia o
cronômetro de regeneração contar a partir do primeiro consumo de todos
os tempos, não do mais recente — um bug real (ver seção de Bugs). A
correção passou a atualizar esse timestamp em **todo** consumo.

### Feedback Visual Antecipado (Cor da Porta)

Em vez de o jogador só descobrir o bloqueio ao tentar atravessar uma
porta, `Door` ganhou um segundo estado de bloqueio (`reentry_blocked`,
independente de `locked`), atualizado a cada frame para refletir se a
sala de destino está sem reentradas — a porta aparece em uma cor
distinta (roxo escuro) antes mesmo do jogador se aproximar,
priorizada sobre a cor de "trancada por horda".

### Reorganização de `door.py` e `game_scene.py`

Ambos os arquivos foram reorganizados em seções comentadas (ex:
`# === COMBATE ===`, `# === DESENHO ===`), sem alteração de
comportamento — parte de uma nova regra de metodologia (ver abaixo).

---

## Conceitos de Python

- **Escopo de Estado: Onde um Contador Deveria Viver** — a diferença
  entre "recurso global do jogador" e "recurso por sala" ilustra uma
  decisão fundamental de modelagem: qual objeto é o dono legítimo de
  um dado. Colocar o contador no lugar errado (Player) produzia um
  comportamento tecnicamente correto, porém semanticamente equivocado.
- **Condição Guarda que Impede Atualizações Necessárias** — o bug de
  `last_regen_time` é um exemplo de uma condição (`if valor ==
  inicial`) pensada para "só rodar uma vez", mas que acidentalmente
  impede atualizações legítimas em todas as vezes seguintes.

---

## Conceitos de Arquitetura

- **Depuração por Eliminação de Hipóteses** — a investigação desta
  Sprint seguiu um processo de descartar explicações uma a uma
  (condição de corrida por velocidade, tempo de regeneração coincidente,
  glitch de porta) até isolar a causa real através de logs
  instrumentados e testes controlados — uma habilidade tão importante
  quanto escrever o código em si.
- **Feedback Visual Antecipado como Requisito de Design, não Luxo** —
  a cor da porta não é apenas estética: ela transforma uma restrição
  que o jogador só descobriria por tentativa e erro em uma informação
  visível de antemão, permitindo decisões informadas.
- **Organização de Código como Parte do Material Didático** — a partir
  desta Sprint, a metodologia do projeto passa a exigir que todo novo
  método seja acompanhado da indicação explícita de sua localização
  (seção/classe), reconhecendo que o código do jogo é também o
  material-fonte de um curso futuro.

---

## Implementações

### Missão 1 — Reentradas por Sala

**Arquivo:** `room.py`

Adicionados `max_reentries`, `reentries`, `regen_interval`,
`last_regen_time`, e os métodos `has_reentries_left()`,
`consume_reentry()`, `regen_reentries()`.

### Missão 2 — Bloqueio de Entrada sem Reentradas

**Arquivo:** `game_scene.py`

A detecção de porta passou a calcular `is_reentry` (sala de destino já
vencida e sem inimigos) e bloquear o início da sequência de entrada
quando `not target_room.has_reentries_left()`.

### Missão 3 — Consumo no Momento Correto

**Arquivo:** `game_scene.py`

`create_room()` passou a chamar `room.consume_reentry()` exatamente no
momento em que uma nova horda é gerada por reentrada — centralizando
o consumo em um único ponto do código.

### Missão 4 — Feedback Visual de Bloqueio

**Arquivos:** `door.py`, `game_scene.py`

Adicionado `reentry_blocked` a `Door`, com cor própria (roxo escuro)
na hierarquia de cores do método `draw()`. `GameScene.update()` passou
a atualizar esse estado para todas as portas da sala atual, a cada
frame.

### Missão 5 — Reorganização em Seções Comentadas

**Arquivos:** `door.py`, `game_scene.py`

Ambos os arquivos foram divididos em blocos com cabeçalhos de seção,
sem alteração de comportamento.

---

## Bugs Encontrados

### Bug 1 — Reentradas Globais Bloqueavam Salas Erradas

**Sintoma:** ao esgotar reentradas em uma sala, outra sala completamente
diferente também ficava bloqueada, mesmo tendo sido visitada muito
menos vezes.

**Causa:** o contador de reentradas vivia no `Player`, compartilhado
entre todas as salas — qualquer reentrada, em qualquer sala, consumia
o mesmo saldo único.

**Investigação:** identificado ao comparar o número de visitas de cada
sala com o comportamento de bloqueio relatado, percebendo que a soma
das reentradas consumidas nas duas salas batia exatamente com o limite
global.

**Solução:** o contador foi movido de `Player` para `Room`, tornando
cada sala independente.

**Lição Aprendida:** ao modelar um limite de recurso, é essencial
identificar corretamente qual entidade é a "dona" conceitual desse
recurso — um valor tecnicamente funcional, mas hospedado no objeto
errado, produz um comportamento que só parece incorreto quando
testado em cenários com múltiplas instâncias (neste caso, múltiplas
salas).

### Bug 2 — Regeneração Ancorada no Primeiro Consumo, não no Último

**Sintoma:** o número de reentradas parecia "travado", não diminuindo
de forma consistente em uma sala específica, enquanto outra sala se
comportava normalmente.

**Causa:** `consume_reentry()` só atualizava `last_regen_time` na
primeira chamada (condição `if self.last_regen_time == 0.0`), fazendo
o cronômetro de regeneração contar a partir do consumo mais antigo, não
do mais recente — em sessões de teste longas, isso permitia
regeneração "adiantada" o suficiente para mascarar consumos reais.

**Investigação:** confirmado através de testes controlados com valores
temporariamente ajustados (menos inimigos por horda, maior intervalo
de regeneração), isolando a variável tempo do restante do sistema.

**Solução:** `last_regen_time` passou a ser reatribuído em todo
consumo, não apenas no primeiro.

**Lição Aprendida:** uma condição guarda escrita para "inicializar uma
vez" pode, sem intenção, impedir atualizações legítimas nas chamadas
seguintes — vale sempre questionar se a condição deveria disparar uma
única vez na vida do objeto, ou a cada evento relevante.

### Bug 3 — `draw_ui` Sem Indentação (Fora da Classe)

**Sintoma:** não observado em execução (identificado antes de rodar),
mas teria causado erro de sintaxe ou comportamento incorreto — o
método `draw_ui` estava definido no nível do módulo, não como método
da classe `GameScene`.

**Causa:** durante edições sucessivas do arquivo, a indentação do
método foi perdida.

**Solução:** reindentação corrigida durante a reorganização completa
do arquivo nesta Sprint.

**Lição Aprendida:** reforça uma lição já registrada na Sprint 008 —
erros de indentação em Python mudam silenciosamente o significado do
código, sem necessariamente gerar um erro imediato e claro.

---

## Estado Atual da Arquitetura

```
Room
 ├── max_reentries / reentries
 ├── regen_interval / last_regen_time
 ├── has_reentries_left() — verifica e aciona regeneracao
 ├── consume_reentry() — decrementa e reinicia o cronometro
 └── regen_reentries() — regenera com base no tempo decorrido

Door
 ├── locked — trancada por horda ativa
 └── reentry_blocked — sala de destino sem reentradas (cor propria)

GameScene.update()
 ├── atualiza reentry_blocked de todas as portas da sala atual
 └── bloqueia inicio da sequencia de entrada se is_reentry e sem reentradas

GameScene.create_room()
 └── consome reentrada exatamente ao gerar nova horda por reentrada
```

Testado extensivamente: contadores de reentrada corretos e
independentes entre salas, bloqueio funcionando de forma consistente,
feedback visual (porta roxa) antecipando o estado antes da aproximação.

---

## Nota de Processo: Valores de Teste Mantidos Intencionalmente

Durante a investigação, os valores `enemy_count` (reduzido para 2,
temporariamente) e `regen_interval` (aumentado para isolar a variável
tempo) foram ajustados para acelerar os testes. Por decisão explícita,
esses valores de teste **permanecem** no código ao final desta Sprint
— o processo de teste ainda está em andamento, e reverter para os
valores de produção antes de finalizar os testes geraria mais atrito
do que benefício neste momento. Fica registrado como pendência
consciente, não como esquecimento.

---

## O que o aluno aprendeu

Como identificar a entidade correta para hospedar um recurso limitado,
evitando comportamento tecnicamente correto mas semanticamente errado.
Como uma condição guarda mal desenhada pode mascarar um bug por muito
tempo, especialmente em sessões de teste longas. Como isolar variáveis
(tempo, quantidade) durante uma investigação, ajustando temporariamente
valores de configuração para testar hipóteses com mais agilidade. Como
a organização e os comentários de um código não são apenas estética —
são parte do material de ensino que o código representa.

---

## Próxima Sprint

Sprint 019 — centralização de constantes de tuning em `settings.py`
(inimigos por horda, raio de percepção, intervalo de regeneração,
etc.), seguida da adoção de feedback visual/debug em tela como prática
padrão para toda nova regra de jogo introduzida.

---

## Resumo Executivo

Esta Sprint implementa o sistema de Reentradas Limitadas por sala —
não globalmente, uma correção de design importante descoberta durante
o desenvolvimento — com feedback visual antecipado (cor da porta) e
regeneração por tempo real. Dois bugs reais foram encontrados e
corrigidos através de investigação sistemática, e um terceiro (erro de
indentação crítico) foi corrigido durante a reorganização completa do
código em seções comentadas — reorganização essa que também deu origem
a uma nova regra permanente de metodologia sobre localização explícita
de métodos novos.
