# Contexto do Projeto — A1 Game Academy / Forgotten Ship

> Atualizar este arquivo a cada sprint fechado. Manter enxuto, sem histórico de conversa.

## Estado Atual
- Projeto: Forgotten Ship (jogo 01 da A1 Game Academy), horde survival espacial em Python/Pygame CE
- Vinculado a: canal do YouTube (documentação em vídeo) + curso pago futuro
- Último sprint fechado: [SPRINT_029.md] — Regeneração de vida (segundo power-up passivo) + correção do upgrade automático genérico
- Em andamento agora: pesquisar boas práticas validadas de power-up em jogos horde survival antes de decidir o próximo item (candidatos: arma Fang, armas de fogo, tiro múltiplo, sabre giratório, escudo)

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
- Power-ups passivos: configuração genérica via dicionário (`PASSIVE_POWERUPS`, mesmo padrão de `Enemy`/`Obstacle`), nível calculado sob demanda via `get_passive_value()`, sobem junto com o upgrade automático via laço sobre todos os itens configurados (sem escolha de opções ainda) — ímã e regeneração de vida implementados e validados juntos (Sprint 029)

## Bugs e Refinamentos Pendentes (Sprint futura de correção — Obstáculos)
- Bug: obstáculo destrutível pode nascer sobre a posição de entrada de uma porta, prendendo o player sem chance de escapar do dano
- Refinamento: obstáculos destrutíveis sem margem mínima da parede, permitindo inimigo preso no vão entre parede e obstáculo
- Conteúdo faltando: obstáculos fixos (`obstacle_data`) definidos só na Sala 1; Salas 2 e 3 sem nenhum

## Backlog — Blocos Pendentes (VISAO.md v4.9)
- Power-ups: arma Fang, armas de fogo (munição/recarga), tiro múltiplo, sabre giratório, escudo (ímã e regeneração de vida já implementados — Sprints 028/029)
- Boss Entities: mini-bosses, boss com barra de fases e stagger
- Ship Restoration: mecânica narrativa central (reparo da nave = defesa)

## Preferências de Estilo
- Tema Star Trek (Stardate, terminologia de nave)
- Gosta de estatística/dado: ranking, estatística por sessão e por tipo de inimigo, histórico de jogador como feature paga futura
- Quer honestidade direta, inclusive crítica a ideia ruim, sem filtro
- Comunicação rápida com ideias no meio da sessão — devem ser triadas/registradas, não implementadas na hora
