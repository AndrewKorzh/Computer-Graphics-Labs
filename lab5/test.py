import turtle
import random
import sys
import math  # Добавлен импорт модуля math
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk


class LSystem:
    def __init__(self, axiom, angle, rules):
        self.axiom = axiom
        self.angle = angle
        self.rules = rules

    def generate(self, iterations):
        current = self.axiom
        for _ in range(iterations):
            next_seq = ""
            for char in current:
                next_seq += self.rules.get(char, char)
            current = next_seq
        return current


class LSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("L-System Фрактал")
        self.root.geometry("1000x700")  # Увеличенная ширина окна
        self.root.resizable(False, False)

        # Создание фрейма для ввода грамматики
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        # Метка для инструкции
        instruction = ttk.Label(
            input_frame,
            text="Введите грамматику L-системы:",
            wraplength=300,
            justify=tk.LEFT,
        )
        instruction.pack(pady=(0, 10))

        # Поле для ввода грамматики
        self.grammar_input = scrolledtext.ScrolledText(
            input_frame,
            width=35,
            height=30,
            wrap=tk.WORD,  # Уменьшенная ширина и увеличенная высота
        )
        self.grammar_input.pack()

        # Кнопка для рисования
        draw_button = ttk.Button(
            input_frame, text="Рисовать Фрактал", command=self.draw_fractal
        )
        draw_button.pack(pady=10)

        # Создание фрейма для рисования
        draw_frame = ttk.Frame(self.root)
        draw_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Настройка холста для turtle
        self.canvas = tk.Canvas(
            draw_frame, width=700, height=700, bg="white"
        )  # Увеличенная ширина холста
        self.canvas.pack()

        # Настройка turtle
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.tracer(0, 0)  # Отключаем автоматическое обновление
        self.t = turtle.RawTurtle(self.screen)
        self.t.hideturtle()
        self.t.speed(0)

    def parse_grammar(self, grammar_text):
        lines = grammar_text.strip().split("\n")
        if len(lines) < 2:
            raise ValueError(
                "Грамматика должна содержать как минимум аксиому и одну правило."
            )

        # Первая строка: <аксиома> <угол поворота> <начальное направление>
        first_line = lines[0].strip().split()
        if len(first_line) != 3:
            raise ValueError(
                "Первая строка должна содержать аксиому, угол поворота и начальное направление."
            )
        axiom, angle, direction = first_line
        try:
            angle = float(angle)
        except ValueError:
            raise ValueError("Угол поворота должен быть числом.")

        try:
            direction = float(direction)  # Преобразуем direction в float
        except ValueError:
            raise ValueError("Начальное направление должно быть числом.")

        # Остальные строки: правила замены
        rules = {}
        for line in lines[1:]:
            parts = line.strip().split("->")
            if len(parts) != 2:
                continue  # Игнорируем некорректные строки
            key = parts[0].strip()
            value = parts[1].strip()
            rules[key] = value

        return axiom, angle, direction, rules

    def simulate_drawing(self, instructions, angle):
        """
        Симулирует рисование фрактала без отрисовки, чтобы определить границы.
        Возвращает минимальные и максимальные координаты.
        """
        stack = []
        x, y = 0, 0
        heading = 90  # Начальное направление вверх
        min_x = max_x = x
        min_y = max_y = y

        for cmd in instructions:
            if cmd == "F" or cmd == "f":
                # Вычисляем новое положение
                rad_heading = math.radians(heading)
                # Добавим небольшую случайность для естественности
                distance = 5 * 1 * random.uniform(0.9, 1.1)
                dx = distance * math.cos(rad_heading)
                dy = distance * math.sin(rad_heading)
                x += dx
                y += dy

                # Обновляем границы
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
            elif cmd == "+":
                heading -= angle + random.uniform(-angle * 0.1, angle * 0.1)
            elif cmd == "-":
                heading += angle + random.uniform(-angle * 0.1, angle * 0.1)
            elif cmd == "[":
                stack.append((x, y, heading))
            elif cmd == "]":
                if stack:
                    x, y, heading = stack.pop()
                else:
                    raise ValueError("Неправильная структура скобок в грамматике.")

        return min_x, max_x, min_y, max_y

    def draw_fractal(self):
        grammar_text = self.grammar_input.get("1.0", tk.END)
        try:
            axiom, angle, direction, rules = self.parse_grammar(grammar_text)
        except ValueError as ve:
            messagebox.showerror("Ошибка грамматики", str(ve))
            return

        # Генерация инструкции
        lsys = LSystem(axiom, angle, rules)
        iterations = self.get_iterations()
        instructions = lsys.generate(iterations=iterations)

        try:
            # Симулируем рисование для определения границ
            min_x, max_x, min_y, max_y = self.simulate_drawing(instructions, angle)
        except ValueError as ve:
            messagebox.showerror("Ошибка при симуляции", str(ve))
            return

        # Вычисляем масштаб, чтобы фрактал помещался в холст с отступами
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        fractal_width = max_x - min_x
        fractal_height = max_y - min_y

        if fractal_width == 0 or fractal_height == 0:
            scale = 1
        else:
            scale_x = (canvas_width - 40) / fractal_width
            scale_y = (canvas_height - 40) / fractal_height
            scale = min(scale_x, scale_y)

        # Очистка предыдущего рисунка
        self.t.reset()
        self.t.hideturtle()
        self.screen.update()

        # Настройка начальной позиции для центрирования
        self.t.penup()
        # Центрируем фрактал
        self.t.goto(
            -(min_x + fractal_width / 2) * scale, -(min_y + fractal_height / 2) * scale
        )
        self.t.setheading(direction)  # Устанавливаем начальное направление
        self.t.pendown()

        # Подготовка к рисованию
        stack = []
        self.t.speed(0)
        self.t.hideturtle()

        for cmd in instructions:
            if cmd == "F":
                self.t.forward(5 * scale)
            elif cmd == "f":
                self.t.penup()
                self.t.forward(5 * scale)
                self.t.pendown()
            elif cmd == "+":
                self.t.right(angle + random.uniform(-angle * 0.1, angle * 0.1))
            elif cmd == "-":
                self.t.left(angle + random.uniform(-angle * 0.1, angle * 0.1))
            elif cmd == "[":
                # Сохранить состояние: позиция и направление
                pos = self.t.position()
                heading = self.t.heading()
                stack.append((pos, heading))
            elif cmd == "]":
                if stack:
                    pos, heading = stack.pop()
                    self.t.penup()
                    self.t.goto(pos)
                    self.t.setheading(heading)
                    self.t.pendown()
                else:
                    messagebox.showerror(
                        "Ошибка", "Неправильная структура скобок в инструкции."
                    )
                    return

        self.screen.update()

    def get_iterations(self):
        # Определите количество итераций в зависимости от длины или других параметров
        # Для простоты используем фиксированное значение
        return 5

    def calculate_scale(self, instructions, angle, length=5):
        # Этот метод больше не нужен, так как мы реализовали масштабирование в draw_fractal
        return 1


def main():
    root = tk.Tk()
    gui = LSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
