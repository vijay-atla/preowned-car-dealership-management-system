import customtkinter as ctk
from PIL import Image, ImageTk
from utils import load_background, load_iconctk, show_gif_loader, hide_loader

def show_home_screen(root):

    # Clear entire root window
    for widget in root.winfo_children():
        widget.destroy()

    # Load Background
    bg_photo=load_background("icons/home_screen.jpg", (900,650), 1)

    # Place background image
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")
    bg_label.image = bg_photo  # prevent garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # === Button Actions ===
    # Navigation handlers
    def go_to_login():
        show_gif_loader(root, "Opening Login Page...")
        root.after(1000, lambda: switch_to("login"))

    def go_to_signup():
        show_gif_loader(root, "Opening Sign Up Page...")
        root.after(1000, lambda: switch_to("signup"))

    def go_to_search():
        show_gif_loader(root, "Browsing Cars...")
        root.after(1000, lambda: switch_to("browse"))

    # === Very Simple Switch Logic ===
    def switch_to(screen):
        hide_loader()
        if screen == "login":
            from login import open_login_screen
            open_login_screen(root)
        elif screen == "signup":
            from signup import open_signup_screen
            open_signup_screen(root)
        elif screen == "browse":
            from browse_cars_anon import open_browse_anon_screen
            open_browse_anon_screen(root)

    # === Buttons ===
    search_btn = ctk.CTkButton(root, text="Browse Cars", image=load_iconctk("icons/browse_car_icon.png", (100, 100)), width=90, height=90, compound="top",
                              fg_color="#ffffff", hover_color="#ffffff", corner_radius=0, border_color="#ffffff", border_width=0, bg_color="#ffffff",
                              text_color="black", font=("Lato", 16), background_corner_colors=None, command=go_to_search)
    search_btn.place(x=770, y=325)

    login_btn = ctk.CTkButton(root, text="Login", image=load_iconctk("icons/auth_icon.jpg", (100, 100)), width=90, height=90, compound="top",
                              fg_color="#ffffff", hover_color="#ffffff", border_width=0,corner_radius=0, border_color="#ffffff", bg_color="#ffffff",
                              text_color="black", background_corner_colors=None, font=("Lato", 16), command=go_to_login)
    login_btn.place(x=25, y=458)

    signup_btn = ctk.CTkButton(root, text="Sign Up", image=load_iconctk("icons/user.png", (80, 80)), width=80, height=80, compound="top",
                               fg_color="#ffffff", background_corner_colors=None, hover_color="#cccccc",  border_width=0,corner_radius=0, border_color="#ffffff", 
                                text_color="black", font=("Lato", 16),
                               command=go_to_signup)
    signup_btn.place(x=750, y=520)
