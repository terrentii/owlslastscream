import arcade
from src.settings import settings
from src.animations.RunningAlien import RunningAlien

class GameView(arcade.View):
    """Представление игрового процесса"""
    def __init__(self, window):
        super().__init__()
        self.window = window
        
        # Настройка фона
        self.bg = arcade.Sprite('resources/background/image.png', scale=1.0)
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)
        
        # Настройка пришельца
        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=1.0)
        self.alien.center_x = settings.width // 2
        self.alien.center_y = settings.height // 4
        self.alien_list.append(self.alien)
        
        # Управление
        self.left_pressed = False
        self.right_pressed = False
        
    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()
        self.bg_list.draw()
        self.alien_list.draw()

    def on_update(self, delta_time):
        """Обновление игровой логики"""
        # Управление скоростью
        self.alien.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -settings.PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = settings.PLAYER_SPEED
            
        # Обновление спрайтов
        self.alien_list.update()
        self.alien.update_animation(delta_time)
        
        # Ограничение движения
        if self.alien.center_x < 0:
            self.alien.center_x = 0
        elif self.alien.center_x > settings.width:
            self.alien.center_x = settings.width

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.ESCAPE:
            self.window.switch_view("main_menu")
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False