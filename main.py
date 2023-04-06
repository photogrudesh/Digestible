import configparser
import os
import shutil
import time
import tkinter as tk
import exifread
import psutil
from tkinter import ttk

window = tk.Tk()
window.geometry("800x480")
window.configure(bg="#1F2124")
window.title("Digestible")
window.resizable(False, False)

image_list = []
average_time = 0
total_files = 0
eta = 0


def write(config_file):
    with open('./config.dgstbl', 'w') as configfile:
        config_file.write(configfile)


def main(message=""):
    canvas = clear_screen()

    config = configparser.ConfigParser()

    if not os.path.exists('/config.dgstbl'):
        write(config)
        config.add_section('Program')
    else:
        config.read('/config.dgstbl')

    write(config)

    if message:
        window.after(5000, lambda: canvas.itemconfig(change_message, text=""))

    canvas.create_text(90.0, 37.0, anchor="nw", text="Digestible", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    change_message = canvas.create_text((800 - len(message)*10)/2 + len(message)*2, 150, anchor="nw", text=message, fill="#FFFFFF", font=("Roboto Mono", 10 * -1))

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

    canvas.create_text(630.0, 52.0, anchor="nw", text="Welcome back 👋", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

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

    canvas = clear_screen()

    canvas.create_text(335.0, 37.0, anchor="nw", text="Ingest\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

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

    image_list = []
    for i in inputs:
        files_on_drive = 0
        for root, dirs, files in os.walk(i):
            for f in files:
                if is_media(f):
                    image_list.append(os.path.join(root, f))
                    files_on_drive += 1
        drive_files.append(str(files_on_drive) + " files")
    total_files = len(image_list)

    while len(inputs) < 3:
        inputs.append("No Drive Detected")
        drive_files.append("0 Files")

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 395.0, anchor="nw", text="Sort By:", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    tk.Checkbutton(window, text="Body Type", variable=sort_body).place(x=40, y=425.0)
    tk.Checkbutton(window, text="Optics", variable=sort_optics).place(x=145.0, y=425.0)
    tk.Checkbutton(window, text="Orientation", variable=sort_orientation).place(x=225.0, y=425.0)

    button_image_1 = tk.PhotoImage(file="assets/frame4/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: ingesting(inputs, drive_files, sort_body, sort_optics, sort_orientation), relief="flat")
    button_1.place(x=692.0, y=417.0, width=72.0, height=36.0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from ingest"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    if len(image_list) > 1000:
        canvas.create_text(267.0, 297.0, anchor="nw", text=f"Long Operation Warning ({len(image_list)} images to ingest)", fill="#FF0000", font=("Roboto Mono", 20 * -1))
    else:
        canvas.create_text(247.0, 297.0, anchor="nw", text=f"Total images to ingest {len(image_list)}", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))

    canvas.create_text(76.0, 158.0, anchor="nw", text=inputs[0], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(315.0, 158.0, anchor="nw", text=inputs[1], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(554.0, 158.0, anchor="nw", text=inputs[2], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(115.0, 192.0, anchor="nw", text=drive_files[0], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(354.0, 192.0, anchor="nw", text=drive_files[1], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(593.0, 192.0, anchor="nw", text=drive_files[2], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    window.mainloop()


def ingesting(inputs, drive_files, body, optics, orientation):
    global image_list
    global total_files
    global average_time

    canvas = clear_screen()

    canvas.create_text(302.0, 37.0, anchor="nw", text="Ingesting\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 271.0, 61.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(526.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    time_remaining = canvas.create_text(41.0, 426.0, anchor="nw", text=eta, fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame3/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: abort("Ingest Aborted"),
                         relief="flat")
    button_1.place(x=704.0, y=421.0, width=59.0, height=31.0)

    entry_image_1 = tk.PhotoImage(file="assets/frame3/entry_1.png")
    canvas.create_image(399.5, 282.0, image=entry_image_1)

    entry_1 = tk.Text(bd=0, bg="#2C2E2F", fg="#FFFFFF", highlightthickness=0)
    entry_1.place(x=41.0, y=187.0, width=717.0, height=188.0)

    canvas.create_text(315.0, 108.0, anchor="nw", text=inputs[0], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(554.0, 108.0, anchor="nw", text=inputs[2], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(76.0, 108.0, anchor="nw", text=inputs[1], fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(354.0, 142.0, anchor="nw", text=drive_files[0], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(593.0, 142.0, anchor="nw", text=drive_files[2], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(115.0, 142.0, anchor="nw", text=drive_files[1], fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    progress = ttk.Progressbar(window, orient='horizontal', mode='determinate', length=718)
    progress.place(x=41, y=375)

    window.after(1, lambda: ingest_process(body, optics, orientation, progress))
    window.after(10, lambda: time_left(canvas, time_remaining))

    Lb1 = tk.Listbox()
    Lb1.place()

    window.mainloop()


def ingest_process(body, optics, orientation, progress):
    global image_list
    global average_time
    global total_files
    root = "/Users/sudesh/Desktop/test output/"

    start_time = time.time()

    current_image = image_list[-1]
    image_list.remove(current_image)
    num_files = total_files - len(image_list)

    output = root

    if not os.path.isdir(output):
        os.mkdir(output)

    if body.get() == 0 and optics.get() == 0 and orientation.get() == 0:
        pass
    else:
        file = open(current_image, 'rb')
        tags = exifread.process_file(file, stop_tag='LensModel', details=False)

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

    shutil.copy(current_image, output)

    progress["value"] = 100 - len(image_list)/total_files * 100

    average_time = (average_time * (num_files - 1) + time.time() - start_time) / num_files

    if len(image_list) > 0:
        window.after(1, lambda: ingest_process(body, optics, orientation, progress))
    else:
        time.sleep(1)
        main(f"Ingested {total_files} files to {root}")


def time_left(canvas, time_remaining):
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

    canvas.itemconfig(time_remaining, text=eta)
    window.after(10, lambda: time_left(canvas, time_remaining))


def digest():
    canvas = clear_screen()

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

    canvas.create_text(303.0, 37.0, anchor="nw", text="Digesting", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 275.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(524.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Time Remaining:", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    canvas.create_text(510.0, 271.0, anchor="nw", text="Current image is:", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame1/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, command=lambda: abort("Aborted Digest"), highlightthickness=0,
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
    ext = file.split(".")[-1]
    raw_extensions = ["cr2", "rw2", "raf", "erf", "nrw", "nef", "arw", "rwz", "eip", "bay", "dng", "dcr", "gpr", "raw",
                      "crw", "3fr", "sr2", "k25", "kc2", "mef", "dng", "cs1", "orf", "mos", "ari", "kdc", "cr3", "fff",
                      "srf", "srw", "j6i", "mrw", "mfw", "x3f", "rwl", "pef", "iiq", "cxi", "nksc", "mdc"]

    if ext.lower() in raw_extensions:
        return True
    else:
        return False


def delegate():
    canvas = clear_screen()

    canvas.create_text(313.0, 37.0, anchor="nw", text="Delegate", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    image_image_1 = tk.PhotoImage(file="assets/frame6/image_1.png")
    canvas.create_image(569.0, 221.0, image=image_image_1)

    canvas.create_text(35.0, 432.0, anchor="nw", text="Delegating from:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(41.0, 114.0, anchor="nw", text="Select Editors:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(381.0, 340.0, anchor="nw", text="Total Images:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(381.0, 365.0, anchor="nw", text="Images per person:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame6/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: delegating(), relief="flat")
    button_1.place(x=684.0, y=428.0, width=82.0, height=25.0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from delegate"), relief="flat")
    button_2.place(x=611.0, y=429.0, width=64.0, height=25.0)

    window.mainloop()


def delegating():
    canvas = clear_screen()

    canvas.create_text(294.0, 37.0, anchor="nw", text="Delegating", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(139.0, 58.0, 275.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(528.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    image_image_1 = tk.PhotoImage(file="assets/frame7/image_1.png")
    canvas.create_image(569.0, 221.0, image=image_image_1)

    canvas.create_text(41.0, 384.0, anchor="nw", text="Digesting Folder:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(41.0, 114.0, anchor="nw", text="Delegating To:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(380.0, 384.0, anchor="nw", text="Output Folder:", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    canvas.create_text(380.0, 335.0, anchor="nw", text="Images Left:", fill="#FFFFFF", font=("Roboto Mono", 11 * -1))

    canvas.create_text(697.0, 335.0, anchor="nw", text="File Name", fill="#FFFFFF", font=("Roboto Mono", 11 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame7/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: abort("Aborted Delegation"), relief="flat")
    button_1.place(x=699.0, y=422.0, width=70.0, height=39.0)

    window.mainloop()


def settings():
    canvas = clear_screen()

    canvas.create_text(42.0, 37.0, anchor="nw", text="Options", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(217.0, 58.0, 551.0, 61.0, fill="#2C2E2F", outline="")

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from settings"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def inventory():
    canvas = clear_screen()

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the inventory"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def help_menu():
    canvas = clear_screen()

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: main("Came from the help menu"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def abort(message):
    main(message)


if __name__ == '__main__':
    main()
