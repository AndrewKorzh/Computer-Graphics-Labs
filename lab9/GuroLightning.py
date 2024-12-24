import tkinter as tk
from tkinter import Canvas
import numpy as np

light_position = np.array([10.0, 10.0, 10.0])  # Light source position
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

def compute_normals(vertices, faces):
    normals = np.zeros_like(vertices)
    for face in faces:
        v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        normal = np.cross(v1 - v0, v2 - v0)
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm
        for idx in face:
            normals[idx] += normal

    for i in range(len(normals)):
        norm = np.linalg.norm(normals[i])
        if norm > 0:
            normals[i] = normals[i] / norm
    return normals

def lambert_shading(vertex, normal):
    light_dir = light_position - vertex
    light_dir = light_dir / np.linalg.norm(light_dir)
    intensity = max(np.dot(normal, light_dir), 0.0)
    color = object_color * intensity
    return np.clip(color, 0, 1)

def project(vertex, width, height):
    scale = 200
    x = int(width / 2 + vertex[0] * scale)
    y = int(height / 2 - vertex[1] * scale)
    return x, y

def render(canvas, vertices, faces, normals, width, height):
    canvas.delete("all")
    for face in faces:
        vertex_colors = [lambert_shading(vertices[idx], normals[idx]) for idx in face]
        points = [project(vertices[idx], width, height) for idx in face]
        color = "#{:02x}{:02x}{:02x}".format(
            int(vertex_colors[0][0] * 255),
            int(vertex_colors[0][1] * 255),
            int(vertex_colors[0][2] * 255),
        )
        canvas.create_polygon(points, fill=color, outline=color)

def apply_affine_transformation(vertices, transformation_matrix):
    return np.dot(vertices, transformation_matrix.T)

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

def scale(vertices, factor):
    scaling_matrix = np.diag([factor, factor, factor])
    return apply_affine_transformation(vertices, scaling_matrix)

def update(canvas, vertices, faces, normals, width, height):
    render(canvas, vertices, faces, normals, width, height)

def main():
    diameter = 2.0
    slices, stacks = 20, 20
    vertices, faces = create_sphere(diameter, slices, stacks)
    normals = compute_normals(vertices, faces)

    root = tk.Tk()
    root.title("3D Sphere Viewer")

    width, height = 800, 600
    canvas = Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    class SphereRenderer:
        def __init__(self):
            self.vertices = vertices
            self.faces = faces
            self.normals = normals
            self.angle_x = 0.0
            self.angle_y = 0.0
            self.last_mouse_pos = None

        def draw_sphere(self):
            # Обновляем матрицу вращения
            rotation_x = rotate(np.eye(3), self.angle_x, 'x')
            rotation_y = rotate(np.eye(3), self.angle_y, 'y')
            rotation_matrix = np.dot(rotation_y, rotation_x)

            # Применяем вращение к вершинам
            rotated_vertices = np.dot(self.vertices, rotation_matrix.T)
            update(canvas, rotated_vertices, self.faces, self.normals, width, height)

        def on_mouse_drag(self, event):
            if self.last_mouse_pos is not None:
                dx = event.x - self.last_mouse_pos[0]
                dy = event.y - self.last_mouse_pos[1]
                self.angle_y += dx * 0.01
                self.angle_x += dy * 0.01
                self.draw_sphere()
            self.last_mouse_pos = (event.x, event.y)

    renderer = SphereRenderer()

    # Привязываем события мыши
    canvas.bind("<ButtonPress-1>", lambda event: setattr(renderer, 'last_mouse_pos', (event.x, event.y)))
    canvas.bind("<ButtonRelease-1>", lambda event: setattr(renderer, 'last_mouse_pos', None))
    canvas.bind("<B1-Motion>", renderer.on_mouse_drag)

    # Кнопки для управления масштабированием
    def scale_up():
        renderer.vertices = scale(renderer.vertices, 1.1)
        renderer.draw_sphere()

    def scale_down():
        renderer.vertices = scale(renderer.vertices, 0.9)
        renderer.draw_sphere()

    button_frame = tk.Frame(root)
    button_frame.pack()

    btn_scale_up = tk.Button(button_frame, text="Scale Up", command=scale_up)
    btn_scale_up.pack(side=tk.LEFT)

    btn_scale_down = tk.Button(button_frame, text="Scale Down", command=scale_down)
    btn_scale_down.pack(side=tk.LEFT)

    # Начальное обновление
    renderer.draw_sphere()
    root.mainloop()


if __name__ == "__main__":
    main()
