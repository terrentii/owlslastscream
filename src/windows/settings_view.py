import arcade
import random
import math
from src.settings import settings
from pyglet.graphics import Batch

class SettingsView(arcade.View):
    """Окно настроек игры"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.batch = Batch()
        self.shape_list = arcade.shape_list.ShapeElementList()
        self.title_text = None
        self.back_button = None
        self.back_text = None
        self.button_width = 0
        self.button_height = 0
        self.button_spacing = 0

        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2
        self.snowflake_speed_min = 1.5
        self.snowflake_speed_max = 4.0
        self.snowflake_drift_min = -5.0
        self.snowflake_drift_max = 0.7
        self.snowflake_wobble_speed = 0.03
        self.snowflake_wobble_amount = 0.8

        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)

    def on_show_view(self):
        self.create_settings()

    def on_draw(self):
        self.clear()
        
        # Отрисовка снежинок
        self.snowflake_list.draw()
        
        # Отрисовка элементов настроек
        self.shape_list.draw()
        self.batch.draw()

    def on_update(self, delta_time):
        self.update_snowflakes()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.create_settings()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.check_back_button(x, y)

    def create_settings(self):
        """Создание элементов интерфейса настроек"""
        self.batch = Batch()
        self.shape_list.clear()


        center_x = self.window.width // 2
        title_y = self.window.height * 0.8
        back_y = self.window.height * 0.2
        base_width = settings.width_min

        # Размеры шрифтов
        title_font_size = int(24 * (self.window.width / base_width))
        button_font_size = int(20 * (self.window.width / base_width))

        # === Заголовок ===
        self.title_text = arcade.Text(
            "Настройки",
            center_x,
            title_y,
            arcade.color.YELLOW,
            title_font_size,
            bold=True,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # === Кнопка "Назад" ===
        self.back_text = arcade.Text(
            "Назад",
            center_x,
            back_y,
            arcade.color.WHITE,
            button_font_size,
            bold=True,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )
        self.button_width = self.back_text.content_width * 1.6
        self.button_height = self.back_text.content_height * 1.6
        self.button_spacing = self.button_height * 1.5

        # Прямоугольник под кнопкой (визуальный элемент)
        self.back_button = arcade.shape_list.create_rectangle_filled(
            center_x=center_x,
            center_y=back_y,
            width=self.button_width,
            height=self.button_height,
            color=arcade.color.BLUE
        )
        self.shape_list.append(self.back_button)

    def check_back_button(self, x, y):
        """Проверка нажатия на кнопку 'Назад'"""
        center_x = self.window.width // 2
        back_y = self.window.height * 0.2

        if (center_x - self.button_width / 2 < x < center_x + self.button_width / 2 and
            back_y - self.button_height / 2 < y < back_y + self.button_height / 2):
            self.window.switch_view("main_menu")

    def update_snowflakes(self):
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite()
            snowflake.texture = self.snowflake_texture

            size = random.uniform(0.5, 1.5)
            snowflake.scale = size

            snowflake.center_x = random.uniform(0, self.window.width)
            snowflake.center_y = self.window.height + 20

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

            if snowflake.center_y < -20:
                snowflake.remove_from_sprite_lists()