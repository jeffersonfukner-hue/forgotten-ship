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
PLAYER_RANGE_RADIUS: float = 300  # raio unico: percepcao de inimigos e alcance do tiro
PLAYER_KNOCKBACK_FORCE: int = 220
PLAYER_SHOOT_DAMAGE: int = 10  # dano de cada projetil disparado automaticamente
POINTS_PER_UPGRADE: int = 10  # pontos de drop necessarios para o proximo upgrade automatico
UPGRADE_DAMAGE_INCREMENT: int = 5  # quanto o dano do tiro aumenta a cada upgrade
UPGRADE_THRESHOLD_GROWTH: float = 1.5  # limiar de pontos cresce 50% a cada upgrade conquistado

# --- Horda: geracao de inimigos ---
HORDE_BASE_ENEMIES: int = 12  # quantidade de inimigos na primeira horda de uma sala
HORDE_ENEMIES_PER_VISIT: int = 6  # incremento de inimigos a cada revisita (rejogabilidade)
SAFE_SPAWN_DISTANCE: float = 120  # distancia minima entre um inimigo e qualquer porta ao nascer
ROOM_SURVIVAL_DURATION: float = 30.0  # segundos que o jogador precisa sobreviver para limpar a sala
STRONG_ENEMY_RAMP_TIME: float = 20.0  # tempo (s) para a chance de inimigo forte atingir o maximo
STRONG_ENEMY_MAX_CHANCE: float = 0.5  # chance maxima (50%) de spawnar um inimigo forte no reabastecimento

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
ENEMY_POINTS_DIVISOR: float = 30  # (hp + damage) / este valor = pontos de drop do inimigo