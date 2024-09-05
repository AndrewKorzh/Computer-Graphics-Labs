import tkinter as tk
import math


class GraphDraw:
    def __init__(
        self,
        width=800,
        height=600,
        x_min=-10,
        x_max=10,
        functions={"None": None},
    ):
        """
        param: functions - dict with functions
        """
        self.functions = functions
        self.width = width
        self.height = height
        self.x_min = x_min
        self.x_max = x_max
        self.root = tk.Tk()

    def start(self):
        self.var = tk.StringVar(value=list(self.functions.keys())[0])
        option_menu = tk.OptionMenu(self.root, self.var, *self.functions.keys())
        draw_button = tk.Button(
            self.root, text="Draw", command=self.draw_selected_graph
        )

        self.root.title("GraphDraw")
        self.root.geometry(f"{self.width}x{self.height}")

        option_menu.pack(side=tk.TOP, padx=10)
        draw_button.pack(side=tk.TOP, padx=10)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas.bind(
            "<Configure>",
            lambda event: self.draw_selected_graph(),
        )

        self.root.mainloop()

    def get_y_range_with_offset(self, func, x_min, x_max, step=0.1):
        y_min = float("inf")
        y_max = float("-inf")

        x = x_min
        while x <= x_max:
            y = func(x)
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y
            x += step

        return max(abs(y_min), abs(y_max)) * 1.2

    def draw_selected_graph(self):
        selected_function_name = self.var.get()
        func = self.functions.get(selected_function_name)
        if func:
            self.canvas.delete("all")
            y_range = self.get_y_range_with_offset(func, self.x_min, self.x_max)
            self.draw_graph(func, self.x_min, self.x_max, -y_range, y_range)

    def draw_graph(self, func, x_min, x_max, y_min, y_max):
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()

        x_scale = window_width / (x_max - x_min)
        y_scale = window_height / (y_max - y_min)

        self.canvas.create_line(
            0, window_height / 2, window_width, window_height / 2, fill="black"
        )
        self.canvas.create_line(
            window_width / 2, 0, window_width / 2, window_height, fill="black"
        )
        previous_point = None
        for x_pixel in range(window_width):
            x = x_min + x_pixel / x_scale
            y = func(x)

            y_pixel = window_height - (y - y_min) * y_scale

            if previous_point:
                self.canvas.create_line(
                    previous_point[0], previous_point[1], x_pixel, y_pixel, fill="blue"
                )

            previous_point = (x_pixel, y_pixel)


functions = {
    "sin(x)": lambda x: math.sin(x),
    "sin(x/10)": lambda x: math.sin(x / 10),
    "sin(x*10)": lambda x: math.sin(x * 10),
    "sin(x)*cos(x)": lambda x: math.sin(x) * math.cos(x),
    "x^2": lambda x: x**2,
    "x^3": lambda x: x**3,
}

graph_draw = GraphDraw(
    x_min=-10,
    x_max=10,
    functions=functions,
)
graph_draw.start()
