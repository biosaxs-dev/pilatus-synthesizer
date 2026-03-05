"""Entry point for pilatus-synthesizer."""

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        prog='pilatus-synthesizer',
        description='Pilatus detector image synthesizer for SAXS beamlines',
    )
    parser.add_argument('-c', '--command', action='store_true',
                        help='run in command mode (no GUI)')
    parser.add_argument('-i', '--in-folder', dest='in_folder',
                        help='input image folder')
    parser.add_argument('-o', '--out-folder', dest='out_folder',
                        help='output image folder (default: IN_FOLDER/Synthesized)')
    parser.add_argument('-n', '--autonum-folders', action='store_true', dest='autonum_folders',
                        help='auto-number output folders if default exists')
    parser.add_argument('-j', '--adj-folder', dest='adj_folder',
                        help='adjusted image folder')
    parser.add_argument('-m', '--intermediate-results', action='store_true', dest='intermediate_results',
                        help='write intermediate results')
    parser.add_argument('-d', '--direction', choices=['left', 'right'],
                        help='positive adjustment direction: left (KEK-PF) or right (SPring-8)')
    parser.add_argument('-v', '--version', action='store_true',
                        help='show version info')
    return parser.parse_args()


def main():
    opts = parse_args()

    if opts.version:
        from pilatus_synthesizer import version_string
        print(version_string())
        sys.exit(0)

    if opts.command:
        from pilatus_synthesizer.cli.command import Controller
        controller = Controller(opts)
        controller.execute()
    else:
        gui_main()


def gui_main():
    from tkinterDnD import Tk
    from pilatus_synthesizer.gui.controller import Controller
    root = Tk()
    root.withdraw()
    Controller(root)
    root.mainloop()


if __name__ == '__main__':
    main()
