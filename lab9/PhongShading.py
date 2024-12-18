import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Векторное произведение для получения нормали
def cross_product(a, b):
    return np.array([a[1] * b[2] - a[2] * b[1],
                     a[2] * b[0] - a[0] * b[2],
                     a[0] * b[1] - a[1] * b[0]])

# Нормализация вектора
def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

# Модель освещения Фонга
def phong_shading(normal, light_dir, view_dir, ambient, diffuse, specular, shininess):
    # Амбиентное освещение
    ambient_color = ambient

    # Диффузное освещение 
    diff = max(np.dot(normal, light_dir), 0)
    diffuse_color = diffuse * diff

    # Зеркальное освещение
    reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
    spec = max(np.dot(reflect_dir, view_dir), 0) ** shininess
    specular_color = specular * spec

    # Сумма всех компонентов освещения
    total_color = ambient_color + diffuse_color + specular_color

    # Ограничиваем значения в пределах [0, 1]
    return np.clip(total_color, 0, 1)

# Генерация вершин и нормалей для 3D-сферы
def generate_sphere(radius, latitude_count, longitude_count):
    vertices = []
    normals = []

    for i in range(latitude_count + 1):
        theta = np.pi * i / latitude_count  # угол по широте
        for j in range(longitude_count + 1):
            phi = 2 * np.pi * j / longitude_count  # угол по долготе

            # Параметрическое представление точки на сфере
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(theta)

            # Добавляем вершину и нормаль
            vertices.append([x, y, z])
            normals.append([x, y, z])

    vertices = np.array(vertices)
    normals = np.array(normals)

    return vertices, normals

# Индексы для треугольников
def generate_sphere_faces(latitude_count, longitude_count):
    faces = []

    for i in range(latitude_count):
        for j in range(longitude_count):
            p1 = i * (longitude_count + 1) + j
            p2 = p1 + 1
            p3 = (i + 1) * (longitude_count + 1) + j
            p4 = p3 + 1

            # Добавляем два треугольника для каждого квадрата
            faces.append([p1, p2, p3])
            faces.append([p2, p3, p4])

    return faces

# Параметры освещения
light_dir = np.array([1, 1, 1])  # Направление источника света
view_dir = np.array([0, 0, 1])   # Направление наблюдателя
ambient = np.array([0.1, 0.1, 0.1])  # Амбиентный компонент
diffuse = np.array([0.8, 0.8, 0.8])  # Диффузный компонент
specular = np.array([1.0, 1.0, 1.0])  # Зеркальный компонент
shininess = 32  # Шероховатость для зеркального отражения

# Параметры сферы
radius = 1  # Радиус сферы
latitude_count = 20  # Количество параллелей
longitude_count = 20  # Количество меридианов

# Генерация вершин и нормалей для сферы
vertices, normals = generate_sphere(radius, latitude_count, longitude_count)

# Генерация треугольников (граней) для сферы
faces = generate_sphere_faces(latitude_count, longitude_count)

# Визуализация: для каждого треугольника на сфере
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x_coords = []
y_coords = []
z_coords = []
colors = []

# Преобразуем для визуализации в 3D
for face in faces:
    p1, p2, p3 = face

    # Получаем нормали для билинейной интерполяции
    normal_interp = normalize(np.cross(vertices[p2] - vertices[p1], vertices[p3] - vertices[p1]))

    # Цвет пикселя, рассчитываем с использованием модели Фонга
    color = phong_shading(normal_interp, normalize(light_dir), normalize(view_dir), ambient, diffuse, specular, shininess)

    # Добавляем координаты треугольников в список
    x_coords.extend([vertices[p1][0], vertices[p2][0], vertices[p3][0]])
    y_coords.extend([vertices[p1][1], vertices[p2][1], vertices[p3][1]])
    z_coords.extend([vertices[p1][2], vertices[p2][2], vertices[p3][2]])
    colors.extend([color, color, color])

# Визуализируем грани с полученным цветом
# Каждый треугольник должен быть представлен как список из трех точек
triangles = []
for face in faces:
    triangles.append([vertices[face[0]], vertices[face[1]], vertices[face[2]]])

poly3d = Poly3DCollection(triangles, facecolors=colors, linewidths=0, edgecolors='k', alpha=0.7)

ax.add_collection3d(poly3d)

ax.set_title("Phong Shading")
plt.show()
