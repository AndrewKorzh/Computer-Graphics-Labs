import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.tri import Triangulation

class Task3Window:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.root.configure(bg=parent.back_ground)
        self.root.geometry("600x600+500+20")
        self.root.title("task3")

        self.entry_fields = []
        for i in range(3):
            tk.Label(root, text=f"Vertex {i+1} (x, y):").pack()
            entry_x = tk.Entry(root)
            entry_y = tk.Entry(root)
            entry_x.pack()
            entry_y.pack()
            self.entry_fields.append((entry_x, entry_y))

        self.color_fields = []
        for i in range(3):
            tk.Label(root, text=f"Color {i+1} (RGB values from 0 to 1):").pack()
            entry_r = tk.Entry(root)
            entry_g = tk.Entry(root)
            entry_b = tk.Entry(root)
            entry_r.pack()
            entry_g.pack()
            entry_b.pack()
            self.color_fields.append((entry_r, entry_g, entry_b))

        self.gradient_button = tk.Button(
            root,
            text="Draw Gradient Triangle",
            command=self.draw_gradient_triangle,
            bg="#555",
            fg="white",
            width=30
        )
        self.gradient_button.pack(pady=20)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def draw_gradient_triangle(self):

        triangle = np.array([[float(entry_x.get()), float(entry_y.get())] for entry_x, entry_y in self.entry_fields])

        vertex_colors = np.array([
            [float(entry_r.get()), float(entry_g.get()), float(entry_b.get())]
            for entry_r, entry_g, entry_b in self.color_fields
        ])

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, 400)
        ax.set_ylim(0, 400)

        # Функция для вычисления барицентрических координат
        def barycentric_coords(p, a, b, c):
            v0 = b - a
            v1 = c - a
            v2 = p - a
            d00 = np.dot(v0, v0)
            d01 = np.dot(v0, v1)
            d11 = np.dot(v1, v1)
            d20 = np.dot(v2, v0)
            d21 = np.dot(v2, v1)
            denom = d00 * d11 - d01 * d01
            v = (d11 * d20 - d01 * d21) / denom
            w = (d00 * d21 - d01 * d20) / denom
            u = 1.0 - v - w
            return u, v, w

        # Определяем границы треугольника
        min_x, min_y = np.min(triangle, axis=0).astype(int)
        max_x, max_y = np.max(triangle, axis=0).astype(int)

        # Проходим по всем точкам внутри ограничивающего прямоугольника
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                point = np.array([x, y])
                u, v, w = barycentric_coords(point, triangle[0], triangle[1], triangle[2])

                # Если точка внутри треугольника (все барицентрические координаты >= 0)
                if u >= 0 and v >= 0 and w >= 0:
                    # Интерполируем цвет на основе барицентрических координат
                    color = u * vertex_colors[0] + v * vertex_colors[1] + w * vertex_colors[2]
                    ax.add_patch(plt.Circle((x, y), 0.5, color=color, lw=0))

        ax.invert_yaxis()
        ax.axis('off')

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

        return
