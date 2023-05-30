import os
import shutil
import exifread
from global_functions import is_media


def ingest_image(activity_list, body, optics, orientation, current_image, root, name, current_file, backup_root):
    body_name = "unknown body"
    lens_name = "unknown lens"
    orientation_str = "unknown"
    ingest_failed = False

    output = ""
    message = "Shot on "

    if body.get() == 0 and optics.get() == 0 and orientation.get() == 0:
        pass
    else:
        try:
            file = open(current_image, 'rb')
            if is_media(current_image) == "video":
                output = os.path.join(output, "Videos")
            else:
                if optics.get() == 1:
                    tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                else:
                    tags = exifread.process_file(file, stop_tag='Image Orientation', details=False)

                file.close()

                if body.get() == 1:
                    if "Image Model" in tags:
                        body_name = str(tags['Image Model']).strip()
                    else:
                        body_name = "unknown body"

                    output = os.path.join(output, body_name.replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))
                    message += f"{body_name} "

                if optics.get() == 1:
                    if "EXIF LensModel" in tags:
                        lens_name = str(tags['EXIF LensModel']).strip()
                    else:
                        lens_name = "unknown lens"

                    output = os.path.join(output, lens_name.replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))
                    message += f"with {lens_name} "

                if orientation.get() == 1:
                    if "Image Orientation" in tags:
                        orientation_str = str(tags['Image Orientation']).strip()
                    else:
                        orientation_str = "unknown"

                    output = os.path.join(output, orientation_str.replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))
                    message += f"in {orientation_str} orientation"

                if body_name == "unknown body" and lens_name == "unknown lens" and orientation_str == "unknown":
                    output = "Unsorted (No image data)"

        except FileNotFoundError:
            ingest_failed = True

    next_index = activity_list.size() + 1

    main_out = os.path.join(root, output)

    if os.path.isfile(os.path.join(main_out, current_file)) or os.path.isfile(os.path.join(main_out, name)):
        message = f"{current_file}: Skipped image as it already exists in the output folder"
    else:

        try:
            if not os.path.isdir(main_out):
                os.makedirs(main_out)

            shutil.copy2(current_image, main_out)

            if name != "" and not os.path.exists(os.path.join(main_out, name)):
                original_output_file_dir = os.path.join(main_out, current_file)
                final_dir = os.path.join(main_out, name)
                os.rename(original_output_file_dir, final_dir)
        except FileNotFoundError:
            ingest_failed = True
        except PermissionError:
            ingest_failed = True

        if backup_root != "":
            try:
                backup_out = os.path.join(backup_root, output)

                if not os.path.exists(backup_out):
                    os.makedirs(backup_out)

                shutil.copy2(current_image, backup_out)

                if name != "":
                    original_backup_file_dir = os.path.join(backup_out, current_file)
                    final_backup_dir = os.path.join(backup_out, name)
                    os.rename(original_backup_file_dir, final_backup_dir)

            except FileNotFoundError:
                pass
            except FileExistsError:
                pass

        if body_name == "unknown body" and lens_name == "unknown lens" and orientation_str == "unknown":
            message = "Unsorted (No image data)"

    activity_list.insert(next_index, f"{current_file}: {message}")
    activity_list.yview_scroll(1, "unit")

    return ingest_failed
