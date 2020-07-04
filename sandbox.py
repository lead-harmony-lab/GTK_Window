import cairo
import gi
import math

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk

class TransparentWindow(Gtk.Window):
    def __init__(self):
        # create gtk-window for drawing
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_app_paintable(True)
        # self.window.set_decorated(False)
        self.window.set_title("cairo-countdown")
        # self.window.set_keep_above(True)
        # self.window.set_focus_on_map(False)
        # self.window.set_accept_focus(False)
        # self.window.set_skip_pager_hint(True)
        # self.window.set_skip_taskbar_hint(True)

        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect('draw', self.draw)





        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.window.set_visual(visual)


        # # make window click-through, this needs pycairo 1.10.0 for python3
        # # to work
        # rect = cairo.RectangleInt(0, 0, 1, 1)
        # region = cairo.Region(rect)
        # if (not region.is_empty()):
        #     self.window.input_shape_combine_region(None)
        #     self.window.input_shape_combine_region(region)


        self.window.show_all()

    def draw(self, widget, context):
        context.set_source_rgba(1, 1, 1, 1)
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

        context.set_source_surface(overlay, 0, 0)
        #context.paint()

        # custom window shape
        # sface = context.get_group_target()
        # mregion = Gdk.cairo_region_create_from_surface(sface)
        # self.get_window().imput_shape_combine_region(mregion, 0, 0)

        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)


TransparentWindow()
Gtk.main()