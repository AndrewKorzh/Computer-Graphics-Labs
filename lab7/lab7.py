import math
import tkinter as tk
import numpy as np
from tkinter import filedialog, messagebox
from lab6 import (
    Polyhedron3D,
    Camera,
    PolyhedronDrawer,
    get_progection_matrix,
    get_polyhedron,
    MainWindow,
)


def load_from_obj(filepath):
    """
    Загрузка модели из файла OBJ.

    """
    vertices = []
    faces = []
    edges = set()

    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "v":  # Вершина
                vertices.append(list(map(float, parts[1:4])))
            elif parts[0] == "f":  # Грань
                face = [int(idx.split("/")[0]) - 1 for idx in parts[1:]]
                faces.append(face)
            elif parts[0] == "l":  # Ребро
                edge = [int(idx) - 1 for idx in parts[1:]]
                for i in range(len(edge) - 1):
                    edges.add((edge[i], edge[i + 1]))

    # Если есть грани, извлекаем рёбра из них
    for face in faces:
        for i in range(len(face)):
            edges.add((face[i], face[(i + 1) % len(face)]))

    return Polyhedron3D(vertices, list(edges))


def save_to_obj(polyhedron, filepath):
    """
    Сохранение модели в формате OBJ (только вершины и рёбра).

    :param filepath: Путь к файлу для сохранения.
    """
    with open(filepath, "w") as file:
        # Записываем вершины
        for vertex in polyhedron.vertices:
            # Если вершина не содержит координаты Z, добавляем её как 0.0
            if len(vertex) == 2:
                x, y = vertex
                z = 0.0
            elif len(vertex) == 3:
                x, y, z = vertex
            else:
                raise ValueError(f"Некорректная вершина: {vertex}")

            file.write(f"v {x} {y} {z}\n")

        # Записываем рёбра
        for edge in polyhedron.edges:
            # Убедимся, что рёбра содержат только существующие индексы
            start, end = edge
            if start >= len(polyhedron.vertices) or end >= len(polyhedron.vertices):
                raise ValueError(f"Некорректное ребро: {edge}")

            # Добавляем 1 к индексам для соответствия формату OBJ
            file.write(f"l {start + 1} {end + 1}\n")


class NewMainWindow(MainWindow):
    def __init__(self, root: tk.Tk):
        super().__init__(root)
        row_count = 11

        tk.Button(root, text="Load OBJ File", command=self.load_obj).grid(
            row=row_count, column=3
        )
        tk.Button(root, text="Save OBJ File", command=self.save_obj).grid(
            row=row_count, column=4
        )

        row_count += 1

        tk.Label(self.root, text="Points (x, y, z):").grid(
            row=row_count, column=0, padx=5, pady=5
        )
        self.points_entry = tk.Entry(self.root, width=40)
        self.points_entry.grid(row=row_count, column=1, padx=5, pady=5)

        row_count += 1

        # Поле для оси
        tk.Label(self.root, text="Axis of Rotation (x, y, z):").grid(
            row=row_count, column=0, padx=5, pady=5
        )
        self.axis_entry = tk.Entry(self.root, width=10)
        self.axis_entry.grid(row=row_count, column=1, padx=5, pady=5)

        # row_count += 1

        # Поле для количества сегментов
        tk.Label(self.root, text="Number of Segments:").grid(
            row=row_count, column=2, padx=5, pady=5
        )
        self.segments_entry = tk.Entry(self.root, width=10)
        self.segments_entry.grid(row=row_count, column=3, padx=5, pady=5)

        # row_count += 1

        # Кнопка для генерации вращённой фигуры
        self.generate_button = tk.Button(
            self.root, text="Generate Revolved Shape", command=self.generate_shape
        )
        self.generate_button.grid(row=row_count, column=5, columnspan=2, padx=5, pady=5)

        row_count += 1

        self.x0_var = tk.DoubleVar(value=-5)
        self.x1_var = tk.DoubleVar(value=5)
        self.y0_var = tk.DoubleVar(value=-5)
        self.y1_var = tk.DoubleVar(value=5)
        self.num_segments_var = tk.IntVar(value=10)
        self.function_var = tk.StringVar(value="sin(sqrt(x^2 + y^2))")
        self.functions = {
            "sin(sqrt(x^2 + y^2))": self.surface_sin,
            "x^2 - y^2": self.surface_parabola,
            "cos(x) * sin(y)": self.surface_cos_sin,
        }

        tk.Label(self.root, text="X0:").grid(
            row=row_count, column=0, padx=5, pady=5, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.x0_var).grid(
            row=row_count, column=1, padx=5, pady=5
        )

        tk.Label(self.root, text="X1:").grid(
            row=row_count, column=2, padx=5, pady=5, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.x1_var).grid(
            row=row_count, column=3, padx=5, pady=5
        )

        row_count += 1

        tk.Label(self.root, text="Y0:").grid(
            row=row_count, column=0, padx=5, pady=5, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.y0_var).grid(
            row=row_count, column=1, padx=5, pady=5
        )

        tk.Label(self.root, text="Y1:").grid(
            row=row_count, column=2, padx=5, pady=5, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.y1_var).grid(
            row=row_count, column=3, padx=5, pady=5
        )

        row_count += 1

        tk.Label(self.root, text="Разбиения:").grid(
            row=row_count, column=0, padx=5, pady=5, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.num_segments_var).grid(
            row=row_count, column=1, padx=5, pady=5
        )

        row_count += 1

        tk.Label(self.root, text="Функция:").grid(
            row=row_count, column=0, padx=5, pady=5, sticky="w"
        )
        tk.OptionMenu(self.root, self.function_var, *self.functions.keys()).grid(
            row=row_count, column=1, padx=5, pady=5
        )

        # row_count += 1

        # Кнопка для построения поверхности
        tk.Button(
            self.root, text="Построить поверхность", command=self.generate_surface
        ).grid(row=row_count, column=6, columnspan=2, pady=10)

        self.root.bind("<MouseWheel>", self.on_mouse_wheel)

    def load_obj(self):
        filepath = filedialog.askopenfilename(filetypes=[("OBJ Files", "*.obj")])
        if filepath:
            self.polyhedron = load_from_obj(filepath)
            self.redraw()
            messagebox.showinfo("Success", "OBJ file loaded successfully!")

    def save_obj(self):
        if not self.polyhedron:
            messagebox.showerror("Error", "No polyhedron to save!")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".obj", filetypes=[("OBJ Files", "*.obj")]
        )
        if filepath:
            save_to_obj(self.polyhedron, filepath)
            messagebox.showinfo("Success", "OBJ file saved successfully!")

    def parse_points(self):
        """Парсит введённые пользователем точки."""
        try:
            points = [
                list(map(float, point.split(",")))
                for point in self.points_entry.get().strip().split(";")
            ]
            return points
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Points should be in the format: x,y,z;x,y,z"
            )
            return None

    def generate_shape(self):
        """Генерирует вращённую фигуру на основе введённых данных."""
        points = self.parse_points()
        if not points:
            return

        axis = self.axis_entry.get().strip().lower()
        if axis not in ("x", "y", "z"):
            messagebox.showerror("Invalid Axis", "Axis should be one of: x, y, z")
            return

        try:
            num_segments = int(self.segments_entry.get())
            if num_segments <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Segments", "Number of segments should be a positive integer"
            )
            return

        # Генерация вращённой фигуры
        self.polyhedron = self.generate_revolved_shape(points, axis, num_segments)
        self.redraw()
        messagebox.showinfo(
            "Success", f"Shape generated with {len(self.polyhedron.vertices)} vertices!"
        )

    def generate_revolved_shape(self, points, axis, num_segments):
        angle_step = 2 * math.pi / num_segments
        vertices = []
        faces = []

        for i in range(num_segments):
            angle = i * angle_step
            if axis == "z":
                rotation_matrix = np.array(
                    [
                        [math.cos(angle), -math.sin(angle), 0],
                        [math.sin(angle), math.cos(angle), 0],
                        [0, 0, 1],
                    ]
                )
            elif axis == "x":
                rotation_matrix = np.array(
                    [
                        [1, 0, 0],
                        [0, math.cos(angle), -math.sin(angle)],
                        [0, math.sin(angle), math.cos(angle)],
                    ]
                )
            elif axis == "y":
                rotation_matrix = np.array(
                    [
                        [math.cos(angle), 0, math.sin(angle)],
                        [0, 1, 0],
                        [-math.sin(angle), 0, math.cos(angle)],
                    ]
                )
            else:
                rotation_matrix = np.eye(3)

            for point in points:
                rotated_point = np.dot(rotation_matrix, point)
                vertices.append(rotated_point.tolist())

            if i > 0:
                for j in range(len(points) - 1):
                    faces.append(
                        [
                            i * len(points) + j,
                            (i - 1) * len(points) + j,
                            (i - 1) * len(points) + (j + 1),
                            i * len(points) + (j + 1),
                        ]
                    )

        # Рассчитываем рёбра
        edges = set()
        for face in faces:
            for i in range(len(face)):
                edges.add((face[i], face[(i + 1) % len(face)]))

        return Polyhedron3D(vertices, list(edges))

    def generate_surface(self):
        # Чтение параметров
        x0, x1 = self.x0_var.get(), self.x1_var.get()
        y0, y1 = self.y0_var.get(), self.y1_var.get()
        num_segments = self.num_segments_var.get()
        func = self.functions[self.function_var.get()]

        # Генерация поверхности
        self.polyhedron = self.generate_surface_mesh(
            x0, x1, y0, y1, num_segments, num_segments, func
        )
        self.redraw()

    def generate_surface_mesh(self, x0, x1, y0, y1, nx, ny, func):
        """Генерация сетки поверхности."""
        vertices = []
        edges = []

        # Шаг по X и Y
        dx = (x1 - x0) / nx
        dy = (y1 - y0) / ny

        # Генерация вершин
        for i in range(nx + 1):
            for j in range(ny + 1):
                x = x0 + i * dx
                y = y0 + j * dy
                z = func(x, y)  # Z = f(x, y)
                vertices.append([x, y, z])

        # Генерация рёбер
        for i in range(nx):
            for j in range(ny):
                v0 = i * (ny + 1) + j
                v1 = v0 + 1
                v2 = v0 + (ny + 1)
                v3 = v2 + 1

                edges.append((v0, v1))  # Ребро по X
                edges.append((v0, v2))  # Ребро по Y

            # Последняя строка рёбер по X
            edges.append((i * (ny + 1) + ny, (i + 1) * (ny + 1) + ny))

        # Последний ряд рёбер по Y
        for j in range(ny):
            edges.append((nx * (ny + 1) + j, nx * (ny + 1) + j + 1))

        return Polyhedron3D(vertices, list(edges))

    def surface_sin(self, x, y):
        """Функция sin(sqrt(x^2 + y^2))."""
        return math.sin(math.sqrt(x**2 + y**2))

    def surface_parabola(self, x, y):
        """Функция x^2 - y^2."""
        return x**2 - y**2

    def surface_cos_sin(self, x, y):
        """Функция cos(x) * sin(y)."""
        return math.cos(x) * math.sin(y)


if __name__ == "__main__":
    root = tk.Tk()
    main_window = NewMainWindow(root=root)
    main_window.start()
