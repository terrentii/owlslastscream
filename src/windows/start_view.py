import arcade
from pyglet.graphics import Batch
from src.settings import settings
import random
import math




class StartView(arcade.View):
    """Стартовый экран с таймером перехода в главное меню"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.timer = 0.0
        self.batch = Batch()
        self.shape_list = arcade.shape_list.ShapeElementList()
        self.name_game = None
        self.rect_outline = None
        self.owl_sprite = None
        self.owl_scale = 10.0

        self.snowflake_list = arcade.SpriteList()
        self.owl_list = arcade.SpriteList()

        self.background_texture = arcade.load_texture('resources/UI/spruces_start.png')
        self.background_sprite = arcade.Sprite()
        self.background_sprite.texture = self.background_texture
        self.background_sprite.scale = 10.0
        self.background_sprite.center_x = self.window.width / 2
        self.background_sprite.center_y = self.window.height / 2

        self.fon_owl_list = arcade.SpriteList()
        self.fon_owl_list.append(self.background_sprite)

        # Загрузка текстур для анимации совы
        self.owl_textures = []
        texture_files = [
            'Sprite-0004.png',
            'Sprite-0005.png',
            'Sprite-0006.png',
            'Sprite-0007.png',
            'Sprite-0008.png',
            'Sprite-0009.png',
            'Sprite-0010.png',
            'Sprite-0011.png'
        ]
        
        for texture_file in texture_files:
            texture = arcade.load_texture(f'resources/UI/Owl/{texture_file}')
            self.owl_textures.append(texture)
        
        # Создание спрайта совы
        self.owl_sprite = arcade.Sprite()
        self.owl_sprite.center_x = -100  # Начальная позиция за левой границей экрана
        self.owl_sprite.center_y = self.window.height * 0.7  # 70% от высоты экрана
        self.owl_sprite.scale = 1.5
        self.owl_sprite.texture = self.owl_textures[0]
        self.owl_list.append(self.owl_sprite)
        
        # Параметры анимации
        self.current_texture_index = 0
        self.texture_change_frames = 5  # Количество кадров между сменой текстур
        self.frame_count = 0
        self.snowflake_spawn_chance = 0.2
        self.snowflake_speed_min = 1.5
        self.snowflake_speed_max = 4.0
        self.snowflake_drift_min = -5.0
        self.snowflake_drift_max = 0.7
        self.snowflake_wobble_speed = 0.03
        self.snowflake_wobble_amount = 0.8

        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)

    def setup(self):
        self.create_text()


    def on_show_view(self):
        self.setup()
        self.timer = 0.0

    def on_draw(self):
        self.clear()

        self.fon_owl_list.draw(pixelated=True)

        # Отрисовка снежинок
        self.snowflake_list.draw()
            
        # Отрисовка совы
        self.owl_list.draw(pixelated=True)
        
        # Отрисовка элементов старта
        self.batch.draw()
        self.shape_list.draw()

    def on_update(self, delta_time):
        self.update_snowflakes()
        
        # Обновление анимации совы
        self.frame_count += 1
        if self.frame_count % self.texture_change_frames == 0:
            self.current_texture_index = (self.current_texture_index + 1) % len(self.owl_textures)
            self.owl_sprite.texture = self.owl_textures[self.current_texture_index]
        
        # Движение совы слева направо
        self.owl_sprite.center_x += 5  # Скорость движения
        
        # Проверка выхода за правую границу экрана
        if self.owl_sprite.center_x > self.window.width + 100:
            # Возвращаем сову в начало за левую границу
            self.owl_sprite.center_x = -100
            
        self.timer += delta_time

        if self.timer >= 5.0:
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

        center_x = self.window.width // 2
        center_y = self.window.height // 2

        base_width = settings.width_min
        font_size = int(24 * (self.window.width / base_width))

        self.name_game = arcade.Text(
            settings.title,
            center_x,
            center_y,
            arcade.color.SNOW,
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
            color=arcade.color.ICEBERG,
            border_width=2
        )
        self.shape_list.append(self.rect_outline)
