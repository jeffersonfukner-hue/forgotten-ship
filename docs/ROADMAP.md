# ROADMAP
### Forgotten Ship

> Este documento descreve as fases internas de desenvolvimento do jogo.
> Para o roadmap da Academia (múltiplos projetos), ver
> `a1-game-academy/docs/metodologia/ROADMAP.md`.

---

## Fase 1 — Jogo Mínimo Jogável
**Status:** Em andamento (Sprints 001-004 cobrem parte da fundação)

Objetivo: ter um ciclo completo de jogo, mesmo que simples, sem combate.

- Menu de inicialização (start).
- Um level completo, jogável do início ao fim.
- Condição de derrota (game over).
- Fluxo: Menu → Jogo → Game Over → volta ao Menu.

> Nota: esta fase foi iniciada antes da mudança de direção para o gênero
> Horde (ver `VISAO.md` v2.0). Parte da arquitetura de Room/Door construída
> nas Sprints 001-004 será revisada para se adequar à nova visão.

---

## Fase 2A — Hordes e Progressão
**Status:** Planejamento

Objetivo: transformar o jogo mínimo em uma experiência Horde completa,
com progressão permanente.

- Implementação do Modo 1 (Horde Interna) e Modo 2 (Horde de Nave),
  conforme `VISAO.md`.
- Sistemas de restauração com dupla função (defesa ativa / fortalecimento).
- Progressão permanente e dupla: Jogador e Nave.
- Sistema de upgrades (escolha de 1 ou 3 via vídeo simulado).
- 10 levels criados manualmente para validar o ciclo completo.

---

## Fase 2B — Geração Procedural e Comunidade
**Status:** Planejamento

Objetivo: expandir o jogo validado na Fase 2A para uma experiência
compartilhada entre jogadores.

- Geração automática do level 11 em diante, ao primeiro jogador
  completar o level 10.
- Registro do jogador **fundador** de cada level gerado.
- Banco de dados de jogadores e estatísticas de jogo.

  > ⚠️ **Atenção: LGPD/GDPR a considerar quando chegar essa etapa.**

- Ranking por país e por "mundo" (servidor/região).

---

## Fase 3 — A Definir
**Status:** Visão futura, não planejada em detalhe

Ideias registradas para o futuro, fora do escopo atual (ver `VISAO.md`,
seção "Fora do Escopo do MVP Atual"):

- Mundo aberto / exploração de planetas.
- Venda e troca de naves entre jogadores.

Detalhamento adiado intencionalmente, para não cair em planejamento
eterno antes das fases anteriores estarem concluídas.

---

## Nota sobre Proporcionalidade

As fases devem ser, na medida do possível, proporcionais em tempo e
volume de desenvolvimento. Se qualquer fase crescer desproporcionalmente
durante o planejamento ou execução, ela deve ser subdividida (como já
ocorreu aqui com a antiga Fase 2, dividida em 2A e 2B) em vez de crescer
sem controle.

---

## Histórico de Versões

### v1.1
- Fase 2 dividida em 2A (Hordes e Progressão) e 2B (Geração Procedural
  e Comunidade), por desproporção de escopo frente às demais fases.
- Adicionada nota de atenção a LGPD/GDPR na etapa de banco de dados.
- Adicionada seção de Proporcionalidade como princípio geral do roadmap.

### v1.0
- Documento criado, consolidando a visão de fases descrita durante
  a definição da mudança de direção do jogo (v2.0 do VISAO.md).
