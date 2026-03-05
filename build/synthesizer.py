"""Entry-point script for the embeddable distribution.

This file is invoked by pythonw.exe inside the embeddables/ folder.
"""
from pilatus_synthesizer.app import gui_main

gui_main()
