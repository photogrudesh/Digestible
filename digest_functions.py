import numpy
import webcolors
from PIL import Image
import rawpy
import cv2
from colorthief import ColorThief as Ct

from global_functions import asset_relative_path


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


def get_colour_name(rgb_triplet):
    min_colours = {}
    for key, name in webcolors.CSS21_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - rgb_triplet[0]) ** 2
        gd = (g_c - rgb_triplet[1]) ** 2
        bd = (b_c - rgb_triplet[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def check_colour(image):
    image.save(asset_relative_path("thumbnail.jpg"))
    extracted_colour = Ct(asset_relative_path("thumbnail.jpg"))
    dominant_rgb = extracted_colour.get_color(quality=1)

    highest = 0

    for i in dominant_rgb:
        if i > highest:
            highest = i

    if 0.99 * dominant_rgb[1] < dominant_rgb[0] < 1.01 * dominant_rgb[1] and highest > dominant_rgb[2]:
        colour_dominance = "Yellow"
    elif 0.99 * dominant_rgb[0] < dominant_rgb[1] < 1.01 * dominant_rgb[0] and highest > dominant_rgb[2]:
        colour_dominance = "Yellow"
    elif dominant_rgb[2] == highest and highest > dominant_rgb[1] * 1.01 and highest > dominant_rgb[0] * 1.01:
        colour_dominance = "Blue"
    elif dominant_rgb[1] == highest and highest > dominant_rgb[2] * 1.015 and highest > dominant_rgb[0] * 1.015:
        colour_dominance = "Green"
    elif dominant_rgb[0] == highest and highest > dominant_rgb[1] * 1.3 and highest > dominant_rgb[2] * 1.3:
        colour_dominance = "Red"
    else:
        colour_dominance = "No colour dominance"

    return colour_dominance


def blur_detect(image):
    image.convert('RGB')
    cv_img = numpy.array(image)

    mono_file = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    focus_index = cv2.Laplacian(mono_file, cv2.CV_64F).var()

    if focus_index < 95:
        blur = True
    else:
        blur = False

    return blur
