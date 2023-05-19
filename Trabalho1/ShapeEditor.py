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
        self.center = points[0] 
        self.set_matrix(m) # Inicializa a matriz de transformações com a matriz fornecida ou a matriz identidade

    def set_point (self, i, p):
        self.points[i] = p
        self.set_center(self.points)
        
    def set_center(self, points): # Atualiza o atributo que contem o centro do retangulo
        self.center = [(points[0][0] + points[1][0])/2, 
                        (points[1][1] + points[0][1])/2]

    def set_matrix(self,t):
        self.m = t
        self.invm = inverse(t)

    def contains(self,p):
        p = apply_to_vector(self.invm, [p[0],p[1],0,1])
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
        self.set_matrix(m)

    def set_center(self, center):
        self.center = center

    def set_radius(self, radius):
        self.radius = radius

    def set_matrix(self, t): # Aplicar ransformação 
        self.m = t
        self.invm = inverse(t)

    def contains(self, p):
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
modeConstants = ["CREATE RECT", "CREATE CIRCLE", "TRANSLATE", "ROTATE"]
mode = modeConstants[0]

def reshape( width, height):
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,width,height,0)
    glMatrixMode (GL_MODELVIEW)

def mouse (button, state, x, y): # Ação após primeiro clique
    global lastx,lasty,picked
    if state!=GLUT_DOWN: return
    if mode == "CREATE RECT":
        shapes.append(Rect([[x,y],[x,y]]))
    elif mode == "CREATE CIRCLE":
        shapes.append(Circle([x, y], 0))
    elif mode == "TRANSLATE":
        picked = None
        for s in shapes:
            if s.contains([x,y]): picked = s
        lastx,lasty = x,y 
    elif mode == "ROTATE":
        picked = None
        for s in shapes:
            if s.contains([x,y]): picked = s
        lastx,lasty = x,y 

def mouse_drag(x, y): # Ação durante arrastar do mouse
    global lastx,lasty
    if mode == "CREATE RECT":
        shapes[-1].set_point(1,[x,y])
    elif mode == "CREATE CIRCLE":
        dx = x - shapes[-1].center[0]
        dy = y - shapes[-1].center[1]
        radius = math.sqrt(dx * dx + dy * dy)
        shapes[-1].set_radius(radius)
    elif mode == "TRANSLATE":
        if picked:
            t = create_from_translation([x-lastx,y-lasty,0])
            picked.set_matrix(multiply(picked.m,t))
            lastx, lasty = x, y
    elif mode == "ROTATE":
        if picked:
            # Vetores entre o ponto clicado e o centro da forma
            last_vector = [lastx - picked.center[0], lasty - picked.center[1]]
            current_vector = [x - picked.center[0], y - picked.center[1]]

            angle = (math.atan2(current_vector[1], current_vector[0]) 
                     - math.atan2(last_vector[1], last_vector[0]))

            # Traz a forma para o centro do eixo, rotaciona e a leva de volta
            t = create_from_translation([-picked.center[0], -picked.center[1], 0])
            rotation_matrix = create_from_eulers([0, -angle, 0])
            rt = create_from_translation([picked.center[0], picked.center[1], 0])
            transform_matrix = t @ rotation_matrix @ rt
            picked.set_matrix(picked.m @ transform_matrix)
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
