from gi.repository import Gtk
from gi.repository import cairo
import sys
import math


def hexagon(coord_x, coord_y):

    # because of the symetry I take only the absolute value
    coord_x, coord_y= abs(coord_x), abs(coord_y)


    # I got the constants by clicling in the image and printing the coord_x and coord_y values

    if coord_x <= 13 and coord_y <= 25:   # define a rectangle
        return True
    else:
        # I cut the coord x to define a triangle
        coord_x=coord_x-13/2

        # line equation
        ymax=(-25/31)*coord_x+25

        if coord_y < ymax:
            return True
        else:
            return False


class GUI(Gtk.Window):

    def __init__(self):

        self.window_root=Gtk.Window()


        # Create an event box to handle the click's
        self.eventbox=Gtk.EventBox()
        self.eventbox.connect('button-press-event' , self.on_eventbox_pressed)
        self.eventbox.connect('button-release-event' , self.on_eventbox_released)

        # Load the images
        self.hexagon1=Gtk.Image.new_from_file('./3uSFN.png')
        self.hexagon2=Gtk.Image.new_from_file('./cWmUA.png')

        # init the event box
        self.eventbox.add(self.hexagon1)
        self.window_root.add(self.eventbox)
        self.window_root.show_all()

        # a variable to store the state of the button
        self.state=False



    def on_eventbox_pressed(self, widget , event):

        if 'GDK_BUTTON_PRESS' in str(event.type): # If the user made a "single click"
            if event.button == 1: # if it is a left click

                # get the x,y of the mouse from the center of the image
                pos_x, pos_y=self.window_root.get_position()
                siz_x, siz_y=self.window_root.get_size()
                mouse_x,mouse_y=event.x-siz_x/2, siz_y/2-event.y

                if hexagon(mouse_x, mouse_y):
                    self.eventbox.remove(self.hexagon1)
                    self.eventbox.add(self.hexagon2)
                    self.eventbox.show_all()

                    self.state=True


    def on_eventbox_released(self, widget , event):
        if self.state:
            self.eventbox.remove(self.hexagon2)
            self.eventbox.add(self.hexagon1)
            self.state=False


main=GUI()
Gtk.main()