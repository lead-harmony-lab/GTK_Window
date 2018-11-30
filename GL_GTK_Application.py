#!/usr/bin/python3
# coding=utf8
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gio, Gdk, Gtk

GDK_Escape=0xff1b;

class MyApplication(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id, flags):
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)

    def new_window(self, *args):
        AppWindow(self)

    def key_pressed(self, widget, event, data=None):
        # ~ print "%4x" % (event.keyval)
        if (event.keyval == GDK_Escape):
            gtk.main_quit()

class AppWindow(object):
    def __init__(self, application):
        self.Application = application

        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            GtkBuilder = Gtk.Builder.new_from_file("gui.glade")
            GtkBuilder.connect_signals(self)
        except GObject.GError:
            print("Error reading GUI file")
            raise

        # Fire up the main window
        self.MainWindow = GtkBuilder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        self.MainWindow.show()

    def close(self, *args):
        self.MainWindow.destroy()


# Starter
def main():
    # Initialize GTK Application
    Application = MyApplication("com.bachsau.example", Gio.ApplicationFlags.FLAGS_NONE)

    # Start GUI
    Application.run()


if __name__ == "__main__": main()