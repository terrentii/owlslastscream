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

        self.bg_color = arcade.color.BLACK
        self.button_color = arcade.color.DARK_SLATE_GRAY
        self.button_hover_color = arcade.color.SLATE_GRAY
        self.button_outline_color = arcade.color.DARK_BLUE
        self.text_color = arcade.color.OLD_LACE
        self.title_color = arcade.color.GO_GREEN
        
    def on_show_view(self):
        self.create_menu()

    def on_draw(self):
        self.clear(self.bg_color)
        self.snowflake_list.draw()
        self.owl_list.draw(pixelated=True)

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

        menu_x = self.window.width * 0.25
        menu_base_y = self.window.height * 0.25
        button_rise = 100
        
        # Позиция заголовка остается вверху
        title_y = self.window.height * 0.85
        base_width = settings.width_min

        # Размеры шрифтов
        title_font_size = int(24 * (self.window.width / base_width))
        button_font_size = int(20 * (self.window.width / base_width))

        self.title_text = arcade.Text(
            "Начальное меню",
            self.window.width // 1.5,
            title_y + 20,
            self.title_color,
            title_font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Рамка вокруг заголовка изо льда
        title_rect_width = self.title_text.content_width + int(min(self.window.width, self.window.height) * 0.1)
        title_rect_height = self.title_text.content_height + int(min(self.window.width, self.window.height) * 0.1)
        title_rect = arcade.shape_list.create_rectangle_outline(
            center_x=self.window.width // 1.5,
            center_y=title_y + 20,
            width=title_rect_width,
            height=title_rect_height,
            color=self.title_color,
            border_width=4
        )
        self.shape_list.append(title_rect)
        
        # Внутренняя рамка заголовка
        title_inner_rect = arcade.shape_list.create_rectangle_outline(
            center_x=self.window.width // 1.5,
            center_y=title_y + 20,
            width=title_rect_width - 8,
            height=title_rect_height - 8,
            color=arcade.color.LIGHT_BLUE,
            border_width=2
        )
        self.shape_list.append(title_inner_rect)

        # === Кнопка "Играть" ===
        button_center_y = menu_base_y + self.button_height + button_rise
        self.play_text = arcade.Text(
            "Играть",
            menu_x,
            button_center_y,
            self.text_color,
            button_font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )
        self.button_width = self.play_text.content_width * 2.0  # Шире кнопки
        self.button_height = self.play_text.content_height * 2.0

        # Заливка кнопки
        self.play_button = arcade.shape_list.create_rectangle_filled(
            center_x=menu_x,
            center_y=button_center_y,
            width=self.button_width,
            height=self.button_height,
            color=self.button_color
        )
        self.shape_list.append(self.play_button)
        
        # Обводка кнопки
        self.play_button_outline = arcade.shape_list.create_rectangle_outline(
            center_x=menu_x,
            center_y=button_center_y,
            width=self.button_width + 4,
            height=self.button_height + 4,
            color=self.button_outline_color,
            border_width=3
        )
        self.shape_list.append(self.play_button_outline)

        # Настройки
        settings_y = menu_base_y - 20

        self.settings_text = arcade.Text(
            "Настройки",
            menu_x,
            settings_y,
            self.text_color,
            button_font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Заливка кнопки настроек
        self.settings_button = arcade.shape_list.create_rectangle_filled(
            center_x=menu_x,
            center_y=settings_y,
            width=self.button_width,
            height=self.button_height,
            color=self.button_color
        )
        self.shape_list.append(self.settings_button)
        
        # Обводка кнопки настроек
        self.settings_button_outline = arcade.shape_list.create_rectangle_outline(
            center_x=menu_x,
            center_y=settings_y,
            width=self.button_width + 4,
            height=self.button_height + 4,
            color=self.button_outline_color,
            border_width=3
        )
        self.shape_list.append(self.settings_button_outline)

    def check_button_click(self, x, y):
        menu_x = self.window.width * 0.25
        menu_base_y = self.window.height * 0.25
        button_rise = 40
        button_center_y = menu_base_y + self.button_height + button_rise
        settings_y = menu_base_y - 20

        # Кнопка "Играть"
        if (menu_x - self.button_width / 2 < x < menu_x + self.button_width / 2 and 
            button_center_y - self.button_height / 2 < y < button_center_y + self.button_height / 2):
            self.start_game()

        # Кнопка "Настройки"
        elif (menu_x - self.button_width / 2 < x < menu_x + self.button_width / 2 and 
            settings_y - self.button_height / 2 < y < settings_y + self.button_height / 2):
            self.window.switch_view("settings")

    def start_game(self):
        """Запуск игры"""
        self.window.switch_view("game")

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