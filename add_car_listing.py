# add_car_listing.py

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
import os
from utils import load_background, load_iconctk
from session import current_user

uploaded_images = []  # List of image paths
image_thumbnails = []  # Store CTkImage objects to prevent GC
selected_main_image_path = None  # ✅ Track selected main image




def open_add_car_listing(root, parent_frame):
    # Clear existing widgets from parent_frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.2)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(parent_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)


    # Welcome Message
    ctk.CTkLabel(parent_frame,  image=load_iconctk("icons/add_car_icon.png", (60, 60)), text="  Add Car Listing", 
                                font=("Lato", 30, "bold"), text_color="#008080", fg_color="#ffffff", compound="left").place(x=25, y=45)  

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)
    

    # Table Frame
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=480, fg_color="#ffffff", corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # === Scrollable Area ===
    scrollable_frame = ctk.CTkScrollableFrame(table_frame, width=655, height=450, fg_color="white", corner_radius=10,
                                               scrollbar_button_color="#d9d9d9", scrollbar_button_hover_color="#666666")
    scrollable_frame.grid(row=0, column=0, padx=5, pady=10)

    # === Form Fields Grid ===
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
        "Status": ["Available", "Sold"],
        "Title": ["Clean", "Rebuilt", "Salvage", "Lemon", "Bonded"]

    }

    entry_refs = {}

    for row_idx, (left_label, right_label) in enumerate(fields):
        for col_idx, field in enumerate([left_label, right_label]):
            label = ctk.CTkLabel(scrollable_frame, text=field, font=("Lato", 15))
            label.grid(row=row_idx * 2, column=col_idx, padx=37, pady=(10, 0), sticky="w")

            if field in dropdowns:
                entry = ctk.CTkComboBox(scrollable_frame, values=dropdowns[field], width=250, height=35,
                                        border_color="#b4b4b4", fg_color="#d9d9d9")
                entry.set("Select")  # 👈 This sets the default display
            else:
                entry = ctk.CTkEntry(scrollable_frame, width=250, height=35, border_color="#b4b4b4", fg_color="#d9d9d9")

            entry.grid(row=row_idx * 2 + 1, column=col_idx, padx=37, pady=(0, 10), sticky="w")
            entry_refs[field] = entry

    # === Description Box ===
    ctk.CTkLabel(scrollable_frame, text="Description (Optional)", font=("Lato", 15)).grid(row=14, column=0, columnspan=2, sticky="w", padx=37, pady=(20, 0))
    description_box = ctk.CTkTextbox(scrollable_frame, width=575, height=100, border_color="#b4b4b4", fg_color="#d9d9d9", border_width=2)
    description_box.grid(row=15, column=0, columnspan=2, padx=37, pady=(5, 10), sticky="w")

    # === Upload Image ===
    # Image Section Title
    ctk.CTkLabel(scrollable_frame, text="Car Images", font=("Lato", 15)).grid(
        row=18, column=0, sticky="w", padx=37, pady=(20, 0), columnspan=2
    )

    # Frame that holds image previews
    preview_frame = ctk.CTkScrollableFrame(scrollable_frame, orientation="horizontal", width=550, height=110, fg_color="#d9d9d9", 
                                           border_color="#b4b4b4", border_width=2, corner_radius=10, scrollbar_button_color="#b4b4b4", 
                                           scrollbar_button_hover_color="#666666")
    preview_frame._scrollbar.grid_configure(pady=5)
    preview_frame.grid(row=19, column=0, columnspan=2, padx=37, pady=(5, 10), sticky="w")



    def show_image_popup(path):
        popup = ctk.CTkToplevel()
        popup.title("Image Preview")
        popup.geometry("600x450")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.lift()
        popup.configure(bg="#f9f9f9")
        popup.update_idletasks()
        w = 600
        h = 450
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")


        # Load and resize image
        img = Image.open(path)
        img.thumbnail((580, 400))
        ctk_img = ctk.CTkImage(light_image=img, size=(580, 400))

        img_label = ctk.CTkLabel(popup, image=ctk_img, text="")
        img_label.image = ctk_img  # Keep reference
        img_label.pack(padx=10, pady=10)


    def set_main_image(path):
        global selected_main_image_path
        selected_main_image_path = path
        render_image_previews()


    def upload_images():
        global uploaded_images, selected_main_image_path
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not file_paths:
            return

        uploaded_images.extend(file_paths)

         # ✅ Set first image as default main image
        if not selected_main_image_path and uploaded_images:
            selected_main_image_path = uploaded_images[0]

        render_image_previews()


    def delete_image(path):
        global selected_main_image_path
        uploaded_images.remove(path)

        # Reset main image if it was deleted
        if selected_main_image_path == path:
            selected_main_image_path = uploaded_images[0] if uploaded_images else None

        render_image_previews()


    
    def render_image_previews():
        for widget in preview_frame.winfo_children():
            widget.destroy()

        # Add the [+] tile at the start
        plus_tile = ctk.CTkFrame(preview_frame, width=100, height=100, fg_color="#f0f0f0", corner_radius=10)
        plus_tile.grid(row=0, column=0, padx=5, pady=5)

        plus_btn = ctk.CTkButton(
            plus_tile, text="➕", font=("Lato", 24, "bold"), width=100, height=100, corner_radius=10, border_color="#666666",
            fg_color="#666666", command=upload_images, hover_color="#17B8A6"
        )
        plus_btn.place(relx=0.5, rely=0.5, anchor="center")

        # Show uploaded thumbnails
        for i, img_path in enumerate(uploaded_images):
            border_color = "#00cc66" if selected_main_image_path == img_path else "#cccccc"
            img_frame = ctk.CTkFrame(preview_frame, width=100, height=100, fg_color="#eeeeee", corner_radius=10, border_width=3,
                                     border_color=border_color)
            img_frame.grid(row=0, column=i + 1, padx=5, pady=5)

            pil_img = Image.open(img_path)
            pil_img.thumbnail((90, 90))
            img = ctk.CTkImage(light_image=pil_img, size=(90, 80))
            image_thumbnails.append(img)

            img_label = ctk.CTkLabel(img_frame, image=img, text="")
            img_label.image = img
            img_label.place(x=5, y=5)

            img_label.bind("<Button-1>", lambda e, p=img_path: show_image_popup(p))

            # Delete button (top-right)
            del_btn = ctk.CTkButton(
                img_frame, text="❌", width=5, height=5, font=("Lato", 12),
                fg_color="white", text_color="red",
                command=lambda p=img_path: delete_image(p)
            )
            del_btn.place(x=75, y=5)

            # ✅ Show "Set" button or "✔" for main image
            if selected_main_image_path == img_path:
                ctk.CTkLabel(
                    img_frame, text="✔", font=("Lato", 16, "bold"), text_color="green",
                    width=16, height=16, fg_color="#d9d9d9", corner_radius=0,
                ).place(x=5, y=75)
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


    render_image_previews()


    # === Buttons ===
    def submit_form():
        data = {}

        for key, field in entry_refs.items():
            val = field.get().strip()
            
            # Apply formatting based on field
            if key in ["Make", "Model", "Color", "Fuel Type", "Condition", "Title"]:
                val = val.title()
            elif key in ["VIN Number", "Drivetrain"]:
                val = val.upper()

            data[key] = val

        # Keep description as is (multi-line)
        desc = description_box.get("1.0", "end").strip()
        data["description"] = desc if desc else ""  # store empty string if nothing typed
        data["staff_id"] = current_user["user_id"]

        
        if not uploaded_images:
            messagebox.showerror("Missing Images", "Please upload at least one image.")
            return
        
        if not selected_main_image_path:
            messagebox.showerror("Main Image", "Please select a main image.")
            return

        data["Images"] = uploaded_images  # ✅ List of uploaded image paths
        data["MainImage"] = selected_main_image_path

        # Create a list of required fields (excluding 'description')
        required_fields = {k: v for k, v in data.items() if k != "description"}

        if not all(required_fields.values()):
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        # Add DB insert here
        from database_utils import insert_car_with_images
    
        success, msg, car_id = insert_car_with_images(data, uploaded_images, selected_main_image_path)
        if success:
            # clear form or redirect
            show_success_popup(car_id, data, selected_main_image_path, reset_form,lambda: go_back())
        else:
            messagebox.showerror("Error", msg)

    def show_success_popup(car_id, data, main_img_path, reset_callback, dashboard_callback):
        popup = ctk.CTkToplevel()
        popup.title("Car Added Successfully")
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
        ctk.CTkLabel(popup, text="🎉 Car Listing Added Successfully!", font=("Lato", 20, "bold"), text_color="black").pack(pady=25)

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

        # Buttons
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.place(x=35, y=350)

        # Edit (placeholder – future feature)
        ctk.CTkButton(btn_frame, text="Edit", width=120, fg_color="#d7f58a", text_color="black", hover_color="#cff06a",
                      border_color="#b4b4b4", border_width=2).grid(row=0, column=0, padx=20)

        ctk.CTkButton(btn_frame, text="Add Another", width=120, fg_color="#17b8a6", text_color="black", border_color="#b4b4b4",border_width=2,
                  command=lambda: [popup.destroy(), reset_callback()]).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_frame, text="Go to Dashboard", width=120, fg_color="#11998e", text_color="black", border_color="#b4b4b4",border_width=2,
                    command=lambda: [popup.destroy(), dashboard_callback()]).grid(row=0, column=2, padx=10)



    def reset_form():
        for key, field in entry_refs.items():
            if isinstance(field, ctk.CTkEntry):
                field.delete(0, "end")
            elif isinstance(field, ctk.CTkComboBox):
                field.set("Select")  # 👈 reset dropdowns to default
        description_box.delete("1.0", "end")
        uploaded_images.clear()
        image_thumbnails.clear()
        render_image_previews()  # 👈 Refresh the preview tiles

    def go_back():
        try:
            for widget in parent_frame.winfo_children():
                widget.destroy()

            if current_user["role"] == "admin":
                from admin_dashboard import open_admin_dashboard_main_frame
                open_admin_dashboard_main_frame(root) 
            elif current_user["role"] == "staff":
                 from staff_dashboard import open_staff_dashboard_main_frame
                 open_staff_dashboard_main_frame(root)
            else:
                messagebox.showerror("Error", f"Unrecognized role: {current_user["role"]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to dashboard.\n{e}")
        


    # Create a centered row with 3 buttons spaced out
    button_row = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    button_row.grid(row=23, column=0, columnspan=4, pady=30)

    # Cancel Button (Red)
    ctk.CTkButton(button_row, text="Cancel", width=120, fg_color="#f05f5f", font=("Lato", 16, "bold"),
                  text_color="black", hover_color="#f77474",border_color="#b4b4b4", command=go_back).grid(row=0, column=0, padx=(37, 45))

    # Reset Button (Light Green)
    ctk.CTkButton(button_row, text="Reset", width=120, fg_color="#d7f58a", font=("Lato", 16, "bold"),
                  text_color="black", border_color="#b4b4b4", hover_color="#cff06a", command=reset_form).grid(row=0, column=1, padx=45)

    # Submit Button (Teal)
    ctk.CTkButton(button_row, text="Submit", width=120, fg_color="#17b8a6", font=("Lato", 16, "bold"),
                  text_color="black", border_color="#b4b4b4", hover_color="#17B8A6", command=submit_form).grid(row=0, column=2, padx=45)