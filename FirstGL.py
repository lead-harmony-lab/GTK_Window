import gi, pyrr
from pyrr import Matrix44, Vector4, Vector3, Quaternion
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from OpenGL.GL import *
from OpenGL.GL import shaders
import math
import numpy as np
import time

# Search through https://www.mail-archive.com/opensuse-commit@opensuse.org/msg103010.html

FRAGMENT_SOURCE ='''
#version 330
// Interpolated values from the vertex shaders
in vec3 fragmentColor;
// Ouput data
out vec3 color;
void main(){
	color = fragmentColor;
}'''

VERTEX_SOURCE = '''
#version 330
layout(location = 0) in vec4 position;
layout(location = 1) in vec3 vertexColor;

out vec3 fragmentColor;

uniform mat4 MVP;
void main(){
gl_Position =  MVP * position;
fragmentColor = vertexColor;
}'''

WINDOW_WIDTH=800
WINDOW_HEIGHT=500

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
        self.model_matrix = Matrix44.identity()
        self.view_matrix = Matrix44.identity()
        self.projection_matrix = Matrix44.identity()
        self.vertex_buffer = 0
        self.color_buffer = 0


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

        # Print information about our OpenGL Context
        ctx = self.get_context()
        print('is legacy context %s' % Gdk.GLContext.is_legacy(ctx))
        major, minor = ctx.get_required_version()
        print("Using OpenGL Version " + str(major) + "." + str(minor))
        print('glGenVertexArrays Available %s' % bool(glGenVertexArrays))
        print('Alpha Available %s' % bool(area.get_has_alpha()))
        print('Depth buffer Available %s' % bool(area.get_has_depth_buffer()))

        self.mvpMatrixLocationInShader = 0

        # Initialize GL Scene
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def on_render(self, area, ctx):
        # Main Render Loop
        self.frame_counter += 1
        ctx.make_current()


        VERTEX_SHADER_PROG = shaders.compileShader(VERTEX_SOURCE, GL_VERTEX_SHADER)
        FRAGMENT_SHADER_PROG = shaders.compileShader(FRAGMENT_SOURCE, GL_FRAGMENT_SHADER)
        self.shader_prog = shaders.compileProgram(VERTEX_SHADER_PROG, FRAGMENT_SHADER_PROG)

        self.create_object()


    def create_object(self):

        # Create a new VAO (Vertex Array Object) and bind it
        vertex_array_object = glGenVertexArrays(1)
        glBindVertexArray(vertex_array_object)

        vertices = np.array([-1.0, -1.0, -1.0,
                             -1.0, -1.0, 1.0,
                             -1.0, 1.0, 1.0,
                             1.0, 1.0, -1.0,
                             -1.0, -1.0, -1.0,
                             -1.0, 1.0, -1.0,
                             1.0, -1.0, 1.0,
                             -1.0, -1.0, -1.0,
                             1.0, -1.0, -1.0,
                             1.0, 1.0, -1.0,
                             1.0, -1.0, -1.0,
                             -1.0, -1.0, -1.0,
                             -1.0, -1.0, -1.0,
                             -1.0, 1.0, 1.0,
                             -1.0, 1.0, -1.0,
                             1.0, -1.0, 1.0,
                             -1.0, -1.0, 1.0,
                             -1.0, -1.0, -1.0,
                             -1.0, 1.0, 1.0,
                             -1.0, -1.0, 1.0,
                             1.0, -1.0, 1.0,
                             1.0, 1.0, 1.0,
                             1.0, -1.0, -1.0,
                             1.0, 1.0, -1.0,
                             1.0, -1.0, -1.0,
                             1.0, 1.0, 1.0,
                             1.0, -1.0, 1.0,
                             1.0, 1.0, 1.0,
                             1.0, 1.0, -1.0,
                             -1.0, 1.0, -1.0,
                             1.0, 1.0, 1.0,
                             -1.0, 1.0, -1.0,
                             -1.0, 1.0, 1.0,
                             1.0, 1.0, 1.0,
                             -1.0, 1.0, 1.0,
                             1.0, -1.0, 1.0
                             ], dtype=np.float32)

        colors = np.array([0.483, 0.596, 0.789,
                           0.483, 0.596, 0.789,
                           0.483, 0.596, 0.789,
                           1.0, 0.0, 0.0,
                           1.0, 0.0, 0.0,
                           1.0, 0.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.0, 1.0, 0.0,
                           1.0, 0.0, 0.0,
                           1.0, 0.0, 0.0,
                           1.0, 0.0, 0.0,
                           0.483, 0.596, 0.789,
                           0.483, 0.596, 0.789,
                           0.483, 0.596, 0.789,
                           0.0, 1.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.140, 0.616, 0.489,
                           0.140, 0.616, 0.489,
                           0.140, 0.616, 0.489,
                           0.055, 0.953, 0.042,
                           0.055, 0.953, 0.042,
                           0.055, 0.953, 0.042,
                           0.055, 0.953, 0.042,
                           0.055, 0.953, 0.042,
                           0.055, 0.953, 0.042,
                           0.0, 0.0, 1.0,
                           0.0, 0.0, 1.0,
                           0.0, 0.0, 1.0,
                           0.0, 0.0, 1.0,
                           0.0, 0.0, 1.0,
                           0.0, 0.0, 1.0,
                           0.140, 0.616, 0.489,
                           0.140, 0.616, 0.489,
                           0.140, 0.616, 0.489,
                           ], dtype=np.float32)

        # Generate buffer to hold our vertices
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Generate buffer to hold our colors
        self.color_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)

        self.display()

    def display(self):

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader_prog)

        eye = (4.0, 3.0, 3.0)
        target = (0.0, 0.0, 0.0)
        up = (0.0, 1.0, 0.0)

        ct = time.clock()
        perspective_matrix = Matrix44.perspective_projection(45.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200.0)
        view_matrix = Matrix44.look_at(eye, target, up)
        model_matrix = Matrix44.from_translation([0.0, 0.0, 0.0]) * pyrr.matrix44.create_from_axis_rotation((0.0, 1.0, 0.0), 4 * ct) * Matrix44.from_scale([1.0, 1.0, 1.0])

        MVP = perspective_matrix * view_matrix * model_matrix

        self.mvpMatrixLocationInShader = glGetUniformLocation(self.shader_prog, "MVP")
        glUniformMatrix4fv(self.mvpMatrixLocationInShader, 1, GL_FALSE, MVP)


        # Get the layout position of the 'position' parameter in the vertex shader and bind it.
        position = glGetAttribLocation(self.shader_prog, 'position')
        glEnableVertexAttribArray(position)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glVertexAttribPointer(position, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))  # Describe the position data layout in the buffer

        # Get the layout position of the 'vertexColor' parameter in the vertex shader and bind it.
        vertexColor = glGetAttribLocation(self.shader_prog, 'vertexColor')
        glEnableVertexAttribArray(vertexColor)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glVertexAttribPointer(vertexColor, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))


        glDrawArrays(GL_TRIANGLES, 0, 12*3)


        # Unbind the VAO first (Important)
        glBindVertexArray(0)
        # Unbind other stuff
        glDisableVertexAttribArray(position)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glUseProgram(0)

        # Schedule Redraw
        self.queue_draw()


class RootWidget(Gtk.Window):
    def __init__(self):
        win = Gtk.Window.__init__(self, title='GL Example')
        self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)

        gl_area = MyGLArea()
        gl_area.set_has_depth_buffer(True)
        gl_area.set_has_stencil_buffer(False)

        self.add(gl_area)

win = RootWidget()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()