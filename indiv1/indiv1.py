import numpy as np
import matplotlib.pyplot as plt


def cross(o, a, b):
    """Вычисляет векторное произведение (o -> a) x (o -> b)"""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points):
    """Строит выпуклую оболочку методом Эндрю"""
    # Сортируем точки по x, затем по y
    points = sorted(points, key=lambda p: (p[0], p[1]))

    # Обрабатываем нижнюю оболочку
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Обрабатываем верхнюю оболочку
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Убираем последнюю точку каждого списка, так как она повторяется в конце другого
    return lower[:-1] + upper[:-1]


np.random.seed(0)
points = np.random.rand(1000, 2)

hull = convex_hull(points)

plt.figure(figsize=(8, 6))
plt.scatter(points[:, 0], points[:, 1], color="blue", label="Точки")
plt.scatter(
    np.array(hull)[:, 0], np.array(hull)[:, 1], color="red", label="Выпуклая оболочка"
)

# Соединяем точки выпуклой оболочки
hull = np.array(hull + [hull[0]])  # Замыкаем оболочку
plt.plot(hull[:, 0], hull[:, 1], color="red")

plt.title("Выпуклая оболочка методом Эндрю")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid()
plt.show()
