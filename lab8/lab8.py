import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

def load_from_obj(filepath):
    """
    Загрузка модели из файла OBJ с использованием faces.
    """
    vertices = []
    faces = []

    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "v":  # Вершина
                vertices.append(list(map(float, parts[1:4])))
            elif parts[0] == "f":  # Грань
                # Обработка грани, где индексы вершин могут содержать дополнительные данные
                face = [int(idx.split("/")[0]) - 1 for idx in parts[1:]]
                print(face)
                faces.append(face)

    # Извлекаем рёбра из граней
    edges = set()
    for face in faces:
        for i in range(len(face)):
            edges.add((face[i], face[(i + 1) % len(face)]))

    return Polyhedron3D(vertices, list(edges), faces)


def save_to_obj(polyhedron, filepath):
    """
    Сохранение модели в формате OBJ с использованием faces.

    :param polyhedron: Экземпляр Polyhedron3D для сохранения.
    :param filepath: Путь к файлу для сохранения.
    """
    with open(filepath, "w") as file:
        # Записываем вершины
        for vertex in polyhedron.vertices:
            if len(vertex) == 2:  # Если координаты только X и Y
                x, y = vertex
                z = 0.0
            elif len(vertex) == 3:  # Координаты X, Y, Z
                x, y, z = vertex
            else:
                raise ValueError(f"Некорректная вершина: {vertex}")

            file.write(f"v {x} {y} {z}\n")

        # Записываем грани
        for face in polyhedron.faces:
            face_str = " ".join(str(idx + 1) for idx in face)  # OBJ формат использует индексацию с 1
            file.write(f"f {face_str}\n")


class Sphere:
    def __init__(self, radius, segments, rings):
        self.radius = radius
        self.segments = segments
        self.rings = rings
        self.vertices = []
        self.edges = []
        self.faces = []
        self.generate_sphere()

    def generate_sphere(self):
        """Генерация вершин, рёбер и граней для представления поверхности сферы."""
        for i in range(self.rings + 1):  # Шаг по широте
            theta = np.pi * i / self.rings  # Угол от 0 до pi (от полюса до полюса)
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            for j in range(self.segments):  # Шаг по долготе
                phi = 2 * np.pi * j / self.segments  # Угол от 0 до 2*pi
                x = self.radius * sin_theta * np.cos(phi)
                y = self.radius * sin_theta * np.sin(phi)
                z = self.radius * cos_theta
                self.vertices.append((x, y, z))

                # Добавление рёбер
                # Соединяем точки вдоль долгот (вертикальные рёбра)
                if j > 0:
                    self.edges.append(
                        (i * self.segments + j, i * self.segments + (j - 1))
                    )
                # Соединяем точки вдоль широт (горизонтальные рёбра)
                if i > 0:
                    self.edges.append(
                        ((i - 1) * self.segments + j, i * self.segments + j)
                    )

            # Замыкание последней точки с первой вдоль долготы
            self.edges.append(
                (i * self.segments, i * self.segments + self.segments - 1)
            )

        # Замыкаем последние кольца
        for j in range(self.segments):
            self.edges.append(((self.rings - 1) * self.segments + j, j))

        # Генерация граней
        for i in range(self.rings):  # Проход по широте
            for j in range(self.segments):  # Проход по долготе
                next_j = (j + 1) % self.segments

                # Верхний треугольник
                self.faces.append([
                    i * self.segments + j,
                    (i + 1) * self.segments + j,
                    i * self.segments + next_j,
                ])

                # Нижний треугольник
                self.faces.append([
                    i * self.segments + next_j,
                    (i + 1) * self.segments + j,
                    (i + 1) * self.segments + next_j,
                ])



class Camera:
    """Класс для камеры, которая определяет её положение и ориентацию."""

    def __init__(self, position, look_at, up_vector):
        self.position = np.array(position)
        self.look_at = np.array(look_at)
        self.up_vector = np.array(up_vector)

    def get_view_matrix(self):
        """Возвращает матрицу вида камеры для преобразования в пространство камеры."""
        z_axis = self.position - self.look_at
        z_axis = z_axis / np.linalg.norm(z_axis)  # Нормализуем вектор

        x_axis = np.cross(self.up_vector, z_axis)  # Перпендикулярно z
        x_axis = x_axis / np.linalg.norm(x_axis)

        y_axis = np.cross(z_axis, x_axis)

        rotation_matrix = np.array([x_axis, y_axis, z_axis])

        # Позиция камеры в пространстве
        translation_vector = -np.dot(rotation_matrix, self.position)

        # Формируем итоговую матрицу вида
        return np.vstack(
            [np.column_stack([rotation_matrix, translation_vector]), [0, 0, 0, 1]]
        )


class Polyhedron3D:
    """Класс для многогранника."""

    def __init__(self, vertices, edges,faces):
        self.vertices = np.array(vertices)  # Координаты вершин
        self.edges = edges  # Пары индексов для рёбер
        self.faces = faces
    def project(self, point, matrix):
        """Проецируем точку через заданную матрицу."""
        x, y, z = point
        point_4d = np.array([x, y, z, 1])
        projected = np.dot(matrix, point_4d)
        return projected[0] / projected[3], projected[1] / projected[3]

    def calculate_normal(self, face):
        v1 = self.vertices[face[1]] - self.vertices[face[0]]
        v2 = self.vertices[face[2]] - self.vertices[face[0]]
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)  # Нормализация
        return normal

    def is_face_visible(self, face, camera_position):
        """Проверяет видимость грани относительно камеры."""
        normal = self.calculate_normal(face)
        center = np.mean([self.vertices[idx] for idx in face], axis=0)
        view_vector = camera_position - center
        return np.dot(normal, view_vector) < 0

    def translate(self, tx, ty, tz):
        """Смещение многогранника на (tx, ty, tz)."""
        translation_matrix = np.array(
            [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]]
        )
        self.vertices = np.dot(
            np.c_[self.vertices, np.ones(len(self.vertices))], translation_matrix.T
        )[:, :3]

    def scale(self, sx, sy, sz):
        """Масштабирование многогранника относительно его центра."""
        centroid = np.mean(self.vertices, axis=0)
        scaling_matrix = np.array(
            [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]]
        )

        self.translate(-centroid[0], -centroid[1], -centroid[2])
        self.vertices = np.dot(
            np.c_[self.vertices, np.ones(len(self.vertices))], scaling_matrix.T
        )[:, :3]
        self.translate(centroid[0], centroid[1], centroid[2])

    def rotate(self, angle, axis):
        """Поворот многогранника вокруг оси (x, y, z)."""
        axis = axis / np.linalg.norm(axis)
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        ux, uy, uz = axis

        # Матрица поворота (по оси с заданными углами)
        rotation_matrix = np.array(
            [
                [
                    cos_angle + ux**2 * (1 - cos_angle),
                    ux * uy * (1 - cos_angle) - uz * sin_angle,
                    ux * uz * (1 - cos_angle) + uy * sin_angle,
                ],
                [
                    uy * ux * (1 - cos_angle) + uz * sin_angle,
                    cos_angle + uy**2 * (1 - cos_angle),
                    uy * uz * (1 - cos_angle) - ux * sin_angle,
                ],
                [
                    uz * ux * (1 - cos_angle) - uy * sin_angle,
                    uz * uy * (1 - cos_angle) + ux * sin_angle,
                    cos_angle + uz**2 * (1 - cos_angle),
                ],
            ]
        )
        self.vertices = np.dot(self.vertices, rotation_matrix.T)

    def reflect(self, plane_normal, point_on_plane):
        """Отражение относительно выбранной плоскости."""
        # Создаем матрицу для отражения
        normal = plane_normal / np.linalg.norm(plane_normal)  # Нормализуем нормаль
        d = -np.dot(normal, point_on_plane)

        reflection_matrix = np.array(
            [
                [
                    1 - 2 * normal[0] ** 2,
                    -2 * normal[0] * normal[1],
                    -2 * normal[0] * normal[2],
                    -2 * normal[0] * d,
                ],
                [
                    -2 * normal[1] * normal[0],
                    1 - 2 * normal[1] ** 2,
                    -2 * normal[1] * normal[2],
                    -2 * normal[1] * d,
                ],
                [
                    -2 * normal[2] * normal[0],
                    -2 * normal[2] * normal[1],
                    1 - 2 * normal[2] ** 2,
                    -2 * normal[2] * d,
                ],
                [0, 0, 0, 1],
            ]
        )
        self.vertices = np.dot(
            np.c_[self.vertices, np.ones(len(self.vertices))], reflection_matrix.T
        )[:, :3]

    def rotate_around_line(self, point1, point2, angle):
        """Поворот многогранника вокруг прямой, заданной двумя точками."""
        # Вектор направления оси вращения
        direction = point2 - point1
        axis = direction / np.linalg.norm(direction)

        # Переносим точку point1 в начало
        self.translate(-point1[0], -point1[1], -point1[2])

        # Поворот вокруг оси
        self.rotate(angle, axis)

        # Возвращаем многогранник на прежнее место
        self.translate(point1[0], point1[1], point1[2])


def get_polyhedron(name):
    """Возвращает многогранник по имени."""
    if name == "tetrahedron":
        # Тетраэдр
        vertices = np.array([[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]])
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        faces = [
            [0, 1, 2],
            [0, 1, 3],
            [0, 2, 3],
            [1, 2, 3],
        ]
    elif name == "cube":
        # Куб
        vertices = np.array(
            [
                [-1, -1, 1],
                [-1, 1, 1],
                [-1, -1, -1],
                [-1, 1, -1],
                [1, -1, 1],
                [1, 1, 1],
                [1, -1, -1],
                [1, 1, -1],
            ]
        )
        edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),  # Верхняя грань
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),  # Нижняя грань
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),  # Вертикальные рёбра
        ]

        faces = [
            [0, 1, 3, 2],  # Передняя грань
            [2,3,7,6],  # Задняя грань
            [6,7,5,4],  # Правая грань
            [4,5,1,0],  # Левая грань
            [2,6,4,0],  # Верхняя грань
            [7,3,1,5],  # Нижняя грань
        ]

    elif name == "octahedron":
        # Октаэдр
        vertices = np.array(
            [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]
        )
        edges = [
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, 4),
            (2, 5),
            (3, 4),
            (3, 5),
        ]
        faces = [
            [0, 2, 4],
            [0, 2, 5],
            [0, 3, 4],
            [0, 3, 5],
            [1, 2, 4],
            [1, 2, 5],
            [1, 3, 4],
            [1, 3, 5],
        ]
    elif name == "icosahedron":
        # Икосаэдр
        phi = (1 + np.sqrt(5)) / 2  # Золотое сечение
        vertices = np.array(
            [
                [-1, phi, 0],
                [1, phi, 0],
                [-1, -phi, 0],
                [1, -phi, 0],
                [0, -1, phi],
                [0, 1, phi],
                [0, -1, -phi],
                [0, 1, -phi],
                [phi, 0, -1],
                [phi, 0, 1],
                [-phi, 0, -1],
                [-phi, 0, 1],
            ]
        )
        edges = [
            (0, 1),
            (0, 5),
            (0, 7),
            (0, 11),
            (0, 10),
            (1, 5),
            (1, 7),
            (1, 9),
            (1, 8),
            (2, 4),
            (2, 6),
            (2, 11),
            (2, 10),
            (3, 4),
            (3, 6),
            (3, 8),
            (3, 9),
            (4, 5),
            (4, 9),
            (5, 11),
            (6, 7),
            (6, 10),
            (7, 8),
            (8, 9),
            (10, 11),
        ]
        faces = [
    [0, 1, 5],
    [0, 5, 11],
    [0, 11, 10],
    [0, 10, 7],
    [0, 7, 1],
    [1, 7, 8],
    [1, 8, 9],
    [1, 9, 5],
    [5, 9, 4],
    [5, 4, 11],
    [11, 4, 2],
    [11, 2, 10],
    [10, 2, 6],
    [10, 6, 7],
    [7, 6, 8],
    [8, 6, 3],
    [8, 3, 9],
    [9, 3, 4],
    [4, 3, 2],
    [2, 3, 6],
]
    elif name == "dodecahedron":
        # Додекаэдр
        phi = (1 + np.sqrt(5)) / 2
        a, b = 1 / phi, phi
        vertices = np.array(
            [
                [-1, -1, -1],
                [-1, -1, 1],
                [-1, 1, -1],
                [-1, 1, 1],
                [1, -1, -1],
                [1, -1, 1],
                [1, 1, -1],
                [1, 1, 1],
                [0, -a, -b],
                [0, -a, b],
                [0, a, -b],
                [0, a, b],
                [-a, -b, 0],
                [-a, b, 0],
                [a, -b, 0],
                [a, b, 0],
                [-b, 0, -a],
                [b, 0, -a],
                [-b, 0, a],
                [b, 0, a],
            ]
        )
        edges = [
            (0, 8),
            (0, 10),
            (0, 16),
            (1, 9),
            (1, 11),
            (1, 18),
            (2, 12),
            (2, 13),
            (2, 16),
            (3, 13),
            (3, 15),
            (3, 18),
            (4, 8),
            (4, 14),
            (4, 17),
            (5, 9),
            (5, 14),
            (5, 19),
            (6, 10),
            (6, 15),
            (6, 17),
            (7, 11),
            (7, 15),
            (7, 19),
            (8, 12),
            (9, 13),
            (10, 16),
            (11, 18),
            (12, 17),
            (13, 18),
            (14, 17),
            (15, 19),
            (16, 18),
            (17, 19),
        ]
        faces = [
    [0, 8, 9, 1, 16],
    [0, 16, 2, 12, 8],
    [8, 12, 4, 14, 9],
    [9, 14, 5, 19, 1],
    [1, 19, 7, 11, 18],
    [18, 11, 3, 13, 2],
    [2, 13, 3, 15, 12],
    [12, 15, 6, 17, 4],
    [4, 17, 10, 6, 14],
    [14, 6, 10, 7, 19],
    [7, 10, 17, 15, 3],
    [18, 13, 15, 17, 6],
]

    elif name == "sphere":
        sphere = Sphere(radius=3.0, segments=20, rings=20)

        vertices = np.array(sphere.vertices)

        edges = sphere.edges
        faces = sphere.faces


    return Polyhedron3D(vertices, edges, faces)


def get_perspective_projection_matrix(fov=90, aspect_ratio=1, near=0.1, far=1000):
    """Перспективная проекционная матрица."""
    # Конвертируем угол обзора в радианы
    fov_rad = np.radians(fov)
    tan_half_fov = np.tan(fov_rad / 2)

    # Строим матрицу перспективы
    projection_matrix = np.array(
        [
            [1 / (aspect_ratio * tan_half_fov), 0, 0, 0],
            [0, 1 / tan_half_fov, 0, 0],
            [0, 0, -(far + near) / (far - near), -1],
            [0, 0, -(2 * far * near) / (far - near), 0],
        ]
    )

    return projection_matrix


def get_orthographic_projection_matrix(
    left=-1, right=1, bottom=-1, top=1, near=0.1, far=1000
):
    projection_matrix = np.array(
        [
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1],
        ]
    )

    return projection_matrix


def get_progection_matrix(projection_type):
    if projection_type == "perspective":
        return get_perspective_projection_matrix()
    else:
        return get_orthographic_projection_matrix()


class PolyhedronDrawer:
    """Класс для рисования многогранника с использованием Z-буфера."""

    def __init__(self, canvas, projection_matrix, view_matrix, camera, objects=None):
        self.canvas = canvas
        self.camera = camera
        self.projection_matrix = projection_matrix
        self.view_matrix = view_matrix
        self.center_x = 200
        self.center_y = 200
        self.canvas_width = 400  # Ширина холста
        self.canvas_height = 400  # Высота холста
        self.frame_buffer = np.full((400, 400, 3), (255, 255, 255), dtype=np.uint8)  # Белый фон
        self.z_buffer = np.full((self.canvas_width, self.canvas_height), np.inf)
        self.objects = []
        if objects != None:
            self.objects = objects

    def add_polyhedron(self, polyhedron):
        """Добавляет многогранник в список."""
        self.objects.append(polyhedron)

    def draw(self):
        """Отрисовывает многогранник с использованием Z-буфера."""
        self.canvas.delete("all")
        self.z_buffer.fill(-np.inf)  # Сброс Z-буфера

        # Матрица вида и проекции
        projection_view_matrix = self.projection_matrix @ self.view_matrix
        camera_position = self.camera.position

        for polyhedron in self.objects:
            for face in polyhedron.faces:
                # Проверяем видимость грани
                if not polyhedron.is_face_visible(face, camera_position):
                    continue

                # Проецируем все вершины грани
                projected_points = []
                z_values = []
                for idx in face:
                    x, y, z = polyhedron.vertices[idx]
                    point_4d = np.array([x, y, z, 1])
                    projected = np.dot(projection_view_matrix, point_4d)

                    if projected[3] != 0:  # Нормализация координат
                        x_proj = projected[0] / projected[3]
                        y_proj = projected[1] / projected[3]
                        z_proj = projected[2] / projected[3]
                    else:
                        x_proj, y_proj, z_proj = projected[0], projected[1], projected[2]

                    # Переводим в координаты экрана
                    screen_x = int(self.center_x + x_proj * 100)
                    screen_y = int(self.center_y - y_proj * 100)
                    projected_points.append((screen_x, screen_y))
                    z_values.append(z_proj)

                # Отрисовка грани с использованием Z-буфера
                for i in range(len(face)):
                    start = projected_points[i]
                    end = projected_points[(i + 1) % len(face)]
                    z_start = z_values[i]
                    z_end = z_values[(i + 1) % len(face)]

                    # Линия Брезенхема с учётом глубины
                    self._draw_line_with_zbuffer(start, end, z_start, z_end)

    def _draw_line_with_zbuffer(self, start, end, z_start, z_end):
        """Рисует линию с использованием Z-буфера (алгоритм Брезенхема)."""
        x1, y1 = start
        x2, y2 = end
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        z_current = z_start
        length = max(dx, dy)  # Используем максимальный шаг для расчёта
        z_step = (z_end - z_start) / length if length != 0 else 0

        while True:
            # Проверяем, что координаты находятся в пределах экрана
            if 0 <= x1 < self.z_buffer.shape[1] and 0 <= y1 < self.z_buffer.shape[0]:
                # Z-буфер: Проверяем глубину пикселя
                if z_current > self.z_buffer[y1, x1]:  # Порядок индексов [y, x]
                    self.z_buffer[y1, x1] = z_current
                    # Рисуем пиксель на экране
                    self.canvas.create_oval(x1, y1, x1 + 1, y1 + 1, fill="black", outline="black")

            # Если достигли конца линии
            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

            # Обновляем значение z
            z_current += z_step


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lab6")
        self.canvas = None
        self.camera = None
        self.drawer = None
        self.objects = []

        self.view_matrix = None
        self.polyhedron = None
        self.projection_matrix = None

        self.camera_position = [5, 5, 6]
        self.camera_look_at = [0, 0, 0]
        self.camera_up_vector = [0, 0, 1]

        self.polyhedron_name = "cube"
        self.polyhedrons_names = [
            "cube",
            "tetrahedron",
            "octahedron",
            "icosahedron",
            "dodecahedron",
            "sphere",
        ]

        self.projection_type = "perspective"
        self.projection_types = ["perspective", "orthographic"]

        ### Camera position ###
        row_count = 0

        self.change_camera_pos_label = tk.Label(self.root, text="camera position:")

        self.change_camera_pos_label.grid(row=row_count, column=0)

        self.x_plus_button = tk.Button(
            self.root, text="   x+   ", command=lambda: self.change_camera_pos("x+")
        )
        self.x_plus_button.grid(row=row_count, column=1)

        self.x_minus_button = tk.Button(
            self.root, text="   x-   ", command=lambda: self.change_camera_pos("x-")
        )
        self.x_minus_button.grid(row=row_count, column=2)

        self.y_plus_button = tk.Button(
            self.root, text="   y+   ", command=lambda: self.change_camera_pos("y+")
        )
        self.y_plus_button.grid(row=row_count, column=3)

        self.y_minus_button = tk.Button(
            self.root, text="   y-   ", command=lambda: self.change_camera_pos("y-")
        )
        self.y_minus_button.grid(row=row_count, column=4)

        self.z_plus_button = tk.Button(
            self.root, text="   z+   ", command=lambda: self.change_camera_pos("z+")
        )
        self.z_plus_button.grid(row=row_count, column=5)

        self.z_minus_button = tk.Button(
            self.root, text="   z-   ", command=lambda: self.change_camera_pos("z-")
        )
        self.z_minus_button.grid(row=row_count, column=6)

        ### Camera Look ###

        row_count += 1

        self.change_look_at_label = tk.Label(self.root, text="camera look_at:")

        self.change_look_at_label.grid(row=row_count, column=0)

        self.look_at_x_plus_button = tk.Button(
            self.root, text="   x+   ", command=lambda: self.change_look_at("x+")
        )
        self.look_at_x_plus_button.grid(row=row_count, column=1)

        self.look_at_x_minus_button = tk.Button(
            self.root, text="   x-   ", command=lambda: self.change_look_at("x-")
        )
        self.look_at_x_minus_button.grid(row=row_count, column=2)

        self.look_at_y_plus_button = tk.Button(
            self.root, text="   y+   ", command=lambda: self.change_look_at("y+")
        )
        self.look_at_y_plus_button.grid(row=row_count, column=3)

        self.look_at_y_minus_button = tk.Button(
            self.root, text="   y-   ", command=lambda: self.change_look_at("y-")
        )
        self.look_at_y_minus_button.grid(row=row_count, column=4)

        self.look_at_z_plus_button = tk.Button(
            self.root, text="   z+   ", command=lambda: self.change_look_at("z+")
        )
        self.look_at_z_plus_button.grid(row=row_count, column=5)

        self.look_at_z_minus_button = tk.Button(
            self.root, text="   z-   ", command=lambda: self.change_look_at("z-")
        )
        self.look_at_z_minus_button.grid(row=row_count, column=6)

        ### Translation ###
        row_count += 1

        self.translation_label = tk.Label(self.root, text="translation:")

        self.translation_label.grid(row=row_count, column=0)

        self.translation_x_plus_button = tk.Button(
            self.root,
            text="   x+   ",
            command=lambda: self.translate_polyhedron(1, 0, 0),
        )
        self.translation_x_plus_button.grid(row=row_count, column=1)

        self.translation_x_minus_button = tk.Button(
            self.root,
            text="   x-   ",
            command=lambda: self.translate_polyhedron(-1, 0, 0),
        )
        self.translation_x_minus_button.grid(row=row_count, column=2)

        self.translation_y_plus_button = tk.Button(
            self.root,
            text="   y+   ",
            command=lambda: self.translate_polyhedron(0, 1, 0),
        )
        self.translation_y_plus_button.grid(row=row_count, column=3)

        self.translation_y_minus_button = tk.Button(
            self.root,
            text="   y-   ",
            command=lambda: self.translate_polyhedron(0, -1, 0),
        )
        self.translation_y_minus_button.grid(row=row_count, column=4)

        self.translation_z_plus_button = tk.Button(
            self.root,
            text="   z+   ",
            command=lambda: self.translate_polyhedron(0, 0, 1),
        )
        self.translation_z_plus_button.grid(row=row_count, column=5)

        self.translation_z_minus_button = tk.Button(
            self.root,
            text="   z-   ",
            command=lambda: self.translate_polyhedron(0, 0, -1),
        )
        self.translation_z_minus_button.grid(row=row_count, column=6)

        ### Rotation ###
        row_count += 1

        entry_width = 5

        self.rotation_label = tk.Label(self.root, text="Rotation:")
        self.rotation_label.grid(row=row_count, column=0)

        self.rotation_angle_label = tk.Label(self.root, text="a, (x,y,z):")
        self.rotation_angle_label.grid(row=row_count, column=1)

        self.angle_entry = tk.Entry(self.root, width=entry_width)
        self.angle_entry.grid(row=row_count, column=2)
        self.angle_entry.insert(0, "2")

        self.rotation_x_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_x_entry.grid(row=row_count, column=3)
        self.rotation_x_entry.insert(0, "1")

        self.rotation_y_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_y_entry.grid(row=row_count, column=4)
        self.rotation_y_entry.insert(0, "0")

        self.rotation_z_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_z_entry.grid(row=row_count, column=5)
        self.rotation_z_entry.insert(0, "0")

        self.rotate_button = tk.Button(
            self.root,
            text="rotate",
            command=self.rotate_polyhedron,
        )
        self.rotate_button.grid(row=row_count, column=6)

        ### Scale ###
        row_count += 1

        self.scale_label = tk.Label(self.root, text="scale:")

        self.scale_label.grid(row=row_count, column=0)

        self.scale_x_plus_button = tk.Button(
            self.root,
            text="   x+   ",
            command=lambda: self.scale_polyhedron(1, 0, 0),
        )
        self.scale_x_plus_button.grid(row=row_count, column=1)

        self.scale_x_minus_button = tk.Button(
            self.root,
            text="   x-   ",
            command=lambda: self.scale_polyhedron(-1, 0, 0),
        )
        self.scale_x_minus_button.grid(row=row_count, column=2)

        self.scale_y_plus_button = tk.Button(
            self.root,
            text="   y+   ",
            command=lambda: self.scale_polyhedron(0, 1, 0),
        )
        self.scale_y_plus_button.grid(row=row_count, column=3)

        self.scale_y_minus_button = tk.Button(
            self.root,
            text="   y-   ",
            command=lambda: self.scale_polyhedron(0, -1, 0),
        )
        self.scale_y_minus_button.grid(row=row_count, column=4)

        self.scale_z_plus_button = tk.Button(
            self.root,
            text="   z+   ",
            command=lambda: self.scale_polyhedron(0, 0, 1),
        )
        self.scale_z_plus_button.grid(row=row_count, column=5)

        self.scale_z_minus_button = tk.Button(
            self.root,
            text="   z-   ",
            command=lambda: self.scale_polyhedron(0, 0, -1),
        )
        self.scale_z_minus_button.grid(row=row_count, column=6)

        ### Reflection ###
        row_count += 1

        self.reflection_label = tk.Label(self.root, text="Reflection:")
        self.reflection_label.grid(row=row_count, column=0, rowspan=2)

        self.reflection_normal_label = tk.Label(self.root, text="Normal:")  # (x,y,z):
        self.reflection_normal_label.grid(row=row_count, column=1)

        # Ввод нормали плоскости для отражения
        self.reflection_normal_x_entry = tk.Entry(self.root, width=entry_width)
        self.reflection_normal_x_entry.grid(row=row_count, column=2)
        self.reflection_normal_x_entry.insert(0, "1")

        self.reflection_normal_y_entry = tk.Entry(self.root, width=entry_width)
        self.reflection_normal_y_entry.grid(row=row_count, column=3)
        self.reflection_normal_y_entry.insert(0, "0")

        self.reflection_normal_z_entry = tk.Entry(self.root, width=entry_width)
        self.reflection_normal_z_entry.grid(row=row_count, column=4)
        self.reflection_normal_z_entry.insert(0, "1")

        self.reflect_button = tk.Button(
            self.root,
            text="Reflect",
            command=self.reflect_polyhedron,
        )
        self.reflect_button.grid(row=row_count, column=5, columnspan=2, rowspan=2)

        row_count += 1

        # Ввод точки на плоскости
        self.reflection_point_label = tk.Label(
            self.root, text="Point:"  #  on plane (x,y,z):
        )
        self.reflection_point_label.grid(row=row_count, column=1)

        self.reflection_point_x_entry = tk.Entry(self.root, width=entry_width)
        self.reflection_point_x_entry.grid(row=row_count, column=2)
        self.reflection_point_x_entry.insert(0, "1")

        self.reflection_point_y_entry = tk.Entry(self.root, width=entry_width)
        self.reflection_point_y_entry.grid(row=row_count, column=3)
        self.reflection_point_y_entry.insert(0, "0")

        self.reflection_point_z_entry = tk.Entry(self.root, width=entry_width)
        self.reflection_point_z_entry.grid(row=row_count, column=4)
        self.reflection_point_z_entry.insert(0, "0")

        ### Rotation around a Line ###
        row_count += 1

        self.rotation_around_line_label = tk.Label(self.root, text="Around line:")
        self.rotation_around_line_label.grid(row=row_count, column=0, rowspan=2)

        self.rotation_line_point1_label = tk.Label(self.root, text="Point 1:")
        self.rotation_line_point1_label.grid(row=row_count, column=1)

        # Ввод первой точки на линии
        self.rotation_line_point1_x_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_line_point1_x_entry.grid(row=row_count, column=2)
        self.rotation_line_point1_x_entry.insert(0, "0")

        self.rotation_line_point1_y_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_line_point1_y_entry.grid(row=row_count, column=3)
        self.rotation_line_point1_y_entry.insert(0, "0")

        self.rotation_line_point1_z_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_line_point1_z_entry.grid(row=row_count, column=4)
        self.rotation_line_point1_z_entry.insert(0, "0")

        self.rotation_angle_label = tk.Label(self.root, text="Angle:")
        self.rotation_angle_label.grid(row=row_count, column=5)

        self.rotation_angle_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_angle_entry.grid(row=row_count, column=6)
        self.rotation_angle_entry.insert(0, "30")

        row_count += 1

        self.rotation_line_point2_label = tk.Label(self.root, text="Point 2:")
        self.rotation_line_point2_label.grid(row=row_count, column=1)

        # Ввод второй точки на линии
        self.rotation_line_point2_x_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_line_point2_x_entry.grid(row=row_count, column=2)
        self.rotation_line_point2_x_entry.insert(0, "1")

        self.rotation_line_point2_y_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_line_point2_y_entry.grid(row=row_count, column=3)
        self.rotation_line_point2_y_entry.insert(0, "0")

        self.rotation_line_point2_z_entry = tk.Entry(self.root, width=entry_width)
        self.rotation_line_point2_z_entry.grid(row=row_count, column=4)
        self.rotation_line_point2_z_entry.insert(0, "0")

        self.rotate_around_line_button = tk.Button(
            self.root,
            text="Rotate",
            command=self.rotate_around_line_polyhedron,
        )
        self.rotate_around_line_button.grid(row=row_count, column=5, columnspan=2)

        ### Chage polyhedron and projection ###
        row_count += 1

        self.selected_polyhedron_name = tk.StringVar()
        self.selected_polyhedron_name.set(self.polyhedrons_names[0])

        self.polyhedrons_dropdown = tk.OptionMenu(
            self.root,
            self.selected_polyhedron_name,
            *self.polyhedrons_names,
            command=self.select_polyhedron,
        )

        self.polyhedrons_dropdown.grid(row=row_count, column=1, columnspan=3)

        self.selected_projection = tk.StringVar()
        self.selected_projection.set(self.projection_types[0])

        self.projection_dropdown = tk.OptionMenu(
            self.root,
            self.selected_projection,
            *self.projection_types,
            command=self.select_projection,
        )
        self.projection_dropdown.grid(row=row_count, column=4, columnspan=3)

        row_count += 1

        tk.Button(root, text="Clear", command=self.clear).grid(
            row=row_count, column=0
        )

        row_count += 1

        tk.Button(root, text="Load OBJ File", command=self.load_obj).grid(
            row=row_count, column=0
        )
        tk.Button(root, text="Save OBJ File", command=self.save_obj).grid(
            row=row_count, column=2
        )

        row_count += 1

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="white")
        self.canvas.grid(row=row_count, column=0, columnspan=7)

        self.root.bind("<MouseWheel>", self.on_mouse_wheel)

    def select_polyhedron(self, selected_value):
        print(f"Вы выбрали: {selected_value}")
        self.polyhedron_name = selected_value
        self.polyhedron = get_polyhedron(self.polyhedron_name)
        self.redraw()

    def select_projection(self, selected_value):
        print(f"Вы выбрали: {selected_value}")
        self.projection_type = selected_value
        self.redraw()

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            print("Прокрутили вверх")
            self.camera_position[0] += 1
            self.camera_position[1] += 1
            self.camera_position[2] += 1
            self.redraw()
        else:
            print("Прокрутили вниз")
            self.camera_position[0] -= 1
            self.camera_position[1] -= 1
            self.camera_position[2] -= 1
            self.redraw()
        return

    def change_camera_pos(self, com):
        if com == "x+":
            self.camera_position[0] += 1
        elif com == "x-":
            self.camera_position[0] -= 1
        elif com == "y+":
            self.camera_position[1] += 1
        elif com == "y-":
            self.camera_position[1] -= 1
        elif com == "z+":
            self.camera_position[2] += 1
        elif com == "z-":
            self.camera_position[2] -= 1
        self.redraw()

    def change_look_at(self, com):
        if com == "x+":
            self.camera_look_at[0] += 1
        elif com == "x-":
            self.camera_look_at[0] -= 1
        elif com == "y+":
            self.camera_look_at[1] += 1
        elif com == "y-":
            self.camera_look_at[1] -= 1
        elif com == "z+":
            self.camera_look_at[2] += 1
        elif com == "z-":
            self.camera_look_at[2] -= 1
        self.redraw()

    def translate_polyhedron(self, x, y, z):
        self.polyhedron.translate(x, y, z)
        self.redraw()
        return

    def rotate_polyhedron(self):

        angle = float(self.angle_entry.get())
        axis_x = float(self.rotation_x_entry.get())
        axis_y = float(self.rotation_y_entry.get())
        axis_z = float(self.rotation_z_entry.get())
        self.polyhedron.rotate(angle, np.array([axis_x, axis_y, axis_z]))
        self.redraw()
        return

    def scale_polyhedron(self, x, y, z):
        self.polyhedron.scale(1 + x * 0.3, 1 + y * 0.3, 1 + z * 0.3)
        self.redraw()
        return

    def reflect_polyhedron(self):
        normal_x = float(self.reflection_normal_x_entry.get())
        normal_y = float(self.reflection_normal_y_entry.get())
        normal_z = float(self.reflection_normal_z_entry.get())

        point_x = float(self.reflection_point_x_entry.get())
        point_y = float(self.reflection_point_y_entry.get())
        point_z = float(self.reflection_point_z_entry.get())

        # Преобразуем нормаль в numpy массив
        normal = np.array([normal_x, normal_y, normal_z])
        point_on_plane = np.array([point_x, point_y, point_z])

        self.polyhedron.reflect(normal, point_on_plane)
        self.redraw()
        return

    def rotate_around_line_polyhedron(self):
        point1_x = float(self.rotation_line_point1_x_entry.get())
        point1_y = float(self.rotation_line_point1_y_entry.get())
        point1_z = float(self.rotation_line_point1_z_entry.get())

        point2_x = float(self.rotation_line_point2_x_entry.get())
        point2_y = float(self.rotation_line_point2_y_entry.get())
        point2_z = float(self.rotation_line_point2_z_entry.get())

        angle = float(self.rotation_angle_entry.get())

        point1 = np.array([point1_x, point1_y, point1_z])
        point2 = np.array([point2_x, point2_y, point2_z])

        self.polyhedron.rotate_around_line(point1, point2, angle)
        self.redraw()
        return
    def clear(self):
        self.canvas.delete("all")
        self.drawer = None
        self.objects = []

    def start(self):
        self.polyhedron = get_polyhedron(self.polyhedron_name)
        self.redraw()
        self.root.mainloop()

    def redraw(self):
        print(
            f"camera_position: {self.camera_position}, look_at: {self.camera_look_at}"
        )
        self.canvas.delete("all")

        self.camera = Camera(
            position=self.camera_position,
            look_at=self.camera_look_at,
            up_vector=self.camera_up_vector,
        )
        self.view_matrix = self.camera.get_view_matrix()
        self.projection_matrix = get_progection_matrix(self.projection_type)

        self.drawer = PolyhedronDrawer(
            self.canvas, self.projection_matrix, self.view_matrix, self.camera, objects=self.objects
        )


        self.drawer.add_polyhedron(self.polyhedron)
        self.drawer.draw()
        return

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


if __name__ == "__main__":
    root = tk.Tk()
    main_window = MainWindow(root=root)
    main_window.start()