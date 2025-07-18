from io import BytesIO
from typing import BinaryIO

import numpy
from PIL import Image


def generate_random_image(width: int = 800, height: int = 1000) -> BinaryIO:
    imarray = numpy.random.rand(width, height, 3) * 255
    im = Image.fromarray(imarray.astype("uint8")).convert("RGBA")
    output = BytesIO()
    im.save(output, format="PNG")
    output.seek(0)
    return output
