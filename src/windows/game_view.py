import arcade
import math
from src.settings import settings
from src.animations.RunningAlien import RunningAlien

class GameView(arcade.View):
    """Представление игрового процесса"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        
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
        self.alien.center_x = settings.width // 2
        self.alien.center_y = settings.height // 2
        self.alien_list.append(self.alien)

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
                for side_offset in [-road_width//2, road_width//2]:
                    wall = arcade.Sprite()
                    wall.texture = wall_texture
                    wall.center_x = center_x + dx * distance + perp_dx * side_offset
                    wall.center_y = center_y + dy * distance + perp_dy * side_offset
                    wall.angle = road_angle + 90  # Поворачиваем стену перпендикулярно дороге
                    self.wall_list.append(wall)

        # Обнесем всю карту по периметру стенами (дополнительная мера)
        # Нижняя сторона
        for x in range(left_edge + wall_width//2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = bottom_edge
            wall.angle = 0  # Горизонтальная ориентация
            self.wall_list.append(wall)
        
        # Верхняя сторона
        for x in range(left_edge + wall_width//2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = top_edge
            wall.angle = 0  # Горизонтальная ориентация
            self.wall_list.append(wall)
            
        # Левая сторона
        for y in range(bottom_edge + wall_width//2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = left_edge
            wall.center_y = y
            wall.angle = 90  # Вертикальная ориентация
            self.wall_list.append(wall)
            
        # Правая сторона
        for y in range(bottom_edge + wall_width//2, top_edge, wall_width):
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
        self.ness = arcade.Sprite('resources/persons/alien_ness/ness_no_anim.png', scale=0.22)
        # Ness
        import random
        center_x = settings.width // 2 + 50
        center_y = settings.height // 4
        
        self.ness.center_x = center_x + random.randint(-200, 200)
        self.ness.center_y = center_y + random.randint(-200, 200)
        self.alien_list.append(self.ness)

        # Добавляем коллизию для spaceship
        self.spaceship.width = spaceship_texture.width * 10.0
        self.spaceship.height = spaceship_texture.height * 10.0
        
        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()
        
        self.camera.use()
        self.bg_list.draw(pixelated=True)
        self.wall_list.draw()
        self.alien_list.draw(pixelated=True)


        self.filter_list.draw()
        self.buildings_list.draw(pixelated=True)

    def on_update(self, delta_time):
        """Обновление игровой логики"""
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

        # Проверка коллизии со стенами
        if arcade.check_for_collision_with_list(self.alien, self.wall_list):
            # При столкновении возвращаем пришельца на предыдущую позицию
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Проверка коллизии с spaceship
        if arcade.check_for_collision_with_list(self.alien, self.buildings_list):
            # При столкновении возвращаем пришельца на предыдущую позицию
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Позиция камеры с небольшим смещением вверх
        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2  # Поднимаем камеру на половину высоты экрана
        self.camera.position = camera_x, camera_y

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")
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