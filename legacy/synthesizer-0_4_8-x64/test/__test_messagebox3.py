# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
from nose.tools import eq_

sys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )
import KekLib, Synthesizer
from OurTkinter         import Tk
import OurMessageBox    as MessageBox

root = Tk.Tk()

label_ = Tk.Label( root, text="Hello" )
label_.pack()

button_ = Tk.Button( root, text="Ok", command=lambda: root.destroy() )
button_.pack()

MessageBox.showinfo( 'Info', 'This box should have global grab.', parent=root )

root.mainloop()
