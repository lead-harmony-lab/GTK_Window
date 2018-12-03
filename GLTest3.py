import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from OpenGL.GL import *
from OpenGL.GL import shaders
import math
import numpy as np
from pyrr import Matrix44
import time

# Search through https://www.mail-archive.com/opensuse-commit@opensuse.org/msg103010.html

FRAGMENT_SOURCE ='''
#version 330
in vec4 inputColor;
out vec4 outputColor;
void main(){
outputColor = vec4(1.0,0.0,0.0,1.0); //constant red.
}'''

VERTEX_SOURCE = '''
#version 330
in vec4 position;
uniform mat4 MVP;
void main(){
gl_Position =  MVP * position;
}'''

class MyGLArea(Gtk.GLArea):
    def __init__(self):
        Gtk.GLArea.__init__(self)
        self.set_required_version(3, 3)
        self.connect("realize", self.on_realize)
        #self.connect("unrealize" self.on_unrealize)  # Catch this signal to clean up buffer objects and shaders
        self.connect("render", self.on_render)
        self.last_frame_time = 0
        self.add_tick_callback(self._tick)
        self.counter = 0
        self.frame_counter = 0
        self.rot_y = self.identity()


    def _tick(self, wi, clock):
        ti = clock.get_frame_time()
        if ti - self.last_frame_time > 1000000:
            self.counter += 1
            print(str(self.frame_counter) + "/s")
            self.frame_counter = 0
            self.last_frame_time = ti
            #self.queue_draw()
        return True

    def on_realize(self, area):
        # OpenGL Context Successfully Initalized
        ctx = self.get_context()
        print('is legacy context %s' % Gdk.GLContext.is_legacy(ctx))
        major, minor = ctx.get_required_version()
        print("Using OpenGL Version " + str(major) + "." + str(minor))
        print('glGenVertexArrays Available %s' % bool(glGenVertexArrays))
        print('Alpha Available %s' % bool(area.get_has_alpha()))
        print('Depth buffer Available %s' % bool(area.get_has_depth_buffer()))
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def on_render(self, area, ctx):
        # Main Render Loop
        self.frame_counter += 1
        ctx.make_current()
        glClearColor(0.0, 1.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        VERTEX_SHADER_PROG = shaders.compileShader(VERTEX_SOURCE, GL_VERTEX_SHADER)
        FRAGMENT_SHADER_PROG = shaders.compileShader(FRAGMENT_SOURCE, GL_FRAGMENT_SHADER)
        self.shader_prog = shaders.compileProgram(VERTEX_SHADER_PROG, FRAGMENT_SHADER_PROG)
        self.create_object()


    def create_object(self):



        # Create a new VAO (Vertex Array Object) and bind it
        vertex_array_object = glGenVertexArrays(1)
        glBindVertexArray(vertex_array_object)
        # Generate buffers to hold our vertices
        vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
        # Get the position of the 'position' in parameter of our shader and bind it.
        position = glGetAttribLocation(self.shader_prog, 'position')
        glEnableVertexAttribArray(position)
        # Describe the position data layout in the buffer
        glVertexAttribPointer(position, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        # Send the data over to the buffer
        vertices = np.array([-0.5, -0.5, 0.0,
                             0.5, -0.5, 0.0,
                             0.0, 0.5, 0.0
                             ], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, 96, vertices, GL_STATIC_DRAW)
        # Unbind the VAO first (Important)
        glBindVertexArray(0)
        # Unbind other stuff
        glDisableVertexAttribArray(position)




        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.display(vertex_array_object)

    def display(self, vert):

        #matModel = self.rotate(np.pi, np.array([1, 1, 1]))

        eye = np.array([0, 0, 0.5])
        target = np.array([0, 0, 0])
        up = np.array([0, 1, 0])

        #matView = self.lookat(eye, target, up)
        # matView = np.eye(4)

        #matProjection = self.perspective(fovy=45.0, aspect=4.0 / 3.0, n=0.1, f=100.0)
        # matProjection = np.eye(4)


        glUseProgram(self.shader_prog)


        ct = time.clock()
        self.rot_y = Matrix44.from_y_rotation(4*ct)
        self.model_loc = glGetUniformLocation(self.shader_prog, "MVP")
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, self.rot_y)




        # Begin 'draw_axis()'
        glBindVertexArray(vert)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)
        # End 'draw_axis()'

        glUseProgram(0)

        # Schedule Redraw
        self.queue_draw()

    def identity(self):
        return np.matrix([1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0,
                          0, 0, 0, 1], dtype=np.float32)

    def transform(self, m, v):
        return np.asarray(m * np.asmatrix(v).T)[:, 0]

    def magnitude(self, v):
        return math.sqrt(np.sum(v ** 2))

    def normalize(self, v):
        m = self.magnitude(v)
        if m == 0:
            return v
        return v / m

    def ortho(self, l, r, b, t, n, f):
        dx = r - l
        dy = t - b
        dz = f - n
        rx = -(r + l) / (r - l)
        ry = -(t + b) / (t - b)
        rz = -(f + n) / (f - n)
        return np.matrix([[2.0 / dx, 0, 0, rx],
                          [0, 2.0 / dy, 0, ry],
                          [0, 0, -2.0 / dz, rz],
                          [0, 0, 0, 1]])

    def perspective(self, fovy, aspect, n, f):
        s = 1.0 / math.tan(math.radians(fovy) / 2.0)
        sx, sy = s / aspect, s
        zz = (f + n) / (n - f)
        zw = 2 * f * n / (n - f)
        return np.matrix([[sx, 0, 0, 0],
                          [0, sy, 0, 0],
                          [0, 0, zz, zw],
                          [0, 0, -1, 0]])

    def frustum(self, x0, x1, y0, y1, z0, z1):
        a = (x1 + x0) / (x1 - x0)
        b = (y1 + y0) / (y1 - y0)
        c = -(z1 + z0) / (z1 - z0)
        d = -2 * z1 * z0 / (z1 - z0)
        sx = 2 * z0 / (x1 - x0)
        sy = 2 * z0 / (y1 - y0)
        return np.matrix([[sx, 0, a, 0],
                          [0, sy, b, 0],
                          [0, 0, c, d],
                          [0, 0, -1, 0]])

    def translate(self, xyz):
        x, y, z = xyz
        return np.matrix([[1, 0, 0, x],
                          [0, 1, 0, y],
                          [0, 0, 1, z],
                          [0, 0, 0, 1]])

    def scale(self, xyz):
        x, y, z = xyz
        return np.matrix([[x, 0, 0, 0],
                          [0, y, 0, 0],
                          [0, 0, z, 0],
                          [0, 0, 0, 1]])

    def sincos(self, a):
        a = math.radians(a)
        return math.sin(a), math.cos(a)

    def rotate(self, a, xyz):
        x, y, z = self.normalize(xyz)
        s, c = self.sincos(a)
        nc = 1 - c
        return np.matrix([[x * x * nc + c, x * y * nc - z * s, x * z * nc + y * s, 0],
                          [y * x * nc + z * s, y * y * nc + c, y * z * nc - x * s, 0],
                          [x * z * nc - y * s, y * z * nc + x * s, z * z * nc + c, 0],
                          [0, 0, 0, 1]])

    def rotx(self, a):
        s, c = self.sincos(a)
        return np.matrix([[1, 0, 0, 0],
                          [0, c, -s, 0],
                          [0, s, c, 0],
                          [0, 0, 0, 1]])

    def roty(self, a):
        s, c = self.sincos(a)
        return np.matrix([[c, 0, s, 0],
                          [0, 1, 0, 0],
                          [-s, 0, c, 0],
                          [0, 0, 0, 1]])

    def rotz(self, a):
        s, c = self.sincos(a)
        return np.matrix([[c, -s, 0, 0],
                          [s, c, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])

    def lookat(self, eye, target, up):
        F = target[:3] - eye[:3]
        f = self.normalize(F)
        U = self.normalize(up[:3])
        s = np.cross(f, U)
        u = np.cross(s, f)
        M = np.matrix(np.identity(4))
        M[:3, :3] = np.vstack([s, u, -f])
        T = self.translate(-eye)
        return M * T

    # Similar function to glViewPort()
    def viewport(self, x, y, width, height):
        x, y, width, height = map(float, (x, y, width, height))
        return np.matrix([[width / 2, 0, 0, x + width / 2],
                          [0, height / 2, 0, y + height / 2],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])

    def timer(self):
        #global clock
        #clock += 0.0005 * 1000.0 / fps

        #theta = 1.0/60.0;
        #matModel = self.rotate(theta * 180 / np.pi, np.array([1, 1, 1]))
        matModel = self.rotate(180 / np.pi, np.array([1, 1, 1]))

        eye = np.array([0, 0, 2])
        target = np.array([0, 0, 0])
        up = np.array([0, 1, 0])

        matView = self.lookat(eye, target, up)
        # matView = np.eye(4)

        matProjection = self.perspective(fovy=45.0, aspect=4.0 / 3.0, n=0.1, f=10.0)
        # matProjection = np.eye(4)

        loc = glGetUniformLocation(self.program, "Model")
        glUniformMatrix4fv(loc, 1, False, np.asfortranarray(matModel))

        loc = glGetUniformLocation(self.program, "View")
        glUniformMatrix4fv(loc, 1, False, np.asfortranarray(matView))

        loc = glGetUniformLocation(self.program, "Projection")
        glUniformMatrix4fv(loc, 1, False, np.asfortranarray(matProjection))



class RootWidget(Gtk.Window):
    def __init__(self):
        win = Gtk.Window.__init__(self, title='GL Example')
        self.set_default_size(800, 500)

        gl_area = MyGLArea()
        gl_area.set_has_depth_buffer(True)
        gl_area.set_has_stencil_buffer(False)

        self.add(gl_area)



win = RootWidget()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()