import tkinter as tk
import numpy as np


def cross_product(a, b):
    return np.array([a[1] * b[2] - a[2] * b[1],
                     a[2] * b[0] - a[0] * b[2],
                     a[0] * b[1] - a[1] * b[0]])


def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v


def phong_shading(normal, light_dir, view_dir, ambient, diffuse, specular, shininess):
    ambient_color = ambient
    diff = max(np.dot(normal, light_dir), 0)
    diffuse_color = diffuse * diff
    reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
    spec = max(np.dot(reflect_dir, view_dir), 0) ** shininess
    specular_color = specular * spec
    total_color = ambient_color + diffuse_color + specular_color
    return np.clip(total_color, 0, 1)


def generate_sphere(radius, latitude_count, longitude_count):
    vertices = []
    normals = []
    for i in range(latitude_count + 1):
        theta = np.pi * i / latitude_count
        for j in range(longitude_count + 1):
            phi = 2 * np.pi * j / longitude_count
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(theta)
            vertices.append([x, y, z])
            normals.append([x, y, z])
    return np.array(vertices), np.array(normals)


def generate_sphere_faces(latitude_count, longitude_count):
    faces = []
    for i in range(latitude_count):
        for j in range(longitude_count):
            p1 = i * (longitude_count + 1) + j
            p2 = p1 + 1
            p3 = (i + 1) * (longitude_count + 1) + j
            p4 = p3 + 1
            faces.append([p1, p2, p3])
            faces.append([p2, p3, p4])
    return faces


class PhongSphereApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=800, height=800, bg="white")
        self.canvas.pack()

        self.radius = 200
        self.latitude_count = 20
        self.longitude_count = 20

        self.light_dir = normalize(np.array([1, 1, 1]))
        self.view_dir = normalize(np.array([0, 0, 1]))
        self.ambient = np.array([0.1, 0.1, 0.1])
        self.diffuse = np.array([0.8, 0.8, 0.8])
        self.specular = np.array([1.0, 1.0, 1.0])
        self.shininess = 32

        self.vertices, self.normals = generate_sphere(1, self.latitude_count, self.longitude_count)
        self.faces = generate_sphere_faces(self.latitude_count, self.longitude_count)

        self.angle_x = 0
        self.angle_y = 0
        self.last_mouse_pos = None

        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.draw_sphere()

    def rotate(self, vertices, angle_x, angle_y):
        rot_x = np.array([[1, 0, 0],
                          [0, np.cos(angle_x), -np.sin(angle_x)],
                          [0, np.sin(angle_x), np.cos(angle_x)]])
        rot_y = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                          [0, 1, 0],
                          [-np.sin(angle_y), 0, np.cos(angle_y)]])
        rotation_matrix = rot_y @ rot_x
        return np.dot(vertices, rotation_matrix.T)

    def project(self, vertex):
        scale = 350
        x = int(vertex[0] * scale + 400)
        y = int(-vertex[1] * scale + 400)
        return x, y

    def draw_sphere(self):
        self.canvas.delete("all")
        rotated_vertices = self.rotate(self.vertices, self.angle_x, self.angle_y)
        for face in self.faces:
            p1, p2, p3 = face
            v1, v2, v3 = rotated_vertices[p1], rotated_vertices[p2], rotated_vertices[p3]
            normal = normalize(cross_product(v2 - v1, v3 - v1))
            color = phong_shading(normal, self.light_dir, self.view_dir, self.ambient, self.diffuse, self.specular, self.shininess)
            fill_color = "#%02x%02x%02x" % tuple((color * 255).astype(int))
            x1, y1 = self.project(v1)
            x2, y2 = self.project(v2)
            x3, y3 = self.project(v3)
            self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill=fill_color, outline="black")

    def on_mouse_drag(self, event):
        if self.last_mouse_pos is not None:
            dx = event.x - self.last_mouse_pos[0]
            dy = event.y - self.last_mouse_pos[1]
            self.angle_y += dx * 0.01
            self.angle_x += dy * 0.01
            self.draw_sphere()
        self.last_mouse_pos = (event.x, event.y)


root = tk.Tk()
app = PhongSphereApp(root)
root.mainloop()
