import configparser
import datetime
import os
import shutil
import time
import tkinter as tk
import exifread
import psutil
from tkinter import ttk
from tkinter import filedialog

window = tk.Tk()
window.geometry("800x480")
window.configure(bg="#1F2124")
window.resizable(False, False)
config = configparser.ConfigParser()

image_list = []
file_names = []
average_time = 0
total_files = 0
eta = 0


def write(config_file):
    with open('./config.dgstbl', 'w') as configfile:
        config_file.write(configfile)


def main(message=""):
    canvas = clear_screen()

    window.title("Digestible")

    if os.path.exists('./config.dgstbl'):
        config.read('./config.dgstbl')
    else:
        config.add_section("Program")
        write(config)

    config["Program"]["default Output"] = "/Users/sudesh/Desktop/test output"
    config["Program"]["saved_editors"] = "The Hair*Matt Smith*Pikachu*Robbie*Anne"

    write(config)

    if message:
        window.after(5000, lambda: canvas.itemconfig(change_message, text=""))

    canvas.create_text(90.0, 37.0, anchor="nw", text="Digestible", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    change_message = canvas.create_text(400, 150, anchor="n", text=message, fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    logo = tk.PhotoImage(file="assets/frame0/image_1.png")
    canvas.create_image(60.0, 59.0, image=logo)

    button_image_help = tk.PhotoImage(file="assets/frame0/button_1.png")
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0,
                         command=lambda: help_menu(), relief="flat")
    help_btn.place(x=42.0, y=421.0, width=51.0, height=25.0)

    button_image_settings = tk.PhotoImage(file="assets/frame0/button_2.png")
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(), relief="flat")
    settings_btn.place(x=678.0, y=421.0, width=81.0, height=24.0)

    canvas.create_text(747.0, 52.0, anchor="ne", text="Welcome back 👋", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    button_image_inventory = tk.PhotoImage(file="assets/frame0/button_3.png")
    inventory_btn = tk.Button(image=button_image_inventory, borderwidth=0, highlightthickness=0,
                              command=lambda: inventory(), relief="flat")
    inventory_btn.place(x=354.0, y=419.0, width=92.0, height=28.0)

    button_image_ingest = tk.PhotoImage(file="assets/frame0/button_4.png")
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0,
                           command=lambda: ingest(), relief="flat")
    ingest_btn.place(x=101.0, y=219.0, width=124.0, height=42.0)

    button_image_delegate = tk.PhotoImage(file="assets/frame0/button_5.png")
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(), relief="flat")
    delegate_btn.place(x=568.0, y=219.0, width=138.0, height=42.0)

    button_image_digest = tk.PhotoImage(file="assets/frame0/button_6.png")
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0,
                           command=lambda: digest(), relief="flat")
    digest_btn.place(x=338.0, y=219.0, width=124.0, height=42.0)

    canvas.create_rectangle(42.0, 237.0, 96.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(229.0, 237.0, 328.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(467.0, 237.0, 551.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(716.0, 237.0, 754.0, 240.0, fill="#2C2E2F", outline="")

    window.mainloop()


def ingest():
    global image_list
    global total_files
    global average_time
    global file_names

    window.title("Digestible · Ingest")

    canvas = clear_screen()

    canvas.create_text(335.0, 37.0, anchor="nw", text="Ingest\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    image_list = []
    file_names = []
    drive_files = []

    sort_orientation, sort_body, sort_optics = tk.IntVar(), tk.IntVar(), tk.IntVar()

    inputs = []

    for i in psutil.disk_partitions():
        add_volume = True
        if psutil.disk_usage(i.mountpoint).total > 137438953472:
            add_volume = False
        if os.name == "posix" and i.mountpoint.startswith("/System"):
            add_volume = False

        if add_volume:
            inputs.append(i.mountpoint)

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
    body.tk_setPalette(background="#1F2124", foreground="white")
    body.place(x=40, y=425.0)

    optics = tk.Checkbutton(window, text="Optics", variable=sort_optics)
    optics.tk_setPalette(background="#1F2124", foreground="white")
    optics.place(x=133.0, y=425.0)

    orient = tk.Checkbutton(window, text="Orientation", variable=sort_orientation)
    orient.tk_setPalette(background="#1F2124", foreground="white")
    orient.place(x=201.0, y=425.0)

    current_time = datetime.datetime.now()
    default_name = current_time.strftime("%d-%m-%Y-%H-%M-%S")

    canvas.create_text(315, 428, text="Ingest Name:", anchor="nw", font=("Roboto Mono", 14 * -1), fill="#FFFFFF")

    ingest_name_var = tk.StringVar()
    ingest_name = tk.Entry(window, textvariable=ingest_name_var, font=("Roboto mono", 10), width=27)
    ingest_name.insert(0, f"{default_name}")
    ingest_name.tk_setPalette(background="#1F2124")
    ingest_name.focus_set()
    ingest_name.place(x=410.0, y=426)

    button_image_1 = tk.PhotoImage(file="assets/frame4/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: ingesting(drives, sort_body, sort_optics, sort_orientation, ingest_name_var.get().strip()), relief="flat")
    button_1.place(x=692.0, y=417.0, width=72.0, height=36.0)

    message = canvas.create_text(400.0, 345.0, anchor="n", text="Name the ingest below to start", fill="#FFFFFF", font=("Roboto Mono", 14 * -1), width=750)

    disable_button(canvas, ingest_name_var, button_1, message)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Cancelled Ingest"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    extra_drives = len(inputs) - 3
    if extra_drives > 0:
        canvas.create_text(400.0, 250.0, anchor="n", text=f"{extra_drive_files} files to ingest from {extra_drives} other drive(s)", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    if len(image_list) > 1000:
        canvas.create_text(400.0, 297.0, anchor="n", text=f"This may take a while, {len(image_list)} images to ingest", fill="#FF0000", font=("Roboto Mono", 16 * -1))
    else:
        canvas.create_text(400.0, 297.0, anchor="n", text=f"{len(image_list)} images to ingest", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    canvas.create_text(150.0, 158.0, anchor="n", text=inputs[0], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(400.0, 158.0, anchor="n", text=inputs[1], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(650.0, 158.0, anchor="n", text=inputs[2], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(150.0, 192.0, anchor="n", text=drive_files[0], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(400.0, 192.0, anchor="n", text=drive_files[1], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(650.0, 192.0, anchor="n", text=drive_files[2], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    window.mainloop()


def disable_button(canvas, ingest_name_var, button_1, message):
    illegal_characters = ["\\", '/', '*', '?', '"', '<', '>', '|', ":"]
    illegal_name = False
    ingest_name = ingest_name_var.get()
    root = os.path.join(str(config["Program"]["default output"]), ingest_name)

    for i in illegal_characters:
        if i in ingest_name_var.get():
            illegal_name = True

    if ingest_name == "" or ingest_name is None:
        canvas.itemconfig(message, text="Name the ingest below to start")
        button_1["state"] = "disabled"
    elif illegal_name:
        canvas.itemconfig(message, text='Avoid using \ / : * ? " < > |')
        button_1["state"] = "disabled"
    elif os.path.exists(root):
        canvas.itemconfig(message, text=f'Adding to existing ingest at {os.path.join(str(config["Program"]["default output"]), ingest_name)}')
        button_1["state"] = "normal"
    else:
        canvas.itemconfig(message, text=f'Ingesting to {os.path.join(str(config["Program"]["default output"]), ingest_name)}')
        button_1["state"] = "normal"
    canvas.after(1, lambda: disable_button(canvas, ingest_name_var, button_1, message))


def ingesting(drives, body, optics, orientation, ingest_name):
    global image_list
    global total_files
    global average_time

    window.title("Digestible · Ingesting")

    canvas = clear_screen()

    canvas.create_text(302.0, 37.0, anchor="nw", text="Ingesting\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 271.0, 61.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(526.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    time_remaining = canvas.create_text(41.0, 426.0, anchor="nw", text=eta, fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame3/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: main("Ingest Aborted"),
                         relief="flat")
    button_1.place(x=704.0, y=421.0, width=59.0, height=31.0)

    entry_image_1 = tk.PhotoImage(file="assets/frame3/entry_1.png")
    canvas.create_image(399.5, 282.0, image=entry_image_1)

    if drives == 1:
        canvas.create_text(400.0, 108.0, anchor="n", text=f"Ingesting {str(total_files)} files from {str(drives)} drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    else:
        canvas.create_text(400.0, 108.0, anchor="n", text=f"Ingesting {str(total_files)} files from {str(drives)} drives", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))

    images_left = canvas.create_text(400.0, 145.0, anchor="n", text="", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    progress = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=718)
    progress.place(x=41, y=375)

    activity_list = tk.Listbox(font=("Roboto Mono", 14))
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

    if not os.path.isdir(root):
        os.mkdir(root)

    start_time = time.time()

    current_image = image_list[-1]
    current_file = current_image.split("/")[-1]
    image_list.remove(current_image)
    file_names.remove(current_file)

    num_files = total_files - len(image_list)

    output = root

    if current_file in file_names:
        file = open(current_image, 'rb')
        extension = current_file.split(".")[-1]
        tags = exifread.process_file(file, stop_tag='LensModel', details=False)
        name = current_file + " " + str(tags["Image DateTime"]).replace(":", "-") + "." + extension
        output = root

    if not os.path.isdir(output):
        os.mkdir(output)

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
                output = os.path.join(output, str(tags['Image Model']).replace("/", ""))
                if not os.path.isdir(output):
                    os.mkdir(output)

            if optics.get() == 1:
                output = os.path.join(output, str(tags['EXIF LensModel']).replace("/", ""))
                if not os.path.isdir(output):
                    os.mkdir(output)

            if orientation.get() == 1:
                output = os.path.join(output, str(tags['Image Orientation']).replace("/", ""))
                if not os.path.isdir(output):
                    os.mkdir(output)

        except exifread.exceptions:
            output = os.path.join(output, "Unsorted (No image data)")
            if not os.path.isdir(output):
                os.mkdir(output)

        except FileNotFoundError:
            main("Drive unplugged or missing, reattach storage and start ingesting again")

    next_index = activity_list.size() + 1

    if os.path.exists(os.path.join(output, current_file)):
        activity_list.insert(next_index, f"Skipped {current_file}, file already exists at {output.replace(root, '')}")
        activity_list.yview_scroll(1, "unit")
    else:
        shutil.copy(current_image, output)

        if name != "":
            original_output_file_dir = os.path.join(output, current_file)
            final_dir = os.path.join(output, name)
            os.rename(original_output_file_dir, final_dir)

        progress["value"] = 100 - len(image_list)/total_files * 100

        average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

        activity_list.insert(next_index, f"Ingested {current_file} to .{output.replace(root, '')}")
        activity_list.yview_scroll(1, "unit")

    if len(image_list) > 0:
        window.after(1, lambda: ingest_process(body, optics, orientation, progress, ingest_name, activity_list))
    else:
        time.sleep(1)
        main(f"Ingested {total_files} files to {root}")


def time_left(canvas, time_remaining, images_left):
    global eta
    num_files = total_files - len(image_list)
    items_left = total_files - num_files

    eta = average_time * items_left

    if round(eta) < 2:
        eta = "Almost done ingesting"
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


def digest():
    canvas = clear_screen()

    window.title("Digestible · Digest")

    canvas.create_text(335.0, 37.0, anchor="nw", text="Digest", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Long Operation Warning", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame2/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: digesting(),
                         relief="flat")

    button_1.place(x=683.0, y=418.0, width=80.0, height=35.0)

    entry_image_1 = tk.PhotoImage(file="assets/frame2/entry_1.png")
    canvas.create_image(182.0, 118.5, image=entry_image_1)

    entry_1 = tk.Entry(bd=0, bg="#1F2124", fg="#FFFFFF", highlightthickness=0)

    entry_1.place(x=40.0, y=106.0, width=284.0, height=23.0)

    entry_image_2 = tk.PhotoImage(file="assets/frame2/entry_2.png")
    canvas.create_image(399.5, 271.5, image=entry_image_2)
    entry_2 = tk.Text(bd=0, bg="#2C2E2F", fg="#FFFFFF", highlightthickness=0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from digest"), relief="flat")
    button_2.place(x=600.0, y=424.0, width=64.0, height=25.0)

    entry_2.place(x=40.0, y=145.0, width=719.0, height=251.0)

    window.mainloop()


def digesting():
    canvas = clear_screen()

    window.title("Digestible · Digesting")

    canvas.create_text(303.0, 37.0, anchor="nw", text="Digesting", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 275.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(524.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Time Remaining:", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    canvas.create_text(510.0, 271.0, anchor="nw", text="Current image is:", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame1/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, command=lambda: main("Aborted Digest"), highlightthickness=0,
                         relief="flat")
    button_1.place(x=696.0, y=416.0, width=70.0, height=39.0)

    image_image_1 = tk.PhotoImage(file="assets/frame1/image_1.png")
    canvas.create_image(261.0, 259.0, image=image_image_1)

    entry_image_1 = tk.PhotoImage(file="assets/frame1/entry_1.png")
    canvas.create_image(635.5, 201.5, image=entry_image_1)
    entry_1 = tk.Text(bd=0, bg="#2C2E2F", fg="#FFFFFF", highlightthickness=0)
    entry_1.place(x=510.0, y=150.0, width=251.0, height=101.0)

    canvas.create_text(41.0, 115.0, anchor="nw", text="Digesting Folder:", fill="#FFFFFF",
                       font=("Roboto Mono", 14 * -1))

    window.mainloop()


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


def delegate(selected_folder=""):
    global total_files
    global image_list

    window.title("Digestible · Delegate")

    num_people = 1

    if selected_folder == "":
        selected_folder = tk.filedialog.askdirectory()
        if selected_folder != "":
            delegate(selected_folder)
        else:
            main("Delegation aborted, no folder selected")

    image_list = []
    files_to_delegate = 0

    for root, dirs, files in os.walk(selected_folder):
        for f in files:
            if is_media(f):
                image_list.append(os.path.join(root, f))
                files_to_delegate += 1
    total_files = len(image_list)

    if len(image_list) == 0:
        main("No files to delegate")

    canvas = clear_screen()

    canvas.create_text(313.0, 37.0, anchor="nw", text="Delegate", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(35.0, 432.0, anchor="nw", text=f"Delegating from: {selected_folder}", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(45.0, 360.0, anchor="nw", text="Enter the names of additional editors separated by commas.", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(400.0, 116.0, anchor="n", text=f"Total Images: {total_files}  |  Images per person: {round(total_files/num_people)}", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    editors = config["Program"]["saved_editors"].split("*")

    while len(editors) < 10:
        editors.append("Save an editor to this list from settings")

    d2e1, d2e2, d2e3, d2e4, d2e5, d2e6, d2e7, d2e8, d2e9, d2e10 = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()

    e1 = tk.Checkbutton(window, text=editors[0], variable=d2e1)
    e1.tk_setPalette(background="#1F2124", foreground="white")
    e1.place(x=60.0, y=155.0)

    e2 = tk.Checkbutton(window, text=editors[1], variable=d2e2)
    e2.tk_setPalette(background="#1F2124", foreground="white")
    e2.place(x=60.0, y=185.0)

    e3 = tk.Checkbutton(window, text=editors[2], variable=d2e3)
    e3.tk_setPalette(background="#1F2124", foreground="white")
    e3.place(x=60.0, y=215.0)

    e4 = tk.Checkbutton(window, text=editors[3], variable=d2e4)
    e4.tk_setPalette(background="#1F2124", foreground="white")
    e4.place(x=60.0, y=245.0)

    e5 = tk.Checkbutton(window, text=editors[4], variable=d2e5)
    e5.tk_setPalette(background="#1F2124", foreground="white")
    e5.place(x=60.0, y=275.0)

    e6 = tk.Checkbutton(window, text=editors[5], variable=d2e6)
    e6.tk_setPalette(background="#1F2124", foreground="white")
    e6.place(x=400.0, y=155.0)

    e7 = tk.Checkbutton(window, text=editors[6], variable=d2e7)
    e7.tk_setPalette(background="#1F2124", foreground="white")
    e7.place(x=400.0, y=185.0)

    e8 = tk.Checkbutton(window, text=editors[7], variable=d2e8)
    e8.tk_setPalette(background="#1F2124", foreground="white")
    e8.place(x=400.0, y=215.0)

    e9 = tk.Checkbutton(window, text=editors[8], variable=d2e9)
    e9.tk_setPalette(background="#1F2124", foreground="white")
    e9.place(x=400.0, y=245.0)

    e10 = tk.Checkbutton(window, text=editors[9], variable=d2e10)
    e10.tk_setPalette(background="#1F2124", foreground="white")
    e10.place(x=400.0, y=275.0)

    editor_names_var = tk.StringVar()
    ingest_name = tk.Entry(window, textvariable=editor_names_var, font=("Roboto mono", 10), width=50)
    ingest_name.insert(0, f"Type names here")
    ingest_name.tk_setPalette(background="#1F2124")
    ingest_name.focus_set()
    ingest_name.place(x=45.0, y=390)

    button_image_1 = tk.PhotoImage(file="assets/frame6/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: delegating(), relief="flat")
    button_1.place(x=684.0, y=428.0, width=82.0, height=25.0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Delegation cancelled"), relief="flat")
    button_2.place(x=611.0, y=429.0, width=64.0, height=25.0)

    window.mainloop()


def delegating():
    canvas = clear_screen()

    window.title("Digestible · Delegating")

    canvas.create_text(294.0, 37.0, anchor="nw", text="Delegating", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(139.0, 58.0, 275.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(528.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    image_image_1 = tk.PhotoImage(file="assets/frame7/image_1.png")
    canvas.create_image(569.0, 221.0, image=image_image_1)

    canvas.create_text(41.0, 384.0, anchor="nw", text="Delegating from::", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(41.0, 114.0, anchor="nw", text="Delegating To:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(380.0, 384.0, anchor="nw", text="Output Folder:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(380.0, 335.0, anchor="nw", text="Images Left:", fill="#FFFFFF", font=("Roboto Mono", 11 * -1))

    canvas.create_text(697.0, 335.0, anchor="nw", text="File Name", fill="#FFFFFF", font=("Roboto Mono", 11 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame7/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: main("Aborted delegation"), relief="flat")
    button_1.place(x=699.0, y=422.0, width=70.0, height=39.0)

    window.mainloop()


def settings():
    canvas = clear_screen()

    window.title("Digestible · Options")

    canvas.create_text(42.0, 37.0, anchor="nw", text="Options", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(217.0, 58.0, 551.0, 61.0, fill="#2C2E2F", outline="")

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from settings"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def inventory():
    canvas = clear_screen()

    window.title("Digestible · Inventory")

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the inventory"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def help_menu():
    canvas = clear_screen()

    window.title("Digestible · Help")

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the help menu"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


if __name__ == '__main__':
    main()
