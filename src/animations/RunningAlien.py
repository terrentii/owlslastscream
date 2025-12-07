import arcade
from src.registry import ALIEN_RUNNING_PATH, ALIEN_IDLE_RIGHT_PATH, ALIEN_IDLE_LEFT_PATH


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
            alien_run_right = arcade.load_texture(f'{ALIEN_RUNNING_PATH}{frame_number}.png')
            self.running_textures_right.append(alien_run_right)
            # движение влево
            alien_run_left = arcade.load_texture(f'{ALIEN_RUNNING_PATH}{frame_number}.png')
            alien_run_left = alien_run_left.flip_left_right()
            self.running_textures_left.append(alien_run_left)

        # idle
        self.idle_texture_right = arcade.load_texture(ALIEN_IDLE_RIGHT_PATH)
        self.idle_texture_left = arcade.load_texture(ALIEN_IDLE_LEFT_PATH)

        self.texture = self.running_textures_right[0]
        self._facing_right = True

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
                facing_right = self.change_x > 0
                self._facing_right = facing_right

                if facing_right:
                    self.texture = self.running_textures_right[self.current_frame]
                else:
                    self.texture = self.running_textures_left[self.current_frame]
                self.time_since_last_frame = 0
        else:
            # Стоит
            if hasattr(self, '_facing_right'):
                facing_right = self._facing_right
            else:
                facing_right = True

            if self.change_x != 0:
                facing_right = self.change_x > 0
                self._facing_right = facing_right

            if facing_right:
                self.texture = self.idle_texture_right
            else:
                self.texture = self.idle_texture_left

            self.current_frame = 0
            self.time_since_last_frame = 0


running_alien = RunningAlien