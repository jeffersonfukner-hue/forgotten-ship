WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600

WINDOW_TITLE: str = "Forgotten Ship"

FPS: int = 60


# ==========================================================================
# TUNING / DESENVOLVIMENTO
# Constantes ajustaveis para testes rapidos, sem precisar caçar valores
# espalhados pelo codigo. Mude aqui, teste, ajuste - sem editar a logica.
# ==========================================================================

# --- Player: combate ---
PLAYER_MAX_HP: int = 100
PLAYER_MAX_LIVES: int = 5
PLAYER_SHOOT_INTERVAL: float = 0.8  # segundos entre disparos automaticos
# valor inicial do alcance (percepcao de inimigos e alcance do tiro compartilham
# este raio) - sobrescrito a cada frame por get_passive_value("range") assim que
# o Player e criado; ver entrada "range" em POWER_UPS logo abaixo
PLAYER_RANGE_RADIUS: float = 100
PLAYER_KNOCKBACK_FORCE: int = 220
PLAYER_SHOOT_DAMAGE: int = 10  # dano de cada projetil disparado automaticamente

# --- Player: progressao (drops e upgrades) ---
# pontos de drop necessarios para o proximo level up (abre a tela de escolha de 3 opcoes)
POINTS_PER_UPGRADE: int = 1
# quanto o dano do tiro aumenta a cada escolha de "damage"
UPGRADE_DAMAGE_INCREMENT: int = 5
# limiar de pontos cresce 50% a cada upgrade conquistado
UPGRADE_THRESHOLD_GROWTH: float = 1.5

# ==========================================================================
# POWER-UPS: configuracao generica por chave, ativos e passivos
# Cada entrada e um eixo de upgrade escolhivel na tela de level up. O campo
# "type" ("active" ou "passive") classifica o eixo para fins estatisticos
# (comparacao de eficiencia entre tipos de escolha, futura area de simulacao
# de builds) - nao afeta a logica de jogo, apenas metadados.
# "active" = arma/sistema que causa dano por conta propria (Sabre, Sifao,
# Campo de Forca, armas de fogo, variantes do Tiro Multiplo).
# "passive" = modifica um atributo do player sem agir por si so (Ima,
# Regeneracao, Escudo, e os eixos de Velocidade/Penetracao/Rajada/Alcance
# do Tiro base).
# Adicionar novo power-up aqui, sem precisar mexer na logica do Player
# (mesmo padrao de ENEMY_TYPES).
# ==========================================================================
POWER_UPS: dict = {
    "magnet": {
        "base_value": 60,   # raio inicial de atracao, em pixels
        "increment": 20,    # ganho de raio por nivel
        "max_level": 5,
        "type": "passive",
    },
    "regen": {
        "base_value": 1,    # HP regenerado por segundo, no nivel 1
        "increment": 1,     # ganho de HP/s por nivel
        "max_level": 5,
        "type": "passive",
    },
    "sabre_quantidade": {
        # nivel 0 = nenhuma lamina (arma ainda nao escolhida)
        "base_value": 0,
        # +1 lamina por nivel (nivel 1 = 1 lamina, nivel 5 = 5 laminas)
        "increment": 1,
        "max_level": 5,
        "type": "active",
    },
    "sabre_velocidade": {
        "base_value": 90,   # graus por segundo de giro, no nivel 1
        "increment": 30,    # ganho de velocidade de giro por nivel
        "max_level": 5,
        "type": "active",
    },
    "sabre_dano": {
        "base_value": 5,    # dano por lamina, no nivel 1
        "increment": 3,     # ganho de dano por nivel
        "max_level": 5,
        "type": "active",
    },
    "siphon_dano": {
        # nivel 0 = arma nao dispara ainda (sem dano, sem efeito)
        "base_value": 0,
        "increment": 4,     # dano do raio extrator por disparo, por nivel
        "max_level": 5,
        "type": "active",
    },
    "siphon_conversao": {
        "base_value": 0,    # nivel 0 = nenhuma cura, mesmo se a arma ja disparar
        # fracao do dano causado convertida em cura (0.1 = 10%)
        "increment": 0.1,
        "max_level": 5,
        "type": "active",
    },
    "escudo_reducao": {
        "base_value": 10,   # 10% de reducao de dano no nivel 1
        "increment": 10,    # nivel 2 = 20%
        "max_level": 2,
        "type": "passive",
    },
    "escudo_barreira": {
        "base_value": 30,   # HP maximo da barreira no nivel 1
        "increment": 30,    # nivel 2 = 60 HP maximo
        "max_level": 2,
        "type": "passive",
    },
    "escudo_bloqueio": {
        "base_value": 1,    # so serve como "flag" - liga o bloqueio periodico
        "increment": 0,
        "max_level": 1,
        "type": "passive",
    },
    "tiro_diagonal": {
        # nivel 1 = 1 par de tiros diagonais (3 tiros total, com o reto)
        "base_value": 1,
        "increment": 1,     # cada nivel soma mais um par angulado
        "max_level": 5,
        "type": "active",
    },
    "tiro_quadrantes": {
        "base_value": 1,    # apenas marca o nivel (1=Tras, 2=+Cima, 3=+Baixo)
        "increment": 1,
        "max_level": 3,     # forca/velocidade ja vem dos upgrades globais existentes
        "type": "active",
    },
    "tiro_paralelo": {
        "base_value": 1,    # nivel 1 = 2 tiros em paralelo
        "increment": 1,     # nivel 2 = 3 tiros, ate nivel 5 = 6 tiros
        "max_level": 5,
        "type": "active",
    },
    "tiro_velocidade": {
        # velocidade padrao do projetil (mesmo valor de antes desta feature)
        "base_value": 400,
        "increment": 80,    # ganho de velocidade por nivel
        "max_level": 5,
        "type": "passive",
    },
    "tiro_penetracao": {
        # nivel 0 = 1 impacto (comportamento atual, sem regressao)
        "base_value": 1,
        "increment": 1,     # +1 inimigo atravessado por nivel
        "max_level": 5,
        "type": "passive",
    },
    "tiro_rajada": {
        "base_value": 1,    # nivel 0 = 1 tiro por gatilho (normal)
        "increment": 1,     # nivel 1 = 2 tiros, nivel 5 = 6 tiros por rajada
        "max_level": 5,
        "type": "passive",
    },
    "range": {
        "base_value": 100,  # mesmo valor de PLAYER_RANGE_RADIUS, sem regressao no nivel 0
        "increment": 40,    # ganho de alcance por nivel
        "max_level": 5,
        "type": "passive",
    },
    "campo_area": {
        # nivel 0 = campo nao existe ainda (raio zero, sem efeito)
        "base_value": 0,
        "increment": 40,    # ganho de raio por nivel, em pixels
        "max_level": 5,
        "type": "active",
    },
    "campo_dano": {
        "base_value": 4,    # dano aplicado a cada tique (0.5s), no nivel 1
        "increment": 3,     # ganho de dano por tique, por nivel
        "max_level": 5,
        "type": "active",
    },
    "phaser_capacidade": {
        # nivel 0 = arma nao existe (base_value nao usado, existencia checada por nivel > 0)
        "base_value": 4,
        "increment": 1,     # nivel 1 = 5 tiros, nivel 5 = 9 tiros por carregador
        "max_level": 5,
        "type": "active",
    },
    "phaser_dano": {
        # dano por tiro, no nivel 1 (arma ja atira com esse valor de base)
        "base_value": 5,
        "increment": 3,     # ganho de dano por nivel
        "max_level": 5,
        "type": "active",
    },
    "phaser_reload": {
        "base_value": 2.0,  # segundos de recarga, no nivel 1
        # cada nivel reduz o tempo de recarga (reload mais rapido)
        "increment": -0.3,
        "max_level": 5,
        "type": "active",
    },
    "plasma_capacidade": {
        "base_value": 11,   # nivel 1 = 12 tiros no carregador
        "increment": 2,     # nivel 5 = 20 tiros
        "max_level": 5,
        "type": "active",
    },
    "plasma_dano": {
        "base_value": 15,   # dano por tiro, no nivel 1 - bem mais alto que o Phaser
        "increment": 6,     # ganho de dano por nivel
        "max_level": 5,
        "type": "active",
    },
    "plasma_reload": {
        "base_value": 3.5,  # segundos de recarga, no nivel 1 - mais lento que o Phaser
        "increment": -0.5,  # cada nivel reduz o tempo de recarga
        "max_level": 5,
        "type": "active",
    },
    "pulso_capacidade": {
        "base_value": 19,   # nivel 1 = 20 tiros no carregador
        "increment": 1,     # nivel 5 = 24 tiros
        "max_level": 5,
        "type": "active",
    },
    "pulso_dano": {
        "base_value": 3,    # dano por tiro, no nivel 1 - baixo, compensado pela cadencia
        "increment": 1,     # ganho de dano por nivel
        "max_level": 5,
        "type": "active",
    },
    "pulso_reload": {
        "base_value": 1.0,  # segundos de recarga, no nivel 1 - reload rapido
        "increment": -0.15,  # cada nivel reduz o tempo de recarga
        "max_level": 5,
        "type": "active",
    },
    "pulso_cadencia": {
        "base_value": 0.12,  # segundos entre tiros, no nivel 1 - ja bem rapido de saida
        "increment": -0.015,  # cada nivel acelera ainda mais a cadencia
        "max_level": 5,
        "type": "active",
    },
}

# --- agrupa eixos que pertencem a mesma arma, para contagem de slots (uma arma = 1 slot, nao 1 por eixo) ---
CATEGORY_GROUPS: dict = {
    "sabre_quantidade": "sabre",
    "sabre_velocidade": "sabre",
    "sabre_dano": "sabre",
    "siphon_dano": "sifao",
    "siphon_conversao": "sifao",
    "escudo_reducao": "escudo",
    "escudo_barreira": "escudo",
    "escudo_bloqueio": "escudo",
    "tiro_diagonal": "tiro_multiplo",
    "tiro_quadrantes": "tiro_multiplo",
    "tiro_paralelo": "tiro_multiplo",
    "campo_area": "campo",
    "campo_dano": "campo",
    "phaser_capacidade": "phaser",
    "phaser_dano": "phaser",
    "phaser_reload": "phaser",
    "plasma_capacidade": "plasma",
    "plasma_dano": "plasma",
    "plasma_reload": "plasma",
    "pulso_capacidade": "pulso",
    "pulso_dano": "pulso",
    "pulso_reload": "pulso",
    "pulso_cadencia": "pulso",
}

# --- categorias onde a PRIMEIRA escolha entre os ramos bloqueia os demais para sempre -
# diferente de pre-requisito (que so exige nivel minimo em outro eixo), aqui os ramos
# irmaos se tornam inacessiveis assim que qualquer um deles for escolhido ---
EXCLUSIVE_CATEGORIES: set = {"tiro_multiplo"}

# --- categorias que nunca ocupam slot de power-up, mesmo apos equipadas -
# tiro multiplo e os eixos soltos do Tiro base sao parte do Tiro (arma inicial),
# que ja nao ocupa slot como "damage" ---
FREE_CATEGORIES: set = {
    "tiro_multiplo", "tiro_velocidade", "tiro_penetracao", "tiro_rajada", "range",
}

# --- pre-requisitos: eixo -> (eixo do qual depende, nivel minimo exigido) ---
# eixo com pre-requisito so aparece como opcao depois que o eixo base atingir o nivel exigido -
# cria sensacao de progresso e novidade (feature nova se abre em nivel avancado, nao tudo de uma vez)
UPGRADE_PREREQUISITES: dict = {
    "sabre_velocidade": ("sabre_quantidade", 1),
    "sabre_dano": ("sabre_quantidade", 1),
    "siphon_conversao": ("siphon_dano", 1),
    # cadeia do escudo: reducao -> barreira -> bloqueio, cada camada some-se as anteriores
    "escudo_barreira": ("escudo_reducao", 2),
    "escudo_bloqueio": ("escudo_barreira", 2),
    "campo_dano": ("campo_area", 1),
    "phaser_dano": ("phaser_capacidade", 1),
    "phaser_reload": ("phaser_capacidade", 1),
    "plasma_dano": ("plasma_capacidade", 1),
    "plasma_reload": ("plasma_capacidade", 1),
    "pulso_dano": ("pulso_capacidade", 1),
    "pulso_reload": ("pulso_capacidade", 1),
    "pulso_cadencia": ("pulso_capacidade", 1),
}

# --- quantos power-ups diferentes (fora "damage") o jogador pode ter equipados, por nivel minimo ---
POWERUP_SLOTS_BY_LEVEL: list = [
    (0, 2),
    (5, 3),
    (10, 4),
    (15, 5),
]

# --- siglas compactas por categoria, para o resumo do painel de debug ---
CATEGORY_LABELS: dict = {
    "magnet": "I",
    "regen": "R",
    "sabre": "S",
    "sifao": "SF",
    "escudo": "ED",
    "tiro_multiplo": "TM",
    "campo": "CF",
    "phaser": "PL",
    "plasma": "CP",
    "pulso": "MP",
}

# --- nomes exibidos na tela de escolha de upgrade (chave -> texto amigavel) ---
UPGRADE_LABELS: dict = {
    "damage": "Dano do Tiro",
    "magnet": "Ima (raio de atracao)",
    "regen": "Regeneracao de Vida",
    "sabre_quantidade": "Sabre - Quantidade de Laminas",
    "sabre_velocidade": "Sabre - Velocidade de Giro",
    "sabre_dano": "Sabre - Dano por Lamina",
    "siphon_dano": "Sifao de Energia - Dano",
    "siphon_conversao": "Sifao de Energia - Conversao em Reparo",
    "escudo_reducao": "Escudo Deflector - Reducao de Dano",
    "escudo_barreira": "Escudo Deflector - Barreira de Energia",
    "escudo_bloqueio": "Escudo Deflector - Bloqueio Periodico",
    "tiro_diagonal": "Tiro Multiplo - Diagonal",
    "tiro_quadrantes": "Tiro Multiplo - Quadrantes",
    "tiro_paralelo": "Tiro Multiplo - Paralelo",
    "tiro_velocidade": "Tiro - Velocidade",
    "tiro_penetracao": "Tiro - Penetracao",
    "tiro_rajada": "Tiro - Rajada",
    "range": "Tiro - Alcance",
    "campo_area": "Campo de Forca - Area",
    "campo_dano": "Campo de Forca - Dano",
    "phaser_capacidade": "Phaser Leve - Capacidade do Carregador",
    "phaser_dano": "Phaser Leve - Dano",
    "phaser_reload": "Phaser Leve - Velocidade de Recarga",
    "plasma_capacidade": "Canhao de Plasma - Capacidade do Carregador",
    "plasma_dano": "Canhao de Plasma - Dano",
    "plasma_reload": "Canhao de Plasma - Velocidade de Recarga",
    "pulso_capacidade": "Metralhadora de Pulso - Capacidade do Carregador",
    "pulso_dano": "Metralhadora de Pulso - Dano",
    "pulso_reload": "Metralhadora de Pulso - Velocidade de Recarga",
    "pulso_cadencia": "Metralhadora de Pulso - Cadencia",
}

# --- Gemas: coleta e efeito de arrasto ---
# distancia (entre centros) para a gema comecar a ser puxada
GEM_PICKUP_RADIUS: float = 60
# distancia minima para considerar a gema efetivamente coletada
GEM_COLLECT_DISTANCE: float = 6
# aceleracao da gema enquanto e puxada (pixels/s por segundo)
GEM_PULL_ACCELERATION: float = 400
# velocidade maxima que a gema pode atingir sendo puxada
GEM_PULL_MAX_SPEED: float = 500

# --- Horda: geracao de inimigos ---
HORDE_BASE_ENEMIES: int = 12  # quantidade de inimigos na primeira horda de uma sala
# segundos que cada onda dura antes da proxima ser somada aos inimigos remanescentes -
# nao espera a onda atual acabar, e nao substitui: acumula (ver Room.wave_timer)
WAVE_DURATION: float = 15.0
# incremento de inimigos a cada revisita (rejogabilidade) - conectado em spawn_horde(),
# multiplicado por room.times_cleared (quantidade de vezes que a sala ja foi vencida)
HORDE_ENEMIES_PER_VISIT: int = 6
# fracao do piso de inimigos que precisa estar morta para iniciar o reabastecimento
# gradual (0.2 = 20%) - antes disso, a sala fica sem reabastecer, dando respiro real
HORDE_REINFORCEMENT_TRIGGER_RATIO: float = 0.2
# segundos entre cada inimigo reabastecido individualmente - reabastecimento gradual,
# nao em massa (reabastecer tudo de uma vez fica reservado para o futuro modo "swarm")
HORDE_REINFORCEMENT_INTERVAL: float = 1.0
# distancia minima entre um inimigo e qualquer porta ao nascer
SAFE_SPAWN_DISTANCE: float = 120
# segundos que o jogador precisa sobreviver para limpar a sala
ROOM_SURVIVAL_DURATION: float = 180.0

# --- Bloco de Entidades de Chefes: divisao proporcional do tempo total da sala
# entre as 3 ondas (crescente, mais dificil no final - mesma referencia de
# mercado registrada no VISAO.md) ---
BOSS_WAVE_RATIOS: list = [0.20, 0.30, 0.50]

# --- agenda de spawn de cada chefe: lista de (numero_da_onda, fracao_dentro_da_onda).
# Cada entrada dispara 1 spawn daquele boss_type quando o tempo decorrido da sala
# atinge aquele ponto - uma unica vez por visita. Mini-chefe: fim da Onda 1, meio
# da Onda 2, 1/3 da Onda 3 (Sprint B). Chefe e Chefao seguem o mesmo padrao nas
# suas proprias sprints (C e D) - registrado aqui como documentacao do formato,
# ainda comentado ate as entidades existirem. ---
BOSS_SPAWN_SCHEDULE: dict = {
    "mini_boss": [(1, 1.0), (2, 0.5), (3, 1 / 3)],
    # "chefe": [(2, 1.0), (3, 2 / 3)],   # Sprint C - fim da Onda 2, 2/3 da Onda 3
    # "chefao": [(3, 1.0)],              # Sprint D - ultimo, absorve sobreviventes
}

# --- Bloco de Entidades de Chefes: aviso visual antes de cada chefe nascer ---
BOSS_WARNING_LEAD_TIME: float = 4.0  # segundos de antecedencia do aviso
BOSS_WARNING_DURATION: float = 3.0   # segundos que o aviso fica visivel na tela
# segundos entre cada estado (visivel/invisivel) do retangulo vermelho pisca-pisca
BOSS_WARNING_BLINK_INTERVAL: float = 0.15

BOSS_WARNING_LABELS: dict = {
    "mini_boss": "MINI-CHEFE SE APROXIMANDO",
    # "chefe": "CHEFE SE APROXIMANDO",     # Sprint C
    # "chefao": "CHEFAO SE APROXIMANDO",   # Sprint D
}

# tempo (s) para a chance de inimigo forte atingir o maximo
STRONG_ENEMY_RAMP_TIME: float = 20.0
# chance maxima (50%) de spawnar um inimigo forte no reabastecimento
STRONG_ENEMY_MAX_CHANCE: float = 0.5

# --- Reentradas: limite de revisitas por sala ---
ROOM_MAX_REENTRIES: int = 5
ROOM_REGEN_INTERVAL: float = 60.0  # segundos para regenerar 1 reentrada

# --- Inimigos: configuracao por tipo (Terrestre fraco/forte, por enquanto) ---
ENEMY_TYPES: dict = {
    "weak": {
        "hp": 20,
        "speed": 80,
        "width": 14,
        "height": 14,
        "color": (180, 60, 60),  # vermelho
        "damage": 10,  # dano causado ao player por contato
    },
    "strong": {
        "hp": 40,
        "speed": 70,  # um pouco mais lento, compensando o HP maior
        "width": 18,
        "height": 18,
        "color": (120, 40, 90),  # roxo escuro, visualmente distinto
        "damage": 20,  # mais forte, condizente com o tamanho e HP maiores
    },
    "mini_boss": {
        "hp": 300,
        "speed": 60,  # mais lento que os Terrestres comuns, compensando o HP alto
        "width": 32,
        "height": 32,
        # dourado, visualmente distinto de weak/strong
        "color": (210, 170, 40),
        "damage": 25,
        # flag lida por Enemy.__init__ e usada em GameScene para desviar do
        # drop de gema normal (chefe dropa o Ima Super Power, nao gema direto)
        "is_boss": True,
    },
}

# (hp + damage) / este valor = pontos de drop do inimigo
ENEMY_POINTS_DIVISOR: float = 30

# --- Sabre Giratorio: orbita o player, dano por contato continuo ---
SABER_ORBIT_RADIUS: float = 50  # distancia da lamina ate o centro do player
# segundos entre "cortes" no mesmo inimigo, evita dano por frame
SABER_HIT_COOLDOWN: float = 0.5

# --- Tiro (base): rajada dispara N tiros em sequencia rapida, sem re-mirar entre eles ---
BURST_SHOT_DELAY: float = 0.08  # segundos entre cada disparo dentro da mesma rajada

# --- Campo de Forca: dano em area ao redor do player, aplicado em tiques periodicos ---
FORCE_FIELD_TICK_INTERVAL: float = 0.5  # segundos entre cada pulso de dano

# --- Phaser Leve: municao limitada, mira o 3o inimigo mais proximo (cadencia fixa,
# diferente da Metralhadora de Pulso, cuja cadencia e um eixo upavel em POWER_UPS) ---
# segundos entre tiros, enquanto houver municao no carregador
PHASER_FIRE_RATE: float = 0.3

# --- Canhao de Plasma: dano concentrado, mira o 4o inimigo mais proximo (cadencia fixa) ---
PLASMA_FIRE_RATE: float = 0.6  # mais lenta que o Phaser, dano por tiro compensa

# --- Sifao de Energia: raio extrator instantaneo, mira o 2o inimigo mais proximo ---
# segundos entre disparos - cadencia propria, mais lenta que o tiro
SIPHON_INTERVAL: float = 1.5
# segundos que o feixe visual permanece na tela apos disparar
SIPHON_BEAM_DURATION: float = 0.15

# --- Escudo Deflector: 3 camadas cumulativas (reducao %, barreira HP, bloqueio periodico) ---
# segundos sem levar dano antes da barreira comecar a regenerar
SHIELD_REGEN_DELAY: float = 3.0
# HP de barreira regenerado por segundo, apos o delay
SHIELD_REGEN_RATE: float = 5.0
SHIELD_BLOCK_COOLDOWN: float = 8.0  # segundos entre bloqueios totais gratuitos

# --- Obstaculos: fixos (indestrutiveis) e destrutiveis (corroidos por inimigos, nao pelo player) ---
DESTRUCTIBLE_OBSTACLE_HP: int = 20
# quantidade gerada aleatoriamente por sala
DESTRUCTIBLE_OBSTACLES_PER_ROOM: int = 4
DESTRUCTIBLE_OBSTACLE_SIZE: int = 40  # largura/altura do obstaculo destrutivel
# segundos entre "mordidas" do inimigo no obstaculo (corrosao lenta)
OBSTACLE_DAMAGE_COOLDOWN: float = 0.5
# dano causado pelo inimigo ao obstaculo destrutivel por contato
ENEMY_OBSTACLE_DAMAGE: int = 2
# distancia minima entre um obstaculo destrutivel e a posicao de entrada de
# qualquer porta da sala - evita prender o player contra a parede ao entrar
DESTRUCTIBLE_OBSTACLE_DOOR_MARGIN: float = 100
# distancia minima entre um obstaculo destrutivel e a parede da sala - evita
# um vao estreito onde um inimigo poderia ficar preso entre parede e obstaculo
DESTRUCTIBLE_OBSTACLE_WALL_MARGIN: float = 30
