import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import pyrr
from pyrr import Matrix44
from pyassimp import *
from pyassimp.helper import get_bounding_box
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import cairo
import math
import numpy as np
import time

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


def recur_node(node, level=0):
    print("  " + "\t" * level + "- " + str(node))
    for child in node.children:
        recur_node(child, level + 1)


class MyGLArea(Gtk.GLArea):
    def __init__(self):
        Gtk.GLArea.__init__(self)
        self.set_required_version(3, 3)
        self.connect("realize", self.on_realize)
        self.connect("unrealize", self.on_unrealize)  # Catch this signal to clean up buffer objects and shaders
        self.connect("render", self.on_render)
        self.connect("resize", self.on_resize)
        self.last_frame_time = 0
        self.add_tick_callback(self._tick)
        self.counter = 0
        self.frame_counter = 0

        """
        # Begin Pyassimp functions
        print("SCENE:")
        print("   meshes: " + str(len(self.scene.meshes)))
        print("   total faces: %d" % sum([len(mesh.faces) for mesh in self.scene.meshes]))
        print("   materials: " + str(len(self.scene.materials)))
        print("   textures: " + str(len(self.scene.textures)))
        print("NODES:")
        recur_node(self.scene.rootnode)
        print("MESHES")
        for index, mesh in enumerate(self.scene.meshes):
            print("   MESH " + str(index+1))
            print("      material id: " + str(mesh.materialindex+1))
            print("      vertices: " + str(len(mesh.vertices)))
            print("      faces: " + str(len(mesh.faces)))
            print("      normals: " + str(len(mesh.normals)))
            self.bb_min, self.bb_max = get_bounding_box(self.scene)
            print("      bounding box:" + str(self.bb_min) + " - " + str(self.bb_max))

            self.scene_center = [(a + b) / 2. for a, b in zip(self.bb_min, self.bb_max)]
            print("      scene center: ", self.scene_center)
            print("      first 3 verts:\n" + str(mesh.normals[:3]))
            if mesh.normals.any():
                print("      first 3 normals:\n" + str(mesh.normals[:3]))
            else:
                print("      no normals")
            print("      colors: " + str(len(mesh.colors)))
            self.tcs = mesh.texturecoords
            if self.tcs.any():
                for tc_index, tc in enumerate(self.tcs):
                    print("      texture-coords " + str(tc_index) + ": " + str(len(self.tcs[tc_index])) + "      first 3: " + str(self.tcs[tc_index][:3]))
            else:
                print("      no texture coordinates")
            print("      uv-component-count: " + str(len(mesh.numuvcomponents)))
            print("      faces: " + str(len(mesh.faces)) + " -> first 3:\n" + str(mesh.faces[:3]))
            print("      bones: " + str(len(mesh.bones)) + " -> first: " + str([str(b) for b in mesh.bones[:3]]))
        print("MATERIALS:")
        for index, material in enumerate (self.scene.materials):
            print("   MATERIAL (id: " + str(index+1) + ")")
            for key, value in material.properties.items():
                print("      %s: %s" % (key, value))
        print("TEXTURES:")
        for index, texture in enumerate(self.scene.textures):
            print("   TEXTURE " + str(index+1))
            print("      width: " + str(texture.width))
            print("      height: " + str(texture.height))
            print("      hint: " + str(texture.achformathint))
            print("      data (size): " + str(len(texture.data)))
        # End Pyassimp functions
        """

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
        ctx.make_current()
        print('Using legacy context: %s' % Gdk.GLContext.is_legacy(ctx))
        major, minor = ctx.get_required_version()
        print("Using OpenGL Version " + str(major) + "." + str(minor))
        print('glGenVertexArrays Available %s' % bool(glGenVertexArrays))
        print('Alpha Available %s' % bool(area.get_has_alpha()))
        print('Depth buffer Available %s' % bool(area.get_has_depth_buffer()))

        # Get information about current GTK GLArea canvas
        window = area.get_allocation()
        # Construct perspective matrix using width and height of window allocated by GTK
        self.perspective_matrix = Matrix44.perspective_projection(45.0, window.width / window.height, 0.1, 200.0)

        # Initialize GL Scene
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Pyassimp function
        self.scene = load('models/NewSnake1.fbx')
        self.blenderModel = self.scene.meshes[0]
        print("Name of model being loaded: ", self.blenderModel)
        self.model = np.concatenate((self.blenderModel.vertices, self.blenderModel.texturecoords[0]), axis=0)

        VERTEX_SHADER_PROG = compileShader(VERTEX_SOURCE, GL_VERTEX_SHADER)
        FRAGMENT_SHADER_PROG = compileShader(FRAGMENT_SOURCE, GL_FRAGMENT_SHADER)
        self.shader_prog = compileProgram(VERTEX_SHADER_PROG, FRAGMENT_SHADER_PROG)

        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # Generate buffer object names - paramater specifies number of names to generate
        self.VBO = glGenBuffers(1)
        # Bind a named buffer object to a target (this is a gl constant)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        # Creates a new data store for the buffer object currently bound to target. Static_Draw indicates teh store contents will be modified once and used many times.
        # Parameter #2 is equal to the number of vertices in model * 4 bytes
        glBufferData(GL_ARRAY_BUFFER, self.model.nbytes, self.model, GL_STATIC_DRAW)

        # Get the 'position layout' (index of the generic vertex attribute) of the 'in_positions' parameter from the vertex shader program and store it.
        self.position_in = glGetAttribLocation(self.shader_prog, 'in_positions')
        glEnableVertexAttribArray(self.position_in)
        # Describe the 'position layout' data in the buffer
        # ctypes.c_void_p(0) specifies the offset location in the buffer to begin reading data. Here it reads from the start of the buffer.
        # self.model.itemsize*3 specifies the stride (how to step through the data in the buffer). This is important for telling OpenGL how to step through a buffer having concatinated vertex and color data (see: https://youtu.be/bmCYgoCAyMQ).
        glVertexAttribPointer(self.position_in, 3, GL_FLOAT, GL_FALSE, self.model.itemsize * 3, ctypes.c_void_p(0))

        # Get the layout position of the 'in_positions' parameter in the vertex shader and bind it.
        self.texture_in = glGetAttribLocation(self.shader_prog, 'in_texCoords')
        self.texture_offset = self.model.itemsize * (len(self.model) // 2) * 3
        # Describe the position data layout in the buffer
        glVertexAttribPointer(self.texture_in, 3, GL_FLOAT, GL_FALSE, self.model.itemsize * 3, ctypes.c_void_p(self.texture_offset))
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
        image = Image.open("models/NewSnakeSkin.png")
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(list(flipped_image.getdata()), np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    def on_render(self, area, ctx):
        # Main Render Loop
        self.frame_counter += 1

        glUseProgram(self.shader_prog)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        eye = (0.0, 4.0, 20.0)
        target = (0.0, 7.0, 0.0)
        up = (0.0, 1.0, 0.0)

        ct = time.process_time()

        view_matrix = Matrix44.look_at(eye, target, up)
        model_matrix = Matrix44.from_translation([0.0, 0.0, 0.0]) * pyrr.matrix44.create_from_axis_rotation((0.0, 1.0, 0.0), 4 * ct) * Matrix44.from_scale([1.0, 1.0, 1.0])

        MVP = self.perspective_matrix * view_matrix * model_matrix

        self.mvpMatrixLocationInShader = glGetUniformLocation(self.shader_prog, "MVP")
        glUniformMatrix4fv(self.mvpMatrixLocationInShader, 1, GL_FALSE, MVP)

        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.blenderModel.vertices))

        # Unbind the VAO first (Important)
        glBindVertexArray(0)
        # Unbind other stuff
        glDisableVertexAttribArray(self.position_in)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glUseProgram(0)

        # Schedule Redraw
        self.queue_draw()

    def on_unrealize(self, area):
        release(self.scene)     #Pyassimp function
        print("closing time")

    def on_resize(self, area, width, height):
        self.perspective_matrix = Matrix44.perspective_projection(45.0, width / height, 0.1, 200.0)

class RootWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='GL Example')
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
        self.set_default_size(651, 397)
        self.set_border_width(20)
        self.set_decorated(False) # Creates a borderless window without a title bar
        self.set_app_paintable(True)
        self.connect('draw', self.draw)

        area = self.get_content_area()

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        area.add(grid)
        #grid.get_style_context().add_class('yellow-background')
        grid.set_margin_top(260)
        grid.set_margin_start(120)


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
                button.get_style_context().add_class('blue-text')
                button.connect("toggled", self.on_button_toggled, i, parent)
                button.set_active(True)

            else:
                label = "Monitor #" + repr(i) + " - " + repr(width) + " X " + repr(height)

                button = Gtk.RadioButton.new_with_label_from_widget(group, label)
                button.get_style_context().add_class('blue-text')
                button.connect("toggled", self.on_button_toggled, i, parent)

            grid.add(button)

        checkbutton = Gtk.CheckButton.new_with_label("Fullscreen Window")
        checkbutton.get_style_context().add_class('blue-text')
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
        self.image = cairo.ImageSurface.create_from_png("claver-splash.png")
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


        #context.set_source_surface(overlay, 0, 0)
        context.set_source_surface(self.image, 0, 0)



        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)

win = RootWidget()
win.connect("delete-event", Gtk.main_quit)
win.connect("key-release-event", win.on_key_release)

cssProvider = Gtk.CssProvider()
cssProvider.load_from_path('style.css')
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

if win.popup_run_dialog():
    if win.is_fullscreen:
        screen = Gdk.Screen.get_default()
        win.fullscreen_on_monitor(screen, win.monitor_num_for_display)
    win.show_all()
    Gtk.main()



