import configparser
import datetime
import shutil
import time
import tkinter as tk
from threading import *

import PIL
from PIL import Image, ImageTk

import math
import requests as requests

from global_functions import is_media
from global_functions import clear_screen
from global_functions import asset_relative_path
from global_functions import write
from global_functions import collect_inputs

from ingest_functions import ingest_image
import digest_functions
import delegate_functions

import exifread
from tkinter import ttk
from tkinter import filedialog

import os

from imageai.Detection import ObjectDetection
from imageai.Classification import ImageClassification

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath(asset_relative_path("yolov3.pt"))
detector.loadModel()

predictor = ImageClassification()
predictor.setModelTypeAsResNet50()
predictor.setModelPath(asset_relative_path("resnet50-19c8e357.pth"))
predictor.loadModel()

window = tk.Tk()
window.geometry("1200x700")
window.configure(bg="#FFFFFF")
window.resizable(False, False)
config = configparser.ConfigParser()
version_number = "Digestible v0.4.0"

# Initiate Windows toast notification service if running in a Windows Environment 
if os.name == "nt":
    # from win10toast import ToastNotifier
    # notify = ToastNotifier()
    print("nt")

# window.iconbitmap(asset_relative_path("Digestible Icon.ico"))
icon_image = tk.Image("photo", file=asset_relative_path("Digestible Icon.png"))
window.tk.call('wm', 'iconphoto', window._w, icon_image)
# Set Tkinter taskbar icon variable 

image_list = []
file_names = []
delegating_to = []
average_time = 0
total_files = 0
saved_editors = []
selected_digest_dir = ""
selected_delegation_dir = ""
last_eta = 0
started_calculation = False
aborted = False

# initialise global variables


def button_hover_action(button, active_image, inactive_image):
    # bind hover events with specified images to passed button object 

    active = tk.PhotoImage(file=asset_relative_path(active_image))
    inactive = tk.PhotoImage(file=asset_relative_path(inactive_image))
    button.bind("<Enter>", func=lambda e: button.config(image=active))
    button.bind("<Leave>", func=lambda e: button.config(image=inactive))


def settings():
    canvas = clear_screen(window)

    window.title("Digestible · Settings")

    banner_text = "Settings"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Courier", 26 * -1, "bold"))

    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title 

    canvas.create_text(300, 140, text="Ingest Output Preferences", anchor="nw", fill="#37352F",
                       font=("Courier", 22 * -1, "bold"))

    output_img = tk.PhotoImage(file=asset_relative_path("main_output_btn.png"))
    add_default_output = tk.Button(image=output_img, bg="#FFFFFF", command=lambda: add_dir(default=True), anchor="nw",
                                   borderwidth=0, highlightthickness=0, relief="flat", padx=0, pady=0)
    add_default_output.place(x=300, y=180, width=249, height=35)

    backup_img = tk.PhotoImage(file=asset_relative_path("backup_btn.png"))
    add_backup_output = tk.Button(image=backup_img, bg="#FFFFFF", command=lambda: add_dir(default=False), anchor="nw",
                                  borderwidth=0, highlightthickness=0, relief="flat", padx=0, pady=0)
    add_backup_output.place(x=570, y=180, width=249, height=35)

    try:
        output = config['Program']['default output']
    except KeyError:
        output = "Not set"

    try:
        backup = config['Program']['backup output']
    except KeyError:
        backup = "Not set"
    # Check for backup and saved output to be displayed as text

    canvas.create_text(300, 230,
                       text=f"Current output: {output} \nCurrent backup: {backup}\n\nIngests will be saved to your output folder and your backup folder simultaneously.",
                       anchor="nw", fill="#37352F", width=870, font=("Courier", 16 * -1))

    if not config.has_option("Program", "saved editors"):
        config["Program"]["saved editors"] = ""
        write(config)
    # Update config file if missing saved editors key

    editors = config["Program"]["saved editors"].split("*")
    # Retrieve saved editors from config file

    try:
        editors.remove("")
    except ValueError:
        pass
    # Remove blank value (may arise with empty keys)

    canvas.create_text(300, 355, text=f"Delegate Speed Dial: {12 - len(editors)} slots left", anchor="nw",
                       fill="#37352F", font=("Courier", 22 * -1, "bold"))

    if len(editors) == 0:
        canvas.create_text(300, 395,
                           text="Save up to 12 frequently delegated to editors on delegate speed dial by adding names below!",
                           anchor="nw", fill="#37352F",
                           font=("Courier", 16 * -1), width=850)
    else:
        canvas.create_text(300, 395, text=f"{str(editors).replace('[', '').replace(']', '')}", anchor="nw",
                           fill="#37352F",
                           font=("Courier", 16 * -1), width=850)
    # Print Delegate speed dial text and currently saved editors

    if len(editors) == 0:
        placeholder_text = "Type to save editors"
    else:
        placeholder_text = str(editors).replace('[', '').replace(']', '').replace("'", "")

    new_editors_var = tk.StringVar()
    editors_to_add = tk.Entry(window, textvariable=new_editors_var, font=("Courier", 14 * -1), width=80)
    editors_to_add.insert(0, f"{placeholder_text}")
    editors_to_add.tk_setPalette(background="#FFFFFF")
    editors_to_add.focus_set()
    editors_to_add.place(x=300.0, y=475)
    # draw entry box to modify delegate speed dial editors with currently saved editors as placeholder

    canvas.create_text(300, 515, text=f"Alter your saved editors by adding names separated by commas.", anchor="nw",
                       fill="#37352F", font=("Courier", 16 * -1))

    update_image = tk.PhotoImage(file=asset_relative_path("update_btn.png"))
    update_editors = tk.Button(image=update_image, command=lambda: add_editors(new_editors_var), borderwidth=0,
                               highlightthickness=0, relief="flat", bg="#FFFFFF", anchor="w")
    update_editors.place(x=972.0, y=468, width=125, height=35)

    window.mainloop()


def add_dir(default):
    if default:
        selected_folder = tk.filedialog.askdirectory(title="Add ingest output folder")
    else:
        selected_folder = tk.filedialog.askdirectory(title="Add backup output folder")
    # Change window title depending on which saved directory is being modified

    if os.name == "nt":
        selected_folder = selected_folder.replace("/", "\\")

    if selected_folder and default:
        config["Program"]["default output"] = str(selected_folder)
        write(config)
        main(f"Changed your default output to {selected_folder}")
    elif selected_folder and not default:
        config["Program"]["backup output"] = str(selected_folder)
        write(config)
        main(f"Changed your backup output to {selected_folder}")
    else:
        main("Did not change default output")
    # edit config file if changes were made


def add_editors(editor_string):
    new_string = ""
    editors = []
    editors_lower = []

    for i in editor_string.get().split(","):
        name = i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(
            ">", "").replace("|", "").replace("*", "")
        if len(editors) < 12 and name.lower() not in editors_lower and name != "Save some editors" and len(name) < 21:
            editors_lower.append(i.lower().strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(
                    ">", "").replace("|", "").replace("*", ""))
            editors.append(
                i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(
                    ">", "").replace("|", "").replace("*", ""))
        # replace unwanted characters in new editor names and save to editor list if not already present

    for name in editors:
        if editors.index(name) == 0:
            new_string = name
        else:
            new_string = new_string + "*" + name
    # Generate string to save

    config["Program"]["saved editors"] = new_string
    write(config)
    settings()
    # Update config file and refresh settings page


def get_sidebar_assets():
    banner = tk.PhotoImage(file=asset_relative_path("banner_g.png"))
    button_image_home = tk.PhotoImage(file=asset_relative_path("in_home.png"))
    button_image_ingest = tk.PhotoImage(file=asset_relative_path("in_ingest.png"))
    button_image_delegate = tk.PhotoImage(file=asset_relative_path("in_delegate.png"))
    button_image_digest = tk.PhotoImage(file=asset_relative_path("in_digest.png"))
    button_image_help = tk.PhotoImage(file=asset_relative_path("in_help.png"))
    button_image_settings = tk.PhotoImage(file=asset_relative_path("in_settings.png"))
    return banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings
    # Collect and return image assets to draw sidebar


def help_menu():
    canvas = clear_screen(window)

    window.title("Digestible · Help")
    banner_text = "Help"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Courier", 26 * -1, "bold"))

    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title

    canvas.create_text(725, 150, anchor="n",
                       text="\nWelcome! Digestible has three modes: Ingest, Digest, and Delegate. Each mode is designed to streamline your photography workflow, so you can spend less time sorting through images and more time doing what you love.\n\nIngest mode: This mode copies images from cards under 100GB in size to your computer while automatically sorting images by camera body, lens used, and orientation so you don't have to.\n\nAfter you've ingested your images, it's time to start culling!\n\nDigest mode: This mode automatically separates your images based on how usable they are by analysing exposure and blurriness\n\nDelegate: Once you've sorted your images, it's time to delegate them to your team for post-production. This mode splits the sorted images between editors evenly so post-production can begin as soon as possible.\n\nIf you have digested the folder already, Digestible will automatically delegate the digested folder and delegated images will be inside.\n\n\n\nRemember, Digestible is designed for use with RAW image formats exclusively and will not function with JPEGs.",
                       width=800, font=("Courier", 18 * -1), fill="#37352F")
    # Display help text

    window.mainloop()


def time_left(canvas, time_remaining, images_left):
    while True:
        # Calculate and update time remaining text on screen during an operation

        num_files = total_files - len(image_list)
        items_left = total_files - num_files

        eta = average_time * items_left

        if num_files / total_files < 0.1:
            eta = "Calculating time remaining"
        elif round(eta) < 2:
            eta = "Almost done"
        elif eta > 60:
            eta = "About " + str(round(eta / 60)) + " minute(s) remaining"
        elif eta > 3600:
            eta = "About " + str(round(eta / 60 / 60)) + " hours(s) remaining, this may take a while"
        elif eta > 86400:
            eta = "About " + str(round(eta / 60 / 60 / 24)) + " day(s) remaining, this may take a while"
        else:
            eta = "About " + str(round(eta)) + " seconds(s) remaining"
        # Convert eta to text format

        canvas.itemconfig(images_left, text=f"{str(len(image_list))} files left from {str(total_files)}")
        # Update remaining items text on screen

        canvas.itemconfig(time_remaining, text=eta)
        # Update time remaining text and rerun time_left function every 1 second


def disable_ingest_button(canvas, ingest_name_var, button_1, message):
    illegal_characters = ["\\", '/', '*', '?', '"', '<', '>', '|', ":"]
    illegal_name = False
    ingest_name = ingest_name_var.get()

    root = ""

    try:
        root = os.path.join(str(config["Program"]["default output"]), str(ingest_name))
        if not os.path.isdir(str(config["Program"]["default output"])):
            config["Program"]["default output"] = ""
            write(config)
            main("Default output path does not exist, add one in settings before ingesting")
    except KeyError:
        main("Add a default output path in settings before ingesting")
    # check if output path exists, clear key if non-existent and return to main menu

    for i in illegal_characters:
        if i in ingest_name_var.get():
            illegal_name = True
    # check ingest name for characters unaccepted by Windows

    if ingest_name == "" or ingest_name is None:
        canvas.itemconfig(message, text="Name the ingest below to start")
        button_1["state"] = "disabled"
    elif illegal_name:
        canvas.itemconfig(message, text='Avoid using \\ / : * ? " < > |')
        button_1["state"] = "disabled"
    elif os.path.exists(root):
        canvas.itemconfig(message,
                          text=f'Adding to existing ingest at {os.path.join(str(config["Program"]["default output"]), ingest_name)}')
        button_1["state"] = "normal"
    else:
        canvas.itemconfig(message,
                          text=f'Ingesting to {os.path.join(str(config["Program"]["default output"]), ingest_name)}')
        button_1["state"] = "normal"
    canvas.after(1, lambda: disable_ingest_button(canvas, ingest_name_var, button_1, message))
    # Disable buttons and show warning if ingest name is missing or contains an illegal character else enable button and show message with output path


def ingest():
    global image_list
    global total_files
    global average_time
    global file_names

    window.title("Digestible · Ingest")

    canvas = clear_screen(window)
    banner_text = "Ingest"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Courier", 26 * -1, "bold"))

    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title

    image_list = []
    file_names = []
    drive_files = []

    sort_orientation, sort_body, sort_optics = tk.IntVar(), tk.IntVar(), tk.IntVar()

    inputs = collect_inputs()
    # Search through filesystem for removable drives under 100 gigabytes in size

    extra_drive_files = 0
    for i in inputs:
        files_on_drive = 0
        for root, dirs, files in os.walk(i):
            for f in files:
                file_type = is_media(f)
                if f.startswith("."):
                    pass
                elif file_type == "image" or file_type == "video":
                    image_list.append(os.path.join(root, f))
                    files_on_drive += 1
        if inputs.index(i) > 2:
            extra_drive_files += files_on_drive

        drive_files.append(str(files_on_drive) + " files")
    # crawl through directories in identified drives looking for media files

    for i in image_list:
        if os.name == "nt":
            file_names.append(i.split("\\")[-1])
        else:
            file_names.append(i.split("/")[-1])
    # identify file name of each file

    total_files = len(image_list)
    drives = len(inputs)
    # save integer values of the number of images and inputs to be displayed on screen

    while len(inputs) < 3:
        inputs.append("No card detected")
        drive_files.append("0 files")
    # generate placeholder text for unplugged inputs

    if len(image_list) == 0:
        main("No RAW or videos files to ingest")
    # return to main if no ingestible files are present

    # draw ingest screen elements

    canvas.create_text(300.0, 650.0, anchor="nw", text="Sort By:", fill="#37352F", font=("Courier", 15 * -1))

    body = tk.Checkbutton(window, text="Body Type", variable=sort_body)
    body.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    body.place(x=380, y=648.0)

    optics = tk.Checkbutton(window, text="Optics", variable=sort_optics)
    optics.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    optics.place(x=473.0, y=648.0)

    orient = tk.Checkbutton(window, text="Orientation", variable=sort_orientation)
    orient.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    orient.place(x=541.0, y=648.0)

    current_time = datetime.datetime.now()
    default_name = current_time.strftime("%d-%m-%Y-%H-%M-%S")

    canvas.create_text(655, 653, text="Ingest Name:", anchor="nw", font=("Courier", 14 * -1), fill="#37352F")

    canvas.create_text(725, 220, anchor="n", justify="center",
                       text="Ingest Mode\n\nDesigned to simplify your ingest processes, Digestible will automatically look through your storage devices for RAW image formats and copy them over to your specified output folder.\n\nYou have three options: body, optics and orientation. Digestible will look at the image's exif information and determine where to place the files on your local disk.",
                       fill="#37352F",
                       font=("Courier", 16 * -1), width=820)

    ingest_name_var = tk.StringVar()
    ingest_name = tk.Entry(window, textvariable=ingest_name_var, font=("Courier", 10), width=30)
    ingest_name.insert(0, f"{default_name}")
    ingest_name.tk_setPalette(background="#FFFFFF")
    ingest_name.focus_set()
    ingest_name.place(x=760.0, y=651)

    button_image_1 = tk.PhotoImage(file=asset_relative_path("begin_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: operation_in_progress("Ingesting", drives=drives, body=sort_body,
                                                               optics=sort_optics, orientation=sort_orientation,
                                                               ingest_name=ingest_name_var.get().strip()),
                         relief="flat", padx=0, pady=0)
    button_1.place(x=1020.0, y=642.0, width=125, height=35)

    message = canvas.create_text(725.0, 595.0, anchor="n", text="Name the ingest below to start", fill="#37352F",
                                 font=("Courier", 15 * -1), width=850, justify="center")

    disable_ingest_button(canvas, ingest_name_var, button_1, message)

    if len(image_list) > 1000:
        canvas.create_text(725.0, 127.0, anchor="n", text=f"This may take a while, {len(image_list)} images to ingest",
                           fill="#FF0000", font=("Courier", 15 * -1), justify="center")
    else:
        canvas.create_text(725.0, 127.0, anchor="n",
                           text=f"{len(image_list)} images to ingest from {drives} drive(s) · Ignoring drives over 100 GB in size",
                           fill="#37352F", font=("Courier", 15 * -1), justify="center")

    canvas.create_text(500.0, 500.0, anchor="n", text=inputs[0], fill="#37352F", font=("Courier", 16 * -1))
    canvas.create_text(725.0, 500.0, anchor="n", text=inputs[1], fill="#37352F", font=("Courier", 16 * -1))
    canvas.create_text(950.0, 500.0, anchor="n", text=inputs[2], fill="#37352F", font=("Courier", 16 * -1))
    canvas.create_text(500.0, 534.0, anchor="n", text=drive_files[0], fill="#37352F", font=("Courier", 15 * -1))
    canvas.create_text(725.0, 534.0, anchor="n", text=drive_files[1], fill="#37352F", font=("Courier", 15 * -1))
    canvas.create_text(950.0, 534.0, anchor="n", text=drive_files[2], fill="#37352F", font=("Courier", 15 * -1))

    # draw ingest screen elements

    window.mainloop()


def digest():
    global total_files
    global image_list
    global file_names
    global selected_digest_dir

    window.title("Digestible · Digest")

    if selected_digest_dir == "":
        selected_folder = tk.filedialog.askdirectory(title="Select folder to digest", initialdir=config["Program"]["default output"])
        if selected_folder != "":
            selected_digest_dir = selected_folder
            digest()
        else:
            main("Digest aborted, no folder selected")
    # Ask user for folder to digest from

    image_list = []
    file_names = []

    if not os.path.exists(selected_digest_dir):
        selected_digest_dir = ""
        main("Digest folder missing or destroyed")
    # check folder still exists, else return to main menu

    if "Digested Images" in os.listdir(selected_digest_dir):
        selected_digest_dir = ""
        main('Folder has already been digested, delete the "Digested Images" folder to try again')
    # check if digested images folder is in the selected folder and return to the main menu

    for root, dirs, files in os.walk(selected_digest_dir):

        for f in files:
            if is_media(f) == "image":
                image_list.append(os.path.join(root, f))
                file_names.append(f)
    total_files = len(image_list)
    # Crawl through files and save paths of all raw image files

    if len(image_list) == 0:
        selected_digest_dir = ""
        main("No RAW images to digest")
    # return to main if no Raw files are present

    canvas = clear_screen(window)

    banner_text = "Digest"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Courier", 26 * -1, "bold"))

    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title

    # Draw screen elements

    if len(image_list) > 500:
        canvas.create_text(725.0, 590.0, anchor="n", text=f"{str(total_files)} files to digest. This may take a while",
                           fill="#37352F", font=("Courier", 16 * -1))
    else:
        canvas.create_text(400.0, 590.0, anchor="n", text=f"{str(total_files)} files to digest.", fill="#FFFFFF",
                           font=("Courier", 16 * -1))

    canvas.create_text(725, 180, anchor="n",
                       text="\nWelcome to Digest. This should be the second part of your improved post-production workflow, After ingesting, you might want to cull through the images you've just taken, but why bother doing that yourself. The digest mode has 3 options: Colour dominance, Exposure and Blur. \n\nExposure is the simplest and most common reason for an unusable image, Digestible will identify and remove any irrecoverably underexposed or overexposed images from your ingest folder. Be careful when digesting images if shot intentionally in low light.\n\nThe blur option will identify unusable images based on how blurry the image is. Use with caution if images are intentionally blurry (e.g. panning action shots).\n\nFinally the colour dominance option will split images based on the colour that is most dominant in the frame. \n\nRemember digest mode is not human and does not perceive colour the same way you do.\n\nHappy Digesting!",
                       width=800, font=("Courier", 16 * -1), fill="#37352F")

    canvas.create_text(300.0, 610.0, anchor="nw", text="Options:", fill="#37352F", font=("Courier", 16 * -1))

    taste, colour, exposure, blur = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()

    e1 = tk.Checkbutton(window, text="Colour dominance", variable=colour)
    e1.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e1.place(x=400.0, y=644.0)

    e3 = tk.Checkbutton(window, text="Blur detection", variable=blur)
    e3.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e3.place(x=535.0, y=644.0)

    e2 = tk.Checkbutton(window, text="Exposure", variable=exposure)
    e2.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e2.place(x=647.0, y=644.0)

    e3 = tk.Checkbutton(window, text="Taste (beta)", variable=taste)
    e3.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e3.place(x=300.0, y=644.0)

    # Draw screen elements

    if os.name == "nt":
        file_path = selected_digest_dir.split('\\')[-2] + "\\" + selected_digest_dir.split('\\')[-1]
    else:
        file_path = f"{selected_digest_dir.split('/')[-2]}/{selected_digest_dir.split('/')[-1]}"
    # edit file path to display based on os

    if len(file_path) > 55:
        file_path = f"{selected_digest_dir.split('/')[-1]}"
    if len(file_path) > 55:
        while len(file_path) > 52:
            file_path = file_path[:-1] + ''
        file_path += "..."
    # shorten file path if too long

    canvas.create_text(725.0, 135.0, anchor="n", text=f"Digesting from: {file_path}",
                       fill="#37352F",
                       font=("Courier", 18 * -1))

    button_image_2 = tk.PhotoImage(file=asset_relative_path("change_digest.png"))
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0,
                         command=lambda: change_dir("digest"), relief="flat", padx=0, pady=0)
    button_2.place(x=776.0, y=642.0, width=249, height=35)

    button_image_1 = tk.PhotoImage(file=asset_relative_path("begin_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: operation_in_progress("Digesting", colour=colour, exposure=exposure, blur=blur,
                                                               folder=selected_digest_dir, taste=taste), relief="flat", padx=0,
                         pady=0)
    button_1.place(x=1025.0, y=642.0, width=125, height=35)

    # Draw remaining screen elements

    window.mainloop()


def change_dir(operation):
    global selected_digest_dir
    global selected_delegation_dir

    selected_folder = tk.filedialog.askdirectory(title=f"Select folder to {operation}")
    if selected_folder != "" and operation == "digest":
        selected_digest_dir = selected_folder
        digest()
    elif selected_folder != "" and operation == "delegate":
        selected_delegation_dir = selected_folder
        delegate()
    else:
        main(f"Select a folder to {operation}")
    # Change dir depending on which operation is currently in use. Save for future use.


def delegate():
    global total_files
    global image_list
    global file_names
    global selected_delegation_dir

    window.title("Digestible · Delegate")

    if selected_delegation_dir == "":
        selected_folder = tk.filedialog.askdirectory(title="Select folder to digest", initialdir=config["Program"]["default output"])
        if selected_folder != "":
            selected_delegation_dir = selected_folder
            delegate()
        else:
            main("Delegate aborted, no folder selected")
    # Ask for directory to delegate from, if none provided return to main menu and display error

    image_list = []
    file_names = []
    files_to_delegate = 0
    digested_found = False

    if not os.path.exists(selected_delegation_dir):
        selected_delegation_dir = ""
        main("Delegate folder missing or destroyed")
    # Check to see if delegate folder still exists, if not return to main menu

    if "Digested Images" in os.listdir(selected_delegation_dir):
        digested_found = True
        selected_delegation_dir = os.path.join(selected_delegation_dir, "Digested Images")
    # Check to see if folder has been digested, if so change delegation dir to digested images folder

    if "Delegated Images" in os.listdir(selected_delegation_dir):
        selected_delegation_dir = ""
        main('Folder has already been delegated, delete the "Delegated Images" folder to try again')
    # Check to see if folder has been delegated, if so return to main menu and display warning

    for root, dirs, files in os.walk(selected_delegation_dir):
        if "Rejects" not in root.split("\\"):
            for f in files:
                if is_media(f) == "image" and not f.startswith("."):
                    image_list.append(os.path.join(root, f))
                    file_names.append(f)
                    files_to_delegate += 1
    total_files = len(image_list)
    # look through files in folder while ignoring those in the rejects folder.

    if len(image_list) == 0:
        selected_delegation_dir = ""
        main("No RAW files to delegate")
    # if no raw files present, return to main menu and display warning

    canvas = clear_screen(window)

    banner_text = "Delegate"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Courier", 26 * -1, "bold"))

    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title

    canvas.create_text(725.0, 600.0, anchor="n",
                       text="Enter the names (under 20 characters long) of up to 20 additional editors separated by commas.",
                       fill="#37352F", font=("Courier", 14 * -1))

    images_per_person_message = canvas.create_text(725.0, 123.0, anchor="n", text=f"", fill="#37352F",
                                                   font=("Courier", 15 * -1), width=880)

    try:
        editors = config["Program"]["saved editors"].split("*")
        if "" in editors:
            editors.remove("")
    except KeyError:
        editors = []
    # remove extra blank editor name if key is blank, if key does not exist display blank editor list

    d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, d2e7, d2e8, d2e9, d2e10, d2e11, d2e12 = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()

    # Display screen elements

    delegating_to_y = 332

    if len(editors) == 0:
        canvas.create_text(725, 564, text=f"Tip: You can add editors to the delegate speed dial from settings!",
                           anchor="n",
                           width=870,
                           fill="#37352F", font=("Courier", 15 * -1), justify="center")

    if len(editors) > 0:
        e1 = tk.Checkbutton(window, text=editors[0], variable=d2e1)
        e1.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e1.place(x=725.0, y=550.0, anchor="n")
        delegating_to_y = 325

    if len(editors) > 1:
        e2 = tk.Checkbutton(window, text=editors[1], variable=d2e2)
        e2.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e2.place(x=470.0, y=550.0, anchor="n")

    if len(editors) > 2:
        e3 = tk.Checkbutton(window, text=editors[2], variable=d2e3)
        e3.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e3.place(x=980.0, y=550.0, anchor="n")

    if len(editors) > 3:
        e4 = tk.Checkbutton(window, text=editors[3], variable=d2e4)
        e4.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e4.place(x=725.0, y=508.0, anchor="n")
        delegating_to_y = 288

    if len(editors) > 4:
        e5 = tk.Checkbutton(window, text=editors[4], variable=d2e5)
        e5.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e5.place(x=470.0, y=508.0, anchor="n")

    if len(editors) > 5:
        e6 = tk.Checkbutton(window, text=editors[5], variable=d2e6)
        e6.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e6.place(x=980.0, y=508.0, anchor="n")

    if len(editors) > 6:
        e7 = tk.Checkbutton(window, text=editors[6], variable=d2e7)
        e7.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e7.place(x=725.0, y=465.0, anchor="n")
        delegating_to_y = 265

    if len(editors) > 7:
        e8 = tk.Checkbutton(window, text=editors[7], variable=d2e8)
        e8.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e8.place(x=470.0, y=465.0, anchor="n")

    if len(editors) > 8:
        e9 = tk.Checkbutton(window, text=editors[8], variable=d2e9)
        e9.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e9.place(x=980.0, y=465.0, anchor="n")

    if len(editors) > 9:
        e10 = tk.Checkbutton(window, text=editors[9], variable=d2e10)
        e10.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e10.place(x=725.0, y=422.0, anchor="n")
        delegating_to_y = 264

    if len(editors) > 10:
        e11 = tk.Checkbutton(window, text=editors[10], variable=d2e11)
        e11.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e11.place(x=470.0, y=422.0, anchor="n")

    if len(editors) == 12:
        e12 = tk.Checkbutton(window, text=editors[11], variable=d2e12)
        e12.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
        e12.place(x=980.0, y=422.0, anchor="n")

    editor_names_var = tk.StringVar()
    editor_names = tk.Entry(window, textvariable=editor_names_var, font=("Courier", 15), width=47)
    editor_names.insert(0, f"Type extra names here")
    editor_names.tk_setPalette(background="#FFFFFF")
    editor_names.focus_set()
    editor_names.place(x=300.0, y=641, anchor="nw")

    if digested_found:
        canvas.create_text(725.0, 185.0, anchor="s",
                           text=f"Digested folder found (delegated images will be inside the digested folder)",
                           fill="#37352F",
                           font=("Courier", 15 * -1))

    delegating_to_message = canvas.create_text(725, delegating_to_y, text=f"Delegating to nobody", anchor="center",
                                               width=870,
                                               fill="#37352F", font=("Courier", 15 * -1), justify="center")

    button_image_1 = tk.PhotoImage(file=asset_relative_path("begin_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: operation_in_progress("Delegating", folder=selected_delegation_dir),
                         relief="flat", padx=0, pady=0)
    button_1.place(x=1040.0, y=640.0, width=125.0, height=35.0)

    button_image_2 = tk.PhotoImage(file=asset_relative_path("change_delegate.png"))
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0,
                         command=lambda: change_dir("delegate"), relief="flat", padx=0, pady=0)
    button_2.place(x=776.0, y=640.0, width=249, height=35)

    # Display screen elements

    canvas.after(20,
                 lambda: check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, d2e7,
                                                d2e8, d2e9, d2e10, d2e11, d2e12,
                                                editors, editor_names_var, images_per_person_message, button_1))
    # Continually check editor names for length and illegal characters

    window.mainloop()


def check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, d2e7, d2e8, d2e9, d2e10,
                           d2e11, d2e12, editors, entered_editors, images_per_person_message, start_button):
    global delegating_to
    delegating_to = []
    illegal_characters = ["\\", '/', '*', '?', '"', '<', '>', '|', ":"]
    illegal_name = False

    if d2e1.get() == 1 and editors[0] != "":
        delegating_to.append(editors[0])
    if d2e2.get() == 1 and editors[1] != "":
        delegating_to.append(editors[1])
    if d2e3.get() == 1 and editors[2] != "":
        delegating_to.append(editors[2])
    if d2e4.get() == 1 and editors[3] != "":
        delegating_to.append(editors[3])
    if d2e5.get() == 1 and editors[4] != "":
        delegating_to.append(editors[4])
    if d2e6.get() == 1 and editors[5] != "":
        delegating_to.append(editors[5])
    if d2e7.get() == 1 and editors[6] != "":
        delegating_to.append(editors[6])
    if d2e8.get() == 1 and editors[7] != "":
        delegating_to.append(editors[7])
    if d2e9.get() == 1 and editors[8] != "":
        delegating_to.append(editors[8])
    if d2e10.get() == 1 and editors[9] != "":
        delegating_to.append(editors[9])
    if d2e11.get() == 1 and editors[10] != "":
        delegating_to.append(editors[10])
    if d2e12.get() == 1 and editors[11] != "":
        delegating_to.append(editors[11])

    delegating_to_lower = []

    for i in delegating_to:
        delegating_to_lower.append(i.strip().lower())

    for i in illegal_characters:
        if i in entered_editors.get():
            illegal_name = True

    if illegal_name:
        message = 'Avoid using \\ / : * ? " < > |'
        start_button["state"] = "disabled"

    else:
        additional_editors = entered_editors.get().split(",")
        for i in additional_editors:
            name_to_add = i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<",
                                                                                                                 "").replace(
                ">", "").replace("|", "")
            if name_to_add != "Type names here" and name_to_add != "" and len(
                    i) < 20 and name_to_add.lower() not in delegating_to_lower and len(delegating_to) < 33:
                delegating_to.append(name_to_add)

        if len(delegating_to) == 0:
            message = "Delegating to nobody"
        else:
            message = f"Images will be delegated to the following editors\n\n {str(delegating_to).replace('[', '').replace(']', '')}"

    canvas.itemconfig(delegating_to_message, text=message)

    if len(delegating_to) == 0:
        canvas.itemconfig(images_per_person_message, text=f"Select some editors to begin delegating.")
        start_button["state"] = "disabled"
    elif len(delegating_to) == 1:
        canvas.itemconfig(images_per_person_message, text=f"Delegate to more than 1 person to begin delegating")
        start_button["state"] = "disabled"
    else:
        file_path = f"{selected_delegation_dir.split('/')[-2]}/{selected_delegation_dir.split('/')[-1]}"

        if len(file_path) > 41:
            file_path = f"{selected_delegation_dir.split('/')[-1]}"
        if len(file_path) > 41:
            while len(file_path) > 37:
                file_path = file_path[:-1] + ''
            file_path += "..."

        canvas.itemconfig(images_per_person_message,
                          text=f"{file_path} | Total Images: {total_files}  |  About {round(total_files / len(delegating_to))} images per person")
        start_button["state"] = "normal"

    canvas.after(50,
                 lambda: check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, d2e7,
                                                d2e8, d2e9, d2e10, d2e11, d2e12,
                                                editors, entered_editors, images_per_person_message, start_button))


def operation_in_progress(operation_type, colour=None, exposure=None, blur=None, folder=None, drives=None, body=None,
                          optics=None, orientation=None, ingest_name=None, taste=None):
    global image_list
    global total_files
    global average_time
    global started_calculation
    global delegating_to
    global selected_delegation_dir
    global selected_digest_dir
    selected_delegation_dir = ""
    selected_digest_dir = ""

    started_calculation = False
    average_time = 0

    window.title(f"Digestible · {operation_type}")

    canvas = clear_screen(window)

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=operation_type, fill="#F5F5F5", font=("Courier", 26 * -1, "bold"))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0, state="disabled")
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0, state="disabled")
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0, state="disabled")
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0,
                             state="disabled")
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0, state="disabled")
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0,
                             state="disabled")
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title

    time.sleep(1)

    if operation_type == "Delegating":
        output = os.path.join(folder, "Delegated Images")

        images_in_folder = 0
        current_folder = 0
        images_per_editor = math.floor(len(image_list) / len(delegating_to))

        for image in image_list:
            index = image_list.index(image)

            if os.name == "nt":
                current_file = image.split("\\")[-1]
            else:
                current_file = image.split("/")[-1]

            file_names.remove(current_file)

            file_name = current_file

            if current_folder > len(delegating_to) - 1:
                current_folder = current_folder - 1

            editor_output = os.path.join(output, delegating_to[current_folder])

            image_list[index] = [image, editor_output, file_name]
            print(image, editor_output, file_name, current_folder)
            images_in_folder += 1

            if images_in_folder == images_per_editor:
                images_in_folder = 0
                current_folder += 1

        image_list.sort(key=lambda item: item[1])

    button_image_1 = tk.PhotoImage(file=asset_relative_path("abort_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: main(f"{operation_type} Aborted"),
                         relief="flat", padx=0, pady=0)
    button_1.place(x=1020.0, y=638.0, width=125, height=35)

    if drives is None:
        canvas.create_text(725.0, 115.0, anchor="n",
                           text=f"{operation_type} {str(total_files)} files", fill="#37352F",
                           font=("Courier", 16 * -1))
    elif drives == 1:
        canvas.create_text(725.0, 115.0, anchor="n",
                           text=f"{operation_type} {str(total_files)} files from {str(drives)} drive", fill="#37352F",
                           font=("Courier", 16 * -1))
    else:
        canvas.create_text(725.0, 115.0, anchor="n",
                           text=f"{operation_type} {str(total_files)} files from {str(drives)} drives", fill="#37352F",
                           font=("Courier", 16 * -1))

    images_left = canvas.create_text(650.0, 618.0, anchor="n", text="", fill="#37352F", font=("Courier", 12 * -1))

    progress = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=700)
    progress.place(x=300, y=645)

    time_remaining = canvas.create_text(650.0, 674.0, anchor="n", text="", fill="#37352F",
                                        font=("Courier", 12 * -1))
    activity_list = tk.Listbox(font=("Courier", 20 * -1))
    if taste.get() == 1:
        activity_list.place(x=300.0, y=150.0, width=600.0, height=460.0)
    else:
        activity_list.place(x=300.0, y=150.0, width=850.0, height=460.0)

    preview_image = Image.open(asset_relative_path("Digestible Icon.png")).resize((200, 200))

    test = ImageTk.PhotoImage(preview_image)

    preview = tk.Label(image=test)
    preview.place(x=945, y=150)

    t1 = Thread(target=lambda: process_image(operation_type, progress, activity_list, colour, exposure, blur, folder,
                                             body, optics, orientation, ingest_name, taste))

    t2 = Thread(target=lambda: time_left(canvas, time_remaining, images_left))

    t3 = Thread(target=lambda: update_preview(preview))

    t1.start()
    t2.start()
    t3.start()

    window.mainloop()


def update_preview(preview):
    while True:
        try:
            preview_img = ImageTk.PhotoImage(Image.open(asset_relative_path("preview.png")))
            preview.configure(image=preview_img)
            preview.image = preview_img
        except PIL.UnidentifiedImageError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass


def check_filename(current_file, current_image):
    name = ""

    if current_file in file_names:
        try:
            file = open(current_image, 'rb')
            image_name = current_file.split(".")[0]
            extension = current_file.split(".")[-1]

            try:
                tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                name = image_name + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension
            except KeyError:
                current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

                name = image_name + " " + str(current_time) + " duplicate" + "." + extension

            file.close()

        except FileNotFoundError:
            main(f"Operation aborted, {current_image} was not found")

    return name


def process_image(operation_type, progress, activity_list, colour=None, exposure=None, blur=None, folder=None,
                  body=None, optics=None, orientation=None, ingest_name=None, taste=None):
    global total_files
    global image_list
    global file_names
    global average_time
    global aborted

    if len(image_list) == 0:
        if os.path.isfile(asset_relative_path("preview.png")):
            os.remove(asset_relative_path("preview.png"))

    while len(image_list) > 0:
        if operation_type == "Ingesting":
            start_time = time.time()

            current_image = image_list[-1]
            if os.name == "nt":
                current_file = current_image.split("\\")[-1]
            else:
                current_file = current_image.split("/")[-1]

            del image_list[-1]
            del file_names[-1]

            num_files = total_files - len(image_list)

            root = os.path.join(str(config["Program"]["default output"]), ingest_name)

            name = check_filename(current_file, current_image)

            backup_root = ""

            try:
                backup = str(config["Program"]["backup output"])

                if os.path.exists(backup):
                    backup_root = os.path.join(backup, ingest_name)
            except KeyError:
                pass

            if ingest_image(activity_list, body, optics, orientation, current_image, root, name, current_file, backup_root):
                main("Ingest aborted")

            progress["value"] = 100 - len(image_list) / total_files * 100

            average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

            time.sleep(0.5)
            main(f"Ingested {total_files} files")
            if os.name == "nt":
                pass
                # notify.show_toast("Digestible", f"Ingest complete: Ingested {total_files} files")

        elif operation_type == "Digesting":
            root = os.path.join(folder, "Digested Images")

            start_time = time.time()

            current_image = image_list[-1]
            current_file = file_names[-1]
            del image_list[-1]
            del file_names[-1]

            message = f"{current_file}: "

            print(current_image)

            name = check_filename(current_file, current_image)

            image_preview = digest_functions.get_thumbnail(current_image)
            output = root
            reject = False

            if image_preview != "no thumbnail":
                if exposure.get() == 1:
                    exposure_check = digest_functions.check_exposure(image_preview)
                    if exposure_check == "underexposed":
                        output = os.path.join(os.path.join(output, "Rejects"), "Underexposed")
                        reject = True
                        message += f"underexposed and rejected "

                    elif exposure_check == "overexposed":
                        output = os.path.join(os.path.join(output, "Rejects"), "Overexposed")
                        reject = True
                        message += f"overexposed and rejected "

                if blur.get() == 1 and not reject:
                    blurry = digest_functions.check_image_blur(image_preview)
                    if blurry:
                        output = os.path.join(os.path.join(output, "Rejects"), "Blurry")
                        reject = True
                        message += "blurry and rejected"

                if not reject:

                    if taste.get() == 1:
                        classification = digest_functions.get_image_contents(image_preview, detector, predictor)
                        output = os.path.join(output, classification)
                        message += f"{classification} "

                    if colour.get() == 1:
                        colour_dominance = digest_functions.check_colour(image_preview)
                        if colour_dominance != "not colour dominant":
                            output = os.path.join(output, colour_dominance)
                        message += f"({colour_dominance})"

                del image_preview
            else:
                output = os.path.join(output, "No thumbnail available")
                message += "not tested (could not generate a thumbnail)"

            try:
                if not os.path.exists(output):
                    os.makedirs(output)

                shutil.copy2(current_image, os.path.join(output, current_file))
            except PermissionError:
                main("Digest aborted, check your permissions to edit this folder")
            except OSError:
                pass

            if name != "":
                original_output_file_dir = os.path.join(output, current_file)
                final_dir = os.path.join(output, name)
                os.rename(original_output_file_dir, final_dir)

            if len(image_list) > 0:
                progress["value"] = 100 - len(image_list) / total_files * 100
                next_index = activity_list.size() + 1
                activity_list.insert(next_index, message)
                activity_list.yview_scroll(1, "unit")
                average_time = (average_time * (len(image_list) - 1) + time.time() - start_time) / len(image_list)
            else:
                main(f"Digested {total_files} images")
                if os.name == "nt":
                    pass
                    # notify.show_toast("Digestible", f"Digest complete: Digested {total_files} images")

        elif operation_type == "Delegating":
            start_time = time.time()

            current_image = image_list[-1]
            del image_list[-1]

            name = current_image[2]
            editor_folder = current_image[1]
            original_path = current_image[0]

            delegate_failed = delegate_functions.delegate_image(name, editor_folder, original_path)

            num_files = total_files - len(image_list)

            progress["value"] = 100 - len(image_list) / total_files * 100

            average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

            if delegate_failed == "Failed":
                main("Ingest aborted, you may be out of space")
            elif len(image_list) == 0:
                main(f"Delegated {total_files} files to {len(delegating_to)} editors")

            else:
                next_index = activity_list.size() + 1
                activity_list.insert(next_index, f"Delegated to {editor_folder.split('/')[-1]}: {name} ")
                activity_list.yview_scroll(1, "unit")


def main(message=""):
    canvas = clear_screen(window)
    global aborted
    aborted = False

    window.title("Digestible")

    wallpaper = tk.PhotoImage(file=asset_relative_path("main_wp.png"))
    canvas.create_image(250, 0, image=wallpaper, anchor="nw")

    welcome_message = canvas.create_text(1160.0, 42.0, anchor="ne", text="Welcome to Digestible!", fill="#37352F",
                                         font=("Courier", 16 * -1))

    try:
        response = requests.get("https://api.github.com/repos/photogrudesh/digestible/releases/latest", timeout=3)
        if response.json()["name"] != version_number:
            canvas.itemconfig(welcome_message, text=f"{response.json()['name']} is available")
    except requests.ConnectionError:
        pass
    except requests.Timeout:
        pass
    except KeyError:
        pass

    if os.path.exists('./config.dgstbl'):
        config.read('./config.dgstbl')

    if not config.has_section("Program"):
        config.add_section("Program")

    write(config)

    canvas.create_text(290, 670, anchor="sw", justify="left", text=message, fill="#FF0000",
                       font=("Courier", 16 * -1, "bold"), width=350)

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_rectangle(0, 0, 250, 700, fill="#F7FBFB", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Courier", 26 * -1, "bold"))
    main_btn = tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    main_btn.place(x=0.0, y=135.0, width=249.0, height=35.0)
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(),
                           relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    ingest_btn.place(x=0.0, y=170.0, width=249.0, height=35.0)
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(),
                           relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    digest_btn.place(x=0.0, y=205.0, width=249.0, height=35.0)
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7FBFB", padx=0, pady=0)
    delegate_btn.place(x=0.0, y=240, width=249.0, height=35.0)
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(),
                         relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    help_btn.place(x=0.0, y=603.0, width=249.0, height=35.0)
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat", bg="#F7FBFB", anchor="nw", padx=0, pady=0)
    settings_btn.place(x=0.0, y=638.0, width=249.0, height=35.0)

    button_hover_action(main_btn, "home_btn.png", "in_home.png")
    button_hover_action(ingest_btn, "ingest_btn.png", "in_ingest.png")
    button_hover_action(digest_btn, "digest_btn.png", "in_digest.png")
    button_hover_action(delegate_btn, "delegate_btn.png", "in_delegate.png")
    button_hover_action(help_btn, "help_btn.png", "in_help.png")
    button_hover_action(settings_btn, "settings_btn.png", "in_settings.png")

    # Clear window, draw sidebar objects and set window title

    window.mainloop()


if __name__ == '__main__':
    main()
