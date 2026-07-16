# SPRINT_001.md

# USS Forgotten Ship

## Sprint 001 --- Fundação do Projeto

------------------------------------------------------------------------

## Data

Início: 13/07/2026

Conclusão: 15/07/2026

------------------------------------------------------------------------

# Objetivo

Construir toda a fundação técnica do Forgotten Ship.

Ao final desta Sprint o projeto deveria possuir uma arquitetura
organizada, um Game Loop funcional, uma primeira sala jogável e um
ambiente de desenvolvimento completamente configurado.

Esta Sprint teve como foco estabelecer bases sólidas para todo o
restante do desenvolvimento.

------------------------------------------------------------------------

# Funcionalidades Implementadas

## Arquitetura

-   Estrutura inicial do projeto
-   Organização das pastas
-   Classe Game
-   Sistema de Scenes
-   Classe base Entity
-   EntityManager
-   Settings centralizados
-   Game Loop
-   Delta Time

## Gameplay

-   Player
-   Movimento em 8 direções
-   Normalização do movimento diagonal
-   Primeira sala
-   Paredes visuais
-   Limites da sala
-   Primeira colisão

## Infraestrutura

-   Configuração oficial do projeto
-   Ambiente virtual (.venv)
-   Python 3.14
-   pygame-ce
-   requirements.txt
-   Integração com GitHub
-   Primeiro fluxo oficial de commits

------------------------------------------------------------------------

# Decisões Arquiteturais

-   Scene System desacoplado.
-   Classe base Entity para padronização.
-   EntityManager centralizando atualização e renderização.
-   Desenvolvimento incremental: primeiro desenhar, depois adicionar
    comportamento.

------------------------------------------------------------------------

# Bugs Encontrados

1.  Construtor do Player incompatível com Entity.
2.  `draw()` fora da classe por erro de indentação.
3.  `dt` utilizado antes de ser calculado.
4.  `pygame.rect` em vez de `pygame.Rect`.
5.  `room.botton` em vez de `room.bottom`.
6.  Limite direito incorreto (`688` → `668`).
7.  Clamp aplicado antes do movimento.

------------------------------------------------------------------------

# Lições Aprendidas

-   A ordem das operações influencia diretamente o comportamento do
    jogo.
-   Testar jogando revela bugs que a leitura do código não encontra.
-   Implementações incrementais reduzem a complexidade.
-   Corrigir cedo é mais barato do que refatorar tarde.

------------------------------------------------------------------------

# Estado Final

-   Arquitetura pronta.
-   Primeira sala funcional.
-   Player com movimentação e limites.
-   Ambiente de desenvolvimento configurado.

------------------------------------------------------------------------

# Próxima Sprint

-   Sistema de Room.
-   Portas.
-   Segunda sala.
-   Transição entre salas.
-   Spawn por porta.
