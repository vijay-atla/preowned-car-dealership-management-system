import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message
from session import current_user
from database_utils import get_user_profile
from validators import is_valid_first_name, is_valid_last_name, is_valid_email, is_valid_phone
from password_change import open_change_password_screen


def open_profile_settings(root, parent_frame):
    # Clear frame
    for widget in parent_frame.winfo_children():
        widget.destroy()


    # ==== UI ====
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=illustration_image, text="").place(x=0, y=65)

    ctk.CTkLabel( parent_frame, image=load_iconctk("icons/user-profile.png", (60, 60)), text="  My Profile & Settings",
        font=("Lato", 30, "bold"), text_color="#008080", compound="left" ).place(x=61, y=59)

    ctk.CTkLabel(parent_frame, text=f"Welcome, {current_user["full_name"].title()}!", font=("Lato", 20)).place(x=515, y=73)
    ctk.CTkLabel(parent_frame, text="Account Details", font=("Lato", 16)).place(x=65, y=156)

    display_frame = ctk.CTkFrame(parent_frame, width=620, height=350, corner_radius=10,
                                 border_color="#808080", border_width=5)
    display_frame.place(x=65, y=178)

    profile_info = get_user_profile(current_user.get("user_id"))

    ctk.CTkLabel(display_frame, text="Profile Last Updated on:", font=("Lato", 12, "italic"),
                 text_color="gray").place(x=315, y=20)
    ctk.CTkLabel(display_frame, text=profile_info["last_updated"], font=("Lato", 12, "italic"),
                 text_color="gray").place(x=450, y=20)

    avatar_icon = load_iconctk("icons/user_profile_setting.png", (125, 125))
    ctk.CTkLabel(display_frame, image=avatar_icon, text="").place(x=60, y=85)

    role = profile_info["role"].title()
    labels = ["First Name", "Last Name", "Email", "Phone", "Role", "User Since"] if role in ["Admin", "Staff"] else ["First Name", "Last Name", "Email", "Phone", "User Since"]
    values = [profile_info["first_name"].title(), profile_info["last_name"].title(),
              profile_info["email"], profile_info["phone"], role, profile_info["user_since"]] if role in ["Admin", "Staff"] else [profile_info["first_name"].title(), 
                 profile_info["last_name"].title(), profile_info["email"], profile_info["phone"], profile_info["user_since"]] 

    for i, (label, value) in enumerate(zip(labels, values)):
        ctk.CTkLabel(display_frame, text=f"{label}:", font=("Lato", 16, "bold")).place(x=210, y=80 + i * 30)
        ctk.CTkLabel(display_frame, text=f"{value} ", font=("Lato", 16)).place(x=300, y=80 + i * 30)

    # ==== Edit Popup ====
    def open_edit_popup():
        popup = ctk.CTkToplevel(root)
        popup.title("Edit Profile Details")
        popup.geometry("450x400")
        popup.transient(root)
        popup.grab_set()

        x = display_frame.winfo_rootx()
        y = display_frame.winfo_rooty()
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(popup, text="Edit Your Details", font=("Lato", 20, "bold")).place(x=140, y=10)

        error_label = ctk.CTkLabel(popup, text="", text_color="red", font=("Lato", 13), wraplength=380, justify="center")
        error_label.place(x=120, y=50)

        entries = {}
        row = 0

        # Validation map
        validators = {
            "first_name": is_valid_first_name,
            "last_name": is_valid_last_name,
            "email": is_valid_email,
            "phone": is_valid_phone
        }

        submit_btn = None

        def validate_all(*_):
            for key, entry in entries.items():
                value = entry.get().strip()
                if key in validators:
                    valid, msg = validators[key](value)
                    if not valid:
                        error_label.configure(text=msg)
                        if submit_btn:
                            submit_btn.configure(state="disabled")
                        return
            error_label.configure(text="")
            if submit_btn:
                submit_btn.configure(state="normal")

        for i, label in enumerate(labels):
            ctk.CTkLabel(popup, text=f"{label}:", font=("Lato", 14, "bold")).place(x=60, y=85 + row * 45)
            if label in ["Role", "User Since"]:
                ctk.CTkLabel(popup, text=values[i], font=("Lato", 14, "bold"), text_color="gray").place(x=150, y=85 + row * 45)
            else:
                key = label.lower().replace(" ", "_")
                entry = ctk.CTkEntry(popup, width=200, font=("Lato", 12))
                entry.insert(0, profile_info[key])
                entry.place(x=150, y=85 + row * 45)
                entry.bind("<KeyRelease>", validate_all)
                entries[key] = entry
            row += 1

        ctk.CTkButton(popup, text="Cancel", width=100, command=popup.destroy).place(x=140, y=350)

        submit_btn = ctk.CTkButton(popup, text="Submit", width=100, fg_color="#008080", state="normal", command=lambda: submit_changes())
        submit_btn.place(x=260, y=350)

        validate_all()  # Initial check

        def submit_changes():
            updated = {k: v.get().strip() for k, v in entries.items()}
            changes = {k: v for k, v in updated.items() if v.casefold() != profile_info[k].casefold()}

            if not changes:
                error_label.configure(text="No changes detected.")
                return

            for key in changes:
                if key in validators:
                    valid, msg = validators[key](changes[key])
                    if not valid:
                        error_label.configure(text=msg)
                        return
            # Apply casing rules
            if "first_name" in changes:
                changes["first_name"] = changes["first_name"].upper()
            if "last_name" in changes:
                changes["last_name"] = changes["last_name"].upper()
            if "email" in changes:
                changes["email"] = changes["email"].lower()


            from database_utils import update_user_profile
            success, message = update_user_profile(current_user["user_id"], current_user["role"], changes)
            if success:
                popup.destroy()
                show_custom_message("Profile Updated", message)
                open_profile_settings(root, parent_frame)  # Reload updated data
            else:
                error_label.configure(text=message)


    # ==== Bottom Buttons ====
    ctk.CTkButton(parent_frame, text="Edit Details", width=120, height=30, corner_radius=5,bg_color="#dbdbdb", text_color="black",
                  font=("Lato", 16, "bold"), fg_color="#3ac3b3", command=open_edit_popup).place(x=450, y=448)

    ctk.CTkButton(parent_frame, text="Change Password", width=160, height=30, corner_radius=5,text_color="black",
                  font=("Lato", 16, "bold"), fg_color="#3ac3b3",bg_color="#dbdbdb",
                 command=lambda: open_change_password_screen(root, parent_frame, mode="Dashboard")).place(x=260, y=448)
    
    def go_to_dashboard(root):
        from session import current_user
        role = current_user.get("role", "").lower()

        if role == "customer":
            import customer_dashboard
            customer_dashboard.open_customer_dashboard(root)
        elif role == "staff":
            import staff_dashboard
            staff_dashboard.open_staff_dashboard(root)
        elif role == "admin":
            import admin_dashboard
            admin_dashboard.open_admin_dashboard(root)
        else:
            show_custom_message("Error", f"Unknown role: {role}")

    ctk.CTkButton(parent_frame, text="Back", width=60, height=30, corner_radius=5,text_color="black",
                  font=("Lato", 16, "bold"), fg_color="#3ac3b3", bg_color="#dbdbdb",
                  command=lambda: go_to_dashboard(root)).place(x=152, y=448)

