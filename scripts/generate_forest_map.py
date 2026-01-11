from PIL import Image, ImageDraw
import random
import math
import os

def create_forest_map_with_roads(
    background_path: str,
    spruce_paths: list,
    output_path: str,
    num_spruces: int = 1000,
    safe_zone_radius: int = 200,
    road_width: int = 80,
    road_length: int = 1000
):
    """
    Создает карту леса с центральной безопасной зоной и тремя дорогами.
    
    Args:
        background_path: путь к фоновому изображению (snow_blank.png)
        spruce_paths: список путей к изображениям елок
        output_path: путь для сохранения результата
        num_spruces: количество елок для размещения
        safe_zone_radius: радиус центральной области без елок
        road_width: ширина дорог
        road_length: длина дорог от центра
    """
    # Открываем фоновое изображение
    base_dir = os.path.dirname(os.path.abspath(__file__))
    background_full_path = os.path.join(base_dir, "..", background_path)
    background = Image.open(background_full_path).convert("RGBA")
    bg_width, bg_height = background.size
    
    # Создаем новое изображение для отрисовки
    result = background.copy()
    
    # Определяем центр изображения
    center_x = bg_width // 2
    center_y = bg_height // 2
    
    # Углы для трех дорог (равномерно распределены по кругу)
    road_angles = [0, 120, 240]  # в градусах
    
    def is_in_safe_zone(x, y, spruce_width, spruce_height):
        """Проверяет, находится ли елка в безопасной зоне или на дороге"""
        # Центр елки
        spruce_center_x = x + spruce_width // 2
        spruce_center_y = y + spruce_height // 2
        
        # Проверка центральной безопасной зоны
        distance_to_center = ((spruce_center_x - center_x) ** 2 + (spruce_center_y - center_y) ** 2) ** 0.5
        if distance_to_center <= safe_zone_radius:
            return True
        
        # Проверка каждой дороги
        for angle in road_angles:
            # Преобразуем угол в радианы
            angle_rad = math.radians(angle)
            
            # Вычисляем направляющий вектор дороги
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            
            # Вектор от центра до точки
            to_point_x = spruce_center_x - center_x
            to_point_y = spruce_center_y - center_y
            
            # Длина проекции вектора на дорогу
            projection = to_point_x * dx + to_point_y * dy
            
            # Если проекция положительна и в пределах длины дороги
            if 0 <= projection <= road_length:
                # Перпендикулярное расстояние до дороги
                perp_distance = abs(to_point_x * dy - to_point_y * dx)
                if perp_distance <= road_width // 2:
                    return True
        
        return False
    
    placed_spruces = 0
    attempts = 0
    max_attempts = num_spruces * 10  # Ограничение попыток
    
    while placed_spruces < num_spruces and attempts < max_attempts:
        attempts += 1
        
        # Выбираем случайную елку
        spruce_path = random.choice(spruce_paths)
        spruce_full_path = os.path.join(base_dir, "..", spruce_path)
        spruce = Image.open(spruce_full_path).convert("RGBA")
        
        # Масштабируем елку с высоким качеством
        scale = random.uniform(0.07, 0.1)
        new_width = int(spruce.width * scale)
        new_height = int(spruce.height * scale)
        spruce = spruce.resize((new_width, new_height), Image.LANCZOS)
        
        # Генерируем случайные координаты
        x = random.randint(0, bg_width - spruce.width)
        y = random.randint(0, bg_height - spruce.height)
        
        # Проверяем, находится ли елка в безопасной зоне или на дороге
        if not is_in_safe_zone(x, y, spruce.width, spruce.height):
            # Накладываем елку на фон
            result.paste(spruce, (x, y), spruce)
            placed_spruces += 1
    
    print(f"Успешно размещено {placed_spruces} елок из {num_spruces} запрошенных")
    if attempts >= max_attempts:
        print(f"Достигнуто максимальное количество попыток ({max_attempts})")

    # Сохраняем результат
    output_full_path = os.path.join(base_dir, "..", output_path)
    result.save(output_full_path)
    print(f"Карта леса сохранена: {output_path}")

if __name__ == "__main__":
    background_path = "resources/background/snow_blank.png"
    spruce_paths = [
        "resources/background/outer_space/spruce_1.png",
        "resources/background/outer_space/spruce_2.png",
        "resources/background/outer_space/spruce_3.png",
        "resources/background/outer_space/spruce_4.png"
    ]
    output_path = "resources/background/forest_map.png"

    create_forest_map_with_roads(
        background_path=background_path,
        spruce_paths=spruce_paths,
        output_path=output_path,
        num_spruces=1000,
        safe_zone_radius=200,
        road_width=80,
        road_length=1000
    )