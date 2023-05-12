import configparser
import datetime
import os
import shutil
import time
import tkinter as tk
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

window = tk.Tk()
window.geometry("1200x700")
window.iconbitmap(asset_relative_path("Digestible Icon.ico"))
window.configure(bg="#FFFFFF")
window.resizable(False, False)
config = configparser.ConfigParser()
version_number = "Digestible v0.3.0"

image_list = []
file_names = []
delegating_to = []
average_time = 0
total_files = 0
saved_editors = []
last_eta = 0
started_calculation = False
aborted = False


def settings():
    canvas = clear_screen(window)

    window.title("Digestible · Settings")

    banner_text = "Settings"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Roboto Mono", 26 * -1))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    canvas.create_text(300, 140, text="Output Preferences", anchor="nw", fill="#37352F", font=("Roboto Mono", 15))

    output_img = tk.PhotoImage(file=asset_relative_path("main_output_btn.png"))
    add_default_output = tk.Button(image=output_img, bg="#FFFFFF", command=lambda: add_dir(default=True), anchor="nw", borderwidth=0, highlightthickness=0, relief="flat")
    add_default_output.place(x=300, y=180)

    backup_img = tk.PhotoImage(file=asset_relative_path("backup_btn.png"))
    add_backup_output = tk.Button(image=backup_img, bg="#FFFFFF", command=lambda: add_dir(default=False), anchor="nw", borderwidth=0, highlightthickness=0, relief="flat")
    add_backup_output.place(x=550, y=180)

    canvas.create_text(300, 230, text="This is where your ingests will go", anchor="nw", fill="#37352F",
                       font=("Roboto Mono", 14 * -1))

    canvas.create_text(300, 300, text="Saved Editors", anchor="nw", fill="#37352F", font=("Roboto Mono", 15))

    if not config.has_option("Program", "saved editors"):
        config["Program"]["saved editors"] = ""
        write(config)

    editors = config["Program"]["saved editors"].split("*")

    try:
        editors.remove("")
    except ValueError:
        pass

    while len(editors) < 6:
        editors.append("Open slot")

    canvas.create_text(300, 330, text=f"{str(editors).replace('[', '').replace(']', '')}", anchor="nw", fill="#37352F",
                       font=("Roboto Mono", 11))

    while "Open slot" in editors:
        editors.remove("Open slot")

    if len(editors) == 0:
        placeholder_text = "Save some editors"
    else:
        placeholder_text = str(editors).replace('[', '').replace(']', '').replace("'", "")

    new_editors_var = tk.StringVar()
    editors_to_add = tk.Entry(window, textvariable=new_editors_var, font=("Roboto Mono", 14), width=45)
    editors_to_add.insert(0, f"{placeholder_text}")
    editors_to_add.tk_setPalette(background="#FFFFFF")
    editors_to_add.focus_set()
    editors_to_add.place(x=300.0, y=370)

    canvas.create_text(300, 410, text=f"Alter your saved editors by adding names separated by commas.", anchor="nw",
                       fill="#37352F", font=("Roboto Mono", 12))

    update_image = tk.PhotoImage(file=asset_relative_path("update_btn.png"))
    update_editors = tk.Button(image=update_image, command=lambda: add_editors(new_editors_var), borderwidth=0, highlightthickness=0, relief="flat", bg="#F7F9F9", anchor="w")
    update_editors.place(x=800.0, y=367)

    window.mainloop()


def add_dir(default):
    selected_folder = tk.filedialog.askdirectory()

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


def add_editors(editor_string):
    new_string = ""
    editors = []

    for i in editor_string.get().split(","):
        name = i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", "")
        if len(editors) < 6 and name not in editors and name != "Save some editors":
            editors.append(i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))

    for name in editors:
        if editors.index(name) == 0:
            new_string = name
        else:
            new_string = new_string + "*" + name

    config["Program"]["saved editors"] = new_string
    write(config)

    settings()


def get_sidebar_assets():
    banner = tk.PhotoImage(file=asset_relative_path("banner_g.png"))

    button_image_home = tk.PhotoImage(file=asset_relative_path("home_btn.png"))

    button_image_ingest = tk.PhotoImage(file=asset_relative_path("ingest_btn.png"))

    button_image_delegate = tk.PhotoImage(file=asset_relative_path("delegate_btn.png"))

    button_image_digest = tk.PhotoImage(file=asset_relative_path("digest_btn.png"))

    button_image_help = tk.PhotoImage(file=asset_relative_path("help_btn.png"))

    button_image_settings = tk.PhotoImage(file=asset_relative_path("settings_btn.png"))

    return banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings


def help_menu():
    canvas = clear_screen(window)

    window.title("Digestible · Help")
    banner_text = "Help"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Roboto Mono", 26 * -1))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    canvas.create_text(725, 140, anchor="n",
                       text="\nWelcome! Digestible has three modes: Ingest, Digest, and Delegate. Each mode is designed to streamline your photography workflow, so you can spend less time sorting through images and more time doing what you love.\n\nWhen you get home after a shoot, Ingest mode makes it easy to process the files from your camera (cards under 100 GB). Digestible automatically sorts images by camera body, lens used, and orientation of the image so you don't have to.\n\nAfter you've ingested your images, it's time to start culling! Digest mode automatically separates images based on how usable they are by analysing exposure and blurriness, so you can quickly identify the images that are worth keeping.\n\nOnce you've sorted your images, it's time to delegate them to your team for post-production. Delegate mode automatically splits the sorted images between editors evenly so editing can become as soon as possible.",
                       width=800, font=("Roboto Mono", 12), fill="#37352F")

    window.mainloop()


def time_left(canvas, time_remaining, images_left):
    num_files = total_files - len(image_list)
    items_left = total_files - num_files

    eta = average_time * items_left

    if num_files/total_files < 0.1:
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
        eta = "About " + str(round(eta, 2)) + " seconds(s) remaining"

    canvas.itemconfig(images_left, text=f"{str(len(image_list))} files left from {str(total_files)}")

    canvas.itemconfig(time_remaining, text=eta)
    window.after(500, lambda: time_left(canvas, time_remaining, images_left))


def disable_ingest_button(canvas, ingest_name_var, button_1, message):
    illegal_characters = ["\\", '/', '*', '?', '"', '<', '>', '|', ":"]
    illegal_name = False
    ingest_name = ingest_name_var.get()

    root = ""

    try:
        root = os.path.join(str(config["Program"]["default output"]), str(ingest_name))
    except KeyError:
        main("Add a default output path in settings before ingesting")

    for i in illegal_characters:
        if i in ingest_name_var.get():
            illegal_name = True

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
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Roboto Mono", 26 * -1))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    image_list = []
    file_names = []
    drive_files = []

    sort_orientation, sort_body, sort_optics = tk.IntVar(), tk.IntVar(), tk.IntVar()

    inputs = collect_inputs()

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

    for i in image_list:
        if os.name == "nt":
            file_names.append(i.split("\\")[-1])
        else:
            file_names.append(i.split("/")[-1])

    total_files = len(image_list)
    drives = len(inputs)

    while len(inputs) < 3:
        inputs.append("No card detected")
        drive_files.append("0 files")

    if len(image_list) == 0:
        main("No files to ingest")

    canvas.create_text(300.0, 650.0, anchor="nw", text="Sort By:", fill="#37352F", font=("Roboto Mono", 15 * -1))

    body = tk.Checkbutton(window, text="Body Type", variable=sort_body)
    body.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    body.place(x=380, y=650.0)

    optics = tk.Checkbutton(window, text="Optics", variable=sort_optics)
    optics.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    optics.place(x=473.0, y=650.0)

    orient = tk.Checkbutton(window, text="Orientation", variable=sort_orientation)
    orient.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    orient.place(x=541.0, y=650.0)

    current_time = datetime.datetime.now()
    default_name = current_time.strftime("%d-%m-%Y-%H-%M-%S")

    canvas.create_text(655, 653, text="Ingest Name:", anchor="nw", font=("Roboto Mono", 14 * -1), fill="#37352F")

    ingest_name_var = tk.StringVar()
    ingest_name = tk.Entry(window, textvariable=ingest_name_var, font=("Roboto Mono", 10), width=30)
    ingest_name.insert(0, f"{default_name}")
    ingest_name.tk_setPalette(background="#FFFFFF")
    ingest_name.focus_set()
    ingest_name.place(x=760.0, y=651)

    button_image_1 = tk.PhotoImage(file=asset_relative_path("begin_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: operation_in_progress("Ingesting", drives=drives, body=sort_body, optics=sort_optics, orientation=sort_orientation,
                                                            ingest_name=ingest_name_var.get().strip()), relief="flat")
    button_1.place(x=1020.0, y=642.0, width=160.0, height=35.0)

    message = canvas.create_text(725.0, 580.0, anchor="n", text="Name the ingest below to start", fill="#37352F",
                                 font=("Roboto Mono", 15 * -1), width=850, justify="center")

    disable_ingest_button(canvas, ingest_name_var, button_1, message)

    extra_drives = len(inputs) - 3
    if extra_drives > 0:
        canvas.create_text(725.0, 250.0, anchor="n",
                           text=f"{extra_drive_files} files to ingest from {extra_drives} other drive(s)",
                           fill="#37352F", font=("Roboto Mono", 18 * -1), justify="center")

    if len(image_list) > 1000:
        canvas.create_text(725.0, 307.0, anchor="n", text=f"This may take a while, {len(image_list)} images to ingest",
                           fill="#FF0000", font=("Roboto Mono", 18 * -1), justify="center")
    else:
        canvas.create_text(725.0, 245.0, anchor="n",
                           text=f"(Ignoring drives over 100 GB in size)\n{len(image_list)} images to ingest",
                           fill="#37352F", font=("Roboto Mono", 18 * -1), justify="center")

    canvas.create_text(500.0, 150.0, anchor="n", text=inputs[0], fill="#37352F", font=("Roboto Mono", 16 * -1))
    canvas.create_text(725.0, 150.0, anchor="n", text=inputs[1], fill="#37352F", font=("Roboto Mono", 16 * -1))
    canvas.create_text(950.0, 150.0, anchor="n", text=inputs[2], fill="#37352F", font=("Roboto Mono", 16 * -1))
    canvas.create_text(500.0, 184.0, anchor="n", text=drive_files[0], fill="#37352F", font=("Roboto Mono", 15 * -1))
    canvas.create_text(725.0, 184.0, anchor="n", text=drive_files[1], fill="#37352F", font=("Roboto Mono", 15 * -1))
    canvas.create_text(950.0, 184.0, anchor="n", text=drive_files[2], fill="#37352F", font=("Roboto Mono", 15 * -1))

    window.mainloop()


def digest(selected_folder=""):
    global total_files
    global image_list
    global file_names

    if selected_folder == "":
        selected_folder = tk.filedialog.askdirectory()
        if selected_folder != "":
            digest(selected_folder)
        else:
            main("Digest aborted, no folder selected")

    image_list = []
    file_names = []

    if "Digested Images" in os.listdir(selected_folder):
        main('Folder has already been digested, delete the "Digested Images" folder to try again')

    for root, dirs, files in os.walk(selected_folder):

        for f in files:
            if is_media(f) == "image":
                image_list.append(os.path.join(root, f))
                file_names.append(f)
    total_files = len(image_list)

    if len(image_list) == 0:
        main("No files to delegate")

    canvas = clear_screen(window)

    banner_text = "Digest"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Roboto Mono", 26 * -1))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    if len(image_list) > 500:
        canvas.create_text(725.0, 108.0, anchor="n", text=f"{str(total_files)} files to digest. This may take a while",
                           fill="#37352F", font=("Roboto Mono", 16 * -1))
    else:
        canvas.create_text(400.0, 108.0, anchor="n", text=f"{str(total_files)} files to digest.", fill="#FFFFFF",
                           font=("Roboto Mono", 16 * -1))

    canvas.create_text(725, 180, anchor="n",
                       text="\nWelcome to Digest. This should be the second part of your improved post-production workflow, After ingesting, you might want to cull through the images you've just taken, but why bother doing that yourself. The digest mode has 3 options, Colour dominance, Exposure and Blur. While digestible may not be perfect at culling your images, it should still save your time by moving unusable images to a Rejects folder. \n\nExposure is the simplest and most common reasons for an unusable image, Digestible will identify and remove any underexposed or overexposed images from your ingest folder.\n\nThe blur option will identify unusable images based on motion blur. Use with caution if images are intentionally blurry (e.g. panning action shots).\n\nFinally the colour dominance option will split images based on the colour that is most dominant in the frame.\n\nHappy Digesting!",
                       width=800, font=("Roboto Mono", 12), fill="#37352F")

    canvas.create_text(300.0, 645.0, anchor="nw", text="Options:", fill="#37352F", font=("Roboto Mono", 16 * -1))

    colour, exposure, blur = tk.IntVar(), tk.IntVar(), tk.IntVar()

    e1 = tk.Checkbutton(window, text="Colour dominance", variable=colour)
    e1.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e1.place(x=400.0, y=644.0)

    e3 = tk.Checkbutton(window, text="Blur detection", variable=blur)
    e3.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e3.place(x=535.0, y=644.0)

    e2 = tk.Checkbutton(window, text="Exposure", variable=exposure)
    e2.tk_setPalette(background="#ffffff", foreground="#37352F", selectcolor="#FFFFFF")
    e2.place(x=647.0, y=644.0)

    canvas.create_text(725.0, 140.0, anchor="n", text=f"Digesting from: {selected_folder.split('/')[-1]}", fill="#37352F",
                       font=("Roboto Mono", 18 * -1))

    button_image_1 = tk.PhotoImage(file=asset_relative_path("begin_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: operation_in_progress("Digesting", colour=colour, exposure=exposure, blur=blur, folder=selected_folder), relief="flat")
    button_1.place(x=1020.0, y=642.0, width=160.0, height=35.0)

    window.mainloop()


def delegate(selected_folder=""):
    global total_files
    global image_list
    global file_names

    window.title("Digestible · Delegate")

    if selected_folder == "":
        selected_folder = tk.filedialog.askdirectory()
        if selected_folder != "":
            delegate(selected_folder)
        else:
            main("Delegation aborted, no folder selected")

    image_list = []
    file_names = []
    files_to_delegate = 0
    digested_found = False

    if "Digested Images" in os.listdir(selected_folder):
        digested_found = True
        selected_folder = os.path.join(selected_folder, "Digested Images")

    if "Delegated Images" in os.listdir(selected_folder):
        main('Folder has already been delegated, delete the "Delegated Images" folder to try again')

    for root, dirs, files in os.walk(selected_folder):
        if "Rejects" not in root.split("/"):
            for f in files:
                if is_media(f) == "image" and not f.startswith("."):
                    image_list.append(os.path.join(root, f))
                    file_names.append(f)
                    files_to_delegate += 1
    total_files = len(image_list)

    if len(image_list) == 0:
        main("No files to delegate")

    canvas = clear_screen(window)

    banner_text = "Delegate"

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=banner_text, fill="#F5F5F5", font=("Roboto Mono", 26 * -1))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    if digested_found:
        canvas.create_text(300.0, 650.0, anchor="nw", text=f"Delegating from: {selected_folder.split('/')[-1]} (Digested folder found)",
                           fill="#37352F",
                           font=("Roboto Mono", 14 * -1))
    else:
        canvas.create_text(300.0, 650.0, anchor="nw", text=f"Delegating from: {selected_folder.split('/')[-1]}", fill="#37352F",
                       font=("Roboto Mono", 14 * -1))

    canvas.create_text(725.0, 465.0, anchor="n", text="Enter the names (under 20 characters long) of up to 20 additional editors separated by commas.", fill="#37352F", font=("Roboto Mono", 14 * -1))

    images_per_person_message = canvas.create_text(725.0, 116.0, anchor="n",
                                                   text=f"Total Images: {total_files}  |  Images per person: ",
                                                   fill="#37352F", font=("Roboto Mono", 14 * -1))

    try:
        editors = config["Program"]["saved editors"].split("*")
        if "" in editors:
            editors.remove("")
    except KeyError:
        editors = []

    while len(editors) < 6:
        editors.append("Save an editor to this list from settings")

    d2e1, d2e2, d2e3, d2e4, d2e5, d2e6 = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()

    e1 = tk.Checkbutton(window, text=editors[0], variable=d2e1)
    e1.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    e1.place(x=500.0, y=570.0, anchor="n")

    e2 = tk.Checkbutton(window, text=editors[1], variable=d2e2)
    e2.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    e2.place(x=725.0, y=570.0, anchor="n")

    e3 = tk.Checkbutton(window, text=editors[2], variable=d2e3)
    e3.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    e3.place(x=950.0, y=570.0, anchor="n")

    e4 = tk.Checkbutton(window, text=editors[3], variable=d2e4)
    e4.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    e4.place(x=500.0, y=600.0, anchor="n")

    e5 = tk.Checkbutton(window, text=editors[4], variable=d2e5)
    e5.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    e5.place(x=725.0, y=600.0, anchor="n")

    e6 = tk.Checkbutton(window, text=editors[5], variable=d2e6)
    e6.tk_setPalette(background="#FFFFFF", foreground="white", selectcolor="#FFFFFF")
    e6.place(x=950.0, y=600.0, anchor="n")

    editor_names_var = tk.StringVar()
    editor_names = tk.Entry(window, textvariable=editor_names_var, font=("Roboto Mono", 10), width=80)
    editor_names.insert(0, f"Type names here")
    editor_names.tk_setPalette(background="#FFFFFF")
    editor_names.focus_set()
    editor_names.place(x=725.0, y=520, anchor="n")

    delegating_to_message = canvas.create_text(725, 340, text=f"Delegating to nobody", anchor="n", width=850,
                                               fill="#37352F", font=("Roboto Mono", 15 * -1), justify="center")

    button_image_1 = tk.PhotoImage(file=asset_relative_path("begin_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: operation_in_progress("Delegating", folder=selected_folder), relief="flat")
    button_1.place(x=1040.0, y=640.0, width=125.0, height=35.0)

    canvas.after(20, lambda: check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6,
                                                    editors, editor_names_var, images_per_person_message, button_1))

    window.mainloop()


def check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, editors, entered_editors, images_per_person_message, start_button):
    global delegating_to
    delegating_to = []

    if d2e1.get() == 1 and editors[0] != "Save an editor to this list from settings":
        delegating_to.append(editors[0].lower())
    if d2e2.get() == 1 and editors[1] != "Save an editor to this list from settings":
        delegating_to.append(editors[1].lower())
    if d2e3.get() == 1 and editors[2] != "Save an editor to this list from settings":
        delegating_to.append(editors[2].lower())
    if d2e4.get() == 1 and editors[3] != "Save an editor to this list from settings":
        delegating_to.append(editors[3].lower())
    if d2e5.get() == 1 and editors[4] != "Save an editor to this list from settings":
        delegating_to.append(editors[4].lower())
    if d2e6.get() == 1 and editors[5] != "Save an editor to this list from settings":
        delegating_to.append(editors[5].lower())

    additional_editors = entered_editors.get().split(",")
    for i in additional_editors:
        name_to_add = i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<",
                                                                                                             "").replace(
            ">", "").replace("|", "")
        if name_to_add != "Type names here" and name_to_add != "" and len(
                i) < 20 and name_to_add.lower() not in delegating_to and len(delegating_to) < 26:
            delegating_to.append(name_to_add.lower())

    if len(delegating_to) == 0:
        message = "Delegating to nobody"
    else:
        message = f"Delegating to: {str(delegating_to).replace('[', '').replace(']', '')}"

    canvas.itemconfig(delegating_to_message, text=message)

    if len(delegating_to) == 0:
        canvas.itemconfig(images_per_person_message, text=f"Select some editors to begin delegating.")
        start_button["state"] = "disabled"
    elif len(delegating_to) == 1:
        canvas.itemconfig(images_per_person_message, text=f"Delegate to more than 1 person to begin delegating")
        start_button["state"] = "disabled"
    else:
        canvas.itemconfig(images_per_person_message,
                          text=f"Total Images: {total_files}  |  About {round(total_files / len(delegating_to))} images per person")
        start_button["state"] = "normal"

    canvas.after(50, lambda: check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6,
                                                    editors, entered_editors, images_per_person_message, start_button))


def operation_in_progress(operation_type, colour=None, exposure=None, blur=None, folder=None, drives=None, body=None, optics=None, orientation=None, ingest_name=None):
    global image_list
    global total_files
    global average_time
    global started_calculation
    global delegating_to
    started_calculation = False
    average_time = 0

    window.title(f"Digestible · {operation_type}")

    canvas = clear_screen(window)

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_image(250, 0, image=banner, anchor="nw")
    canvas.create_text(300.0, 34.0, anchor="nw", text=operation_type, fill="#F5F5F5", font=("Roboto Mono", 26 * -1))
    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw", state="disabled").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw", state="disabled").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9", state="disabled").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9", state="disabled").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9", state="disabled").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw", state="disabled").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw", state="disabled").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    if operation_type == "Delegating":
        output = os.path.join(folder, "Delegated Images")

        delegating_to_editor = 0

        for image in image_list:
            index = image_list.index(image)

            if delegating_to_editor == len(delegating_to) - 1:
                delegating_to_editor = 0
            else:
                delegating_to_editor += 1

            if os.name == "nt":
                current_file = image.split("\\")[-1]
            else:
                current_file = image.split("/")[-1]

            file_names.remove(current_file)

            file_name = current_file

            if current_file in file_names:
                file = open(image, 'rb')
                image_name = current_file.split(".")[0]
                extension = current_file.split(".")[-1]
                tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                file_name = image_name + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension

            editor_output = os.path.join(output, delegating_to[delegating_to_editor])

            image_list[index] = [image, editor_output, file_name]

        image_list.sort(key=lambda item: item[1])

    button_image_1 = tk.PhotoImage(file=asset_relative_path("abort_btn.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: main(f"{operation_type} Aborted"),
                         relief="flat")
    button_1.place(x=1020.0, y=638.0, width=160.0, height=35.0)

    if drives is None:
        canvas.create_text(725.0, 115.0, anchor="n",
                           text=f"{operation_type} {str(total_files)} files", fill="#37352F",
                           font=("Roboto Mono", 16 * -1))
    elif drives == 1:
        canvas.create_text(725.0, 115.0, anchor="n",
                           text=f"{operation_type} {str(total_files)} files from {str(drives)} drive", fill="#37352F",
                           font=("Roboto Mono", 16 * -1))
    else:
        canvas.create_text(725.0, 115.0, anchor="n",
                           text=f"{operation_type} {str(total_files)} files from {str(drives)} drives", fill="#37352F",
                           font=("Roboto Mono", 16 * -1))

    images_left = canvas.create_text(650.0, 618.0, anchor="n", text="", fill="#37352F", font=("Roboto Mono", 12 * -1))

    progress = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=700)
    progress.place(x=300, y=645)

    time_remaining = canvas.create_text(650.0, 674.0, anchor="n", text="", fill="#37352F", font=("Roboto Mono", 12 * -1))
    activity_list = tk.Listbox(font=("Roboto Mono", 16 * -1))
    activity_list.place(x=300.0, y=150.0, width=850.0, height=460.0)

    window.after(1, lambda: process_image(canvas, operation_type, progress, activity_list, colour, exposure, blur, folder, body, optics, orientation, ingest_name))
    window.after(10, lambda: time_left(canvas, time_remaining, images_left))

    window.mainloop()


def process_image(canvas, operation_type, progress, activity_list, colour=None, exposure=None, blur=None, folder=None, body=None, optics=None, orientation=None, ingest_name=None):
    global total_files
    global image_list
    global file_names
    global average_time
    global aborted

    match operation_type:
        case "Ingesting":
            start_time = time.time()

            current_image = image_list[-1]
            if os.name == "nt":
                current_file = current_image.split("\\")[-1]
            else:
                current_file = current_image.split("/")[-1]

            del image_list[-1]
            del file_names[-1]

            num_files = total_files - len(image_list)

            name = ""
            ingest_failed = False

            root = os.path.join(str(config["Program"]["default output"]), ingest_name)

            try:
                backup_root = os.path.join(str(config["Program"]["backup output"]), ingest_name)
            except KeyError:
                backup_root = ""
                pass

            if current_file in file_names:
                try:
                    file = open(current_image, 'rb')
                    image_name = current_file.split(".")[0]
                    extension = current_file.split(".")[-1]
                    tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                    name = image_name + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension
                except FileNotFoundError:
                    ingest_failed = True

            ingest_image(activity_list, body, optics, orientation, current_image, root, name, current_file, backup_root)

            progress["value"] = 100 - len(image_list) / total_files * 100

            average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

            if ingest_failed:
                main("Ingest aborted")
            elif len(image_list) > 0:
                window.after(1, lambda: process_image(canvas, operation_type, progress, activity_list, colour, exposure, blur, folder, body, optics, orientation, ingest_name))
            else:
                time.sleep(0.5)
                main(f"Ingested {total_files} files")

        case "Digesting":
            root = os.path.join(folder, "Digested Images")

            start_time = time.time()
            digest_failed = False

            current_image = image_list[-1]
            file_name = file_names[-1]
            del image_list[-1]
            del file_names[-1]

            name = ""
            colour_dominance = "Not tested"
            exposure_check = "Exposed correctly"
            blurry = False

            if file_name in file_names:
                try:
                    file = open(current_image, 'rb')
                    image_name = file_name.split(".")[0]
                    extension = file_name.split(".")[-1]
                    tags = exifread.process_file(file, stop_tag='LensModel', details=False)
                    name = image_name + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension
                    file.close()
                except FileNotFoundError:
                    aborted = True

            image_preview = digest_functions.get_thumbnail(current_image)
            output = root
            reject = False

            if image_preview != "no thumbnail":
                if exposure.get() == 1:
                    exposure_check = digest_functions.check_exposure(image_preview)
                    if exposure_check == "Underexposed":
                        output = os.path.join(os.path.join(output, "Rejects"), "Underexposed")
                        reject = True
                    elif exposure_check == "Overexposed":
                        output = os.path.join(os.path.join(output, "Rejects"), "Overexposed")
                        reject = True

                if blur.get() == 1:
                    if digest_functions.blur_detect(image_preview):
                        output = os.path.join(os.path.join(output, "Rejects"), "Blurry")
                        reject = True

                if colour.get() == 1 and not reject:
                    colour_dominance = digest_functions.check_colour(image_preview)
                    if colour_dominance != "Not colour dominant":
                        output = os.path.join(output, colour_dominance)
            else:
                output = os.path.join(output, "No thumbnail available")

            try:
                if not os.path.exists(output):
                    os.makedirs(output)

                shutil.copy2(current_image, os.path.join(output, file_name))
            except OSError:
                digest_failed = False

            if name != "":
                original_output_file_dir = os.path.join(output, file_name)
                final_dir = os.path.join(output, name)
                os.rename(original_output_file_dir, final_dir)

            if aborted:
                main("Aborted Digest")
            elif digest_failed:
                main("Ingest aborted, you may be out of space")
            elif len(image_list) > 0:
                progress["value"] = 100 - len(image_list) / total_files * 100
                next_index = activity_list.size() + 1
                activity_list.insert(next_index, f"{file_name}: {colour_dominance}, {exposure_check}, blur: {blurry}")
                activity_list.yview_scroll(1, "unit")
                average_time = (average_time * (len(image_list) - 1) + time.time() - start_time) / len(image_list)
                window.after(1, lambda: process_image(canvas, operation_type, progress, activity_list, colour, exposure, blur, folder, body, optics, orientation, ingest_name))
            else:
                main(f"Digested {total_files} images")
        case "Delegating":
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
                canvas.after(5, lambda: process_image(canvas, operation_type, progress, activity_list, colour, exposure, blur, folder, body, optics, orientation, ingest_name))
    pass


def main(message=""):
    canvas = clear_screen(window)
    global aborted
    aborted = False

    window.title("Digestible")

    wallpaper = tk.PhotoImage(file=asset_relative_path("main_wp.png"))
    canvas.create_image(250, 0, image=wallpaper, anchor="nw")

    welcome_message = canvas.create_text(1160.0, 45.0, anchor="ne", text="Welcome to Digestible 👋", fill="#37352F", font=("Roboto Mono", 14 * -1))

    try:
        response = requests.get("https://api.github.com/repos/photogrudesh/digestible/releases/latest", timeout=3)
        if response.json()["name"] != version_number:
            canvas.itemconfig(welcome_message, text=f"{response.json()['name']} is available 🌐")
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

    if message:
        window.after(5000, lambda: canvas.itemconfig(change_message, text=""))

    change_message = canvas.create_text(290, 670, anchor="sw", justify="left", text=message, fill="#37352F",
                                        font=("Roboto Mono", 15 * -1), width=350)

    banner, button_image_home, button_image_ingest, button_image_delegate, button_image_digest, button_image_help, button_image_settings = get_sidebar_assets()

    canvas.create_rectangle(0, 0, 250, 700, fill="#F5F5F5", outline="")
    canvas.create_text(32.0, 34.0, anchor="nw", text="Digestible", fill="#37352F", font=("Roboto Mono", 26 * -1))
    tk.Button(image=button_image_home, borderwidth=0, highlightthickness=0, command=lambda: main(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=135.0, width=249.0, height=35.0)
    tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=lambda: ingest(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=170.0, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=lambda: delegate(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=240, width=249.0, height=35.0)
    tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=lambda: digest(), relief="flat", anchor="nw", bg="#F7F9F9").place(x=0.0, y=205.0, width=249.0, height=35.0)
    tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=lambda: help_menu(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=603.0, width=249.0, height=35.0)
    tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=lambda: settings(), relief="flat", bg="#F7F9F9", anchor="nw").place(x=0.0, y=638.0, width=249.0, height=35.0)
    # SIDEBAR

    window.mainloop()


if __name__ == '__main__':
    main()
