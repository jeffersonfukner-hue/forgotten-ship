# SPRINT_009.md
### Forgotten Ship — A1 Game Academy

**Sprint:** 009
**Status:** Concluída
**Versão da Arquitetura:** Estrutura de Níveis com Múltiplas Salas

---

## Objetivo da Sprint

Continuar a Re-arquitetura Espacial iniciada na Sprint 008: remodelar
`room_data`/`door_data` para suportar o conceito de **nível**, onde
cada nível agrupa uma ou mais salas conectadas entre si, com tamanhos
e formatos livres — substituindo o layout de teste usado até aqui por
um desenho real de ambientes da nave.

---

## Situação Inicial

Ao final da Sprint 008, a câmera seguia corretamente o jogador em
salas maiores que a tela, mas `room_data`/`door_data` ainda continham
o layout de teste original (salas numeradas sequencialmente, todas do
mesmo tamanho, sem nenhum agrupamento conceitual entre elas).

---

## Problema

Sem um conceito de nível, não é possível expressar a visão descrita no
`VISAO.md`: "nível N possui N salas conectadas". Além disso, todas as
salas de teste compartilhavam o mesmo tamanho fixo — impedindo a
variação de formato necessária para ambientes como um corredor longo e
estreito, bem diferente de uma sala grande e quadrada.

---

## Decisão Arquitetural

### Campo `level` em `room_data`

Cada sala em `room_data` passou a incluir um campo `"level"`,
associando-a a um nível específico:

```python
room_data = {
    1: {"level": 1, "doors": [1], "spawn": (...)},
    2: {"level": 2, "doors": [2, 3]},
    3: {"level": 2, "doors": [4]},
}
```

Isso não altera o mecanismo de navegação (que continua operando por
porta-a-porta, como desde a Sprint 004) — é uma informação adicional,
usada para consultas futuras (ex: "quais salas pertencem ao nível 2?"),
sem modificar a lógica existente.

### Tamanhos de Sala Explícitos por Ambiente

Foi introduzido `ROOM_SIZES`, um dicionário mapeando cada `room_id` às
suas dimensões específicas, substituindo o tamanho fixo único usado
até então:

```python
ROOM_SIZES = {
    1: (1280, 960),   # Area de Carga
    2: (300, 1400),   # Corredor
    3: (900, 700),    # Engenharia
}
```

Essa mudança prova que a arquitetura de câmera da Sprint 008 já
suporta salas de qualquer formato — não apenas grandes e quadradas,
mas também longas e estreitas, sem exigir nenhum ajuste adicional na
lógica de câmera.

### Primeiro Desenho Real de Ambientes

O layout de teste (5 salas numeradas, sem identidade) foi substituído
pelo primeiro desenho real da nave: **Área de Carga** (Nível 1, sala
inicial), conectada por um **Corredor** (Nível 2) até a **Engenharia**
(Nível 2). Esse desenho substitui integralmente as configurações
anteriores de `room_data`/`door_data`, consideradas apenas testes
estruturais desde suas Sprints de origem.

---

## Conceitos de Python

- **Atributo de Classe como Tabela de Configuração** — `ROOM_SIZES`
  foi definido como atributo de classe (não de instância), por
  representar uma configuração fixa do jogo, não um estado que varia
  por objeto `GameScene`.
- **Metadado Adicional sem Alterar Lógica Existente** — adicionar
  `"level"` a um dicionário já em uso é uma forma simples e segura de
  estender uma estrutura de dados sem quebrar o código que já a
  consome (nenhum lugar que lê `room_data` precisou mudar, exceto
  quem for consultar o novo campo).

---

## Conceitos de Arquitetura

- **Extensão sem Ruptura (Backward-Compatible Data)** — a introdução
  do campo `level` não exigiu nenhuma mudança nos métodos que já
  liam `room_data` — um exemplo de como estruturas de dados bem
  desenhadas permitem crescer sem reescrever o que já funciona.
- **Validação de Arquitetura por Diversidade de Casos** — testar a
  câmera (Sprint 008) com um corredor extremamente longo e estreito,
  bem diferente da sala grande e quadrada usada no teste original,
  reforça a confiança de que a solução é genuinamente geral, não
  apenas ajustada a um caso específico.

---

## Implementações

### Missão 1 — Campo `level` em `room_data`

**Arquivo:** `game_scene.py`

Adicionado `"level"` a cada entrada de `room_data`, associando cada
sala ao nível ao qual pertence.

### Missão 2 — Tamanhos de Sala por Ambiente

**Arquivo:** `game_scene.py`

Criado `ROOM_SIZES`, e `create_room()` passou a consultá-lo para
definir as dimensões de cada sala, em vez de usar um tamanho fixo
único (exceto pela Sala 1, já ajustada na Sprint 008).

### Missão 3 — Primeiro Desenho Real: Área de Carga → Corredor → Engenharia

**Arquivo:** `game_scene.py`

Substituição integral do layout de teste por três ambientes com
identidade: Área de Carga (Nível 1), Corredor e Engenharia (ambos
Nível 2), conectados por portas reposicionadas para as dimensões reais
de cada sala.

---

## Estado Atual da Arquitetura

```
room_data = {
    1: {"level": 1, "doors": [1], "spawn": (...)},   # Area de Carga
    2: {"level": 2, "doors": [2, 3]},                 # Corredor
    3: {"level": 2, "doors": [4]},                    # Engenharia
}

ROOM_SIZES = {
    1: (1280, 960),
    2: (300, 1400),
    3: (900, 700),
}
```

Três ambientes navegáveis, com tamanhos e formatos distintos, a câmera
seguindo corretamente em todos eles. A estrutura já suporta a visão de
"nível N = N salas", validada com o Nível 2 (2 salas conectadas).

---

## O que o aluno aprendeu

Como estender uma estrutura de dados existente (adicionando um campo
novo) sem quebrar nenhum código que já a utiliza. Como separar
configuração (tamanhos de sala) de lógica (criação de sala), usando um
dicionário como tabela de consulta em vez de condicionais espalhadas.
Como validar que uma solução de arquitetura (a câmera) é genuinamente
robusta, testando-a contra um caso bem diferente do original (corredor
longo e estreito vs. sala grande e quadrada).

---

## Próxima Sprint

Continuação da Re-arquitetura Espacial: implementação da condição de
"sala limpa" (todos os inimigos eliminados) como pré-requisito para
destravar portas — base da Progressão Espacial descrita no `VISAO.md`,
ainda pendente. Também candidato: transição cinematográfica ao entrar
em uma nova sala/nível.

---

## Resumo Executivo

Esta Sprint remodela a estrutura de dados de salas e portas para
suportar o conceito de nível, com salas de tamanhos e formatos livres.
O layout de teste original foi substituído pelo primeiro desenho real
de ambientes da nave — Área de Carga, Corredor e Engenharia — validando
que a arquitetura de câmera da Sprint 008 funciona igualmente bem em
salas grandes e quadradas quanto em corredores longos e estreitos.
