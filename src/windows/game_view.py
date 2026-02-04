import arcade
import math
from src.settings import settings
from src.animations.RunningAlien import RunningAlien
import random
import math

import json
import os
import time

class GameView(arcade.View):
    def __init__(self, window, player_position=None):
        super().__init__()
        self.window = window
        self.save_file = "saves/forest_save.json"
        self.last_save_time = 0
        self.save_interval = 20  # seconds
        self.dialogue_active = False
        self.dialogue_text = ""
        
        # Позиция игрока
        self.player_position = player_position or self.load_save() or {'x': settings.width // 2, 'y': settings.height // 2}
        
        # Сюжетные фазы (пример)
        self.story_phases = self.load_story_phases()
        
        # Добавляем флаг паузы
        self.paused = False
        
        # Создаем прямоугольник для затемнения экрана
        self.overlay = arcade.shape_list.ShapeElementList()
        self.overlay_rectangle = arcade.shape_list.create_rectangle_filled(
            center_x=0, center_y=0,
            width=settings.width * 30, height=settings.height * 30,
            color=(0, 0, 0, 150)
        )
        self.overlay.append(self.overlay_rectangle)
        
        # Создаем текст "Пауза"
        self.pause_text = arcade.Text(
            "ПАУЗА",
            x=0, y=0,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center", anchor_y="center"
        )
        
        # --- НОВАЯ НАСТРОЙКА СНЕГА ---
        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2  # Увеличена вероятность спавна снежинки за кадр
        self.snowflake_speed_min = 1.5  # Увеличена минимальная скорость падения
        self.snowflake_speed_max = 4.0  # Увеличена максимальная скорость падения
        self.snowflake_drift_min = -5.0  # Увеличен дрейф влево
        self.snowflake_drift_max = 0.7  # Увеличен дрейф вправо
        self.snowflake_wobble_speed = 0.03  # Увеличена скорость покачивания
        self.snowflake_wobble_amount = 2.0  # Увеличена амплитуда покачивания

        # Создаём текстуру более белой и мягкой снежинки 8x8 пикселей
        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)
        
        # Настройка фона
        bg_texture = arcade.load_texture('resources/background/forest_map.png')
        self.bg = arcade.Sprite()
        self.bg.texture = bg_texture
        self.bg.scale = 10.0
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)

        # Фильтры
        night_texture = arcade.load_texture('resources/background/night.png')
        self.night = arcade.Sprite()
        self.filter_list = arcade.SpriteList()
        self.night.texture = night_texture
        self.night.scale = 20.0
        self.night.center_x = 0
        self.night.center_y = 0
        self.filter_list.append(self.night)

        # Настройка камеры
        self.camera = arcade.camera.Camera2D()
        self.camera.use()
        self.camera.zoom = 0.75

        # Настройка пришельца
        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=3.0)
        self.alien.center_x = self.player_position['x']
        self.alien.center_y = self.player_position['y']
        self.alien_list.append(self.alien)
        
        # Инициализация стрелки над головой пришельца (создается, но пока не видна)
        self.arrow_list = arcade.SpriteList()
        self.arrow = arcade.Sprite('resources/UI/arrow/arrow_mini.png')
        self.arrow.scale = 5.0
        self.arrow.center_x = self.alien.center_x
        self.arrow.center_y = self.alien.center_y + 400  # Над головой пришельца
        self.arrow.alpha = 0  # Прозрачная стрелка
        self.arrow_list.append(self.arrow)
        
        # Флаг для отображения стрелки
        self.show_arrow = False

        # Настройка стен
        self.wall_list = arcade.SpriteList()
        center_x = settings.width // 2
        center_y = settings.height // 2
        wall_texture = arcade.load_texture('resources/background/nothing.png')
        wall_width = 64

        # Размеры карты
        map_width = 10000
        map_height = 10000

        # Координаты границ карты
        left_edge = center_x - map_width // 2
        right_edge = center_x + map_width // 2
        bottom_edge = center_y - map_height // 2
        top_edge = center_y + map_height // 2

        # дороги
        road_angles = [0, 120, 240]
        road_width = 800
        road_length = 6000
        safe_zone_radius = 2000

        # по кругу
        outer_radius = 2000
        circumference = 2 * 3.14159 * outer_radius
        num_walls = int(circumference / wall_width)

        for i in range(num_walls):
            angle = 2 * 3.14159 * i / num_walls
            angle_deg = math.degrees(angle)
            in_road_area = False
            for road_angle in road_angles:
                # зона пропуска для дороги
                angle_diff = abs(angle_deg - road_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                # если угол стены близок к углу дороги, пропускаем ее
                if angle_diff < 10:  # зона пропуска
                    in_road_area = True
                    break

            if not in_road_area:
                wall = arcade.Sprite()
                wall.texture = wall_texture
                wall.center_x = center_x + outer_radius * math.cos(angle)
                wall.center_y = center_y + outer_radius * math.sin(angle)
                wall.angle = angle_deg + 90  # Поворачиваем стену по касательной
                self.wall_list.append(wall)

        # Добавляем стены вдоль дорог
        for road_angle in road_angles:
            road_angle_rad = math.radians(road_angle)
            dx = math.cos(road_angle_rad)
            dy = math.sin(road_angle_rad)

            # вектор для размещения стен по бокам дороги
            perp_dx = -dy
            perp_dy = dx

            # Размещаем стены вдоль дороги
            for distance in range(safe_zone_radius + 40, road_length, 64):
                for side_offset in [-road_width // 2, road_width // 2]:
                    wall = arcade.Sprite()
                    wall.texture = wall_texture
                    wall.center_x = center_x + dx * distance + perp_dx * side_offset
                    wall.center_y = center_y + dy * distance + perp_dy * side_offset
                    wall.angle = road_angle + 90  # Поворачиваем стену перпендикулярно дороге
                    self.wall_list.append(wall)

        # Обнесем всю карту по периметру стенами (дополнительная мера)
        # Нижняя сторона
        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = bottom_edge
            wall.angle = 0  # Горизонтальная ориентация
            self.wall_list.append(wall)

        # Верхняя сторона
        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = top_edge
            wall.angle = 0  # Горизонтальная ориентация
            self.wall_list.append(wall)

        # Левая сторона
        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = left_edge
            wall.center_y = y
            wall.angle = 90  # Вертикальная ориентация
            self.wall_list.append(wall)

        # Правая сторона
        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = right_edge
            wall.center_y = y
            wall.angle = 90  # Вертикальная ориентация
            self.wall_list.append(wall)

        # Настройки spaceship
        spaceship_texture = arcade.load_texture('resources/buildings/spaceship/spaceship.png')
        self.spaceship = arcade.Sprite(scale=10.0)
        self.buildings_list = arcade.SpriteList()
        self.spaceship.texture = spaceship_texture
        self.spaceship.center_x = 0
        self.spaceship.center_y = 0
        self.buildings_list.append(self.spaceship)

        # Настройка Ness
        self.ness = arcade.Sprite('resources/persons/alien_ness/ness_in_spacesuit_darked.png')
        # Ness
        ness_center_x = settings.width // 2 + 100
        ness_center_y = settings.height // 4

        self.ness.center_x = ness_center_x
        self.ness.center_y = ness_center_y
        self.alien_list.append(self.ness)

        # Настройка пришельца sor
        self.sor = arcade.Sprite('resources/persons/alien_sor/alien_sor_not_animated.png')
        self.sor.center_x = settings.width // 2 - 150
        self.sor.center_y = settings.height // 4 + 500
        self.alien_list.append(self.sor)

        # Добавляем коллизию для sor
        self.sor.width = 200
        self.sor.height = 200

        # Настройка факелов
        self.torch_list = arcade.SpriteList()
        torch_texture = arcade.load_texture('resources/buildings/torch.png')
        center_x = settings.width // 2
        center_y = settings.height // 2

        # Размещаем факелы вдоль внешнего круга барьеров (радиус 2000), но гораздо реже
        outer_radius = 1300
        torch_spacing = 700

        # Общая длина окружности
        circumference = 2 * 3.14159 * outer_radius
        # Количество факелов
        num_torches = int(circumference / torch_spacing)

        for i in range(num_torches):
            angle = 2 * 3.14159 * i / num_torches

            # Пропускаем места, где идут дороги
            in_road_area = False
            road_angles = [0, 120, 240]

            if not in_road_area:
                torch = arcade.Sprite(scale=3.0)
                torch.texture = torch_texture
                torch.center_x = center_x + outer_radius * math.cos(angle)
                torch.center_y = center_y + outer_radius * math.sin(angle)
                self.torch_list.append(torch)

        # Размещаем факелы вдоль дорог
        road_width = 800
        road_length = 4500
        safe_zone_radius = 2000

        for road_angle in road_angles:
            road_angle_rad = math.radians(road_angle)
            dx = math.cos(road_angle_rad)
            dy = math.sin(road_angle_rad)

            # Перпендикулярный вектор для размещения факелов по бокам дороги
            perp_dx = -dy
            perp_dy = dx

            # Размещаем факелы вдоль дороги с большим интервалом
            for distance in range(safe_zone_radius + 200, road_length, 800):
                for side_offset in [road_width // 2 - 400, road_width // 2 - 400]:
                    torch = arcade.Sprite(scale=3.0)
                    torch.texture = torch_texture
                    torch.center_x = center_x + dx * distance + perp_dx * side_offset
                    torch.center_y = center_y + dy * distance + perp_dy * side_offset
                    self.torch_list.append(torch)

        # Добавляем коллизию для spaceship
        self.spaceship.width = spaceship_texture.width * 10.0
        self.spaceship.height = spaceship_texture.height * 10.0

        # Добавляем коллизию для Ness
        self.ness.width = 120
        self.ness.height = 120

        # Настройка диалогового окна
        # Получаем размеры экрана из настроек
        screen_width = settings.width
        screen_height = settings.height

        # Диалоговое окно, плотно прилегающее к нижнему краю экрана
        self.dialogue_box = arcade.SpriteSolidColor(
            screen_width,
            120,
            color=(10, 9, 9, 180)
        )
        self.dialogue_box.center_x = screen_width // 2  # По центру по X
        self.dialogue_box.bottom = 0  # Прижато к нижнему краю
        self.dialogue_sprite_list = arcade.SpriteList()
        self.dialogue_sprite_list.append(self.dialogue_box)

        # Текст диалога
        self.dialogue_text_sprite = arcade.Text(
            "",
            self.dialogue_box.center_x + 80,
            self.dialogue_box.center_y,
            arcade.color.ASH_GREY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=screen_width - 200
        )

        self.dialogue_speaker = arcade.Sprite('resources/persons/alien_ness/ness_in_spacesuit.png')
        self.dialogue_speaker.scale = 3
        self.dialogue_speaker.left = 20
        self.dialogue_speaker.bottom = 20
        self.dialogue_sprite_list.append(self.dialogue_speaker)

        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Инициализация музыки
        try:
            self.music = arcade.Sound("sound/music/OutOfSpace.wav")
            self.music_player = self.music.play(loop=True)
        except Exception as e:
            print(f"Failed to load music: {e}")

    def __init__(self, window, player_position=None):
        super().__init__()
        self.window = window
        self.save_file = "saves/forest_save.json"
        self.last_save_time = 0
        self.save_interval = 20  # seconds
        self.dialogue_active = False
        self.dialogue_text = ""
        
        # Позиция игрока
        self.player_position = player_position or self.load_save() or {'x': settings.width // 2, 'y': settings.height // 2}
        
        # Сюжетные фазы (пример)
        self.story_phases = self.load_story_phases()
        
        # Добавляем флаг паузы
        self.paused = False
        
        # Создаем прямоугольник для затемнения экрана
        self.overlay = arcade.shape_list.ShapeElementList()
        self.overlay_rectangle = arcade.shape_list.create_rectangle_filled(
            center_x=0, center_y=0,
            width=settings.width * 30, height=settings.height * 30,
            color=(0, 0, 0, 150)
        )
        self.overlay.append(self.overlay_rectangle)
        
        # Создаем текст "Пауза"
        self.pause_text = arcade.Text(
            "ПАУЗА",
            x=0, y=0,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center", anchor_y="center"
        )
        
        # --- НОВАЯ НАСТРОЙКА СНЕГА ---
        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2  # Увеличена вероятность спавна снежинки за кадр
        self.snowflake_speed_min = 1.5  # Увеличена минимальная скорость падения
        self.snowflake_speed_max = 4.0  # Увеличена максимальная скорость падения
        self.snowflake_drift_min = -5.0  # Увеличен дрейф влево
        self.snowflake_drift_max = 0.7  # Увеличен дрейф вправо
        self.snowflake_wobble_speed = 0.03  # Увеличена скорость покачивания
        self.snowflake_wobble_amount = 2.0  # Увеличена амплитуда покачивания

        # Создаём текстуру более белой и мягкой снежинки 8x8 пикселей
        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)
        
        # Настройка фона
        bg_texture = arcade.load_texture('resources/background/forest_map.png')
        self.bg = arcade.Sprite()
        self.bg.texture = bg_texture
        self.bg.scale = 10.0
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)

        # Фильтры
        night_texture = arcade.load_texture('resources/background/night.png')
        self.night = arcade.Sprite()
        self.filter_list = arcade.SpriteList()
        self.night.texture = night_texture
        self.night.scale = 20.0
        self.night.center_x = 0
        self.night.center_y = 0
        self.filter_list.append(self.night)

        # Настройка камеры
        self.camera = arcade.camera.Camera2D()
        self.camera.use()
        self.camera.zoom = 0.75

        # Настройка пришельца
        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=3.0)
        self.alien.center_x = self.player_position['x']
        self.alien.center_y = self.player_position['y']
        self.alien_list.append(self.alien)
        
        # Инициализация стрелки над головой пришельца (создается, но пока не видна)
        self.arrow_list = arcade.SpriteList()
        self.arrow = arcade.Sprite('resources/UI/arrow/arrow_mini.png')
        self.arrow.scale = 5.0
        self.arrow.center_x = self.alien.center_x
        self.arrow.center_y = self.alien.center_y + 400  # Над головой пришельца
        self.arrow.alpha = 0  # Прозрачная стрелка
        self.arrow_list.append(self.arrow)
        
        # Флаг для отображения стрелки
        self.show_arrow = False

        # Настройка стен
        self.wall_list = arcade.SpriteList()
        center_x = settings.width // 2
        center_y = settings.height // 2
        wall_texture = arcade.load_texture('resources/background/nothing.png')
        wall_width = 64

        # Размеры карты
        map_width = 10000
        map_height = 10000

        # Координаты границ карты
        left_edge = center_x - map_width // 2
        right_edge = center_x + map_width // 2
        bottom_edge = center_y - map_height // 2
        top_edge = center_y + map_height // 2

        # дороги
        road_angles = [0, 120, 240]
        road_width = 800
        road_length = 6000
        safe_zone_radius = 2000

        # по кругу
        outer_radius = 2000
        circumference = 2 * 3.14159 * outer_radius
        num_walls = int(circumference / wall_width)

        for i in range(num_walls):
            angle = 2 * 3.14159 * i / num_walls
            angle_deg = math.degrees(angle)
            in_road_area = False
            for road_angle in road_angles:
                # зона пропуска для дороги
                angle_diff = abs(angle_deg - road_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                # если угол стены близок к углу дороги, пропускаем ее
                if angle_diff < 10:  # зона пропуска
                    in_road_area = True
                    break

            if not in_road_area:
                wall = arcade.Sprite()
                wall.texture = wall_texture
                wall.center_x = center_x + outer_radius * math.cos(angle)
                wall.center_y = center_y + outer_radius * math.sin(angle)
                wall.angle = angle_deg + 90  # Поворачиваем стену по касательной
                self.wall_list.append(wall)

        # Добавляем стены вдоль дорог
        for road_angle in road_angles:
            road_angle_rad = math.radians(road_angle)
            dx = math.cos(road_angle_rad)
            dy = math.sin(road_angle_rad)

            # вектор для размещения стен по бокам дороги
            perp_dx = -dy
            perp_dy = dx

            # Размещаем стены вдоль дороги
            for distance in range(safe_zone_radius + 40, road_length, 64):
                for side_offset in [-road_width // 2, road_width // 2]:
                    wall = arcade.Sprite()
                    wall.texture = wall_texture
                    wall.center_x = center_x + dx * distance + perp_dx * side_offset
                    wall.center_y = center_y + dy * distance + perp_dy * side_offset
                    wall.angle = road_angle + 90  # Поворачиваем стену перпендикулярно дороге
                    self.wall_list.append(wall)

        # Обнесем всю карту по периметру стенами (дополнительная мера)
        # Нижняя сторона
        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = bottom_edge
            wall.angle = 0  # Горизонтальная ориентация
            self.wall_list.append(wall)

        # Верхняя сторона
        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = top_edge
            wall.angle = 0  # Горизонтальная ориентация
            self.wall_list.append(wall)

        # Левая сторона
        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = left_edge
            wall.center_y = y
            wall.angle = 90  # Вертикальная ориентация
            self.wall_list.append(wall)

        # Правая сторона
        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = right_edge
            wall.center_y = y
            wall.angle = 90  # Вертикальная ориентация
            self.wall_list.append(wall)

        # Настройки spaceship
        spaceship_texture = arcade.load_texture('resources/buildings/spaceship/spaceship.png')
        self.spaceship = arcade.Sprite(scale=10.0)
        self.buildings_list = arcade.SpriteList()
        self.spaceship.texture = spaceship_texture
        self.spaceship.center_x = 0
        self.spaceship.center_y = 0
        self.buildings_list.append(self.spaceship)

        # Настройка Ness
        self.ness = arcade.Sprite('resources/persons/alien_ness/ness_in_spacesuit_darked.png')
        # Ness
        ness_center_x = settings.width // 2 + 100
        ness_center_y = settings.height // 4

        self.ness.center_x = ness_center_x
        self.ness.center_y = ness_center_y
        self.alien_list.append(self.ness)

        # Настройка пришельца sor
        self.sor = arcade.Sprite('resources/persons/alien_sor/alien_sor_not_animated.png')
        self.sor.center_x = settings.width // 2 - 150
        self.sor.center_y = settings.height // 4 + 500
        self.alien_list.append(self.sor)

        # Добавляем коллизию для sor
        self.sor.width = 200
        self.sor.height = 200

        # Настройка факелов
        self.torch_list = arcade.SpriteList()
        torch_texture = arcade.load_texture('resources/buildings/torch.png')
        center_x = settings.width // 2
        center_y = settings.height // 2

        # Размещаем факелы вдоль внешнего круга барьеров (радиус 2000), но гораздо реже
        outer_radius = 1300
        torch_spacing = 700

        # Общая длина окружности
        circumference = 2 * 3.14159 * outer_radius
        # Количество факелов
        num_torches = int(circumference / torch_spacing)

        for i in range(num_torches):
            angle = 2 * 3.14159 * i / num_torches

            # Пропускаем места, где идут дороги
            in_road_area = False
            road_angles = [0, 120, 240]

            if not in_road_area:
                torch = arcade.Sprite(scale=3.0)
                torch.texture = torch_texture
                torch.center_x = center_x + outer_radius * math.cos(angle)
                torch.center_y = center_y + outer_radius * math.sin(angle)
                self.torch_list.append(torch)

        # Размещаем факелы вдоль дорог
        road_width = 800
        road_length = 4500
        safe_zone_radius = 2000

        for road_angle in road_angles:
            road_angle_rad = math.radians(road_angle)
            dx = math.cos(road_angle_rad)
            dy = math.sin(road_angle_rad)

            # Перпендикулярный вектор для размещения факелов по бокам дороги
            perp_dx = -dy
            perp_dy = dx

            # Размещаем факелы вдоль дороги с большим интервалом
            for distance in range(safe_zone_radius + 200, road_length, 800):
                for side_offset in [road_width // 2 - 400, road_width // 2 - 400]:
                    torch = arcade.Sprite(scale=3.0)
                    torch.texture = torch_texture
                    torch.center_x = center_x + dx * distance + perp_dx * side_offset
                    torch.center_y = center_y + dy * distance + perp_dy * side_offset
                    self.torch_list.append(torch)

        # Добавляем коллизию для spaceship
        self.spaceship.width = spaceship_texture.width * 10.0
        self.spaceship.height = spaceship_texture.height * 10.0

        # Добавляем коллизию для Ness
        self.ness.width = 120
        self.ness.height = 120

        # Настройка диалогового окна
        # Получаем размеры экрана из настроек
        screen_width = settings.width
        screen_height = settings.height

        # Диалоговое окно, плотно прилегающее к нижнему краю экрана
        self.dialogue_box = arcade.SpriteSolidColor(
            screen_width,
            120,
            color=(10, 9, 9, 180)
        )
        self.dialogue_box.center_x = screen_width // 2  # По центру по X
        self.dialogue_box.bottom = 0  # Прижато к нижнему краю
        self.dialogue_sprite_list = arcade.SpriteList()
        self.dialogue_sprite_list.append(self.dialogue_box)

        # Текст диалога
        self.dialogue_text_sprite = arcade.Text(
            "",
            self.dialogue_box.center_x + 80,
            self.dialogue_box.center_y,
            arcade.color.ASH_GREY,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=screen_width - 200
        )

        self.dialogue_speaker = arcade.Sprite('resources/persons/alien_ness/ness_in_spacesuit.png')
        self.dialogue_speaker.scale = 3
        self.dialogue_speaker.left = 20
        self.dialogue_speaker.bottom = 20
        self.dialogue_sprite_list.append(self.dialogue_speaker)

        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()

        # Отрисовка игрового мира
        self.camera.use()
        self.bg_list.draw(pixelated=True)
        self.wall_list.draw()

        self.filter_list.draw()
        self.torch_list.draw(pixelated=True)
        self.buildings_list.draw(pixelated=True)
        self.alien_list.draw(pixelated=True)
        
        # Отрисовка стрелки над головой пришельца
        self.arrow_list.draw(pixelated=True)
        
        # Отрисовка снежинок
        self.snowflake_list.draw()

        # Отрисовка диалогового окна
        if hasattr(self, 'dialogue_active') and self.dialogue_active:
            self.dialogue_sprite_list.draw(pixelated=True)
            self.dialogue_text_sprite.draw()

        # Отрисовка текста с координатами
        if hasattr(self, 'coordinates_text'):
            self.coordinates_text.draw()
            
        # Отрисовка экрана паузы
        if self.paused:
            # Устанавливаем оверлей по центру камеры
            self.overlay_rectangle.center_x = self.camera.position.x
            self.overlay_rectangle.center_y = self.camera.position.y
            self.overlay.draw()
            
            # Позиционируем текст "Пауза" по центру экрана
            self.pause_text.x = self.camera.position.x
            self.pause_text.y = self.camera.position.y + 100
            self.pause_text.draw()

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        if self.paused:
            return
            
        # Обновление снежинок
        self.update_snowflakes()
        
        # Автоматическое сохранение
        self.auto_save(delta_time)

        # скорость по оси X
        self.alien.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -settings.PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = settings.PLAYER_SPEED

        # скорость по оси Y
        self.alien.change_y = 0
        if self.up_pressed and not self.down_pressed:
            self.alien.change_y = settings.PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.alien.change_y = -settings.PLAYER_SPEED

        # Обновление позиций
        self.alien_list.update()
        self.alien.update_animation(delta_time)
        
        # Проверка перехода в городскую локацию
        if self.alien.center_x > 5230 and 110 <= self.alien.center_y <= 420:
            self.window.switch_view("city")

        # Проверка расстояния до Ness для диалога
        distance_to_ness = arcade.get_distance_between_sprites(self.alien, self.ness)
        if not hasattr(self, 'dialogue_active'):
            self.dialogue_active = False
            self.dialogue_text = ""

        if distance_to_ness < 150 and not self.dialogue_active:
            self.dialogue_active = True
            self.dialogue_text = "Вроде приземлились... Мы немножко обустроили тут территорию, осталось подобрать маскировку."
            self.dialogue_text_sprite.value = self.dialogue_text
        elif distance_to_ness >= 150 and self.dialogue_active:
            self.dialogue_active = False
            self.dialogue_text = ""
            self.dialogue_text_sprite.value = self.dialogue_text
            self.show_arrow = True
            self.arrow.alpha = 255

        if arcade.check_for_collision_with_list(self.alien, self.wall_list):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Проверка коллизии с spaceship
        if arcade.check_for_collision_with_list(self.alien, self.buildings_list):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Проверка коллизии с Ness
        if arcade.check_for_collision(self.alien, self.ness):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        if arcade.check_for_collision(self.alien, self.sor):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y
        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2
        self.camera.position = camera_x, camera_y

        if not hasattr(self, 'coordinates_text'):
            self.coordinates_text = arcade.Text(
                "",
                x=0,
                y=0,
                color=arcade.color.WHITE,
                font_size=24,
                anchor_x="right",
                anchor_y="top"
            )

        if hasattr(self, 'dialogue_box'):
            if hasattr(self, 'coordinates_text'):
                self.coordinates_text.text = f"X: {int(self.alien.center_x)}, Y: {int(self.alien.center_y)}"
                self.coordinates_text.x = camera_x + settings.width // 2 - 20
                self.coordinates_text.y = camera_y + settings.height // 2 - 20

        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.center_x = camera_x
            self.dialogue_box.bottom = camera_y - (settings.height // 2)

            self.dialogue_text_sprite.position = (self.dialogue_box.center_x + 80, self.dialogue_box.center_y)

            self.dialogue_speaker.left = self.dialogue_box.left + 20
            self.dialogue_speaker.bottom = self.dialogue_box.bottom + 20
            
        # обновляем позицию стрелки над головой пришельца
        if self.show_arrow:
            self.arrow.center_x = self.alien.center_x
            self.arrow.center_y = self.alien.center_y + 70

        target_x = 5580
        target_y = 385
        
        # угол между текущей позицией пришельца и целью
        dx = target_x - self.alien.center_x
        dy = target_y - self.alien.center_y
        angle = math.degrees(math.atan2(dy, dx))

        self.arrow.angle = -angle + 90

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.ESCAPE:
            # Переключаем состояние паузы
            self.paused = not self.paused
            
            # При активации паузы обновляем позицию оверлея и текста
            if self.paused:
                self.overlay_rectangle.center_x = self.camera.position.x
                self.overlay_rectangle.center_y = self.camera.position.y
                self.pause_text.x = self.camera.position.x
                self.pause_text.y = self.camera.position.y + 100
        elif key == arcade.key.P:
            self.delete_save()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

    def save_game(self):
        save_data = {
            'player_position': {
                'x': self.alien.center_x,
                'y': self.alien.center_y
            },
            'story_phases': self.story_phases,
            'timestamp': time.time()
        }
        os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"Сохранение создано: X={self.alien.center_x}, Y={self.alien.center_y}")

    def load_save(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    return save_data.get('player_position')
        except Exception as e:
            print(f"Failed to load save: {e}")
        return None
        
    def load_story_phases(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    return save_data.get('story_phases', {})
        except Exception as e:
            print(f"Failed to load story phases: {e}")
        return {}

    def auto_save(self, delta_time):
        self.last_save_time += delta_time
        if self.last_save_time >= self.save_interval:
            self.save_game()
            self.last_save_time = 0

    def delete_save(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
            print("Forest save file deleted")
            # Reset story phases
            self.story_phases = {}
            # Reset player position to default
            self.alien.center_x = settings.width // 2
            self.alien.center_y = settings.height // 2
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

    def update_snowflakes(self):
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite()
            snowflake.texture = self.snowflake_texture

            size = random.uniform(0.5, 1.5)
            snowflake.scale = size

            snowflake.center_x = random.uniform(
                self.camera.position.x - self.window.width // 2 - 500,
                self.camera.position.x + self.window.width // 2 + 500
            )
            snowflake.center_y = self.camera.position.y + self.window.height // 2 + 500

            snowflake.speed = random.uniform(self.snowflake_speed_min, self.snowflake_speed_max)
            snowflake.drift = random.uniform(self.snowflake_drift_min, self.snowflake_drift_max)

            snowflake.base_x = snowflake.center_x
            snowflake.wobble_offset = 0.0

            self.snowflake_list.append(snowflake)

        for snowflake in self.snowflake_list:
            snowflake.center_y -= snowflake.speed
            snowflake.center_x += snowflake.drift
            snowflake.wobble_offset += self.snowflake_wobble_speed
            snowflake.center_x = snowflake.base_x + math.sin(snowflake.wobble_offset) * 0.8
            if snowflake.center_y < self.camera.position.y - self.window.height // 2 - 500:
                snowflake.remove_from_sprite_lists()
