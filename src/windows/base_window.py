import arcade
import math
import random

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
        self.views = {}
        
        # Настройка снега
        self.snowflake_list = arcade.SpriteList()
        self.snowflake_texture = arcade.make_soft_square_texture(6, arcade.color.WHITE, outer_alpha=100)  # Немного больше и прозрачнее
        self.snowflake_spawn_chance = 0.3  # Увеличена вероятность появления
        self.snowflake_speed_y = 2.5  # Увеличена скорость падения
        self.snowflake_drift_x = -0.8  # Увеличено смещение влево
        self.snowflake_wind = 0  # Для эффекта ветра

        # Музыка
        try:
            self.music = arcade.Sound("sound/music/OutOfSpace.wav")
            self.music_player = self.music.play(loop=True)
        except Exception as e:
            print(f"Failed to load music: {e}")

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
            elif view_name == "city":
                from src.windows.city_view import CityView
                self.views[view_name] = CityView(self)
            elif view_name == "settings":
                from src.windows.settings_view import SettingsView
                self.views[view_name] = SettingsView(self)
            elif view_name == "shop_world":
                from src.windows.shop_world_view import ShopWorldView
                self.views[view_name] = ShopWorldView(self)

        return self.views[view_name]

    def switch_view(self, view_name):
        """Переключиться на представление"""
        view = self.get_view(view_name)
        self.show_view(view)

    def on_draw(self):
        """Отрисовка игрового экрана"""
        self.clear()
        
        # Отрисовка фона
        self.bg_list.draw()
        
        # Отрисовка снежинок
        self.snowflake_list.draw()
        
        # Отрисовка пришельца
        self.alien_list.draw(pixelated=True)
        
        # Вызываем on_draw текущего представления, если оно существует
        current_view = self.current_view
        if hasattr(current_view, 'on_draw') and current_view != self:
            current_view.on_draw()
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.close()

    def update_snowflakes(self):
        """Обновление позиций и создание новых снежинок"""
        # Создаем новые снежинки
        if len(self.snowflake_list) < 200:  # Ограничиваем количество снежинок
            for _ in range(3):  # Создаем несколько снежинок за раз
                if random.random() < self.snowflake_spawn_chance:
                    snowflake = arcade.Sprite()
                    snowflake.texture = self.snowflake_texture
                    snowflake.scale = random.uniform(0.5, 1.5)  # Разные размеры снежинок
                    # Снежинка появляется в случайной позиции сверху экрана
                    snowflake.center_x = self.width // 2 + random.randint(-self.width // 2, self.width // 2)
                    snowflake.center_y = self.height
                    self.snowflake_list.append(snowflake)
        
        # Создаем список снежинок для итерации
        snowflakes = list(self.snowflake_list)
        
        # Обновляем позиции всех снежинок
        for snowflake in snowflakes:
            snowflake.center_y -= self.snowflake_speed_y
            snowflake.center_x += self.snowflake_drift_x
            
            # Добавляем легкий эффект ветра
            if random.random() < 0.02:
                self.snowflake_wind = random.uniform(-1.5, 1.5)
            
            # Применяем ветер к снежинкам
            snowflake.center_x += self.snowflake_wind * 0.1
        
        # Удаляем снежинки, которые ушли за нижнюю границу экрана
        for snowflake in snowflakes:
            if snowflake.center_y < 0:
                snowflake.remove_from_sprite_lists()

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
            
        # Обновление снежинок
        self.update_snowflakes()

    def on_key_press(self, key, modifiers):
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