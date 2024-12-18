import pygame
import numpy as np
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Текстурирование 3D-модели")

# Цвета и текстура
WHITE = (255, 255, 255)
texture = pygame.image.load("Texture1.png").convert()
texture = pygame.transform.scale(texture, (256, 256))

# Камера
fov = 256
viewer_distance = 4

# Модели: Куб, Тетраэдр, Октаэдр
MODELS = {
    "cube": {
        "vertices": np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]),
        "faces": [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (0, 3, 7, 4), (1, 2, 6, 5)
        ]
    },
    "tetrahedron": {
        "vertices": np.array([
            [1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]
        ]),
        "faces": [
            (0, 1, 2), (0, 1, 3),
            (0, 2, 3), (1, 2, 3)
        ]
    },
    "octahedron": {
        "vertices": np.array([
            [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]
        ]),
        "faces": [
            (0, 2, 4), (0, 3, 4), (1, 2, 4), (1, 3, 4),
            (0, 2, 5), (0, 3, 5), (1, 2, 5), (1, 3, 5)
        ]
    }
}

def project(vertex):
    x, y, z = vertex
    factor = fov / (z + viewer_distance)
    x_proj = int(x * factor + WIDTH / 2)
    y_proj = int(-y * factor + HEIGHT / 2)
    return x_proj, y_proj

# Трансформация вершин
def transform(vertices, scale, rotation, translation):
    angleX, angleY, angleZ = rotation
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(angleX), -np.sin(angleX)],
        [0, np.sin(angleX), np.cos(angleX)]
    ])
    Ry = np.array([
        [np.cos(angleY), 0, np.sin(angleY)],
        [0, 1, 0],
        [-np.sin(angleY), 0, np.cos(angleY)]
    ])
    Rz = np.array([
        [np.cos(angleZ), -np.sin(angleZ), 0],
        [np.sin(angleZ), np.cos(angleZ), 0],
        [0, 0, 1]
    ])
    vertices = vertices * scale
    vertices = vertices @ Rx @ Ry @ Rz
    vertices += translation
    return vertices

def main():
    current_model = "cube"
    scale = 1.0
    rotation = [0, 0, 0]
    translation = [0, 0, 0]
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_1:
                    current_model = "cube"
                elif event.key == K_2:
                    current_model = "tetrahedron"
                elif event.key == K_3:
                    current_model = "octahedron"
                elif event.key == K_UP:
                    translation[1] += 0.2
                elif event.key == K_DOWN:
                    translation[1] -= 0.2
                elif event.key == K_LEFT:
                    translation[0] -= 0.2
                elif event.key == K_RIGHT:
                    translation[0] += 0.2
                elif event.key == K_w:
                    rotation[0] += 0.1
                elif event.key == K_s:
                    rotation[0] -= 0.1
                elif event.key == K_a:
                    rotation[1] += 0.1
                elif event.key == K_d:
                    rotation[1] -= 0.1
                elif event.key == K_q:
                    scale += 0.1
                elif event.key == K_e:
                    scale -= 0.1

        model = MODELS[current_model]
        vertices = model["vertices"]
        faces = model["faces"]

        # Трансформация и проекция
        transformed_vertices = transform(vertices, scale, rotation, translation)
        projected_vertices = [project(v) for v in transformed_vertices]

        # Отрисовка текстурированных граней
        for face in faces:
            points = [projected_vertices[i] for i in face]
            # Создаем текстурированную поверхность
            min_x = min(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_x = max(p[0] for p in points)
            max_y = max(p[1] for p in points)

            if max_x > min_x and max_y > min_y:
                face_surface = pygame.transform.scale(texture, (max_x - min_x, max_y - min_y))
                screen.blit(face_surface, (min_x, min_y))

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()

if __name__ == "__main__":
    main()
