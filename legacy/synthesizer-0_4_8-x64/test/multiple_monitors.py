# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
import tkinter  as Tk

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from TestUtils      import open_explorer
from MachineTypes   import get_chassistype_name, get_display_resolution, get_monitors

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../..' )
from SynthesizerTestEnv import env_dict

res = get_display_resolution()
print( res )

monitors = get_monitors()
print( monitors )

in_folder = os.path.dirname( env_dict[ 'test_in_folder' ] ).replace( '/', '\\' )

open_explorer( in_folder, at=( res[0] + 800, 100 ) )

root = Tk.Tk()

root.geometry( "100x100+%d+0" % ( res[0] + 500 ) )
root.update()

root.mainloop()
