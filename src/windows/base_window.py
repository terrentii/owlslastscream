import arcade

from src.settings import settings
from src.registry import BACKGROUND_PATH
from src.animations.RunningAlien import running_alien

class BaseWindow(arcade.Window):
    """Базовое окно"""
    def __init__(self):
        super().__init__(settings.width, settings.height, settings.title,
                         resizable=settings.resizable, fullscreen=settings.fullscreen)
        
        self.set_minimum_size(settings.width_min, settings.height_min)
        self.center_window()
        
        self.bg = arcade.Sprite(BACKGROUND_PATH, scale=1.0)
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)
    
        self.alien_list = arcade.SpriteList()
    
        self.alien = running_alien(scale=1.0)
        self.alien.center_x = settings.width // 2
        self.alien.center_y = settings.height // 4
    
        # нажатие клавиш
        self.left_pressed = False
        self.right_pressed = False
        self.speed = settings.PLAYER_SPEED  # скорость
    
        # Добавление в листы
        self.alien_list.append(self.alien)
        # Храним представления
        self.views = {}

    def get_view(self, view_name):
        """Получить или создать представление по имени"""
        if view_name not in self.views:
            if view_name == "start":
                from src.windows.start_view import StartView
                self.views[view_name] = StartView(self)
            elif view_name == "main_menu":
                from src.windows.main_menu_view import MainMenuView
                self.views[view_name] = MainMenuView(self)
            elif view_name == "game":
                from src.windows.game_view import GameView
                self.views[view_name] = GameView(self)
            elif view_name == "settings":
                from src.windows.settings_view import SettingsView
                self.views[view_name] = SettingsView(self)

        return self.views[view_name]

    def switch_view(self, view_name):
        """Переключиться на представление"""
        view = self.get_view(view_name)
        self.show_view(view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.close()

    def on_update(self, delta_time):
        # Обновление положения пришельца
        self.alien.change_x = 0

        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -self.speed
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = self.speed

        self.alien_list.update()
        self.alien.update_animation(delta_time)

        # Ограничение движения по краям экрана
        if self.alien.center_x < 0:
            self.alien.center_x = 0
        elif self.alien.center_x > settings.width:
            self.alien.center_x = settings.width

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.close()
        # Обработка нажатий клавиш для движения
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        # Обработка отпускания клавиш
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False