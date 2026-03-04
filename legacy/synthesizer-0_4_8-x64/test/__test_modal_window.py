##transient is only part of the solution. You also want to set the grab on the
##secondary window, and then wait for the secondary window to close.
##So this is the magical sequence to make a window modal in Tkinter: 
##transient, grab_set, wait_window. -Eric Brunel

from tkinter import *

root = Tk()

def go():
   wdw = Toplevel()
   wdw.geometry('+400+400')
   e = Entry(wdw)
   e.pack()
   e.focus_set()
   wdw.transient(root)
   wdw.grab_set()
   root.wait_window(wdw)
   #print 'done!'

Button(root, text='Go', command=go).pack()
Button(root, text='Quit', command=root.destroy).pack()

root.mainloop()