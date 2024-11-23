#include <GLFW/glfw3.h>
#include <GL/glut.h>
#include <GL/glu.h>
#include <iostream>

float transparency = 1.0f; // Прозрачность (по умолчанию непрозрачный)
bool isMirrored = false;   // Зеркальность (по умолчанию нет)
bool light1Enabled = true; // Первый источник света включен

// Инициализация OpenGL
void initOpenGL()
{
    glEnable(GL_DEPTH_TEST);              // Включаем тест на глубину для правильного отображения 3D объектов
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f); // Цвет фона
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0); // Включаем первый источник света
}

// Настройка источников света
void setupLights()
{
    GLfloat light_position[] = {1.0f, 1.0f, 1.0f, 1.0f};
    GLfloat light_diffuse[] = {1.0f, 1.0f, 1.0f, 1.0f};
    glLightfv(GL_LIGHT0, GL_POSITION, light_position);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse);

    if (light1Enabled)
    {
        glEnable(GL_LIGHT0);
    }
    else
    {
        glDisable(GL_LIGHT0);
    }

    GLfloat second_light_position[] = {-1.0f, 1.0f, -1.0f, 1.0f};
    glLightfv(GL_LIGHT1, GL_POSITION, second_light_position);
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light_diffuse);
    glEnable(GL_LIGHT1);
}

// Рисование куба
void drawCube(float size)
{
    glBegin(GL_QUADS);

    // Передняя грань
    glColor3f(1.0f, 0.0f, 0.0f); // Красный
    glVertex3f(-size, -size, size);
    glVertex3f(size, -size, size);
    glVertex3f(size, size, size);
    glVertex3f(-size, size, size);

    // Задняя грань
    glColor3f(0.0f, 1.0f, 0.0f); // Зеленый
    glVertex3f(-size, -size, -size);
    glVertex3f(-size, size, -size);
    glVertex3f(size, size, -size);
    glVertex3f(size, -size, -size);

    // Остальные грани...

    glEnd();
}

// Рисование шара
void drawSphere(float radius)
{
    glColor3f(0.0f, 0.0f, 1.0f); // Синий
    glutSolidSphere(radius, 50, 50);
}

// Установка зеркального материала
void setMirrorMaterial()
{
    GLfloat mirror[] = {1.0f, 1.0f, 1.0f, 1.0f}; // Белое зеркало
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, mirror);
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 50.0f);
}

// Включение/выключение прозрачности
void setTransparency()
{
    if (transparency < 1.0f)
    {
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    }
    else
    {
        glDisable(GL_BLEND);
    }
}

// Отрисовка сцены
void renderScene()
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); // Очищаем экран
    glLoadIdentity();                                   // Сбрасываем текущую матрицу

    // Настройка камеры
    gluLookAt(0.0f, 0.0f, 5.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f);

    setupLights(); // Настройка источников света

    // Устанавливаем материал для зеркала
    if (isMirrored)
    {
        setMirrorMaterial();
    }

    // Включаем прозрачность, если нужно
    setTransparency();

    // Рисуем куб и шар
    drawCube(1.0f);                 // Куб
    glTranslatef(2.0f, 0.0f, 0.0f); // Перемещаем объект
    drawSphere(0.5f);               // Шар

    glFlush();
    glfwSwapBuffers(); // Отображаем буфер на экране
}

// Обработчик ввода с клавиатуры
void handleKeyPress(GLFWwindow *window, int key, int scancode, int action, int mods)
{
    if (action == GLFW_PRESS)
    {
        if (key == GLFW_KEY_M)
        { // Включение/выключение зеркальности
            isMirrored = !isMirrored;
        }
        if (key == GLFW_KEY_T)
        { // Изменение прозрачности
            transparency = (transparency == 1.0f) ? 0.5f : 1.0f;
        }
        if (key == GLFW_KEY_L)
        { // Включение/выключение второго источника света
            light1Enabled = !light1Enabled;
        }
    }
}

int main()
{
    if (!glfwInit())
    {
        return -1;
    }

    // Создание окна
    GLFWwindow *window = glfwCreateWindow(800, 600, "Cornwell Room", NULL, NULL);
    if (!window)
    {
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);
    initOpenGL();

    // Устанавливаем обработчик ввода с клавиатуры
    glfwSetKeyCallback(window, handleKeyPress);

    // Главный цикл отрисовки
    while (!glfwWindowShouldClose(window))
    {
        renderScene();
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
