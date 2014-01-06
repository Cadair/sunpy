# -*- coding: utf-8 -*-
import copy

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

from mpl_toolkits.axes_grid1 import make_axes_locatable
import mpl_toolkits.axes_grid1.axes_size as Size

__all__ = ['ImageAnimator']

class SliderPB(widgets.Slider):
    __doc__= widgets.Slider.__doc__

    def __init__(self, ax, label, valmin, valmax, valinit=0.5, valfmt='%1.2f',
                 closedmin=True, closedmax=True, slidermin=None,
                 slidermax=None, dragging=True, **kwargs):

        widgets.Slider.__init__(self, ax, label, valmin, valmax, valinit=valinit,
                                valfmt=valfmt, closedmin=closedmin,
                                closedmax=closedmax, slidermin=slidermin,
                                slidermax=slidermax, dragging=dragging, **kwargs)

        self.changed_args = {}

    def set_val(self, val):
        xy = self.poly.xy
        xy[2] = val, 1
        xy[3] = val, 0
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % val)
        if self.drawon:
            self.ax.figure.canvas.draw()
        self.val = val
        if not self.eventson:
            return
        for cid, func in self.observers.iteritems():
            func(val, *self.changed_args[cid])

    def on_changed(self, func, *args):
        """
        When the slider value is changed, call *func* with the new
        slider position

        A connection id is returned which can be used to disconnect
        """
        cid = self.cnt
        self.observers[cid] = func
        self.changed_args[cid] = args
        self.cnt += 1
        return cid

class ButtonPB(widgets.Button):
    def __init__(self, ax, label, image=None,
                 color='0.85', hovercolor='0.95'):

        widgets.Button.__init__(self, ax, label, image=image,
                 color=color, hovercolor=hovercolor)

        self.clicked_args = {}

    def on_clicked(self, func, *args):
        """
        When the button is clicked, call this *func* with event

        A connection id is returned which can be used to disconnect
        """
        cid = self.cnt
        self.observers[cid] = func
        self.clicked_args[cid] = args
        self.cnt += 1
        return cid

    def _release(self, event):
        if self.ignore(event):
            return
        if event.canvas.mouse_grabber != self.ax:
            return
        event.canvas.release_mouse(self.ax)
        if not self.eventson:
            return
        if event.inaxes != self.ax:
            return
        for cid, func in self.observers.iteritems():
            func(event, *self.clicked_args[cid])

class ImageAnimator(object):
    """
    Create a matplotlib backend independant data explorer

    The following keyboard shortcuts are defined in the viewer:

    * 'left': previous step on active slider
    * 'right': next step on active slider
    * 'top': change the active slider up one
    * 'bottom': change the active slider down one
    * 'p': play/pause active slider

    Parameters
    ----------
    data: ndarray
        The data to be visualised > 2D

    image_axes: list
        The two axes that make the image

    fig: mpl.figure
        Figure to use

    axis_range: list of lists
        List of [min, max] pairs for each axis

    interval: int
        Animation interval in ms

    colorbar: bool
        Plot colorbar

    button_labels: list
        List of strings to label buttons

    button_func: list
        List of functions to map to the buttons

    Extra keywords are passed to imshow.
    """

    def __init__(self, data, image_axes=[-2,-1], fig=None,
                 axis_range=None, interval=200, colorbar=False, **kwargs):

        #Allow the user to specify the button func:
        self.button_func = kwargs.pop('button_func', [])
        self.button_labels = kwargs.pop('button_labels', [])
        self.num_buttons = len(self.button_labels)

        if not fig:
            fig = plt.figure()
        self.fig = fig

        self.data = data
        self.interval = interval
        self.if_colorbar = colorbar

        self.naxis = data.ndim
        self.num_sliders = self.naxis - 2
        if len(image_axes) != 2:
            raise ValueError("There can only be two spatial axes")

        all_axes_f = range(self.naxis)
        self.image_axes = [all_axes_f[i] for i in image_axes]

        all_axes = range(self.naxis)
        [all_axes.remove(x) for x in self.image_axes]
        slider_axes = all_axes

        if len(slider_axes) != self.num_sliders:
            raise ValueError("Specific the same number of axes as sliders!")
        self.slider_axes = slider_axes

        ax = self.slider_axes + self.image_axes
        ax.sort()
        if ax != range(self.naxis):
            raise ValueError("spatial_axes and sider_axes mismatch")

        if not axis_range:
            axis_range = [[0, i] for i in self.data.shape]
        else:
            for i,d in enumerate(self.data.shape):
                if axis_range[i][0] == axis_range[i][1]:
                    axis_range[i] = [0, d]
        self.axis_range = axis_range

        #create data slice
        self.image_slice = [slice(None)]*self.naxis
        for i in self.slider_axes:
            self.image_slice[i] = 0

        #Set active slider
        self.active_slider = 0
#==============================================================================
#         Begin Plotting etc.
#==============================================================================
        #Set a blank timer
        self.timer = None

        #Set up axes
        self._make_axes_grid()
        self._add_widgets()
        self._set_active_slider(0)

        #Create extent arg
        extent = []
        #reverse because numpy is in y-x and extent is x-y
        for i in self.image_axes[::-1]:
            extent += self.axis_range[i]

        imshow_args = {'interpolation':'nearest',
                       'origin':'lower',
                       'extent':extent}

        imshow_args.update(kwargs)
        self.im = self.axes.imshow(self.data[self.image_slice], **imshow_args)
        if self.if_colorbar:
            self._add_colorbar()

        #Set the current axes to the main axes so commands like plt.ylabel() work.
        plt.sca(self.axes)

#==============================================================================
#       Connect fig events
#==============================================================================
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        self.fig.canvas.mpl_connect('key_press_event', self._key_press)

    def _get_slice(self, i, n):
        """
        Slice an array, i'th element on n'th axes

        Parameters
        ----------
        i: int
            The element to select
        n: int
            The axis along which to index the i'th element
        """
        nax = self.naxis
        arr_slice = [slice(None)]*nax
        arr_slice[n] = i
        return arr_slice

    def _updatefig(self, ax_slice):
        self.im.set_array(self.data[ax_slice])

    def _add_colorbar(self):
        self.colorbar = plt.colorbar(self.im, self.cax)

    def _on_click(self, event):
        if event.inaxes in self.sliders:
            slider = self.sliders.index(event.inaxes)
            self._set_active_slider(slider)

    def _set_active_slider(self, ind):
        self._dehighlight_slider(self.active_slider)

        self._highliget_slider(ind)
        self.active_slider = ind

    def _highliget_slider(self, ind):
        ax = self.sliders[ind]
        [a.set_linewidth(2.0) for n,a in ax.spines.items()]
        self.fig.canvas.draw()

    def _dehighlight_slider(self, ind):
        ax = self.sliders[ind]
        [a.set_linewidth(1.0) for n,a in ax.spines.items()]
        self.fig.canvas.draw()

    def _make_axes_grid(self):
        self.axes = self.fig.add_subplot(111)

        #Split up the current axes so there is space for a start and a stop button
        self.divider = make_axes_locatable(self.axes)
        pad = 0.01 # Padding between axes
        pad_size = Size.Fraction(pad, Size.AxesX(self.axes))
        large_pad_size = Size.Fraction(0.1, Size.AxesY(self.axes))

        #Define size of useful axes cells, 50% each in x 20% for buttons in y.
        small_x = Size.Fraction((1.-2.*pad)/10, Size.AxesX(self.axes))
        ysize = Size.Fraction((1.-2.*pad)/15., Size.AxesY(self.axes))

        #Set up grid, 3x3 with cells for padding.
        if self.num_buttons > 0:
            xsize = Size.Fraction((1.-2.*pad)/self.num_buttons, Size.AxesX(self.axes))
            horiz = [xsize] + [pad_size, xsize]*(self.num_buttons-1) + \
                    [Size.Fraction(0.1, Size.AxesY(self.axes)), small_x]
            vert = [ysize, pad_size] * self.num_sliders + \
                   [large_pad_size, large_pad_size, Size.AxesY(self.axes)]
        else:
            vert = [ysize, pad_size] * self.num_sliders + \
                   [large_pad_size, Size.AxesY(self.axes)]
            horiz = [Size.Fraction(0.8, Size.AxesX(self.axes))] + \
                    [Size.Fraction(0.1, Size.AxesX(self.axes))]*2

        self.divider.set_horizontal(horiz)
        self.divider.set_vertical(vert)
        self.button_ny = len(vert) - 3


        #If we are going to add a colorbar it will need an axis next to the plot
        if self.if_colorbar:
            nx1 = -3
            self.cax = self.fig.add_axes((0.,0.,0.141,1.))
            locator = self.divider.new_locator(nx=-2, ny=len(vert)-1, nx1=-1)
            self.cax.set_axes_locator(locator)
        else:
            #Main figure spans all horiz and is in the top (2) in vert.
            nx1 = -1

        self.axes.set_axes_locator(self.divider.new_locator(nx=0, ny=len(vert)-1,
                                                  nx1=nx1))

    def _add_widgets(self):
        self.buttons = []
        for i in range(0,self.num_buttons):
            x = i*2
            #The i+1/10. is a bug that if you make two axes directly ontop of
            #one another then the divider doesn't work.
            self.buttons.append(self.fig.add_axes((0.,0.,0.+i/10.,1.)))
            locator = self.divider.new_locator(nx=x, ny=self.button_ny)
            self.buttons[-1].set_axes_locator(locator)
            self.buttons[-1]._button = widgets.Button(self.buttons[-1],
                                                         self.button_labels[i])
            self.buttons[-1]._button.on_clicked(self.button_func[i])

        self.sliders = []
        self.radio = []
        for i in range(self.num_sliders):
            x = i * 2
            self.sliders.append(self.fig.add_axes((0.,0.,0.01+i/10.,1.)))
            if self.num_buttons == 0:
                nx1 = 1
            else:
                nx1 = -3
            locator = self.divider.new_locator(nx=0, ny=x, nx1=nx1)
            self.sliders[-1].set_axes_locator(locator)
            sframe = SliderPB(self.sliders[-1], "%i"%i,
                                    self.axis_range[self.slider_axes[i]][0],
                                    self.axis_range[self.slider_axes[i]][1]-1,
                                    valinit=0, valfmt = '%i')
            sframe.on_changed(self._slider_changed, sframe)
            sframe.axes_num = self.slider_axes[i]
            sframe.cval = sframe.val
            self.sliders[-1]._slider = sframe

            self.radio.append(self.fig.add_axes((0., 0., 0.05+x/10., 1.)))
            if self.num_buttons == 0:
                nx = 2
            else:
                nx = 2 + 2*(self.num_buttons-1)
            locator = self.divider.new_locator(nx=nx, ny=x)
            self.radio[-1].set_axes_locator(locator)
            rdo = ButtonPB(self.radio[-1],">")
            rdo.on_clicked(self._click_button, rdo, sframe)
            rdo.clicked = False
            self.radio[-1]._radio = rdo

    def _click_button(self, event, button, slider):
        self._set_active_slider(slider.axes_num)
        if button.clicked:
            self._stop_play(event)
            button.clicked = False
            button.label.set_text(">")
        else:
            button.clicked = True
            self._start_play(event, button, slider)
            button.label.set_text("||")
        self.fig.canvas.draw()

    def _key_press(self, event):
        if event.key == 'left':
            self._previous(self.sliders[self.active_slider]._slider)
        elif event.key == 'right':
            self._step(self.sliders[self.active_slider]._slider)
        elif event.key == 'up':
            self._set_active_slider((self.active_slider+1)%self.num_sliders)
        elif event.key == 'down':
            self._set_active_slider((self.active_slider-1)%self.num_sliders)
        elif event.key == 'p':
            self._click_button(event, self.radio[self.active_slider]._radio, self.sliders[self.active_slider]._slider)

    def _start_play(self, event, button, slider=None):
        if not slider:
            slider = self.sliders[0]._sliders
        if not self.timer:
            self.timer = self.fig.canvas.new_timer()
            self.timer.interval = self.interval
            self.timer.add_callback(self._step, slider)
            self.timer.start()

    def _stop_play(self, event):
        if self.timer:
            self.timer.remove_callback(self._step)
            self.timer = None

    def _step(self, slider):
        s = slider
        if s.val >= s.valmax:
            s.set_val(s.valmin)
        else:
            s.set_val(s.val+1)

    def _previous(self, slider):
        s = slider
        if s.val <= s.valmin:
            s.set_val(s.valmin)
        else:
            s.set_val(s.val-1)

    def _slider_changed(self, val, slider):
        val = int(val)
        ax = slider.axes_num
        ax_slice = copy.copy(self.image_slice)
        ax_slice[ax] = val
        if val != slider.cval:
            self._updatefig(ax_slice)
            slider.cval = val

    def label_slider(self, i, label):
        """
        Change the Slider label

        Parameters
        ----------
        i: int
            The index of the slider to change (0 is bottom)
        label: str
            The label to set
        """
        self.sliders[i]._slider.label.set_text(label)