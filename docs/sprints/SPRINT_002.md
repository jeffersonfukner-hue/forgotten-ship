# SPRINT 002 — Sistema de Salas, Portas e Tipagem

**Status:** ✅ Concluída

---

# Objetivo

Evoluir a arquitetura do Forgotten Ship, introduzindo um sistema de salas conectado por portas, melhorando a organização do projeto e realizando a primeira auditoria completa de tipagem utilizando Type Hints.

---

# Implementações

## Sistema de Salas

Foi criada a classe `Room`, responsável por representar uma sala do jogo.

Cada sala possui:

- limites (Rect);
- ponto de spawn;
- portas;
- desenho das paredes;
- atualização das portas.

A responsabilidade de controlar a própria sala deixou de ficar espalhada em outras classes.

---

## Sistema de Portas

Foi criada a classe `Door`.

Cada porta possui:

- posição;
- direção;
- sala de destino;
- ponto de spawn na próxima sala.

A detecção de colisão passou a ser responsabilidade da própria porta.

---

## Navegação entre Salas

O Player passou a detectar quando atravessa uma porta.

Quando isso ocorre:

- registra a porta utilizada;
- solicita troca de sala;
- GameScene cria a nova sala;
- Player reaparece no spawn correspondente.

A troca de salas ficou totalmente desacoplada do restante do código.

---

## Máquina de Estados do Player

Foi implementada uma pequena máquina de estados para controlar o comportamento do jogador durante a transição entre salas.

Estados utilizados:

- Normal
- Room Transition

Isso eliminou verificações espalhadas pelo código.

---

## Refatorações

Durante esta Sprint foram realizadas diversas melhorias arquiteturais.

Entre elas:

- redução de responsabilidades da GameScene;
- separação das classes Room e Door;
- simplificação da lógica de colisão;
- organização dos imports;
- melhoria na estrutura das entidades.

---

# Tipagem (Type Hints)

Foi realizada uma auditoria completa de tipagem.

Foram adicionados Type Hints em:

- atributos;
- parâmetros;
- retornos;
- constantes;
- listas;
- tuplas;
- referências entre classes.

Também foram utilizados:

- `None`
- Union (`|`)
- Forward References

---

# Conceitos Aprendidos

Durante esta Sprint foram estudados:

- Type Hints
- Organização de classes
- Separação de responsabilidades
- Composição
- Responsabilidade única (SRP)
- Estados de objetos
- Navegação entre salas
- Organização de projeto em módulos

---

# Arquivos Trabalhados

- main.py
- game.py
- settings.py
- entities/entity.py
- entities/player.py
- entities/door.py
- entities/entity_manager.py
- systems/room.py
- scenes/scene.py
- scenes/game_scene.py

---

# Bugs Corrigidos

Entre os problemas resolvidos durante a Sprint:

- colisão nas bordas;
- posicionamento incorreto após troca de sala;
- normalização de direção;
- organização da lógica de atualização;
- pequenos erros de tipagem;
- ajustes na arquitetura.

---

# Resultado

Ao final da Sprint o projeto possui:

- arquitetura modular;
- sistema funcional de salas;
- sistema funcional de portas;
- troca de salas operacional;
- tipagem consistente;
- código significativamente mais organizado.

A base do projeto está pronta para receber novas funcionalidades sem necessidade de grandes refatorações.

---

# Próxima Sprint

## Sprint 003

Implementação de um sistema de múltiplas salas, permitindo expandir o mapa da nave de forma organizada e preparando a arquitetura para a futura geração procedural baseada em seeds.

---

**Fim da Sprint 002**