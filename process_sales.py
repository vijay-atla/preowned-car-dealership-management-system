# process_sales.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils import load_background, load_iconctk, show_custom_message
from session import current_user
import re
from custom_toggle import ToggleSwitch
from database_utils import insert_customer_and_sale, generate_invoice_number
from fetch_registered_customers import open_fetch_customers_popup
from fetch_available_cars import open_fetch_cars_popup
import subprocess, os
from generate_invoice_pdf import generate_invoice_pdf
from generate_invoice import generate_invoice



def open_process_sales(root, parent_frame):

    global selected_customer_id 

    edit_icon = load_iconctk("icons/edit_icon.png",(25,25))
    color_icon = load_iconctk("icons/color_icon.png",(13,13))
    transmission_icon = load_iconctk("icons/transmission_icon.png",(13,13))
    fuel_icon = load_iconctk("icons/fuel_icon.png",(13,13))
    id_icon = load_iconctk("icons/id.png",(18,18))

    # Clear existing widgets from parent_frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    def validate_customer_fields():
        customer_error_label.configure(text="")

        first_name = entry_refs["First Name"].get().strip()
        last_name = entry_refs["Last Name"].get().strip()
        email = entry_refs["Email"].get().strip()
        phone = entry_refs["Phone Number"].get().strip()
        id_type = entry_refs["ID Type"].get().strip()
        custom_id_type = custom_id_type_entry.get().strip() if id_type == "Other" else ""
        id_number = entry_refs["ID Number"].get().strip()
        address = entry_refs["Address"].get("1.0", "end").strip()


        # First Name Validation
        if not first_name:
            customer_error_label.configure(text="⚠️ Please enter First Name.")
            return False
        elif not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", first_name):
            customer_error_label.configure(text="⚠️ First Name can only contain letters and spaces.")
            return False
        elif len(first_name.replace(" ", "")) < 3:
            customer_error_label.configure(text="⚠️ First Name must be at least 3 letters (excluding spaces).")
            return False
        # Last Name Validation
        if not last_name:
            customer_error_label.configure(text="⚠️ Please enter Last Name.")
            return False
        elif not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", last_name):
            customer_error_label.configure(text="⚠️ Last Name can only contain letters and spaces.")
            return False
        elif len(last_name.replace(" ", "")) < 3:
            customer_error_label.configure(text="⚠️ Last Name must be at least 3 letters (excluding spaces).")
            return False
        
        # Email Validation
        if not email:
            customer_error_label.configure(text="⚠️ Please enter Email.")
            return False
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            customer_error_label.configure(text="⚠️ Invalid Email format.")
            return False
        # Phone Number Validation
        if not phone:
            customer_error_label.configure(text="⚠️ Please enter Phone Number.")
            return False
        elif not phone.isdigit() or len(phone) != 10:
            customer_error_label.configure(text="⚠️ Phone Number must be exactly 10 digits.")
            return False
        # ID Type Validation
        if id_type == "Select":
            customer_error_label.configure(text="⚠️ Please select an ID Type.")
            return False
        if id_type == "Other" and not custom_id_type:
            customer_error_label.configure(text="⚠️ Please enter Custom ID Type.")
            return False
        if id_type == "Other" and not custom_id_type:
            customer_error_label.configure(text="⚠️ Please enter custom ID Type.")
            return False
        # ID Number Validation
        if not id_number:
            customer_error_label.configure(text="⚠️ Please enter ID Number.")
            return False
        # Address Validation
        if not address:
            customer_error_label.configure(text="⚠️ Please enter Address.")
            return False
        elif len(address) < 10:
            customer_error_label.configure(text="⚠️ Address must be at least 5 characters.")
            return False


        return True # ✅ All customer fields validated
    
    def validate_car_fields():
        car_error_label.configure(text="")

        car_id = entry_refs["Car ID"].get().strip()
        if not car_id:
            car_error_label.configure(text="⚠️ Please enter Car ID.")
            return False

        return True
    
    def validate_payment_fields():
        payment_error_label.configure(text="")

        try:
            listing_price = float(entry_refs["Listing Price ($)"].get().strip())
            discount = float(entry_refs["Discount ($)"].get().strip()) if entry_refs["Discount ($)"].get().strip() else 0.0
            tax_percent = float(entry_refs["Tax %"].get().strip()) if entry_refs["Tax %"].get().strip() else 0.0
            tax_amount = float(entry_refs["Tax Amount ($)"].get().strip())
        except ValueError:
            payment_error_label.configure(text="⚠️ Please Enter all Valid Details")
            return False

        payment_method = entry_refs["Payment Method"].get().strip()
        custom_payment_method = custom_payment_method_entry.get().strip() if payment_method == "Other" else ""
        payment_ref = entry_refs["Payment Reference"].get().strip()

        if listing_price <= 0:
            payment_error_label.configure(text="⚠️ Listing Price must be greater than 0.")
            return False
        if discount < 0:
            payment_error_label.configure(text="⚠️ Discount cannot be negative.")
            return False
        if discount > listing_price:
            payment_error_label.configure(text="⚠️ Discount cannot exceed Listing Price.")
            return False
        if tax_percent < 0 or tax_percent > 100:
            payment_error_label.configure(text="⚠️ Tax % must be between 0 and 100.")
            return False
        if payment_method == "Select":
            payment_error_label.configure(text="⚠️ Please select a Payment Method.")
            return False
        if payment_method == "Other" and not custom_payment_method:
            payment_error_label.configure(text="⚠️ Please enter custom Payment Method.")
            return False
        if not payment_ref:
            payment_error_label.configure(text="⚠️ Please enter Payment Reference.")
            return False

        return True




    def on_customer_type_change():
        if customer_toggle.get() == 1:  # Registered
            fetch_button.grid()
        else:
            fetch_button.grid_remove()
            for key in ["First Name", "Last Name", "Email", "Phone Number", "ID Type", "ID Number"]:
                widget = entry_refs[key]
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("Select")


    def on_id_type_change():
        selected = entry_refs["ID Type"].get()
        if selected == "Other":
            custom_id_type_entry.grid()
        else:
            custom_id_type_entry.grid_remove()
        validate_customer_fields()  # <-- add this!

    def on_payment_method_change():
        selected = entry_refs["Payment Method"].get()
        if selected == "Other":
            custom_payment_method_entry.grid()
        else:
            custom_payment_method_entry.grid_remove()
        validate_payment_fields()  # <-- add this!

    def fetch_available_car():
        def fill_selected_car(car):
            entry_refs["Car ID"].configure(state="normal")
            entry_refs["Car ID"].delete(0, "end")
            entry_refs["Car ID"].insert(0, car["car_id"])
            entry_refs["Car ID"].configure(state="readonly")


            car_name_label.configure(text=f"Car Name: {car['make']} {car['model']} {car['year']}")
            car_vin_label.configure(text=f"VIN: {car['vin']}")
            car_price_label.configure(text=f"Price: ${car['price']}")
            car_color_label.configure(text=f"  {car['car_color']}")
            car_mileage_label.configure(text=f"  {car['fuel_type']}")
            car_transmission_label.configure(text=f"  {car['transmission']}")


            # Auto-fill Listing Price field
            entry_refs["Listing Price ($)"].delete(0, "end")
            entry_refs["Listing Price ($)"].insert(0, car["price"])

            # Load and show Main Image
            try:
                car_image_path = car["img"]  # Assuming you store path or you retrieve from DB
                car_image = load_iconctk(car_image_path, (150, 120))
                car_image_label.configure(image=car_image)
                car_image_label.image = car_image  # keep a reference
            except:
                car_image_label.configure(image=None)
                car_image_label.configure(text="No Image")
        open_fetch_cars_popup(root, callback_on_select=fill_selected_car)


    def fetch_registered_customer():
        def fill_selected_customer(cust):
            global selected_customer_id
            selected_customer_id = cust["user_id"]

            entry_refs["First Name"].delete(0, "end")
            entry_refs["First Name"].insert(0, cust["first_name"])

            entry_refs["Last Name"].delete(0, "end")
            entry_refs["Last Name"].insert(0, cust["last_name"])

            entry_refs["Email"].delete(0, "end")
            entry_refs["Email"].insert(0, cust["email"])

            entry_refs["Phone Number"].delete(0, "end")
            entry_refs["Phone Number"].insert(0, cust["phone"])

        open_fetch_customers_popup(root, callback_on_select=fill_selected_customer)

    def on_tax_or_price_change(event=None):
        try:
            price = float(entry_refs["Listing Price ($)"].get().strip())
            discount = float(entry_refs["Discount ($)"].get().strip()) if entry_refs["Discount ($)"].get().strip() else 0.0
            tax_percent = float(entry_refs["Tax %"].get().strip())

            taxable_amount = max(0, price - discount)
            tax_amount = round(taxable_amount * (tax_percent / 100), 0)

            entry_refs["Tax Amount ($)"].configure(state="normal")
            entry_refs["Tax Amount ($)"].delete(0, "end")
            entry_refs["Tax Amount ($)"].insert(0, str(tax_amount))
            entry_refs["Tax Amount ($)"].configure(state="readonly")
            total_price = max(0, price - discount) + tax_amount
            entry_refs["Total Price ($)"].configure(state="normal")
            entry_refs["Total Price ($)"].delete(0, "end")
            entry_refs["Total Price ($)"].insert(0, str(round(total_price, 0)))
            entry_refs["Total Price ($)"].configure(font=("Lato", 14, "bold"))
            entry_refs["Total Price ($)"].configure(state="readonly")

        except:
            entry_refs["Tax Amount ($)"].configure(state="normal")
            entry_refs["Tax Amount ($)"].delete(0, "end")
            entry_refs["Tax Amount ($)"].configure(state="readonly")


    # Background illustration (optional)
    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.2)
    illustration_label_right = ctk.CTkLabel(parent_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)

    # Welcome Message
    ctk.CTkLabel(parent_frame,  image=load_iconctk("icons/process_sale_icon.png", (60, 60)), 
                 text="  Process Sale", font=("Lato", 30, "bold"), text_color="#008080", 
                 fg_color="#ffffff", compound="left").place(x=25, y=45)

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    # === Table Frame ===
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=480, 
                               fg_color="#ffffff", corner_radius=10, 
                               border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # === Scrollable Area Inside Table Frame ===
    scrollable_frame = ctk.CTkScrollableFrame(table_frame, width=655, height=450, 
                                              fg_color="white", corner_radius=10,
                                              scrollbar_button_color="#d9d9d9", 
                                              scrollbar_button_hover_color="#666666")
    scrollable_frame.grid(row=0, column=0, padx=5, pady=10)

    # === Form Fields with Section Headers ===
    entry_refs = {}
    row_counter = 0

    
    # -------------------- Customer Section --------------------
    customer_section_label = ctk.CTkLabel(scrollable_frame, text="🔹 Customer Information", 
                                          font=("Lato", 17, "bold"), text_color="#008080")
    customer_section_label.grid(row=row_counter, column=0, columnspan=2, sticky="w", padx=37, pady=(10, 0))
    row_counter += 1

    customer_error_label = ctk.CTkLabel(scrollable_frame, text="", text_color="red", font=("Lato", 14))
    customer_error_label.grid(row=row_counter, column=0, columnspan=2, padx=125, pady=(0, 0), sticky="w")
    row_counter += 1

    # --- Customer Type Toggle ---
    ctk.CTkLabel(scrollable_frame, text="Customer Type", font=("Lato", 15)).grid(row=row_counter, column=0, padx=37, pady=(10, 0), sticky="w")

    customer_toggle = ToggleSwitch(scrollable_frame, width=100, height=35,
                                    on_text="Registered", off_text="Walk-in",
                                    on_color="#a855f7", off_color="#e5e7eb",
                                    command=lambda: on_customer_type_change())
    customer_toggle.set(False)  # Start as "Walk-in"
    customer_toggle.grid(row=row_counter + 1, column=0, padx=37, pady=(0, 10), sticky="w")

    # --- Fetch Button (hidden by default)
    fetch_button = ctk.CTkButton(scrollable_frame, text="Fetch Customer", width=80, font=("Lato", 13), height=30,
                                fg_color="#a855f7", text_color="black", corner_radius=8,
                                hover_color="#74c2f3", command=lambda: fetch_registered_customer())
    fetch_button.grid(row=row_counter + 1, column=1, padx=37, pady=(0, 10), sticky="w")
    fetch_button.grid_remove()  # Hide by default

    row_counter += 2


    customer_fields = [
        ("First Name", "Last Name"),
        ("Email", "Phone Number"),
        ("ID Type", ""),
        ("ID Number", "Address")
    ]

    dropdowns = {
        # "Customer Type": ["Registered", "Walk-in"],
        "Payment Method": ["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Check", "Other"],
        "ID Type": ["Driver's License", "Passport", "National ID", "Other"]
    }

    for left_label, right_label in customer_fields:
        for col_idx, field in enumerate([left_label, right_label]):
            if not field:
                continue

            label = ctk.CTkLabel(scrollable_frame, text=field, font=("Lato", 15))
            label.grid(row=row_counter, column=col_idx, padx=37, pady=(10, 0), sticky="w")

            if field in dropdowns:
                if field == "ID Type":
                    entry = ctk.CTkComboBox(scrollable_frame, values=dropdowns[field], width=250, height=35,
                                            border_color="#b4b4b4", fg_color="#d9d9d9",
                                            command=lambda _: on_id_type_change())
                    entry.set("Select")
                else:
                    entry = ctk.CTkComboBox(scrollable_frame, values=dropdowns[field], width=250, height=35,
                                            border_color="#b4b4b4", fg_color="#d9d9d9")
                    entry.set("Select")

            else:
                if field == "Address":
                    entry = ctk.CTkTextbox(scrollable_frame, width=250, height=70, border_width=2,
                                        border_color="#b4b4b4", fg_color="#d9d9d9",
                                        corner_radius=6, wrap="word")
                else:
                    entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                        border_color="#b4b4b4", fg_color="#d9d9d9")
                if field in ["First Name", "Last Name", "Email", "Phone Number", "ID Number", "Address"]:
                    entry.bind("<KeyRelease>", lambda e: validate_customer_fields())
                    

            entry.grid(row=row_counter + 1, column=col_idx, padx=37, pady=(0, 10), sticky="w")
            entry_refs[field] = entry
            if field == "ID Type":
                global custom_id_type_entry  # Make it accessible inside submit logic if needed
                custom_id_type_entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                                    border_color="#b4b4b4", fg_color="#d9d9d9",
                                                    placeholder_text="Enter custom ID type...")
                custom_id_type_entry.grid(row=row_counter + 1, column=1, padx=37, pady=(0, 10), sticky="w")
                custom_id_type_entry.grid_remove()
        row_counter += 2

    # -------------------- Car Section --------------------
    car_section_label = ctk.CTkLabel(scrollable_frame, text="🔹 Car Information", 
                                     font=("Lato", 17, "bold"), text_color="#008080")
    car_section_label.grid(row=row_counter, column=0, columnspan=2, sticky="w", padx=37, pady=(40, 0))
    row_counter += 1

    car_error_label = ctk.CTkLabel(scrollable_frame, text="", text_color="red", font=("Lato", 14))
    car_error_label.grid(row=row_counter, column=0, columnspan=2, padx=125, pady=(0, 0), sticky="w")
    row_counter += 1

    fetch_car_button = ctk.CTkButton(scrollable_frame, text="Fetch Car", width=100, font=("Lato", 14), height=30,
                                 fg_color="#a855f7", text_color="black", corner_radius=8, border_color="#808080", border_width=1,
                                 hover_color="#74c2f3", command=lambda: fetch_available_car())
    fetch_car_button.grid(row=row_counter + 1, column=1, padx=37, pady=(0, 10), sticky="w")


    car_fields = [
        ("Car ID", "")
    ]

    for left_label, right_label in car_fields:
        for col_idx, field in enumerate([left_label, right_label]):
            if not field:
                continue

            label = ctk.CTkLabel(scrollable_frame, text=field, font=("Lato", 15))
            label.grid(row=row_counter, column=col_idx, padx=37, pady=(10, 0), sticky="w")

            entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                 border_color="#b4b4b4", fg_color="#d9d9d9", state="readonly")
            if field in ["Car ID"]:
                entry.bind("<KeyRelease>", lambda e: validate_car_fields())

            entry.grid(row=row_counter + 1, column=col_idx, padx=37, pady=(0, 10), sticky="w")
            entry_refs[field] = entry
        row_counter += 2

    # Car Preview Frame
    car_preview_frame = ctk.CTkFrame(scrollable_frame, width=550, height=150, fg_color="#f4f4f4", corner_radius=10, border_color="#808080", border_width=1)
    car_preview_frame.grid(row=row_counter, column=0, columnspan=2, padx=37, pady=(10, 10), sticky="w")
    row_counter += 1


    # Inside car_preview_frame
    content_frame = ctk.CTkFrame(car_preview_frame, fg_color="transparent", width=550, height=150)
    content_frame.pack(fill="both", expand=True, padx=(5,5), pady=10)

    # Inside car_preview_frame
    car_image_label = ctk.CTkLabel(content_frame, text="", width=140, height=120, corner_radius=10, fg_color="transparent")
    car_image_label.place(x=5, y=15)

    car_name_label = ctk.CTkLabel(content_frame, text="Car Name: -", font=("Lato", 18))
    car_name_label.place(x=180, y=10)

    car_vin_label = ctk.CTkLabel(content_frame, text="VIN: -", font=("Lato", 13))
    car_vin_label.place(x=180, y=90)

    car_price_label = ctk.CTkLabel(content_frame, text="Price: -", font=("Lato", 13))
    car_price_label.place(x=180, y=120)

    car_color_label = ctk.CTkLabel(content_frame, image=color_icon, text=f" ", font=("Lato", 13), compound="left")
    car_color_label.place(x=400, y=60)

    car_mileage_label = ctk.CTkLabel(content_frame, image=fuel_icon, text=f" ", font=("Lato", 13), compound="left")
    car_mileage_label.place(x=400, y=90)

    car_transmission_label = ctk.CTkLabel(content_frame, image=transmission_icon, text=" ", font=("Lato", 13), compound="left")
    car_transmission_label.place(x=400, y=120)

    




    # -------------------- Payment Section --------------------
    payment_section_label = ctk.CTkLabel(scrollable_frame, text="🔹 Payment Information", 
                                         font=("Lato", 17, "bold"), text_color="#008080")
    payment_section_label.grid(row=row_counter, column=0, columnspan=2, sticky="w", padx=37, pady=(40, 0))
    row_counter += 1

    payment_error_label = ctk.CTkLabel(scrollable_frame, text="", text_color="red", font=("Lato", 14))
    payment_error_label.grid(row=row_counter, column=0, columnspan=2, padx=125, pady=(0, 0), sticky="w")
    row_counter += 1

    payment_fields = [
        ("Listing Price ($)", "Discount ($)"),
        ("Tax %", "Tax Amount ($)"),
        ("Total Price ($)", "Payment Method"),
        ("Payment Reference", "")
    ]

    for left_label, right_label in payment_fields:
        for col_idx, field in enumerate([left_label, right_label]):
            if not field:
                continue

            label = ctk.CTkLabel(scrollable_frame, text=field, font=("Lato", 15))
            label.grid(row=row_counter, column=col_idx, padx=37, pady=(10, 0), sticky="w")

            if field in dropdowns:
                if field == "Payment Method":
                    entry = ctk.CTkComboBox(scrollable_frame, values=dropdowns[field], width=250, height=35,
                                            border_color="#b4b4b4", fg_color="#d9d9d9",
                                            command=lambda _: on_payment_method_change())
                    entry.set("Select")
                else:
                    if field == "Total Price ($)":
                        entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                            border_color="#b4b4b4", fg_color="#d9d9d9",
                                            state="readonly")
                    else:
                        entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                            border_color="#b4b4b4", fg_color="#d9d9d9")

            else:
                entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                     border_color="#b4b4b4", fg_color="#d9d9d9")
                if field in ["Listing Price ($)", "Discount ($)", "Tax Amount ($)", "Tax %", "Payment Reference"]:
                    entry.bind("<KeyRelease>", lambda e: validate_payment_fields())
                    
                    if field in ["Listing Price ($)", "Tax %"]:
                        entry.bind("<KeyRelease>", on_tax_or_price_change)


            entry.grid(row=row_counter + 1, column=col_idx, padx=37, pady=(0, 10), sticky="w")
            entry_refs[field] = entry
            if field == "Payment Method":
                global custom_payment_method_entry
                custom_payment_method_entry = ctk.CTkEntry(scrollable_frame, width=250, height=35,
                                                        border_color="#b4b4b4", fg_color="#d9d9d9",
                                                        placeholder_text="Enter other payment method...")
                custom_payment_method_entry.grid(row=row_counter + 2, column=1, padx=37, pady=(0, 10), sticky="w")
                custom_payment_method_entry.grid_remove()

        row_counter += 2

    # === Buttons Row (Submit, Reset, Cancel) ===
    submit_error_label = ctk.CTkLabel(scrollable_frame, text="", text_color="red", font=("Lato", 14))
    submit_error_label.grid(row=row_counter, column=0, columnspan=2, padx=125, pady=(5, 5), sticky="w")
    row_counter += 1
 

    button_row = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    button_row.grid(row=row_counter, column=0, columnspan=2, pady=30)

    def show_sale_summary(invoice_number, customer_name, car_id, total_price):
        popup = tk.Toplevel(root)
        popup.title("Sale Completed")
        popup.geometry("550x650")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.lift()

        # Main Heading
        ctk.CTkLabel(popup, text="✅ Sale Summary", font=("Lato", 24, "bold")).pack(pady=(15, 10))
        # Sale Details
        ctk.CTkLabel(popup, text=f"Invoice Number: {invoice_number}", font=("Lato", 16)).pack(pady=(5, 5))
        ctk.CTkLabel(popup, text=f"Customer: {customer_name.title()}", font=("Lato", 16)).pack(pady=(5, 5))
        ctk.CTkLabel(popup, text=f"Car ID: {car_id}", font=("Lato", 16)).pack(pady=(5, 5))
        ctk.CTkLabel(popup, text=f"Total Price: ${float(total_price):,.2f}", font=("Lato", 16)).pack(pady=(5, 15))

        def download_invoice():
            try:
                pdf_path = generate_invoice(invoice_number)
                if pdf_path:
                    show_custom_message("Invoice Downloaded", f"Invoice #{invoice_number} saved to your Downloads folder!")

                    # Auto-open the downloaded PDF
                    if os.name == 'nt':  # Windows
                        os.startfile(pdf_path)
                    elif os.name == 'posix':  # macOS/Linux
                        subprocess.Popen(['open', pdf_path])
                    else:
                        subprocess.Popen(['xdg-open', pdf_path])
                else:
                    show_custom_message("Download Failed", "Invoice not found!")
            except Exception as e:
                show_custom_message("Error", f"Failed to download invoice:\n{str(e)}")

        def close_and_redirect():
            from admin_dashboard import open_admin_dashboard_main_frame
            popup.destroy()
            open_admin_dashboard_main_frame(root)

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
        buttons_frame.pack(pady=(10, 20))

        # Download Invoice Button
        download_btn = ctk.CTkButton(buttons_frame, text="Download Invoice PDF", command=download_invoice, 
                                    fg_color="#17b8a6", hover_color="#139e91", text_color="white", width=180)
        download_btn.grid(row=0, column=0, padx=10, pady=10)

        # Ok Button
        ok_btn = ctk.CTkButton(buttons_frame, text="Ok", command=close_and_redirect, 
                            fg_color="#0f9bff", hover_color="#0b7fc7", text_color="white", width=100)
        ok_btn.grid(row=0, column=1, padx=10, pady=10)


    def reset_sale_form():
        for key, field in entry_refs.items():
            custom_id_type_entry.delete(0, "end")
            custom_id_type_entry.grid_remove()

            custom_payment_method_entry.delete(0, "end")
            custom_payment_method_entry.grid_remove()

            
            if isinstance(field, ctk.CTkEntry):
                field.delete(0, "end")
            elif isinstance(field, ctk.CTkComboBox):
                field.set("Select")

    def cancel_sale_form():
        try:
            for widget in parent_frame.winfo_children():
                widget.destroy()

            if current_user["role"] == "admin":
                from admin_dashboard import open_admin_dashboard_main_frame
                open_admin_dashboard_main_frame(root)
            else:
                messagebox.showerror("Error", f"Unrecognized role: {current_user["role"]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return to dashboard.\n{e}")

    def submit_sale_form():
        submit_error_label.configure(text="")  # Clear previous submit errors

        is_customer_valid = validate_customer_fields()
        is_car_valid = validate_car_fields()
        is_payment_valid = validate_payment_fields()

        if not (is_customer_valid and is_car_valid and is_payment_valid):
            submit_error_label.configure(text="⚠️ Please fix the errors highlighted above before submitting.")
        try:
            # Gather Form Values
            car_id = entry_refs["Car ID"].get().strip()
            customer_first_name = entry_refs["First Name"].get().strip().upper()
            customer_last_name = entry_refs["Last Name"].get().strip().upper()
            customer_email = entry_refs["Email"].get().strip().lower()
            customer_phone = entry_refs["Phone Number"].get().strip()
            id_type = entry_refs["ID Type"].get().strip().title()  
            if id_type == "Other":
                id_type = custom_id_type_entry.get().strip().title()  
            id_number = entry_refs["ID Number"].get().strip().upper()
            address = entry_refs["Address"].get("1.0", "end").strip().title()  
            listing_price = float(entry_refs["Listing Price ($)"].get().strip())
            discount = float(entry_refs["Discount ($)"].get().strip()) if entry_refs["Discount ($)"].get().strip() else 0.0
            tax_percent = float(entry_refs["Tax %"].get().strip()) if entry_refs["Tax %"].get().strip() else 0.0
            tax_amount = float(entry_refs["Tax Amount ($)"].get().strip())
            total_price = float(entry_refs["Total Price ($)"].get().strip())
            payment_method = entry_refs["Payment Method"].get().strip().title()  
            if payment_method == "Other":
                payment_method = custom_payment_method_entry.get().strip().title()  
            payment_reference = entry_refs["Payment Reference"].get().strip().upper()
            staff_id = current_user["user_id"]

            # Customer Type
            customer_type_value = customer_toggle.get()  # 1 = Registered, 0 = Walk-in

            # Step 1: Generate Invoice Number
            invoice_number = generate_invoice_number()
            if not invoice_number:
                messagebox.showerror("Error", "Failed to generate invoice number.")
                return
            invoice_number = invoice_number.upper()  # <-- Force Uppercase

            global selected_customer_id
            # Step 2: Prepare Data for DB Insert
            if customer_type_value == 1:  # Registered
                # Assume selected_customer_id is globally set after Fetch
                if selected_customer_id is None:
                    messagebox.showerror("Error", "Please fetch a registered customer first!")
                    return
                customer_id = selected_customer_id

            else:  # Walk-in
                customer_id = None  # Walk-in will be created inside DB transaction

            user_data = {
                "first_name": customer_first_name,
                "last_name": customer_last_name,
                "email": customer_email,
                "phone": customer_phone
            }

            sale_data = {
                "invoice_number": invoice_number,
                "car_id": car_id,
                "customer_first_name": customer_first_name,
                "customer_last_name": customer_last_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "id_type": id_type,
                "id_number": id_number,
                "address": address,
                "listing_price": listing_price,
                "discount": discount,
                "tax_percent": tax_percent,
                "tax_amount": tax_amount,
                "total_price": total_price,
                "payment_method": payment_method,
                "payment_reference": payment_reference,
                "staff_id": staff_id
            }

            # Step 3: Insert Customer (if needed) + Insert Sale
            success, result = insert_customer_and_sale(customer_id, user_data, sale_data)

            if success:
                show_sale_summary(invoice_number, f"{customer_first_name} {customer_last_name}", car_id, total_price)
            else:
                messagebox.showerror("Error", f"Failed to process sale.\n{result}")

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error occurred.\n{str(e)}")


    

    # Cancel Button (Red)
    ctk.CTkButton(button_row, text="Cancel", width=120, fg_color="#f05f5f", font=("Lato", 16, "bold"),
                  text_color="black", hover_color="#f77474", border_color="#b4b4b4",
                  command=cancel_sale_form).grid(row=0, column=0, padx=(37, 45))

    # Reset Button (Light Green)
    ctk.CTkButton(button_row, text="Reset", width=120, fg_color="#d7f58a", font=("Lato", 16, "bold"),
                  text_color="black", border_color="#b4b4b4", hover_color="#cff06a",
                  command=reset_sale_form).grid(row=0, column=1, padx=45)

    # Submit Button (Teal)
    ctk.CTkButton(button_row, text="Submit", width=120, fg_color="#17b8a6", font=("Lato", 16, "bold"),
                  text_color="black", border_color="#b4b4b4", hover_color="#17B8A6",
                  command=submit_sale_form).grid(row=0, column=2, padx=45)