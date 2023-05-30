import tkinter as tk
import os

import psutil

from environment import Environment
environment = Environment()


def is_media(file):
    media = "none"

    ext = file.split(".")[-1]
    raw_extensions = ["cr2", "rw2", "raf", "erf", "nrw", "nef", "arw", "rwz", "eip", "bay", "dng", "dcr", "gpr",
                      "raw",
                      "crw", "3fr", "sr2", "k25", "kc2", "mef", "dng", "cs1", "orf", "mos", "ari", "kdc", "cr3",
                      "fff",
                      "srf", "srw", "j6i", "mrw", "mfw", "x3f", "rwl", "pef", "iiq", "cxi", "nksc", "mdc"]

    video_extensions = ["webm", "mpg", "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov",
                        "qt", "flv", "swf"]

    if ext.lower() in raw_extensions:
        media = "image"
    elif ext.lower() in video_extensions:
        media = "video"

    if os.name == "nt":
        filename = file.split("\\")[-1]
    else:
        filename = file.split("/")[-1]

    if filename.startswith('.'):
        media = "none"

    return media


def clear_screen(window):
    for widget in window.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(window, bg="#FFFFFF", height=700, width=1200, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)

    return canvas


def asset_relative_path(path):
    root_path = os.path.join(environment.get_main_path(), "assets")
    full_path = os.path.join(root_path, path)

    # full_path = os.path.join(environment.get_main_path(), path)

    return full_path


def write(config_file):
    with open('./config.dgstbl', 'w') as configfile:
        config_file.write(configfile)


def collect_inputs():
    inputs = []

    for i in psutil.disk_partitions():
        add_volume = True
        try:
            if psutil.disk_usage(i.mountpoint).total > 100000000000:
                add_volume = False
            if os.name == "posix" and i.mountpoint.startswith("/System") or i.mountpoint == "/":
                add_volume = False

            if add_volume:
                inputs.append(i.mountpoint)
        except PermissionError:
            pass

    return inputs


def make_btn_reactive(button_object, hover_colour, default_colour):
    button_object.bind("<Enter>", func=lambda: button_object.config(background=hover_colour))
    button_object.bind("<Leave>", func=lambda: button_object.config(background=default_colour))
