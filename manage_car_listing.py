import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils import load_background, load_iconctk, show_gif_loader,hide_loader
import re
from database_utils import get_all_car_listings
from datetime import datetime
from session import current_user
from filter_popup import show_filter_popup
from view_car_details import open_view_car_details


active_filters = {}
debounce_timer = None




def open_manage_car_listing(root, parent_frame):

    def view_car(car):
        car_id = car["car_id"]
        show_gif_loader(parent_frame)
        parent_frame.after(300, lambda: [open_view_car_details(root, parent_frame, car_id=car_id), hide_loader()])

    def apply_search():
        search_text = search_var.get().strip()
        if search_text.lower() == "search by model, year or vin":
            search_text = ""
        selected_status = status_filter.get()
        filters = active_filters.copy()

        if search_text == "":
            search_box.delete(0, "end")  # Reset entry
            search_box.configure(placeholder_text="Search by model, year or VIN")

        if 'price' in filters:
            filters['price'] = tuple(filters['price'])
        if 'year' in filters:
            filters['year'] = tuple(filters['year'])
        if 'mileage' in filters:
            filters['mileage'] = tuple(filters['mileage'])
        if 'economy' in filters:
            filters['economy'] = tuple(filters['economy'])

        # 🛠️ Fix empty filters
        if not filters:
            filters = None

        results = get_all_car_listings(search_text=search_text, filters=filters, status=selected_status)
        load_manage_car_listing(root, scrollable_frame, results)




    def show_filter_with_loader():
        show_gif_loader(root, "Opening Filters...")
        root.after(500, lambda: [show_filter_popup(
            root, attr_filter_entry, attr_filter_entry, apply_search
        ), hide_loader()])
    
    def go_to_edit_car_listing(root, car_id):
        from edit_car_listing import open_edit_screen  # You'll create this screen if not already

        show_gif_loader(root, "Opening Edit Screen...")
        root.after(500, lambda: [open_edit_screen(root, parent_frame, car_id), hide_loader()])


    def debounced_search(*args):
        global debounce_timer
        if debounce_timer:
            root.after_cancel(debounce_timer)
        debounce_timer = root.after(400, apply_search)


    for widget in parent_frame.winfo_children():
        widget.destroy()

    # === Background ===
    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.2)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(parent_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)

    # Title + Icon
    ctk.CTkLabel(parent_frame, image=load_iconctk("icons/manage_cars_icon.png", (60, 60)),
                 text="  Manage Car Listings", font=("Lato", 30, "bold"),
                 text_color="#008080", fg_color="#ffffff", compound="left").place(x=25, y=45)

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    # === Table Frame ===
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=500, fg_color="#ffffff",
                               corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # === Search Frame (top of table) ===
    search_frame = ctk.CTkFrame(table_frame, width=660, height=40, fg_color="#bababa",
                                corner_radius=10, border_color="#808080", border_width=1)
    search_frame.place(x=15, y=10)

    search_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/search_icon.png", (25, 25)), text="")
    search_icon_label.place(x=10, y=7)

    search_var = tk.StringVar()
    search_box = ctk.CTkEntry(search_frame, placeholder_text="Search by model, year or VIN", corner_radius=20,
                              width=250)
    search_box.place(x=40, y=7)
    search_box.configure(textvariable=search_var)
    search_box.bind("<FocusIn>", lambda e: search_box.configure(placeholder_text=""))
    search_box.bind("<FocusOut>", lambda e: search_box.configure(placeholder_text="Search by model, year or VIN" if not search_var.get().strip() else ""))
    search_box.bind("<KeyRelease>", debounced_search)
    search_box.bind("<Return>", debounced_search)  # Enter key binding

    

    go_btn = ctk.CTkButton(search_frame, text="Go", width=37, height=23, fg_color="#30b8a9", text_color="black", border_width=1, cursor="hand2",
                           border_color="#b4b4b4", font=("Lato", 14), hover_color="#30b8a9", command=apply_search)
    go_btn.place(x=295, y=9)


    # Attribute-based filter icon (left side)
    filter_icon = load_iconctk("icons/filter_icon.png", (20, 20))

    attr_filter_icon_label = ctk.CTkLabel(search_frame, image=filter_icon, text="", cursor="hand2")
    attr_filter_icon_label.place(x=345, y=7)

    attr_filter_entry = ctk.CTkEntry(search_frame, placeholder_text="Filter by", width=100, height=23,
                                 border_color="#a7a7a7", corner_radius=5, border_width=1,
                                 text_color="#808080", font=("Lato", 16))
    attr_filter_entry.place(x=370, y=7)

    attr_filter_entry._entry.configure(cursor="hand2")
    attr_filter_entry.bind("<Button-1>", lambda e: show_filter_popup(root, attr_filter_entry, attr_filter_entry, apply_search, active_filters))
    attr_filter_icon_label.bind("<Button-1>", lambda e: show_filter_popup(root, attr_filter_entry, attr_filter_entry, apply_search, active_filters))

    filter_icon_label = ctk.CTkLabel(search_frame, image=filter_icon, text="  Status: ",
                                     compound="left", font=("Lato", 14))
    filter_icon_label.place(x=480, y=7)

    filter_var = tk.StringVar(value="All")

    status_filter = ctk.CTkComboBox(search_frame, values=["Available", "Sold", "Archived", "All"],
                                    width=100, height=25, variable=filter_var)
    status_filter.set("All")
    status_filter.place(x=550, y=8)
    status_filter.configure(command=lambda _: apply_search())



    # Scroll Frame for listing cards
    scroll_container = ctk.CTkFrame(table_frame, width=685, height=433, fg_color="white")
    scroll_container.place(x=5, y=60)

    scrollable_frame = ctk.CTkScrollableFrame(scroll_container, width=662, height=428, fg_color="white",
                                              corner_radius=10, scrollbar_button_color="#d9d9d9",
                                              scrollbar_button_hover_color="#666666")
    scrollable_frame.place(x=0, y=0)

    # 🧠 Placeholder for load_car_cards() will be added next step.

    edit_icon = load_iconctk("icons/edit_icon.png",(25,25))
    color_icon = load_iconctk("icons/color_icon.png",(13,13))
    transmission_icon = load_iconctk("icons/transmission_icon.png",(13,13))
    fuel_icon = load_iconctk("icons/fuel_icon.png",(13,13))
    id_icon = load_iconctk("icons/id.png",(18,18))




    def load_manage_car_listing(root, scrollable_frame, cars_list):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()


        if not cars_list:
            ctk.CTkLabel(scrollable_frame, text="😢 No cars found matching your filters.",
                        font=("Lato", 16, "bold"), text_color="red").pack(pady=20)
            return # ✅ Stop further execution
        

        for car in cars_list:
            card = ctk.CTkFrame(scrollable_frame, width=640, height=90,
                                fg_color="#ebebeb", corner_radius=10,
                                border_color="#808080", border_width=1)
            card.pack(pady=7)

            image_frame = ctk.CTkFrame(card, width=100, height=80, fg_color="black", corner_radius=8, border_color="#808080")
            image_frame.place(x=7, y=5)

            car_img = load_iconctk(car["img"], (100, 80))

            image_label = ctk.CTkLabel(image_frame, image=car_img, text="", corner_radius=10)
            image_label.image = car_img  # Prevent garbage collection
            image_label.place(x=-10, y=0)

            # Title & Specs
            car_name = f"{car['make']} {car['model']} {car['year']}"

            car_title = ctk.CTkLabel(card, text=car_name.title(), font=("Lato", 18) , text_color="#333333")
            car_title.place(x=120, y=5)
            ctk.CTkLabel(card, image=id_icon, compound="left", text=f" {car["car_id"]}", font=("Lato", 14), text_color="#444444").place(x=400, y=5)
            ctk.CTkLabel(card, text=f"VIN: {car['vin']}", font=("Lato", 12), text_color="#444444").place(x=120, y=35)
            ctk.CTkLabel(card, image=color_icon ,compound="left",text=f" {car['car_color']}", font=("Lato", 12), text_color="#444444").place(x=400, y=35)
            ctk.CTkLabel(card, image=fuel_icon ,compound="left",text=f" {car['fuel_type']}", font=("Lato", 12), text_color="#444444").place(x=120, y=60)
            ctk.CTkLabel(card, image=transmission_icon ,compound="left",text=f" {car['transmission']}", font=("Lato", 12), text_color="#444444").place(x=400, y=60)
            # ctk.CTkLabel(card, text=f"Condition: {car['car_condition']}", font=("Lato", 13), text_color="#666666").place(x=120, y=80)

            car_title.configure(cursor = "hand2")
            car_title.bind("<Button-1>", lambda e, c=car: view_car(c))

            # Edit Button (you can wire this to a real edit screen)
            edit_button = ctk.CTkLabel(card, image= edit_icon, text="")
            edit_button.place(x=600, y=5)
            edit_button.configure(cursor = "hand2")
            edit_button.bind("<Button-1>", lambda e, cid=car["car_id"]: go_to_edit_car_listing(root, cid))

            # Status Pill
            status_color = {"Available": "green", "Sold": "red", "Archived": "gray"}.get(car["status"], "#999999")
            ctk.CTkLabel(card, text=car["status"], font=("Lato", 13, "bold"),
                        fg_color=status_color, text_color="white",
                        width=70, height=25, corner_radius=10).place(x=540, y=50)

            


    show_gif_loader(parent_frame)
    parent_frame.after(300, lambda: [apply_search(), hide_loader()]) # Will respect active_filters