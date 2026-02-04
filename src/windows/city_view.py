import arcade
import random
import math
from src.settings import settings
from src.animations.RunningAlien import RunningAlien
import json
import os
import time

class CityView(arcade.View):
    def __init__(self, window, player_position=None):
        super().__init__()
        self.window = window
        self.save_file = "saves/city_save.json"
        self.last_save_time = 0
        self.save_interval = 20  # секунды
        self.player_position = player_position or self.load_save() or {'x': -4000, 'y': -1000}
        self.paused = False

        # Оверлей и текст паузы
        self.overlay = arcade.shape_list.ShapeElementList()
        self.overlay_rectangle = arcade.shape_list.create_rectangle_filled(
            center_x=0, center_y=0,
            width=settings.width * 30, height=settings.height * 30,
            color=(0, 0, 0, 150)
        )
        self.overlay.append(self.overlay_rectangle)
        self.pause_text = arcade.Text(
            "ПАУЗА", x=0, y=0, color=arcade.color.WHITE, font_size=50,
            anchor_x="center", anchor_y="center"
        )

        # Фон
        bg_texture = arcade.load_texture('resources/background/gorod.png')
        self.bg = arcade.Sprite(bg_texture, scale=8.0)
        self.bg.center_x = settings.width // 2
        self.bg.center_y = settings.height // 2
        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg)

        # Камера
        self.camera = arcade.camera.Camera2D()
        self.camera.zoom = 0.75

        # Пришелец
        self.alien = RunningAlien(scale=3.0)
        self.alien.center_x = self.player_position['x']
        self.alien.center_y = self.player_position['y']
        self.alien_list = arcade.SpriteList()
        self.alien_list.append(self.alien)

        # Сюжетные фазы
        self.story_phases = self.load_story_phases()

        # Стрелка над пришельцем
        self.arrow = arcade.Sprite('resources/UI/arrow/arrow_mini.png', scale=5.0)
        self.arrow.alpha = 0
        self.arrow_list = arcade.SpriteList()
        self.arrow_list.append(self.arrow)
        self.show_arrow = False

        # Стены
        self.wall_list = arcade.SpriteList()
        center_x, center_y = settings.width // 2, settings.height // 2
        map_width, map_height = 10280, 5800
        left_edge = center_x - map_width // 2
        right_edge = center_x + map_width // 2
        bottom_edge = center_y - map_height // 2
        top_edge = center_y + map_height // 2
        wall_texture = arcade.load_texture('resources/background/nothing.png')
        wall_width = 64

        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite(wall_texture)
            wall.center_x, wall.center_y = x, bottom_edge
            self.wall_list.append(wall)

        for x in range(left_edge + wall_width // 2, right_edge, wall_width):
            wall = arcade.Sprite(wall_texture)
            wall.center_x, wall.center_y = x, top_edge
            self.wall_list.append(wall)

        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite(wall_texture, angle=90)
            wall.center_x, wall.center_y = left_edge, y
            self.wall_list.append(wall)

        for y in range(bottom_edge + wall_width // 2, top_edge, wall_width):
            wall = arcade.Sprite(wall_texture, angle=90)
            wall.center_x, wall.center_y = right_edge, y
            self.wall_list.append(wall)

        # Диалоговое окно
        screen_width, screen_height = settings.width, settings.height
        self.dialogue_box = arcade.SpriteSolidColor(screen_width, 120, color=(10, 9, 9, 180))
        self.dialogue_box.center_x = screen_width // 2
        self.dialogue_box.bottom = 0
        self.dialogue_sprite_list = arcade.SpriteList()
        self.dialogue_sprite_list.append(self.dialogue_box)

        self.dialogue_text_sprite = arcade.Text(
            "", self.dialogue_box.center_x + 80, self.dialogue_box.center_y,
            arcade.color.ASH_GREY, font_size=18, anchor_x="center", anchor_y="center",
            multiline=True, width=screen_width - 200
        )

        self.dialogue_speaker = arcade.Sprite('resources/persons/alien_ness/ness_in_spacesuit.png', scale=3)
        self.dialogue_speaker.left, self.dialogue_speaker.bottom = 20, 20
        self.dialogue_sprite_list.append(self.dialogue_speaker)

        # Управление
        self.left_pressed = self.right_pressed = self.up_pressed = self.down_pressed = False

        # Снег
        self.snowflake_list = arcade.SpriteList()
        self.snowflake_spawn_chance = 0.2
        self.snowflake_speed_min, self.snowflake_speed_max = 1.5, 4.0
        self.snowflake_drift_min, self.snowflake_drift_max = -5.0, 0.7
        self.snowflake_wobble_speed, self.snowflake_wobble_amount = 0.03, 0.8
        self.snowflake_texture = arcade.make_soft_square_texture(8, arcade.color.WHITE_SMOKE, 255)
        
        # Магазин
        shop_texture = arcade.load_texture('resources/buildings/shop.png')
        self.shop = arcade.Sprite(shop_texture, scale=8.0)
        self.shop.center_x = -185
        self.shop.center_y = 2415
        self.shop_list = arcade.SpriteList()
        self.shop_list.append(self.shop)

        # Пришелец Sor
        sor_texture = arcade.load_texture('resources/persons/alien_sor/alien_sor_not_animated.png')
        self.sor = arcade.Sprite(sor_texture, scale=4.0)
        self.sor.center_x = -670
        self.sor.center_y = 2380
        self.sor_list = arcade.SpriteList()
        self.sor_list.append(self.sor)

        # Пришелец Ness (У магазина)
        ness1_texture = arcade.load_texture('resources/persons/alien_ness/ness_in_spacesuit_darked.png')
        self.ness1 = arcade.Sprite(ness1_texture, scale=3.0)
        self.ness1.center_x = -50
        self.ness1.center_y = 2020
        self.ness1.width = 120
        self.ness1.height = 120
        self.ness1_list = arcade.SpriteList()
        self.ness1_list.append(self.ness1)

        # Пришелец Ness (У дороги)
        ness2_texture = arcade.load_texture('resources/persons/alien_ness/ness_in_spacesuit_darked.png')
        self.ness2 = arcade.Sprite(ness2_texture, scale=3.0)
        self.ness2.center_x = -2180
        self.ness2.center_y = -850
        self.ness2.width = 120
        self.ness2.height = 120
        self.ness2_list = arcade.SpriteList()
        self.ness2_list.append(self.ness2)

        # Диалоговые состояния
        self.dialogue_active = False
        self.dialogue_text = ""

    def update_snowflakes(self):
        if random.random() < self.snowflake_spawn_chance:
            snowflake = arcade.Sprite(self.snowflake_texture)
            snowflake.scale = random.uniform(0.5, 1.5)
            snowflake.center_x = random.uniform(
                self.camera.position.x - self.window.width // 2 - 500,
                self.camera.position.x + self.window.width // 2 + 500
            )
            snowflake.center_y = self.camera.position.y + self.window.height // 2 + 500
            snowflake.speed = random.uniform(self.snowflake_speed_min, self.snowflake_speed_max)
            snowflake.drift = random.uniform(self.snowflake_drift_min, self.snowflake_drift_max)
            snowflake.base_x = snowflake.center_x
            snowflake.wobble_offset = 0.0
            self.snowflake_list.append(snowflake)

        for snowflake in self.snowflake_list:
            snowflake.center_y -= snowflake.speed
            snowflake.center_x += snowflake.drift
            snowflake.wobble_offset += self.snowflake_wobble_speed
            snowflake.center_x = snowflake.base_x + math.sin(snowflake.wobble_offset) * self.snowflake_wobble_amount
            if snowflake.center_y < self.camera.position.y - self.window.height // 2 - 500:
                snowflake.remove_from_sprite_lists()


    def on_draw(self):
        self.clear()
        self.camera.use()

        # Отрисовка элементов игрового мира
        self.bg_list.draw(pixelated=True)
        self.wall_list.draw()
        self.shop_list.draw(pixelated=True)
        self.sor_list.draw(pixelated=True)
        self.ness1_list.draw(pixelated=True)
        self.ness2_list.draw(pixelated=True)
        self.snowflake_list.draw()
        self.alien_list.draw(pixelated=True)
        self.arrow_list.draw(pixelated=True)

        # Отрисовка диалогового окна
        if hasattr(self, 'dialogue_active') and self.dialogue_active:
            self.dialogue_sprite_list.draw(pixelated=True)
            self.dialogue_text_sprite.draw()

        # Диалоговое окно
        if hasattr(self, 'dialogue_active') and self.dialogue_active:
            self.dialogue_sprite_list.draw(pixelated=True)
            self.dialogue_text_sprite.draw()

        # Текст с координатами
        if hasattr(self, 'coordinates_text'):
            self.coordinates_text.draw()

        # Экран паузы
        if self.paused:
            self.overlay_rectangle.center_x = self.camera.position.x
            self.overlay_rectangle.center_y = self.camera.position.y
            self.overlay.draw()
            self.pause_text.x = self.camera.position.x
            self.pause_text.y = self.camera.position.y + 100
            self.pause_text.draw()

    def on_update(self, delta_time):
        if self.paused:
            return

        self.update_snowflakes()
        self.auto_save(delta_time)

        self.alien.change_x = 0
        if self.left_pressed and not self.right_pressed:
            self.alien.change_x = -settings.PLAYER_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.alien.change_x = settings.PLAYER_SPEED

        self.alien.change_y = 0
        if self.up_pressed and not self.down_pressed:
            self.alien.change_y = settings.PLAYER_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.alien.change_y = -settings.PLAYER_SPEED

        self.alien_list.update()
        self.alien.update_animation(delta_time)

        # коллизия со стенами
        if arcade.check_for_collision_with_list(self.alien, self.wall_list):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Коллизии с Ness
        if arcade.check_for_collision(self.alien, self.ness1):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y
        if arcade.check_for_collision(self.alien, self.ness2):
            self.alien.center_x -= self.alien.change_x
            self.alien.center_y -= self.alien.change_y

        # Камера
        camera_x = self.alien.center_x
        camera_y = self.alien.center_y + settings.height * 0.2
        self.camera.position = camera_x, camera_y

        # # Координаты (Dev Func)
        # if not hasattr(self, 'coordinates_text'):
        #     self.coordinates_text = arcade.Text(
        #         "", x=0, y=0, color=arcade.color.WHITE, font_size=24,
        #         anchor_x="right", anchor_y="top"
        #     )
        # self.coordinates_text.text = f"X: {int(self.alien.center_x)}, Y: {int(self.alien.center_y)}"
        # self.coordinates_text.x = camera_x + settings.width // 2 - 20
        # self.coordinates_text.y = camera_y + settings.height // 2 - 20

        # Диалоговое окно
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.center_x = camera_x
            self.dialogue_box.bottom = camera_y - (settings.height // 2)
            self.dialogue_text_sprite.position = (
                self.dialogue_box.center_x + 80, self.dialogue_box.center_y
            )
            self.dialogue_speaker.left = self.dialogue_box.left + 20
            self.dialogue_speaker.bottom = self.dialogue_box.bottom + 20

        # Стрелка
        if self.show_arrow:
            self.arrow.center_x = self.alien.center_x
            self.arrow.center_y = self.alien.center_y + 70

            target_x = -205
            target_y = 2110

            dx = target_x - self.alien.center_x
            dy = target_y - self.alien.center_y
            angle = math.degrees(math.atan2(dy, dx))

            self.arrow.angle = -angle + 90

        # Диалог с Ness 1
        distance_to_ness1 = arcade.get_distance_between_sprites(self.alien, self.ness1)
        if not hasattr(self, 'dialogue_active'):
            self.dialogue_active = False
            self.dialogue_text = ""

        if distance_to_ness1 < 150 and not self.dialogue_active:
            self.dialogue_active = True
            self.dialogue_text = "К сожалению магазин пока закрыт, поэтому мы останемся без маскировки("
            self.dialogue_text_sprite.text = self.dialogue_text
            self.dialogue_speaker.texture = arcade.load_texture('resources/persons/alien_ness/ness_in_spacesuit.png')
        elif distance_to_ness1 >= 150 and self.dialogue_active and self.dialogue_text == "К сожалению магазин пока закрыт, поэтому мы останемся без маскировки(":
            self.dialogue_active = False
            self.dialogue_text = ""
            self.dialogue_text_sprite.text = self.dialogue_text

            self.show_arrow = False
            self.arrow.alpha = 0

        # Диалог с Ness 2
        distance_to_ness2 = arcade.get_distance_between_sprites(self.alien, self.ness2)
        if distance_to_ness2 < 150 and not self.dialogue_active:
            self.dialogue_active = True
            self.dialogue_text = "Нам нужно быть осторожнее! Здесь живут люди, надо быстрее найти магазин одежды, чтобы маскироваться!"
            self.dialogue_text_sprite.text = self.dialogue_text
            self.dialogue_speaker.texture = arcade.load_texture('resources/persons/alien_ness/ness_in_spacesuit.png')
        elif distance_to_ness2 >= 150 and self.dialogue_active and self.dialogue_text == "Нам нужно быть осторожнее! Здесь живут люди, надо быстрее найти магазин одежды, чтобы маскироваться!":
            self.dialogue_active = False
            self.dialogue_text = ""
            self.dialogue_text_sprite.text = self.dialogue_text

            self.show_arrow = True
            self.arrow.alpha = 255

        # Выход из локации
        if self.alien.center_x == -4200 and self.alien.center_y == -1000:
            self.window.switch_view("game")

    def save_game(self):
        save_data = {
            'player_position': {
                'x': self.alien.center_x,
                'y': self.alien.center_y
            },
            'story_phases': self.story_phases,
            'timestamp': time.time()
        }
        os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

    def load_save(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    return save_data.get('player_position')
        except Exception as e:
            print(f"Failed to load save: {e}")
        return None
        
    def load_story_phases(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    return save_data.get('story_phases', {})
        except Exception as e:
            print(f"Failed to load story phases: {e}")
        return {}

    def auto_save(self, delta_time):
        self.last_save_time += delta_time
        if self.last_save_time >= self.save_interval:
            self.save_game()
            print(f"Сохранение создано: X={self.alien.center_x}, Y={self.alien.center_y}")
            self.last_save_time = 0

    def delete_save(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)

            self.story_phases = {}

            self.alien.center_x = -4000
            self.alien.center_y = -1000

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            if self.paused:
                self.overlay_rectangle.center_x = self.camera.position.x
                self.overlay_rectangle.center_y = self.camera.position.y
                self.pause_text.x = self.camera.position.x
                self.pause_text.y = self.camera.position.y + 100
        elif key == arcade.key.P:
            self.delete_save()
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
