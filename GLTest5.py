import textwrap
import math
import numpy as np

from ctypes import *
from OpenGL.GL import *
from OpenGL.GL.ARB.multitexture import *
from OpenGL.GL.ARB.debug_output import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def make_program(vs, fs):
    id_program = glCreateProgram()
    glAttachShader(id_program, vs)
    glAttachShader(id_program, fs)
    glLinkProgram(id_program)

    result = glGetProgramiv(id_program, GL_LINK_STATUS)
    if not(result):
        raise RuntimeError(glGetProgramInfoLog(id_program))

    return id_program


def make_fs(source):
    id_fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(id_fs, source)
    glCompileShader(id_fs)

    result = glGetShaderiv(id_fs, GL_COMPILE_STATUS)
    if not(result):
        raise Exception("Error: {0}".format(
            glGetShaderInfoLog(id_fs)
        ))

    return id_fs


def make_vs(source):
    id_vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(id_vs, source)
    glCompileShader(id_vs)

    result = glGetShaderiv(id_vs, GL_COMPILE_STATUS)
    if not(result):
        raise Exception("Error: {0}".format(
            glGetShaderInfoLog(id_vs)
        ))

    return id_vs


def v_length(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def v_normalize(a):
    v = v_length(a)
    inv_length = 1.0 / v_length(a)
    return [a[0] * inv_length, a[1] * inv_length, a[2] * inv_length]


def v_cross(a, b):
    return [
        a[1] * b[2] - b[1] * a[2],
        a[2] * b[0] - b[2] * a[0],
        a[0] * b[1] - b[0] * a[1]
    ]


def identity():
    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def transpose(a):
    return [
        a[0], a[4], a[8], a[12],
        a[1], a[5], a[9], a[13],
        a[2], a[6], a[10], a[14],
        a[3], a[7], a[11], a[15]
    ]


def perspective(fovy, aspect, znear, zfar):
    tan_half_fovy = math.tan(fovy / 2.0)

    m00 = 1.0 / (aspect * tan_half_fovy)
    m11 = 1.0 / (tan_half_fovy)
    m22 = - (zfar + znear) / (zfar - znear)
    m23 = -1.0
    m32 = -(2.0 * zfar * znear) / (zfar - znear)

    return transpose([
        m00, 0.0, 0.0, 0.0,
        0.0, m11, 0.0, 0.0,
        0.0, 0.0, m22, m32,
        0.0, 0.0, m23, 0.0
    ])


def lookat(eye, target, up):
    zaxis = v_normalize(
        [target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]]
    )
    xaxis = v_normalize(v_cross(zaxis, up))
    yaxis = v_cross(xaxis, zaxis)

    return transpose([
        xaxis[0], xaxis[1], xaxis[2], -v_dot(xaxis, eye),
        yaxis[0], yaxis[1], yaxis[2], -v_dot(yaxis, eye),
        -zaxis[0], -zaxis[1], -zaxis[2], v_dot(zaxis, eye),
        0,   0,   0,   1
    ])

def sincos(a):
    a = math.radians(a)
    return math.sin(a), math.cos(a)

def rotate(a, xyz):
    x, y, z = v_normalize(xyz)
    s, c = sincos(a)
    nc = 1 - c
    return [x * x * nc + c, x * y * nc - z * s, x * z * nc + y * s, 0,
            y * x * nc + z * s, y * y * nc + c, y * z * nc - x * s, 0,
            x * z * nc - y * s, y * z * nc + x * s, z * z * nc + c, 0,
            0, 0, 0, 1]


def add_line(data, p0, p1, color):
    data += [p0[0], p0[1], p0[2], color[0], color[1], color[2]]
    data += [p1[0], p1[1], p1[2], color[0], color[1], color[2]]


def make_axis(k=25.0):
    data = []
    add_line(data, [k, 0.0, 0.0], [0, 0, 0], [1.0, 0.0, 0.0])
    add_line(data, [0.0, k, 0.0], [0, 0, 0], [0.0, 1.0, 0.0])
    add_line(data, [-k, 0.0, 0.0], [0, 0, 0], [0.0, 0.0, 1.0])
    data = np.array(data, dtype=np.float32)

    print("len(data)={} bytes(data)={}".format(
        len(data), ArrayDatatype.arrayByteCount(data)))

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(
        GL_ARRAY_BUFFER,
        ArrayDatatype.arrayByteCount(data),
        data, GL_STATIC_DRAW
    )
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, c_void_p(3 * 4))
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return vao


def draw_axis(id_vao):
    glBindVertexArray(id_vao)
    glDrawArrays(GL_LINES, 0, 6)
    glBindVertexArray(0)


class Mcve():

    def __init__(self, window_name, width, height):
        self.window_width = width
        self.window_height = height
        self.window_name = window_name

    def init(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.0, 0.0, 0.0, 0.0)

        self.prog_axis = make_program(
            make_vs(textwrap.dedent("""
                #version 410

                layout (location = 0) in vec2 a_position;
                layout (location = 1) in vec3 a_color;

                out vec3 color;

                uniform mat4 projection;
                uniform mat4 view;
                uniform mat4 model;

                void main () {
                    color=a_color;
                    gl_Position = projection*view*model*vec4(a_position, 0.0, 1.0);
                }
            """)),
            make_fs(textwrap.dedent("""
                #version 410
                in vec3 color;
                out vec4 frag_colour;

                void main () {
                  frag_colour = vec4(color,1.0);
                }
            """))
        )

        self.axis = make_axis()

    def display(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #matModel = rotate(180 / math.pi, [1, 1, 1])
        a = identity()
        matModel = glGetFloatv(GL_MODELVIEW_MATRIX)

        eye = [50.0, 50.0, 50.0]
        target = [0, 0, 0]
        up = [0, 1, 0]
        view = lookat(eye, target, up)
        projection = perspective(45.0, 1.0, 0.1, 1000.0)

        prog = self.prog_axis
        glUseProgram(prog)

        glUniformMatrix4fv(glGetUniformLocation(prog, "model"), 1, False,
                           np.array(identity(), dtype=np.float32)
                           )
        glUniformMatrix4fv(glGetUniformLocation(prog, "view"), 1, False,
                           np.array(view, dtype=np.float32)
                           )
        glUniformMatrix4fv(glGetUniformLocation(prog, "projection"), 1, False,
                           np.array(projection, dtype=np.float32)
                           )

        draw_axis(self.axis)

        glUseProgram(0)

        glutSwapBuffers()
        print("loop")

    def reshape(self, w, h):
        self.window_width = w
        self.window_height = h
        glViewport(0, 0, w, h)

    def animate(self):
        glutPostRedisplay()

    def visible(self, vis):
        if (vis == GLUT_VISIBLE):
            glutIdleFunc(self.animate)
        else:
            glutIdleFunc(0)

    def key_pressed(self, *args):
        key = args[0].decode("utf8")
        if key == "\x1b":
            sys.exit()

    def run(self):
        glutInit(sys.argv)
        glutInitDisplayMode(
            GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH | GLUT_MULTISAMPLE)
        glutInitWindowSize(self.window_width, self.window_height)
        glutInitWindowPosition(800, 100)
        glutCreateWindow(self.window_name)
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutIdleFunc(self.animate)
        glutVisibilityFunc(self.visible)
        glutKeyboardFunc(self.key_pressed)
        self.init()
        glutMainLoop()

if __name__ == "__main__":
    Mcve(b"MCVE", 800, 600).run()