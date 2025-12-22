import arcade
import random as rd
from src.settings import settings
from src.animations.RunningAlien import RunningAlien

class GameView(arcade.View):
    """Представление игрового процесса"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        
        # Настройка фона
        self.bg = arcade.Sprite('resources/background/snow_blank.png', scale=1.0)
        self.bg.center_x = 0
        self.bg.center_y = 0
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)
        
        # Настройка елок
        self.spruce_list = arcade.SpriteList()
        for i in range(1000):
            spruce_type = 'spruce_3.png' if i % 3 == 0 else 'spruce_2.png' if i % 3 == 1 else 'spruce_1.png'
            spruce = arcade.Sprite(f'resources/background/outer_space/{spruce_type}', scale=0.5)
            spruce.center_x = rd.randint(-10000, 10000)
            spruce.center_y = rd.randint(-10000, 10000)
            self.spruce_list.append(spruce)
        
        # Настройка камеры
        self.camera = arcade.camera.Camera2D()
        self.camera.use()
        self.camera.zoom = 0.75
        
        # Настройка пришельца
        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=1.0)
        self.alien.center_x = settings.width // 2
        self.alien.center_y = settings.height // 4
        self.alien_list.append(self.alien)
        
        # Настройка Ness
        self.ness = arcade.Sprite('resources/persons/alien_ness/ness_no_anim.png', scale=0.22)
        # Ness
        import random
        center_x = settings.width // 2 + 50
        center_y = settings.height // 4
        
        self.ness.center_x = center_x + random.randint(-200, 200)
        self.ness.center_y = center_y + random.randint(-200, 200)
        self.alien_list.append(self.ness)
        
        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()
        
        self.camera.use()
        self.bg_list.draw()
        self.spruce_list.draw()
        self.alien_list.draw()

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        # скорость по оси X
        self.alien.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -settings.PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = settings.PLAYER_SPEED
            
        # скорость по оси Y
        self.alien.change_y = 0
        if self.up_pressed and not self.down_pressed:
            self.alien.change_y = settings.PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.alien.change_y = -settings.PLAYER_SPEED
            
        self.alien_list.update()
        self.alien.update_animation(delta_time)

        # Позиция камеры с небольшим смещением вверх
        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2  # Поднимаем камеру на половину высоты экрана
        self.camera.position = camera_x, camera_y

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False