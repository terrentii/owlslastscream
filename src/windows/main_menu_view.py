import arcade
from pyglet.graphics import Batch
from src.settings import settings


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
        self.settings_button = None  # НОВОЕ: кнопка настроек
        self.settings_text = None    # НОВОЕ: текст настроек
        self.button_width = 0
        self.button_height = 0
        self.button_spacing = 0      # НОВОЕ: расстояние между кнопками
        
    def on_show_view(self):
        self.create_menu()

    def on_draw(self):
        """Рисование"""
        self.clear()
        self.shape_list.draw()
        self.batch.draw()

    def on_update(self, delta_time):
        pass

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

        # === Заголовок ===
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

        # === Кнопка "Настройки" ===
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