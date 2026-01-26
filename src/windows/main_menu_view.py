import arcade
from pyglet.graphics import Batch
from src.settings import settings
import random
import math


class MainMenuView(arcade.View):
    """Главное меню игры"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.batch = Batch()
        self.shape_list = arcade.shape_list.ShapeElementList()
        self.title_text = None
        self.play_button = None
        self.play_text = None
        self.button_width = 0
        self.button_height = 0
        self.settings_button = None
        self.settings_text = None
        self.button_width = 0
        self.button_height = 0
        self.button_spacing = 0

        # Снежинки
        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2
        self.snowflake_speed_min = 1.5
        self.snowflake_speed_max = 4.0
        self.snowflake_drift_min = -5.0
        self.snowflake_drift_max = 0.7
        self.snowflake_wobble_speed = 0.03
        self.snowflake_wobble_amount = 0.8
        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)

        # Сова
        self.owl_list = arcade.SpriteList()
        self.owl_sprite = arcade.Sprite()
        self.owl_sprite.texture = arcade.load_texture("resources/UI/loading_screen/front_with_owl.png")
        self.owl_sprite.scale = 10.0
        self.owl_sprite.center_x = self.window.width // 2
        self.owl_sprite.center_y = self.window.height // 2
        self.owl_list.append(self.owl_sprite)
        
    def on_show_view(self):
        self.create_menu()

    def on_draw(self):
        self.clear()

        self.owl_list.draw(pixelated=True)

        self.snowflake_list.draw()
        
        # Отрисовка элементов меню
        self.shape_list.draw()
        self.batch.draw()

    def on_update(self, delta_time):
        self.update_snowflakes()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.switch_view("start")
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            self.start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка клика мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.check_button_click(x, y)

    def on_resize(self, width: float, height: float):
        """Обработка изменения размера окна"""
        super().on_resize(width, height)
        if hasattr(self, 'owl_sprite') and self.owl_sprite is not None:
            self.owl_sprite.center_x = self.window.width // 2
            self.owl_sprite.center_y = self.window.height // 2
        self.create_menu()

    def create_menu(self):
        """Создание элементов главного меню"""
        self.batch = Batch()
        self.shape_list.clear()

        center_x = self.window.width // 2
        title_y = self.window.height // 1.2
        button_y = self.window.height // 2
        base_width = settings.width_min

        # Размеры шрифтов
        title_font_size = int(24 * (self.window.width / base_width))
        button_font_size = int(20 * (self.window.width / base_width))

        self.title_text = arcade.Text(
            "Главное меню",
            center_x,
            title_y,
            arcade.color.RED,
            title_font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Рамка вокруг заголовка
        title_rect_width = self.title_text.content_width + int(min(self.window.width, self.window.height) * 0.05)
        title_rect_height = self.title_text.content_height + int(min(self.window.width, self.window.height) * 0.05)
        title_rect = arcade.shape_list.create_rectangle_outline(
            center_x=center_x,
            center_y=title_y,
            width=title_rect_width,
            height=title_rect_height,
            color=arcade.color.RED,
            border_width=2
        )
        self.shape_list.append(title_rect)

        # === Кнопка "Играть" ===
        self.play_text = arcade.Text(
            "Играть",
            center_x,
            button_y,
            arcade.color.WHITE,
            button_font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )
        self.button_width = self.play_text.content_width * 1.6
        self.button_height = self.play_text.content_height * 1.6
        self.button_spacing = self.button_height * 1.5  # Расстояние между кнопками

        self.play_button = arcade.shape_list.create_rectangle_filled(
            center_x=center_x,
            center_y=button_y,
            width=self.button_width,
            height=self.button_height,
            color=arcade.color.GREEN
        )
        self.shape_list.append(self.play_button)

        # Настройки
        settings_y = button_y - self.button_spacing  # Ниже кнопки "Играть"

        self.settings_text = arcade.Text(
            "Настройки",
            center_x,
            settings_y,
            arcade.color.WHITE,
            button_font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        self.settings_button = arcade.shape_list.create_rectangle_filled(
            center_x=center_x,
            center_y=settings_y,
            width=self.button_width,
            height=self.button_height,
            color=arcade.color.GREEN
        )
        self.shape_list.append(self.settings_button)

    def check_button_click(self, x, y):
        """Проверка нажатия на кнопку"""
        center_x = self.window.width // 2
        button_y = self.window.height // 2
        settings_y = button_y - self.button_spacing

        # Кнопка "Играть"
        if (center_x - self.button_width / 2 < x < center_x + self.button_width / 2 and 
            button_y - self.button_height / 2 < y < button_y + self.button_height / 2):
            self.start_game()

        # Кнопка "Настройки"
        elif (center_x - self.button_width / 2 < x < center_x + self.button_width / 2 and 
            settings_y - self.button_height / 2 < y < settings_y + self.button_height / 2):
            self.window.switch_view("settings")

    def start_game(self):
        """Запуск игры"""
        self.window.switch_view("game")

    def update_snowflakes(self):
        """Обновление снежинок: создание, движение и удаление"""
        # Спавн новых снежинок — только в пределах видимой области камеры
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite()
            snowflake.texture = self.snowflake_texture

            # Случайный размер: от 0.5 до 1.5
            size = random.uniform(0.5, 1.5)
            snowflake.scale = size

            # Начальная позиция — сверху экрана
            snowflake.center_x = random.uniform(0, self.window.width)
            snowflake.center_y = self.window.height + 20

            # Случайная скорость падения и дрейф
            snowflake.speed = random.uniform(self.snowflake_speed_min, self.snowflake_speed_max)
            snowflake.drift = random.uniform(self.snowflake_drift_min, self.snowflake_drift_max)

            # Покачивание: сохраняем начальный X как базу
            snowflake.base_x = snowflake.center_x
            snowflake.wobble_offset = 0.0

            self.snowflake_list.append(snowflake)

        # Обновляем каждую снежинку
        for snowflake in self.snowflake_list:
            # Падение вниз
            snowflake.center_y -= snowflake.speed
            # Дрейф влево/вправо
            snowflake.center_x += snowflake.drift
            # Покачивание (лёгкое движение из стороны в сторону)
            snowflake.wobble_offset += self.snowflake_wobble_speed
            # Используем только численные значения без дополнительных операций
            snowflake.center_x = snowflake.base_x + math.sin(snowflake.wobble_offset) * 0.8

            # Удаляем, если ушла за нижнюю границу
            if snowflake.center_y < -20:
                snowflake.remove_from_sprite_lists()