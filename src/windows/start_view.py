import arcade
from pyglet.graphics import Batch
from src.settings import settings


class StartView(arcade.View):
    """Стартовый экран с таймером перехода в главное меню"""
    def __init__(self, window):
        super().__init__()
        self.window = window  # Ссылка на главное окно
        self.timer = 0.0
        self.batch = Batch()
        self.shape_list = arcade.shape_list.ShapeElementList()
        self.name_game = None
        self.rect_outline = None

    def setup(self):
        self.create_text()

    def on_show_view(self):
        self.setup()
        self.timer = 0.0

    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.shape_list.draw()

    def on_update(self, delta_time):
        self.timer += delta_time

        # Переход на главное меню через 5 секунд
        if self.timer >= 3.0:
            self.window.switch_view("main_menu")

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.create_text()

    def create_text(self):
        self.batch = Batch()
        if self.shape_list:
            self.shape_list.clear()

        center_x = self.window.width // 2
        center_y = self.window.height // 2

        base_width = settings.width_min
        font_size = int(24 * (self.window.width / base_width))

        self.name_game = arcade.Text(
            settings.title,
            center_x,
            center_y,
            arcade.color.RED,
            font_size,
            bold=True,
            align="center",
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )

        text_width = self.name_game.content_width
        text_height = self.name_game.content_height
        padding = int(min(self.window.width, self.window.height) * 0.05)
        rect_width = text_width + padding
        rect_height = text_height + padding

        self.rect_outline = arcade.shape_list.create_rectangle_outline(
            center_x=center_x,
            center_y=center_y,
            width=rect_width,
            height=rect_height,
            color=arcade.color.RED,
            border_width=2
        )
        self.shape_list.append(self.rect_outline)
