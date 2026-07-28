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
# raio unico: percepcao de inimigos e alcance do tiro
PLAYER_RANGE_RADIUS: float = 300
PLAYER_KNOCKBACK_FORCE: int = 220
PLAYER_SHOOT_DAMAGE: int = 10  # dano de cada projetil disparado automaticamente

# --- Player: progressao (drops e upgrades automaticos) ---
# pontos de drop necessarios para o proximo upgrade automatico
POINTS_PER_UPGRADE: int = 1
UPGRADE_DAMAGE_INCREMENT: int = 5  # quanto o dano do tiro aumenta a cada upgrade
# limiar de pontos cresce 50% a cada upgrade conquistado
UPGRADE_THRESHOLD_GROWTH: float = 1.5

# --- Power-ups passivos: configuracao generica por chave ---
# Cada entrada = um power-up passivo. Adicionar novo power-up aqui,
# sem precisar mexer na logica do Player (mesmo padrao de ENEMY_TYPES).
PASSIVE_POWERUPS: dict = {
    "magnet": {
        "base_value": 60,   # raio inicial de atracao, em pixels
        "increment": 20,    # ganho de raio por nivel
        "max_level": 5,
    },
    "regen": {
        "base_value": 1,    # HP regenerado por segundo, no nivel 1
        "increment": 1,     # ganho de HP/s por nivel
        "max_level": 5,
    },
    "sabre_quantidade": {
        # nivel 0 = nenhuma lamina (arma ainda nao escolhida)
        "base_value": 0,
        # +1 lamina por nivel (nivel 1 = 1 lamina, nivel 5 = 5 laminas)
        "increment": 1,
        "max_level": 5,
    },
    "sabre_velocidade": {
        "base_value": 90,   # graus por segundo de giro, no nivel 1
        "increment": 30,    # ganho de velocidade de giro por nivel
        "max_level": 5,
    },
    "sabre_dano": {
        "base_value": 5,    # dano por lamina, no nivel 1
        "increment": 3,     # ganho de dano por nivel
        "max_level": 5,
    },
    "siphon_dano": {
        # nivel 0 = arma nao dispara ainda (sem dano, sem efeito)
        "base_value": 0,
        "increment": 4,     # dano do raio extrator por disparo, por nivel
        "max_level": 5,
    },
    "siphon_conversao": {
        "base_value": 0,    # nivel 0 = nenhuma cura, mesmo se a arma ja disparar
        # fracao do dano causado convertida em cura (0.1 = 10%)
        "increment": 0.1,
        "max_level": 5,
    },
    "escudo_reducao": {
        "base_value": 10,   # 10% de reducao de dano no nivel 1
        "increment": 10,    # nivel 2 = 20%
        "max_level": 2,
    },
    "escudo_barreira": {
        "base_value": 30,   # HP maximo da barreira no nivel 1
        "increment": 30,    # nivel 2 = 60 HP maximo
        "max_level": 2,
    },
    "escudo_bloqueio": {
        "base_value": 1,    # so serve como "flag" - liga o bloqueio periodico
        "increment": 0,
        "max_level": 1,
    },
    "tiro_diagonal": {
        # nivel 1 = 1 par de tiros diagonais (3 tiros total, com o reto)
        "base_value": 1,
        "increment": 1,     # cada nivel soma mais um par angulado
        "max_level": 5,
    },
    "tiro_quadrantes": {
        "base_value": 1,    # apenas marca o nivel (1=Tras, 2=+Cima, 3=+Baixo)
        "increment": 1,
        "max_level": 3,     # forca/velocidade ja vem dos upgrades globais existentes
    },
    "tiro_paralelo": {
        "base_value": 1,    # nivel 1 = 2 tiros em paralelo
        "increment": 1,     # nivel 2 = 3 tiros, ate nivel 5 = 6 tiros
        "max_level": 5,
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
}

# --- categorias onde a PRIMEIRA escolha entre os ramos bloqueia os demais para sempre -
# diferente de pre-requisito (que so exige nivel minimo em outro eixo), aqui os ramos
# irmaos se tornam inacessiveis assim que qualquer um deles for escolhido ---
EXCLUSIVE_CATEGORIES: set = {"tiro_multiplo"}

# --- categorias que nunca ocupam slot de power-up, mesmo apos equipadas -
# tiro multiplo e parte do Tiro (base), que ja nao ocupa slot como "damage" ---
FREE_CATEGORIES: set = {"tiro_multiplo"}

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
HORDE_BASE_ENEMIES: int = 30  # quantidade de inimigos na primeira horda de uma sala
# incremento de inimigos a cada revisita (rejogabilidade)
HORDE_ENEMIES_PER_VISIT: int = 6
# distancia minima entre um inimigo e qualquer porta ao nascer
SAFE_SPAWN_DISTANCE: float = 120
# segundos que o jogador precisa sobreviver para limpar a sala
ROOM_SURVIVAL_DURATION: float = 30.0
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
}
# (hp + damage) / este valor = pontos de drop do inimigo
ENEMY_POINTS_DIVISOR: float = 30

# --- Sabre Giratorio: orbita o player, dano por contato continuo ---
SABER_ORBIT_RADIUS: float = 50  # distancia da lamina ate o centro do player
# segundos entre "cortes" no mesmo inimigo, evita dano por frame
SABER_HIT_COOLDOWN: float = 0.5

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
