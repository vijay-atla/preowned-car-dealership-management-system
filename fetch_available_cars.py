import customtkinter as ctk
import tkinter as tk
from utils import load_iconctk
from database_utils import get_all_car_listings

def open_fetch_cars_popup(root, callback_on_select):
    popup = ctk.CTkToplevel(root)
    popup.geometry("720x550")
    popup.title("Select Car")
    popup.configure(fg_color="white")
    popup.attributes("-topmost", True)
    popup.lift()

    x = root.winfo_rootx() + 150
    y = root.winfo_rooty() + 100
    popup.geometry(f"+{x}+{y}")

    search_var = tk.StringVar()
    search_debounce_timer = [None]

    def on_search_change(*args):
        if search_debounce_timer[0] is not None:
            root.after_cancel(search_debounce_timer[0])

        def delayed_reload():
            reload_cars()

        search_debounce_timer[0] = root.after(400, delayed_reload)

    search_var.trace_add("write", on_search_change)

    edit_icon = load_iconctk("icons/edit_icon.png",(25,25))
    color_icon = load_iconctk("icons/color_icon.png",(13,13))
    transmission_icon = load_iconctk("icons/transmission_icon.png",(13,13))
    fuel_icon = load_iconctk("icons/fuel_icon.png",(13,13))
    id_icon = load_iconctk("icons/id.png",(18,18))


    def reload_cars():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        cars = get_all_car_listings(search_text=search_var.get(), filters=None, status="Available")

        if not cars:
            ctk.CTkLabel(scrollable_frame, text="😢 No cars found.", font=("Lato", 15, "bold")).pack(pady=40)
            return

        for car in cars:
            car_name = f"{car['make']} {car['model']} {car['year']}"

            card = ctk.CTkFrame(scrollable_frame, width=620, height=90, fg_color="#f4f4f4", corner_radius=10, border_color="#808080", border_width=1)
            card.pack(padx=10, pady=5)

            car_img = load_iconctk(car['img'], (100, 80))

            image_label = ctk.CTkLabel(card, image=car_img, text="", corner_radius=10)
            image_label.image = car_img  # Prevent garbage collection
            image_label.place(x=0, y=5)

            ctk.CTkLabel(card, text=car_name, font=("Lato", 16)).place(x=120, y=10)
            ctk.CTkLabel(card, text=f"VIN: {car['vin']}", font=("Lato", 12)).place(x=120, y=35)
            ctk.CTkLabel(card, text=f"${car['price']} | {car['fuel_type']} | {car['transmission']}", font=("Lato", 12)).place(x=120, y=60)

            def select_this(c=car):
                callback_on_select(c)
                popup.destroy()

            ctk.CTkButton(card, text="Select", width=80, font=("Lato", 14), fg_color="#a855f7", text_color="black", border_color="#808080", 
                          border_width=1, hover_color="#8b3cd3", command=select_this).place(x=500, y=30)

    # Search Bar
    search_frame = ctk.CTkFrame(popup, width=655, height=40, fg_color="#bababa",
                                corner_radius=10, border_color="#808080", border_width=1)
    search_frame.place(x=25, y=15)

    search_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/search_icon.png", (25, 25)), text="")
    search_icon_label.place(x=110, y=7)

    search_box = ctk.CTkEntry(search_frame, width=350, textvariable=search_var, placeholder_text="Search by model, year, or VIN...", corner_radius=15)
    search_box.place(x=140, y=7)

    ctk.CTkButton(search_frame, text="Go", width=60, fg_color="#30b8a9", text_color="black", command=reload_cars).place(x=500, y=7)

    # Scrollable Frame
    scroll_container = ctk.CTkFrame(popup, width=660, height=450, fg_color="white")
    scroll_container.place(x=25, y=60)

    scrollable_frame = ctk.CTkScrollableFrame(scroll_container, width=635, height=400, fg_color="white",
                                              corner_radius=10, border_color="#808080", border_width=5)
    scrollable_frame.pack()
    scrollable_frame._scrollbar.grid_configure(padx=(0, 10))

    reload_cars()
