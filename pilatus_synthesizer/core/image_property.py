"""TIFF header property extraction for Pilatus detector images.

Core function for reading TIFF image description metadata.
The GUI display class (ImagePropertyWindow) is in pilatus_synthesizer.gui.

Original: lib/PilatusImageProperty.py (core part only)
Copyright (c) SAXS Team, KEK-PF
"""

from PIL import Image, TiffImagePlugin

IMAGEDESCRIPTION = TiffImagePlugin.IMAGEDESCRIPTION  # 270


def get_tiffinfo(image):
    """Extract TIFF metadata from a PIL Image object."""
    info = TiffImagePlugin.ImageFileDirectory()

    description = image.tag.get(IMAGEDESCRIPTION)
    if description:
        info[IMAGEDESCRIPTION] = description[0]

    return info


def get_properties(path):
    """Read TIFF description text from a file path."""
    im = Image.open(path)

    tiffinfo = get_tiffinfo(im)
    description = tiffinfo.get(IMAGEDESCRIPTION)

    if description:
        return description[0]
    else:
        return 'Tiff file has no property text.'
