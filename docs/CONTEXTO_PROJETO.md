# Contexto do Projeto — A1 Game Academy / Forgotten Ship

> Atualizar este arquivo a cada sprint fechado. Manter enxuto, sem histórico de conversa.

## Estado Atual
- Projeto: Forgotten Ship (jogo 01 da A1 Game Academy), horde survival espacial em Python/Pygame CE
- Vinculado a: canal do YouTube (documentação em vídeo) + curso pago futuro
- Último sprint fechado: [SPRINT_046B.md] — Mini-chefe (Bloco de Entidades de Chefes, Parte 2/5)
- Em andamento agora: Sprint C do Bloco de Chefes — Chefe (~700 HP, drop cumulativo: tudo do Mini-chefe + 50% de HP do player)

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

## Regra: Vc Sempre Recebe os Documentos Completos para Download
Sempre que uma Sprint fecha ou um documento institucional é editado, a IA entrega o arquivo completo atualizado, pronto para download e substituição direta — nunca apenas um diff para o usuário aplicar manualmente.

## Regra: Quando um Bloco Fecha, a Decisão Migra pro VISAO.md e Some Daqui
`VISAO.md` = conceito + decisões de design JÁ FECHADAS, com o porquê (estável, material de curso). `CONTEXTO_PROJETO.md` = onde estamos agora (vivo, descartável). Ao fechar um Bloco temático inteiro (ex: Bloco de Power-ups completo), a decisão de arquitetura correspondente deve ser: (1) escrita no `VISAO.md` como "decisão fechada + razão", e (2) **removida** da lista "Decisões de Arquitetura Já Tomadas" abaixo — não duplicada nos dois lugares. Sprints individuais dentro de um bloco ainda em andamento continuam registradas aqui normalmente; só migram quando o bloco inteiro fecha. Isso evita a desatualização silenciosa que já aconteceu (VISAO.md ficou 15 Sprints defasado do Bloco de Power-ups até ser notado e corrigido).

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

> Bloco de Power-ups (Sprints 028-042) — decisões de arquitetura completas migradas para `VISAO.md` v6.0 ("Decisões de Design Fechadas — Bloco de Power-ups"). Consulte lá; não duplicar aqui.

- Painel de debug reorganizado: resumo compacto sempre visível (`CATEGORY_LABELS`, sigla + maior nível por categoria equipada via `get_category_max_level()`), histórico completo (estatísticas, salas, visitas) expansível via tecla `TAB` (`debug_expanded`) — nenhum dado descartado, só reorganização de exibição (Sprint 034)
- Pontuação fixa em tela: "Sala: X pts" (destaque) + "Total: Y pts" (discreto), reaproveitando `room.points_by_type`/`player.points_by_type` já existentes, sem nova lógica de acumulação; HUD reposicionado em cascata para abrir espaço no topo (Sprint 035)
- Tempo de sessão e salas limpas: `session_time` vive na `GameScene` (confirmado via `game.py` que ela não é recriada durante a sessão), incrementado antes até da pausa de upgrade; salas limpas reaproveita `room.times_cleared` já existente, somado via `sum()` sobre todas as salas (Sprint 039)
- Refactor `POWER_UPS`: renomeado de `PASSIVE_POWERUPS`, cada entrada com `"type": "active"/"passive"` (metadado, sem uso funcional ainda); métodos renomeados em cadeia (`passive_levels`→`power_up_levels`, `get_passive_value`→`get_power_up_value`, `upgrade_passive`→`increase_power_up_level`); arquivos entregues completos, não em diffs, dado o volume (Sprint 043)
- Bugs de obstáculos corrigidos: `DESTRUCTIBLE_OBSTACLE_DOOR_MARGIN`/`DESTRUCTIBLE_OBSTACLE_WALL_MARGIN` evitam spawn sobre porta ou colado à parede (faixa protegida por `min()`/`max()` para salas estreitas); obstáculos fixos adicionados às Salas 2 e 3 (Sprint 044)
- Reabastecimento gradual + dificuldade por reentrada: gatilho de 20% de baixa populacional antes de repor (`HORDE_REINFORCEMENT_TRIGGER_RATIO`), reposição de 1 inimigo por vez com intervalo (`HORDE_REINFORCEMENT_INTERVAL`) — distinto de reposição "em massa" (reservado para futuro modo swarm); piso de inimigos escala com `room.times_cleared` via `HORDE_ENEMIES_PER_VISIT` (finalmente conectado); corrigido bug de inimigo nascendo preso em obstáculo fixo (`_spawn_wave_enemies` agora também checa `colliderect` contra obstáculos) (Sprint 045)
- Sistema de Ondas (Bloco de Chefes, Parte 1/5): `Room.current_wave`/`wave_timer` — cada onda soma `HORDE_ENEMIES_PER_VISIT` inimigos aos remanescentes após `WAVE_DURATION` (15s), nunca espera limpar a onda atual; roda em paralelo ao critério de vitória existente (`ROOM_SURVIVAL_DURATION`, agora 90s), ainda não integrados — integração completa fica pra Sprint E (Sprint 046A). Correção pós-fechamento: `survival_start_time` (relógio real) trocado por `survival_elapsed` (acumulado via `dt`) — sem isso, ficar parado na tela de escolha de upgrade "descontava" tempo de sobrevivência/onda de graça ao voltar, um exploit real para pular ondas
- Mini-chefe (Bloco de Chefes, Parte 2/5): `ENEMY_TYPES["mini_boss"]` (300 HP) com flag `is_boss`; drop **condicional**, não automático — dropa o pickup `SuperMagnet`, que só ao ser coletado libera `Player.apply_boss_reward()` (+1 nível em 3 power-ups já equipados) e o puxão automático de gemas da sala; `GameScene._handle_enemy_death()` centraliza a decisão gema-normal-vs-SuperMagnet, eliminando 4 blocos duplicados. Agendamento de spawn genérico por fração de onda (`settings.BOSS_SPAWN_SCHEDULE`, formato `(número_da_onda, fração)`), já com entradas prontas (comentadas) para Chefe e Chefão; ondas passam a ocupar frações proporcionais da duração total da sala (`BOSS_WAVE_RATIOS = [0.20, 0.30, 0.50]`), que subiu de 90s para 180s. Aviso visual pisca-pisca antes de cada spawn agendado (`BOSS_WARNING_LEAD_TIME`/`BOSS_WARNING_DURATION`), com controle de disparo (`Room.boss_warnings_triggered`) separado do controle de spawn real (`Room.boss_spawns_triggered`) (Sprint 046B)

## Backlog — Próximos Blocos (decisão em aberto)
- Bloco de Entidades de Chefes — quebrado em 5 Sprints menores, nesta ordem:
  - **Sprint A (concluída — 046A):** Sistema de ondas com timer e acúmulo — cada onda tem countdown próprio; soma inimigos remanescentes, nunca substitui.
  - **Sprint B (concluída — 046B):** Mini-chefe — fraco, ~300 HP; drop: pickup `SuperMagnet` que, só ao ser coletado, libera 3 upgrades garantidos (+1 nível em power-ups já adquiridos pelo player) + puxão automático de todas as gemas da sala. Nasce 1x por visita, agendado por fração de onda (fim da Onda 1, meio da Onda 2, 1/3 da Onda 3).
  - **Sprint C (em andamento):** Chefe — normal, ~700 HP; drop CUMULATIVO: tudo que o Mini-chefe dropa (via mesmo pickup, ou pickup próprio — decidir na sprint) + 50% de HP do player + puxão automático de gemas. Segue o mesmo padrão de agendamento da Sprint B: fim da Onda 2, 2/3 da Onda 3.
  - **Sprint D:** Chefão — forte, ~2000 HP; ataque de projétil sequencial (~12 tiros lentos e desviáveis, cada um mirando a posição do player NO MOMENTO do disparo, não perseguição contínua — 1º mira onde o player está, ele se move, 2º mira a última posição registrada, etc. — testar); chefes de "retorno de sala" (revisitas) podem reaproveitar esse padrão + variação "raio" que persegue o player por um tempo; chefões variam de tipo entre si; drop cumulativo dos dois anteriores + o que for específico dele.
  - **Sprint E:** Composição final — as 3 ondas completas (Onda 1: 1 swarm central + 1 mini-chefe; Onda 2: 2 swarms divididos + 1 mini-chefe central + 1 chefe; Onda 3/final: 3 swarms + 2 mini-chefes + 1 chefe + o chefão); contador grande e chamativo avisando a chegada do chefão na onda final; integração completa do sistema de ondas com o critério de vitória da sala (hoje ainda rodam em paralelo, não integrados). Nota: a divisão proporcional 20/30/50% e a duração total já foram implementadas antecipadamente na Sprint B (180s, ajustável) — o que resta aqui é a composição completa de inimigos por onda.
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
- Cor do Ímã Super Power muito parecida com a cor do aviso de chefe se aproximando (`(255, 215, 0)` vs `(255, 210, 60)`) — não é bug, pode confundir visualmente à distância; revisar na passada de polish geral — identificado na Sprint 046B

## Preferências de Estilo
- Tema Star Trek (Stardate, terminologia de nave)
- Gosta de estatística/dado: ranking, estatística por sessão e por tipo de inimigo, histórico de jogador como feature paga futura
- Quer honestidade direta, inclusive crítica a ideia ruim, sem filtro
- Comunicação rápida com ideias no meio da sessão — devem ser triadas/registradas, não implementadas na hora
- Sempre entregar documentos completos para download ao fechar sprint, não diffs manuais
