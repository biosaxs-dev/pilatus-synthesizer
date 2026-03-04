"""
DetectorSettings.py

Detector Settings Dialog
"""

from OurTkinter import Tk, Dialog, tk_set_icon_portable
from SynthesizerSettings import save_settings, get_setting, set_setting

class DetectorSettings(Dialog):
    def __init__(self, parent, title):
        Dialog.__init__(self, parent, title)

    def body(self, body_frame):
        tk_set_icon_portable(self, 'synthesizer')
 
        iframe = Tk.Frame(body_frame)
        iframe.pack(expand=1, fill=Tk.BOTH, padx=50, pady=10)

        grid_row = 0

        text =  """
Select the direction considered as positive for adjustment.
This setting is site-dependent. For example select:
        "Left"  for Photon Factory
        "Right" for SPring-8 
"""
        label = Tk.Label(iframe, text=text, justify=Tk.LEFT, wraplength=500, bg="white", width=60)
        label.grid(row=grid_row, column=0, columnspan=3, sticky=Tk.W, pady=20)

        label_spacing = '     '
        grid_row += 1
        syn_method_label = Tk.Label(iframe, text= 'Positive Adjust Direction:' + label_spacing)
        syn_method_label.grid(row=grid_row, column=0, sticky=Tk.E)
        self.positive_direction = Tk.StringVar()
        self.positive_direction.set(get_setting('positive_direction'))
        j = 0
        for t, method in (['Left', 'left'], ['Right', 'right']):
            b = Tk.Radiobutton(iframe, text='%-22.22s' % (t),
                            variable=self.positive_direction, value=method)
            j += 1
            b.grid(row=grid_row, column=j, sticky=Tk.W, pady=20)


    def apply(self):
        value = self.positive_direction.get()
        print("DetectorSettings: Positive Adjust Direction =", value)
        set_setting('positive_direction', None if value == 'None' else value)
        save_settings()