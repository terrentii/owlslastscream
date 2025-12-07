import arcade
from src.windows.base_window import BaseWindow


def main():
    """Запуск игры"""
    window = BaseWindow()
    window.switch_view("start")  # Начинаем с стартового экрана
    arcade.run()


if __name__ == "__main__":
    main()
