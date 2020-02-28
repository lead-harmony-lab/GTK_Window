# Gtk3 has the shape_combine_region method which takes a cairo.Region object
# (see docs) which allows making the window a non rectangular shape. This would be straightforward by
# turning my cairo.ImageSurface (created from a png) into a region with Gdk.cairo_region_create_from_surface,
# however pycairo does not support the cairo.Region in

# gdk_window_is_shaped ()
# gdk_window_set_opaque_region ()
#    This function only works for toplevel windows.
# gdk_window_shape_combine_region ()
#     This function works on both toplevel and child windows.

# gtk_widget_shape_combine_mask()


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

'''
The expose event handler for the event box.

This function simply draws a transparency onto a widget on the area
for which it receives expose events.  This is intended to give the
event box a "transparent" background.

In order for this to work properly, the widget must have an RGBA
colourmap.  The widget should also be set as app-paintable since it
doesn't make sense for GTK+ to draw a background if we are drawing it
(and because GTK+ might actually replace our transparency with its
default background colour).
'''
def transparent_expose(widget, event):
    cr = widget.window.cairo_create()
    cr.set_operator(cairo.OPERATOR_CLEAR)

    # Ugly but we don't have event.region
    region = Gtk.gdk.region_rectangle(event.area)

    cr.region(region)
    cr.fill()

    return False

'''
The expose event handler for the window.

This function performs the actual compositing of the event box onto
the already-existing background of the window at 50% normal opacity.

In this case we do not want app-paintable to be set on the widget
since we want it to draw its own (red) background. Because of this,
however, we must ensure that we use g_signal_register_after so that
this handler is called after the red has been drawn. If it was
called before then GTK would just blindly paint over our work.

Note: if the child window has children, then you need a cairo 1.16
feature to make this work correctly.
'''
def window_expose_event(widget, event):

    #get our child (in this case, the event box)
    child = widget.get_child()

    #create a cairo context to draw to the window
    cr = widget.window.cairo_create()

    #the source data is the (composited) event box
    cr.set_source_pixmap (child.window,
                          child.allocation.x,
                          child.allocation.y)

    #draw no more than our expose event intersects our child
    region = Gtk.gdk.region_rectangle(child.allocation)
    r = Gtk.gdk.region_rectangle(event.area)
    region.intersect(r)
    cr.region (region)
    cr.clip()

    #composite, with a 50% opacity
    cr.set_operator(cairo.OPERATOR_OVER)
    cr.paint_with_alpha(0.5)

    return False

# Make the widgets
w = Gtk.Window()
b = Gtk.Button("A Button")
e = Gtk.EventBox()

# Put a red background on the window
red = Gtk.gdk.color_parse("red")
w.modify_bg(Gtk.STATE_NORMAL, red)

# Set the colourmap for the event box.
# Must be done before the event box is realised.
screen = e.get_screen()
rgba = screen.get_rgba_colormap()
e.set_colormap(rgba)

# Set our event box to have a fully-transparent background
# drawn on it. Currently there is no way to simply tell GTK+
# that "transparency" is the background colour for a widget.
e.set_app_paintable(True)
e.connect("expose-event", transparent_expose)

# Put them inside one another
w.set_border_width(10)
w.add(e)
e.add(b)

# Realise and show everything
w.show_all()

# Set the event box GdkWindow to be composited.
# Obviously must be performed after event box is realised.
e.window.set_composited(True)

# Set up the compositing handler.
# Note that we do _after_ so that the normal (red) background is drawn
# by gtk before our compositing occurs.
w.connect_after("expose-event", window_expose_event)

Gtk.main()