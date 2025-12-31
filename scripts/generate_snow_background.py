from PIL import Image, ImageDraw
import random

def create_snow_background_with_spruces(
    background_path: str,
    spruce_paths: list,
    output_path: str,
    num_spruces: int = 100,
    safe_zone_radius: int = 400
):
    """
    Создает фоновое изображение с добавлением елок.
    В центральной области (safe_zone_radius) елки не размещаются.
    
    Args:
        background_path: путь к фоновому изображению (snow_blank.png)
        spruce_paths: список путей к изображениям елок
        output_path: путь для сохранения результата
        num_spruces: количество елок для размещения
        safe_zone_radius: радиус центральной области без елок
    """
    # Открываем фоновое изображение
    # Строим абсолютный путь от текущего расположения скрипта
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    background_full_path = os.path.join(base_dir, "..", background_path)
    background = Image.open(background_full_path).convert("RGBA")
    bg_width, bg_height = background.size
    
    # Создаем новое изображение для отрисовки
    result = background.copy()
    
    for _ in range(num_spruces):
        # Выбираем случайную елку
        spruce_path = random.choice(spruce_paths)
        spruce_full_path = os.path.join(base_dir, "..", spruce_path)
        spruce = Image.open(spruce_full_path).convert("RGBA")
        
        # Масштабируем елку (если нужно)
        scale = random.uniform(0.3, 0.6)
        spruce = spruce.resize((
            int(spruce.width * scale),
            int(spruce.height * scale)
        ))
        
        # Определяем центральную безопасную зону
        center_x = bg_width // 2
        center_y = bg_height // 2
        
        # Генерируем случайные координаты вне безопасной зоны
        while True:
            x = random.randint(0, bg_width - spruce.width)
            y = random.randint(0, bg_height - spruce.height)
            
            # Проверяем, находится ли центр елки в безопасной зоне
            spruce_center_x = x + spruce.width // 2
            spruce_center_y = y + spruce.height // 2
            
            distance_to_center = ((spruce_center_x - center_x) ** 2 + (spruce_center_y - center_y) ** 2) ** 0.5
            
            if distance_to_center >= safe_zone_radius:
                break
        
        # Накладываем елку на фон
        result.paste(spruce, (x, y), spruce)
    
    # Сохраняем результат
    output_full_path = os.path.join(base_dir, "..", output_path)
    result.save(output_full_path)
    print(f"Фоновое изображение сохранено: {output_path}")

if __name__ == "__main__":
    background_path = "resources/background/snow_blank.png"
    spruce_paths = [
        "resources/background/outer_space/spruce_1.png",
        "resources/background/outer_space/spruce_2.png",
        "resources/background/outer_space/spruce_3.png"
    ]
    output_path = "resources/background/snow_with_spruces.png"

    create_snow_background_with_spruces(
        background_path=background_path,
        spruce_paths=spruce_paths,
        output_path=output_path,
        num_spruces=1000,
        safe_zone_radius=700
    )