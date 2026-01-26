import arcade
from pyglet.graphics import Batch
from src.settings import settings
import random
import math




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
        self.owl_sprite = None
        self.owl_scale = 10.0  # Начальный размер совы
        
        # --- НОВАЯ НАСТРОЙКА СНЕГА ---
        self.snowflake_list = arcade.SpriteList()
        self.owl_list = arcade.SpriteList()  # Список для спрайта совы
        
        # --- НОВАЯ НАСТРОЙКА СНЕГА ---
        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2  # Увеличена вероятность спавна снежинки за кадр
        self.snowflake_speed_min = 1.5  # Увеличена минимальная скорость падения
        self.snowflake_speed_max = 4.0  # Увеличена максимальная скорость падения
        self.snowflake_drift_min = -5.0  # Увеличен дрейф влево
        self.snowflake_drift_max = 0.7  # Увеличен дрейф вправо
        self.snowflake_wobble_speed = 0.03  # Увеличена скорость покачивания
        self.snowflake_wobble_amount = 0.8  # Увеличена амплитуда покачивания

        # Создаём текстуру более белой и мягкой снежинки 8x8 пикселей
        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)

    def setup(self):
        self.create_text()
        # Загрузка спрайта совы
        self.owl_sprite = arcade.Sprite("resources/UI/loading_screen/front_with_owl.png")
        self.owl_sprite.scale = self.owl_scale
        self.owl_sprite.center_x = self.window.width // 2
        self.owl_sprite.center_y = self.window.height // 2
        # Добавляем спрайт совы в SpriteList
        self.owl_list.clear()
        self.owl_list.append(self.owl_sprite)

    def on_show_view(self):
        self.setup()
        self.timer = 0.0

    def on_draw(self):
        self.clear()
        
        # Отрисовка снежинок
        self.snowflake_list.draw()
        
        # Отрисовка совы, если она загружена
        if hasattr(self, 'owl_list') and self.owl_list is not None:
            self.owl_list.draw(pixelated=True)
            
        # Отрисовка элементов старта
        self.batch.draw()
        self.shape_list.draw()

    def on_update(self, delta_time):
        # Обновление снежинок
        self.update_snowflakes()
        
        self.timer += delta_time

        # Обновление позиции совы
        if self.owl_sprite is not None:
            # Сову размещаем в верхней части экрана
            self.owl_sprite.center_x = self.window.width // 2
            self.owl_sprite.center_y = self.window.height * 0.7  # 70% от высоты экрана

        # Переход на главное меню через 3 секунды
        if self.timer >= 3.0:
            self.window.switch_view("main_menu")

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.create_text()

    def create_text(self):
        self.batch = Batch()
        if self.shape_list:
            self.shape_list.clear()

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
