import configparser
import datetime
import os
import shutil
import time
import tkinter as tk
from environment import Environment

import exifread
import psutil
from tkinter import ttk
from tkinter import filedialog

window = tk.Tk()
window.geometry("800x480")
window.configure(bg="#1F2124")
window.resizable(False, False)
config = configparser.ConfigParser()

environment = Environment()

image_list = []
file_names = []
delegating_to = []
average_time = 0
total_files = 0
saved_editors = []


def asset_relative_path(path):
    root_path = os.path.join(environment.get_main_path(), "assets")
    full_path = os.path.join(root_path, path)
    return full_path


def clear_screen():
    for widget in window.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)

    return canvas


def is_media(file):
    media = False
    ext = file.split(".")[-1]
    raw_extensions = ["cr2", "rw2", "raf", "erf", "nrw", "nef", "arw", "rwz", "eip", "bay", "dng", "dcr", "gpr", "raw",
                      "crw", "3fr", "sr2", "k25", "kc2", "mef", "dng", "cs1", "orf", "mos", "ari", "kdc", "cr3", "fff",
                      "srf", "srw", "j6i", "mrw", "mfw", "x3f", "rwl", "pef", "iiq", "cxi", "nksc", "mdc"]

    if ext.lower() in raw_extensions:
        media = True

    return media


def settings():
    canvas = clear_screen()

    window.title("Digestible · Options")

    canvas.create_text(42.0, 37.0, anchor="nw", text="Options", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(217.0, 58.0, 551.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(43, 110, text="Output Preferences", anchor="nw", fill="#FFFFFF", font=("Roboto Mono", 18))

    add_default_output = tk.Button(text="Add an output directory", fg="#000000", command=lambda: add_dir(default=True))
    add_default_output.place(x=41, y=150)

    add_backup_output = tk.Button(text="Add a backup directory", fg="#000000", command=lambda: add_dir(default=False))
    add_backup_output.place(x=220, y=150)

    canvas.create_text(42, 200, text="This is where your ingests will go", anchor="nw", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(43, 270, text="Saved Editors", anchor="nw", fill="#FFFFFF", font=("Roboto Mono", 18))

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

    canvas.create_text(42, 300, text=f"{str(editors).replace('[', '').replace(']', '')}", anchor="nw", fill="#FFFFFF", font=("Roboto Mono", 14))

    canvas.create_text(42, 350, text=f"Edit this list:", anchor="nw", fill="#FFFFFF", font=("Roboto Mono", 14))

    while "Open slot" in editors:
        editors.remove("Open slot")

    if len(editors) == 0:
        placeholder_text = "Save some editors"
    else:
        placeholder_text = str(editors).replace('[', '').replace(']', '').replace("'", "")

    new_editors_var = tk.StringVar()
    editors_to_add = tk.Entry(window, textvariable=new_editors_var, font=("Roboto Mono", 10), width=80)
    editors_to_add.insert(0, f"{placeholder_text}")
    editors_to_add.tk_setPalette(background="#1F2124")
    editors_to_add.focus_set()
    editors_to_add.place(x=165.0, y=348)

    canvas.create_text(42, 380, text=f"Alter your saved editors by adding names separated by commas.", anchor="nw", fill="#FFFFFF", font=("Roboto Mono", 14))

    button_image_2 = tk.PhotoImage(file=asset_relative_path("cancel.png"))
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the help menu"), relief="flat")
    button_2.place(x=695.0, y=421.0, width=64.0, height=25.0)

    update_editors = tk.Button(text="Update", command=lambda: add_editors(new_editors_var), fg="#000000")
    update_editors.place(x=665.0, y=344)

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
        if len(editors) < 6 and i.strip() not in editors:
            editors.append(i.strip())

    for name in editors:
        if editors.index(name) == 0:
            new_string = name
        else:
            new_string = new_string + "*" + name

    config["Program"]["saved editors"] = new_string
    write(config)

    main("Updated saved editors")


def inventory():
    canvas = clear_screen()
    main("Inventory is WIP")

    window.title("Digestible · Inventory")

    cancel_image = tk.PhotoImage(file=asset_relative_path("cancel.png"))
    cancel_button = tk.Button(image=cancel_image, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the !inventory"), relief="flat")
    cancel_button.place(x=695.0, y=421.0, width=64.0, height=25.0)

    window.mainloop()


def help_menu():
    canvas = clear_screen()

    window.title("Digestible · Help")

    canvas.create_text(42.0, 37.0, anchor="nw", text="Help", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(157.0, 58.0, 501.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41, 100, anchor="nw", text="\nWelcome! Digestible has three modes: Ingest, Digest, and Delegate. Each mode is designed to streamline your photography workflow, so you can spend less time sorting through images and more time doing what you love.\n\nWhen you get home after a shoot, Ingest mode makes it easy to process the files from your camera (cards under 100 GB). Digestible automatically sorts images by camera body, lens used, and orientation of the image so you don't have to.\n\nAfter you've ingested your images, it's time to start culling! Digest mode automatically separates images based on how usable they are by analysing exposure and blurriness, so you can quickly identify the images that are worth keeping.\n\nOnce you've sorted your images, it's time to delegate them to your team for post-production. Delegate mode automatically splits the sorted images between editors evenly so editing can become as soon as possible.", width=720, font=("Roboto Mono", 14), fill="#FFFFFF")

    cancel_image = tk.PhotoImage(file=asset_relative_path("cancel.png"))
    cancel_button = tk.Button(image=cancel_image, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the help menu"), relief="flat")
    cancel_button.place(x=695.0, y=421.0, width=64.0, height=25.0)

    window.mainloop()


def time_left(canvas, time_remaining, images_left):
    num_files = total_files - len(image_list)
    items_left = total_files - num_files

    eta = average_time * items_left

    if round(eta) < 2:
        eta = "Almost done"
    elif eta > 60:
        eta = str(round(eta / 60)) + " minute(s) remaining"
    elif eta > 3600:
        eta = str(round(eta / 60 / 60)) + " hours(s) remaining, this may take a while"
    elif eta > 86400:
        eta = str(round(eta / 60 / 60 / 24)) + " day(s) remaining, this may take a while"
    else:
        eta = str(round(eta)) + " seconds(s) remaining"

    canvas.itemconfig(images_left, text=f"{str(len(image_list))} files left from {str(total_files)}")

    canvas.itemconfig(time_remaining, text=eta)
    window.after(500, lambda: time_left(canvas, time_remaining, images_left))


def write(config_file):
    with open('./config.dgstbl', 'w') as configfile:
        config_file.write(configfile)


def main(message=""):
    canvas = clear_screen()

    window.title("Digestible")

    if os.path.exists('./config.dgstbl'):
        config.read('./config.dgstbl')

    if not config.has_section("Program"):
        config.add_section("Program")

    write(config)

    if message:
        window.after(5000, lambda: canvas.itemconfig(change_message, text=""))

    canvas.create_text(90.0, 37.0, anchor="nw", text="Digestible", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    change_message = canvas.create_text(400, 150, anchor="n", text=message, fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    logo = tk.PhotoImage(file=asset_relative_path("icon.png"))
    canvas.create_image(60.0, 59.0, image=logo)

    button_image_help = tk.PhotoImage(file=asset_relative_path("main_help.png"))
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0,
                         command=lambda: help_menu(), relief="flat")
    help_btn.place(x=42.0, y=421.0, width=51.0, height=25.0)

    button_image_settings = tk.PhotoImage(file=asset_relative_path("main_settings.png"))
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat")
    settings_btn.place(x=678.0, y=421.0, width=81.0, height=24.0)

    canvas.create_text(747.0, 52.0, anchor="ne", text="Welcome back 👋", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    button_image_inventory = tk.PhotoImage(file=asset_relative_path("main_inv.png"))
    inventory_btn = tk.Button(image=button_image_inventory, borderwidth=0, highlightthickness=0,
                              command=lambda: inventory(), relief="flat")
    inventory_btn.place(x=354.0, y=419.0, width=92.0, height=28.0)

    button_image_ingest = tk.PhotoImage(file=asset_relative_path("main_ingest.png"))
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0,
                           command=lambda: ingest(), relief="flat")
    ingest_btn.place(x=101.0, y=219.0, width=124.0, height=42.0)

    button_image_delegate = tk.PhotoImage(file=asset_relative_path("main_delegate.png"))
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat")
    delegate_btn.place(x=568.0, y=219.0, width=138.0, height=42.0)

    button_image_digest = tk.PhotoImage(file=asset_relative_path("main_digest.png"))
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0,
                           command=lambda: digest(), relief="flat")
    digest_btn.place(x=338.0, y=219.0, width=124.0, height=42.0)

    canvas.create_rectangle(42.0, 237.0, 96.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(229.0, 237.0, 328.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(467.0, 237.0, 551.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(716.0, 237.0, 754.0, 240.0, fill="#2C2E2F", outline="")

    window.mainloop()


def collect_inputs():
    inputs = []

    for i in psutil.disk_partitions():
        add_volume = True
        try:
            if psutil.disk_usage(i.mountpoint).total > 100000000000:
                add_volume = False
            if os.name == "posix" and i.mountpoint.startswith("/System"):
                add_volume = False

            if add_volume:
                inputs.append(i.mountpoint)
        except PermissionError:
            pass

    return inputs


def ingest():
    global image_list
    global total_files
    global average_time
    global file_names

    window.title("Digestible · Ingest")

    canvas = clear_screen()

    canvas.create_text(400.0, 37.0, anchor="n", text="Ingest\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

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
                if is_media(f):
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

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 395.0, anchor="nw", text="Sort By:", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    body = tk.Checkbutton(window, text="Body Type", variable=sort_body)
    body.tk_setPalette(background="#1F2124", foreground="white", selectcolor="black")
    body.place(x=40, y=425.0)

    optics = tk.Checkbutton(window, text="Optics", variable=sort_optics)
    optics.tk_setPalette(background="#1F2124", foreground="white", selectcolor="black")
    optics.place(x=133.0, y=425.0)

    orient = tk.Checkbutton(window, text="Orientation", variable=sort_orientation)
    orient.tk_setPalette(background="#1F2124", foreground="white", selectcolor="black")
    orient.place(x=201.0, y=425.0)

    current_time = datetime.datetime.now()
    default_name = current_time.strftime("%d-%m-%Y-%H-%M-%S")

    canvas.create_text(315, 428, text="Ingest Name:", anchor="nw", font=("Roboto Mono", 14 * -1), fill="#FFFFFF")

    ingest_name_var = tk.StringVar()
    ingest_name = tk.Entry(window, textvariable=ingest_name_var, font=("Roboto Mono", 10), width=20)
    ingest_name.insert(0, f"{default_name}")
    ingest_name.tk_setPalette(background="#1F2124")
    ingest_name.focus_set()
    ingest_name.place(x=410.0, y=426)

    button_image_1 = tk.PhotoImage(file=asset_relative_path("ingest_start.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: ingest_in_progress(drives, sort_body, sort_optics, sort_orientation, ingest_name_var.get().strip()), relief="flat")
    button_1.place(x=692.0, y=417.0, width=72.0, height=36.0)

    message = canvas.create_text(400.0, 345.0, anchor="n", text="Name the ingest below to start", fill="#FFFFFF", font=("Roboto Mono", 14 * -1), width=750)

    disable_ingest_button(canvas, ingest_name_var, button_1, message)

    button_image_2 = tk.PhotoImage(file=asset_relative_path("cancel.png"))
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Cancelled Ingest"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    extra_drives = len(inputs) - 3
    if extra_drives > 0:
        canvas.create_text(400.0, 250.0, anchor="n", text=f"{extra_drive_files} files to ingest from {extra_drives} other drive(s)", fill="#FFFFFF", font=("Roboto Mono", 16 * -1), justify="center")

    if len(image_list) > 1000:
        canvas.create_text(400.0, 307.0, anchor="n", text=f"This may take a while, {len(image_list)} images to ingest", fill="#FF0000", font=("Roboto Mono", 16 * -1), justify="center")
    else:
        canvas.create_text(400.0, 297.0, anchor="n", text=f"{len(image_list)} images to ingest\n(Ignoring drives over 100 GB in size)", fill="#FFFFFF", font=("Roboto Mono", 16 * -1), justify="center")

    canvas.create_text(150.0, 150.0, anchor="n", text=inputs[0], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(400.0, 150.0, anchor="n", text=inputs[1], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(650.0, 150.0, anchor="n", text=inputs[2], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(150.0, 184.0, anchor="n", text=drive_files[0], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(400.0, 184.0, anchor="n", text=drive_files[1], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(650.0, 184.0, anchor="n", text=drive_files[2], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    window.mainloop()


def disable_ingest_button(canvas, ingest_name_var, button_1, message):
    illegal_characters = ["\\", '/', '*', '?', '"', '<', '>', '|', ":"]
    illegal_name = False
    ingest_name = ingest_name_var.get()

    root = ""

    try:
        root = os.path.join(str(config["Program"]["default output"]), ingest_name)
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
        canvas.itemconfig(message, text=f'Adding to existing ingest at {os.path.join(str(config["Program"]["default output"]), ingest_name)}')
        button_1["state"] = "normal"
    else:
        canvas.itemconfig(message, text=f'Ingesting to {os.path.join(str(config["Program"]["default output"]), ingest_name)}')
        button_1["state"] = "normal"
    canvas.after(1, lambda: disable_ingest_button(canvas, ingest_name_var, button_1, message))


def ingest_in_progress(drives, body, optics, orientation, ingest_name):
    global image_list
    global total_files
    global average_time
    average_time = 0

    window.title("Digestible · Ingesting")

    canvas = clear_screen()

    canvas.create_text(400.0, 37.0, anchor="n", text="Ingesting\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 271.0, 61.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(526.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    button_image_1 = tk.PhotoImage(file=asset_relative_path("abort.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: main("Ingest Aborted"),
                         relief="flat")
    button_1.place(x=704.0, y=421.0, width=59.0, height=31.0)

    entry_image_1 = tk.PhotoImage(file=asset_relative_path("ingesting_entry.png"))
    canvas.create_image(399.5, 282.0, image=entry_image_1)

    if drives == 1:
        canvas.create_text(400.0, 108.0, anchor="n", text=f"Ingesting {str(total_files)} files from {str(drives)} drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    else:
        canvas.create_text(400.0, 108.0, anchor="n", text=f"Ingesting {str(total_files)} files from {str(drives)} drives", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))

    images_left = canvas.create_text(400.0, 145.0, anchor="n", text="", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    progress = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=718)
    progress.place(x=41, y=375)

    time_remaining = canvas.create_text(41.0, 426.0, anchor="nw", text="", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))
    activity_list = tk.Listbox(font=("Roboto Mono", 13))
    activity_list.place(x=41.0, y=187.0, width=717.0, height=188.0)

    window.after(1, lambda: ingest_process(body, optics, orientation, progress, ingest_name, activity_list))
    window.after(10, lambda: time_left(canvas, time_remaining, images_left))

    window.mainloop()


def ingest_process(body, optics, orientation, progress, ingest_name, activity_list):
    global image_list
    global file_names
    global average_time
    global total_files
    root = os.path.join(str(config["Program"]["default output"]), ingest_name)
    name = ""

    start_time = time.time()

    current_image = image_list[-1]
    if os.name == "nt":
        current_file = current_image.split("\\")[-1]
    else:
        current_file = current_image.split("/")[-1]

    image_list.remove(current_image)
    file_names.remove(current_file)

    num_files = total_files - len(image_list)

    output = root

    if current_file in file_names:
        try:
            file = open(current_image, 'rb')
            image_name = current_file.split(".")[0]
            extension = current_file.split(".")[-1]
            tags = exifread.process_file(file, stop_tag='LensModel', details=False)
            name = image_name + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension
        except FileNotFoundError:
            main("Ingest failed, storage may have been disconnected, reattach and try again")

    body_name = "Unknown"
    lens_name = "Unknown"
    orientation_str = "Unknown"

    if body.get() == 0 and optics.get() == 0 and orientation.get() == 0:
        pass
    else:
        try:
            file = open(current_image, 'rb')

            if optics.get() == 1:
                tags = exifread.process_file(file, stop_tag='LensModel', details=False)
            else:
                tags = exifread.process_file(file, stop_tag='Image Orientation', details=False)

            if body.get() == 1:
                output = os.path.join(output, str(tags['Image Model']).replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))
                body_name = str(tags['Image Model'])

            if optics.get() == 1:
                output = os.path.join(output, str(tags['EXIF LensModel']).replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))
                lens_name = str(tags['EXIF LensModel'])

            if orientation.get() == 1:
                output = os.path.join(output, str(tags['Image Orientation']).replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", ""))
                orientation_str = str(tags['Image Orientation'])

        except exifread.exceptions:
            output = os.path.join(output, "Unsorted (No image data)")
        except FileNotFoundError:
            main("Ingest failed, storage may have been disconnected, reattach and try again")

    next_index = activity_list.size() + 1

    if os.path.exists(os.path.join(output, name)) and name != "":
        activity_list.insert(next_index, f"Skipped {current_file}, file already exists at {output}")
        activity_list.yview_scroll(1, "unit")

    elif os.path.exists(os.path.join(output, current_file)):
        activity_list.insert(next_index, f"Skipped {current_file}, file already exists at {output}")
        activity_list.yview_scroll(1, "unit")
    else:
        if not os.path.isdir(output):
            os.makedirs(output)

        try:
            shutil.copy2(current_image, output)
        except FileNotFoundError:
            main("Ingest failed, storage may have been disconnected, reattach and try again")

        if name != "":
            original_output_file_dir = os.path.join(output, current_file)
            final_dir = os.path.join(output, name)
            os.rename(original_output_file_dir, final_dir)

        if body_name == "Unknown" and lens_name == "Unknown" and orientation_str == "Unknown":
            message = "Image was not sorted"
        else:
            message = f"Shot on {body_name.strip()} with {lens_name.strip()}"

        activity_list.insert(next_index, f"Ingested {current_file}: {message}")
        activity_list.yview_scroll(1, "unit")

    progress["value"] = 100 - len(image_list)/total_files * 100

    average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

    if len(image_list) > 0:
        window.after(1, lambda: ingest_process(body, optics, orientation, progress, ingest_name, activity_list))
    else:
        time.sleep(1)
        main(f"Ingested {total_files} files to {root}")


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
        name_to_add = i.strip().replace("/", "").replace("\\", "").replace("*", "").replace(":", "").replace("<", "").replace(">", "").replace("|", "")
        if name_to_add != "Type names here" and name_to_add != "" and len(i) < 20 and name_to_add.lower() not in delegating_to and len(delegating_to) < 20:
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
        canvas.itemconfig(images_per_person_message, text=f"Total Images: {total_files}  |  About {round(total_files / len(delegating_to))} images per person")
        start_button["state"] = "normal"

    canvas.after(50, lambda: check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, editors, entered_editors, images_per_person_message, start_button))


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

    if "Delegated Images" in os.listdir(selected_folder):
        main('Folder has already been delegated, delete the "Delegated Images" folder to try again')

    for root, dirs, files in os.walk(selected_folder):

        for f in files:
            if is_media(f):
                image_list.append(os.path.join(root, f))
                file_names.append(f)
                files_to_delegate += 1
    total_files = len(image_list)

    if len(image_list) == 0:
        main("No files to delegate")

    canvas = clear_screen()

    canvas.create_text(400.0, 37.0, anchor="n", text="Delegate", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(35.0, 432.0, anchor="nw", text=f"Delegating from: {selected_folder}", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(45.0, 360.0, anchor="nw", text="Enter the names of up to 20 additional editors separated by commas.", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(370.0, 392.0, anchor="nw", text="Use names under 20 characters long", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    images_per_person_message = canvas.create_text(400.0, 116.0, anchor="n", text=f"Total Images: {total_files}  |  Images per person: ", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    editors = config["Program"]["saved editors"].split("*")

    while len(editors) < 6:
        editors.append("Save an editor to this list from settings")

    d2e1, d2e2, d2e3, d2e4, d2e5, d2e6 = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()

    e1 = tk.Checkbutton(window, text=editors[0], variable=d2e1)
    e1.tk_setPalette(background="#1F2124", foreground="white", selectcolor="#000000")
    e1.place(x=470.0, y=160.0)

    e2 = tk.Checkbutton(window, text=editors[1], variable=d2e2)
    e2.tk_setPalette(background="#1F2124", foreground="white", selectcolor="#000000")
    e2.place(x=470.0, y=190.0)

    e3 = tk.Checkbutton(window, text=editors[2], variable=d2e3)
    e3.tk_setPalette(background="#1F2124", foreground="white", selectcolor="#000000")
    e3.place(x=470.0, y=220.0)

    e4 = tk.Checkbutton(window, text=editors[3], variable=d2e4)
    e4.tk_setPalette(background="#1F2124", foreground="white", selectcolor="#000000")
    e4.place(x=470.0, y=250.0)

    e5 = tk.Checkbutton(window, text=editors[4], variable=d2e5)
    e5.tk_setPalette(background="#1F2124", foreground="white", selectcolor="#000000")
    e5.place(x=470.0, y=280.0)

    e6 = tk.Checkbutton(window, text=editors[5], variable=d2e6)
    e6.tk_setPalette(background="#1F2124", foreground="white", selectcolor="#000000")
    e6.place(x=470.0, y=310.0)

    editor_names_var = tk.StringVar()
    editor_names = tk.Entry(window, textvariable=editor_names_var, font=("Roboto Mono", 10), width=50)
    editor_names.insert(0, f"Type names here")
    editor_names.tk_setPalette(background="#1F2124")
    editor_names.focus_set()
    editor_names.place(x=45.0, y=390)

    delegating_to_message = canvas.create_text(41, 160, text=f"Delegating to nobody", anchor="nw", width=410, fill="#FFFFFF")

    button_image_1 = tk.PhotoImage(file=asset_relative_path("delegate_start.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: delegate_in_progress(selected_folder), relief="flat")
    button_1.place(x=684.0, y=428.0, width=82.0, height=25.0)

    button_image_2 = tk.PhotoImage(file=asset_relative_path("cancel.png"))
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Delegation cancelled"), relief="flat")
    button_2.place(x=611.0, y=429.0, width=64.0, height=25.0)

    canvas.after(20, lambda: check_selected_editors(canvas, delegating_to_message, d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, editors, editor_names_var, images_per_person_message, button_1))

    window.mainloop()


def delegate_in_progress(selected_folder):
    global delegating_to
    global average_time
    global file_names
    global image_list
    average_time = 0

    canvas = clear_screen()

    output = os.path.join(selected_folder, "Delegated Images")

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

    window.title("Digestible · Delegating")

    canvas.create_text(400.0, 37.0, anchor="n", text="Delegating", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(139.0, 58.0, 275.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(528.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    progress = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=718)
    progress.place(x=41, y=375)

    images_left = canvas.create_text(400.0, 145.0, anchor="n", text="", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    time_remaining = canvas.create_text(41.0, 426.0, anchor="nw", text="", fill="#FFFFFF",
                                        font=("Roboto Mono", 16 * -1))
    activity_list = tk.Listbox(font=("Roboto Mono", 13))
    activity_list.place(x=41.0, y=187.0, width=717.0, height=188.0)

    canvas.after(5, lambda: delegate_process(canvas, images_left, progress, selected_folder, activity_list))
    window.after(10, lambda: time_left(canvas, time_remaining, images_left))

    button_image_1 = tk.PhotoImage(file=asset_relative_path("abort.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: main("Aborted delegation"), relief="flat")
    button_1.place(x=699.0, y=422.0, width=70.0, height=39.0)

    window.mainloop()


def delegate_process(canvas, images_left, progress, selected_folder, activity_list):
    global image_list
    global average_time
    global total_files

    start_time = time.time()

    current_image = image_list[-1]
    image_list.remove(current_image)

    name = current_image[2]
    editor_folder = current_image[1]
    original_path = current_image[0]

    num_files = total_files - len(image_list)

    output = os.path.join(editor_folder, name)

    if not os.path.isdir(editor_folder):
        os.makedirs(editor_folder)

    try:
        shutil.copy2(original_path, output)
    except OSError:
        main("Ingest aborted, you may be out of space")

    progress["value"] = 100 - len(image_list)/total_files * 100

    average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

    if len(image_list) == 0:
        main(f"Delegated {total_files} to {len(delegating_to)}")
    else:
        next_index = activity_list.size() + 1
        activity_list.insert(next_index, f"Delegated {name} to {editor_folder.split('/')[-1]}")
        activity_list.yview_scroll(1, "unit")
        canvas.after(5, lambda: delegate_process(canvas, images_left, progress, selected_folder, activity_list))


def digest():
    canvas = clear_screen()
    main("Digest is WIP")

    window.title("Digestible · Digest")

    canvas.create_text(400.0, 37.0, anchor="n", text="Digest", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(400.0, 426.0, anchor="n", text="Long Operation Warning", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file=asset_relative_path("digest_start.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: digest_in_progress(),
                         relief="flat")

    button_1.place(x=683.0, y=418.0, width=80.0, height=35.0)

    entry_image_1 = tk.PhotoImage(file=asset_relative_path("digest_entry_1.png"))
    canvas.create_image(182.0, 118.5, image=entry_image_1)

    entry_1 = tk.Entry(bd=0, bg="#1F2124", fg="#FFFFFF", highlightthickness=0)

    entry_1.place(x=40.0, y=106.0, width=284.0, height=23.0)

    entry_image_2 = tk.PhotoImage(file=asset_relative_path("digest_entry_2.png"))
    canvas.create_image(399.5, 271.5, image=entry_image_2)
    entry_2 = tk.Text(bd=0, bg="#2C2E2F", fg="#FFFFFF", highlightthickness=0)

    button_image_2 = tk.PhotoImage(file=asset_relative_path("cancel.png"))
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from digest"), relief="flat")
    button_2.place(x=600.0, y=424.0, width=64.0, height=25.0)

    entry_2.place(x=40.0, y=145.0, width=719.0, height=251.0)

    window.mainloop()


def digest_in_progress():
    canvas = clear_screen()

    window.title("Digestible · Digesting")

    canvas.create_text(400.0, 37.0, anchor="n", text="Digesting", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 275.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(524.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Time Remaining:", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    canvas.create_text(510.0, 271.0, anchor="nw", text="Current image is:", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file=asset_relative_path("abort.png"))
    button_1 = tk.Button(image=button_image_1, borderwidth=0, command=lambda: main("Aborted Digest"), highlightthickness=0,
                         relief="flat")
    button_1.place(x=696.0, y=416.0, width=70.0, height=39.0)

    image_image_1 = tk.PhotoImage(file=asset_relative_path("placeholder_image.png"))
    canvas.create_image(261.0, 259.0, image=image_image_1)

    entry_image_1 = tk.PhotoImage(file=asset_relative_path("digest_entry.png"))
    canvas.create_image(635.5, 201.5, image=entry_image_1)
    entry_1 = tk.Text(bd=0, bg="#2C2E2F", fg="#FFFFFF", highlightthickness=0)
    entry_1.place(x=510.0, y=150.0, width=251.0, height=101.0)

    canvas.create_text(41.0, 115.0, anchor="nw", text="Digesting Folder:", fill="#FFFFFF",
                       font=("Roboto Mono", 14 * -1))

    window.mainloop()


if __name__ == '__main__':
    main()
