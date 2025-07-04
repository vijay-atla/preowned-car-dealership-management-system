# edit_car_listing.py

import customtkinter as ctk
import tkinter as tk
from utils import load_background, load_iconctk
from session import current_user
from database_utils import get_car_by_id
from PIL import Image
from tkinter import filedialog, messagebox





def open_edit_screen(root, parent_frame, car_id):
    global uploaded_images, selected_main_image_path, image_thumbnails
    uploaded_images = []
    selected_main_image_path = None
    image_thumbnails = []

    # Clear parent frame
    # parent_frame = root.winfo_children()[-1]
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # === Load car data ===
    car = get_car_by_id(car_id)
    if not car:
        tk.messagebox.showerror("Error", "Car not found!")
        return

    def show_success_popup(car_id, data, main_img_path):
        popup = ctk.CTkToplevel()
        popup.title("Car Updated Successfully")
        popup.geometry("500x400")
        popup.resizable(False, False)

        popup.attributes("-topmost", True)
        popup.lift()
        popup.configure(bg="#f9f9f9")
        popup.update_idletasks()
        w = 500
        h = 400
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")

        # Title
        ctk.CTkLabel(popup, text="✅ Car Listing Updated Successfully!", font=("Lato", 20, "bold"), text_color="black").pack(pady=25)

        # Thumbnail
        try:
            img = Image.open(main_img_path)
            img.thumbnail((140, 140))
            tk_img = ctk.CTkImage(light_image=img, size=(140, 140))
            ctk.CTkLabel(popup, image=tk_img, text="").place(x=30, y=100)
        except Exception as e:
            print("Thumbnail Error:", e)

        # Info
        info_text = f"Car ID: {car_id}\n\nMake: {data['Make']}\n\nModel: {data['Model']}\n\nYear: {data['Year']}\n\nPrice: ${data['Price ($)']}"
        ctk.CTkLabel(popup, text=info_text, font=("Lato", 14)).place(x=250, y=100)

        # OK Button
        def go_to_manage_listings():
            popup.destroy()
            from manage_car_listing import open_manage_car_listing
            open_manage_car_listing(root, parent_frame)

        ctk.CTkButton(popup, text="OK", width=120, fg_color="#17b8a6", text_color="black", border_color="#b4b4b4",
                    hover_color="#11998e", command=go_to_manage_listings).place(x=180, y=330)


    def save_changes():
        from database_utils import update_car_with_images  # 🔁 You must define this in your DB file

        # 1. Gather updated field values
        data = {}
        for key, widget in entry_refs.items():
            val = widget.get().strip()
            if key in ["Make", "Model", "Color", "Fuel Type", "Condition", "Title"]:
                val = val.title()
            elif key in ["VIN Number", "Drivetrain"]:
                val = val.upper()
            data[key] = val

        # 2. Description
        desc = description_box.get("1.0", "end").strip()
        data["description"] = desc if desc else ""
        data["Images"] = uploaded_images
        data["MainImage"] = selected_main_image_path

        # 3. Validation
        if not uploaded_images:
            messagebox.showerror("Missing Images", "Please upload at least one image.")
            return

        if not selected_main_image_path:
            messagebox.showerror("Main Image", "Please select a main image.")
            return

        # 4. Update in DB
        success, msg = update_car_with_images(car_id, data)

        if success:
            show_success_popup(car_id, data, selected_main_image_path)
        else:
            messagebox.showerror("Error", f"Failed to update car listing.\n{msg}")



    # === Background Image ===
    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.2)
    illustration_label_right = ctk.CTkLabel(parent_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)

    # === Top Header ===
    ctk.CTkLabel(parent_frame, image=load_iconctk("icons/manage_cars_icon.png", (60, 60)),
                 text="  Edit Car Listing", font=("Lato", 30, "bold"),
                 text_color="#008080", fg_color="#ffffff", compound="left").place(x=25, y=45)

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    # === Table Frame ===
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=480, fg_color="#ffffff",
                               corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # === Scrollable Content Frame ===
    scrollable_frame = ctk.CTkScrollableFrame(table_frame, width=655, height=450,
                                              fg_color="white", corner_radius=10,
                                              scrollbar_button_color="#d9d9d9",
                                              scrollbar_button_hover_color="#666666")
    scrollable_frame.grid(row=0, column=0, padx=5, pady=10)

    # Next Steps: Add form fields with edit icons and prefill values here...

    fields = [
        ("Make", "Model"),
        ("Year", "Price ($)"),
        ("VIN Number", "Drivetrain"),
        ("Fuel Type", "Mileage (mi)"),
        ("Condition", "Transmission"),
        ("Color", "Title"),
        ("Status", "Economy")
    ]

    dropdowns = {
        "Fuel Type": ["Gasoline", "Diesel", "Electric", "Hybrid"],
        "Condition": ["Excellent", "Good", "Average"],
        "Transmission": ["Automatic", "Manual", "CVT", "DCT"],
        "Status": ["Available", "Sold", "Archived"],
        "Title": ["Clean", "Rebuilt", "Salvage", "Lemon", "Bonded"]
    }

    field_to_key = {
        "Make": "make",
        "Model": "model",
        "Year": "year",
        "Price ($)": "price",
        "VIN Number": "vin",
        "Drivetrain": "drivetrain",
        "Fuel Type": "fuel_type",
        "Mileage (mi)": "mileage",
        "Condition": "car_condition",
        "Transmission": "transmission",
        "Color": "color",
        "Title": "title_status",
        "Status": "status",
        "Economy": "economy"
    }


    edit_icon = load_iconctk("icons/edit_icon.png", (15, 15))

    entry_refs = {}

    for row_idx, (left_label, right_label) in enumerate(fields):
        for col_idx, field in enumerate([left_label, right_label]):
            label = ctk.CTkLabel(scrollable_frame, text=field, font=("Lato", 15))
            label.grid(row=row_idx * 2, column=col_idx, padx=37, pady=(10, 0), sticky="w")

            # Decide input type
            if field in dropdowns:
                entry = ctk.CTkComboBox(scrollable_frame, values=dropdowns[field],
                                        width=230, height=35, border_color="#b4b4b4", fg_color="#e3e3e3", state="readonly")
                db_key = field_to_key.get(field, field.lower().replace(" ", "_"))
                value = str(car.get(db_key, "")).strip().title()
                # ✅ Validate value before setting
                if value in dropdowns[field]:
                    entry.set(value)
                else:
                    entry.set("Select")
            else:
                entry = ctk.CTkEntry(scrollable_frame, width=230, height=35,
                                     border_color="#b4b4b4", fg_color="#e3e3e3")
                db_key = field_to_key.get(field, field.lower().replace(" ", "_"))
                entry.insert(0, str(car.get(db_key, "")))

                entry.configure(state="readonly")

            entry.grid(row=row_idx * 2 + 1, column=col_idx, padx=(37, 0), pady=(0, 10), sticky="w")
            entry_refs[field] = entry

            # ✏️ Edit icon
            icon_label = ctk.CTkLabel(scrollable_frame, image=edit_icon, text="")
            icon_label.grid(row=row_idx * 2 + 1, column=col_idx, padx=(275, 0), pady=(0, 10), sticky="w")
            icon_label.configure(cursor="hand2")

            # Enable editing on click
            def make_editable(e, field_name=field, is_dropdown=(field in dropdowns)):
                widget = entry_refs[field_name]
                if is_dropdown:
                    widget.configure(state="normal")
                else:
                    widget.configure(state="normal")

            icon_label.bind("<Button-1>", make_editable)


    # === Description Box ===
    ctk.CTkLabel(scrollable_frame, text="Description", font=("Lato", 15)).grid(
        row=17, column=0, columnspan=2, sticky="w", padx=37, pady=(10, 0)
    )
    description_box = ctk.CTkTextbox(scrollable_frame, width=575, height=100, border_color="#b4b4b4",
                                    fg_color="#e3e3e3", border_width=2)
    description_box.insert("1.0", car.get("description", "").strip())
    description_box.configure(state="disabled")
    description_box.grid(row=18, column=0, columnspan=2, padx=37, pady=(5, 10), sticky="w")

    # ✏️ Description edit icon
    desc_edit_icon = ctk.CTkLabel(scrollable_frame, image=edit_icon, text="", cursor="hand2")
    desc_edit_icon.place(x=610, y=180)
    desc_edit_icon.grid(row = 18, column = 1, padx=(315, 0), pady=(0, 80), sticky="w")
    desc_edit_icon.bind("<Button-1>", lambda e: description_box.configure(state="normal"))

    # === Prepare image data ===
    uploaded_images = car.get("images", [])
    selected_main_image_path = car.get("main_image")
    image_thumbnails = []

    # === Image Section Title ===
    ctk.CTkLabel(scrollable_frame, text="Car Images", font=("Lato", 15)).grid(
        row=19, column=0, sticky="w", padx=37, pady=(20, 0), columnspan=2
    )

    # === Preview Frame ===
    preview_frame = ctk.CTkScrollableFrame(scrollable_frame, orientation="horizontal", width=550, height=110, fg_color="#d9d9d9", border_color="#b4b4b4", 
                                           border_width=2, corner_radius=10, scrollbar_button_color="#b4b4b4",
                                        scrollbar_button_hover_color="#666666")
    preview_frame._scrollbar.grid_configure(pady=5)
    preview_frame.grid(row=20, column=0, columnspan=2, padx=37, pady=(5, 10), sticky="w")

    def set_main_image(path):
        global selected_main_image_path
        selected_main_image_path = path
        render_edit_image_previews()

    def delete_image(path):
        global uploaded_images, selected_main_image_path
        uploaded_images.remove(path)
        if selected_main_image_path == path:
            selected_main_image_path = uploaded_images[0] if uploaded_images else None
        render_edit_image_previews()

    def show_image_popup(path):
        popup = ctk.CTkToplevel()
        popup.title("Image Preview")
        popup.geometry("600x450")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.lift()
        popup.configure(bg="#f9f9f9")
        popup.update_idletasks()

        img = Image.open(path)
        img.thumbnail((580, 400))
        ctk_img = ctk.CTkImage(light_image=img, size=(580, 400))

        img_label = ctk.CTkLabel(popup, image=ctk_img, text="")
        img_label.image = ctk_img
        img_label.pack(padx=10, pady=10)

    def upload_images():
        global uploaded_images, selected_main_image_path
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not file_paths:
            return

        uploaded_images.extend(file_paths)
        if not selected_main_image_path:
            selected_main_image_path = uploaded_images[0]
        render_edit_image_previews()


    def render_edit_image_previews():
        for widget in preview_frame.winfo_children():
            widget.destroy()

        # === Add ➕ Upload Tile ===
        plus_tile = ctk.CTkFrame(preview_frame, width=100, height=100, fg_color="#f0f0f0", corner_radius=10)
        plus_tile.grid(row=0, column=0, padx=5, pady=5)

        plus_btn = ctk.CTkButton(
            plus_tile, text="➕", font=("Lato", 24, "bold"), width=100, height=100,
            corner_radius=10, border_color="#666666", fg_color="#666666",
            command=upload_images, hover_color="#17B8A6"
        )
        plus_btn.place(relx=0.5, rely=0.5, anchor="center")

        # === Loop through images ===
        for i, img_path in enumerate(uploaded_images):
            is_main = img_path == selected_main_image_path
            border_color = "#00cc66" if is_main else "#cccccc"

            img_frame = ctk.CTkFrame(preview_frame, width=100, height=100, fg_color="#eeeeee",
                                    corner_radius=10, border_width=3, border_color=border_color)
            img_frame.grid(row=0, column=i+1, padx=5, pady=5)

            try:
                pil_img = Image.open(img_path)
                pil_img.thumbnail((90, 90))
                img = ctk.CTkImage(light_image=pil_img, size=(90, 80))
                image_thumbnails.append(img)

                img_label = ctk.CTkLabel(img_frame, image=img, text="")
                img_label.image = img
                img_label.place(x=5, y=5)

                # Click to preview full
                img_label.bind("<Button-1>", lambda e, p=img_path: show_image_popup(p))

            except Exception as e:
                print(f"[Image Load Error] {img_path}: {e}")

            # === Delete Button ===
            del_btn = ctk.CTkButton(
                img_frame, text="❌", width=5, height=5, font=("Lato", 12),
                fg_color="white", text_color="red",
                command=lambda p=img_path: delete_image(p)
            )
            del_btn.place(x=75, y=5)

            # === Main image mark or Set button ===
            if is_main:
                ctk.CTkLabel(img_frame, text="✔", font=("Lato", 16, "bold"), text_color="green",
                            width=16, height=16, fg_color="#d9d9d9", corner_radius=0).place(x=5, y=75)
            else:
                set_btn = ctk.CTkButton(
                    img_frame, text="⬜", width=11, height=11, font=("Lato", 11),
                    fg_color="#d9d9d9", text_color="#666666", corner_radius=0, hover_color="#d9d9d9",
                    command=lambda p=img_path: set_main_image(p)
                )
                set_btn.place(x=5, y=75)
                create_tooltip(set_btn, "Set as Display Image")

    def create_tooltip(widget, text, timeout=500):
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.overrideredirect(True)
            tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = tk.Label(tooltip, text=text, bg=None, fg="black", font=("Lato", 9), relief="solid", borderwidth=0)
            label.pack(ipadx=4, ipady=2)

            # Auto-destroy the tooltip after 3 sec
            tooltip.after(timeout, tooltip.destroy)

        widget.bind("<Enter>", show_tooltip)

    # === Call it now
    render_edit_image_previews()

    def go_back_to_manage():
        from manage_car_listing import open_manage_car_listing
        open_manage_car_listing(root, parent_frame)


    # === Save & Back Button Row ===
    button_row = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    button_row.grid(row=22, column=0, columnspan=2, pady=20)

    # Back Button
    ctk.CTkButton(
        button_row, text="Cancel", width=140, fg_color="#f05f5f", text_color="black",
        font=("Lato", 15, "bold"), hover_color="#f77474", border_color="#b4b4b4",
        command=lambda: go_back_to_manage()
    ).grid(row=0, column=0, padx=30)

    # Save Button
    ctk.CTkButton(
        button_row, text="Save Changes", width=160, fg_color="#17b8a6", text_color="black",
        font=("Lato", 15, "bold"), border_color="#b4b4b4", hover_color="#11998e",
        command=save_changes
    ).grid(row=0, column=1, padx=30)
