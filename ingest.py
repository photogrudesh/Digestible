import os
import shutil
import exifread
from global_functions import is_media


class Ingest:
    def __init__(self, body, optics, orientation, root, file_names, activity_list, ingest_name):
        self.complete_message = ""
        self.body = body
        self.optics = optics
        self.orientation = orientation
        self.item = ""
        self.root = root
        self.file_names = file_names
        self.current_file = ""
        self.activity_list = activity_list
        self.ingest_failed = False
        self.ingest_name = ingest_name

    def ingest_image(self):
        current_image = self.item
        name = ""

        output = self.root

        if self.current_file in self.file_names:
            try:
                file = open(current_image, 'rb')
                image_name = self.current_file.split(".")[0]
                extension = self.current_file.split(".")[-1]
                tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                name = image_name + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension
            except FileNotFoundError:
                self.ingest_failed = True

        body_name = "Unknown"
        lens_name = "Unknown"
        orientation_str = "Unknown"

        if self.body.get() == 0 and self.optics.get() == 0 and self.orientation.get() == 0:
            pass
        else:
            try:
                file = open(current_image, 'rb')

                if self.optics.get() == 1:
                    tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                else:
                    tags = exifread.process_file(file, stop_tag='Image Orientation', details=False)

                if self.body.get() == 1:
                    output = os.path.join(output,
                                          str(tags['Image Model']).replace("/", "").replace("\\", "").replace("*",
                                                                                                              "").replace(
                                              ":", "").replace("<", "").replace(">", "").replace("|", ""))
                    body_name = str(tags['Image Model'])

                if self.optics.get() == 1:
                    output = os.path.join(output,
                                          str(tags['EXIF LensModel']).replace("/", "").replace("\\", "").replace("*",
                                                                                                                 "").replace(
                                              ":", "").replace("<", "").replace(">", "").replace("|", ""))
                    lens_name = str(tags['EXIF LensModel'])

                if self.orientation.get() == 1:
                    output = os.path.join(output,
                                          str(tags['Image Orientation']).replace("/", "").replace("\\", "").replace("*",
                                                                                                                    "").replace(
                                              ":", "").replace("<", "").replace(">", "").replace("|", ""))
                    orientation_str = str(tags['Image Orientation'])

            except exifread.exceptions:
                if is_media(current_image) == "video":
                    output = os.path.join(output, "Videos")
                elif is_media(current_image) == "image":
                    output = os.path.join(output, "Unsorted (No image data)")
            except FileNotFoundError:
                self.ingest_failed = True

        next_index = self.activity_list.size() + 1

        if os.path.exists(os.path.join(output, name)) and name != "":
            self.activity_list.insert(next_index, f"Skipped {self.current_file}, file already exists at {output}")
            self.activity_list.yview_scroll(1, "unit")

        elif os.path.exists(os.path.join(output, self.current_file)):
            self.activity_list.insert(next_index, f"Skipped {self.current_file}, file already exists at {output}")
            self.activity_list.yview_scroll(1, "unit")
        else:
            if not os.path.isdir(output):
                os.makedirs(output)

            try:
                shutil.copy2(current_image, output)
            except FileNotFoundError:
                self.ingest_failed = True

            if name != "":
                original_output_file_dir = os.path.join(output, self.current_file)
                final_dir = os.path.join(output, name)
                os.rename(original_output_file_dir, final_dir)

            if body_name == "Unknown" and lens_name == "Unknown" and orientation_str == "Unknown":
                message = "Image was not sorted"
            else:
                message = f"Shot on {body_name.strip()} with {lens_name.strip()}"

            self.activity_list.insert(next_index, f"Ingested {self.current_file}: {message}")
            self.activity_list.yview_scroll(1, "unit")
