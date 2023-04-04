import tkinter as tk


def main():
    window = tk.Tk()

    window.geometry("800x480")
    window.configure(bg="#1F2124")
    window.title("Digestible")
    window.resizable(False, False)

    home(window, "")


def home(window, message):
    clear_screen(window)

    if not message:
        message = ""
    else:
        window.after(3000, lambda: canvas.itemconfig(change_message, text=""))

    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")
    canvas.place(x=0, y=0)

    canvas.create_text(90.0, 37.0, anchor="nw", text="Digestible", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    change_message = canvas.create_text((800 - len(message)*10)/2 + len(message)*2, 150, anchor="nw", text=message, fill="#FFFFFF", font=("Roboto Mono", 10 * -1))

    logo = tk.PhotoImage(file="assets/frame0/image_1.png")
    canvas.create_image(60.0, 59.0, image=logo)

    button_image_help = tk.PhotoImage(file="assets/frame0/button_1.png")
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0,
                         command=lambda: help_menu(window), relief="flat")
    help_btn.place(x=42.0, y=421.0, width=51.0, height=25.0)

    button_image_settings = tk.PhotoImage(file="assets/frame0/button_2.png")
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0,
                             command=lambda: settings(window), relief="flat")
    settings_btn.place(x=678.0, y=421.0, width=81.0, height=24.0)

    canvas.create_text(630.0, 52.0, anchor="nw", text="Welcome back 👋", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    button_image_inventory = tk.PhotoImage(file="assets/frame0/button_3.png")
    inventory_btn = tk.Button(image=button_image_inventory, borderwidth=0, highlightthickness=0,
                              command=lambda: inventory(window), relief="flat")
    inventory_btn.place(x=354.0, y=419.0, width=92.0, height=28.0)

    button_image_ingest = tk.PhotoImage(file="assets/frame0/button_4.png")
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0,
                           command=lambda: ingest(window), relief="flat")
    ingest_btn.place(x=101.0, y=219.0, width=124.0, height=42.0)

    button_image_delegate = tk.PhotoImage(file="assets/frame0/button_5.png")
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0,
                             command=lambda: delegate(window), relief="flat")
    delegate_btn.place(x=568.0, y=219.0, width=138.0, height=42.0)

    button_image_digest = tk.PhotoImage(file="assets/frame0/button_6.png")
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0,
                           command=lambda: digest(window), relief="flat")
    digest_btn.place(x=338.0, y=219.0, width=124.0, height=42.0)

    canvas.create_rectangle(42.0, 237.0, 96.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(229.0, 237.0, 328.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(467.0, 237.0, 551.0, 240.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(716.0, 237.0, 754.0, 240.0, fill="#2C2E2F", outline="")

    window.mainloop()


def ingest(window):
    clear_screen(window)
    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(335.0, 37.0, anchor="nw", text="Ingest\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 402.0, anchor="nw", text="Sort By:", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame4/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0,
                         command=lambda: ingesting(window), relief="flat")
    button_1.place(x=692.0, y=417.0, width=72.0, height=36.0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: home(window, "Came from ingest"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    canvas.create_text(315.0, 172.0, anchor="nw", text="Detected Drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(267.0, 297.0, anchor="nw", text="Long Operation Warning", fill="#FF0000",
                       font=("Roboto Mono", 20 * -1))
    canvas.create_text(554.0, 172.0, anchor="nw", text="Detected Drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(76.0, 172.0, anchor="nw", text="Detected Drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(354.0, 206.0, anchor="nw", text="File Count", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(593.0, 206.0, anchor="nw", text="File Count", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(115.0, 206.0, anchor="nw", text="File Count", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    window.mainloop()


def ingesting(window):
    clear_screen(window)
    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(335.0, 37.0, anchor="nw", text="Ingest\n", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")
    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Time Remaining:", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame3/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: abort(window, "Ingest Aborted"),
                         relief="flat")
    button_1.place(x=704.0, y=421.0, width=59.0, height=31.0)

    entry_image_1 = tk.PhotoImage(file="assets/frame3/entry_1.png")
    canvas.create_image(399.5, 282.0, image=entry_image_1)

    entry_1 = tk.Text(bd=0, bg="#2C2E2F", fg="#FFFFFF", highlightthickness=0)
    entry_1.place(x=41.0, y=187.0, width=717.0, height=188.0)

    canvas.create_text(315.0, 108.0, anchor="nw", text="Detected Drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(554.0, 108.0, anchor="nw", text="Detected Drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(76.0, 108.0, anchor="nw", text="Detected Drive", fill="#FFFFFF", font=("Roboto Mono", 20 * -1))
    canvas.create_text(354.0, 142.0, anchor="nw", text="File Count", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(593.0, 142.0, anchor="nw", text="File Count", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))
    canvas.create_text(115.0, 142.0, anchor="nw", text="File Count", fill="#FFFFFF", font=("Roboto Mono", 15 * -1))

    window.mainloop()


def digest(window):
    clear_screen(window)
    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(335.0, 37.0, anchor="nw", text="Digest", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Long Operation Warning", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame2/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: digesting(window),
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
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: home(window, "Came from digest"), relief="flat")
    button_2.place(x=600.0, y=424.0, width=64.0, height=25.0)

    entry_2.place(x=40.0, y=145.0, width=719.0, height=251.0)

    window.mainloop()


def digesting(window):
    clear_screen(window)

    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(335.0, 37.0, anchor="nw", text="Digest", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(516.0, 58.0, 651.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_text(41.0, 426.0, anchor="nw", text="Time Remaining:", fill="#FFFFFF", font=("Roboto Mono", 16 * -1))

    canvas.create_text(510.0, 271.0, anchor="nw", text="Current image is:", fill="#FFFFFF",
                       font=("Roboto Mono", 16 * -1))

    button_image_1 = tk.PhotoImage(file="assets/frame1/button_1.png")
    button_1 = tk.Button(image=button_image_1, borderwidth=0, command=lambda: abort(window, "Aborted Digest"), highlightthickness=0,
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


def clear_screen(window):
    for widget in window.winfo_children():
        widget.destroy()


def delegate(window):
    clear_screen(window)
    print("DELEGATE MENU")
    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
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
    button_1 = tk.Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: delegating(window), relief="flat")
    button_1.place(x=684.0, y=428.0, width=82.0, height=25.0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: home(window, "Came from delegate"), relief="flat")
    button_2.place(x=611.0, y=429.0, width=64.0, height=25.0)

    window.mainloop()


def delegating(window):
    clear_screen(window)
    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(313.0, 37.0, anchor="nw", text="Delegate", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(145.0, 58.0, 281.0, 61.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(
        516.0,
        58.0,
        651.0,
        61.0,
        fill="#2C2E2F",
        outline="")

    image_image_1 = tk.PhotoImage(
        file="assets/frame7/image_1.png")
    canvas.create_image(
        569.0,
        221.0,
        image=image_image_1
    )

    canvas.create_text(
        41.0,
        384.0,
        anchor="nw",
        text="Digesting Folder:",
        fill="#FFFFFF",
        font=("Roboto Mono", 14 * -1)
    )

    canvas.create_text(
        41.0,
        114.0,
        anchor="nw",
        text="Delegating To:",
        fill="#FFFFFF",
        font=("Roboto Mono", 14 * -1)
    )

    canvas.create_text(
        380.0,
        384.0,
        anchor="nw",
        text="Output Folder:",
        fill="#FFFFFF",
        font=("Roboto Mono", 14 * -1)
    )

    canvas.create_text(
        380.0,
        335.0,
        anchor="nw",
        text="Images Left:",
        fill="#FFFFFF",
        font=("Roboto Mono", 11 * -1)
    )

    canvas.create_text(
        697.0,
        335.0,
        anchor="nw",
        text="File Name",
        fill="#FFFFFF",
        font=("Roboto Mono", 11 * -1)
    )

    button_image_1 = tk.PhotoImage(
        file="assets/frame7/button_1.png")
    button_1 = tk.Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: abort(window, "Aborted Delegation"),
        relief="flat"
    )
    button_1.place(
        x=699.0,
        y=422.0,
        width=70.0,
        height=39.0
    )

    window.mainloop()


def settings(window):
    clear_screen(window)
    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(42.0, 37.0, anchor="nw", text="Options", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    canvas.create_rectangle(217.0, 58.0, 551.0, 61.0, fill="#2C2E2F", outline="")

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: home(window, "Came from settings"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def inventory(window):
    clear_screen(window)
    print("INVENTORY MENU")

    clear_screen(window)
    canvas = tk.Canvas(
        window,
        bg="#1F2124",
        height=480,
        width=800,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: home(window, "Came from the inventory"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def help_menu(window):
    clear_screen(window)
    print("HELP SCREEN")

    clear_screen(window)
    canvas = tk.Canvas(
        window,
        bg="#1F2124",
        height=480,
        width=800,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)

    button_image_2 = tk.PhotoImage(file="assets/frame6/button_2.png")
    button_2 = tk.Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: home(window, "Came from the help menu"), relief="flat")
    button_2.place(x=611.0, y=425.0, width=64.0, height=25.0)

    window.mainloop()


def abort(window, message):
    home(window, message)


if __name__ == '__main__':
    main()
