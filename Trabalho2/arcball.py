
from math import *
import vector

__all__ = ["ArcBall"]

class ArcBall(object):
    """Implements an arcball manipulator for specifying rotations."""
    
    def __init__(self, center, radius):
        """Creates a new arcball manipulator. 
        @param center: Center point of the sphere (in window coordinates).
        @param radius: Radius of the sphere (in window coordinates).
        """
        self.center = center
        self.radius = radius
        
    def _rotby2vectors (self, startvector, endvector):
        """Given two unit vectors returns the rotation axis and rotation angle 
        that maps the first onto the second.
        @param startvector: original vector.
        @param endvector: destination vector.
        @return: (angle,axis).
        """
        r = vector.cross(startvector, endvector)
        l = vector.length (r)
        if l<1e-10: return 0,(0,0,1)
        angle = acos(vector.dot(startvector,endvector))
        #angle = asin (l)
        axis = vector.scale(r,1.0/l)
        return (angle,axis)
    
    def _projvector (self, x, y):
        """Given a ray with origin (x,y,inf) and direction (0,0,-inf), translate
        it to the arcball's local coordinate system and return the intersection
        point with that sphere of unit radius and centered at the origin. If no 
        intersection exists, intersect it with the plane z=0 and project that
        that point onto the unit sphere.
        @param x,y: coordinates for the ray.
        @return: projected vector.
        """
        v = vector.scale ((x-self.center[0],y-self.center[1],0.0), 1.0/self.radius)
        l = vector.length(v)
        if l>=1.0: return vector.scale(v,1.0/l)
        z = sqrt (1.0 - l*l)
        return (v[0],v[1],z)
                
    def rot (self, x0, y0, x1, y1):
        """Given two screen points, returns the arcball rotation that maps
        the first onto the second.
        @param x0,y0: first point.
        @param x1,y1: second point.
        @return: (angle,axis).
        """
        return self._rotby2vectors (self._projvector(x0,y0), self._projvector(x1,y1))
    
if __name__=="__main__":
    # A simple test
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    width,height = 500,500
    
    def display ():
        glClear (GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixd (matrix)
        glutSolidCube (1)
        glutSwapBuffers()
        
    def init():
        glPolygonMode (GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_CULL_FACE)
        global matrix 
        matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        
    def reshape (w, h):
        global width,height
        width,height = w,h
        glViewport (0, 0, w, h);
        glMatrixMode (GL_PROJECTION);
        glLoadIdentity()
        glOrtho (-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();
    
    def mousepress (button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                global arcball
                arcball = ArcBall ((width/2,height/2,0), width/2)
                global startx, starty
                startx, starty = x,y
                glutMotionFunc (rotatecallback)
            else:
                glutMotionFunc (None)
                
    def rotatecallback (x, y):
        global startx,starty,matrix
        angle, axis = arcball.rot (startx, height - starty, x, height - y)
        glLoadIdentity ()
        glRotatef (degrees(angle),*axis)
        glMultMatrixd (matrix)
        matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        startx,starty = x,y
        glutPostRedisplay()
        
    glutInit([]) 
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_STENCIL)
    glutInitWindowSize(width, height)
    glutCreateWindow("Test")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mousepress)
    
    init()
    glutMainLoop()

