class Settings:
    def __init__(self):
        self.resolution = self.width, self.height = 1280, 720  # Разрешение экрана

        # Минимальное разрешение экрана
        self.resolution_min = self.width_min, self.height_min = 800, 600
        self.resizable = False  # редактирование размера окна
        self.fullscreen = False  # Полноэкранный режим экрана, берется размер экрана

        self.title = "Owl`s last scream"

        self.reboot = False  # для перезагрузки приложения

        self.FPS = 60

        self.PLAYER_SPEED = 5


settings = Settings()
