import customtkinter as ctk
import tkinter as tk
from utils import load_background, load_iconctk
import re
from datetime import datetime
from database_utils import get_customers, hash_password, user_exists, insert_customer, update_customer_db  # reused functions
from validators import is_valid_phone, is_valid_email, is_valid_first_name ,is_valid_last_name
from session import current_user


def open_manage_customers(root, parent_frame):
    search_debounce_timer = [None]

    def format_timestamp(dt_obj):
        try:
            return dt_obj.strftime("%B %d, %Y  %I:%M %p")
        except:
            return str(dt_obj)

    def open_add_customer_popup():
        popup = ctk.CTkToplevel(root)
        popup.geometry("500x480")
        popup.title("Add New Customer")
        popup.configure(fg_color="#E5F9F9")
        popup.attributes("-topmost", True)
        popup.lift()

        popup.update_idletasks()
        x = parent_frame.winfo_rootx() + 125
        y = parent_frame.winfo_rooty() + 50
        popup.geometry(f"500x480+{x}+{y}")

        ctk.CTkLabel(popup, text="Add New Customer", font=("Lato", 22, "bold")).place(x=140, y=20)

        y_pos = 70
        spacing = 50
        field_data = {}

        def create_entry(label, key):
            nonlocal y_pos
            ctk.CTkLabel(popup, text=f"{label}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
            entry = ctk.CTkEntry(popup, width=280, height=30)
            entry.place(x=150, y=y_pos)
            field_data[key] = entry

            if key in ["first_name", "last_name"]:
                entry.bind("<KeyRelease>", lambda e: validate_name(entry, popup))
            elif key == "email":
                entry.bind("<KeyRelease>", lambda e: validate_email(entry, popup))
            elif key == "phone":
                entry.bind("<KeyRelease>", lambda e: validate_phone(entry, popup))

            y_pos += spacing

        create_entry("First Name", "first_name")
        create_entry("Last Name", "last_name")
        create_entry("Email", "email")
        create_entry("Phone", "phone")

        ctk.CTkLabel(popup, text="Role:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
        role_label = ctk.CTkLabel(popup, text="Customer", font=("Lato", 14))
        role_label.place(x=150, y=y_pos)
        y_pos += spacing

        ctk.CTkLabel(popup, text="Status:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
        status_dropdown = ctk.CTkComboBox(popup, width=280, height=30, values=["Active", "Inactive"])
        status_dropdown.set("Active")
        status_dropdown.place(x=150, y=y_pos)

        success_label = ctk.CTkLabel(popup, text="", font=("Lato", 14, "bold"), text_color="#006600")

        def reset_form():
            for widget in field_data.values():
                widget.delete(0, "end")
            status_dropdown.set("Active")
            success_label.configure(text="")

        def add_customer():
            validate_name(field_data["first_name"], popup)
            validate_name(field_data["last_name"], popup)
            validate_email(field_data["email"], popup)
            validate_phone(field_data["phone"], popup)

            if error_labels:
                return

            data = {key: widget.get().strip() for key, widget in field_data.items()}
            data["status"] = 1 if status_dropdown.get() == "Active" else 0
            data["password"] = "Customer@123"
            data["first_name"] = data["first_name"].upper()
            data["last_name"] = data["last_name"].upper()
            data["email"] = data["email"].lower()

            exists, reason = user_exists(data["email"], data["phone"])
            if exists:
                show_error(field_data["email"], reason, popup) if "email" in reason else show_error(field_data["phone"], reason, popup)
                return

            password_hash = hash_password(data["password"])

            success, user_id = insert_customer(
                data["first_name"], data["last_name"], data["email"], data["phone"],
                password_hash, "Customer", data["status"]
            )

            if success:
                reset_form()
                show_success_popup(user_id)
            else:
                show_error(field_data["email"], user_id, popup)

        def show_success_popup(user_id):
            success_popup = ctk.CTkToplevel(popup)
            success_popup.geometry("350x150")
            success_popup.title("Success")
            success_popup.configure(fg_color="#E5F9F9")
            success_popup.lift()
            success_popup.attributes("-topmost", True)
            success_popup.after(100, lambda: success_popup.focus_force())

            success_popup.update_idletasks()
            x = parent_frame.winfo_rootx() + 175
            y = parent_frame.winfo_rooty() + 150
            success_popup.geometry(f"350x150+{x}+{y}")

            ctk.CTkLabel(success_popup, text="✅ Customer added successfully!", font=("Lato", 16, "bold"), text_color="#006600").place(x=50, y=30)
            ctk.CTkLabel(success_popup, text=f"🆔 Assigned Customer ID: {user_id}", font=("Lato", 14)).place(x=60, y=70)

            def close_both():
                success_popup.destroy()
                popup.destroy()
                load_customer_cards()

            ctk.CTkButton(success_popup, text="OK", fg_color="#30b8a9", text_color="black", command=close_both).place(x=130, y=110)

        ctk.CTkButton(popup, text="Back", width=100, fg_color="#d9534f", command=popup.destroy).place(x=50, y=420)
        ctk.CTkButton(popup, text="Reset", width=100, fg_color="#808080", command=reset_form).place(x=200, y=420)
        ctk.CTkButton(popup, text="Add Customer", width=120, fg_color="#30b8a9", command=add_customer).place(x=330, y=420)

    error_labels = {}
    def show_error(entry, msg, container):
        if entry in error_labels:
            error_labels[entry].configure(text=msg)
        else:
            label = ctk.CTkLabel(container, text=msg, text_color="red", font=("Lato", 13), bg_color="transparent")
            label.place(x=175, y=40)
            error_labels[entry] = label

    def clear_error(entry):
        if entry in error_labels:
            error_labels[entry].destroy()
            del error_labels[entry]

    def validate_name(entry, container):
        value = entry.get().strip()
        if not value.isalpha() or len(value) < 3:
            show_error(entry, "Must be 3+ alphabet letters", container)
        else:
            clear_error(entry)

    def validate_email(entry, container):
        value = entry.get().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            show_error(entry, "Invalid email", container)
        else:
            clear_error(entry)

    def validate_phone(entry, container):
        value = entry.get().strip()
        if not re.fullmatch(r"\d{10}", value):
            show_error(entry, "Must be 10-digit number", container)
        else:
            clear_error(entry)

    # UI layout placeholders...
    # Now build table_frame, search_bar, scrollable frame and cards like you do in manage_staff
    # But instead of `load_staff_cards()` you’ll use `load_customer_cards()`
    # And instead of `open_staff_details_popup()` you’ll make a `open_customer_details_popup(customer)` with non-editable role

    # 👇 Let me know if you want the remaining part (scrollable cards, filter, view/edit popup etc.)



    def open_customer_details_popup(customer):
        popup = ctk.CTkToplevel(root)
        popup.geometry("500x500")
        popup.title(f"Customer Details - {customer['name']}")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#f0f0f0")

        entries = {}
        edit_icons = {}
        y_pos = 60
        spacing = 50

        ctk.CTkLabel(popup, text="View / Edit Customer", font=("Lato", 22, "bold")).place(x=140, y=20)

        fields = ["First Name", "Last Name", "Email", "Phone", "Role", "Status"]
        values = {
            "First Name": customer["first_name"].title(),
            "Last Name": customer["last_name"].title(),
            "Email": customer["email"],
            "Phone": customer["phone"],
            "Role": "Customer",
            "Status": customer["status"]
        }

        for field in fields:
            ctk.CTkLabel(popup, text=f"{field}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)

            if field == "Status":
                entry = ctk.CTkComboBox(popup, values=["Active", "Inactive"], width=280, height=30)
                entry.set(values[field])
            elif field == "Role":
                entry = ctk.CTkEntry(popup, width=280)
                entry.insert(0, values[field])
                entry.configure(state="disabled", text_color="gray")
            else:
                entry = ctk.CTkEntry(popup, width=280)
                entry.insert(0, values[field])
                entry.configure(state="disabled", text_color="black")  # 🔐 Initially disabled

                # ✏️ Edit icon

                icon = ctk.CTkLabel(popup, image=load_iconctk("icons/edit_icon.png",(20,20)), text="", cursor="hand2", font=("Lato", 14))
                icon.place(x=440, y=y_pos)
                icon.bind("<Button-1>", lambda e, ent=entry, ic=icon: enable_edit(ent, ic))
                edit_icons[field] = icon

            entry.place(x=150, y=y_pos)
            entries[field] = entry
            y_pos += spacing

        def enable_edit(entry_widget, icon_label):
            entry_widget.configure(state="normal")
            entry_widget.focus()
            icon_label.place_forget()

        def live_validate(entry_widget, validator):
            def validate(_):
                value = entry_widget.get().strip()
                valid, msg = validator(value)
                if not valid:
                    show_error(entry_widget, msg, popup)
                else:
                    clear_error(entry_widget)
            return validate


        def update_customer():
            updated = { 
                "first_name": entries["First Name"].get().strip().upper(),
                "last_name": entries["Last Name"].get().strip().upper(),
                "email": entries["Email"].get().strip().lower(),
                "phone": entries["Phone"].get().strip(),
                "status": 1 if entries["Status"].get() == "Active" else 0
            }

            for field_key, validator in [
                ("First Name", is_valid_first_name),
                ("Last Name", is_valid_last_name),
                ("Email", is_valid_email),
                ("Phone", is_valid_phone),
            ]:
                value = entries[field_key].get().strip()
                valid, msg = validator(value)
                if not valid:
                    show_error(entries[field_key], msg, popup)
                    return

            success, msg = update_customer_db(user_id=customer["user_id"], **updated)

            # Re-fetch the same staff from DB to get updated timestamps
            latest = get_customers(str(customer["user_id"]))  # search by ID (as string)
            if latest:
                customer.update(latest[0])  # refresh the staff dictionary
            
            entries["First Name"].delete(0, tk.END)
            entries["First Name"].insert(0, customer["first_name"])

            entries["Last Name"].delete(0, tk.END)
            entries["Last Name"].insert(0, customer["last_name"])

            entries["Email"].delete(0, tk.END)
            entries["Email"].insert(0, customer["email"])

            entries["Phone"].delete(0, tk.END)
            entries["Phone"].insert(0, customer["phone"])

            entries["Status"].set("Active" if customer["status"] == 1 or customer["status"] == "Active" else "Inactive")


            if success:
                label.configure(text="✅ Customer updated successfully!")
                
                # Auto-hide after 2.5 seconds and close
                def finish_update():
                    label.place_forget()
                    popup.destroy()
                popup.after(2000, finish_update)
                # popup.after(2000, lambda: label.configure(text=""))
                load_customer_cards()
            else:
                show_error(entries["Email"], msg, popup)

        label = ctk.CTkLabel(popup, text="", font=("Lato", 14), text_color="green")
        label.place(x=130, y=250)


        readonly_fields = {
            "User Since": format_timestamp(customer.get("created_at")),
            "Last Updated": format_timestamp(customer.get("updated_at"))
        }

        for field, value in readonly_fields.items():
            ctk.CTkLabel(popup, text=f"{field}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
            display = ctk.CTkEntry(popup, width=280)
            display.insert(0, value)
            display.configure(state="disabled", text_color="gray")
            display.place(x=150, y=y_pos)
            y_pos += spacing


        update_btn = ctk.CTkButton(popup, text="Update", width=100, fg_color="#30b8a9", command=update_customer)
        update_btn.place(x=350, y=440)
        update_btn.place_forget()  # Initially hidden
        ctk.CTkButton(popup, text="Back", width=100, fg_color="#d9534f", command=popup.destroy).place(x=50, y=440)
        

        def show_update_btn(*args):
            update_btn.place(x=350, y=440)

        for field, entry in entries.items():
            if field not in ["Status", "Role"]:
                entry.bind("<KeyRelease>", show_update_btn)

                # 🔄 Live validators
                if field == "First Name":
                    entry.bind("<KeyRelease>", live_validate(entry, is_valid_first_name))
                elif field == "Last Name":
                    entry.bind("<KeyRelease>", live_validate(entry, is_valid_last_name))
                elif field == "Email":
                    entry.bind("<KeyRelease>", live_validate(entry, is_valid_email))
                elif field == "Phone":
                    entry.bind("<KeyRelease>", live_validate(entry, is_valid_phone))

        entries["Status"].bind("<<ComboboxSelected>>", show_update_btn)



    # === Parent Frame Cleanup & Background ===
    for widget in parent_frame.winfo_children():
        widget.destroy()

    illustration = load_background("icons/default_bg.png", (750, 525), 0.2)
    ctk.CTkLabel(parent_frame, image=illustration, text="").place(x=0, y=65)

    # Welcome Message
    ctk.CTkLabel(parent_frame,  image=load_iconctk("icons/manage_customer_icon.png", (60, 60)), text="  Manage Customer", 
                                font=("Lato", 30, "bold"), text_color="#008080", fg_color="#ffffff", compound="left").place(x=25, y=45)  
    
    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)


    # === Table Frame ===
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=480, fg_color="#ffffff",
                                corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # === Search and Filter Frame ===
    search_frame = ctk.CTkFrame(table_frame, width=660, height=40, fg_color="#bababa",
                                corner_radius=10, border_color="#808080", border_width=1)
    search_frame.place(x=15, y=10)

    search_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/search_icon.png", (25, 25)), text="")
    search_icon_label.place(x=10, y=7)

    search_var = tk.StringVar()
    search_box = ctk.CTkEntry(search_frame, placeholder_text="Search Customers...", corner_radius=20, width=250, textvariable=search_var)
    search_box.place(x=40, y=7)

    filter_var = tk.StringVar(value="All")
    status_filter = ctk.CTkComboBox(search_frame, values=["Active", "Inactive", "All"], width=90, height=25, variable=filter_var)
    status_filter.place(x=430, y=8)

    def on_filter_change_var(*args):
        load_customer_cards(search_text=search_var.get(), filter_text=filter_var.get())
    filter_var.trace_add("write", on_filter_change_var)

    def on_search_change(*args):
        if search_debounce_timer[0] is not None:
            root.after_cancel(search_debounce_timer[0])

        def delayed():
            load_customer_cards(search_text=search_var.get(), filter_text=filter_var.get())
        search_debounce_timer[0] = root.after(400, delayed)

    search_var.trace_add("write", on_search_change)

    # === Buttons ===
    ctk.CTkButton(search_frame, text="Go", width=37, height=23, fg_color="#30b8a9", text_color="black", command=on_filter_change_var).place(x=300, y=9)
    ctk.CTkLabel(search_frame, image=load_iconctk("icons/filter_icon.png", (20, 20)), text="  Status: ", compound="left", font=("Lato", 14)).place(x=360, y=7)
    ctk.CTkButton(search_frame, text="➕ Add Customer", fg_color="#30b8a9", font=("Lato", 13, "bold"),
                text_color="black", width=120, height=30, command=open_add_customer_popup).place(x=535, y=6)

    # === Scroll Area ===
    scroll_container = ctk.CTkFrame(table_frame, width=685, height=413, fg_color="white")
    scroll_container.place(x=5, y=60)

    scrollable_frame = ctk.CTkScrollableFrame(scroll_container, width=662, height=400, fg_color="white", corner_radius=10)
    scrollable_frame.place(x=0, y=0)

    user_icon = load_iconctk("icons/user_profile_setting.png", (60, 60))




    def load_customer_cards(search_text=None, filter_text="All"):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        customer_list = get_customers(search_text, filter_text)

        if not customer_list:
            ctk.CTkLabel(scrollable_frame, text="😢 No customers found.", font=("Lato", 16, "bold"), text_color="gray").pack(pady=150)
            return

        for customer in customer_list:

            customer["name"] = f"{customer['first_name']} {customer['last_name']}".title()

            card = ctk.CTkFrame(scrollable_frame, width=630, height=80, fg_color="#ececec", corner_radius=10,
                                border_color="#b1b1b1", border_width=1, cursor="hand2")
            card.pack(padx=8, pady=5, fill="x")
            card.bind("<Button-1>", lambda e, c=customer: open_customer_details_popup(c))

            ctk.CTkLabel(card, image=user_icon, text="").place(x=15, y=10)
            customer["name"] = customer["name"].title()
            ctk.CTkLabel(card, text=customer["name"], font=("Lato", 16, "bold")).place(x=90, y=10)
            ctk.CTkLabel(card, text=f"🖂  {customer['email']}", font=("Lato", 15), text_color="black").place(x=90, y=40)
            ctk.CTkLabel(card, text=f"🆔  {customer['user_id']}", font=("Lato", 14), text_color="black").place(x=300, y=10)
            ctk.CTkLabel(card, text=f"📞  {customer['phone']}", font=("Lato", 14)).place(x=300, y=40)

            status_color = "#a2f5b5" if customer["status"] == "Active" else "#ffe066"
            ctk.CTkLabel(card, text=customer["role"], font=("Lato", 14, "bold")).place(x=565, y=10)
            ctk.CTkLabel(card, text=customer["status"], font=("Lato", 14), fg_color=status_color, corner_radius=5,
                        text_color="black", width=60, height=23).place(x=550, y=40)

            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda e, c=customer: open_customer_details_popup(c))

    # Load once on page open
    load_customer_cards()
