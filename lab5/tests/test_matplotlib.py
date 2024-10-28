import matplotlib.pyplot as plt
import numpy as np
import random

# Основные параметры для удобства настройки
default_iterations = 0  # Число итераций
default_start_direction = 90  # Начальный угол поворота
default_angle = 60  # Угол поворота
index = 0
iterations = [i for i in range(1, 6)]

# Определение L-систем
l_systems = [
    # Снежинка Коха
    {
        "atom": "F++F++F",
        "rules": {"F": "F-F++F-F"},
        "angle": 60,
        "start_direction": 0,
    },
    # Снежинка Коха
    {
        "atom": "FXF−−FF−−FF",
        "rules": {"F": "FF", "X": "−−FXF++FXF++FXF−−"},
        "angle": 60,
        "start_direction": 0,
    },
]


def generate_l_system(axiom, rules, iterations):
    """Генерирует строку L-системы после заданного количества итераций."""
    for _ in range(iterations):
        result = "".join(rules.get(char, char) for char in axiom)
        axiom = result
    return axiom


def points_l_system(l_system_index):
    # Получаем параметры выбранной L-системы
    system = l_systems[l_system_index]
    axiom = system["atom"]
    angle = system["angle"]
    direction = system["start_direction"]
    if default_iterations:
        iterations = default_iterations
    else:
        iterations = system["iterations"]

    rules = system["rules"]

    # Генерируем строку L-системы
    instructions = generate_l_system(axiom, rules, iterations)

    # Начальные условия для отрисовки
    x, y = 0, 0
    stack = []
    points = [(x, y)]
    current_angle = np.radians(direction)

    for char in instructions:
        if char == "F":
            # Двигаемся вперед и сохраняем новую точку
            x_new = x + np.cos(current_angle)
            y_new = y + np.sin(current_angle)
            points.append((x_new, y_new))
            x, y = x_new, y_new  # Обновляем текущую позицию
        elif char == "+":
            # Поворачиваем на угол (вправо)
            current_angle -= np.radians(angle)
        elif char == "-":
            # Поворачиваем на угол (влево)
            current_angle += np.radians(angle)
        elif char == "[":
            # Сохраняем текущую позицию и угол
            stack.append((x, y, current_angle))
        elif char == "]":
            # Восстанавливаем сохраненную позицию и угол
            x, y, current_angle = stack.pop()
            points.append((x, y))

    return points


def draw_by_points(points):
    # Приведение координат к масштабу окна
    points = np.array(points)
    points -= points.min(axis=0)
    points /= points.max(axis=0)

    # Построение фрактала
    plt.figure(figsize=(8, 8))
    plt.plot(points[:, 0], points[:, 1], color="green")
    plt.axis("equal")
    plt.axis("off")

    plt.show()


def draw_iter(l_system_index):
    for ell in iterations:
        global default_iterations
        default_iterations = ell
        print(f"iter = {ell}")
        points = points_l_system(l_system_index=l_system_index)
        draw_by_points(points=points)


draw_iter(index)
