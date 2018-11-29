import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from OpenGL.GL import *
from OpenGL.GLU import *


class MyGLArea(Gtk.GLArea):
    def __init__(self):
        Gtk.GLArea.__init__(self)
        self.connect("realize", self.on_realize)


    def on_realize(self, area):
        ctx = self.get_context()
        ctx.make_current()
        print("The context is {}".format(self.get_property("context")))
        err = self.get_error()
        if err:
            print(err)
        return




class RootWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='GL Example')
        self.set_default_size(800,500)
        gl_area = MyGLArea()
        self.add(gl_area)


win = RootWidget()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()