# Make sure the right Gtk version is loaded
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from threading import Thread
from time import sleep


class Splash(Thread):
    def __init__(self):
        super(Splash, self).__init__()

        # Create a popup window
        self.window = Gtk.Window(Gtk.WindowType.POPUP)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect('destroy', Gtk.main_quit)
        self.window.set_default_size(400, 250)

        # Add box and label
        box = Gtk.Box()
        lbl = Gtk.Label()
        lbl.set_label("My app is loading...")
        box.pack_start(lbl, True, True, 0)
        self.window.add(box)

    def run(self):
        # Show the splash screen without causing startup notification
        # https://developer.gnome.org/gtk3/stable/GtkWindow.html#gtk-window-set-auto-startup-notification
        self.window.set_auto_startup_notification(False)
        self.window.show_all()
        self.window.set_auto_startup_notification(True)

        # Need to call Gtk.main to draw all widgets
        Gtk.main()

    def destroy(self):
        self.window.destroy()


class MainUI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        # Set position and decoration
        self.set_position(Gtk.WindowPosition.CENTER)
        self.lbl = Gtk.Label()
        self.lbl.set_label("Main window started")
        self.add(self.lbl)
        self.connect('destroy', Gtk.main_quit)

        # Initiate and show the splash screen
        print(("Starting splash"))
        splash = Splash()
        splash.start()

        print(("Simulate MainUI work"))
        sleep(5)

        # Destroy splash
        splash.destroy()
        print(("Splash destroyed"))

        print(("Starting MainUI"))
        self.show_all()


if __name__ == '__main__':
    # Now show the actual main window
    MainUI()
    Gtk.main()
    print(("MainUI ended"))