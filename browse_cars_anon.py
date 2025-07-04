import customtkinter as ctk
from browse_cars import open_browse_cars
from utils import load_iconctk, show_gif_loader, hide_loader
# from home_screen import show_home_screen
# from login_screen import show_login_screen
# from signup_screen import show_signup_screen


def open_browse_anon_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

    def go_home():
        from home import show_home_screen  # 💡 move inside
        show_gif_loader(root, "Returning Home...")
        root.after(700, lambda: [hide_loader(), show_home_screen(root)])

    def go_login():
        from login import open_login_screen  # 💡 move inside
        show_gif_loader(root, "Opening Login...")
        root.after(700, lambda: [hide_loader(), open_login_screen(root)])

    def go_signup():
        from signup import open_signup_screen  # 💡 move inside
        show_gif_loader(root, "Opening Sign Up...")
        root.after(700, lambda: [hide_loader(), open_signup_screen(root)])


    # Sidebar Frame
    sidebar = ctk.CTkFrame(root, width=150, height=650, corner_radius=0, fg_color="#e0e0e0")
    sidebar.place(x=0, y=0)  

    # Function to create sidebar buttons
    def create_sidebar_button(parent, image_path, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action=None):
        # img = ctk.CTkImage(light_image=Image.open(image_path), size=(icon_width, icon_height))
        btn = ctk.CTkButton(parent, image=load_iconctk(image_path,(icon_width, icon_height)),
                            fg_color="transparent", width=80, height=50, command=action, hover_color="#e0e0e0")
        btn.place(x=x_pos, y=y_pos)
        lbl = ctk.CTkLabel(parent, text=text, font=("Lato", 14), text_color="Black", justify="center", height=10)
        lbl.place(x= x_pos_lab, y= y_pos_lab)
        return btn
    

    # Sidebar Buttons
    buttons_data = [
        ("icons/pcds_logo.png", "", 16, 11, 100 ,100 , 0, 0, None),
        ("icons/home_icon.png", "Home", 33, 150, 75, 75, 57, 230, lambda: go_home()),
        ("icons/browse_car_icon.png", "Browse Cars", 33, 275, 75, 75, 41, 345,None),
        # ("icons/manage_customer_icon.png", "Manage\nCustomer", 41, 325, 50, 50, 49, 382, None),
        # ("icons/manage_staff_icon.png", "Manage\nStaff", 41, 385, 50, 50, 51, 435, None),
        ("icons/user.png", "Sign Up", 33, 400, 75, 75, 45, 480, lambda: go_signup()),
        ("icons/auth_icon.jpg", "Log In", 33, 541, 75, 75, 45, 605, lambda: go_login())
    ]

    for img, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action in buttons_data:
        create_sidebar_button(sidebar, img, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action)

    # Main Content Area
    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)
    
    open_browse_cars(root, main_frame)

    




    
