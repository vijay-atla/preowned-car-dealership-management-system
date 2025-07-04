import customtkinter as ctk
import tkinter as tk
from utils import load_background, load_icon, load_iconctk, show_gif_loader,hide_loader
import re
import hashlib
from database_utils import hash_password, insert_user, user_exists



def open_signup_screen(root):
    # Clear previous screen
    for widget in root.winfo_children():
        widget.destroy()

    def go_to_login():
        from login import open_login_screen
        show_gif_loader(root, "Redirecting to Login...")
        root.after(1000, lambda: [hide_loader(), open_login_screen(root)])


    # === Error Label Handler ===
    error_labels = {}
    def show_error(entry, message):
        if entry in error_labels:
            error_labels[entry].configure(text=message)
        else:
            label = ctk.CTkLabel(right_frame, text=message, text_color="red", font=("Lato", 16), justify = "center", width=300, fg_color="transparent")
            label.place(x=140, y=140)
            error_labels[entry] = label

    def clear_error(entry):
        if entry in error_labels:
            error_labels[entry].destroy()
            del error_labels[entry]

    # === Live Validation ===
    def validate_name(entry):
        value = entry.get().strip()
        if not value or len(value) < 3 or not all(part.isalpha() for part in value.split()):
            show_error(entry, "Name should be minimum 3 and only alphabetic characters")
        else:
            clear_error(entry)

    def validate_email(event=None):
        email = email_entry.get().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            show_error(email_entry, "Enter a valid email")
        else:
            clear_error(email_entry)

    def validate_phone(event=None):
        phone = phone_entry.get().strip()
        if not re.fullmatch(r"\d{10}", phone):
            show_error(phone_entry, "Enter 10 digit number")
        else:
            clear_error(phone_entry)

    def validate_password_live(event=None):
        pwd = password_entry.get()
        checks = {
            "Length (8+)": len(pwd) >= 8,
            "Uppercase": bool(re.search(r"[A-Z]", pwd)),
            "Lowercase": bool(re.search(r"[a-z]", pwd)),
            "Digit": bool(re.search(r"\d", pwd)),
            "Special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd)),
        }
        met_all = all(checks.values())
        passwodrequirement_label.configure(text_color="green" if met_all else "red")
        if not met_all:
            show_error(password_entry, "Password doesn't meet criteria")
        else:
            clear_error(password_entry)

    def validate_confirm_password(event=None):
        if confirmpassword_entry.get() != password_entry.get():
            show_error(confirmpassword_entry, "Passwords do not match")
        else:
            clear_error(confirmpassword_entry)

    def show_password_popup(event=None):
        popup = ctk.CTkToplevel(root)
        popup.geometry("400x250")
        popup.title("Password Requirements")
        popup.resizable(False, False)
        popup.transient(root)
        popup.grab_set()

        # Position the popup exactly over the right frame
        x = right_frame.winfo_rootx() + 100
        y = right_frame.winfo_rooty() + 250
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(popup, text="Password Requirements", font=("Lato", 20, "bold")).place(x=105, y=10)

        pwd = password_entry.get()
        status = {
            "Length sholud be minumimum 8 characters": len(pwd) >= 8,
            "Should Contain atleast 1 Uppercase alphabet": bool(re.search(r"[A-Z]", pwd)),
            "Should Contain atleast 1 Lowercase alphabet": bool(re.search(r"[a-z]", pwd)),
            "Should Contain atleast 1 Digit": bool(re.search(r"\d", pwd)),
            "Should Contain atleast 1 Special character": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd)),
        }
        for i, (rule, passed) in enumerate(status.items()):
            symbol = "✔️" if passed else "❌"
            ctk.CTkLabel(popup, text=f"{symbol} {rule}", text_color="green" if passed else "red",
                font=("Lato", 13)).place(x=70, y=50 + (i * 30))

    # === Register User ===
    def register_user():
        validate_name(firstname_entry)
        validate_name(lastname_entry)
        validate_email()
        validate_phone()
        validate_password_live()
        validate_confirm_password()

        if error_labels:
            return

        fname = firstname_entry.get().strip().upper()
        lname = lastname_entry.get().strip().upper()
        email = email_entry.get().strip().lower()
        phone = phone_entry.get().strip()
        pwd = password_entry.get()

        from utils import show_custom_message
        exists, reason = user_exists(email, phone)
        if exists:
            show_custom_message("Error", reason)
            return

        pwd_hashed = hash_password(pwd)
        success, msg = insert_user(fname, lname, email, phone, pwd_hashed, role="customer")
        if success:
            show_custom_message("Success", msg)
            show_gif_loader(root, "Redirecting to Login...")
            root.after(1200, lambda: [hide_loader(), go_to_login()])
        else:
            show_custom_message("Error", msg)


    # === UI Layout ===


    # Left Side - Illustration Frame
    left_frame = ctk.CTkFrame(root, width=305, height=653, fg_color="white", corner_radius=5, border_color="#dedede", border_width=3)
    left_frame.place(x=-3, y=-3)

    illustration_image = load_background("icons/signup_bg.png", (260, 190))
    illustration_label = ctk.CTkLabel(left_frame, image=illustration_image, text="")
    illustration_label.place(x=35, y=235)


    label_login_icon = load_iconctk("icons/login_icon.png" , (50, 50))  # Make sure logo.png is in your directory
    label_login = ctk.CTkLabel(left_frame, image=label_login_icon, text="", cursor="hand2")
    label_login.bind("<Button-1>",  lambda e: go_to_login())
    label_login.place(x=209, y=543)

    label_back_label = ctk.CTkLabel(left_frame, text="Already have an account?\nClick to Login", font=("Lato", 14), text_color= "#000000",
                                    justify = "center")
    label_back_label.place(x=40, y=554)



    # Right Side - Login Form Frame
    # Right Form Area
    global right_frame, firstname_entry, lastname_entry, email_entry, phone_entry, password_entry, confirmpassword_entry, passwodrequirement_label
    right_frame = ctk.CTkFrame(root, width=600, height=650, fg_color="white", corner_radius=5)
    right_frame.place(x=300, y=0)

    illustration_image_right = load_background("icons/default_bg.png", (580, 405), 0.15)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(right_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=5, y=125)

    signup_label = ctk.CTkLabel(right_frame, text="New User Registration", font=("Lato", 40, "bold"))
    signup_label.place(x=97, y=70)


    firstname_label = ctk.CTkLabel(right_frame, text="First Name", font=("Lato", 14))
    firstname_label.place(x=42, y=180)
    firstname_entry = ctk.CTkEntry(right_frame, width=225, height=40, font=("Lato", 14), placeholder_text="john", corner_radius=5,
                            placeholder_text_color="#6d6d6d", border_color="#b4b4b4", border_width= 1, fg_color="#d9d9d9")
    firstname_entry.place(x=42, y=203)
    firstname_entry.bind("<KeyRelease>", lambda e: validate_name(firstname_entry))


    lastname_label = ctk.CTkLabel(right_frame, text="Last Name", font=("Lato", 14), fg_color="#e8e7ff")
    lastname_label.place(x=334, y=180)
    lastname_entry = ctk.CTkEntry(right_frame, width=225, height=40, font=("Lato", 14), placeholder_text="doe", corner_radius=5,
                            placeholder_text_color="#6d6d6d", border_color="#b4b4b4", border_width= 1, fg_color="#d9d9d9")
    lastname_entry.place(x=332, y=203)
    lastname_entry.bind("<KeyRelease>", lambda e: validate_name(lastname_entry))


    email_label = ctk.CTkLabel(right_frame, text="Email", font=("Lato", 14), fg_color="transparent", bg_color="transparent")
    email_label.place(x=42, y=285)
    email_entry = ctk.CTkEntry(right_frame, width=225, height=40, font=("Lato", 14), placeholder_text="abc@abc.com", corner_radius=5,
                            placeholder_text_color="#6d6d6d", border_color="#b4b4b4", border_width= 1, fg_color="#d9d9d9")
    email_entry.place(x=42, y=309)
    email_entry.bind("<KeyRelease>", validate_email)


    phone_label = ctk.CTkLabel(right_frame, text="Phone Number", font=("Lato", 14), fg_color="#e8e7ff",height=1)
    phone_label.place(x=334, y=290)
    phone_entry = ctk.CTkEntry(right_frame, width=225, height=40, font=("Lato", 14), placeholder_text="9876543210", corner_radius=5,
                            placeholder_text_color="#6d6d6d", border_color="#b4b4b4", border_width= 1, fg_color="#d9d9d9")
    phone_entry.place(x=332, y=309)
    phone_entry.bind("<KeyRelease>", validate_phone)



    password_label = ctk.CTkLabel(right_frame, text="Password", font=("Lato", 14), fg_color="#e8e7ff")
    password_label.place(x=42, y=392)
    password_entry = ctk.CTkEntry(right_frame, width=225, height=40, font=("Lato", 20), show="*", placeholder_text="********", 
                                placeholder_text_color="#6d6d6d", border_color="#b4b4b4", border_width= 1, fg_color="#d9d9d9",
                                )
    password_entry.place(x=42, y=415)
    password_entry.bind("<KeyRelease>", validate_password_live)


    confirmpassword_label = ctk.CTkLabel(right_frame, text="Confirm Password", font=("Lato", 14), fg_color="#e8e7ff")
    confirmpassword_label.place(x=334, y=392)
    confirmpassword_entry = ctk.CTkEntry(right_frame, width=225, height=40, font=("Lato", 20), show="*", placeholder_text="********", 
                                placeholder_text_color="#6d6d6d", border_color="#b4b4b4", border_width= 1, fg_color="#d9d9d9")
    confirmpassword_entry.place(x=332, y=415)
    confirmpassword_entry.bind("<KeyRelease>", validate_confirm_password)


    # Show Password Function
    def toggle_password():
        password_entry.configure(show="" if password_entry.cget("show") == "*" else "*")
        confirmpassword_entry.configure(show="" if confirmpassword_entry.cget("show") == "*" else "*")

    

    show_password = ctk.CTkCheckBox(right_frame, text="Show Password", font=("Lato", 14), corner_radius= 4,command=toggle_password,
                                    bg_color="#fbfbfb", fg_color="#fbfbfb", border_width=2, border_color="#b4b4b4", checkbox_height=15,
                                    checkbox_width=15, hover_color="#d9d9d9", height=20, checkmark_color="green")
    show_password.place(x=430, y=455)

    passwodrequirement_label = ctk.CTkLabel(right_frame, text="Password Requirements", font=("Lato", 13), text_color="black", cursor="hand2",
                                            fg_color="#e8e7ff")
    passwodrequirement_label.place(x=44, y=455)
    passwodrequirement_label.bind("<Button-1>", show_password_popup)
    password_entry.bind("<KeyRelease>", validate_password_live)

    register_button = ctk.CTkButton(right_frame, text="Register", width=300, height=45, text_color="black", font=("Lato", 24, "bold"),
                                corner_radius=5, fg_color="#17B8A6", border_color="#b4b4b4", border_width=1, hover_color="#17B8A6", cursor="hand2",
                                command=register_user)
    register_button.place(x=150, y=527)

