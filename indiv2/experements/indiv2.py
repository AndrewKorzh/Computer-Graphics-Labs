import tkinter as tk
import numpy as np

# Размеры окна
WIDTH, HEIGHT = 800, 600

# Определим начальные цвета
WHITE = "#FFFFFF"
BLACK = "#000000"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
LIGHT_GRAY = "#D3D3D3"
DARK_GRAY = "#505050"

# Параметры куба (комнаты)
CUBE_SIZE = 300
CUBE_X, CUBE_Y = WIDTH // 2 - CUBE_SIZE // 2, HEIGHT // 2 - CUBE_SIZE // 2

# Источник света
light_position = np.array([WIDTH // 2, HEIGHT // 4])

# Массив объектов внутри комнаты (кубы и шары)
objects = []


# Перспективная проекция 3D в 2D
def project_3d_to_2d(x, y, z, width, height):
    fov = 500  # поле зрения
    z_offset = 1000  # положение камеры
    scale = fov / (z + z_offset)
    x2d = int(x * scale + width // 2)
    y2d = int(-y * scale + height // 2)
    return x2d, y2d


# Определим класс для объектов
class Object:
    def __init__(
        self, obj_type, x, y, z, size, color, reflective=False, transparent=False
    ):
        self.obj_type = obj_type
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.color = color
        self.reflective = reflective
        self.transparent = transparent

    def draw(self, canvas):
        x2d, y2d = project_3d_to_2d(self.x, self.y, self.z, WIDTH, HEIGHT)
        if self.obj_type == "cube":
            half_size = self.size // 2
            # Рисуем 3D куб, используя проекцию
            canvas.create_rectangle(
                x2d - half_size,
                y2d - half_size,
                x2d + half_size,
                y2d + half_size,
                fill=self.color,
            )
        elif self.obj_type == "sphere":
            half_size = self.size // 2
            # Рисуем 3D шар
            canvas.create_oval(
                x2d - half_size,
                y2d - half_size,
                x2d + half_size,
                y2d + half_size,
                fill=self.color,
            )

    def toggle_reflection(self):
        self.reflective = not self.reflective

    def toggle_transparency(self):
        self.transparent = not self.transparent


# Функция рисования куба (комнаты)
def draw_cube(canvas):
    # Нарисуем стенки куба с гранями
    cube_points = [
        [-CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2],
        [CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2],
        [CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2],
        [-CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2],
        [-CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2],
        [CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2],
        [CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2],
        [-CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2],
    ]

    # Применяем проекцию для всех вершин
    projected_points = [
        project_3d_to_2d(x, y, z, WIDTH, HEIGHT) for x, y, z in cube_points
    ]

    # Соединяем точки, чтобы нарисовать грани куба
    for i, (x1, y1) in enumerate(projected_points):
        for j in range(i + 1, len(projected_points)):
            x2, y2 = projected_points[j]
            canvas.create_line(x1, y1, x2, y2, fill=LIGHT_GRAY)


# Функция рисования света
def draw_light(canvas):
    canvas.create_oval(
        light_position[0] - 10,
        light_position[1] - 10,
        light_position[0] + 10,
        light_position[1] + 10,
        fill=WHITE,
    )


# Функция для отрисовки сцены
def draw_scene(canvas):
    canvas.delete("all")  # Очистить экран

    # Рисуем комнату (куб)
    draw_cube(canvas)

    # Рисуем источник света
    draw_light(canvas)

    # Рисуем объекты внутри комнаты
    for obj in objects:
        obj.draw(canvas)


# Главная функция
def main():
    root = tk.Tk()
    root.title("Cornwell Room Scene")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BLACK)
    canvas.pack()

    # Добавляем объекты в комнату
    objects.append(Object("cube", 100, 100, 100, 50, RED))
    objects.append(Object("sphere", 200, 150, 100, 50, BLUE))
    objects.append(Object("cube", 300, 200, 50, 50, GREEN))

    # Главный цикл отрисовки
    draw_scene(canvas)

    # Запускаем главный цикл Tkinter
    root.mainloop()


if __name__ == "__main__":
    main()
