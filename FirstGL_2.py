import gi, pyrr
from pyrr import Matrix44, Vector4, Vector3, Quaternion
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from OpenGL.GL import *
from OpenGL.GL import shaders
import cairo
import math
import numpy as np
import time
# Run with version of pyassimp 3.3
from pyassimp import *
from PIL import Image

# Search through https://www.mail-archive.com/opensuse-commit@opensuse.org/msg103010.html

FRAGMENT_SOURCE ='''
#version 330
in vec2 v_texCoords;
out vec4 outColor;
uniform sampler2D samplerTexture;
void main(){
	outColor = texture(samplerTexture, v_texCoords);
}'''

VERTEX_SOURCE = '''
#version 330
layout(location = 0) in vec3 in_positions;
layout(location = 1) in vec3 in_texCoords;

out vec2 v_texCoords;

uniform mat4 MVP;
void main(){
gl_Position =  MVP * vec4(in_positions, 1.0f);
v_texCoords = in_texCoords.xy;
}'''

WINDOW_WIDTH=800
WINDOW_HEIGHT=500

class MyGLArea(Gtk.GLArea):
    def __init__(self):
        Gtk.GLArea.__init__(self)
        self.set_required_version(3, 3)
        self.connect("realize", self.on_realize)
        self.connect("unrealize", self.on_unrealize)  # Catch this signal to clean up buffer objects and shaders
        self.connect("render", self.on_render)
        self.last_frame_time = 0
        self.add_tick_callback(self._tick)
        self.counter = 0
        self.frame_counter = 0
        self.model_matrix = Matrix44.identity()
        self.view_matrix = Matrix44.identity()
        self.projection_matrix = Matrix44.identity()
        self.scene = load('models/char_01_triangulated.obj')
        self.obj = self.scene.meshes[0]
        self.model = np.concatenate((self.obj.vertices, self.obj.texturecoords[0]), axis=0)
        #print(self.obj.texturecoords[0])  #  The obj file only uses two values for the texture coordinate but pyassimp adds a third value. This is wy we use a vec3 in the shader for texCoords
        self.texture_offset = self.model.itemsize * (len(self.model) // 2) * 3
        self.shader_prog = 0
        self.initialize = False
        self.VAO = 0
        self.window_width = 0
        self.window_height = 0

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

        window = area.get_allocation()

        self.window_width = window.width
        self.window_height = window.height

        # Initialize GL Scene
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def on_render(self, area, ctx):
        # Main Render Loop
        self.frame_counter += 1
        ctx.make_current()

        if self.initialize == False:
            VERTEX_SHADER_PROG = shaders.compileShader(VERTEX_SOURCE, GL_VERTEX_SHADER)
            FRAGMENT_SHADER_PROG = shaders.compileShader(FRAGMENT_SOURCE, GL_FRAGMENT_SHADER)
            self.shader_prog = shaders.compileProgram(VERTEX_SHADER_PROG, FRAGMENT_SHADER_PROG)

            self.VAO = glGenVertexArrays(1)
            glBindVertexArray(self.VAO)

            VBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, VBO)
            glBufferData(GL_ARRAY_BUFFER, self.model.nbytes, self.model, GL_STATIC_DRAW)

            # Get the layout position of the 'in_positions' parameter in the vertex shader and bind it.
            self.position_in = glGetAttribLocation(self.shader_prog, 'in_positions')
            glVertexAttribPointer(self.position_in, 3, GL_FLOAT, GL_FALSE, self.model.itemsize * 3, ctypes.c_void_p(0))  # Describe the position data layout in the buffer
            glEnableVertexAttribArray(self.position_in)

            # Get the layout position of the 'in_positions' parameter in the vertex shader and bind it.
            self.texture_in = glGetAttribLocation(self.shader_prog, 'in_texCoords')
            glVertexAttribPointer(self.texture_in, 3, GL_FLOAT, GL_FALSE, self.model.itemsize * 3, ctypes.c_void_p(self.texture_offset))  # Describe the position data layout in the buffer
            glEnableVertexAttribArray(self.texture_in)

            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            # Set the texture wrapping parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            # Set texture filtering parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            # Load Image
            image = Image.open("models/Chibi_Texture_D.png")
            flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = np.array(list(flipped_image.getdata()), np.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            self.initialize = True

        glUseProgram(self.shader_prog)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        eye = (0.0, 4.0, 20.0)
        target = (0.0, 7.0, 0.0)
        up = (0.0, 1.0, 0.0)

        ct = time.process_time()
        perspective_matrix = Matrix44.perspective_projection(45.0, self.window_width/self.window_height, 0.1, 200.0)
        view_matrix = Matrix44.look_at(eye, target, up)
        model_matrix = Matrix44.from_translation([0.0, 0.0, 0.0]) * pyrr.matrix44.create_from_axis_rotation((0.0, 1.0, 0.0), 4 * ct) * Matrix44.from_scale([1.0, 1.0, 1.0])

        MVP = perspective_matrix * view_matrix * model_matrix

        self.mvpMatrixLocationInShader = glGetUniformLocation(self.shader_prog, "MVP")
        glUniformMatrix4fv(self.mvpMatrixLocationInShader, 1, GL_FALSE, MVP)

        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, len(self.obj.vertices))

        # Unbind the VAO first (Important)
        glBindVertexArray(0)
        # Unbind other stuff
        glDisableVertexAttribArray(self.position_in)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glUseProgram(0)

        # Schedule Redraw
        self.queue_draw()

    def on_unrealize(self, area):
        print("closing time")

class RootWidget(Gtk.Window):
    def __init__(self):
        win = Gtk.Window.__init__(self, title='GL Example')
        self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.is_fullscreen = True
        self.monitor_num_for_display = 0

        gl_area = MyGLArea()
        gl_area.set_has_depth_buffer(True)
        self.add(gl_area)

    def on_key_release(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        elif event.keyval == Gdk.KEY_f:
            self.fullscreen_mode()

    def fullscreen_mode(self):
        if self._is_fullscreen == True:
            self.unfullscreen()
            self._is_fullscreen = False
        else:
            self.fullscreen()
            self._is_fullscreen = True

    def popup_run_dialog(self):
        dialog = PopUp(self)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            return True
        elif response == Gtk.ResponseType.CANCEL:
            return False

class PopUp(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Demo Launcher", parent, modal=True)
        self.add_buttons(
            "Quit", Gtk.ResponseType.CANCEL,
            "Run", Gtk.ResponseType.OK
        )
        self.set_default_size(200, 300)
        self.set_border_width(20)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.connect('draw', self.draw)

        area = self.get_content_area()
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        area.add(box_outer)


        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        box_outer.add(grid)

        group = Gtk.RadioButton.new(None)

        display = Gdk.Display.get_default()
        num_of_monitors = display.get_n_monitors()

        for i in range(num_of_monitors):

            monitor = display.get_monitor(i)
            geometry = monitor.get_geometry()
            scale_factor = monitor.get_scale_factor()
            width = scale_factor * geometry.width
            height = scale_factor * geometry.height

            if monitor.is_primary():
                label = "Monitor #" + repr(i) + " - " + repr(width) + " X " + repr(height) + " (PRIMARY)"

                button = Gtk.RadioButton.new_with_label_from_widget(group, label)
                button.connect("toggled", self.on_button_toggled, i, parent)
                button.set_active(True)

            else:
                label = "Monitor #" + repr(i) + " - " + repr(width) + " X " + repr(height)

                button = Gtk.RadioButton.new_with_label_from_widget(group, label)
                button.connect("toggled", self.on_button_toggled, i, parent)

            grid.add(button)

        checkbutton = Gtk.CheckButton.new_with_label("Fullscreen Window")
        checkbutton.connect("toggled", self.on_fullscreen_toggled, "fullscreen", parent)
        checkbutton.set_active(True)
        grid.add(checkbutton)

        self.show_all()

    def on_button_toggled(self, button, name, parent):
        if button.get_active():
            parent.monitor_num_for_display = name

    def on_fullscreen_toggled(self, button, name, parent):
        if button.get_active():
            parent.is_fullscreen = True
        else:
            parent.is_fullscreen = False

    def draw(self, widget, context):
        context.set_source_rgba(1, 1, 1, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)

        # Draw some shapes into the context here
        alloc = widget.get_allocation()

        width = alloc.width
        height = alloc.height

        radius = 0.5 * min(width, height) - 10
        xc = width / 2.
        yc = height / 2.

        target = context.get_target()
        overlay = target.create_similar(cairo.CONTENT_COLOR_ALPHA, width, height)

        # Draw a black circle on the overlay
        overlay_cr = cairo.Context(overlay)
        overlay_cr.set_source_rgb(0, 0, 0)

        overlay_cr.save()

        overlay_cr.translate(xc, yc)
        overlay_cr.scale(1.0, radius / radius)
        overlay_cr.move_to(radius, 0.0)
        overlay_cr.arc(0, 0, radius, 0, 2 * math.pi)
        overlay_cr.close_path()

        overlay_cr.restore()

        overlay_cr.fill()


        context.set_source_surface(overlay, 0, 0)



        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)

win = RootWidget()
win.connect("delete-event", Gtk.main_quit)
win.connect("key-release-event", win.on_key_release)

if win.popup_run_dialog():
    if win.is_fullscreen:
        screen = Gdk.Screen.get_default()
        win.fullscreen_on_monitor(screen, win.monitor_num_for_display)
    win.show_all()
    Gtk.main()



