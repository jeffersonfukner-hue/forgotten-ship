# SPRINT 003 — Sistema de Múltiplas Salas

**Status:** 🚧 Em andamento

---

# Objetivo

Implementar a primeira versão do sistema de múltiplas salas do Forgotten Ship.

Até a Sprint anterior o jogo possuía apenas uma sala fixa. Nesta Sprint inicia-se a transição para uma arquitetura capaz de gerenciar diversas salas independentes, permitindo que o jogador navegue entre elas.

Esta arquitetura servirá como base para futuras funcionalidades, como:

- mapas maiores;
- salas persistentes;
- eventos permanentes;
- portas bloqueadas;
- geração procedural baseada em seeds.

---

# Evolução da Sprint

## 1. Cache de salas

O gerenciamento das salas passou a utilizar um dicionário (`self.rooms`) responsável por armazenar todas as salas já criadas durante a execução do jogo.

Anteriormente, uma nova instância de `Room` era criada sempre que o jogador atravessava uma porta.

Agora, cada sala é criada apenas na primeira visita e reutilizada nas visitas seguintes.

### Benefícios

- preservação do estado de cada sala;
- menor criação de objetos;
- preparação para persistência de eventos futuros;
- arquitetura compatível com mapas grandes.

---

## 2. Separação entre criação e configuração

Durante a implementação ficou evidente que o método `create_room()` estava acumulando responsabilidades.

A lógica foi dividida em duas etapas:

- criação da sala;
- configuração do conteúdo da sala.

Foi criado o método:

```python
configure_room(room, room_id)
```

responsável exclusivamente por adicionar paredes, portas e demais elementos.

### Benefícios

- menor acoplamento;
- código mais organizado;
- facilita manutenção;
- prepara a migração da configuração para estruturas de dados.

---

## 3. Estrutura de conexões

As conexões entre salas deixaram de ser definidas diretamente dentro da criação das portas.

Foi criada a estrutura:

```python
self.room_connections = {
    1: 2,
    2: 3,
    3: 1,
}
```

As portas passaram a consultar essa estrutura para descobrir qual é sua sala de destino.

### Benefícios

- elimina valores fixos espalhados pelo código;
- simplifica alterações futuras;
- aproxima o projeto de uma arquitetura orientada a dados.

---

## 4. Inclusão da terceira sala

Foi criada uma terceira sala para validar o funcionamento do sistema de cache e das conexões.

A sequência atual ficou:

```
Room 1
   ↓
Room 2
   ↓
Room 3
   ↓
Room 1
```

Essa estrutura permitiu testar o reaproveitamento das salas e confirmar que o sistema funciona corretamente.

---

# Problemas encontrados

## Teletransporte imediato

Durante os testes foi identificado um comportamento inesperado.

Ao entrar na terceira sala, o jogador era imediatamente transportado novamente para outra sala.

Após análise verificou-se que o ponto de spawn estava sobrepondo a área de colisão da porta.

### Decisão

Optou-se por não corrigir esse comportamento nesta Sprint.

A solução será implementada futuramente juntamente com o sistema definitivo de transição entre salas.

---

# Decisões Arquiteturais

Durante esta Sprint foram definidas algumas diretrizes importantes para a evolução do projeto.

- Cada sala existirá apenas uma vez durante a execução do jogo.
- O estado de cada sala deverá ser preservado.
- A configuração das salas será gradualmente migrada para estruturas de dados.
- As conexões entre salas serão orientadas por dados e não por código fixo.
- A arquitetura deverá suportar geração procedural baseada em seeds.

---

# Conhecimentos adquiridos

Durante esta Sprint foi possível observar alguns conceitos importantes de arquitetura de software.

## Cache de objetos

Nem sempre recriar objetos é a melhor solução.

Manter instâncias reutilizáveis permite preservar estado e reduz processamento.

---

## Separação de responsabilidades

Criar um objeto e configurá-lo são responsabilidades diferentes.

Separar essas etapas torna o código mais simples e facilita futuras modificações.

---

## Arquitetura orientada a dados

Mover informações do código para estruturas de dados torna o sistema mais flexível e reduz dependências entre componentes.

Esta decisão será fundamental para a futura geração procedural da nave.

---

# Próximos passos

- iniciar a migração da configuração das salas para uma estrutura de dados;
- implementar bloqueio de transição imediata entre salas;
- preparar o sistema para portas com estados (travadas, destravadas, etc.);
- expandir o mapa para validar a escalabilidade da arquitetura.