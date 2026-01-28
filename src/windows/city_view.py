import arcade
import random
import math
from src.settings import settings
from src.animations.RunningAlien import RunningAlien


class CityView(arcade.View):
    def __init__(self, window, player_position=None):
        super().__init__()
        self.window = window

        self.player_position = player_position or {'x': -4000, 'y': -1000}

        self.paused = False

        self.overlay = arcade.shape_list.ShapeElementList()
        self.overlay_rectangle = arcade.shape_list.create_rectangle_filled(
            center_x=0, center_y=0,
            width=settings.width * 30, height=settings.height * 30,
            color=(0, 0, 0, 150)
        )
        self.overlay.append(self.overlay_rectangle)

        # Пауза
        self.pause_text = arcade.Text(
            "ПАУЗА",
            x=0, y=0,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center", anchor_y="center"
        )

        bg_texture = arcade.load_texture('resources/background/gorod.png')
        self.bg = arcade.Sprite()
        self.bg.texture = bg_texture
        self.bg.scale = 8.0
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)

        # Фильтры
        night_texture = arcade.load_texture('resources/background/night.png')
        self.filter_list = arcade.SpriteList()
        self.night = arcade.Sprite()
        self.night.texture = night_texture
        self.night.scale = 20.0
        self.night.center_x = 0
        self.night.center_y = 0
        self.filter_list.append(self.night)

        # камера
        self.camera = arcade.camera.Camera2D()
        self.camera.use()
        self.camera.zoom = 0.75

        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=3.0)
        self.alien.center_x = self.player_position['x']
        self.alien.center_y = self.player_position['y']
        self.alien_list.append(self.alien)

        self.arrow_list = arcade.SpriteList()
        self.arrow = arcade.Sprite('resources/UI/arrow/arrow_mini.png')
        self.arrow.scale = 5.0
        self.arrow.center_x = self.alien.center_x
        self.arrow.center_y = self.alien.center_y + 400
        self.arrow.alpha = 0
        self.arrow_list.append(self.arrow)

        self.show_arrow = False

        # Настройка стен для городской локации
        self.wall_list = arcade.SpriteList()
        center_x = settings.width // 2
        center_y = settings.height // 2
        wall_texture = arcade.load_texture('resources/background/nothing.png')
        wall_width = 64

        # Размеры карты
        map_width = 10280
        map_height = 5800

        # Координаты границ карты
        left_edge = center_x - map_width // 2
        right_edge = center_x + map_width // 2
        bottom_edge = center_y - map_height // 2
        top_edge = center_y + map_height // 2

        # Создаем стены по периметру карты
        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = bottom_edge
            self.wall_list.append(wall)

        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = x
            wall.center_y = top_edge
            self.wall_list.append(wall)

        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = left_edge
            wall.center_y = y
            wall.angle = 90
            self.wall_list.append(wall)

        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite()
            wall.texture = wall_texture
            wall.center_x = right_edge
            wall.center_y = y
            wall.angle = 90
            self.wall_list.append(wall)

        # Настройка диалогового окна
        screen_width = settings.width
        screen_height = settings.height

        self.dialogue_box = arcade.SpriteSolidColor(
            screen_width,
            120,
            color=(10, 9, 9, 180)
        )
        self.dialogue_box.center_x = screen_width // 2
        self.dialogue_box.bottom = 0
        self.dialogue_sprite_list = arcade.SpriteList()
        self.dialogue_sprite_list.append(self.dialogue_box)

        self.dialogue_text_sprite = arcade.Text(
            "",
            self.dialogue_box.center_x + 80,
            self.dialogue_box.center_y,
            arcade.color.ASH_GREY,
            font_size=18,
            anchor_x="center", anchor_y="center",
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

        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2
        self.snowflake_speed_min = 1.5
        self.snowflake_speed_max = 4.0
        self.snowflake_drift_min = -5.0
        self.snowflake_drift_max = 0.7
        self.snowflake_wobble_speed = 0.03
        self.snowflake_wobble_amount = 0.8

        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)

    def update_snowflakes(self):
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite()
            snowflake.texture = self.snowflake_texture

            size = random.uniform(0.5, 1.5)
            snowflake.scale = size

            snowflake.center_x = random.uniform(
                self.camera.position.x - self.window.width // 2,
                self.camera.position.x + self.window.width // 2
            )
            snowflake.center_y = self.camera.position.y + self.window.height // 2 + 150

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

            if snowflake.center_y < self.camera.position.y - self.window.height // 2:
                snowflake.remove_from_sprite_lists()

    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()

        self.camera.use()
        self.bg_list.draw(pixelated=True)
        self.wall_list.draw()

        # Фильтры
        self.filter_list.draw()
        self.alien_list.draw(pixelated=True)
        self.arrow_list.draw(pixelated=True)

        self.snowflake_list.draw()

        if hasattr(self, 'dialogue_active') and self.dialogue_active:
            self.dialogue_sprite_list.draw(pixelated=True)
            self.dialogue_text_sprite.draw()

        if hasattr(self, 'coordinates_text'):
            self.coordinates_text.draw()

        if self.paused:
            self.overlay_rectangle.center_x = self.camera.position.x
            self.overlay_rectangle.center_y = self.camera.position.y
            self.overlay.draw()
            self.pause_text.x = self.camera.position.x
            self.pause_text.y = self.camera.position.y + 100
            self.pause_text.draw()

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        if self.paused:
            return

        self.update_snowflakes()

        self.alien.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -settings.PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = settings.PLAYER_SPEED

        self.alien.change_y = 0
        if self.up_pressed and not self.down_pressed:
            self.alien.change_y = settings.PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.alien.change_y = -settings.PLAYER_SPEED

        self.alien_list.update()
        self.alien.update_animation(delta_time)

        if arcade.check_for_collision_with_list(self.alien, self.wall_list):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2
        self.camera.position = camera_x, camera_y

        if not hasattr(self, 'coordinates_text'):
            self.coordinates_text = arcade.Text(
                "",
                x=0, y=0,
                color=arcade.color.WHITE,
                font_size=24,
                anchor_x="right", anchor_y="top"
            )
        self.coordinates_text.text = f"X: {int(self.alien.center_x)}, Y: {int(self.alien.center_y)}"
        self.coordinates_text.x = camera_x + settings.width // 2 - 20
        self.coordinates_text.y = camera_y + settings.height // 2 - 20

        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.center_x = camera_x
            self.dialogue_box.bottom = camera_y - (settings.height // 2)
            self.dialogue_text_sprite.position = (self.dialogue_box.center_x + 80, self.dialogue_box.center_y)
            self.dialogue_speaker.left = self.dialogue_box.left + 20
            self.dialogue_speaker.bottom = self.dialogue_box.bottom + 20

        if self.show_arrow:
            self.arrow.center_x = self.alien.center_x
            self.arrow.center_y = self.alien.center_y + 70

        if self.alien.center_x == -4200 or self.alien.center_x == -4000 and self.alien.center_y == -1000 or self.alien.center_y == -1200:
            self.window.switch_view("game")

    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()

        # Отрисовка игрового мира
        self.camera.use()
        self.bg_list.draw(pixelated=True)
        self.wall_list.draw()

        self.filter_list.draw()
        self.alien_list.draw(pixelated=True)

        self.snowflake_list.draw()

        self.arrow_list.draw(pixelated=True)

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
                anchor_x="right", anchor_y="top"
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

        # Проверка выхода из городской локации (если игрок возвращается назад)
        if self.alien.center_x == -4200 and self.alien.center_y == -1000:  # Проверка по X координате
            # Возвращаемся в основную локацию с помощью switch_view
            self.window.switch_view("game")

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

    def update_snowflakes(self):
        """Обновление снежинок: создание, движение и удаление"""
        # Спавн новых снежинок — только в пределах видимой области камеры
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite()
            snowflake.texture = self.snowflake_texture

            # Случайный размер: от 0.5 до 1.5
            size = random.uniform(0.5, 1.5)
            snowflake.scale = size

            # Начальная позиция — сверху экрана, с учётом камеры
            snowflake.center_x = random.uniform(
                self.camera.position.x - self.window.width // 2 - 1000,
                self.camera.position.x + self.window.width // 2 + 1000
            )
            snowflake.center_y = self.camera.position.y + self.window.height // 2 + 500

            # Случайная скорость падения и дрейф
            snowflake.speed = random.uniform(self.snowflake_speed_min, self.snowflake_speed_max)
            snowflake.drift = random.uniform(self.snowflake_drift_min, self.snowflake_drift_max)

            # Покачивание: сохраняем начальный X как базу
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
