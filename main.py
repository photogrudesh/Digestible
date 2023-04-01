# import os

import tkinter as tk


def main():
    window = tk.Tk()

    window.geometry("800x480")
    window.configure(bg="#1F2124")
    window.title("Digestible")

    canvas = tk.Canvas(window, bg="#1F2124", height=480, width=800, bd=0, highlightthickness=0, relief="ridge")

    canvas.place(x=0, y=0)
    canvas.create_text(90.0, 37.0, anchor="nw", text="Digestible", fill="#FFFFFF", font=("Roboto Mono", 36 * -1))

    logo = tk.PhotoImage(file="assets/frame0/image_1.png")
    canvas.create_image(60.0, 59.0, image=logo)

    button_image_help = tk.PhotoImage(file="assets/frame0/button_1.png")
    help_btn = tk.Button(image=button_image_help, borderwidth=0, highlightthickness=0, command=help_menu, relief="flat")
    help_btn.place(x=42.0, y=421.0, width=51.0, height=25.0)

    button_image_settings = tk.PhotoImage(file="assets/frame0/button_2.png")
    settings_btn = tk.Button(image=button_image_settings, borderwidth=0, highlightthickness=0, command=settings, relief="flat")
    settings_btn.place(x=678.0, y=421.0, width=81.0, height=24.0)

    canvas.create_text(630.0, 52.0, anchor="nw", text="Welcome back 👋", fill="#FFFFFF", font=("Roboto Mono", 14 * -1))

    button_image_inventory = tk.PhotoImage(file="assets/frame0/button_3.png")
    inventory_btn = tk.Button(image=button_image_inventory, borderwidth=0, highlightthickness=0, command=inventory, relief="flat")
    inventory_btn.place(x=354.0, y=419.0, width=92.0, height=28.0)

    button_image_ingest = tk.PhotoImage(file="assets/frame0/button_4.png")
    ingest_btn = tk.Button(image=button_image_ingest, borderwidth=0, highlightthickness=0, command=ingest, relief="flat")
    ingest_btn.place(x=101.0, y=219.0, width=124.0, height=42.0)

    button_image_delegate = tk.PhotoImage(file="assets/frame0/button_5.png")
    delegate_btn = tk.Button(image=button_image_delegate, borderwidth=0, highlightthickness=0, command=delegate, relief="flat")
    delegate_btn.place(x=568.0, y=219.0, width=138.0, height=42.0)

    button_image_digest = tk.PhotoImage(file="assets/frame0/button_6.png")
    digest_btn = tk.Button(image=button_image_digest, borderwidth=0, highlightthickness=0, command=digest, relief="flat")
    digest_btn.place(x=338.0, y=219.0, width=124.0, height=42.0)

    canvas.create_rectangle(42.0, 237.0, 96.0, 240.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(229.0, 237.0, 328.0, 240.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(467.0, 237.0, 551.0, 240.0, fill="#2C2E2F", outline="")

    canvas.create_rectangle(716.0, 237.0, 754.0, 240.0, fill="#2C2E2F", outline="")

    window.resizable(False, False)
    window.mainloop()


def ingest():
    print("INGEST")


def digest():
    print("DIGEST")


def delegate():
    print("DELEGATE")


def settings():
    print("SETTINGS")


def inventory():
    print("INVENTORY")


def help_menu():
    print("HELP")


if __name__ == '__main__':
    main()
