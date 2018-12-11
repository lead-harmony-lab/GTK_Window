from ctypes import *
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('PangoCairo', '1.0')



import time
import math
import cairo

from gi.repository import GLib, Gdk, Gtk, Pango, PangoCairo

HEIGHT_FRACTION = 2.5
COUNTDOWN_STEPS = 5
FPS = 24
LIBPIXMAN_NAME = "libpixman-1.so"
PIXMAN_FILTER_CONVOLUTION = 5
PIXMAN_OP_SRC = 1
PIXMAN_a8r8g8b8 = 0x20028888


class Countdown:
    def setupPixman(self, name):
        libpixman = cdll.LoadLibrary(name)
        self.pixman_image_create_bits = libpixman.pixman_image_create_bits
        self.pixman_image_set_filter = libpixman.pixman_image_set_filter
        self.pixman_image_composite = libpixman.pixman_image_composite
        self.pixman_image_unref = libpixman.pixman_image_unref

    def drawNumber(self, cr, width, height, number):
        # create pango desc/layout
        if (self.layout == None):
            self.layout = PangoCairo.create_layout(cr)
            self.desc = Pango.font_description_from_string("Ubuntu Mono")
            self.desc.set_absolute_size(0.75 * height * Pango.SCALE)
            self.desc.set_weight(Pango.Weight.NORMAL)
            self.desc.set_style(Pango.Style.NORMAL)
            self.layout.set_font_description(self.desc)

        # print and layout string (pango-wise)
        self.layout.set_text(str(number), -1)

        # determine center position for number
        rects = self.layout.get_extents()
        x = width / 2 - rects[0].x / Pango.SCALE - rects[0].width / Pango.SCALE / 2;
        y = height / 2 - rects[0].y / Pango.SCALE - rects[0].height / Pango.SCALE / 2;

        # draw text
        cr.move_to(x, y)
        PangoCairo.layout_path(cr, self.layout)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.fill()

    def createGaussianBlurKerne1D(self, radius, sigma):
        scale2 = 2.0 * sigma * sigma
        scale1 = 1.0 / (math.pi * scale2)
        size = 2 * radius + 1;
        n_params = size

        tmp = (c_double * n_params)()
        tmpSum = 0.0
        i = 0

        # caluclate gaussian kernel in floating point format
        for x in range(-radius, radius + 1):
            u = x * x
            tmp[i] = scale1 * math.exp(-u / scale2)
            tmpSum += tmp[i]
            i += 1

        # normalize gaussian kernel and convert to fixed point format
        params = (c_int32 * (n_params + 2))()

        params[0] = size << 16
        params[1] = 1 << 16

        for i in range(n_params):
            params[2 + i] = int((tmp[i] / tmpSum) * 65536.0)

        n_params += 2

        return params, n_params

    def blurSurface(self, surface, data, radius, sigma):
        width = surface.get_width()
        height = surface.get_height()
        stride = surface.get_stride()
        format = surface.get_forcontextmat()

        # create pixman image for cairo image surface
        src = self.pixman_image_create_bits(PIXMAN_a8r8g8b8, width, height, data, stride)

        # attach gaussian kernel to pixman image
        params, n_params = self.createGaussianBlurKerne1D(radius, sigma)
        self.pixman_image_set_filter(src, PIXMAN_FILTER_CONVOLUTION, params, n_params)

        # render blured image to new pixman image
        pass1Data = (c_uint32 * stride * height)()
        pass1 = self.pixman_image_create_bits(PIXMAN_a8r8g8b8, width, height, pass1Data, stride)
        self.pixman_image_composite(PIXMAN_OP_SRC, src, None, pass1, 0, 0, 0, 0, 0, 0, width, height)
        self.pixman_image_unref(src)

        # flip the 1D kernel
        tmp = params[0]
        params[0] = params[1]
        params[1] = tmp
        self.pixman_image_set_filter(pass1, PIXMAN_FILTER_CONVOLUTION, params, n_params)

        pass2Data = (c_ubyte * stride * height)()
        pass2 = self.pixman_image_create_bits(PIXMAN_a8r8g8b8, width, height, pass2Data, stride)
        self.pixman_image_composite(PIXMAN_OP_SRC, pass1, None, pass2, 0, 0, 0, 0, 0, 0, width, height)
        self.pixman_image_unref(pass1)

        # create new cairo image for blured pixman image
        surface = cairo.ImageSurface.create_for_data(pass2Data, format, width, height, stride)
        self.pixman_image_unref(pass2)

        return surface

    def createDropShadow(self, width, height, blurRadius):
        stride = 4 * width
        format = cairo.FORMAT_ARGB32
        data = (c_uint32 * stride * height)()
        surface = cairo.ImageSurface.create_for_data(data, format, width, height)
        cr = cairo.Context(surface)

        # clear context
        cr.scale(width, height)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()

        # drop-shadow
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0.35, 0.35, 0.35, 0.8)
        cr.move_to(0.5, 0.5)
        cr.arc(0.5, 0.5, 0.4125, 0.0, math.pi / 180.0 * 360.0)
        cr.close_path()
        cr.fill()

        # blur surface
        blurredSurface = self.blurSurface(surface, data, 10, 3.0)

        return blurredSurface

    def render(self, cr, width, height, angle, number):
        # clear context
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()

        cr.set_operator(cairo.OPERATOR_SOURCE)

        # "drop-shadow" with blurrrrrrr!!!
        if (self.dropShadow):
            cr.set_source_surface(self.dropShadow, 0.0, 0.0)
            cr.paint()

        cr.save()

        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.scale(width, height)

        # draw "tinted" area
        cr.set_source_rgba(0.65, 0.65, 0.65, 0.9)
        cr.move_to(0.5, 0.5)
        fillRadian = -math.pi / 180.0 * (angle + 90.0);
        cr.arc(0.5, 0.5, 0.40375, math.pi / 180.0 * 270.0, fillRadian)
        cr.close_path()
        cr.fill()

        # draw black "grid"
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        cr.set_line_width(0.0025)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.move_to(0.5 - 0.40375, 0.5)
        cr.rel_line_to(2.0 * 0.40375, 0.0)
        cr.move_to(0.5, 0.5 - 0.40375)
        cr.rel_line_to(0.0, 2.0 * 0.40375)
        cr.stroke()

        # draw two thick black lines
        strokeRadian = math.pi / 180.0 * (angle - 180.0)
        x = math.sin(strokeRadian) * 0.40375
        y = math.cos(strokeRadian) * 0.40375
        cr.set_line_width(0.0125)
        cr.move_to(0.5, 0.5 - 0.40375)
        cr.line_to(0.5, 0.5)
        cr.rel_line_to(x, y)
        cr.stroke()

        # draw two white circles
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_line_width(0.0085)
        cr.arc(0.5, 0.5, 0.4, 0.0, 2 * math.pi)
        cr.stroke()
        cr.arc(0.5, 0.5, 0.35, 0.0, 2 * math.pi)
        cr.stroke()

        cr.restore()
        self.drawNumber(cr, width, height, number)

    def onDraw(self, widget, cr, number):
        secondsf = time.time() - self.starttime
        seconds = math.trunc(secondsf) % number
        angle = (math.trunc(secondsf) - secondsf) * 360.0
        self.render(cr, widget.get_allocated_width(), widget.get_allocated_height(), angle, number - seconds)

        if (number - seconds == 1):
            widget.set_opacity(1.0 + (math.trunc(secondsf) - secondsf))
        else:
            widget.set_opacity(1.0)

        return True

    def onScreenChanged(self, widget, oldScreen):
        screen = widget.get_screen()
        visual = screen.get_rgba_visual()
        if (visual == None):
            visual = screen.get_system_visual()
        widget.set_visual(visual)

    def onDelete(self, widget, event):
        Gtk.main_quit()
        return False

    def onTimeout(self, widget):
        widget.queue_draw()
        return True

    def __init__(self):
        # create gtk-window for drawing
        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_app_paintable(True)
        self.window.set_decorated(False)
        self.window.set_title("cairo-countdown")
        self.window.set_keep_above(True)
        self.window.set_focus_on_map(False)
        self.window.set_accept_focus(False)
        self.window.set_skip_pager_hint(True)
        self.window.set_skip_taskbar_hint(True)

        # make window click-through, this needs pycairo 1.10.0 for python3
        # to work
        rect = cairo.RectangleInt(0, 0, 1, 1)
        region = cairo.Region(rect)
        if (not region.is_empty()):
            self.window.input_shape_combine_region(None)
            self.window.input_shape_combine_region(region)

        # make sure that gtk-window opens with a RGBA-visual
        self.onScreenChanged(self.window, None)
        self.window.realize()
        self.window.set_type_hint(Gdk.WindowTypeHint.DOCK)
        transparent = Gdk.RGBA(0.0, 0.0, 0.0, 0.0)
        gdkwindow = self.window.get_window()
        gdkwindow.set_background_rgba(transparent)

        # center the gtk-window on the screen
        screen = self.window.get_screen()
        monitor = screen.get_monitor_at_window(gdkwindow)
        geo = screen.get_monitor_geometry(monitor)
        size = geo.height / HEIGHT_FRACTION
        self.window.set_size_request(size, size)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        # now it's time to show it
        self.window.show_all()

        # setup libpixman via ctypes
        self.setupPixman(LIBPIXMAN_NAME)

        # start timer and timeout
        self.timeoutId = GLib.timeout_add(1000 / FPS, self.onTimeout, self.window)
        self.layout = None
        self.desc = None
        self.starttime = time.time()
        self.dropShadow = self.createDropShadow(int(size), int(size), 10)

        # hook up signal-callbacks
        self.window.connect("screen-changed", self.onScreenChanged)
        self.window.connect("draw", self.onDraw, COUNTDOWN_STEPS)
        self.window.connect("delete-event", self.onDelete)


countdown = Countdown()
Gtk.main()
self.layout.unref()
self.desc.free()