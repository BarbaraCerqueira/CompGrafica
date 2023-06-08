import sys
import random
import numpy as np
from math import degrees
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL  import Image
from arcball import ArcBall

# Selected object
selected = []

# Set of removed objects
removed = set()

# size of cube array
n = 3

# Window dimensions
width, height = 800, 800

''' Stores each occurrence of cube click animation currently happening.
    Click animation happens when any cube is clicked even if mouse button is not released.
    Each cube name (key) is associated with a list containing its removal direction, current step size
    and a boolean variable that indicates if it is bouncing forward (True) or returning (False). '''
click_animation = dict()

''' Stores each occurrence of removal animation currently happening.
    Removal will only happen if mouse doesn't drag after click and no other cube is blocking the removal direction.
    Each cube name (key) is associated with a list containing its removal direction and current step size. '''
removal_animation = dict()

# Total distance the cube will travel during removal animation (equal or less than perspective 'far' parameter)
removal_distance = 7 

# Total distance the cube will travel during click animation (no more than distance between cubes)
click_distance = 0.2 * 1/n

# Texture coordinates for each cube removal direction
tex_coord = {
    # Front direction
    1: [[(0.0, 0.8),(1.0, 0.8),(1.0, 1.0),(0.0, 1.0)], # front face (blank -> white area of the image)
        [(0.0, 0.0),(1.0, 0.0),(1.0, 0.2),(0.0, 0.2)], # back face (colored -> blue area of the image)
        [(1.0, 1.0),(0.0, 1.0),(0.0, 0.0),(1.0, 0.0)], # top face
        [(1.0, 1.0),(0.0, 1.0),(0.0, 0.0),(1.0, 0.0)], # bottom face
        [(0.0, 1.0),(0.0, 0.0),(1.0, 0.0),(1.0, 1.0)], # right face
        [(1.0, 0.0),(1.0, 1.0),(0.0, 1.0),(0.0, 0.0)]], # left face
    # Back direction
    2: [[(0.0, 0.0),(1.0, 0.0),(1.0, 0.2),(0.0, 0.2)], # front face (colored)
        [(0.0, 0.8),(1.0, 0.8),(1.0, 1.0),(0.0, 1.0)], # back face (blank)
        [(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)], # top face
        [(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)], # bottom face
        [(1.0, 0.0),(1.0, 1.0),(0.0, 1.0),(0.0, 0.0)], # right face
        [(0.0, 1.0),(0.0, 0.0),(1.0, 0.0),(1.0, 1.0)]], # left face
    # Top direction
    3: [[(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)], # front face
        [(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)], # back face
        [(0.0, 0.8),(1.0, 0.8),(1.0, 1.0),(0.0, 1.0)], # top face (blank)
        [(0.0, 0.0),(1.0, 0.0),(1.0, 0.2),(0.0, 0.2)], # bottom face (colored)
        [(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)], # right face
        [(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)]], # left face
    # Bottom direction
    4: [[(1.0, 1.0),(0.0, 1.0),(0.0, 0.0),(1.0, 0.0)], # front face
        [(1.0, 1.0),(0.0, 1.0),(0.0, 0.0),(1.0, 0.0)], # back face
        [(0.0, 0.0),(1.0, 0.0),(1.0, 0.2),(0.0, 0.2)], # top face (colored)
        [(0.0, 0.8),(1.0, 0.8),(1.0, 1.0),(0.0, 1.0)], # bottom face (blank)
        [(1.0, 1.0),(0.0, 1.0),(0.0, 0.0),(1.0, 0.0)], # right face
        [(1.0, 1.0),(0.0, 1.0),(0.0, 0.0),(1.0, 0.0)]], # left face 
    # Right direction
    5: [[(1.0, 0.0),(1.0, 1.0),(0.0, 1.0),(0.0, 0.0)], # front face
        [(0.0, 1.0),(0.0, 0.0),(1.0, 0.0),(1.0, 1.0)], # back face
        [(1.0, 0.0),(1.0, 1.0),(0.0, 1.0),(0.0, 0.0)], # top face
        [(0.0, 1.0),(0.0, 0.0),(1.0, 0.0),(1.0, 1.0)], # bottom face
        [(0.0, 0.8),(1.0, 0.8),(1.0, 1.0),(0.0, 1.0)], # right face (blank)
        [(0.0, 0.0),(1.0, 0.0),(1.0, 0.2),(0.0, 0.2)]], # left face (colored)
    # Left direction
    6: [[(0.0, 1.0),(0.0, 0.0),(1.0, 0.0),(1.0, 1.0)], # front face
        [(1.0, 0.0),(1.0, 1.0),(0.0, 1.0),(0.0, 0.0)], # back face
        [(0.0, 1.0),(0.0, 0.0),(1.0, 0.0),(1.0, 1.0)], # top face
        [(1.0, 0.0),(1.0, 1.0),(0.0, 1.0),(0.0, 0.0)], # bottom face
        [(0.0, 0.0),(1.0, 0.0),(1.0, 0.2),(0.0, 0.2)], # right face (colored)
        [(0.0, 0.8),(1.0, 0.8),(1.0, 1.0),(0.0, 1.0)]] # left face (blank)
}

def find_cube_coord(name):
    ''' Finds coordinates (i,j,k) of cube relative to the big cube '''
    global n
    i = name // n**2  # front-back direction
    remainder = name % n**2  
    j = remainder // n  # top-bottom direction 
    k = remainder % n  # left-right direction
    return i,j,k

def find_cube_name(i,j,k):
    ''' Finds name of cube from (i,j,k) coordinates '''
    return i * n**2 + j * n + k

def generate_random_directions():
    ''' Generates random cube removal directions as the following:
    1: front; 2: back; 3:top; 4: bottom; 5: right; 6: left '''
    # Generates random directions
    directions = []
    for name in range(n**3):
        random_dir = random.randint(1, 6)
        directions += [random_dir]       
    return directions

def validate_directions(directions):
    ''' Verifies if there isn't cycles in the system making it impossible to be solved. If there is, 
        changes directions vector to appropriate values. Returns the corrected directions array. '''
    
    available_directions = [1,2,3,4,5,6]
    
    ''' Verifying existence of cycles among immediate and non immediate cubes (other intercalating cubes exist inside the cycle)
    Due to system configuration, game must be solvable regardless the order in which the cubes are deleted. Thus, we can verify 
    solvability by simulating a random deletion order. Here, cubes are deleted one by one in a loop as long as they are not blocked 
    by another cube. If cubes can no longer be removed and system is not solved, it means a cycle exists. In this case, the cubes 
    blocked will have their directions randomized again in directions array until all (or all minus one) cubes are removed. '''
    removed_cubes = set() # Stores coordinates of removed cubes during simulation
    while len(removed_cubes) < n**3 - 1: # Repeat until only one or no cube is left
        removal_count = 0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    current_cube = i,j,k
                    cube_name = find_cube_name(*current_cube)
                    if current_cube in removed_cubes:
                        continue
                    else:
                        # Jump to next non eliminated cube in the same direction. If there isn't one, next will be 'None', meaning cube is free
                        next_cube = get_next_cube(current_cube,directions[cube_name])
                        while next_cube in removed_cubes:
                            next_cube = get_next_cube(next_cube,directions[cube_name])
                        if next_cube == None:
                            removed_cubes.add(current_cube)
                            removal_count += 1
        if removal_count > 0: # At least one cube was removed, no cycle detected yet
            continue
        else: # Cycle detected, cubes are blocked
            for cube in range(n**3):
                if find_cube_coord(cube) not in removed_cubes:
                    current_direction = directions[cube]
                    directions[cube] = random.choice([x for x in available_directions if x != current_direction])
    return directions

def get_next_cube(cube, direction):
    ''' Gets coordinates of cube pointed to '''
    i, j, k = cube
    if direction == 1:  # Front
        if k == n - 1:
            return None
        return i, j, k + 1
    elif direction == 2:  # Back
        if k == 0:
            return None
        return i, j, k - 1
    elif direction == 3:  # Top
        if j == n - 1:
            return None
        return i, j + 1, k
    elif direction == 4:  # Bottom
        if j == 0:
            return None
        return i, j - 1, k
    elif direction == 5:  # Right
        if i == n - 1:
            return None
        return i + 1, j, k
    elif direction == 6:  # Left
        if i == 0:
            return None
        return i - 1, j, k

''' GLOBAL - Random cube directions validated to ensure system's solvability.
    Index of each direction is equivalent to its associated cube name. '''
directions = validate_directions(generate_random_directions())


def loadTexture(filename):
    "Loads an image from a file as a texture"

    # Read file and get pixels
    imagefile = Image.open(filename)
    sx,sy = imagefile.size[0:2]
    global pixels
    pixels = imagefile.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    # Create an OpenGL texture name and load image into it
    image = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, image)  
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, sx, sy, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)
    
    # Set other texture mapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    # Return texture name (an integer)
    return image


def draw_scene(flatColors = False):
    "Draws the scene emitting a 'name' for each cube"
    global n, directions, removal_animation, click_animation, textureId_arrow, matrix
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -3)
    glRotatef(-80, 1, 0, 0)
    glMultMatrixd (matrix)
    size = 1 / n
    for i in range(n):
        x = i - (n - 1) / 2
        for j in range(n):
            y = j - (n - 1) / 2
            for k in range(n):
                z = k - (n - 1) / 2
                name = (i * n + j) * n + k  # Number associated to each cube, from 0 to (n^3-1)
                if flatColors:
                    glColor3f((i+1)/n, (j+1)/n, (k+1)/n)
                # Ignore removed objects
                if name in removed:
                    continue
                glLoadName(name)
                glPushMatrix()
                glTranslatef(x * size, y * size, z * size)

                if name in removal_animation:
                    removal_direction = removal_animation.get(name)[0]
                    removal_step = removal_animation.get(name)[1]

                    if removal_direction == 1:  # Front
                        glTranslatef(0, 0, removal_step)
                    elif removal_direction == 2:  # Back
                        glTranslatef(0, 0, -removal_step)
                    elif removal_direction == 3:  # Top
                        glTranslatef(0, removal_step, 0)
                    elif removal_direction == 4:  # Bottom
                        glTranslatef(0, -removal_step, 0)
                    elif removal_direction == 5:  # Right
                        glTranslatef(removal_step, 0, 0)
                    elif removal_direction == 6:  # Left
                        glTranslatef(-removal_step, 0, 0)
                
                elif name in click_animation:
                    click_direction = click_animation.get(name)[0]
                    click_step = click_animation.get(name)[1]

                    if click_direction == 1:  # Front
                        glTranslatef(0, 0, click_step)
                    elif click_direction == 2:  # Back
                        glTranslatef(0, 0, -click_step)
                    elif click_direction == 3:  # Top
                        glTranslatef(0, click_step, 0)
                    elif click_direction == 4:  # Bottom
                        glTranslatef(0, -click_step, 0)
                    elif click_direction == 5:  # Right
                        glTranslatef(click_step, 0, 0)
                    elif click_direction == 6:  # Left
                        glTranslatef(-click_step, 0, 0)

                if flatColors:
                    glutSolidCube(size*0.8)
                else:
                    # Bind the texture and enable texture mapping
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, textureId_arrow)

                    # Draw each face of the cube with the texture applied
                    glBegin(GL_QUADS)
                    
                    dir = directions[name]

                    # Front Face
                    glNormal3f(0, 0, 1)
                    glTexCoord2f(*tex_coord[dir][0][0]) 
                    glVertex3f(-size*0.8/2, -size*0.8/2, size*0.8/2)  # Bottom Left Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][0][1])
                    glVertex3f(size*0.8/2, -size*0.8/2, size*0.8/2)  # Bottom Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][0][2])
                    glVertex3f(size*0.8/2, size*0.8/2, size*0.8/2)  # Top Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][0][3])
                    glVertex3f(-size*0.8/2, size*0.8/2, size*0.8/2)  # Top Left Of The Texture and Quad

                    # Back Face
                    glNormal3f(0,0,-1)
                    glTexCoord2f(*tex_coord[dir][1][0])
                    glVertex3f(size*0.8/2, -size*0.8/2, -size*0.8/2)  # Bottom Left Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][1][1])
                    glVertex3f(-size*0.8/2, -size*0.8/2, -size*0.8/2)  # Bottom Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][1][2])
                    glVertex3f(-size*0.8/2, size*0.8/2, -size*0.8/2)  # Top Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][1][3])
                    glVertex3f(size*0.8/2, size*0.8/2, -size*0.8/2)  # Top Left Of The Texture and Quad

                    # Top Face
                    glNormal3f(0,1,0)
                    glTexCoord2f(*tex_coord[dir][2][0])
                    glVertex3f(-size*0.8/2, size*0.8/2, size*0.8/2)  # Bottom Left Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][2][1])
                    glVertex3f(size*0.8/2, size*0.8/2, size*0.8/2)  # Bottom Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][2][2])
                    glVertex3f(size*0.8/2, size*0.8/2, -size*0.8/2)  # Top Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][2][3])
                    glVertex3f(-size*0.8/2, size*0.8/2, -size*0.8/2)  # Top Left Of The Texture and Quad

                    # Bottom Face
                    glNormal3f(0,-1,0)
                    glTexCoord2f(*tex_coord[dir][3][0])
                    glVertex3f(size*0.8/2, -size*0.8/2, size*0.8/2)  # Bottom Left Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][3][1])
                    glVertex3f(-size*0.8/2, -size*0.8/2, size*0.8/2)  # Bottom Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][3][2])
                    glVertex3f(-size*0.8/2, -size*0.8/2, -size*0.8/2)  # Top Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][3][3])
                    glVertex3f(size*0.8/2, -size*0.8/2, -size*0.8/2)  # Top Left Of The Texture and Quad

                    # Right face
                    glNormal3f(1,0,0)
                    glTexCoord2f(*tex_coord[dir][4][0])
                    glVertex3f(size*0.8/2, -size*0.8/2, size*0.8/2)  # Bottom Left Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][4][1])
                    glVertex3f(size*0.8/2, -size*0.8/2, -size*0.8/2)  # Bottom Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][4][2])
                    glVertex3f(size*0.8/2, size*0.8/2, -size*0.8/2)  # Top Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][4][3])
                    glVertex3f(size*0.8/2, size*0.8/2, size*0.8/2)  # Top Left Of The Texture and Quad

                    # Left Face
                    glNormal3f(-1,0,0)
                    glTexCoord2f(*tex_coord[dir][5][0])
                    glVertex3f(-size*0.8/2, -size*0.8/2, -size*0.8/2)  # Bottom Left Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][5][1])
                    glVertex3f(-size*0.8/2, -size*0.8/2, size*0.8/2)  # Bottom Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][5][2])
                    glVertex3f(-size*0.8/2, size*0.8/2, size*0.8/2)  # Top Right Of The Texture and Quad
                    glTexCoord2f(*tex_coord[dir][5][3])
                    glVertex3f(-size*0.8/2, size*0.8/2, -size*0.8/2)  # Top Left Of The Texture and Quad

                    glEnd()

                    # Disable texture mapping
                    glDisable(GL_TEXTURE_2D)

                glPopMatrix()


def update_removal_animation():
    "Updates values for cube removal animation"
    global removal_distance, removed, selected, removal_animation

    if removal_animation: # Verifies if any animation is happening
        for name in removal_animation.copy():
            # Update the step size, that is, the distance the cube will travel every frame
            animation_info = removal_animation.get(name)
            animation_info[1] += 0.07 # Step size

            if animation_info[1] >= removal_distance:
                # Remove the cube from the scene
                removed.add(name)
                del removal_animation[name]


def update_click_animation():
    "Updates values for cube click animation"
    global click_distance, removed, selected, click_animation

    if click_animation: # Verifies if any animation is happening
        for name in click_animation.copy():
            animation_info = click_animation.get(name)
            
            if animation_info[2] == True: # Way forward
                animation_info[1] += 0.01 # Updates step size
                if animation_info[1] >= click_distance: 
                    animation_info[2] = False # Change direction

            if animation_info[2] == False: # Way back
                animation_info[1] -= 0.01 # Updates step size
                if animation_info[1] <= 0.0:
                    del click_animation[name] # Ends animation


def draw_win():
    "Draws rectangle covering the whole window textured with 'You win!' image"
    global textureId_win

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)  
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glBindTexture(GL_TEXTURE_2D, textureId_win)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glEnable(GL_TEXTURE_2D)

    # Draw rectangle
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0, 0)           # Bottom Left 
    glTexCoord2f(1.0, 0.0)
    glVertex2f(width, 0)       # Bottom Right 
    glTexCoord2f(1.0, 1.0)
    glVertex2f(width, height)  # Top Right
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0, height)      # Top Left
    glEnd()
    
    glDisable(GL_TEXTURE_2D)


def display():
    if len(removed) < n ** 3:
        draw_scene()
    else:
        draw_win()
    glutSwapBuffers()


def init():
    global textureId_arrow, textureId_win
    glClearColor(0.0, 0.0, 0.0, 1.0) # Change background color to grey
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glLight(GL_LIGHT0, GL_POSITION, [.0,.2,0.5,0])
    glMaterial(GL_FRONT_AND_BACK, GL_EMISSION, [0.2,0.2,0.2,1])
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    # Helps with antialiasing
    glEnable(GL_MULTISAMPLE)

    # Transformation matrix for arcball
    global matrix 
    matrix = glGetDoublev(GL_MODELVIEW_MATRIX)

    # Texture initialization
    textureId_arrow = loadTexture("arrow2.jpg")
    textureId_win = loadTexture("youwin.png")


def reshape(w, h):
    global width, height
    width, height = w, h 
    glMatrixMode (GL_PROJECTION)
    glLoadIdentity()
    global projectionArgs, windowSize
    windowSize = width,height
    projectionArgs = 50, width/height, 0.1,20
    gluPerspective (*projectionArgs)
    glViewport (0,0,width,height)


def pick(x,y):
    glDisable(GL_LIGHTING)
    draw_scene(True)
    glFlush()
    glEnable (GL_LIGHTING)
    buf = glReadPixels (x,windowSize[1]-y,1,1,GL_RGB,GL_FLOAT)
    pixel = buf[0][0]
    r,g,b = pixel
    i,j,k = int(r*n-1),int(g*n-1),int(b*n-1)
    if i >= 0: return (i*n + j) * n + k
    return -1 

def mousePressed(button, state, x, y):
    global selected,startx,starty
    if state == GLUT_DOWN:
        startx, starty = x, y
        selected = pick(x,y)
        if selected >= 0:
            click_animation[selected] = [directions[selected], 0.0, True]

        global arcball
        arcball = ArcBall ((width/2,height/2,0), width/2)
        global prevx, prevy
        prevx, prevy = startx, starty
        glutMotionFunc (rotatecallback)

    elif state == GLUT_UP:
        glutMotionFunc (None) 
        if (x,y) == (startx,starty): # Click
            if selected >= 0:
                cube_free = verify_removal_possibility(selected)
                if cube_free:
                    # Start cube removal animation
                    removal_animation[selected] = [directions[selected], 0.0]
                selected = None
    glutPostRedisplay()


def rotatecallback (x, y):
    global prevx,prevy,matrix,arcball
    angle, axis = arcball.rot (prevx, height - prevy, x, height - y)
    glLoadIdentity ()
    glRotatef (degrees(angle),*axis)
    glMultMatrixd (matrix)
    matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    prevx, prevy = x, y
    glutPostRedisplay()


def verify_removal_possibility(cube):
    ''' Verifies if it is possible to remove selected cube, that is, if it is not blocked '''
    global n, directions, removed, removal_animation

    cube_coord = find_cube_coord(cube) # cube coordinates

    # Jump to next non eliminated cube in the same direction. If there isn't one, next will be 'None', meaning cube is free
    next_cube_coord = get_next_cube(cube_coord, directions[cube])
    while True:
        if next_cube_coord == None: # on border
            return True
        else:
            if find_cube_name(*next_cube_coord) in removed or find_cube_name(*next_cube_coord) in removal_animation:
                # adjacent cube was removed previously, jump to next one
                next_cube_coord = get_next_cube(next_cube_coord,directions[cube])
            else: # cube in the way
                return False


def idle():
    update_removal_animation()
    update_click_animation()
    glutPostRedisplay()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize (width, height); 
    glutInitWindowPosition (100, 100)
    glutCreateWindow ("Tap Away 3D")
    init ()
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mousePressed)
    glutIdleFunc(idle)
    glutMainLoop()


main()
