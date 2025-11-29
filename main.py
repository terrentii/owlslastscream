import arcade

WIDTH = 1280
HEIGHT = 720
TITLE = 'Owl`s last scream'

class RunningAlien(arcade.Sprite):
    def __init__(self, scale=1.0):
        super().__init__(scale=scale)

        self.textures = []


        for i in range(14):
            frame_number = f"{i:02d}"
            alien_run = arcade.load_texture(f'resources/persons/alien_running/sprite_{frame_number}.png')
            self.textures.append(alien_run)

        self.texture = self.textures[0]

        #Для анимации
        self.current_frame = 0
        self.time_since_last_frame = 0
        self.frames_per_second = 24

    def update_animation(self, delta_time):
        self.time_since_last_frame += delta_time

        frame_duration = 1.0 / self.frames_per_second

        if self.time_since_last_frame >= frame_duration:
            self.current_frame += 1
            if self.current_frame >= len(self.textures):
                self.current_frame = 0

            self.texture = self.textures[self.current_frame]
            self.time_since_last_frame = 0


class Window(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_GREEN) # Загрузка фона (зелёный цвет)

        self.alien_list = arcade.SpriteList()

        self.alien = RunningAlien(scale=1.0)
        self.alien.center_x = WIDTH // 2
        self.alien.center_y = HEIGHT // 2

        #Добавление в листы
        self.alien_list.append(self.alien)

    def on_draw(self):
        """Здесь живут спрайты"""
        self.clear()
        self.alien_list.draw() #Зелёный человечек

    def on_update(self, delta_time):
        self.alien.update_animation(delta_time)


game = Window(WIDTH, HEIGHT, TITLE)
arcade.run()
