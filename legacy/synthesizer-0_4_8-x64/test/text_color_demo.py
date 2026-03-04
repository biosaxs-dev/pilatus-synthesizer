#!/usr/bin/env python3

import tkinter as tk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText

class Pad(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.toolbar = tk.Frame(self, bg="#eee")
        self.toolbar.pack(side="top", fill="x")

        self.bold_btn = tk.Button(self.toolbar, text="Error", command=self.make_error)
        self.bold_btn.pack(side="left")

        self.clear_btn = tk.Button(self.toolbar, text="Clear", command=self.clear)
        self.clear_btn.pack(side="left")

        # Creates a bold font
        self.bold_font = Font(family="Helvetica", size=14, weight="bold")

        self.text = ScrolledText(self)
        self.text.insert("end", "Select part of text and then click 'Bold'...")
        self.text.focus()
        self.text.pack(fill="both", expand=True)

        # configuring a tag called BOLD
        # self.text.tag_configure("BOLD", font=self.bold_font)
        self.text.tag_configure("ERROR",  foreground='red')

    def make_error(self):
        # tk.TclError exception is raised if not text is selected
        try:
            self.text.tag_add("ERROR", "sel.first", "sel.last")        
        except tk.TclError:
            pass

    def clear(self):
        self.text.tag_remove("ERROR",  "1.0", 'end')


def demo():
    root = tk.Tk()
    Pad(root).pack(expand=1, fill="both")
    root.mainloop()


if __name__ == "__main__":
    demo()