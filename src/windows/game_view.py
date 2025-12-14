import arcade
from src.settings import settings
from src.animations.RunningAlien import RunningAlien

class GameView(arcade.View):
    """Представление игрового процесса"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        
        # Настройка фона
        self.bg = arcade.Sprite('resources/background/bg_snow.png', scale=1.0)
        self.bg.center_x = 0
        self.bg.center_y = 0
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)
        
        # Настройка камеры
        self.camera = arcade.camera.Camera2D()
        
        # Настройка пришельца
        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=1.0)
        self.alien.center_x = settings.width // 2
        self.alien.center_y = settings.height // 4
        self.alien_list.append(self.alien)
        
        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()
        
        # Применение камеры
        self.camera.use()
        self.bg_list.draw()
        self.alien_list.draw()

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        # Управление скоростью по оси X
        self.alien.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -settings.PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = settings.PLAYER_SPEED
            
        # Управление скоростью по оси Y
        self.alien.change_y = 0
        if self.up_pressed and not self.down_pressed:
            self.alien.change_y = settings.PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.alien.change_y = -settings.PLAYER_SPEED
            
        # Обновление спрайтов
        self.alien_list.update()
        self.alien.update_animation(delta_time)
        
        # Убраны ограничения движения - пришелец может выходить за края экрана
        # Ограничения были удалены по запросу пользователя
            
        # Обновление камеры, чтобы следовать за пришельцем по обеим осям
        self.camera.position = self.alien.center_x, self.alien.center_y

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