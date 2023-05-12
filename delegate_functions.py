import os
import shutil


def delegate_image(name, editor_folder, original_path):
    output = os.path.join(editor_folder, name)

    if not os.path.isdir(editor_folder):
        os.makedirs(editor_folder)

    try:
        shutil.copy2(original_path, output)
    except OSError:
        return "Failed"
