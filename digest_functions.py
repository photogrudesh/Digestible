import colorsys

from PIL import Image
import numpy
import rawpy
import cv2

from global_functions import asset_relative_path


def get_thumbnail(image):
    try:
        raw = rawpy.imread(image)
        rgb = raw.postprocess()
        thumbnail_image = Image.fromarray(rgb)  # Pillow image
        thumbnail_image = thumbnail_image.resize((round(thumbnail_image.width / 5), round(thumbnail_image.height / 5)))
        del raw
        del rgb
        thumbnail_image.save(asset_relative_path("preview.png"))
        # Generate thumbnail using Rawpy
    except rawpy._rawpy.LibRawFileUnsupportedError:
        return "no thumbnail"

    return thumbnail_image


def check_exposure(colour_image):
    exposure = "exposed correctly"
    colour_image = colour_image.resize((150, 120))
    bw_image = colour_image.convert("L")
    # generate black and white version of resized thumbnail

    histogram = [0, 0, 0, 0, 0, 0, 0]

    for y in range(bw_image.height):
        for x in range(bw_image.width):
            this_pixel = bw_image.getpixel((x, y))
            if 0 < this_pixel < 51:
                histogram[0] += 1
            elif 52 < this_pixel < 102:
                histogram[1] += 1
            elif 103 < this_pixel < 153:
                histogram[2] += 1
            elif 154 < this_pixel < 204:
                histogram[3] += 1
            elif 205 < this_pixel < 255:
                histogram[4] += 1
            elif this_pixel == 255:
                histogram[5] += 1
            elif this_pixel == 0:
                histogram[6] += 1
    # generate numeric "histogram"

    image_dimensions = bw_image.height * bw_image.width

    del bw_image

    if histogram[5] == 0 and histogram[2] < 700 and histogram[3] < 500 and histogram[4] < 200:
        if histogram[0] + histogram[1] > 0.9 * image_dimensions and histogram[4] < 300 and 1000 < histogram[0] and histogram[0] - histogram[1] > 1000:
            exposure = "underexposed"
        if histogram[3] + histogram[4] + histogram[2] < 7000 and histogram[0] > 4000:
            exposure = "underexposed"
        if histogram[6] > 3000:
            exposure = "underexposed"
    elif histogram[3] + histogram[4] < 50:
        exposure = "underexposed"

    if histogram[4] + histogram[3] > 0.9 * image_dimensions and histogram[0] + histogram[1] < 1000 < histogram[4] and histogram[4] - histogram[3] > 1000:
        exposure = "overexposed"
    if histogram[5] > 3000:
        exposure = "overexposed"
    # determine exposure

    return exposure


def check_colour(image):
    resized = image.resize((1, 1))
    dominant_rgb = resized.getpixel((0, 0))

    colour_deg = [0, 45, 90, 120, 180, 210, 240, 270, 300, 400]
    colour_name = ["Red", "Orange", "Green", "Green", "Light Blue", "Light Blue", "Blue", "Purple", "Purple", "Red"]

    converted_rgb = colorsys.rgb_to_hsv(dominant_rgb[0]/255, dominant_rgb[1]/255, dominant_rgb[2]/255)

    hsv = [converted_rgb[0] * 360, converted_rgb[1] * 100, converted_rgb[2] * 100]

    min_dist = None
    min_index = None

    highest_rgb = 0
    dominant = 0
    colour_dominance = "Normal colour distribution"

    for pixel in dominant_rgb:
        if pixel > highest_rgb:
            highest_rgb = pixel

    for pixel in dominant_rgb:
        if abs(highest_rgb - pixel) > 0.065 * highest_rgb:
            dominant += 1
        else:
            pass

    # Determine dominant colour based on how many pixels are close to the detected colour
    if dominant > 0:
        for i in colour_deg:
            if min_dist is None:
                min_dist = abs(i - hsv[0])
                min_index = 0
            else:
                if abs(i - hsv[0]) < min_dist:
                    min_dist = abs(i - hsv[0])
                    min_index = colour_deg.index(i)
                if abs(hsv[0] - i) < min_dist:
                    min_dist = abs(hsv[0] - i)
                    min_index = colour_deg.index(i)

        num_close = 0
        for y in range(image.height):
            for x in range(image.width):
                this_pixel = image.getpixel((x, y))
                hue = colorsys.rgb_to_hsv(this_pixel[0]/255, this_pixel[1]/255, this_pixel[2]/255)[0]
                if abs(hue * 360 - colour_deg[min_index]) < 20:
                    num_close += 1

        if num_close > 6000 and min_dist < 15 and hsv[1] > 20:
            colour_dominance = colour_name[min_index]
        # if criteria are met, determine colour name

    image.close()

    return colour_dominance


def get_image_contents(image, detector, predictor):
    image.save(asset_relative_path("thumbnail.jpg"))
    input_im = asset_relative_path("thumbnail.jpg")
    taste_output_generated = False
    # Save and reopen thumbnail

    detections = detector.detectObjectsFromImage(
        input_image=input_im,
        output_image_path=asset_relative_path("taste_output.jpg"),
        minimum_percentage_probability=30
    )
    # detect objects using yolov3

    objects_present = []
    persons_present = 0
    person_area = 0
    classification = ["Unclassified"]

    for current_object in detections:
        if current_object["name"] == "person" and current_object["percentage_probability"] > 95:
            persons_present += 1

            area = (current_object["box_points"][2] - current_object["box_points"][0]) * (
                        current_object["box_points"][3] - current_object["box_points"][1])

            person_area += area
        elif current_object["percentage_probability"] > 95:
            area = (current_object["box_points"][2] - current_object["box_points"][0]) * (
                    current_object["box_points"][3] - current_object["box_points"][1])

            if area > 0.5 * image.height * image.width:
                objects_present.append(current_object["name"])
        # determine areas of people and objects present

    if persons_present == 1 and person_area > 0.8 * image.height * image.width:
        classification = ["Portrait"]
    elif persons_present > 5 and person_area > 0.7 * image.height * image.width:
        classification = ["Group Photo"]
    elif persons_present > 10:
        classification = ["Many people present", persons_present]
    elif persons_present > 0:
        classification = ["People present", persons_present]
    elif len(objects_present) > 0:
        classification = [f"{objects_present[0]}"]
    # classify images differently based on the number of people present and the area covered by people

    if classification[0] == "Unclassified":
        # predict contents of image using resnet if no objects were found
        prediction, probability = predictor.classifyImage(
            input_im, result_count=1
        )

        if probability[0] > 90:
            classification[0] = prediction[0]

        if prediction[0] == "person":
            classification = ["People present", 1]
    else:
        taste_output_generated = True

    if taste_output_generated:
        preview = Image.open(asset_relative_path("taste_output.jpg"))
        preview.save(asset_relative_path("preview.png"))
    else:
        preview = image
        preview.save(asset_relative_path("preview.png"))
    # save preview to be displayed on screen

    return classification


def check_image_blur(image):
    image.convert('RGB')
    cv_img = numpy.array(image)

    monochrome_file = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    focus_index = cv2.Laplacian(monochrome_file, cv2.CV_64F).var()

    if focus_index < 30:
        blur = True
    else:
        blur = False
    # If calculated focus index is too low, declare image as blurry

    return blur
