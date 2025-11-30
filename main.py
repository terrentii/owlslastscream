import arcade
from pyglet.event import EVENT_HANDLE_STATE

WIDTH = 1280
HEIGHT = 720
TITLE = 'Owl`s last scream'


class RunningAlien(arcade.Sprite):
    def __init__(self, scale=1.0):
        super().__init__(scale=scale)

        self.textures = []

        # Бег
        self.running_textures_right = []
        self.running_textures_left = []
        for i in range(14):
            frame_number = f"{i:02d}"
            # движение вправо
            alien_run_right = arcade.load_texture(f'resources/persons/alien_running/sprite_{frame_number}.png')
            self.running_textures_right.append(alien_run_right)
            # движение влево
            alien_run_left = arcade.load_texture(f'resources/persons/alien_running/sprite_{frame_number}.png')
            alien_run_left = alien_run_left.flip_left_right()
            self.running_textures_left.append(alien_run_left)

        # idle
        self.idle_texture_right = arcade.load_texture('resources/persons/steady_alien.png')
        self.idle_texture_left = arcade.load_texture('resources/persons/steady_alien.png')
        self.idle_texture_left = self.idle_texture_left.flip_left_right()

        self.texture = self.running_textures_right[0]

        # Для анимации
        self.current_frame = 0
        self.time_since_last_frame = 0
        self.frames_per_second = 24

    def update_animation(self, delta_time):
        # Анимация
        if abs(self.change_x) > 0:
            # Бежит
            self.time_since_last_frame += delta_time
            frame_duration = 1.0 / self.frames_per_second

            if self.time_since_last_frame >= frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.running_textures_right)
                # направление
                if self.change_x > 0:
                    self.texture = self.running_textures_right[self.current_frame]
                else:
                    self.texture = self.running_textures_left[self.current_frame]
                self.time_since_last_frame = 0
        else:
            # Стоит
            if self.change_x == 0:
                self.texture = self.idle_texture_right if self.change_x >= 0 else self.idle_texture_left
            self.current_frame = 0
            self.time_since_last_frame = 0


class Window(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        # arcade.set_background_color(arcade.color.DARK_GREEN) # Загрузка фона (зелёный цвет)

        self.bg = arcade.Sprite('resources/background/image.png', scale=1.0)
        self.bg.center_x = WIDTH // 2
        self.bg.center_y = HEIGHT // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)

        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=1.0)
        self.alien.center_x = WIDTH // 2
        self.alien.center_y = HEIGHT // 4

        # нажатие клавиш
        self.left_pressed = False
        self.right_pressed = False
        self.speed = 5  # скорость

        # Добавление в листы
        self.alien_list.append(self.alien)

    def on_draw(self):
        """Здесь живут спрайты"""
        self.clear()
        self.bg_list.draw()

        self.alien_list.draw()  # Зелёный человечек

    def on_update(self, delta_time):
        self.alien.change_x = 0

        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -self.speed
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = self.speed

        self.alien_list.update()

        self.alien.update_animation(delta_time)

        if self.alien.center_x < 0:
            self.alien.center_x = 0
        elif self.alien.center_x > WIDTH:
            self.alien.center_x = WIDTH

    def on_key_press(self, key, modifiers: int) -> EVENT_HANDLE_STATE:  # Нажатие
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers: int) -> EVENT_HANDLE_STATE:  # Отпускание
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False


game = Window(WIDTH, HEIGHT, TITLE)
arcade.run()
