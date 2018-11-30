import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

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
void main(){
gl_Position =  position;
}'''

class MyGLArea(Gtk.GLArea):
    def __init__(self):
        Gtk.GLArea.__init__(self)
        self.set_required_version(3, 3)
        self.connect("realize", self.on_realize)
        #self.connect("unrealize" self.on_unrealize)  # Catch this signal to clean up buffer objects and shaders
        self.connect("render", self.on_render)
        #self.connect("resize", self.on_resize)

    def on_realize(self, area):
        ctx = self.get_context()
        print('is legacy context %s' % Gdk.GLContext.is_legacy(ctx))
        major, minor = ctx.get_required_version()
        print("Using OpenGL Version " + str(major) + "." + str(minor))
        print('glGenVertexArrays Available %s' % bool(glGenVertexArrays))
        print('Alpha Available %s' % bool(area.get_has_alpha()))
        print('Depth buffer Available %s' % bool(area.get_has_depth_buffer()))

    def on_render(self, area, ctx):
        ctx.make_current()
        glClearColor(0, 0, 0, 1)
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
        vertices = np.array([-1.0, -1.0, 0.0,
                             1.0, -1.0, 0.0,
                             0.0, 1.0, 0.0
                             ], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, 96, vertices, GL_STATIC_DRAW)
        # Unbind the VAO first (Important)
        glBindVertexArray(0)
        # Unbind other stuff
        glDisableVertexAttribArray(position)




        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.display(vertex_array_object)

    def display(self, vert):  # Main loop
        glClearColor(0.0, 1.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader_prog)
        glBindVertexArray(vert)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        #glDrawArrays(GL_TRIANGLES, 4, 3)
        glBindVertexArray(0)
        glUseProgram(0)
        print("loop")
        glFlush()


class RootWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='GL Example')
        self.set_default_size(800, 500)


        gl_area = MyGLArea()
        gl_area.set_has_depth_buffer(True)
        gl_area.set_has_stencil_buffer(False)

        self.add(gl_area)



win = RootWidget()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

