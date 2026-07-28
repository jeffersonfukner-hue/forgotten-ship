# Contexto do Projeto — A1 Game Academy / Forgotten Ship

> Atualizar este arquivo a cada sprint fechado. Manter enxuto, sem histórico de conversa.

## Estado Atual
- Projeto: Forgotten Ship (jogo 01 da A1 Game Academy), horde survival espacial em Python/Pygame CE
- Vinculado a: canal do YouTube (documentação em vídeo) + curso pago futuro
- Último sprint fechado: [SPRINT_042.md] — Metralhadora de Pulso (terceira arma de fogo, cadência como eixo upável) — Bloco de Power-ups 100% completo (11 armas/sistemas)
- Em andamento agora: decisão em aberto entre Bloco de Entidades de Chefes, Bloco de Restauração da Nave, refactor POWER_UPS, ou bugs/refinamentos pendentes de obstáculos

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
- Power-ups passivos: configuração genérica via dicionário (`PASSIVE_POWERUPS`, mesmo padrão de `Enemy`/`Obstacle`), nível calculado sob demanda via `get_passive_value()` — ímã e regeneração de vida implementados (Sprints 028/029)
- Sistema de escolha de upgrade: substituiu o upgrade automático — a cada level up, `GameScene` pausa o jogo (early return em `update()`), sorteia 3 opções via `player.choose_random_upgrades()` e aplica a escolha via `player.apply_upgrade(key)`; teclado (1/2/3) nesta primeira versão (Sprint 030)
- Slots de power-up: limite de armas/passivos simultâneos, agrupados por categoria (`CATEGORY_GROUPS` — eixos de uma mesma arma contam como 1 slot só), crescendo com o nível (`POWERUP_SLOTS_BY_LEVEL`: 2→3→4→5); "damage" não ocupa slot. Pré-requisitos entre eixos (`UPGRADE_PREREQUISITES`) escondem upgrades secundários de uma arma até o eixo base atingir nível mínimo (Sprint 031)
- Sabre Giratório: primeira arma com múltiplos eixos (quantidade/velocidade/dano), entidade própria (`Saber`), sincronizada e recriada por inteiro a cada mudança de quantidade para manter espaçamento angular uniforme (Sprint 031)
- Sifão de Energia: arma de efeito instantâneo (raio extrator, sem entidade Projectile), cadência própria, mira o 2º inimigo mais próximo via `get_enemies_by_distance()` (generalização de `find_closest_enemy`); cura com piso mínimo de 1 HP para evitar truncamento silencioso em conversões baixas (Sprint 032)
- Escudo Deflector: 3 camadas cumulativas (não substitutivas) — redução %, barreira com transbordo, bloqueio periódico — desbloqueadas em cadeia via pré-requisito; `take_damage()` retorna tupla `(dano_real, foi_bloqueado)` para feedback visual diferenciado; barreira regenera com delay de 3s sem dano (Sprint 033)
- Painel de debug reorganizado: resumo compacto sempre visível (`CATEGORY_LABELS`, sigla + maior nível por categoria equipada via `get_category_max_level()`), histórico completo (estatísticas, salas, visitas) expansível via tecla `TAB` (`debug_expanded`) — nenhum dado descartado, só reorganização de exibição (Sprint 034)
- Pontuação fixa em tela: "Sala: X pts" (destaque) + "Total: Y pts" (discreto), reaproveitando `room.points_by_type`/`player.points_by_type` já existentes, sem nova lógica de acumulação; HUD reposicionado em cascata para abrir espaço no topo (Sprint 035)
- Tiro Múltiplo: 3 variantes (Diagonal, Paralelo, Quadrantes) em grupo de exclusividade permanente (`EXCLUSIVE_CATEGORIES`) — escolher uma remove as outras duas para sempre da lista de opções; não ocupa slot (`FREE_CATEGORIES`, parte do Tiro base); Quadrantes usa `atan2` para dividir o espaço em 4 fatias, cada uma buscando seu próprio alvo, Frente cobrindo dinamicamente o que sobra (Sprint 036)
- Eixos do Tiro Base completos: velocidade e penetração parametrizados em `Projectile` (antes hardcoded), alcance recalculado a cada frame via `get_passive_value("range")` (antes constante fixa), rajada implementada como fila de disparos pendentes (`pending_burst_shots`, consumida por `BURST_SHOT_DELAY`) — repetição temporal, composável com Múltiplo (repetição espacial); nenhum ocupa slot (Sprint 037)
- Campo de Força: sem entidade própria (cálculo direto de distância no loop principal, diferente do Sabre que tem posição orbital); cronômetro único compartilhado (`force_field_timer`) aplica dano a todos os inimigos no raio simultaneamente a cada tique (0.5s), diferente do cooldown por inimigo do Sabre; ocupa slot normal (não é parte do Tiro base) (Sprint 038)
- Tempo de sessão e salas limpas: `session_time` vive na `GameScene` (confirmado via `game.py` que ela não é recriada durante a sessão), incrementado antes até da pausa de upgrade; salas limpas reaproveita `room.times_cleared` já existente, somado via `sum()` sobre todas as salas (Sprint 039)
- Phaser Leve: primeira arma com munição/recarga — 3 condições combinadas em `ready_to_fire_phaser()` (munição > 0, cadência liberada, fora de reload); mira o 3º inimigo mais próximo; carregador enchido automaticamente ao upar capacidade; `Projectile` ganhou parâmetro `color` (Phaser em azul claro, tiro principal amarelo por padrão) (Sprint 040)
- Canhão de Plasma: segunda arma de fogo, mesma estrutura do Phaser (munição/reload), calibrada para dano concentrado (mira o 4º mais próximo, carregador maior, dano mais alto, reload mais lento); projéteis roxo/lilás (Sprint 041)
- Correção de distribuição de alvo: Sifão/Phaser/Plasma/Pulso usam `ordered_enemies[min(N-1, len(ordered_enemies)-1)]` em vez de exigir quantidade mínima de inimigos — mira o mais distante disponível em vez de ficar mudo com poucos alvos no raio (Sprint 041)
- Metralhadora de Pulso: terceira arma de fogo, única com cadência como eixo upável (`pulso_cadencia`, via `get_passive_value()`, não constante fixa como Phaser/Plasma); mira o 5º mais próximo; projéteis laranja (Sprint 042)

### Bloco de Power-ups — Completo (Sprints 028-042)
11 armas/sistemas implementados: Tiro base (dano/velocidade/penetração/rajada/alcance), Tiro Múltiplo (Diagonal/Paralelo/Quadrantes, exclusivos entre si), Ímã, Regeneração, Sabre Giratório, Sifão de Energia, Escudo Deflector (3 camadas cumulativas), Campo de Força, Phaser Leve, Canhão de Plasma, Metralhadora de Pulso. Arquitetura comum: `PASSIVE_POWERUPS` (dicionário genérico por chave), `CATEGORY_GROUPS` (agrupa eixos por arma para slots), `UPGRADE_PREREQUISITES` (cadeia de liberação), `POWERUP_SLOTS_BY_LEVEL` (2→5), `EXCLUSIVE_CATEGORIES`/`FREE_CATEGORIES`. Distribuição de alvo entre armas automáticas: tiro=1º mais próximo, Sifão=2º, Phaser=3º, Plasma=4º, Pulso=5º (todas resilientes a poucos inimigos). Detalhes de cada Sprint em `docs/sprints/SPRINT_028.md` a `SPRINT_042.md`.

## Backlog — Próximos Blocos (decisão em aberto)
- Bloco de Entidades de Chefes: mini-bosses, boss com barra de fases e stagger
- Bloco de Restauração da Nave: mecânica narrativa central (reparo da nave = defesa)
- Refactor `PASSIVE_POWERUPS` → `POWER_UPS` + campo `"type"` (registrado abaixo)
- Bugs/refinamentos de obstáculos e consumíveis (registrados abaixo)

## Bugs e Refinamentos Pendentes (Sprint futura de correção — Obstáculos e Consumíveis)
- Bug: obstáculo destrutível pode nascer sobre a posição de entrada de uma porta, prendendo o player sem chance de escapar do dano
- Refinamento: obstáculos destrutíveis sem margem mínima da parede, permitindo inimigo preso no vão entre parede e obstáculo
- Conteúdo faltando: obstáculos fixos (`obstacle_data`) definidos só na Sala 1; Salas 2 e 3 sem nenhum
- Nova categoria a implementar: Consumíveis de efeito único (não acumulam nível, diferente dos passivos) — drop do obstáculo destrutível ainda indefinido (candidatos: recarga de energia, puxão total de gemas, sorteio aleatório entre eles)
- Vida extra como drop raro (aumenta `max_lives` permanentemente), introduzindo conceito de raridade ponderada entre itens do mesmo pool
- Tela de Estatísticas dedicada (banco de dados): quando existir, registrar a build de power-ups equipada em cada visita de sala, não só o resultado agregado — permite comparar builds objetivamente e gerar gráficos de decisão (data science aplicada, conecta com "Ranking por Qualidade de Escolha" do VISAO.md)
- Estudo (não decisão): avaliar migrar dicionários de configuração (`settings.py`) para JSON — vale a pena se surgir necessidade de edição por não-programador, hot-reload ou modding; nenhuma pressão real ainda
- Dificuldade escalável por reentrada e por nível de sala: `HORDE_ENEMIES_PER_VISIT` já existe em `settings.py` mas nunca foi conectado (`spawn_horde()` sempre usa `HORDE_BASE_ENEMIES` fixo); `ROOM_SURVIVAL_DURATION` também deveria escalar proporcionalmente por reentrada; campo `"level"` já existe em `room_data` mas ainda não influencia spawn/dificuldade. Conecta direto com a seção já existente no VISAO.md "Continuidade de Ondas Entre Visitas e Teto de Volume" (composição de tipos, não só quantidade, com teto ~18-20) — falta só implementar o que já está desenhado
- Refactor: renomear `PASSIVE_POWERUPS` → `POWER_UPS` em `settings.py`, adicionando campo `"type": "active"/"passive"` em cada entrada — prepara terreno para estatística de eficiência por tipo de power-up escolhido, e uma futura área de simulação/comparação de builds (possível feature paga). Toca `settings.py`, `player.py` e `game_scene.py` em múltiplos pontos — Sprint dedicada, não mid-sprint
- Revisar comentários de `settings.py` — vários ficaram desatualizados conforme o arquivo cresceu; fazer junto do refactor acima, já que renomear a variável exige passar por cada bloco mesmo

## Preferências de Estilo
- Tema Star Trek (Stardate, terminologia de nave)
- Gosta de estatística/dado: ranking, estatística por sessão e por tipo de inimigo, histórico de jogador como feature paga futura
- Quer honestidade direta, inclusive crítica a ideia ruim, sem filtro
- Comunicação rápida com ideias no meio da sessão — devem ser triadas/registradas, não implementadas na hora
