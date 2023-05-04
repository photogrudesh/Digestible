from PIL import Image
import rawpy


def get_thumbnail(image):
    raw = rawpy.imread(image)
    rgb = raw.postprocess()
    thumbnail_image = Image.fromarray(rgb)  # Pillow image
    thumbnail_image = thumbnail_image.resize((150, 120))

    return thumbnail_image


def check_exposure(image):
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
    elif bright_pixels < 0.1 * (height * width) and brightest_pixel < 175:
        exposure = "Underexposed"
    else:
        exposure = "Exposed correctly"

    return exposure


def check_colour(image):
    colour_dominance = "None"
    reds, greens, blues = 0, 0, 0
    total_pixels = image.height * image.width

    for y in range(image.height):
        for x in range(image.width):
            pixels = image.getpixel((x, y))
            if pixels[0] < 50 and pixels[0] < 50 and pixels[0] < 50:
                pass
            else:
                highest_pixels = max(pixels)
                if highest_pixels == pixels[0]:
                    reds += 1
                elif highest_pixels == pixels[1]:
                    greens += 1
                elif highest_pixels == pixels[2]:
                    blues += 1

    highest = max(reds, greens, blues)

    if highest == reds and highest/total_pixels < 0.5:
        highest = max(greens, blues)

    if highest == reds:
        colour_dominance = "Red dominant"
    elif highest == greens:
        colour_dominance = "Green dominant"
    elif highest == blues:
        colour_dominance = "Blue dominant"

    try:
        if highest == reds and blues/greens < 0.1:
            colour_dominance = "Yellow dominant"
    except ZeroDivisionError:
        pass

    if blues == 0 and greens == 0:
        colour_dominance = "Black and white"

    if highest/total_pixels < 0.50:
        colour_dominance = "Normal colour distribution"

    return colour_dominance


def blur_detect(image):
    blur = False

    return blur
