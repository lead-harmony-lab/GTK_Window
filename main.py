import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="OpenGL Window Experiment")

        # How to use a grid layout
        grid = Gtk.Grid()
        self.add(grid)

        #Create a bunch of buttons
        button1 = Gtk.Button(label="Button 1")
        button2 = Gtk.Button(label="Button 2")
        button3 = Gtk.Button(label="Button 3")
        button4 = Gtk.Button(label="Button 4")
        button5 = Gtk.Button(label="Button 5")
        button6 = Gtk.Button(label="Button 6")

        grid.add(button1)
        grid.attach(button2, 1, 0, 2, 1)
        grid.attach_next_to(button3, button1, Gtk.PositionType.BOTTOM, 1, 2)
        grid.attach_next_to(button4, button3, Gtk.PositionType.RIGHT, 2, 1)
        grid.attach(button5, 1, 2, 1, 1)
        grid.attach_next_to(button6, button5, Gtk.PositionType.RIGHT, 1, 1)

        #So Cools
        #stuff

        # How to add a box
        self.box = Gtk.Box(spacing=10)
        #self.add(self.box)

        # How to pack buttons in a box
        self.bacon_button = Gtk.Button(label="Bacon")
        self.bacon_button.connect("clicked", self.bacon_clicked)
        #self.box.pack_start(self.bacon_button, True, True, 0)

        self.tuna_button = Gtk.Button(label="Tuna")
        self.tuna_button.connect("clicked", self.tuna_clicked)
        #self.box.pack_start(self.tuna_button, True, True, 0)

        # How to add a basic Button
        self.button = Gtk.Button(label="Click here!")
        self.button.connect("clicked", self.button_clicked)
        #self.add(self.button)

    # User clicks button
    def button_clicked(self, widget):
        print("Render Time")

    def bacon_clicked(self, widget):
        print("You clicked bacon")

    def tuna_clicked(self, widget):
        print("you have clicked", ''.join(widget.get_properties("label")))



window = MainWindow()





# How to add a label
label = Gtk.Label()
label.set_label("OMG. Label Text")
label.set_angle(30)
label.set_halign(Gtk.Align.END)
#window.add(label)

#print(label.get_properties("angle"))

window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()