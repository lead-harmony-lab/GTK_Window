import math

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import sys


class MyApplication(Gtk.Application):

    def do_activate(self):
        window = Gtk.Window(application=self)
        window.set_title("Welcome to GNOME")
        window.set_default_size(500, 400)
        window.set_position(Gtk.WindowPosition.CENTER)

        grid = Gtk.Grid()

        self.eventbox=Gtk.EventBox()
        self.eventbox.connect('button-press-event' , self.on_eventbox_pressed)
        self.eventbox.connect('button-release-event' , self.on_eventbox_released)
        self.eventbox.connect("draw", self.draw)
        self.eventbox.set_size_request(500, 300)

        grid.attach(self.eventbox, 0, 0, 1, 1)
        window.add(grid)
        window.show_all()

    def draw_rounded_rect(self, context, x, y, width, height, radius, lineWidth):
        """ draws rectangles with rounded (circular arc) corners """
        from math import pi
        degrees = pi / 180

        context.set_line_width(lineWidth)
        context.set_source_rgba(0.5, 0.0, 0.0, 1.0)     # Red

        # cr.new_sub_path()
        context.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
        context.arc(x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees)
        context.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
        context.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        context.close_path()
        context.stroke_preserve()
        context.set_source_rgba(0.0, 0.5, 0.5, 1.0)
        # and use it to fill the path (that we had kept)
        context.fill()
        context.stroke()

    def draw(self, widget, context):
        alloc = widget.get_allocation()
        width = alloc.width
        height = alloc.height

        xOffset = 20
        yOffset = 20

        imagesize = (width, height)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        # paint background
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)  # transparent black
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        self.draw_rounded_rect(context=ctx, x=2.5 + xOffset, y=2.5 + yOffset, width=150, height=150, radius=50, lineWidth=5)

        # save file
        # surface.write_to_png("MyImage.png")

        self.draw_rounded_rect(context=context, x=2.5 + xOffset, y=2.5 + yOffset, width=150, height=150, radius=50, lineWidth=5)

        # image = cairo.ImageSurface.create_from_png("MyImage.png")
        input_region = Gdk.cairo_region_create_from_surface(surface)
        widget.input_shape_combine_region(input_region)

    def on_eventbox_pressed(self, widget , event):
        if 'GDK_BUTTON_PRESS' in str(event.type): # If the user made a "single click"
            if event.button == 1: # if it is a left click
                print("button pressed")

    def on_eventbox_released(self, widget , event):
        print("button released")

# create and run the application, exit with the value returned by
# running the program
app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)