import os
import shutil
import exifread
from global_functions import is_media


class Ingest:
    def __init__(self, body, optics, orientation, root, backup_root, file_names, activity_list, ingest_name):
        self.complete_message = ""
        self.body = body
        self.optics = optics
        self.orientation = orientation
        self.item = ""
        self.root = root
        self.backup_root = backup_root
        self.file_names = file_names
        self.current_file = ""
        self.activity_list = activity_list
        self.ingest_failed = False
        self.ingest_name = ingest_name

    def ingest_image(self):
        current_image = self.item
        name = ""

        output = ""

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
                if is_media(current_image) == "video":
                    output = os.path.join(output, "Videos")
                else:
                    if self.optics.get() == 1:
                        tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                    else:
                        tags = exifread.process_file(file, stop_tag='Image Orientation', details=False)

                    file.close()

                    if self.body.get() == 1 and "Image Model" in tags:
                        body_name = str(tags['Image Model']).strip()
                    else:
                        body_name = "Body unknown"

                    output = os.path.join(output, body_name.replace("/", "").replace("\\", "").replace("*", "").replace( ":", "").replace("<", "").replace(">", "").replace("|", ""))

                    if self.optics.get() == 1 and "EXIF LensModel" in tags:
                        lens_name = str(tags['EXIF LensModel']).strip()
                    else:
                        lens_name = "Lens unknown"

                    output = os.path.join(output, lens_name.replace("/", "").replace("\\", "").replace("*", "").replace( ":", "").replace("<", "").replace(">", "").replace("|", ""))

                    if self.orientation.get() == 1 and "Image Orientation" in tags:
                        orientation_str = str(tags['Image Orientation']).strip()
                    else:
                        orientation_str = "Orientation unknown"

                    output = os.path.join(output, orientation_str.replace("/", "").replace("\\", "").replace("*", "").replace( ":", "").replace("<", "").replace(">", "").replace("|", ""))

                    if body_name == "Body unknown" and lens_name == "Lens unknown" and orientation_str == "Orientation unknown":
                        output = "Unsorted (No image data)"

            except FileNotFoundError:
                self.ingest_failed = True

        next_index = self.activity_list.size() + 1

        main_out = os.path.join(self.root, output)

        if os.path.exists(os.path.join(main_out, name)) and name != "":
            self.activity_list.insert(next_index, f"Skipped {self.current_file}, file already exists at {output}")
            self.activity_list.yview_scroll(1, "unit")

        else:
            try:
                if not os.path.isdir(main_out):
                    os.makedirs(main_out)
                
                shutil.copy2(current_image, main_out)

                if name != "":
                    original_output_file_dir = os.path.join(main_out, self.current_file)
                    final_dir = os.path.join(main_out, name)
                    os.rename(original_output_file_dir, final_dir)
            except FileNotFoundError:
                self.ingest_failed = True

            try:
                backup_out = os.path.join(self.backup_root, output)

                if not os.path.isdir(backup_out):
                    os.makedirs(backup_out)
                    
                shutil.copy2(current_image, backup_out)

                if name != "":
                    original_backup_file_dir = os.path.join(backup_out, self.current_file)
                    final_backup_dir = os.path.join(backup_out, name)
                    os.rename(original_backup_file_dir, final_backup_dir)

            except FileNotFoundError:
                pass

            if body_name == "Unknown" and lens_name == "Unknown" and orientation_str == "Unknown":
                message = "Image was not sorted"
            else:
                message = f"Shot on {body_name.strip()} with {lens_name.strip()} in {orientation_str} orientation"

            self.activity_list.insert(next_index, f"{self.current_file}: {message}")
            self.activity_list.yview_scroll(1, "unit")
