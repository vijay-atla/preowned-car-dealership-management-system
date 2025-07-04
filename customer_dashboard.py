import customtkinter as ctk
from PIL import Image
from tkinter import messagebox  # For pop-up messages
from utils import load_background, load_iconctk, show_gif_loader, hide_loader, show_custom_confirm
import subprocess
import sys
from database_utils import get_user_details
from session import current_user
from browse_cars import open_browse_cars
from customer_purchases import open_customer_purchases
from customer_my_test_drives import open_customer_my_test_drives
from customer_inquires import open_customer_inquiries
from profile_settings import open_profile_settings
from logout import logout_user
from customer_reviews import open_customer_reviews_ratings





global nroot
current_page = "dashboard"

def open_customer_dashboard(root):
    global nroot
    nroot = root

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
        ("icons/home_icon.png", "Home", 33, 150, 75, 75, 57, 230, lambda: check_and_go_home(nroot)),
        ("icons/browse_car_icon.png", "Browse Cars", 33, 275, 75, 75, 41, 345, lambda: check_and_browse(nroot)),
        # ("icons/manage_customer_icon.png", "Manage\nCustomer", 41, 325, 50, 50, 49, 382, None),
        # ("icons/manage_staff_icon.png", "Manage\nStaff", 41, 385, 50, 50, 51, 435, None),
        ("icons/user-profile.png", "Profile &\nSettings", 33, 400, 75, 75, 45, 480, lambda: go_to_profile(nroot)),
        ("icons/logout_icon.png", "Log Out", 33, 541, 60, 60, 45, 605, lambda: logout(root))
    ]

    for img, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action in buttons_data:
        create_sidebar_button(sidebar, img, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action)

    
    open_customer_dashboard_main_frame(nroot)

# loggedin_user = get_user_details(sys.argv[1])
# current_user.update(loggedin_user)

# === DASHBOARD BUTTON ACTIONS ===

def go_to_test_drives(root):
    global current_page, main_frame
    if current_page == "dashboard":
        switch_to_page(lambda: open_customer_my_test_drives(root, main_frame))
        set_page("test_drives")
    else:
        confirm_page_switch(root, "My Test Drives", lambda: [switch_to_page(lambda: open_customer_my_test_drives(root, main_frame)), set_page("test_drives")])



def go_to_inquiries(root):
    global current_page, main_frame
    if current_page == "dashboard":
        switch_to_page(lambda: open_customer_inquiries(root, main_frame))
        set_page("inquiries")
    else:
        confirm_page_switch(root, "My Inquiries", lambda: [switch_to_page(lambda: open_customer_inquiries(root, main_frame)), set_page("inquiries")])


def go_to_purchases(root):
    global current_page, main_frame
    if current_page == "dashboard":
        switch_to_page(lambda: open_customer_purchases(root, main_frame))
        set_page("purchases")
    else:
        confirm_page_switch(root, "My Purchases", lambda: [switch_to_page(lambda: open_customer_purchases(root, main_frame)), set_page("purchases")])


def go_to_profile(root):
    global current_page, main_frame
    if current_page == "dashboard":
        switch_to_page(lambda: open_profile_settings(root, main_frame))
        set_page("profile")
    else:
        confirm_page_switch(root, "Profile & Settings", lambda: [switch_to_page(lambda: open_profile_settings(root, main_frame)), set_page("profile")])

def go_to_reviews(root):
    global current_page, main_frame
    if current_page == "dashboard":
        switch_to_page(lambda: open_customer_reviews_ratings(root, main_frame))
        set_page("reviews")
    else:
        confirm_page_switch(root, "My Reviews & Ratings", lambda: [switch_to_page(lambda: open_customer_reviews_ratings(root, main_frame)), set_page("reviews")])




def logout(root):
    show_custom_confirm(
        "⚠️ Are you sure you want to logout?",
        on_yes=lambda: logout_user(root, main_frame),
        on_no=None,
        title="Confirm Logout",
        root=root
    )


# === PAGE CHECKS ===
def check_and_go_home(root):
    global current_page
    if current_page == "dashboard":
        open_customer_dashboard_main_frame(root)
    else:
        confirm_page_switch(root, "Go to Dashboard", lambda: [open_customer_dashboard_main_frame(root), set_page("dashboard")])


def check_and_browse(root):
    global current_page, main_frame
    if current_page == "dashboard":
        switch_to_page(lambda: open_browse_cars(root, main_frame))
        set_page("browse_cars")
    else:
        confirm_page_switch(root, "Browse Cars", lambda: [switch_to_page(lambda: open_browse_cars(root, main_frame)), set_page("browse_cars")])


def set_page(page):
    global current_page
    current_page = page


def switch_to_page(callback_func):
    global main_frame
    main_frame.destroy()
    main_frame = ctk.CTkFrame(nroot, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)
    show_gif_loader(main_frame, message="Loading...")
    main_frame.after(600, lambda: [callback_func(), hide_loader()])


# === CONFIRM SWITCH ===
def confirm_page_switch(root, title, on_yes_callback):
    popup = ctk.CTkToplevel(root)
    popup.geometry("350x150")
    popup.title("Confirm Navigation")
    popup.configure(fg_color="#F9F9C5")
    popup.attributes("-topmost", True)

    popup.update_idletasks()
    x = root.winfo_rootx() + 350
    y = root.winfo_rooty() + 200
    popup.geometry(f"350x150+{x}+{y}")

    ctk.CTkLabel(popup, text="⚠️ Are you sure you want to exit\nthis screen?", font=("Lato", 16, "bold"), text_color="#333333").place(x=55, y=30)

    ctk.CTkButton(popup, text="Yes", fg_color="#30b8a9", text_color="black", command=lambda: [popup.destroy(), on_yes_callback()], width=80).place(x=70, y=100)
    ctk.CTkButton(popup, text="No", fg_color="#d9534f", text_color="white", command=popup.destroy, width=80).place(x=200, y=100)




# === MAIN FRAME ===

def open_customer_dashboard_main_frame(root):
    global main_frame

    # Main Content Area
    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.3)  # Replace with your image file
    illustration_label_right = ctk.CTkLabel(main_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)


    # Welcome Message
    welcome_label = ctk.CTkLabel(main_frame, text="Customer Dashboard", font=("Lato", 30, "bold"), text_color="#008080", fg_color="#ffffff")
    welcome_label.place(x=53, y=35)  

    sub_text = ctk.CTkLabel(main_frame, text=f"Welcome, {current_user["full_name"].title()}!", font=("Lato", 20), fg_color="#ffffff")
    sub_text.place(x=425, y=64)

    # Grid Layout for Dashboard Buttons
    dashboard_buttons = [
        ("icons/browse_car_icon.png", "Browse Cars", 63, 138, lambda: check_and_browse(root)),
        # ("icons/manage_cars_icon.png", "Manage Car Listings", 222, 180, manage_car_listings),
        ("icons/test_drive_icon.png", "My Test Drives", 300, 138, lambda: go_to_test_drives(root)),
        ("icons/inquiry_icon.png", "My Inquiries", 537, 138, lambda: go_to_inquiries(root)),
        # ("icons/process_sale_icon.png", "Process a Sale", 46, 415, process_sale),
        # ("icons/download_invoide_icon.png", "Download an Invoice", 74, 404, download_invoice),
        ("icons/my_purchases_icon.png", "My Purchases", 63, 373, lambda: go_to_purchases(root)),
        ("icons/reviews_icon.png", "My Reviews & Ratings", 300, 373, lambda: go_to_reviews(root))
    ]

    for img, text, x_pos, y_pos, action in dashboard_buttons:
        img_obj = ctk.CTkImage(light_image=Image.open(img), size=(90, 90))
        btn = ctk.CTkButton(main_frame, text=text, image=img_obj, compound="top", width=150, height=150, command=action,
                            font=("Lato", 14), anchor="center", border_color="#808080", border_width= 5, fg_color="#ffffff", 
                            text_color="black", hover_color = "#ffffff", corner_radius=10)
        btn.place(x=x_pos, y=y_pos)  


