import customtkinter as ctk
import tkinter as tk
from PIL import Image
from utils import load_iconctk, load_background, show_gif_loader, hide_loader, show_custom_message
from database_utils import get_car_by_id, book_test_drive, insert_customer_inquiry
from session import current_user
from tkcalendar import DateEntry
import datetime
import tkinter
from schedule_popup import open_schedule_popup






def open_view_car_details(root, parent_frame, car_id):
    role = current_user["role"]
    car_data = get_car_by_id(car_id)

    # Clear current content
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Background
    bg_img = load_background("icons/default_bg.png", (750, 525), 0.25)
    ctk.CTkLabel(parent_frame, image=bg_img, text="").place(x=0, y=65)

    # Heading
    ctk.CTkLabel(parent_frame, text="  View Car Details", font=("Lato", 30, "bold"), 
                 text_color="#008080", compound="left").place(x=25, y=45)

    if role in ["admin", "staff"]:
        welcome_msg = f"Welcome, {role.title()}, {current_user["full_name"]}!"
    elif role == "customer":
        welcome_msg = f"Welcome, {current_user["full_name"]}!"
    else:
        welcome_msg = "Welcome!"
    ctk.CTkLabel(parent_frame, text=welcome_msg.title(), font=("Lato", 20), fg_color="#ffffff").place(x=500, y=80)

    # === Detail Container Frame ===
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=490, fg_color="#ffffff",
                               corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # (Next steps: Main image, car details right side, thumbnails, buttons, reviews etc.)

    def open_full_image():
        img_path = car_data["images"][current_img_index[0]]
        try:
            # Open new window
            popup = tk.Toplevel(root)
            popup.title("Full Image")
            popup.geometry("800x600")
            popup.configure(bg="black")

            # Load and resize image to fit popup while preserving ratio
            image = Image.open(img_path)
            image = image.resize((780, 560), Image.LANCZOS)
            img_tk = ctk.CTkImage(light_image=image, size=(780, 560))

            lbl = ctk.CTkLabel(popup, image=img_tk, text="")
            lbl.image = img_tk
            lbl.pack(padx=10, pady=10)

        except Exception as e:
            print("Error loading full image:", e)


    def finalize_booking(date_selected, time_selected):
        success, message = book_test_drive(
            customer_id=current_user["user_id"],
            car_id=car_id,
            preferred_date=date_selected,
            preferred_time=time_selected,
            location="PCDS, 1011 S Main St, Mt Pleasant, MI, USA - 48858"
        )
        hide_loader()

        if success:
            show_custom_message("Success", f"Test Drive booked on {date_selected} at {time_selected}!\nSee you at the showroom.")
        else:
            show_custom_message("Error", f"Failed to book test drive: {message}", type="error")


    def handle_book_test_drive():
        if current_user["role"] == "customer":
            def after_confirm(date_selected, time_selected):
                # 👇 Database booking now
                # Show loading GIF
                show_gif_loader(root, "Booking Test Drive...")

                # After a small delay (simulate loading), actually book
                root.after(800, lambda: finalize_booking(date_selected, time_selected))

            open_schedule_popup(root, on_confirm=after_confirm)

        elif current_user["role"] == "anonymous" or not current_user["role"]:
            show_custom_message("Login Required", "Please login to book a test drive!", type="warning")

        else:
            show_custom_message("Access Denied", "Only customers can book a test drive.", type="warning")


    def open_inquiry_popup():
        if current_user["role"] == "anonymous" or not current_user["role"]:
            show_custom_message("Login Required", "Please login to send an inquiry!", type="warning")
            return

        popup = ctk.CTkToplevel(root)
        # popup.geometry("500x300")
        popup.title("Send Inquiry")
        popup.resizable(False, False)
        popup.grab_set()

        popup_width = 500
        popup_height = 300
        # Get right_frame (or root) position and size
        parent_x = root.winfo_rootx()
        parent_y = root.winfo_rooty()
        parent_width = root.winfo_width()
        parent_height = root.winfo_height()
        # Calculate center position
        x = parent_x + (parent_width - popup_width) // 2
        y = parent_y + (parent_height - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        ctk.CTkLabel(popup, text="Type your inquiry below:", font=("Lato", 14)).place(x=20, y=20)

        inquiry_textbox = ctk.CTkTextbox(popup, width=450, height=150, font=("Lato", 13))
        inquiry_textbox.place(x=20, y=60)

        def submit_inquiry():
            message = inquiry_textbox.get("1.0", "end").strip()
            if not message:
                show_custom_message("Warning", "Inquiry cannot be empty.", type="warning")
                return
            
            success, msg = insert_customer_inquiry(current_user["user_id"], car_id, message)
            if success:
                popup.destroy()
                show_custom_message("Success", "Inquiry submitted successfully!\nOur team will get back to you soon.")
            else:
                show_custom_message("Error", f"Failed to submit inquiry: {msg}", type="error")

        ctk.CTkButton(popup, text="Submit Inquiry", width=180, command=submit_inquiry).place(x=80, y=230)
        ctk.CTkButton(popup, text="Cancel", width=120, fg_color="gray", command=popup.destroy).place(x=300, y=230)



    # ===== LEFT SIDE: Main Image + Thumbnails =====
    main_image_frame = ctk.CTkFrame(table_frame, width=320, height=280, fg_color="#f9f9f9", corner_radius=8, border_width=1, border_color="#808080")
    main_image_frame.place(x=10, y=10)

    main_image_label = ctk.CTkLabel(main_image_frame, text="")
    main_image_label.place(x=10, y=10)
    main_image_label.bind("<Button-1>", lambda e: open_full_image())
    main_image_label.configure(cursor="hand2")


    current_img_index = [0]  # wrapped in list so we can update it inside local functions

    def show_image_by_index(index):
        try:
            image = load_iconctk(car_data["images"][index], (300, 220))
            main_image_label.configure(image=image)
            main_image_label.image = image
            current_img_index[0] = index
        except:
            main_image_label.configure(text="Image not found", text_color="red")

    def prev_image():
        if current_img_index[0] > 0:
            show_image_by_index(current_img_index[0] - 1)

    def next_image():
        if current_img_index[0] < len(car_data["images"]) - 1:
            show_image_by_index(current_img_index[0] + 1)

    ctk.CTkButton(main_image_frame, text="◀", width=30, command=prev_image).place(x=10, y=240)
    ctk.CTkButton(main_image_frame, text="▶", width=30, command=next_image).place(x=280, y=240)

    # Initial image
    show_image_by_index(0)



    def update_main_image(image_path):
        try:
            image = load_iconctk(image_path, (300, 220))
            main_image_label.configure(image=image)
            main_image_label.image = image  # keep reference
        except:
            main_image_label.configure(text="Image not found", text_color="red")

    # Set first image
    if car_data.get("images"):
        update_main_image(car_data["images"][0])
    else:
        main_image_label.configure(text="No images", text_color="red")

    # === Thumbnails Row ===
    thumbnail_frame = ctk.CTkScrollableFrame(table_frame, width=300, height=70, fg_color="#f8f8f8", corner_radius=8,
                                         border_color="#aaaaaa", border_width=1, orientation="horizontal",
                                         scrollbar_button_color="#d9d9d9", scrollbar_button_hover_color="#555555")
    thumbnail_frame.place(x=10, y=290)  # Moved up slightly to close the visual gap
    thumbnail_frame._scrollbar.grid_configure(pady=2)


    for idx, img_path in enumerate(car_data.get("images", [])):
        thumb = load_iconctk(img_path, (65, 55))
        thumb_btn = ctk.CTkLabel(thumbnail_frame, image=thumb, text="", cursor="hand2")
        thumb_btn.image = thumb
        thumb_btn.grid(row=0, column=idx, padx=5, pady=3)
        thumb_btn.bind("<Button-1>", lambda e, path=img_path: update_main_image(path))


    # ===== RIGHT SIDE: Car Details =====
    right_frame = ctk.CTkFrame(table_frame, width=330, height=400, fg_color="white")
    right_frame.place(x=360, y=10)

    # === Title
    ctk.CTkLabel(right_frame, text=f"{car_data['make'].title()} {car_data['model'].title()} {car_data['year']}", font=("Lato", 20, "bold"), text_color="black").place(x=5, y=5)

    # Car ID top-right
    icon_id = load_iconctk("icons/id.png", (20, 20))
    ctk.CTkLabel(right_frame, image=icon_id, text=f"  {car_data['car_id']}", font=("Lato", 12), compound="left", text_color="#808080").place(x=275, y=10)

    # === Price
    ctk.CTkLabel(right_frame, text=f"${car_data['price']:,.0f}", font=("Lato", 22, "bold"), text_color="#2f8f4e").place(x=5, y=35)

    # === Basic Info Block (make, model, etc.)
    y_start = 70
    spacing = 25
    info_fields = [
        ("Make", car_data["make"]),
        ("Model", car_data["model"]),
        ("Year", str(car_data["year"])),
        ("VIN", car_data["vin"]),
        ("Condition", car_data["car_condition"]),
        ("Title", car_data["title_status"]),
        ("Drivetrain", car_data["drivetrain"])
    ]
    for i, (label, value) in enumerate(info_fields):
        ctk.CTkLabel(right_frame, text=f"{label}: {value}", font=("Lato", 13)).place(x=5, y=y_start + i * spacing)

    # === Icon Stats: mileage, economy, color, etc.
    y_icon = y_start
    icon_fields = [
        ("icons/odometer.png", f"{car_data['mileage']} mi."),
        ("icons/fuel_economy.png", f"{car_data['economy']} mi/g"),
        ("icons/color_icon.png", car_data["color"]),
        ("icons/transmission_icon.png", car_data["transmission"]),
        ("icons/fuel_icon.png", car_data["fuel_type"])
    ]
    for i, (icon_path, text) in enumerate(icon_fields):
        icon = load_iconctk(icon_path, (15, 15))
        ctk.CTkLabel(right_frame, image=icon, text=f"  {text}", compound="left", font=("Lato", 12)).place(x=190, y=y_icon + i * 23)

    # === Description
    desc_y = y_icon + 5 * 23 + 70  # push it down a bit
    ctk.CTkLabel(right_frame, text="Description:", font=("Lato", 13, "bold")).place(x=5, y=desc_y)
    

    desc_scroll = ctk.CTkScrollableFrame(right_frame, width=310, height=80, fg_color="#ffffff")
    desc_scroll.place(x=5, y=desc_y + 20)

    desc_label = ctk.CTkLabel(desc_scroll, text=car_data.get("description", ""), font=("Lato", 12),
                            wraplength=290, justify="left")
    desc_label.pack(anchor="w", padx=2, pady=2)


    # === Buttons under image on left side ===
    btn_test_drive = ctk.CTkButton(table_frame, text="Book a Test Drive", width=145, height=32,command=handle_book_test_drive,
                                font=("Lato", 12, "bold"), fg_color="#20b2aa", corner_radius=8)
    btn_test_drive.place(x=25, y=420)

    btn_inquiry = ctk.CTkButton(table_frame, text="Inquiry?", width=145, height=32, command=open_inquiry_popup,
                                font=("Lato", 12, "bold"), fg_color="#20b2aa", corner_radius=8)
    btn_inquiry.place(x=180, y=420)

    if role in ["admin", "staff"]:
        from manage_testdrives import open_manage_test_drives
        from manage_inquiries import open_manage_inquiries
        ctk.CTkButton( table_frame, text="Show Test Drives", width=145, height=32, fg_color="#20b2aa", 
                      command=lambda: open_manage_test_drives(root, parent_frame, car_id) ).place(x=25, y=420)

        ctk.CTkButton( table_frame, text="Show Inquiries", width=145, height=32, fg_color="#20b2aa", 
                  command=lambda: open_manage_inquiries(root, parent_frame, car_id) ).place(x=180, y=420)

    else:
        btn_test_drive.place(x=25, y=420)
        btn_inquiry.place(x=180, y=420)