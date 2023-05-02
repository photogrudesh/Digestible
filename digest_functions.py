from PIL import Image
from io import BytesIO

import exifread as exifread


def get_thumbnail(image):
    img = open(image, "rb")

    tags = exifread.process_file(img, stop_tag='JPEGThumbnail')

    try:
        thumbnail_tag = tags["JPEGThumbnail"]
        thumbnail_pixel_data = BytesIO(thumbnail_tag)
        return Image.open(thumbnail_pixel_data)
    except KeyError:
        return "no thumbnail"


def check_exposure(image):
    exposure = "Normal"

    average_pixel_value = 0
    bright_pixels = 0
    brightest_pixel = 0

    height = image.height
    width = image.width

    for y in range(height):
        for x in range(width):
            pixels = image.getpixel((x, y))
            this_pixel = (pixels[0] + pixels[1] + pixels[2]) / 3
            if this_pixel > brightest_pixel:
                brightest_pixel = this_pixel
            if this_pixel > 40:
                average_pixel_value += this_pixel
            if this_pixel > 180:
                bright_pixels += 1

    average_pixel_value = average_pixel_value / (height * width)

    if average_pixel_value > 180 and bright_pixels > 0.8 * (height * width):
        exposure = "Overexposed"
    elif bright_pixels < 0.1 * (height * width) and brightest_pixel < 180:
        exposure = "Underexposed"

    return exposure


def check_colour(image):
    colour_dominance = "None"
    average_pixels = [0, 0, 0]

    for y in range(image.height):
        for x in range(image.width):
            pixels = image.getpixel((x, y))
            if pixels[0] < 50 and pixels[0] < 50 and pixels[0] < 50:
                pass
            else:
                average_pixels[0] += pixels[0]
                average_pixels[1] += pixels[1]
                average_pixels[2] += pixels[2]

    for i in range(3):
        average_pixels[i - 1] = average_pixels[i - 1] / (image.height * image.width)

    highest = [0, None]

    for i in average_pixels:
        if i > highest[0]:
            highest[0] = i
            highest[1] = average_pixels.index(i)

    match highest[1]:
        case 0:
            colour_dominance = "Red dominant"
        case 1:
            colour_dominance = "Green dominant"
        case 2:
            colour_dominance = "Blue dominant"

    for i in average_pixels:
        if highest[0] - i < 10 and highest[0] - i != 0:
            colour_dominance = "Normal colour distribution"

    return colour_dominance


def blur_detect(image):
    blur = False

    return blur
