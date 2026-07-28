import random

import pygame

from typing import TYPE_CHECKING

from src import settings
from src.entities.entity import Entity

if TYPE_CHECKING:
    # imports usados apenas para checagem de tipos (Pylance), evitando import circular real
    from src.systems.room import Room
    from src.systems.door import Door


class Player(Entity):

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x=x, y=y, width=32, height=32,)

        # --- movimento e navegacao entre salas ---
        self.state: str = "walking"
        self.speed: int = 250
        self.room: "Room | None" = None
        self.target_position: pygame.Vector2 | None = None
        self.current_door: "Door | None" = None
        self.room_change_requested: bool = False
        self.path: list[pygame.Vector2] = []

        # --- fade ao atravessar portas ---
        self.alpha: int = 255
        self.door_leg_start: pygame.Vector2 | None = None
        self.door_thickness: float = 0.0

        # --- vida e vidas (sistema de continuar apos morrer) ---
        self.max_hp: int = settings.PLAYER_MAX_HP
        self.hp: int = self.max_hp
        self.max_lives: int = settings.PLAYER_MAX_LIVES
        self.lives: int = self.max_lives
        self.is_dead: bool = False

        # --- cooldowns de dano e knockback ---
        self.damage_cooldown: float = 0.0
        self.damage_cooldown_time: float = 1.0  # 1s de invencibilidade apos levar dano
        self.knockback_force: int = settings.PLAYER_KNOCKBACK_FORCE

        # --- combate: disparo automatico e alcance ---
        self.shoot_cooldown: float = 0.0
        self.shoot_interval: float = settings.PLAYER_SHOOT_INTERVAL
        self.range_radius: float = settings.PLAYER_RANGE_RADIUS
        self.shoot_damage: int = settings.PLAYER_SHOOT_DAMAGE  # pode aumentar com upgrades

        # --- combate: sifao de energia, cadencia propria (independente do tiro principal) ---
        self.siphon_cooldown: float = 0.0
        self.siphon_interval: float = settings.SIPHON_INTERVAL

        # --- combate: phaser leve, municao limitada + recarga ---
        self.phaser_ammo: int = 0
        self.phaser_fire_cooldown: float = 0.0
        self.phaser_reload_timer: float = 0.0

        # --- combate: canhao de plasma, municao limitada + recarga (mesmo padrao do phaser) ---
        self.plasma_ammo: int = 0
        self.plasma_fire_cooldown: float = 0.0
        self.plasma_reload_timer: float = 0.0

        # --- combate: metralhadora de pulso, municao + recarga + cadencia propria upavel ---
        self.pulso_ammo: int = 0
        self.pulso_fire_cooldown: float = 0.0
        self.pulso_reload_timer: float = 0.0

        # --- combate: rajada de tiro, dispara N vezes em sequencia sem re-mirar ---
        self.pending_burst_shots: list = []
        self.burst_timer: float = 0.0

        # --- campo de forca: cronometro do proximo tique de dano em area ---
        self.force_field_timer: float = 0.0

        # --- escudo deflector: barreira atual (HP), tempo desde o ultimo dano, cooldown de bloqueio ---
        self.shield_hp: float = 0.0
        self.shield_regen_timer: float = 0.0
        self.block_cooldown: float = 0.0

        # --- progressao: pontos de drop e upgrades automaticos ---
        self.level: int = 0  # quantidade de upgrades ja conquistados
        self.drop_points: float = 0.0
        self.points_to_upgrade: float = settings.POINTS_PER_UPGRADE

        # --- escolha de upgrade: sinaliza pra GameScene que precisa pausar e sortear opcoes ---
        self.level_up_pending: bool = False

        # --- power-ups (ativos e passivos): nivel atual de cada eixo (0 = nao adquirido) ---
        self.power_up_levels: dict = {
            key: 0 for key in settings.POWER_UPS}

        # --- regeneracao de vida: acumula fracao de HP entre frames, aplica quando >= 1 ---
        self._regen_accumulator: float = 0.0

        # --- estatisticas: mortos e pontos gerados, por tipo de inimigo ---
        self.kills_by_type: dict = {}
        self.points_by_type: dict = {}

    # ==================================================================
    # VIDA, MORTE E CONTINUAR
    # ==================================================================

    def take_damage(self, amount: int) -> tuple[int, bool]:
        """Aplica dano recebido, passando pelas camadas do Escudo Deflector
        na ordem: bloqueio total (se disponivel) -> reducao percentual ->
        absorcao pela barreira (com transbordo) -> HP do player. Retorna
        (dano_real_no_hp, foi_bloqueado) para a GameScene decidir o
        feedback visual correto."""

        if self.is_dead or self.damage_cooldown > 0:
            return 0, False  # ainda invencivel, ignora o dano

        self.shield_regen_timer = 0.0  # qualquer dano reinicia o delay de regeneracao

        # camada 3: bloqueio total periodico (mais forte, checada primeiro)
        if self.power_up_levels["escudo_bloqueio"] > 0 and self.block_cooldown <= 0:
            self.block_cooldown = settings.SHIELD_BLOCK_COOLDOWN
            self.damage_cooldown = self.damage_cooldown_time
            return 0, True

        # camada 1: reducao percentual
        if self.power_up_levels["escudo_reducao"] > 0:
            reduction = self.get_power_up_value("escudo_reducao") / 100
            amount = amount * (1 - reduction)

        # camada 2: barreira com transbordo (absorve o que der, o resto vai pro HP)
        if self.shield_hp > 0:
            absorbed = min(self.shield_hp, amount)
            self.shield_hp -= absorbed
            amount -= absorbed

        damage_taken = round(amount)
        self.hp -= damage_taken
        self.damage_cooldown = self.damage_cooldown_time

        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True

        return damage_taken, False

    def revive(self) -> None:

        # usado ao continuar apos morrer: restaura HP e volta ao estado normal
        self.hp = self.max_hp
        self.is_dead = False

    def has_lives_left(self) -> bool:

        return self.lives > 0

    def consume_life(self) -> None:

        self.lives -= 1

    def apply_knockback(self, from_x: float, from_y: float) -> None:

        direction = pygame.Vector2(self.x - from_x, self.y - from_y)

        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()

        # guarda a posicao antes do empurrao, para poder reverter por eixo se colidir com obstaculo
        previous_x, previous_y = self.x, self.y

        self.x += direction.x * self.knockback_force / 10
        self.y += direction.y * self.knockback_force / 10

        if self.room:  # respeita os limites da sala, mesmo apos empurrao
            left, top, right, bottom = self.room.get_bounds()
            self.x = max(left, min(self.x, right - self.width))
            self.y = max(top, min(self.y, bottom - self.height))

        self.rect.x = self.x
        self.rect.y = self.y

        # bloqueia o empurrao por obstaculo fixo, revertendo eixo por eixo
        if self.room:
            for obstacle in self.room.get_obstacles():
                if self.rect.colliderect(obstacle.rect):
                    self.x = previous_x
                    self.rect.x = self.x

                    if self.rect.colliderect(obstacle.rect):
                        self.y = previous_y
                        self.rect.y = self.y

    # ==================================================================
    # COMBATE: DISPARO AUTOMATICO
    # ==================================================================

    def ready_to_shoot(self) -> bool:

        return self.shoot_cooldown <= 0

    def confirm_shot(self) -> None:

        self.shoot_cooldown = self.shoot_interval

    def ready_to_siphon(self) -> bool:

        return self.siphon_cooldown <= 0

    def confirm_siphon(self) -> None:

        self.siphon_cooldown = self.siphon_interval

    def ready_to_fire_phaser(self) -> bool:

        return (self.phaser_ammo > 0 and self.phaser_fire_cooldown <= 0
                and self.phaser_reload_timer <= 0)

    def confirm_phaser_shot(self) -> None:

        self.phaser_ammo -= 1
        self.phaser_fire_cooldown = settings.PHASER_FIRE_RATE

        if self.phaser_ammo <= 0:
            self.phaser_reload_timer = self.get_power_up_value("phaser_reload")

    def ready_to_fire_plasma(self) -> bool:

        return (self.plasma_ammo > 0 and self.plasma_fire_cooldown <= 0
                and self.plasma_reload_timer <= 0)

    def confirm_plasma_shot(self) -> None:

        self.plasma_ammo -= 1
        self.plasma_fire_cooldown = settings.PLASMA_FIRE_RATE

        if self.plasma_ammo <= 0:
            self.plasma_reload_timer = self.get_power_up_value("plasma_reload")

    def ready_to_fire_pulso(self) -> bool:

        return (self.pulso_ammo > 0 and self.pulso_fire_cooldown <= 0
                and self.pulso_reload_timer <= 0)

    def confirm_pulso_shot(self) -> None:

        self.pulso_ammo -= 1
        # diferente do Phaser/Plasma, a cadencia aqui e o proprio eixo upavel da arma
        self.pulso_fire_cooldown = self.get_power_up_value("pulso_cadencia")

        if self.pulso_ammo <= 0:
            self.pulso_reload_timer = self.get_power_up_value("pulso_reload")

    def queue_burst(self, shots: list, repeats: int) -> None:

        # guarda 'repeats' copias da mesma lista de disparos, para reproduzir
        # sem re-mirar a cada tiro da rajada
        self.pending_burst_shots = [shots] * repeats
        self.burst_timer = settings.BURST_SHOT_DELAY

    def has_pending_burst(self) -> bool:

        return len(self.pending_burst_shots) > 0

    def pop_burst_shots(self) -> list:

        return self.pending_burst_shots.pop(0)

    # ==================================================================
    # PROGRESSAO (DROPS E UPGRADES)
    # ==================================================================

    def add_drop_point(self, amount: float = 1) -> None:

        self.drop_points += amount

        if self.drop_points >= self.points_to_upgrade:
            self.drop_points -= self.points_to_upgrade
            self.level += 1

            # cada novo level exige mais pontos, na mesma proporcao de crescimento das ondas
            self.points_to_upgrade *= settings.UPGRADE_THRESHOLD_GROWTH

            # nao aplica mais automaticamente - sinaliza para a GameScene pausar e sortear 3 opcoes
            self.level_up_pending = True

    def register_kill(self, enemy_type: str, points: float) -> None:

        self.kills_by_type[enemy_type] = self.kills_by_type.get(
            enemy_type, 0) + 1
        self.points_by_type[enemy_type] = self.points_by_type.get(
            enemy_type, 0.0) + points

    def get_category(self, key: str) -> str:

        # eixos de uma mesma arma (ex: sabre_quantidade, sabre_dano) compartilham categoria;
        # chaves sem grupo configurado sao sua propria categoria (ex: "magnet")
        return settings.CATEGORY_GROUPS.get(key, key)

    def get_equipped_categories(self) -> set:

        # uma categoria conta como "equipada" se qualquer um dos seus eixos ja tiver nivel > 0
        return {
            self.get_category(key)
            for key, level in self.power_up_levels.items()
            if level > 0
        }

    def get_category_max_level(self, category: str) -> int:

        # para armas com multiplos eixos (ex: sabre), usa o maior nivel entre eles
        # como indicador rapido de "quao fundo o jogador ja investiu" naquela categoria
        levels = [
            level for key, level in self.power_up_levels.items()
            if self.get_category(key) == category
        ]

        return max(levels) if levels else 0

    def get_max_powerup_slots(self) -> int:

        # POWERUP_SLOTS_BY_LEVEL e uma lista ordenada (nivel_minimo, slots) - pega o ultimo que se aplica
        slots = settings.POWERUP_SLOTS_BY_LEVEL[0][1]

        for min_level, value in settings.POWERUP_SLOTS_BY_LEVEL:
            if self.level >= min_level:
                slots = value

        return slots

    def get_available_upgrades(self) -> list[str]:

        # "damage" nao ocupa slot - e a arma inicial, sempre disponivel
        available = ["damage"]

        equipped_categories = self.get_equipped_categories()
        max_slots = self.get_max_powerup_slots()

        # categorias livres (ex: tiro_multiplo) nao contam para o teto de slots
        countable_equipped = equipped_categories - settings.FREE_CATEGORIES
        slots_full = len(countable_equipped) >= max_slots

        for key in settings.POWER_UPS:

            if self.power_up_levels[key] >= settings.POWER_UPS[key]["max_level"]:
                continue  # eixo no teto, nunca mais aparece

            prereq = settings.UPGRADE_PREREQUISITES.get(key)

            if prereq is not None:
                prereq_key, min_level = prereq

                if self.power_up_levels[prereq_key] < min_level:
                    continue  # pre-requisito ainda nao atingido, eixo fica escondido

            category = self.get_category(key)

            # grupos de exclusividade: se um ramo irmao ja foi escolhido, este some para sempre
            if category in settings.EXCLUSIVE_CATEGORIES and self.power_up_levels[key] == 0:
                sibling_chosen = any(
                    self.power_up_levels[sibling] > 0
                    for sibling, sibling_category in settings.CATEGORY_GROUPS.items()
                    if sibling_category == category and sibling != key
                )

                if sibling_chosen:
                    continue

            if category in equipped_categories:
                # arma ja equipada, eixo livre pra evoluir
                available.append(key)
            elif category in settings.FREE_CATEGORIES or not slots_full:
                # arma nova: categorias livres sempre aparecem; as demais, so se ha slot
                available.append(key)

        return available

    def choose_random_upgrades(self, count: int = 3) -> list[str]:

        # sorteia ate 'count' opcoes distintas, sem repetir, dentre as disponiveis
        available = self.get_available_upgrades()

        return random.sample(available, min(count, len(available)))

    def apply_upgrade(self, key: str) -> None:

        # unico ponto que sabe como cada chave de upgrade e aplicada de fato
        if key == "damage":
            self.shoot_damage += settings.UPGRADE_DAMAGE_INCREMENT
        else:
            self.increase_power_up_level(key)

            if key == "phaser_capacidade":
                # arma nova ou carregador maior: enche o pente por completo
                self.phaser_ammo = int(
                    self.get_power_up_value("phaser_capacidade"))
                self.phaser_reload_timer = 0.0

            elif key == "plasma_capacidade":
                self.plasma_ammo = int(
                    self.get_power_up_value("plasma_capacidade"))
                self.plasma_reload_timer = 0.0

            elif key == "pulso_capacidade":
                self.pulso_ammo = int(
                    self.get_power_up_value("pulso_capacidade"))
                self.pulso_reload_timer = 0.0

    def increase_power_up_level(self, key: str) -> None:

        # aumenta o nivel de um eixo de power-up, respeitando o teto configurado
        config = settings.POWER_UPS[key]

        if self.power_up_levels[key] < config["max_level"]:
            self.power_up_levels[key] += 1

    def get_power_up_value(self, key: str) -> float:

        # calcula o valor atual de um eixo de power-up a partir do nivel
        config = settings.POWER_UPS[key]

        return config["base_value"] + config["increment"] * self.power_up_levels[key]

    def get_shot_vectors(self, base_direction: pygame.Vector2) -> list[dict]:
        """Retorna a lista de disparos a serem criados neste ciclo de tiro,
        cada um como {"direction": Vector2, "offset": Vector2}. Sem
        nenhuma variante de Tiro Multiplo escolhida, retorna apenas o
        tiro reto original (offset zero), preservando o comportamento
        padrao do jogo antes desta feature."""

        for key in ("tiro_diagonal",  "tiro_paralelo"):
            if self.power_up_levels[key] > 0:
                active_variant = key
                break
        else:
            return [{"direction": base_direction, "offset": pygame.Vector2(0, 0)}]

        level = self.power_up_levels[active_variant]
        zero_offset = pygame.Vector2(0, 0)

        if active_variant == "tiro_diagonal":

            shots = [{"direction": base_direction, "offset": zero_offset}]
            pairs = int(self.get_power_up_value("tiro_diagonal"))

            for i in range(pairs):
                angle = 20 + i * 15  # graus - cada par adicional abre mais o leque
                shots.append({"direction": base_direction.rotate(
                    angle), "offset": zero_offset})
                shots.append(
                    {"direction": base_direction.rotate(-angle), "offset": zero_offset})

            return shots

        if active_variant == "tiro_paralelo":

            count = int(self.get_power_up_value("tiro_paralelo"))
            perpendicular = pygame.Vector2(-base_direction.y, base_direction.x)
            spacing = 14  # pixels entre cada tiro paralelo
            start = -(count - 1) / 2

            return [
                {"direction": base_direction,
                    "offset": perpendicular * spacing * (start + i)}
                for i in range(count)
            ]

        return [{"direction": base_direction, "offset": zero_offset}]

    def update_regen(self, dt: float) -> None:

        # nivel 0 = sem regeneracao, nao acumula nada
        if self.power_up_levels["regen"] == 0 or self.hp >= self.max_hp:
            return

        regen_per_second = self.get_power_up_value("regen")
        self._regen_accumulator += regen_per_second * dt

        if self._regen_accumulator >= 1.0:
            healed = int(self._regen_accumulator)
            self.hp = min(self.max_hp, self.hp + healed)
            self._regen_accumulator -= healed

    def update_shield(self, dt: float) -> None:

        if self.block_cooldown > 0:
            self.block_cooldown -= dt

        if self.power_up_levels["escudo_barreira"] == 0:
            return  # barreira nao adquirida, nada a regenerar

        self.shield_regen_timer += dt

        shield_max = self.get_power_up_value("escudo_barreira")

        if self.shield_regen_timer >= settings.SHIELD_REGEN_DELAY and self.shield_hp < shield_max:
            self.shield_hp = min(shield_max, self.shield_hp +
                                 settings.SHIELD_REGEN_RATE * dt)

    # ==================================================================
    # ATUALIZACAO POR FRAME
    # ==================================================================

    def update(self, dt: float) -> None:

        if self.is_dead:
            return  # jogador morto nao processa mais input nem movimento

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt  # cooldown corre independente do estado

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt  # cooldown de tiro corre sempre, independente do estado

        if self.siphon_cooldown > 0:
            self.siphon_cooldown -= dt  # cooldown do sifao corre independente, cadencia propria

        if self.phaser_fire_cooldown > 0:
            self.phaser_fire_cooldown -= dt  # cadencia entre tiros dentro do mesmo carregador

        if self.phaser_reload_timer > 0:
            self.phaser_reload_timer -= dt  # tempo de recarga apos esvaziar o carregador

            if self.phaser_reload_timer <= 0:
                self.phaser_ammo = int(
                    self.get_power_up_value("phaser_capacidade"))

        if self.plasma_fire_cooldown > 0:
            self.plasma_fire_cooldown -= dt

        if self.plasma_reload_timer > 0:
            self.plasma_reload_timer -= dt

            if self.plasma_reload_timer <= 0:
                self.plasma_ammo = int(
                    self.get_power_up_value("plasma_capacidade"))

        if self.pulso_fire_cooldown > 0:
            self.pulso_fire_cooldown -= dt

        if self.pulso_reload_timer > 0:
            self.pulso_reload_timer -= dt

            if self.pulso_reload_timer <= 0:
                self.pulso_ammo = int(
                    self.get_power_up_value("pulso_capacidade"))

        if self.burst_timer > 0:
            self.burst_timer -= dt  # intervalo entre tiros da mesma rajada

        if self.force_field_timer > 0:
            self.force_field_timer -= dt  # intervalo entre tiques do campo de forca

        # alcance recalculado todo frame, a partir do nivel atual do power-up "range"
        self.range_radius = self.get_power_up_value("range")

        self.update_regen(dt)
        self.update_shield(dt)

        if self.state == "walking":
            self.update_walking(dt)

        elif self.state == "entering_door":
            self.update_entering_door(dt)

    def update_walking(self, dt: float) -> None:

        keys = pygame.key.get_pressed()

        direction = pygame.Vector2()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        # guarda a posicao antes de mover, para poder reverter por eixo se colidir com obstaculo
        previous_x, previous_y = self.x, self.y

        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt

        if self.room:

            left, top, right, bottom = self.room.get_bounds()

            self.x = max(left, min(self.x, right - self.width),)
            self.y = max(top, min(self.y, bottom - self.height),)

            self.rect.x = self.x
            self.rect.y = self.y

            # bloqueia movimento por obstaculo fixo, revertendo eixo por eixo (permite "deslizar" na parede)
            for obstacle in self.room.get_obstacles():
                if self.rect.colliderect(obstacle.rect):
                    self.x = previous_x
                    self.rect.x = self.x

                    if self.rect.colliderect(obstacle.rect):
                        self.y = previous_y
                        self.rect.y = self.y

    def update_entering_door(self, dt: float) -> None:

        if self.target_position is None:
            return

        direction = self.target_position - pygame.Vector2(self.x, self.y)

        if direction.length() < 2:

            self.x = self.target_position.x
            self.y = self.target_position.y

            self.rect.x = self.x
            self.rect.y = self.y

            if self.path:
                self.target_position = self.path.pop(0)

                if not self.path:
                    self._begin_final_leg()

                return

            self.target_position = None
            self.alpha = 255
            self.door_leg_start = None

            self.room_change_requested = True

            self.state = "walking"

            return

        direction = direction.normalize()

        self.x += direction.x * self.speed * dt
        self.y += direction.y * self.speed * dt

        self.rect.x = self.x
        self.rect.y = self.y

        if self.door_leg_start is not None:
            self._update_fade()

    # ==================================================================
    # NAVEGACAO ENTRE SALAS (transicao por portas)
    # ==================================================================

    def consume_room_change(self) -> bool:

        if self.room_change_requested:

            self.room_change_requested = False
            return True
        return False

    def start_door_sequence(self, waypoints: list[pygame.Vector2], door_thickness: float) -> None:

        self.path = list(waypoints)
        self.door_thickness = door_thickness
        self.target_position = self.path.pop(0)

    def _begin_final_leg(self) -> None:

        self.door_leg_start = pygame.Vector2(self.x, self.y)

    def _update_fade(self) -> None:

        if self.door_thickness <= 0:
            self.alpha = 0
            return

        traveled = (pygame.Vector2(self.x, self.y) -
                    self.door_leg_start).length()

        progress = traveled / self.door_thickness
        progress = max(0.0, min(progress, 1.0))

        self.alpha = int(255 * (1 - progress))

    # ==================================================================
    # DESENHO
    # ==================================================================

    def draw(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:

        # posicao na tela = posicao no mundo menos o deslocamento da camera
        screen_pos = (self.rect.x - camera_x, self.rect.y - camera_y)

        self.draw_range_indicator(screen, camera_x, camera_y)

        if self.alpha >= 255:
            pygame.draw.rect(
                screen, (70, 150, 150), (*screen_pos, self.rect.width, self.rect.height),)
        else:
            surface = pygame.Surface(
                (self.rect.width, self.rect.height), pygame.SRCALPHA)

            pygame.draw.rect(
                surface, (70, 150, 150, self.alpha), surface.get_rect(),)

            screen.blit(surface, screen_pos)

        self.draw_hp_bar(screen, screen_pos)

    def draw_hp_bar(self, screen: pygame.Surface, screen_pos: tuple) -> None:

        bar_width = self.rect.width
        bar_height = 4
        bar_x = screen_pos[0]
        # um pouco acima do topo do player
        bar_y = screen_pos[1] - bar_height - 4

        hp_ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, (80, 30, 30),
                         (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (60, 180, 90),
                         (bar_x, bar_y, bar_width * hp_ratio, bar_height))

        # barreira do escudo deflector: barra azul fina, logo acima da barra de HP,
        # so desenhada se a barreira ja foi adquirida (nivel > 0)
        if self.power_up_levels["escudo_barreira"] > 0:
            shield_max = self.get_power_up_value("escudo_barreira")
            shield_ratio = self.shield_hp / shield_max if shield_max > 0 else 0

            shield_bar_y = bar_y - bar_height - 2

            pygame.draw.rect(screen, (30, 40, 70),
                             (bar_x, shield_bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (100, 160, 230),
                             (bar_x, shield_bar_y, bar_width * shield_ratio, bar_height))

    def draw_range_indicator(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:

        # circulo sempre visivel: percepcao de inimigos e alcance do tiro compartilham este raio
        center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)

        # desenhado numa surface separada com alpha, para ficar discreto (nao solido)
        diameter = int(self.range_radius * 2)
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        pygame.draw.circle(
            surface, (150, 200, 220, 18), (self.range_radius, self.range_radius), self.range_radius,)
        pygame.draw.circle(
            surface, (150, 200, 220, 45), (self.range_radius, self.range_radius), self.range_radius, width=2,)

        screen.blit(
            surface, (center[0] - self.range_radius, center[1] - self.range_radius))

        self.draw_force_field(screen, camera_x, camera_y)

    def draw_force_field(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:

        field_radius = self.get_power_up_value("campo_area")

        if field_radius <= 0:
            return  # campo nao adquirido ainda, nada a desenhar

        center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)

        diameter = int(field_radius * 2)
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        pygame.draw.circle(
            surface, (220, 90, 60, 35), (field_radius, field_radius), field_radius,)
        pygame.draw.circle(
            surface, (220, 90, 60, 90), (field_radius, field_radius), field_radius, width=2,)

        screen.blit(
            surface, (center[0] - field_radius, center[1] - field_radius))
