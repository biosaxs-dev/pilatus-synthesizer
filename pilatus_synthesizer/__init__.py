import platform

__version__ = "0.5.0"

def version_string():
    return 'Pilatus Synthesizer %s (python %s %s)' % (
        __version__, platform.python_version(), platform.architecture()[0]
    )
