import tkinter as tk
from tkinter import filedialog
import numpy as np
import math


class Polyhedron3D:
    """Класс для загрузки и проекции модели в формате OBJ."""

    def __init__(self, filename):
        self.vertices = []
        self.edges = []
        self.load_from_obj(filename)

    def load_from_obj(self, filename):
        """Загрузка модели из файла формата Wavefront OBJ."""
        with open(filename, "r") as file:
            for line in file:
                if line.startswith("v "):
                    _, x, y, z = line.strip().split()
                    self.vertices.append([float(x), float(y), float(z)])
                elif line.startswith("f ") or line.startswith("l "):
                    indices = [
                        int(i.split("/")[0]) - 1 for i in line.strip().split()[1:]
                    ]
                    for i in range(len(indices) - 1):
                        self.edges.append((indices[i], indices[i + 1]))

    def rotate(self, angle_x, angle_y, angle_z):
        """Вращение модели вокруг осей X, Y и Z."""
        # Матрицы поворота для каждой оси
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)

        rotation_x = np.array([[1, 0, 0], [0, cos_x, -sin_x], [0, sin_x, cos_x]])
        rotation_y = np.array([[cos_y, 0, sin_y], [0, 1, 0], [-sin_y, 0, cos_y]])
        rotation_z = np.array([[cos_z, -sin_z, 0], [sin_z, cos_z, 0], [0, 0, 1]])

        for i in range(len(self.vertices)):
            self.vertices[i] = np.dot(rotation_x, self.vertices[i])
            self.vertices[i] = np.dot(rotation_y, self.vertices[i])
            self.vertices[i] = np.dot(rotation_z, self.vertices[i])

    def project(self, width, height, scale=100):
        """Проекция 3D-модели на 2D-плоскость."""
        projected_points = []
        for vertex in self.vertices:
            # Простейшая перспективная проекция
            z_offset = vertex[2] + 5  # отодвигаем модель от камеры
            f = scale / (z_offset if z_offset != 0 else 0.1)
            x = int(width / 2 + f * vertex[0])
            y = int(height / 2 - f * vertex[1])
            projected_points.append((x, y))
        return projected_points


class ModelViewer:
    """Класс для отображения модели в Tkinter окне."""

    def __init__(self, root):
        self.root = root
        self.root.title("3D OBJ Viewer")
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack()
        self.model = None
        self.angle_x, self.angle_y, self.angle_z = 0, 0, 0

        # Кнопки управления
        load_button = tk.Button(root, text="Load Model", command=self.load_model)
        load_button.pack()

        rotate_x_button = tk.Button(root, text="Rotate X", command=self.rotate_x)
        rotate_x_button.pack(side=tk.LEFT)

        rotate_y_button = tk.Button(root, text="Rotate Y", command=self.rotate_y)
        rotate_y_button.pack(side=tk.LEFT)

        rotate_z_button = tk.Button(root, text="Rotate Z", command=self.rotate_z)
        rotate_z_button.pack(side=tk.LEFT)

    def load_model(self):
        """Открытие файла OBJ и загрузка модели."""
        filename = filedialog.askopenfilename(
            filetypes=[("OBJ and Text Files", "*.obj *.txt")]
        )
        if filename:
            self.model = Polyhedron3D(filename)
            self.draw_model()

    def rotate_x(self):
        """Вращение модели вокруг оси X."""
        if self.model:
            self.angle_x += math.pi / 18  # 10 градусов
            self.model.rotate(self.angle_x, 0, 0)
            self.draw_model()

    def rotate_y(self):
        """Вращение модели вокруг оси Y."""
        if self.model:
            self.angle_y += math.pi / 18  # 10 градусов
            self.model.rotate(0, self.angle_y, 0)
            self.draw_model()

    def rotate_z(self):
        """Вращение модели вокруг оси Z."""
        if self.model:
            self.angle_z += math.pi / 18  # 10 градусов
            self.model.rotate(0, 0, self.angle_z)
            self.draw_model()

    def draw_model(self):
        """Отрисовка модели на холсте."""
        if not self.model:
            return
        self.canvas.delete("all")
        width, height = 600, 400
        points = self.model.project(width, height)

        # Рисуем рёбра модели
        for edge in self.model.edges:
            start, end = edge
            x1, y1 = points[start]
            x2, y2 = points[end]
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    viewer = ModelViewer(root)
    root.mainloop()
