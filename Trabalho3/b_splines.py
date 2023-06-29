import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Parâmetros iniciais
k = 0
d = 1
selected_point = None
width, height = 800, 600
degree_range = (0, 5)
degree_step = 1
control_points = np.array([[100 + ((width - 200) / 5) * i, height / 2 + np.random.uniform(-0.5, 0.5) * (height - 200)] for i in range(6)], dtype=np.float32)
nodes = np.arange(12)



# Função B-Spline de Cox-de Boor recursiva
def B(k, d, nodes):
    if d == 0:
        def base(u):
            return 1 if nodes[k] <= u < nodes[k + 1] else 0
        return base
    else:
        Bk0 = B(k, d - 1, nodes)
        Bk1 = B(k + 1, d - 1, nodes)
        def base(u):
            return ((u - nodes[k]) / (nodes[k + d] - nodes[k])) * Bk0(u) + ((nodes[k + d + 1] - u) / (nodes[k + d + 1] - nodes[k + 1])) * Bk1(u)
        return base

# Amostragem da função B-Spline para desenho
def sample_curve(pts, step=0.01):
    n = len(pts)
    b = [B(i, d, nodes) for i in range(n)]
    sample = []
    for u in np.arange(d, n, step):
        sum_point = np.zeros(2, dtype=np.float32)
        for k, p in enumerate(pts):
            w = b[k](u)
            sum_point += w * p
        sample.append(sum_point)
    return sample

# Função de desenho das curvas B-Spline
def draw_curve():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.0, 0.0, 0.0)
    glPointSize(12)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Desenhar pontos de controle
    glBegin(GL_POINTS)
    for point in control_points:
        x, y = point
        glVertex2f(x, y)
    glEnd()

    glColor4f(1.0, 0.0, 0.0, 0.2)
    glPointSize(7)

    # Desenhar curvas B-Spline
    glBegin(GL_POINTS)
    for point in sample_curve(control_points):
        x, y = point
        glVertex2f(x, y)
    glEnd()

    glColor3f(0.0, 0.0, 0.0)

    # Desenhar legendas dos pontos de controle
    for i, point in enumerate(control_points):
        x, y = point
        glRasterPos2f(x + 8, y - 8)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(str(i)))

    glFlush()

# Função para redimensionar a janela
def reshape(w, h):
    global width, height
    width, height = w, h
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)

# Função para lidar com eventos do teclado
def keyboard(key, x, y):
    global d

    if key == b'd':
        d = max(d - degree_step, degree_range[0])
    elif key == b'D':
        d = min(d + degree_step, degree_range[1])

    glutPostRedisplay()

# Função para lidar com eventos do mouse
def mouse(button, state, x, y):
    global selected_point
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            selected_point = None
            y = height - y
            # Verify if click happened over a point
            for i, [px, py] in enumerate(control_points):
                d = np.sqrt((px - x) ** 2 + (py - y) ** 2)
                if d < 12:
                    selected_point = i
                    break
        elif state == GLUT_UP:
            selected_point = None

# Função para lidar com eventos de movimento do mouse
def mouse_motion(x, y):
    global selected_point
    if selected_point is not None:
        y = height - y
        control_points[selected_point] = np.array([x, y], dtype=np.float32)
    glutPostRedisplay()

# Função principal
def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Demo B-Splines")
    glutDisplayFunc(draw_curve)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_motion)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

# Execução do programa
if __name__ == "__main__":
    main()
