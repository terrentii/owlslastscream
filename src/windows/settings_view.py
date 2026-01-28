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

        self.resolutions = [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1366, 768),
        (1920, 1080)
    ]
        self.current_resolution_index = self.resolutions.index((settings.width, settings.height))
        self.resolution_text = None
        self.apply_button = None
        self.apply_text = None
        self.arrow_left = None
        self.arrow_right = None

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
            self.check_resolution_arrows(x, y)
            self.check_apply_button(x, y)

    def create_settings(self):
        """Создание элементов интерфейса настроек"""
        self.batch = Batch()
        self.shape_list.clear()


        base_x = self.window.width // 4
        title_y = self.window.height * 0.85
        back_y = self.window.height * 0.2
        resolution_y = self.window.height * 0.65
        arrows_y = resolution_y
        apply_y = self.window.height * 0.45
        base_width = settings.width_min

        # Размеры шрифтов
        title_font_size = int(32 * (self.window.width / base_width))
        button_font_size = int(20 * (self.window.width / base_width))
        small_font_size = int(18 * (self.window.width / base_width))
        

        # === Заголовок ===
        self.title_text = arcade.Text(
            "Настройки",
            base_x,
            title_y,
            arcade.color.YELLOW,
            title_font_size,
            bold=True,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )
            # === Стрелочки и поле разрешения ===
        arrow_scale_factor = 0.02   # 2% от ширины — размер стрелочки
        gap_ratio = 0.20            # 20% от ширины — расстояние от центра до стрелок        
        arrow_size = int(self.window.width * arrow_scale_factor)
        arrow_gap = int(self.window.width * gap_ratio)
        
        current_res = self.resolutions[self.current_resolution_index]
        res_text = f"{current_res[0]}x{current_res[1]}"

        # Позиции стрелок
        left_arrow_x = base_x - arrow_gap
        right_arrow_x = base_x + arrow_gap
        arrows_y = self.window.height * 0.65
        
            # Левая стрелочка "<"
        self.arrow_left = arcade.Text(
            "<",
            left_arrow_x,
            arrows_y,
            arcade.color.WHITE,
            arrow_size,
            bold=True,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        # Правая стрелочка ">"
        self.arrow_right = arcade.Text(
            ">",
            right_arrow_x,
            arrows_y,
            arcade.color.WHITE,
            arrow_size,
            bold=True,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
    )
        
        # Текст разрешения
        self.resolution_text = arcade.Text(
        res_text,
        base_x,
        resolution_y,
        arcade.color.LIGHT_GRAY,
        button_font_size,
        bold=True,
        anchor_x="center",
        anchor_y="center",
        batch=self.batch
    )

    # === Кнопка "Применить" ===
        self.apply_text = arcade.Text(
        "Применить",
        base_x,
        apply_y,
        arcade.color.WHITE,
        button_font_size,
        bold=True,
        anchor_x="center",
        anchor_y="center",
        batch=self.batch
    )
        button_width = self.apply_text.content_width * 1.8
        button_height = self.apply_text.content_height * 1.6
        self.button_spacing = self.button_height * 1.5

        self.apply_button = arcade.shape_list.create_rectangle_filled(
            center_x=base_x,
            center_y=apply_y,
            width=button_width,
            height=button_height,
            color=arcade.color.GREEN
        )
        self.shape_list.append(self.apply_button)

        # === Кнопка "Назад" ===
        self.back_text = arcade.Text(
            "Назад",
            base_x,
            back_y,
            arcade.color.WHITE,
            button_font_size,
            bold=True,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )
        back_button_width = self.back_text.content_width * 1.6
        back_button_height = self.back_text.content_height * 1.6

        # Прямоугольник под кнопкой (визуальный элемент)
        self.back_button = arcade.shape_list.create_rectangle_filled(
            center_x=base_x,
            center_y=back_y,
            width=back_button_width,
            height=back_button_height,
            color=arcade.color.BLUE
        )
        self.shape_list.append(self.back_button)

        self.update_resolution_text()

    def check_resolution_arrows(self, x, y):
        base_x = self.window.width // 4
        arrows_y = self.window.height * 0.65

        arrow_gap = int(self.window.width * 0.20)
        arrow_radius = int(self.window.width * 0.03)

        left_arrow_x = base_x - arrow_gap
        right_arrow_x = base_x + arrow_gap

        if (abs(x - left_arrow_x) < arrow_radius and abs(y - arrows_y) < arrow_radius):
                self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
                self.update_resolution_text()
        
        elif (abs(x - right_arrow_x) < arrow_radius and abs(y - arrows_y) < arrow_radius):
                self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
                self.update_resolution_text()

    def check_apply_button(self, x, y):
        base_x = self.window.width // 4
        apply_y = self.window.height * 0.45
        button_width = self.apply_text.content_width * 1.8
        button_height = self.apply_text.content_height * 1.6

        if (base_x - button_width / 2 < x < base_x + button_width / 2 and
            apply_y - button_height / 2 < y < apply_y + button_height / 2):

            # Получаем выбранное разрешение
            new_width, new_height = self.resolutions[self.current_resolution_index]

            # Применяем новое разрешение
            self.window.set_size(new_width, new_height)
            
            # Центрируем окно (опционально)
            screen_width, screen_height = arcade.get_display_size()
            pos_x = (screen_width - new_width) // 2
            pos_y = (screen_height - new_height) // 2
            self.window.set_location(pos_x, pos_y)

            # Обновляем интерфейс
            self.create_settings()  # пересоздаём UI под новый размер

    def update_resolution_text(self):
        """Обновляет текст разрешения после изменения"""
        current_res = self.resolutions[self.current_resolution_index]
        self.resolution_text.text = f"{current_res[0]}x{current_res[1]}"

    def check_back_button(self, x, y):
        base_x = self.window.width // 4
        back_y = self.window.height * 0.2
        width = self.back_text.content_width * 1.6
        height = self.back_text.content_height * 1.6

        if (base_x - width / 2 < x < base_x + width / 2 and
            back_y - height / 2 < y < back_y + height / 2):
            self.window.switch_view("main_menu")

    def update_snowflakes(self):
    # Спавн новых снежинок
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite()
            snowflake.texture = self.snowflake_texture

            size = random.uniform(0.5, 1.5)
            snowflake.scale = size

            snowflake.start_x = random.uniform(0, self.window.width)  # база
            snowflake.center_x = snowflake.start_x
            snowflake.center_y = self.window.height + 20

            snowflake.speed = random.uniform(self.snowflake_speed_min, self.snowflake_speed_max)
            snowflake.drift = random.uniform(self.snowflake_drift_min, self.snowflake_drift_max)
            snowflake.wobble_offset = 0.0

            self.snowflake_list.append(snowflake)

        # Обновление существующих
        for snowflake in self.snowflake_list:
            snowflake.center_y -= snowflake.speed
            snowflake.wobble_offset += self.snowflake_wobble_speed

            # Дрейф + покачивание
            snowflake.center_x = snowflake.start_x + snowflake.drift + math.sin(snowflake.wobble_offset) * self.snowflake_wobble_amount

            # Удаление за экраном
            if snowflake.center_y < -20:
                snowflake.remove_from_sprite_lists()
