import arcade

WIDTH = 1280
HEIGHT = 720
TITLE = 'Owl`s last scream'


class Window(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.AMAZON) # Загрузка фона (зелёный цвет)

    def on_draw(self):
        """Здесь живут спрайты"""
        self.clear()
        arcade.draw_circle_filled(400, 300, 50, arcade.color.RED) #Просто круг

    def update(self, delta_time):
        pass


game = Window(WIDTH, HEIGHT, TITLE)
arcade.run()
