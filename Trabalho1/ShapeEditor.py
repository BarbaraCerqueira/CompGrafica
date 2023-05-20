import sys
import math
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *

shapes = []

# Definindo Retangulo
class Rect(object):
    def __init__ (self, points, m = create_identity()):
        self.points = points # points[0] = vertice superior à esquerda; points[1] = vertice inferior à direita
        self.set_matrix(m) # Inicializa a matriz de transformações

    def set_point (self, i, p):
        self.points[i] = p
        
    def get_center(self): # Retorna o centro da forma transformada
        center = [(self.points[0][0] + self.points[1][0])/2, 
                        (self.points[1][1] + self.points[0][1])/2]
        trans_center = apply_to_vector(self.m, [center[0],center[1],0,1])
        return trans_center

    def set_matrix(self,t): # Aplicar transformação 
        self.m = t
        self.invm = inverse(t)

    def contains(self,p): # Verifica se o ponto está contido na forma
        p = apply_to_vector(self.invm, [p[0],p[1],0,1]) # Desfaz a transformação para verificar o contain
        xmin = min(self.points[0][0],self.points[1][0])
        xmax = max(self.points[0][0],self.points[1][0])
        ymin = min(self.points[0][1],self.points[1][1])
        ymax = max(self.points[0][1],self.points[1][1])
        return xmin <= p[0] <= xmax and ymin <=p[1] <= ymax
    
    def draw (self):
        glPushMatrix()
        glMultMatrixf(self.m)
        glRectf(*self.points[0],*self.points[1])
        glPopMatrix()

#Definindo Circulo
class Circle(object):
    def __init__(self, center, radius, m=create_identity()):
        self.center = center
        self.radius = radius
        self.set_matrix(m) # Inicializa a matriz de transformações

    def get_center(self): # Retorna o centro da forma transformada
        trans_center = apply_to_vector(self.m, [self.center[0],self.center[1],0,1])
        return trans_center

    def set_radius(self, radius):
        self.radius = radius

    def set_matrix(self, t): # Aplicar transformação 
        self.m = t
        self.invm = inverse(t)

    def contains(self, p): # Verifica se o ponto está contido na forma
        p = apply_to_vector(self.invm, [p[0], p[1], 0, 1]) # Desfaz a transformação para verificar o contain
        dx = p[0] - self.center[0]
        dy = p[1] - self.center[1]
        return dx * dx + dy * dy <= self.radius * self.radius

    def draw(self): # Desenha o círculo como um polígono
        glPushMatrix()
        glMultMatrixf(self.m)
        glBegin(GL_POLYGON)
        vertices = np.linspace(0,360,1000) # Usando 1000 - 1 vertices
        for i in vertices:
            angle = 2 * math.pi * i / 360
            x = self.center[0] + self.radius * math.cos(angle)
            y = self.center[1] + self.radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        glPopMatrix()

picked = None
modeConstants = ["CREATE RECT", "CREATE CIRCLE", "TRANSLATE", "ROTATE", "SCALE"]
mode = modeConstants[0]

def reshape( width, height):
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,height,0)
    glMatrixMode (GL_MODELVIEW)

def mouse (button, state, x, y): # Ação após primeiro clique
    global lastx,lasty,picked,firstx,firsty
    if state!=GLUT_DOWN: return
    if mode == "CREATE RECT":
        shapes.append(Rect([[x,y],[x,y]]))
    elif mode == "CREATE CIRCLE":
        shapes.append(Circle([x, y], 0))
    elif mode == "TRANSLATE":
        picked = None
        for s in shapes:
            if s.contains([x,y]): 
                picked = s
        lastx,lasty = x,y 
    elif mode == "ROTATE":
        picked = None
        for s in shapes:
            if s.contains([x,y]): 
                picked = s
        lastx,lasty = x,y 
    elif mode == "SCALE":
        picked = None
        for s in shapes:
            if s.contains([x, y]):
                picked = s
        lastx,lasty = x,y
        firstx,firsty = x,y

def mouse_drag(x, y): # Ação durante arrastar do mouse
    global lastx,lasty,firstx,firsty
    if mode == "CREATE RECT":
        shapes[-1].set_point(1,[x,y])
    elif mode == "CREATE CIRCLE":
        dx = x - shapes[-1].center[0]
        dy = y - shapes[-1].center[1]
        radius = math.sqrt(dx * dx + dy * dy)
        shapes[-1].set_radius(radius)
    elif mode == "TRANSLATE":
        if picked:
            t = create_from_translation([x-lastx, y-lasty, 0])
            picked.set_matrix(multiply(picked.m,t))
            lastx, lasty = x, y
    elif mode == "ROTATE":
        if picked:
            center = picked.get_center()

            # Vetores entre o ponto clicado e o centro da forma
            last_vector = [lastx - center[0], lasty - center[1]]
            current_vector = [x - center[0], y - center[1]]

            angle = (math.atan2(current_vector[1], current_vector[0]) 
                     - math.atan2(last_vector[1], last_vector[0]))

            # Traz a forma para o centro do eixo, rotaciona e a leva de volta
            t = create_from_translation([-center[0], -center[1], 0])
            rotation_matrix = create_from_eulers([0, -angle, 0])
            rt = create_from_translation([center[0], center[1], 0])
            transform_matrix = t @ rotation_matrix @ rt

            picked.set_matrix(picked.m @ transform_matrix) # Aplica transformação
            lastx, lasty = x, y
    elif mode == "SCALE":
        if picked:
            center = picked.get_center()
            if center[0] != firstx or center[1] != firsty:
                scale_axis = np.array([firstx - center[0], firsty - center[1]]) # Eixo de escala definido pelo primeiro clique
                angle_to_x = -math.atan2(scale_axis[1], scale_axis[0]) # Angulo entre o eixo de escalonamento e o eixo X, padrão antihorario

                # Vetores do centro da forma até os pontos de clique atual e anterior do mouse
                mouse_axis = np.array([x - center[0], y - center[1]])
                last_mouse_axis = np.array([lastx - center[0], lasty - center[1]])

                # Projeção dos vetores do mouse sobre o eixo de escala
                proj = np.dot(mouse_axis, scale_axis) / np.linalg.norm(scale_axis)
                last_proj = np.dot(last_mouse_axis, scale_axis) / np.linalg.norm(scale_axis)

                scale_factor = proj/last_proj

                # Traz a forma para o centro do eixo, alinha o eixo de escala com o eixo X, escalona e retorna
                t = create_from_translation([-center[0], -center[1], 0])
                rot = create_from_eulers([0, -angle_to_x, 0])
                scale_matrix = create_from_scale([scale_factor, 1, 1])
                rrot = create_from_eulers([0, angle_to_x, 0])
                rt = create_from_translation([center[0], center[1], 0])
                transform_matrix = t @ rot @ scale_matrix @ rrot @ rt

                picked.set_matrix(picked.m @ transform_matrix) # Aplica transformação
                lastx, lasty = x, y
       
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    for s in shapes:
        glColor3f(0.4,0.4,0.4)
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
        s.draw()
        glColor3f(1,0,1)
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        s.draw()
    glutSwapBuffers()

def createMenu():
    def domenu(item):
        global mode
        mode = modeConstants[item]
        return 0
    glutCreateMenu(domenu)
    for i,name in enumerate(modeConstants):
        glutAddMenuEntry(name, i)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

glutInit(sys.argv)
glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize (800, 600)
glutCreateWindow ("Shape Editor")
glutMouseFunc(mouse)
glutMotionFunc(mouse_drag)
glutDisplayFunc(display)
glutReshapeFunc(reshape)
createMenu()
glutMainLoop()
