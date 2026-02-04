import arcade
from src.settings import settings


class ShopView(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.money = 100
        self.selected_item = None
        self.dragging_item = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.items = []
        self.setup_items()

        self.background = arcade.load_texture("resources/background/shop.png")

        self.back_button = arcade.Sprite("resources/UI/back.png", 2.0)
        self.back_button.center_x = 100
        self.back_button.center_y = 100

        self.back_button_list = arcade.SpriteList()
        self.back_button_list.append(self.back_button)
        
        self.bg_music = None
        self.setup_music()

    def setup_music(self):
        try:
            self.bg_music = arcade.Sound("sound/music/OutOfSpace.wav")
            self.bg_music_player = self.bg_music.play(volume=1.0, loop=True)
        except Exception as e:
            print(f"Failed to load music: {e}")
    def __init__(self, window, player_position=None):
        super().__init__()
        self.window = window
        self.player_position = player_position or {'x': 0, 'y': 0}
        
        # Фон
        bg_texture = arcade.load_texture('resources/background/neutral.png')
        self.bg = arcade.Sprite(bg_texture, scale=8.0)
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)
        
        # Создаем магазин
        shop_texture = arcade.load_texture('resources/buildings/shop.png')
        self.shop = arcade.Sprite(shop_texture, scale=3.0)
        self.shop.center_x = -375
        self.shop.center_y = 2335
        self.shop_list = arcade.SpriteList()
        self.shop_list.append(self.shop)
        
        # Камера
        self.camera = arcade.camera.Camera2D()
        self.camera.zoom = 0.75
        
        # Пришелец
        self.alien = arcade.Sprite('resources/persons/alien_ness/ness_in_spacesuit.png', scale=3.0)
        self.alien.center_x = self.player_position['x']
        self.alien.center_y = self.player_position['y']
        self.alien_list = arcade.SpriteList()
        self.alien_list.append(self.alien)
        
        # Управление
        self.left_pressed = self.right_pressed = self.up_pressed = self.down_pressed = False
        
    def on_draw(self):
        self.clear()
        self.camera.use()
        
        self.bg_list.draw(pixelated=True)
        self.shop_list.draw(pixelated=True)
        self.alien_list.draw(pixelated=True)
        
    def on_update(self, delta_time):
        # Обновление скорости пришельца
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

        # Обновление позиций
        self.alien_list.update()

        # Проверка коллизии с магазином
        if arcade.check_for_collision_with_list(self.alien, self.shop_list):
            # Переключаемся на подмир магазина
            self.window.switch_view("shop_world")

        # Позиционирование камеры
        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2
        self.camera.position = camera_x, camera_y

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False