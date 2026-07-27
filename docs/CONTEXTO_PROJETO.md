# Contexto do Projeto — A1 Game Academy / Forgotten Ship

> Atualizar este arquivo a cada sprint fechado. Manter enxuto, sem histórico de conversa.

## Estado Atual
- Projeto: Forgotten Ship (jogo 01 da A1 Game Academy), horde survival espacial em Python/Pygame CE
- Vinculado a: canal do YouTube (documentação em vídeo) + curso pago futuro
- Último sprint fechado: [SPRINT_035.md] — Pontuação fixa em tela (sala + total, tempo real), reaproveitando dados já existentes
- Em andamento agora: retomar Bloco de Power-ups com o Tiro Múltiplo

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

## Bugs e Refinamentos Pendentes (Sprint futura de correção — Obstáculos e Consumíveis)
- Bug: obstáculo destrutível pode nascer sobre a posição de entrada de uma porta, prendendo o player sem chance de escapar do dano
- Refinamento: obstáculos destrutíveis sem margem mínima da parede, permitindo inimigo preso no vão entre parede e obstáculo
- Conteúdo faltando: obstáculos fixos (`obstacle_data`) definidos só na Sala 1; Salas 2 e 3 sem nenhum
- Nova categoria a implementar: Consumíveis de efeito único (não acumulam nível, diferente dos passivos) — drop do obstáculo destrutível ainda indefinido (candidatos: recarga de energia, puxão total de gemas, sorteio aleatório entre eles)
- Vida extra como drop raro (aumenta `max_lives` permanentemente), introduzindo conceito de raridade ponderada entre itens do mesmo pool
- Tela de Estatísticas dedicada (banco de dados): quando existir, registrar a build de power-ups equipada em cada visita de sala, não só o resultado agregado — permite comparar builds objetivamente e gerar gráficos de decisão (data science aplicada, conecta com "Ranking por Qualidade de Escolha" do VISAO.md)
- Estudo (não decisão): avaliar migrar dicionários de configuração (`settings.py`) para JSON — vale a pena se surgir necessidade de edição por não-programador, hot-reload ou modding; nenhuma pressão real ainda
- Novo eixo do Sifão de Energia: `siphon_cadencia` (reduz `siphon_interval` por nível, mesmo espírito da Cadência do Tiro base) — deve seguir o mesmo pré-requisito de `siphon_dano` nível 1 já usado pelos outros eixos secundários do Sifão

## Backlog — Blocos Pendentes (VISAO.md v4.9)
- Power-ups: armas de fogo (Phaser Leve/Canhão de Plasma/Metralhadora de Pulso, munição/recarga), tiro múltiplo (ímã, regeneração, Sabre, Sifão e Escudo Deflector já implementados — Sprints 028/029/031/032/033)
- Boss Entities: mini-bosses, boss com barra de fases e stagger
- Ship Restoration: mecânica narrativa central (reparo da nave = defesa)

## Preferências de Estilo
- Tema Star Trek (Stardate, terminologia de nave)
- Gosta de estatística/dado: ranking, estatística por sessão e por tipo de inimigo, histórico de jogador como feature paga futura
- Quer honestidade direta, inclusive crítica a ideia ruim, sem filtro
- Comunicação rápida com ideias no meio da sessão — devem ser triadas/registradas, não implementadas na hora
