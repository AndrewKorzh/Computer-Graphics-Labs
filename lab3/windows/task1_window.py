import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class Task1Window:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.back_ground = parent.back_ground
        self.root.configure(bg=parent.back_ground)
        self.root.geometry("230x120+500+20")
        self.root.title("task1")

        # task1a
        self.task1a_button = tk.Button(
            root,
            text="task1a",
            command=self.task1a,
            bg="#555",
            fg="white",
            width=100,
        )
        self.task1a_button.pack(pady=5, padx=5)

        # task1b
        self.task1b_button = tk.Button(
            root,
            text="task1b",
            command=self.task1b,
            bg="#555",
            fg="white",
            width=100,
        )
        self.task1b_button.pack(pady=5, padx=5)

        # task1c
        self.task1c_button = tk.Button(
            root,
            text="task1c",
            command=self.task1c,
            bg="#555",
            fg="white",
            width=100,
        )
        self.task1c_button.pack(pady=5, padx=5)

    def task1a(self):
        child = tk.Tk()
        task1a_window = Task1aWindow(root=child, parent=self)

    def task1b(self):
        child = tk.Tk()
        task1a_window = Task1bWindow(root=child, parent=self)

    def task1c(self):
        child = tk.Tk()
        task1a_window = Task1cWindow(root=child, parent=self)


class Task1aWindow:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.root.configure(bg=parent.back_ground)
        self.width = 800
        self.height = 600
        self.root.title("task1a")
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)

        self.boarders = set()
        self.passed_val = set()

        self.fill_button = tk.Button(
            root,
            text="fill",
            command=self.fill,
            bg="#555",
            fg="white",
            width=100,
        )
        self.fill_button.pack(side=tk.TOP, pady=10)

        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.last_x, self.last_y = None, None

    def fill(self):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<B1-Motion>", self.stack_fill)

    def check_validity(self, x, y):
        if (
            (x, y) not in self.boarders
            and (x, y) not in self.passed_val
            and x > 0
            and x < self.width - 2
            and y > 0
            and y < self.height - 2
        ):
            return True
        else:
            return False

    def stack_fill(self, event):
        self.canvas.unbind("<B1-Motion>")
        x_start, y_start = event.x, event.y
        stack = [(x_start, y_start)]

        while stack:
            x, y = stack.pop()
            self.canvas.create_oval(x, y, x + 1, y + 1, fill="red", outline="red")
            self.canvas.update()
            if self.check_validity(x + 1, y):
                self.passed_val.add((x + 1, y))
                stack.append((x + 1, y))

            if self.check_validity(x - 1, y):
                self.passed_val.add((x - 1, y))
                stack.append((x - 1, y))

            if self.check_validity(x, y + 1):
                self.passed_val.add((x, y + 1))
                stack.append((x, y + 1))

            if self.check_validity(x, y - 1):
                self.passed_val.add((x, y - 1))
                stack.append((x, y - 1))

        print("Done")
        self.canvas.bind("<B1-Motion>", self.paint)
        return

    def rec_fill(self, event):
        passed_val = set()
        self.canvas.unbind("<B1-Motion>")
        x_start, y_start = event.x, event.y

        def f(self: Task1aWindow, x, y):
            self.canvas.create_oval(x, y, x + 1, y + 1, fill="red", outline="red")
            self.canvas.update()

            if self.check_validity(x + 1, y):
                passed_val.add((x + 1, y))
                f(self, x + 1, y)

            if self.check_validity(x - 1, y):
                passed_val.add((x - 1, y))
                f(self, x - 1, y)

            if self.check_validity(x, y + 1):
                passed_val.add((x, y + 1))
                f(self, x, y + 1)

            if self.check_validity(x, y - 1):
                passed_val.add((x, y - 1))
                f(self, x, y - 1)

        f(self=self, x=x_start, y=y_start)
        print("Done")
        self.canvas.bind("<B1-Motion>", self.paint)
        return

    def paint(self, event):
        self.last_x, self.last_y = event.x, event.y
        oval_size = 10

        self.canvas.create_oval(
            self.last_x - oval_size // 2,
            self.last_y - oval_size // 2,
            self.last_x + oval_size // 2,
            self.last_y + oval_size // 2,
            fill="black",
            outline="black",
        )

        for x in range(self.last_x - oval_size // 2, self.last_x + oval_size // 2 + 1):
            for y in range(
                self.last_y - oval_size // 2, self.last_y + oval_size // 2 + 1
            ):
                if (x - self.last_x) ** 2 + (y - self.last_y) ** 2 <= (
                    oval_size // 2
                ) ** 2:
                    self.boarders.add((x, y))


class Task1bWindow:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.width = 800
        self.height = 600
        self.root.configure(bg=parent.back_ground)
        self.root.title("task1b")
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.image_path = ""
        self.image = None
        self.frames_for_update = 100

        self.boarders = set()
        self.passed_val = set()

        self.fill_button = tk.Button(
            root,
            text="fill",
            command=self.fill,
            bg="#555",
            fg="white",
            width=100,
        )
        self.fill_button.pack(side=tk.TOP, pady=5)

        self.browse_button = tk.Button(
            root,
            text="browse",
            command=self.browse_file,
            bg="#555",
            fg="white",
            width=100,
        )
        self.browse_button.pack(side=tk.TOP, pady=5)

        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.last_x, self.last_y = None, None

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if filename:
            self.image_path = filename
            self.image = Image.open(self.image_path)

    def fill(self):
        print(self.image_path)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<B1-Motion>", self.stack_fill)

    def check_validity(self, x, y):
        if (
            (x, y) not in self.boarders
            and (x, y) not in self.passed_val
            and x > 0
            and x < self.width - 2
            and y > 0
            and y < self.height - 2
        ):
            return True
        else:
            return False

    def get_hex_pixel(self, x, y):
        r, g, b = self.image.getpixel((x % self.image.width, y % self.image.height))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def stack_fill(self, event):
        self.canvas.unbind("<B1-Motion>")
        x_start, y_start = event.x, event.y
        stack = [(x_start, y_start)]

        frame_count = 0
        while stack:
            frame_count += 1
            x, y = stack.pop()
            # Тут надо доставать пиксель из фотки - просто достаточно
            color = self.get_hex_pixel(x, y)
            self.canvas.create_oval(x, y, x + 1, y + 1, fill=color, outline=color)
            if frame_count % self.frames_for_update == 0:
                self.canvas.update()
            if self.check_validity(x + 1, y):
                self.passed_val.add((x + 1, y))
                stack.append((x + 1, y))

            if self.check_validity(x - 1, y):
                self.passed_val.add((x - 1, y))
                stack.append((x - 1, y))

            if self.check_validity(x, y + 1):
                self.passed_val.add((x, y + 1))
                stack.append((x, y + 1))

            if self.check_validity(x, y - 1):
                self.passed_val.add((x, y - 1))
                stack.append((x, y - 1))

        print("Done")
        self.canvas.bind("<B1-Motion>", self.paint)
        return

    def paint(self, event):
        self.last_x, self.last_y = event.x, event.y
        oval_size = 10

        self.canvas.create_oval(
            self.last_x - oval_size // 2,
            self.last_y - oval_size // 2,
            self.last_x + oval_size // 2,
            self.last_y + oval_size // 2,
            fill="black",
            outline="black",
        )

        for x in range(self.last_x - oval_size // 2, self.last_x + oval_size // 2 + 1):
            for y in range(
                self.last_y - oval_size // 2, self.last_y + oval_size // 2 + 1
            ):
                if (x - self.last_x) ** 2 + (y - self.last_y) ** 2 <= (
                    oval_size // 2
                ) ** 2:
                    self.boarders.add((x, y))


class Task1cWindow:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.width = 800
        self.height = 600
        self.root.configure(bg=parent.back_ground)

        self.root.title("task1c")
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
