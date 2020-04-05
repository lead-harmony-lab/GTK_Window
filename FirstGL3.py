import gi
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

class RootWidget(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        window = Gtk.Window(application=self)
        window.set_title("GNOME")
        window.set_default_size(500, 500)
        window.show_all()

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
        Gtk.Dialog.__init__(self)
        self.add_buttons(
            "Quit", Gtk.ResponseType.CANCEL,
            "Run", Gtk.ResponseType.OK
        )
        self.set_default_size(651, 397)
        self.set_decorated(False)  # Creates a borderless window without a title bar
        self.set_app_paintable(True)
        self.connect('draw', self.draw)
        self.show_all()

    def draw(self, widget, context):
        self.image = cairo.ImageSurface.create_from_png("claver-splash.png")
        context.set_source_rgba(1, 1, 1, 0)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.set_source_surface(self.image, 0, 0)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)

win = RootWidget()
if win.popup_run_dialog():
    exit_status = win.run(sys.argv)
    sys.exit(exit_status)