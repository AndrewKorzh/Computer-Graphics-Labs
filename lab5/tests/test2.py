import turtle
import random

# Функция для изменения цвета
def get_color(depth, max_depth):
    # Плавный переход от коричневого (ствол) к зеленому (листья)
    r = (139 + (0 - 139) * depth / max_depth) / 255
    g = (69 + (255 - 69) * depth / max_depth) / 255
    b = (19 + (0 - 19) * depth / max_depth) / 255
    return (r, g, b)

# Функция для изменения толщины
def get_thickness(depth, max_depth):
    return max(1, (max_depth - depth) // 2)

# Рисование фрактального дерева с изменяющейся толщиной и цветом
def draw_tree(t, branch_length, angle, depth, max_depth):
    if depth == 0:
        return

    # Настройка цвета и толщины
    color = get_color(depth, max_depth)
    turtle.colormode(1.0)  # Настройка режима цвета для turtle
    t.pencolor(color)
    t.pensize(get_thickness(depth, max_depth))

    # Рисуем ветку
    t.forward(branch_length)

    # Сохраняем текущее состояние (разветвление)
    position, heading = t.position(), t.heading()

    # Рекурсивное рисование левой ветви
    t.left(angle + random.uniform(-15, 15))  # Случайное изменение угла
    draw_tree(t, branch_length * 0.7, angle, depth - 1, max_depth)

    # Возвращаемся к исходной позиции
    t.penup()
    t.setposition(position)
    t.setheading(heading)
    t.pendown()

    # Рекурсивное рисование правой ветви
    t.right(angle + random.uniform(-15, 15))  # Случайное изменение угла
    draw_tree(t, branch_length * 0.7, angle, depth - 1, max_depth)

# Настройка turtle для фрактального дерева
def setup_tree_turtle():
    t = turtle.Turtle()
    t.speed(0)  # Максимальная скорость
    t.left(90)  # Начальное направление вверх (ствол дерева)
    turtle.tracer(0, 0)  # Отключаем анимацию
    return t

# Основная функция для рисования фрактального дерева
def draw_fractal_tree(branch_length=100, angle=30, depth=8):
    t = setup_tree_turtle()
    draw_tree(t, branch_length, angle, depth, depth)
    turtle.update()
    turtle.done()

# Пример использования:
draw_fractal_tree(branch_length=100, angle=25, depth=8)
