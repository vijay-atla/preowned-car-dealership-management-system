import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from utils import load_background, load_icon, load_iconctk, load_custom_fonts, show_gif_loader, hide_loader
from database_utils import validate_user
import subprocess,sys


def open_login_screen(root):
    # Clear previous screen
    for widget in root.winfo_children():
        widget.destroy()


    def handle_login():
        email = email_entry.get().strip().lower()
        password = password_entry.get()
        login_error_label.configure(text="")  # clear old error

        if not email or not password:
            login_error_label.configure(text="Please fill in all fields.")
            return

        valid, result = validate_user(email, password)

        if not valid:
            login_error_label.configure(text=result)
            return

        # If valid = True
        if result["active_status"] != 1:
            login_error_label.configure(text="Account inactive. Please contact admin.")
            return

        if result.get("pwd_change_req") == 1:
            from password_change import open_change_password_screen
            show_gif_loader(root, "Redirecting to Change Password...")
            root.after(1000, lambda: [hide_loader(), open_change_password_screen(root, email)])
            return

        from session import current_user
        current_user.update(result)  # Update session values

        # redirect based on role
        role = current_user["role"]
        show_gif_loader(root, f"Logging in as {role.title()}...")

        def go_to_dashboard():
            hide_loader()
            if role == "admin":
                from admin_dashboard import open_admin_dashboard
                open_admin_dashboard(root)
            elif role == "staff":
                from staff_dashboard import open_staff_dashboard
                open_staff_dashboard(root)
            else:
                from customer_dashboard import open_customer_dashboard
                open_customer_dashboard(root)

        root.after(1000, go_to_dashboard)


    # Left Side - Illustration Frame
    left_frame = ctk.CTkFrame(root, width=428, height=653, fg_color="white", corner_radius=5, border_color="#dedede", border_width=2)
    left_frame.place(x=-3, y=-3)

    illustration_image = load_background("icons/login_bg.png", (331, 386))  # Replace with your image file
    illustration_label = ctk.CTkLabel(left_frame, image=illustration_image, text="")
    illustration_label.place(x=47, y=131)

    label_back_icon = load_iconctk("icons/back_icon.png" , (50, 50))  # Make sure logo.png is in your directory
    label_back = ctk.CTkLabel(left_frame, image=label_back_icon, text="", cursor="hand2")
    label_back.bind("<Button-1>", lambda e: __import__("home").show_home_screen(root))
    label_back.place(x=34, y=570)

    label_back_label = ctk.CTkLabel(left_frame, text="Back to Home", font=("Lato", 16), text_color= "#000000", cursor="hand2")
    label_back_label.place(x=95, y=580)
    label_back_label.bind("<Button-1>", lambda e: __import__("home").show_home_screen(root))



    # Right Side - Login Form Frame
    right_frame = ctk.CTkFrame(root, width=475, height=650, fg_color="white", corner_radius=5)
    right_frame.place(x=425, y=0)

    illustration_image_right = load_background("icons/default_bg.png", (470, 340), 0.2)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(right_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=150)

    login_label = ctk.CTkLabel(right_frame, text="Login", font=("Lato", 40, "bold"))
    login_label.place(x=188, y=90)

    # Inline error label for login
    global email_entry, password_entry, login_error_label
    login_error_label = ctk.CTkLabel(right_frame, text="", text_color="red", font=("Lato", 16), width=150, fg_color="transparent", justify = "center")
    login_error_label.place(x=160, y=165)  # Adjust y if needed


    email_label = ctk.CTkLabel(right_frame, text="Email", height=23, width= 77, font=("Lato", 16))
    email_label.place(x=70, y=196)
    email_entry = ctk.CTkEntry(right_frame, width=300, height=45, font=("Lato", 16), placeholder_text="abc@abc.com", corner_radius=5,
                            placeholder_text_color="#6d6d6d", border_color="#a99e9e", border_width= 1, fg_color="#d9d9d9")
    email_entry.place(x=88, y=219)

    password_label = ctk.CTkLabel(right_frame, text="Password", width=77, height= 23, font=("Lato", 16), bg_color="transparent", fg_color="transparent")
    password_label.place(x=88, y=301)
    password_entry = ctk.CTkEntry(right_frame, width=300, height=45, font=("Lato", 16), show="*", placeholder_text="********", 
                                placeholder_text_color="#6d6d6d", border_color="#a99e9e", border_width= 1, fg_color="#d9d9d9")
    password_entry.place(x=88, y=324)

    email_entry.bind("<KeyRelease>", lambda e: login_error_label.configure(text=""))
    password_entry.bind("<KeyRelease>", lambda e: login_error_label.configure(text=""))

    password_entry.bind("<Return>", lambda e: handle_login())  # Enter key binding


    # Show Password Function
    def toggle_password():
        password_entry.configure(show="" if password_entry.cget("show") == "*" else "*")

    show_password = ctk.CTkCheckBox(right_frame, text="Show Password", font=("Lato", 16), corner_radius= 6,command=toggle_password,
                                    bg_color="#e1dfff", fg_color="#e1dfff", border_width=2, border_color="#a99e9e", checkbox_height=20,
                                    checkbox_width=20, hover_color="#d9d9d9", checkmark_color="green")
    show_password.place(x=242, y=370)

    login_button = ctk.CTkButton(right_frame, text="Login", width=300, height=45, text_color="black", font=("Lato", 24, "bold"), command=handle_login,
                                corner_radius=5, fg_color="#17B8A6", border_color="#a99e9e", border_width=1, hover_color="#17B8A6", cursor="hand2")
    login_button.place(x=88, y=429)

    forgot_label = ctk.CTkLabel(right_frame, text="Forgot Password?", font=("Lato", 16), text_color="black", cursor="hand2")
    forgot_label.place(x=181, y=489.5)

    signup_label = ctk.CTkLabel(right_frame, text="Don't have an account? Sign Up", font=("Lato", 16), text_color="black", cursor="hand2")
    signup_label.place(x=138, y=516.5)

    def go_to_signup():
        show_gif_loader(root, message="Redirecting to Sign Up...")
        root.after(700, lambda: [hide_loader(), __import__("signup").open_signup_screen(root)])

    signup_label.bind("<Button-1>", lambda e: go_to_signup())