# src/windows/settings_view.py
import arcade
from src.settings import settings

class SettingsView(arcade.View):
    """Окно настроек игры"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.batch = arcade.SpriteList()  # Используем SpriteList как контейнер для Text
        self.title_text = None
        self.back_button = None
        self.back_text = None
        self.button_width = 0
        self.button_height = 0

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        self.clear()
        self.batch.draw()

        # Рисуем заголовок и кнопку отдельно, если нужно
        if self.title_text:
            self.title_text.draw()
        if self.back_text:
            self.back_text.draw()

    def on_update(self, delta_time):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.check_back_button(x, y)

    def setup(self):
        """Создание элементов интерфейса настроек"""
        self.batch = arcade.SpriteList()
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
            anchor_y="center"
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
            anchor_y="center"
        )
        self.button_width = self.back_text.content_width * 1.6
        self.button_height = self.back_text.content_height * 1.6

        # Прямоугольник под кнопкой (визуальный элемент)
        self.back_button = arcade.shape_list.create_rectangle_filled(
            center_x=center_x,
            center_y=back_y,
            width=self.button_width,
            height=self.button_height,
            color=arcade.color.BLUE
        )
        self.back_button.draw()  # Рисуем сразу, так как shape_list не включен в SpriteList

    def check_back_button(self, x, y):
        """Проверка нажатия на кнопку 'Назад'"""
        center_x = self.window.width // 2
        back_y = self.window.height * 0.2

        if (center_x - self.button_width / 2 < x < center_x + self.button_width / 2 and
            back_y - self.button_height / 2 < y < back_y + self.button_height / 2):
            self.window.switch_view("main_menu")

    def on_resize(self, width: float, height: float):
        """Обработка изменения размера окна"""
        super().on_resize(width, height)
        self.setup()
