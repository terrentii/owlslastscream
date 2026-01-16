import arcade
import math
from src.settings import settings
from src.animations.RunningAlien import RunningAlien


class GameView(arcade.View):
    """Представление игрового процесса"""

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.dialogue_active = False
        self.dialogue_text = ""

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
        road_length = 6000
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

        # Отрисовка диалогового окна
        if hasattr(self, 'dialogue_active') and self.dialogue_active:
            self.dialogue_sprite_list.draw(pixelated=True)
            self.dialogue_text_sprite.draw()

        # Отрисовка текста с координатами
        if hasattr(self, 'coordinates_text'):
            self.coordinates_text.draw()

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
            # После завершения диалога с Ness, показываем стрелку
            self.show_arrow = True
            self.arrow.alpha = 255  # Делаем стрелку видимой

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

        # Проверка коллизии с Ness
        if arcade.check_for_collision(self.alien, self.ness):
            # При столкновении возвращаем пришельца на предыдущую позицию
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Проверка коллизии с sor
        if arcade.check_for_collision(self.alien, self.sor):
            # При столкновении возвращаем пришельца на предыдущую позицию
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Коллизия с факелами удалена - они декоративные элементы
        # Факелы больше не создают препятствий для движения

        # Позиция камеры с небольшим смещением вверх
        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2  # Поднимаем камеру на половину высоты экрана
        self.camera.position = camera_x, camera_y

        # Настройка текста с координатами
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

        # Обновляем позицию диалогового окна относительно камеры
        if hasattr(self, 'dialogue_box'):
            # Обновляем текст координат
            if hasattr(self, 'coordinates_text'):
                self.coordinates_text.text = f"X: {int(self.alien.center_x)}, Y: {int(self.alien.center_y)}"
                self.coordinates_text.x = camera_x + settings.width // 2 - 20  # Правый край экрана
                self.coordinates_text.y = camera_y + settings.height // 2 - 20  # Верхний край экрана

        # Обновляем позицию диалогового окна относительно камеры
        if hasattr(self, 'dialogue_box'):
            # Диалоговое окно прижато к нижнему краю экрана
            self.dialogue_box.center_x = camera_x  # Центрируем по X относительно камеры
            self.dialogue_box.bottom = camera_y - (settings.height // 2)  # Прижато к нижнему краю

            # Обновляем позицию текста
            self.dialogue_text_sprite.position = (self.dialogue_box.center_x + 80, self.dialogue_box.center_y)

            # Спрайт говорящего прижат к левому краю диалогового окна
            self.dialogue_speaker.left = self.dialogue_box.left + 20
            self.dialogue_speaker.bottom = self.dialogue_box.bottom + 20
            
        # Обновляем позицию стрелки над головой пришельца только если диалог с Ness завершен
        if self.show_arrow:
            self.arrow.center_x = self.alien.center_x
            self.arrow.center_y = self.alien.center_y + 70  # Над головой пришельца
        
        # Обновляем направление стрелки к точке (0, 0)
        target_x = 5580
        target_y = 385
        
        # Вычисляем угол между текущей позицией пришельца и целью
        dx = target_x - self.alien.center_x
        dy = target_y - self.alien.center_y
        angle = math.degrees(math.atan2(dy, dx))
        
        # Устанавливаем угол поворота стрелки
        # Инвертируем ось Y, так как в arcade Y увеличивается вверх, а в математике - вниз
        self.arrow.angle = -angle + 90

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        # if key == arcade.key.ESCAPE:
        #     self.window.switch_view("main_menu")
        if key == arcade.key.LEFT or key == arcade.key.A:
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
