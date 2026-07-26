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
POINTS_PER_UPGRADE: int = 10
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

# --- Obstaculos: fixos (indestrutiveis) e destrutiveis (corroidos por inimigos, nao pelo player) ---
DESTRUCTIBLE_OBSTACLE_HP: int = 20
# quantidade gerada aleatoriamente por sala
DESTRUCTIBLE_OBSTACLES_PER_ROOM: int = 4
DESTRUCTIBLE_OBSTACLE_SIZE: int = 40  # largura/altura do obstaculo destrutivel
# segundos entre "mordidas" do inimigo no obstaculo (corrosao lenta)
OBSTACLE_DAMAGE_COOLDOWN: float = 0.5
# dano causado pelo inimigo ao obstaculo destrutivel por contato
ENEMY_OBSTACLE_DAMAGE: int = 2
