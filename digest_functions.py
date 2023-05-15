import numpy
from PIL import Image, ImageEnhance
import rawpy
import cv2
from colorthief import ColorThief as Ct


def get_thumbnail(image):
    try:
        raw = rawpy.imread(image)
        rgb = raw.postprocess()
        thumbnail_image = Image.fromarray(rgb)  # Pillow image
        thumbnail_image = thumbnail_image.resize((150, 120))
        del raw
    except rawpy._rawpy.LibRawFileUnsupportedError:
        return "no thumbnail"

    return thumbnail_image


def check_exposure(col_image):
    image = col_image.convert('1', dither=Image.NONE)

    num_bright = 0
    num_dark = 0

    for y in range(image.height):
        for x in range(image.width):
            this_pixel = image.getpixel((x, y))
            if this_pixel > 220:
                num_bright += 1
            elif this_pixel < 20:
                num_dark += 1

    if num_bright > 0.95 * 18000:
        exposure = "Overexposed"
    elif num_dark > 0.95 * 18000:
        exposure = "Underexposed"
    else:
        exposure = "Exposed correctly"

    print(num_bright, num_dark, exposure)

    return exposure


def check_colour(image):
    colour_dominance = "None"
    colour_thief = Ct(image)
    colour_dominance = colour_thief.get_color(quality=1)

    return colour_dominance


def blur_detect(image):
    image.convert('RGB')
    cv_img = numpy.array(image)

    mono = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(mono, cv2.CV_64F).var()

    if fm < 95:
        blur = True
    else:
        blur = False

    return blur
