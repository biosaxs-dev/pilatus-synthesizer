# coding: utf-8
"""

    DebugPlot.py

    work-around to debug matplotlib under tkinter

    Copyright (c) 2018-2020, Masatsuyo Takahashi, KEK-PF

"""
import matplotlib.pyplot as _plt
from matplotlib.pyplot import FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from OurTkinter import Tk, Dialog
from OurMatplotlib import NavigationToolbar
import matplotlib
# from CallStack import CallStack

def _reset():
    global dp, dp_list
    dp = None
    dp_list = []

_reset()

kill_button = True
cancel_button = True
ok_text = "OK"

def set_global_opts(**kwargs):
    global kill_button, cancel_button, ok_text
    ok_only = kwargs.pop('ok_only', False)
    ok_text = kwargs.pop('ok_text', "OK")

    if ok_only:
        kill_button = False
        cancel_button = False
    else:
        kill_button = kwargs.pop('kill_button', True)
        cancel_button = kwargs.pop('cancel_button', True)

def set_plot_env( parent=None, sub_parent=None ):
    global dp
    if sub_parent is None:
        dp = DebugPlot(parent)
    else:
        if dp is None:
            dp = DebugPlot(sub_parent)
    dp_list.append(dp)

def set_default_db():
    if dp is None:
        set_plot_env()

def push(parent=None):
    set_default_db()
    dp_ = DebugPlot(dp.parent if parent is None else parent)
    dp_list.append(dp_)
    return dp_

def pop():
    dp_list.pop()

def debug_plot_close():
    # not yet successful
    if dp is not None:
        dp.destroy()

class DebugPlot( Dialog ):
    def __init__( self, parent ):
        self.grab = 'local'     # used in grab_set
        if parent is None:
            from TkUtils import adjusted_geometry
            parent = Tk.Tk()
            parent.geometry( adjusted_geometry( parent.geometry() ) )
            parent.withdraw()
            parent.update()
        self.parent = parent
        self.mpl_canvas = None
        self.fig = None
        self.ax = None
        self.mplt_ge_2_2 = matplotlib.__version__ >= '2.2'
        """
            Call to self.body must be delayed until the figure
            for FigureCanvasTkAgg become available.
            Be aware that this is not yet a Tk widget.
            E.g., you can't Dialog.destroy this instance.
        """

    def figure( self, *args, **kwargs ):
        # assert self.fig is None
        if self.fig is not None:
            # self.fig.close()
            self.fig.clf()

        # print(CallStack())
        dialog_title = kwargs.pop('dialog_title', None)
        self.fig = _plt.figure( *args, **kwargs )
        self.ax = None
        self._do_init(title=dialog_title)
        # in this case, there is no need to _do_init in self.show
        return self.fig

    def _do_init(self, title=None, visible=False, block=False):
        if title is None:
            title = "DebugPlot"
        Dialog.__init__( self, self.parent, title, visible=visible, block=block )

    def _get_fig(self):
        if self.fig is None:
            # import traceback
            # traceback.print_stack()
            self.fig = _plt.gcf()
        return self.fig

    def _get_ax(self):
        if self.ax is None:
            self.ax = self._get_fig().gca()
        return self.ax

    def show( self, block=True, pause=None ):
        """
        There are following two cases.
            Case (1)                Case (2)
            dp = DebugPlot(root)    dp = DebugPlot(root)
                                    fig = plt.figure()
                                    ax = fig.gca()
            plt.plot(...)           ax.plot()
            plt.show()              plt.show()
        """
        if self.mpl_canvas is None:
            # Case (1)
            # fig should be obtained by self._get_fig(), i.e. _plt.gcf(), in self.body
            self._do_init()
        else:
            # Case (2)
            # self._do_init() has been already done by self.figure
            pass

        if self.mplt_ge_2_2:
            self.mpl_canvas.draw()
        else:
            self.mpl_canvas.show()

        self.applied =False
        try:
            self._show(block=block, pause=pause)
        except:
            # _tkinter.TclError: bad window path name ".!debugplot"
            # ignore this exception for it seems harmless
            pass
        return self.applied

    def body( self, body_frame ):   # overrides Dialog.body
        cframe = Tk.Frame( body_frame )
        cframe.pack()
        # figure should have been created before this call
        # (and before any creation of axes belonging to the figure)
        self.mpl_canvas = FigureCanvasTkAgg( self._get_fig(), cframe )
        self.mpl_canvas_widget = self.mpl_canvas.get_tk_widget()
        self.mpl_canvas_widget.pack( fill=Tk.BOTH, expand=1 )
        self.toolbar = NavigationToolbar( self.mpl_canvas, cframe )
        self.toolbar.update()

    def buttonbox( self ):
        box = Tk.Frame(self)
        box.pack()

        w = Tk.Button(box, text=ok_text, width=10, command=self.ok, default=Tk.ACTIVE)
        w.pack(side=Tk.LEFT, padx=5, pady=5)

        if cancel_button:
            w = Tk.Button(box, text="Cancel", width=10, command=self.cancel)
            w.pack(side=Tk.LEFT, padx=5, pady=5)

        if kill_button:
            w = Tk.Button(box, text="Kill", width=10, command=self.kill)
            w.pack(side=Tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def destroy(self):
        '''Destroy the window'''
        # print( "overriden destroy" )
        """
        TODO fix: there may be an instance of DebugPlot which has not been destroyed properly

          File "F:\PyTools\pytools-1_2_2-develop\lib\KekLib\OurTkinter.py", line 173, in ok
            self.withdraw()
          File "c:\program files\python36\lib\tkinter\__init__.py", line 1992, in wm_withdraw
            return self.tk.call('wm', 'withdraw', self._w)
        _tkinter.TclError: bad window path name ".!debugplot"

        SEE ALSO: 
        https://ja.osdn.net/projects/pylaf/scm/hg/pylaf/blobs/tip/src/pylafiii/mplext.py
        """
        # print( "before unbind", self.bind("<Destroy>") )
        self.unbind("<Destroy>")    # don't know whether this is the right way
        # print( "after unbind", self.bind("<Destroy>") )
        self.initial_focus = None
        Tk.Toplevel.destroy(self)

    def apply(self):
        self.applied = True

    def kill(self):
        import sys
        print('kill')
        self.parent.destroy()
        sys.exit()

def get_parent():
    set_default_db()
    dp = dp_list[-1]
    return dp.parent

def debug_plot_ok():
    set_default_db()
    dp = dp_list[-1]
    return dp.applied

def figure( *args, **kwargs ):
    set_default_db()
    dp = dp_list[-1]
    return dp.figure( *args, **kwargs )

def gcf():
    set_default_db()
    dp = dp_list[-1]
    return dp._get_fig()

def clf():
    set_default_db()
    dp = dp_list[-1]
    return dp._get_fig().clf()

def cla():
    set_default_db()
    dp = dp_list[-1]
    return dp._get_ax().cla()

def gca():
    fig = figure()
    return fig.gca()

def plot( *args, **kwargs ):
    return _plt.plot( *args, **kwargs )

def show( block=True, pause=None ):
    set_default_db()
    dp = dp_list[-1]
    ret = dp.show( block=block, pause=pause )
    return ret

def legend():
    return gcf().legend()

def tight_layout():
    return gcf().tight_layout()

def annotate( *args, **kwargs ):
    set_default_db()
    dp = dp_list[-1]
    return dp._get_ax().annotate( *args, **kwargs )

def subplots_adjust( *args, **kwargs ):
    return _plt.subplots_adjust( *args, **kwargs )

def subplots( *args, **kwargs ):
    set_default_db()
    dp = dp_list[-1]
    fig, axes = _plt.subplots( *args, **kwargs )
    dp.fig = fig
    dp.axes = axes
    return fig, axes

def close():
    _plt.close()

def update():
    """
    required in animation to get button events, etc.
    """
    dp.parent.update()

def setp(*args, **kwargs):
    _plt.setp(*args, **kwargs)

class DialogWrapper:
    def __init__(self, parent=None):
        self.parent = parent

    def __enter__(self):
        set_global_opts(ok_only=True, ok_text="Close")
        push(self.parent)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        show()
        pop()
        set_global_opts(ok_only=False)
