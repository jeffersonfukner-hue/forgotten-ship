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

# --- Horda: geracao de inimigos ---
HORDE_BASE_ENEMIES: int = 1  # quantidade de inimigos na primeira horda de uma sala
HORDE_ENEMIES_PER_VISIT: int = 6  # incremento de inimigos a cada revisita (rejogabilidade)
SAFE_SPAWN_DISTANCE: float = 120  # distancia minima entre um inimigo e qualquer porta ao nascer

# --- Reentradas: limite de revisitas por sala ---
ROOM_MAX_REENTRIES: int = 5
ROOM_REGEN_INTERVAL: float = 60.0  # segundos para regenerar 1 reentrada