# Contexto do Projeto — A1 Game Academy / Forgotten Ship

> Atualizar este arquivo a cada sprint fechado. Manter enxuto, sem histórico de conversa.

## Estado Atual
- Projeto: Forgotten Ship (jogo 01 da A1 Game Academy), horde survival espacial em Python/Pygame CE
- Vinculado a: canal do YouTube (documentação em vídeo) + curso pago futuro
- Último sprint fechado: [SPRINT_045.md] — Reabastecimento gradual (gatilho 20%) + dificuldade crescente por reentrada + correção de inimigo nascendo preso em obstáculo
- Em andamento agora: Bloco de Entidades de Chefes (estrutura de ondas com swarms/mini-chefes/chefe/chefão já detalhada)

## Repositórios
- `a1-game-academy`: metodologia e documentação institucional
- `forgotten-ship`: código do jogo e documentação de sprint
- Caminho no Mac mini: `/Volumes/JeffSSD/A1-Game-Academy/` (ambos os repos dentro dela — `a1-game-academy/` e `projetos/001-forgotten-ship/`)

## Vocabulário de Comando
- **Bora** = proceder
- **Feito** = concluído
- **Mayday** = fora do rumo, parar e revisar
- **Palavra:** (prefixo + dois pontos) = classificar/documentar, não implementar ainda

## Convenções Fixas
- Conventional Commits
- Uma branch por sprint
- Constantes centralizadas em `settings.py`
- Sprint = documentação técnica + diário + material didático + roteiro de vídeo (tudo no mesmo texto)
- Foco sequencial: uma coisa por vez, completa, antes de seguir pra próxima

## Ciclo de Trabalho da Sprint
1. Desenvolver a Sprint (missão por missão, sequencial — ver Foco Sequencial abaixo).
2. Ao concluir todas as missões, gerar o documento `SPRINT_XXX.md` (técnica + diário + didático + roteiro).
3. Atualizar `CONTEXTO_PROJETO.md` (último sprint fechado + em andamento) e, se necessário, `VISAO.md`/`METODOLOGIA.md` — só agora, no fechamento.
4. Commitar (branch da Sprint → merge na `main`, Conventional Commits, ver `VERSIONAMENTO.md`).
5. Iniciar a próxima Sprint.

## Padrão de Resposta de Código
- Antes de propor qualquer mudança, peço o conteúdo ATUAL do(s) arquivo(s)/método(s) envolvidos — nunca invento estrutura de código que não vi.
- Toda mudança é apresentada como "Arquivo: X / Método: Y / Trocar: / por:", com o trecho exato de antes e depois — nunca bloco de código solto sem localização.
- Documentos (VISAO.md, METODOLOGIA.md) só são atualizados no fechamento da Sprint, de uma vez só — não a cada ideia isolada durante o desenvolvimento.
- Sprint anexada no Contexto do Projeto: sempre a última fechada + a atual em andamento (nunca acumular todas).
- Arquivos de referência mínimos para retomar em uma conversa nova: este `CONTEXTO_PROJETO.md` + a última Sprint + `METODOLOGIA.md`.

## Decisões de Arquitetura Já Tomadas
- Câmera: cada `draw()` recebe `camera_x`/`camera_y` como parâmetro (padrão 0), desenha `posição - câmera`
- Navegação espacial: Room/Door com portal-to-portal
- Inimigos: fluxo contínuo (substituiu ondas discretas), configuração via dicionário (fraco/forte)
- Obstáculos: fixos e destrutíveis, bloqueiam linha de visão pro auto-aim
- Progressão: drops de gemas com animação de puxão progressivo, upgrades com dano automático crescente
- Power-ups: configuração genérica via dicionário (`POWER_UPS`, ex-`PASSIVE_POWERUPS`, mesmo padrão de `Enemy`/`Obstacle`), nível calculado sob demanda via `get_power_up_value()` — ímã e regeneração de vida implementados (Sprints 028/029)
- Sistema de escolha de upgrade: substituiu o upgrade automático — a cada level up, `GameScene` pausa o jogo (early return em `update()`), sorteia 3 opções via `player.choose_random_upgrades()` e aplica a escolha via `player.apply_upgrade(key)`; teclado (1/2/3) nesta primeira versão (Sprint 030)
- Slots de power-up: limite de armas/passivos simultâneos, agrupados por categoria (`CATEGORY_GROUPS` — eixos de uma mesma arma contam como 1 slot só), crescendo com o nível (`POWERUP_SLOTS_BY_LEVEL`: 2→3→4→5); "damage" não ocupa slot. Pré-requisitos entre eixos (`UPGRADE_PREREQUISITES`) escondem upgrades secundários de uma arma até o eixo base atingir nível mínimo (Sprint 031)
- Sabre Giratório: primeira arma com múltiplos eixos (quantidade/velocidade/dano), entidade própria (`Saber`), sincronizada e recriada por inteiro a cada mudança de quantidade para manter espaçamento angular uniforme (Sprint 031)
- Sifão de Energia: arma de efeito instantâneo (raio extrator, sem entidade Projectile), cadência própria, mira o 2º inimigo mais próximo via `get_enemies_by_distance()` (generalização de `find_closest_enemy`); cura com piso mínimo de 1 HP para evitar truncamento silencioso em conversões baixas (Sprint 032)
- Escudo Deflector: 3 camadas cumulativas (não substitutivas) — redução %, barreira com transbordo, bloqueio periódico — desbloqueadas em cadeia via pré-requisito; `take_damage()` retorna tupla `(dano_real, foi_bloqueado)` para feedback visual diferenciado; barreira regenera com delay de 3s sem dano (Sprint 033)
- Painel de debug reorganizado: resumo compacto sempre visível (`CATEGORY_LABELS`, sigla + maior nível por categoria equipada via `get_category_max_level()`), histórico completo (estatísticas, salas, visitas) expansível via tecla `TAB` (`debug_expanded`) — nenhum dado descartado, só reorganização de exibição (Sprint 034)
- Pontuação fixa em tela: "Sala: X pts" (destaque) + "Total: Y pts" (discreto), reaproveitando `room.points_by_type`/`player.points_by_type` já existentes, sem nova lógica de acumulação; HUD reposicionado em cascata para abrir espaço no topo (Sprint 035)
- Tiro Múltiplo: 3 variantes (Diagonal, Paralelo, Quadrantes) em grupo de exclusividade permanente (`EXCLUSIVE_CATEGORIES`) — escolher uma remove as outras duas para sempre da lista de opções; não ocupa slot (`FREE_CATEGORIES`, parte do Tiro base); Quadrantes usa `atan2` para dividir o espaço em 4 fatias, cada uma buscando seu próprio alvo, Frente cobrindo dinamicamente o que sobra (Sprint 036)
- Eixos do Tiro Base completos: velocidade e penetração parametrizados em `Projectile` (antes hardcoded), alcance recalculado a cada frame via `get_power_up_value("range")` (antes constante fixa), rajada implementada como fila de disparos pendentes (`pending_burst_shots`, consumida por `BURST_SHOT_DELAY`) — repetição temporal, composável com Múltiplo (repetição espacial); nenhum ocupa slot (Sprint 037)
- Campo de Força: sem entidade própria (cálculo direto de distância no loop principal, diferente do Sabre que tem posição orbital); cronômetro único compartilhado (`force_field_timer`) aplica dano a todos os inimigos no raio simultaneamente a cada tique (0.5s), diferente do cooldown por inimigo do Sabre; ocupa slot normal (não é parte do Tiro base) (Sprint 038)
- Tempo de sessão e salas limpas: `session_time` vive na `GameScene` (confirmado via `game.py` que ela não é recriada durante a sessão), incrementado antes até da pausa de upgrade; salas limpas reaproveita `room.times_cleared` já existente, somado via `sum()` sobre todas as salas (Sprint 039)
- Phaser Leve: primeira arma com munição/recarga — 3 condições combinadas em `ready_to_fire_phaser()` (munição > 0, cadência liberada, fora de reload); mira o 3º inimigo mais próximo; carregador enchido automaticamente ao upar capacidade; `Projectile` ganhou parâmetro `color` (Phaser em azul claro, tiro principal amarelo por padrão) (Sprint 040)
- Canhão de Plasma: segunda arma de fogo, mesma estrutura do Phaser (munição/reload), calibrada para dano concentrado (mira o 4º mais próximo, carregador maior, dano mais alto, reload mais lento); projéteis roxo/lilás (Sprint 041)
- Correção de distribuição de alvo: Sifão/Phaser/Plasma/Pulso usam `ordered_enemies[min(N-1, len(ordered_enemies)-1)]` em vez de exigir quantidade mínima de inimigos — mira o mais distante disponível em vez de ficar mudo com poucos alvos no raio (Sprint 041)
- Metralhadora de Pulso: terceira arma de fogo, única com cadência como eixo upável (`pulso_cadencia`, via `get_power_up_value()`, não constante fixa como Phaser/Plasma); mira o 5º mais próximo; projéteis laranja (Sprint 042)
- Refactor `POWER_UPS`: renomeado de `PASSIVE_POWERUPS`, cada entrada com `"type": "active"/"passive"` (metadado, sem uso funcional ainda); métodos renomeados em cadeia (`passive_levels`→`power_up_levels`, `get_passive_value`→`get_power_up_value`, `upgrade_passive`→`increase_power_up_level`); arquivos entregues completos, não em diffs, dado o volume (Sprint 043)
- Bugs de obstáculos corrigidos: `DESTRUCTIBLE_OBSTACLE_DOOR_MARGIN`/`DESTRUCTIBLE_OBSTACLE_WALL_MARGIN` evitam spawn sobre porta ou colado à parede (faixa protegida por `min()`/`max()` para salas estreitas); obstáculos fixos adicionados às Salas 2 e 3 (Sprint 044)
- Reabastecimento gradual + dificuldade por reentrada: gatilho de 20% de baixa populacional antes de repor (`HORDE_REINFORCEMENT_TRIGGER_RATIO`), reposição de 1 inimigo por vez com intervalo (`HORDE_REINFORCEMENT_INTERVAL`) — distinto de reposição "em massa" (reservado para futuro modo swarm); piso de inimigos escala com `room.times_cleared` via `HORDE_ENEMIES_PER_VISIT` (finalmente conectado); corrigido bug de inimigo nascendo preso em obstáculo fixo (`_spawn_wave_enemies` agora também checa `colliderect` contra obstáculos) (Sprint 045)

### Bloco de Power-ups — Completo (Sprints 028-042)
11 armas/sistemas implementados: Tiro base (dano/velocidade/penetração/rajada/alcance), Tiro Múltiplo (Diagonal/Paralelo/Quadrantes, exclusivos entre si), Ímã, Regeneração, Sabre Giratório, Sifão de Energia, Escudo Deflector (3 camadas cumulativas), Campo de Força, Phaser Leve, Canhão de Plasma, Metralhadora de Pulso. Arquitetura comum: `POWER_UPS` (dicionário genérico por chave, com campo `"type"`), `CATEGORY_GROUPS` (agrupa eixos por arma para slots), `UPGRADE_PREREQUISITES` (cadeia de liberação), `POWERUP_SLOTS_BY_LEVEL` (2→5), `EXCLUSIVE_CATEGORIES`/`FREE_CATEGORIES`. Distribuição de alvo entre armas automáticas: tiro=1º mais próximo, Sifão=2º, Phaser=3º, Plasma=4º, Pulso=5º (todas resilientes a poucos inimigos). Detalhes de cada Sprint em `docs/sprints/SPRINT_028.md` a `SPRINT_045.md`.

## Backlog — Próximos Blocos (decisão em aberto)
- Bloco de Entidades de Chefes — quebrado em 5 Sprints menores, nesta ordem:
  - **Sprint A:** Sistema de ondas com timer e acúmulo — cada onda tem countdown próprio; o countdown é para a PRÓXIMA onda começar, não para a atual acabar; se o player demorar, a próxima onda soma aos inimigos remanescentes (inclusive o chefe da onda anterior), nunca espera limpar tudo. Sem chefes ainda, só a mecânica base.
  - **Sprint B:** Mini-chefe — fraco, ~300 HP; drop: 3 upgrades garantidos (+1 nível em power-ups já adquiridos pelo player) + puxão automático de todas as gemas da sala ao morrer.
  - **Sprint C:** Chefe — normal, ~700 HP; drop CUMULATIVO: tudo que o Mini-chefe dropa (3 upgrades) + 50% de HP do player + puxão automático de gemas.
  - **Sprint D:** Chefão — forte, ~2000 HP; ataque de projétil sequencial (~12 tiros lentos e desviáveis, cada um mirando a posição do player NO MOMENTO do disparo, não perseguição contínua — 1º mira onde o player está, ele se move, 2º mira a última posição registrada, etc. — testar); chefes de "retorno de sala" (revisitas) podem reaproveitar esse padrão + variação "raio" que persegue o player por um tempo; chefões variam de tipo entre si; drop cumulativo dos dois anteriores + o que for específico dele.
  - **Sprint E:** Composição final — as 3 ondas completas (Onda 1: 1 swarm central + 1 mini-chefe; Onda 2: 2 swarms divididos + 1 mini-chefe central + 1 chefe; Onda 3/final: 3 swarms + 2 mini-chefes + 1 chefe + o chefão); contador grande e chamativo avisando a chegada do chefão na onda final.
  - Regra transversal: energia dos 3 chefes escala proporcionalmente tanto por reentrada QUANTO por mudança de nível (campo `"level"` de `room_data`, hoje sem uso — conecta com o item de dificuldade por nível já pendente abaixo).
- Bloco de Restauração da Nave: mecânica narrativa central (reparo da nave = defesa)

## Bugs e Refinamentos Pendentes (Sprint futura — Reentrada, Consumíveis, Coleta)
- Dificuldade escalável por reentrada — restante: `ROOM_SURVIVAL_DURATION` deveria escalar proporcionalmente por reentrada (quantidade de inimigos já resolvida na Sprint 045); campo `"level"` já existe em `room_data` mas ainda não influencia spawn/dificuldade; **regeneração de obstáculos destrutíveis por reentrada** (hoje não voltam depois de destruídos, sala fica progressivamente mais vazia) — identificado na Sprint 044. Conecta com VISAO.md "Continuidade de Ondas Entre Visitas e Teto de Volume". Tempo por onda (diferente por onda de swarm/chefe) fica para dentro do Bloco de Entidades de Chefes, não aqui
- Redesenho do Sabre Giratório: hoje desenhado como círculo, vira lâmina fina (2px), curta como adaga no início; novo eixo de upgrade (tamanho/alcance da lâmina); revisar colisão para retângulo fino rotacionado — identificado na Sprint 045
- Nova categoria a implementar: Consumíveis de efeito único (não acumulam nível, diferente dos passivos) — drop do obstáculo destrutível ainda indefinido (candidatos: recarga de energia, puxão total de gemas, sorteio aleatório entre eles)
- Vida extra como drop raro (aumenta `max_lives` permanentemente), introduzindo conceito de raridade ponderada entre itens do mesmo pool
- Coleta Automática de Gemas Remanescentes: já registrado no VISAO.md desde a Sprint 026 (auto-ímã ao vencer sala sem morrer, mini-ímã esporádico), ainda não implementado
- Tela de Estatísticas dedicada (banco de dados): quando existir, registrar a build de power-ups equipada em cada visita de sala, não só o resultado agregado — permite comparar builds objetivamente e gerar gráficos de decisão (data science aplicada, conecta com "Ranking por Qualidade de Escolha" do VISAO.md)
- Estudo (não decisão): avaliar migrar dicionários de configuração (`settings.py`) para JSON — vale a pena se surgir necessidade de edição por não-programador, hot-reload ou modding; nenhuma pressão real ainda
- Novo eixo do Sifão de Energia: `siphon_cadencia` (reduz `siphon_interval` por nível, mesmo espírito da Cadência do Tiro base) — deve seguir o mesmo pré-requisito de `siphon_dano` nível 1 já usado pelos outros eixos secundários do Sifão

## Preferências de Estilo
- Tema Star Trek (Stardate, terminologia de nave)
- Gosta de estatística/dado: ranking, estatística por sessão e por tipo de inimigo, histórico de jogador como feature paga futura
- Quer honestidade direta, inclusive crítica a ideia ruim, sem filtro
- Comunicação rápida com ideias no meio da sessão — devem ser triadas/registradas, não implementadas na hora
