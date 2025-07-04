import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils import load_background, load_iconctk, show_custom_confirm
from database_utils import get_staff
from validators import is_valid_first_name, is_valid_last_name, is_valid_email, is_valid_phone
from session import current_user



def open_manage_staff(root, parent_frame):

    # staff_list = get_staff()  # 🧠 Loads from DB instead of hardcoded list
    search_debounce_timer = [None]  # Using list to make it mutable inside nested function


    def open_staff_details_popup(staff):
        popup_width = 500
        popup_height = 550

        popup = ctk.CTkToplevel(root)
        popup.geometry(f"{popup_width}x{popup_height}")
        popup.title(f"Staff Details - {staff['name']}")
        popup.resizable(False, False)
        popup.configure(fg_color="#f0f0f0")
        popup.attributes("-topmost", True)

        popup.update_idletasks()
        parent_x = parent_frame.winfo_rootx()
        parent_y = parent_frame.winfo_rooty()
        parent_w = parent_frame.winfo_width()
        parent_h = parent_frame.winfo_height()
        x = parent_x + 125
        y = parent_y + 50
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        has_changes = {"value": False}

        def mark_changed(*_):
            if not has_changes["value"]:
                has_changes["value"] = True
                update_btn.place(x=350, y=480)

        def bind_edit_icon(edit_widget, target_entry):
            def make_editable(_):
                try:
                    if target_entry.winfo_exists():
                        target_entry.configure(state="normal")
                        mark_changed()
                except:
                    pass  # widget already destroyed

            edit_widget.bind("<Button-1>", make_editable)

        def validate_entry(entry_widget, validator):
            value = entry_widget.get().strip()
            valid, msg = validator(value)
            if not valid:
                show_error(entry_widget, msg, popup)
            else:
                clear_error(entry_widget)


        ctk.CTkLabel(popup, text="Edit Staff Info", font=("Lato", 22, "bold")).place(x=160, y=20)

        y_pos = 70
        spacing = 50
        entries = {}

        editable_fields = ["First Name", "Last Name", "Email", "Phone", "Role", "Status"]
        values = {
            "First Name": staff["first_name"].title(),
            "Last Name": staff["last_name"].title(),
            "Email": staff["email"],
            "Phone": staff["phone"],
            "Role": staff["role"],
            "Status": staff["status"],
        }

        for field in editable_fields:
            ctk.CTkLabel(popup, text=f"{field}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
            
            if field == "Status":
                entry = ctk.CTkComboBox(popup, values=["Active", "Inactive"], width=280, height=30, state="readonly")
                entry.set(values[field])

            elif field == "Role":
                entry = ctk.CTkComboBox(popup, values=["Admin", "Staff"], width=280, height=30, state="readonly")
                entry.set(values[field])

            else:
                entry = ctk.CTkEntry(popup, height=30, width=280)
                entry.insert(0, values[field])
                entry.configure(state="disabled")
                # 🔄 Add live validation on editable text fields
                if field == "First Name":
                    entry.bind("<KeyRelease>", lambda e, ent=entry: validate_entry(ent, is_valid_first_name))
                elif field == "Last Name":
                    entry.bind("<KeyRelease>", lambda e, ent=entry: validate_entry(ent, is_valid_last_name))
                elif field == "Email":
                    entry.bind("<KeyRelease>", lambda e, ent=entry: validate_entry(ent, is_valid_email))
                elif field == "Phone":
                    entry.bind("<KeyRelease>", lambda e, ent=entry: validate_entry(ent, is_valid_phone))
            entry.place(x=125, y=y_pos)
            entries[field] = entry

            # Add editable emoji with click-to-edit
            edit_icon = ctk.CTkLabel(popup, image=load_iconctk("icons/edit_icon.png",(20,20)),text="", font=("Lato", 14), cursor="hand2")
            edit_icon.place(x=415, y=y_pos + 1)

            bind_edit_icon(edit_icon, entry)  # ✅ Bind each icon+entry here
            
            y_pos += spacing


        


        y_pos += 20  # optional extra spacing

        def format_timestamp(dt_obj):
            try:
                return dt_obj.strftime("%B %d, %Y  %I:%M %p")  # e.g., April 21, 2025  02:45 PM
            except:
                return str(dt_obj)

        # Non-editable fields
        readonly_fields = {
            "User Since": format_timestamp(staff.get("created_at")),     
            "Last Updated": format_timestamp(staff.get("updated_at"))
        }

        for field, value in readonly_fields.items():
            ctk.CTkLabel(popup, text=f"{field}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
            display = ctk.CTkEntry(popup, width=280)
            display.insert(0, value)
            display.configure(state="disabled", text_color="gray")
            display.place(x=150, y=y_pos)
            y_pos += spacing

        def close_popup_and_refresh():
            popup.destroy()
            load_staff_cards()

        ctk.CTkButton(popup, text="Back", fg_color="#d9534f", text_color="white", width=100,
                    command=close_popup_and_refresh).place(x=50, y=480)

        update_btn = ctk.CTkButton(popup, text="Update", fg_color="#30b8a9", text_color="white", width=100)

        success_label = ctk.CTkLabel(popup, text="", font=("Lato", 14, "bold"), text_color="#006600")


        def update_staff_details():

            from database_utils import update_staff

            # Read updated values
            updated_data = {
                "first_name": entries["First Name"].get().strip().upper(),
                "last_name": entries["Last Name"].get().strip().upper(),
                "email": entries["Email"].get().strip().lower(),
                "phone": entries["Phone"].get().strip(),
                "role": entries["Role"].get().strip(),
                "status": 1 if entries["Status"].get() == "Active" else 0
            }

            for key, validator, entry_key in [
                ("first_name", is_valid_first_name, "First Name"),
                ("last_name", is_valid_last_name, "Last Name"),
                ("email", is_valid_email, "Email"),
                ("phone", is_valid_phone, "Phone")
            ]:
                value = updated_data[key]
                valid, msg = validator(value)
                if not valid:
                    return show_error(entries[entry_key], msg, popup)


            original_role = staff["role"]
            original_status = staff["status"]

            new_role = updated_data["role"]
            new_status = "Active" if updated_data["status"] == 1 else "Inactive"

            if new_role != original_role or new_status != original_status:
                confirm = tk.messagebox.askyesno(title="⚠️ Confirm Critical Change",
                    message=f"⚠️ You are changing the user's role or status.\n\nOld Role: {original_role} → New: {new_role}\nOld Status: {original_status} → New: {new_status}\n\nAre you sure?"
                , parent=popup)
                if not confirm:
                    return  # Cancel update



            # Call DB update
            success, msg = update_staff(user_id=staff["user_id"], **updated_data )

            # Re-fetch the same staff from DB to get updated timestamps
            latest = get_staff(str(staff["user_id"]))  # search by ID (as string)
            if latest:
                staff.update(latest[0])  # refresh the staff dictionary

            if success:
                # Show live animation label
                success_label.configure(text="✅ Staff updated successfully!")
                success_label.place(x=130, y=250)

                # Auto-hide after 2.5 seconds and close
                def finish_update():
                    success_label.place_forget()
                    popup.destroy()
                    load_staff_cards()
                popup.after(3000, finish_update)

            else:
                show_error(entries["Email"], msg, popup)


        update_btn.configure(command=update_staff_details)

        # Only appears when a field is edited

    ####

    error_labels = {}

    def show_error(entry, message, container):
        if entry in error_labels:
            error_labels[entry].configure(text=message)
        else:
            label = ctk.CTkLabel(container, text=message, text_color="red", font=("Lato", 13), bg_color="transparent")
            label.place(x=175, y=42)
            error_labels[entry] = label


    def clear_error(entry):
        if entry in error_labels:
            error_labels[entry].destroy()
            del error_labels[entry]


    def open_add_staff_popup():
        popup = ctk.CTkToplevel(root)
        popup.geometry("500x480")
        popup.title("Add New Staff")
        popup.configure(fg_color="#E5F9F9")
        popup.attributes("-topmost", True)

        popup.update_idletasks()
        x = parent_frame.winfo_rootx() + 125
        y = parent_frame.winfo_rooty() + 50
        popup.geometry(f"500x480+{x}+{y}")

        ctk.CTkLabel(popup, text="Add New Staff", font=("Lato", 22, "bold")).place(x=160, y=20)

        y_pos = 70
        spacing = 50
        field_data = {}

        def create_entry(label, key, placeholder=""):
            nonlocal y_pos
            ctk.CTkLabel(popup, text=f"{label}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
            entry = ctk.CTkEntry(popup, width=280, height=30, placeholder_text=placeholder)
            entry.place(x=150, y=y_pos)
            field_data[key] = entry

            def live_validate(entry, validator):
                def inner(_):
                    value = entry.get().strip()
                    valid, msg = validator(value)
                    if not valid:
                        show_error(entry, msg, popup)
                    else:
                        clear_error(entry)
                return inner

            # Bind validation
            if key == "first_name":
                entry.bind("<KeyRelease>", live_validate(entry, is_valid_first_name))
            elif key == "last_name":
                entry.bind("<KeyRelease>", live_validate(entry, is_valid_last_name))
            elif key == "email":
                entry.bind("<KeyRelease>", live_validate(entry, is_valid_email))
            elif key == "phone":
                entry.bind("<KeyRelease>", live_validate(entry, is_valid_phone))

            y_pos += spacing

        def create_dropdown(label, key, values, default=""):
            nonlocal y_pos
            ctk.CTkLabel(popup, text=f"{label}:", font=("Lato", 14, "bold")).place(x=40, y=y_pos)
            dropdown = ctk.CTkComboBox(popup, width=280, height=30, values=values)
            dropdown.set(default or values[0])
            dropdown.place(x=150, y=y_pos)
            field_data[key] = dropdown
            y_pos += spacing

        create_entry("First Name", "first_name")
        create_entry("Last Name", "last_name")
        create_entry("Email", "email")
        create_entry("Phone Number", "phone")
        create_dropdown("Role", "role", [ "Staff", "Admin"])
        create_dropdown("Status", "status", ["Active", "Inactive"])

        success_label = ctk.CTkLabel(popup, text="", font=("Lato", 14, "bold"), text_color="#006600")

        def reset_form():
            for key, widget in field_data.items():
                if isinstance(widget, ctk.CTkComboBox):
                    widget.set(widget.cget("values")[0])
                else:
                    widget.delete(0, "end")
                clear_error(widget)  # ✅ Clear any validation errors
            success_label.configure(text="")

            error_labels.clear()  # ✅ Clear global error tracking dictionary




        def close_popup():
            popup.destroy()

        def add_staff():

            # ✅ Validate fields before proceeding
            for key, validator in [
                ("first_name", is_valid_first_name),
                ("last_name", is_valid_last_name),
                ("email", is_valid_email),
                ("phone", is_valid_phone)
            ]:
                value = field_data[key].get().strip()
                valid, msg = validator(value)
                if not valid:
                    show_error(field_data[key], msg, popup)
                    return


            if error_labels:
                return  # ❌ Don't proceed if there are validation errors
            
            # ✅ Now collect the data after validation passes
            data = {key: widget.get() for key, widget in field_data.items()}

            # Format:
            data["first_name"] = data["first_name"].upper()
            data["last_name"] = data["last_name"].upper()
            data["email"] = data["email"].lower()
            data["status"] = 1 if data["status"] == "Active" else 0
            data["password"] = "Staff@123"  # default password
            
            from database_utils import insert_staff, hash_password, user_exists

            # Check for duplicates
            exists, reason = user_exists(data["email"], data["phone"])
            if exists:
                show_error(field_data["email"], reason, popup) if "email" in reason else show_error(field_data["phone"], reason, popup)
                return

            # Hash the default password
            password_hash = hash_password(data["password"])

            # Insert to DB
            success, result = insert_staff(data["first_name"], data["last_name"], data["email"], data["phone"], password_hash, data["role"], data["status"])

            def show_staff_id_popup(user_id):
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

                ctk.CTkLabel(success_popup, text="✅ Staff added successfully!", font=("Lato", 16, "bold"), text_color="#006600").place(x=70, y=30)
                ctk.CTkLabel(success_popup, text=f"🆔 Assigned Staff ID: {user_id}", font=("Lato", 14)).place(x=80, y=70)

                # ✅ Close both popups on OK
                def close_both():
                    success_popup.destroy()
                    popup.destroy()
                    load_staff_cards()  # ✅ Refresh the staff list after adding new staff


                ctk.CTkButton(success_popup, text="OK", fg_color="#30b8a9", text_color="black", command=close_both).place(x=130, y=110)


            if success:
                reset_form()
                error_labels.clear()
                show_staff_id_popup(result)
                # success_label.configure(text=f"✅ Staff added successfully! ID: {result}")
                # success_label.place(x=80, y=430)
            else:
                show_error(field_data["email"], result, popup)


        ctk.CTkButton(popup, text="Back", width=100, fg_color="#d9534f", text_color="black", font=("Lato", 14, "bold"), command=close_popup).place(x=40, y=410)
        ctk.CTkButton(popup, text="Reset", width=100, fg_color="#808080", text_color="black", font=("Lato", 14, "bold"),command=reset_form).place(x=195, y=410)
        ctk.CTkButton(popup, text="Add Staff", width=100, fg_color="#30b8a9", text_color="black", font=("Lato", 14, "bold"),command=add_staff).place(x=350, y=410)




    # Clear parent frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.2)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(parent_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)


    # Welcome Message
    ctk.CTkLabel(parent_frame,  image=load_iconctk("icons/manage_staff_icon.png", (60, 60)), text="  Manage Staff", 
                                font=("Lato", 30, "bold"), text_color="#008080", fg_color="#ffffff", compound="left").place(x=25, y=45)  

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    # Table Frame
    table_frame = ctk.CTkFrame(parent_frame, width=700, height=480, fg_color="#ffffff",
                                corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=25, y=132)

    # Search Frame
    search_frame = ctk.CTkFrame(table_frame, width=660, height=40, fg_color="#bababa",
                                corner_radius=10, border_color="#808080", border_width=1)
    search_frame.place(x=15, y=10)

    search_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/search_icon.png", (25, 25)), text="")
    search_icon_label.place(x=10, y=7)

    
    search_var = tk.StringVar()
    # Search, Filter & Add Staff
    search_box = ctk.CTkEntry(search_frame, placeholder_text="Search Staff...", corner_radius=20, width=250, textvariable=search_var)
    search_box.place(x=40, y=7)

    

    filter_var = tk.StringVar(value="All")  # 👈 the tracked variable

    status_filter = ctk.CTkComboBox(search_frame, values=["Active", "Inactive", "All"], width=90, height=25, variable=filter_var)
    status_filter.set("All")
    status_filter.place(x=430, y=8)

    def on_filter_change_var(*args):
        filter_val = filter_var.get()
        search_val = search_box.get().strip()
        load_staff_cards(search_text=search_val, filter_text=filter_val)

    filter_var.trace_add("write", on_filter_change_var)

    def on_search_change(*args):
        if search_debounce_timer[0] is not None:
            root.after_cancel(search_debounce_timer[0])  # Cancel previous scheduled call

        def delayed_search():
            filter_val = filter_var.get()
            search_val = search_var.get().strip()
            load_staff_cards(search_text=search_val, filter_text=filter_val)

        # Set timer to trigger delayed_search after 400ms
        search_debounce_timer[0] = root.after(400, delayed_search)

    search_var.trace_add("write", on_search_change)



    


    go_btn = ctk.CTkButton(search_frame, text="Go", width=37, height=23, fg_color="#30b8a9", text_color="black", border_width=1, cursor="hand2",
                           border_color="#b4b4b4", font=("Lato", 14), hover_color="#30b8a9")
    go_btn.place(x=300, y=9)

    


    filter_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/filter_icon.png", (20, 20)), text="  Status: ", compound="left",
                                     font=("Lato", 14))
    filter_icon_label.place(x=360, y=7)

    

    


    add_staff_btn = ctk.CTkButton(search_frame, text="➕ Add Staff", fg_color="#30b8a9", font=("Lato", 13, "bold") , cursor="hand2",
                                 text_color="black", width=105, height=30, border_width=1 , border_color="#b4b4b4",  hover_color="#30b8a9")
    add_staff_btn.configure(command=open_add_staff_popup)
    add_staff_btn.place(x=535, y=6)

    
    # === Scroll Frame Container (inside table_frame, below search_frame) ===
    scroll_container = ctk.CTkFrame(table_frame, width=685, height=413, fg_color="white")
    scroll_container.place(x=5, y=60)

    # === Actual Scrollable Frame (for staff cards) ===
    scrollable_frame = ctk.CTkScrollableFrame(scroll_container, width=662, height=400, fg_color="white", corner_radius=10,
                                            scrollbar_button_color="#d9d9d9", scrollbar_button_hover_color="#666666")
    scrollable_frame.place(x=0, y=0)

    user_icon=load_iconctk("icons/user_profile_setting.png",(60,60))


    def load_staff_cards(search_text=None, filter_text="All"):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        staff_list = get_staff(search_text, filter_text)

        if not staff_list:
            no_result_label = ctk.CTkLabel(scrollable_frame, text="😢 No staff found matching your search.", font=("Lato", 16, "bold"), text_color="gray")
            no_result_label.pack(pady=150)
            return


        # Staff Cards
        for staff in staff_list:
            card = ctk.CTkFrame(scrollable_frame, width=630, height=80, fg_color="#ececec", corner_radius=10, border_color="#b1b1b1",
                                border_width=1, cursor="hand2" )
            card.pack(padx=8, pady=5, fill="x")
            card.bind("<Button-1>", lambda e, s=staff: open_staff_details_popup(s))


            ctk.CTkLabel(card, image=user_icon, text="", cursor="hand2").place(x=15, y=10)
            staff["name"]=staff["name"].title()
            # Name + Email
            ctk.CTkLabel(card, text=staff["name"], font=("Lato", 16, "bold"), cursor="hand2").place(x=90, y=10)
            ctk.CTkLabel(card, text=f"🖂  {staff["email"]}", font=("Lato", 15), text_color="black", cursor="hand2").place(x=90, y=40)

            # ID + Phone
            ctk.CTkLabel(card, text=f"🆔  {staff['user_id']}", font=("Lato", 14), text_color="black", cursor="hand2").place(x=300, y=10)
            ctk.CTkLabel(card, text=f"📞  {staff["phone"]}", font=("Lato", 14), cursor="hand2").place(x=300, y=40)

            status_color = "#a2f5b5" if staff["status"] == "Active" else "#ffe066"

            # Role + Status
            ctk.CTkLabel(card, text=staff["role"], font=("Lato", 14, "bold"), cursor="hand2").place(x=565, y=10)
            ctk.CTkLabel(card, text=staff["status"], font=("Lato", 14), fg_color=status_color, corner_radius=5, justify = "center",
                        text_color="black", width=60, height=23, cursor="hand2").place(x=550, y=40)
        
            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda e, s=staff: open_staff_details_popup(s))


    search_box.bind("<Return>", on_filter_change_var)
    status_filter.bind("<<ComboboxSelected>>", on_filter_change_var)
    go_btn.configure(command=on_filter_change_var)

    load_staff_cards()  # Load all by default
