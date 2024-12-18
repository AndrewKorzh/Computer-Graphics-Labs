import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Button

light_position = np.array([10.0, 10.0, 10.0])  # Положение источника света
object_color = np.array([0.8, 0.3, 0.3])

def create_sphere(diameter, slices, stacks):
    vertices = []
    faces = []
    radius = diameter / 2.0

    for stack in range(stacks):
        theta = np.pi * stack / (stacks - 1)
        for slice in range(slices):
            phi = 2 * np.pi * slice / (slices - 1)

            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(theta)

            vertices.append([x, y, z])

    for stack in range(stacks - 1):
        for slice in range(slices - 1):
            idx = stack * slices + slice
            faces.append([idx, idx + slices, idx + slices + 1])
            faces.append([idx, idx + slices + 1, idx + 1])

    vertices = np.array(vertices)
    return vertices, faces

# Вычисление нормалей к вершинам
def compute_normals(vertices, faces):
    normals = np.zeros_like(vertices)
    for face in faces:
        v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm
        else:
            normal = np.zeros(3)  # Нулевой нормаль для вырожденных граней
        for idx in face:
            normals[idx] += normal

    for i in range(len(normals)):
        norm = np.linalg.norm(normals[i])
        if norm > 0:
            normals[i] = normals[i] / norm
    return normals

# Освещение по модели Ламберта
def lambert_shading(vertex, normal):
    light_dir = light_position - vertex
    light_dir = light_dir / np.linalg.norm(light_dir)
    intensity = max(np.dot(normal, light_dir), 0.0)
    color = object_color * intensity
    return np.clip(color, 0, 1)  # Ограничиваем цвет в диапазоне [0, 1]

# Барицентрическая интерполяция
def barycentric_interpolation(vertices, face, vertex_colors, resolution=20):
    v0, v1, v2 = vertices[face]
    color0, color1, color2 = vertex_colors
    points = []
    colors = []

    for i in range(resolution + 1):
        for j in range(resolution + 1 - i):
            u = i / resolution
            v = j / resolution
            w = 1 - u - v
            # Убедимся, что веса корректные
            w = max(min(w, 1), 0)
            u = max(min(u, 1), 0)
            v = max(min(v, 1), 0)

            point = u * v0 + v * v1 + w * v2
            color = u * color0 + v * color1 + w * color2
            points.append(point)
            colors.append(np.clip(color, 0, 1))  # Ограничиваем значения цветов

    return np.array(points), np.array(colors)

# Функция для применения аффинных преобразований
def apply_affine_transformation(vertices, transformation_matrix):
    return np.dot(vertices, transformation_matrix.T)

# Рендеринг с интерполяцией цветов
def render(vertices, faces, normals, ax):
    ax.cla()  # Очистить предыдущий график
    ax.set_box_aspect([1, 1, 1])

    for face in faces:
        # Рассчитываем цвета вершин
        vertex_colors = [lambert_shading(vertices[idx], normals[idx]) for idx in face]
        # Интерполяция внутри треугольника
        interpolated_points, interpolated_colors = barycentric_interpolation(vertices, face, vertex_colors)

        # Добавляем точки как полигоны для отображения
        ax.scatter(
            interpolated_points[:, 0],
            interpolated_points[:, 1],
            interpolated_points[:, 2],
            c=interpolated_colors,
            s=1,
            edgecolor='none'
        )

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.draw()

# Аффинные преобразования
def apply_affine_transformation(vertices, transformation_matrix):
    return np.dot(vertices, transformation_matrix.T)

# Поворот
def rotate(vertices, angle, axis):
    c = np.cos(angle)
    s = np.sin(angle)
    if axis == 'x':
        rotation_matrix = np.array([[1, 0, 0],
                                    [0, c, -s],
                                    [0, s, c]])
    elif axis == 'y':
        rotation_matrix = np.array([[c, 0, s],
                                    [0, 1, 0],
                                    [-s, 0, c]])
    elif axis == 'z':
        rotation_matrix = np.array([[c, -s, 0],
                                    [s, c, 0],
                                    [0, 0, 1]])
    return apply_affine_transformation(vertices, rotation_matrix)

# Масштабирование
def scale(vertices, factor):
    scaling_matrix = np.diag([factor, factor, factor])
    return apply_affine_transformation(vertices, scaling_matrix)

# Сдвиг
def translate(vertices, dx, dy, dz):
    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = [dx, dy, dz]
    homogeneous_vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
    transformed = np.dot(homogeneous_vertices, translation_matrix.T)
    return transformed[:, :3]

# Обработка событий 
def on_rotate_x(event, vertices, faces, normals, ax):
    rotated_vertices = rotate(vertices, np.pi / 20, 'x')
    render(rotated_vertices, faces, normals, ax)

def on_rotate_y(event, vertices, faces, normals, ax):
    rotated_vertices = rotate(vertices, np.pi / 20, 'y')
    render(rotated_vertices, faces, normals, ax)

def on_scale_up(event, vertices, faces, normals, ax):
    transformed_vertices = scale(vertices, 1.1)
    render(transformed_vertices, faces, normals, ax)

def on_scale_down(event, vertices, faces, normals, ax):
    transformed_vertices = scale(vertices, 0.9)
    render(transformed_vertices, faces, normals, ax)

def on_translate_x(event, vertices, faces, normals, ax, dx=0.1):
    transformed_vertices = translate(vertices, dx, 0, 0)
    render(transformed_vertices, faces, normals, ax)

def on_translate_y(event, vertices, faces, normals, ax, dy=0.1):
    transformed_vertices = translate(vertices, 0, dy, 0)
    render(transformed_vertices, faces, normals, ax)

def on_translate_z(event, vertices, faces, normals, ax, dz=0.1):
    transformed_vertices = translate(vertices, 0, 0, dz)
    render(transformed_vertices, faces, normals, ax)


def main():
    diameter = 2.0
    slices, stacks = 20, 20
    vertices, faces = create_sphere(diameter, slices, stacks)
    normals = compute_normals(vertices, faces)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    render(vertices, faces, normals, ax)

    ax_rotate_x = plt.axes([0.33, 0.01, 0.1, 0.075])
    btn_rotate_x = Button(ax_rotate_x, 'Rotate X')
    btn_rotate_x.on_clicked(lambda event: on_rotate_x(event, vertices, faces, normals, ax))

    ax_rotate_y = plt.axes([0.44, 0.01, 0.1, 0.075])
    btn_rotate_y = Button(ax_rotate_y, 'Rotate Y')
    btn_rotate_y.on_clicked(lambda event: on_rotate_y(event, vertices, faces, normals, ax))

    ax_scale_up = plt.axes([0.55, 0.01, 0.1, 0.075])
    btn_scale_up = Button(ax_scale_up, 'Scale Up')
    btn_scale_up.on_clicked(lambda event: on_scale_up(event, vertices, faces, normals, ax))

    ax_scale_down = plt.axes([0.66, 0.01, 0.1, 0.075])
    btn_scale_down = Button(ax_scale_down, 'Scale Down')
    btn_scale_down.on_clicked(lambda event: on_scale_down(event, vertices, faces, normals, ax))

    ax_translate_x = plt.axes([0.77, 0.017, 0.1, 0.075])
    btn_translate_x = Button(ax_translate_x, 'Move X+')
    btn_translate_x.on_clicked(lambda event: on_translate_x(event, vertices, faces, normals, ax, 0.1))

    ax_translate_y = plt.axes([0.88, 0.017, 0.1, 0.075])
    btn_translate_y = Button(ax_translate_y, 'Move Y+')
    btn_translate_y.on_clicked(lambda event: on_translate_y(event, vertices, faces, normals, ax, 0.1))

    ax_translate_z = plt.axes([0.77, 0.09, 0.1, 0.075])
    btn_translate_z = Button(ax_translate_z, 'Move Z+')
    btn_translate_z.on_clicked(lambda event: on_translate_z(event, vertices, faces, normals, ax, 0.1))

    plt.show()

if __name__ == '__main__':
    main()
