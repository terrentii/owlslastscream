import arcade

WIDTH = 1280
HEIGHT = 720
TITLE = 'Owl`s last scream'


class Window(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_GREEN) # Загрузка фона (зелёный цвет)

        self.alien_list = arcade.SpriteList()
        self.alien = arcade.Sprite('resources/persons/alien_in_pukhovik_new_year.png', 1.5)

        #Позиционирование
        self.alien.center_y = HEIGHT // 2
        self.alien.center_x = WIDTH // 2

        #Добавление в листы
        self.alien_list.append(self.alien)

    def on_draw(self):
        """Здесь живут спрайты"""
        self.clear()
        self.alien_list.draw() #Зелёный человечек

    def update(self, delta_time):
        self.alien.update()
        pass


game = Window(WIDTH, HEIGHT, TITLE)
arcade.run()
