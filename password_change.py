import customtkinter as ctk
import tkinter as tk
from utils import load_background, load_iconctk, show_gif_loader,hide_loader
from session import current_user
from database_utils import hash_password, validate_user, update_user_password
import re



def open_change_password_screen(root, email, mode="login"):
    for widget in root.winfo_children():
        widget.destroy()

    # === Helper Functions ===
    def go_to_login():
        from login import open_login_screen
        show_gif_loader(root, "Redirecting to Login...")
        root.after(1000, lambda: [hide_loader(), open_login_screen(root)])

    def validate_password_live(event=None):
        pwd = new_password_entry.get()
        checks = {
            "Length (8+)": len(pwd) >= 8,
            "Uppercase": bool(re.search(r"[A-Z]", pwd)),
            "Lowercase": bool(re.search(r"[a-z]", pwd)),
            "Digit": bool(re.search(r"\d", pwd)),
            "Special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd)),
        }
        met_all = all(checks.values())
        password_requiremets_label.configure(text_color="green" if met_all else "red")

        if not met_all:
            error_message_label.configure(text="Password doesn't meet criteria", text_color="red")
        else:
            error_message_label.configure(text="")



    def show_password_popup(event=None):
        popup = ctk.CTkToplevel(root)
        popup.geometry("400x250")
        popup.title("Password Requirements")
        popup.resizable(False, False)
        popup.transient(root)
        popup.grab_set()

        x = right_frame.winfo_rootx() + 0
        y = right_frame.winfo_rooty() + 250
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(popup, text="Password Requirements", font=("Lato", 20, "bold")).place(x=105, y=10)

        pwd = new_password_entry.get()
        status = {
            "Length sholud be minimum 8 characters": len(pwd) >= 8,
            "Should Contain atleast 1 Uppercase alphabet": bool(re.search(r"[A-Z]", pwd)),
            "Should Contain atleast 1 Lowercase alphabet": bool(re.search(r"[a-z]", pwd)),
            "Should Contain atleast 1 Digit": bool(re.search(r"\d", pwd)),
            "Should Contain atleast 1 Special character": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd)),
        }

        for i, (rule, passed) in enumerate(status.items()):
            symbol = "✔️" if passed else "❌"
            ctk.CTkLabel(popup, text=f"{symbol} {rule}",
                        text_color="green" if passed else "red", font=("Lato", 13)).place(x=70, y=50 + (i * 30))





    def update_password():
        errors = []
        old_pwd = old_password_entry.get()
        new_pwd = new_password_entry.get()
        confirm_pwd = confirm_password_entry.get()

        if not old_pwd or not new_pwd or not confirm_pwd:
            errors.append("All fields are required.")

        if new_pwd != confirm_pwd:
            errors.append("New passwords do not match.")

        checks = {
            "Length (8+)": len(new_pwd) >= 8,
            "Uppercase": bool(re.search(r"[A-Z]", new_pwd)),
            "Lowercase": bool(re.search(r"[a-z]", new_pwd)),
            "Digit": bool(re.search(r"\d", new_pwd)),
            "Special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_pwd)),
        }

        if not all(checks.values()):
            errors.append("Password doesn't meet required strength.")

        if errors:
            error_message_label.configure(text="\n".join(errors), text_color="red")
            return

        valid, user = validate_user(email, old_pwd)
        if not valid:
            error_message_label.configure(text="Old password is incorrect.", text_color="red")
            return

        hashed = hash_password(new_pwd)
        success, msg = update_user_password(email, hashed)

        if success:
            error_message_label.configure(text="✅ Password changed successfully!", text_color="green")
            current_user.clear()
            show_gif_loader(root, "Redirecting to Login...")
            root.after(1000, lambda: [hide_loader(), __import__('login').open_login_screen(root)])
        else:
            error_message_label.configure(text=msg, text_color="red")

    # Left Side - Illustration Frame
    left_frame = ctk.CTkFrame(root, width=428, height=653, fg_color="white", corner_radius=5, border_color="#dedede", border_width=2)
    left_frame.place(x=-3, y=-3)

    illustration_image = load_background("icons/change_pass_bg.png", (330, 250))  # Replace with your image file
    illustration_label = ctk.CTkLabel(left_frame, image=illustration_image, text="")
    illustration_label.place(x=47, y=210)


    label_back_icon = load_iconctk("icons/back_icon.png" , (50, 50))  # Make sure logo.png is in your directory
    label_back = ctk.CTkLabel(left_frame, image=label_back_icon, text="", cursor="hand2")
    label_back.bind("<Button-1>", lambda e: go_back())
    label_back.place(x=34, y=570)

    label_back_label = ctk.CTkLabel(left_frame, text=f"Back to {mode.title()}", font=("Lato", 16), text_color= "#000000", cursor="hand2")
    label_back_label.place(x=95, y=580)
    label_back.bind("<Button-1>", lambda e: go_back())

    def go_back():
        if current_user["role"] is None:
            go_to_login()
        else:
            role = current_user.get("role", "").lower()

            if role == "admin":
                import admin_dashboard
                admin_dashboard.open_admin_dashboard(root)
            elif role == "staff":
                import staff_dashboard
                staff_dashboard.open_staff_dashboard(root)
            elif role == "customer":
                import customer_dashboard
                customer_dashboard.open_customer_dashboard(root)
            else:
                go_to_login()

#-----------------------------------------------------------------------------------------------------------------------------


    # Right Side - Login Form Frame
    right_frame = ctk.CTkFrame(root, width=475, height=650, fg_color="white", corner_radius=5)
    right_frame.place(x=425, y=0)

    illustration_image_right = load_background("icons/default_bg.png", (470, 340), 0.2)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(right_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=150)

    global old_password_entry, new_password_entry, confirm_password_entry, error_message_label

    change_password_label = ctk.CTkLabel(right_frame, text="Change Password", font=("Lato", 40, "bold"))
    change_password_label.place(x=79, y=82)

    error_message_label = ctk.CTkLabel(right_frame, text="", text_color="red", font=("Lato", 15), fg_color="transparent", wraplength=400, justify="center")
    error_message_label.place(x=105, y=150)


    old_password_label = ctk.CTkLabel(right_frame, text="Old Password", width=110, height= 15, font=("Lato", 14), bg_color="transparent", fg_color="transparent")
    old_password_label.place(x=80, y=199)
    old_password_entry = ctk.CTkEntry(right_frame, width=300, height=45, font=("Lato", 16), show="*", placeholder_text="********", 
                                placeholder_text_color="#6d6d6d", border_color="#a99e9e", border_width= 1, fg_color="#d9d9d9")
    old_password_entry.place(x=88, y=219)


    new_password_label = ctk.CTkLabel(right_frame, text="New Password", width=110, height= 15, font=("Lato", 14), bg_color="transparent", fg_color="transparent")
    new_password_label.place(x=83, y=285)
    new_password_entry = ctk.CTkEntry(right_frame, width=300, height=45, font=("Lato", 16), show="*", placeholder_text="********", 
                                placeholder_text_color="#6d6d6d", border_color="#a99e9e", border_width= 1, fg_color="#d9d9d9")
    new_password_entry.place(x=88, y=304)
    new_password_entry.bind("<KeyRelease>", validate_password_live)




    confirm_password_label = ctk.CTkLabel(right_frame, text="Confirm New Password", width=170, height= 15, font=("Lato", 14),
                                        bg_color="transparent", fg_color="#e1dfff")
    confirm_password_label.place(x=80, y=371)
    confirm_password_entry = ctk.CTkEntry(right_frame, width=300, height=45, font=("Lato", 16), show="*", placeholder_text="********", 
                                placeholder_text_color="#6d6d6d", border_color="#a99e9e", border_width= 1, fg_color="#d9d9d9")
    confirm_password_entry.place(x=88, y=390)

    # Show Password Function
    def toggle_password():
        old_password_entry.configure(show="" if old_password_entry.cget("show") == "*" else "*")
        new_password_entry.configure(show="" if new_password_entry.cget("show") == "*" else "*")
        confirm_password_entry.configure(show="" if confirm_password_entry.cget("show") == "*" else "*")

    show_password = ctk.CTkCheckBox(right_frame, text="Show Password", font=("Lato", 13), corner_radius= 6,command=toggle_password,
                                    bg_color="#e1dfff", fg_color="#e1dfff", border_width=2, border_color="#a99e9e", checkbox_height=20,
                                    checkbox_width=20, hover_color="#d9d9d9", checkmark_color="green")
    show_password.place(x=270, y=435)

    submit_button = ctk.CTkButton(right_frame, text="Submit", width=300, height=45, text_color="black", font=("Lato", 24, "bold"),
                                corner_radius=5, fg_color="#17B8A6", border_color="#a99e9e", border_width=1, hover_color="#17B8A6", cursor="hand2")
    submit_button.place(x=86, y=508)
    submit_button.configure(command=update_password)


    password_requiremets_label = ctk.CTkLabel(right_frame, text="Password Requirements", font=("Lato", 14), bg_color="#e1dfff", fg_color="#e1dfff",
                                            text_color="black", cursor="hand2")
    password_requiremets_label.place(x=89, y=435)
    password_requiremets_label.bind("<Button-1>", show_password_popup)


