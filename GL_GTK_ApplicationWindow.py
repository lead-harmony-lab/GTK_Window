import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys
import numpy as np
from pyassimp import *

# a Gtk ApplicationWindow

def recur_node(node, level=0):
    print("  " + "\t" * level + "- " + str(node))
    for child in node.children:
        recur_node(child, level + 1)


class MyWindow(Gtk.ApplicationWindow):
    # constructor: the title is "Welcome to GNOME" and the window belongs
    # to the application app

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Welcome to GNOME", application=app)


class MyApplication(Gtk.Application):
    # constructor of the Gtk Application

    def __init__(self):
        Gtk.Application.__init__(self)
        self.scene = load('models/char_01_triangulated.obj')
        #self.scene = load('models/snake.blend')    #Pyassimp function
        self.obj = self.scene.meshes[0]
        self.model = np.concatenate((self.obj.vertices, self.obj.texturecoords[0]), axis=0)
        #print(self.obj.texturecoords[0])  #  The obj file only uses two values for the texture coordinate but pyassimp adds a third value. This is wy we use a vec3 in the shader for texCoords
        self.texture_offset = self.model.itemsize * (len(self.model) // 2) * 3
        self.shader_prog = 0
        self.initialize = False
        self.VAO = 0
        # Begin Pyassimp functions
        print("SCENE:")
        print("   meshes: " + str(len(self.scene.meshes)))
        print("   materials: " + str(len(self.scene.materials)))
        print("   textures: " + str(len(self.scene.textures)))
        print("NODES:")
        recur_node(self.scene.rootnode)
        print("MESHES")
        for index, mesh in enumerate(self.scene.meshes):
            print("   MESH " + str(index + 1))
            print("      material id: " + str(mesh.materialindex + 1))
            print("      vertices: " + str(len(mesh.vertices)))
            print("      first 3 verts:\n" + str(mesh.normals[:3]))
            if mesh.normals.any():
                print("      first 3 normals:\n" + str(mesh.normals[:3]))
            else:
                print("      no normals")
            print("      colors: " + str(len(mesh.colors)))
            self.tcs = mesh.texturecoords
            if self.tcs.any():
                for tc_index, tc in enumerate(self.tcs):
                    print("      texture-coords " + str(tc_index) + ": " + str(
                        len(self.tcs[tc_index])) + "      first 3: " + str(self.tcs[tc_index][:3]))
            else:
                print("      no texture coordinates")
            print("      uv-component-count: " + str(len(mesh.numuvcomponents)))
            print("      faces: " + str(len(mesh.faces)) + " -> first 3:\n" + str(mesh.faces[:3]))
            print("      bones: " + str(len(mesh.bones)) + " -> first: " + str([str(b) for b in mesh.bones[:3]]))
        print("MATERIALS:")
        for index, material in enumerate(self.scene.materials):
            print("   MATERIAL (id: " + str(index + 1) + ")")
            for key, value in material.properties.items():
                print("      %s: %s" % (key, value))
        print("TEXTURES:")
        for index, texture in enumerate(self.scene.textures):
            print("   TEXTURE " + str(index + 1))
            print("      width: " + str(texture.width))
            print("      height: " + str(texture.height))
            print("      hint: " + str(texture.achformathint))
            print("      data (size): " + str(len(texture.data)))
        # End Pyassimp functions

    # create and activate a MyWindow, with self (the MyApplication) as
    # application the window belongs to.
    # Note that the function in C activate() becomes do_activate() in Python
    def do_activate(self):
        win = MyWindow(self)
        # show the window and all its content
        # this line could go in the constructor of MyWindow as well
        win.show_all()

    # start up the application
    # Note that the function in C startup() becomes do_startup() in Python
    def do_startup(self):
        Gtk.Application.do_startup(self)

# create and run the application, exit with the value returned by
# running the program
app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)