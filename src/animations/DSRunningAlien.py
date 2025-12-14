import arcade
from src.registry import ALIEN_RUNNING_PATH, ALIEN_IDLE_RIGHT_PATH, ALIEN_IDLE_LEFT_PATH, ALIEN_RUN_GIF_PATH
from PIL import Image
import io


class RunningAlien(arcade.Sprite):
    def __init__(self, scale=1.0, gif_path=None):
        super().__init__(scale=scale)

        self.textures = []

        gif_path = ALIEN_RUN_GIF_PATH

        # Бег — загружаем из GIF
        self.running_textures_right = []
        self.running_textures_left = []

        # Загрузка GIF и извлечение кадров
        with Image.open(gif_path) as img:
            for frame in range(img.n_frames):
                img.seek(frame)
                # Преобразуем кадр в RGB, если нужно
                frame_image = img.convert("RGBA")
                # Создаём arcade.Texture из изображения
                texture = arcade.Texture(f"running_right_frame_{frame}", frame_image)
                self.running_textures_right.append(texture)
                # Создаём зеркальную текстуру (влево)
                flipped_image = frame_image.transpose(Image.FLIP_LEFT_RIGHT)
                flipped_texture = arcade.Texture(f"running_left_frame_{frame}", flipped_image)
                self.running_textures_left.append(flipped_texture)

        # idle текстуры остаются те же
        self.idle_texture_right = arcade.load_texture(ALIEN_IDLE_RIGHT_PATH)
        self.idle_texture_left = arcade.load_texture(ALIEN_IDLE_LEFT_PATH)

        self.texture = self.running_textures_right[0]
        self._facing_right = True

        # Анимация
        self.current_frame = 0
        self.time_since_last_frame = 0
        # Примерно 24 FPS (можно настроить под скорость GIF)
        self.frames_per_second = 24

    def update_animation(self, delta_time):
        # Анимация при движении
        if abs(self.change_x) > 0:
            self.time_since_last_frame += delta_time
            frame_duration = 1.0 / self.frames_per_second

            if self.time_since_last_frame >= frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.running_textures_right)

                facing_right = self.change_x > 0
                self._facing_right = facing_right

                if facing_right:
                    self.texture = self.running_textures_right[self.current_frame]
                else:
                    self.texture = self.running_textures_left[self.current_frame]

                self.time_since_last_frame = 0
        else:
            # Стоим на месте
            facing_right = getattr(self, '_facing_right', True)
            self.texture = self.idle_texture_right if facing_right else self.idle_texture_left
            self.current_frame = 0
            self.time_since_last_frame = 0


running_alien = RunningAlien()
