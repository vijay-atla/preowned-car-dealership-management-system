import customtkinter as ctk
from PIL import Image
from tkinter import messagebox  # For pop-up messages
from utils import load_background, load_iconctk, show_gif_loader,hide_loader, show_custom_confirm
import subprocess
import sys
from session import current_user
from database_utils import get_user_details
from add_car_listing import open_add_car_listing
from manage_staff import open_manage_staff
from manage_customers import open_manage_customers
from browse_cars import open_browse_cars
from manage_car_listing import open_manage_car_listing
from process_sales import open_process_sales
from manage_testdrives import open_manage_test_drives
from manage_inquiries import open_manage_inquiries
from sales_history import open_sales_history
from logout import logout_user
from profile_settings import open_profile_settings
from reports_analytics import open_admin_reports
from manage_reviews import open_manage_reviews



global nroot
current_page = "dashboard"  # default landing screen


def open_admin_dashboard(root):

    # Clear previous screen
    for widget in root.winfo_children():
        widget.destroy()
    
    nroot=root

    # Sidebar Frame
    sidebar = ctk.CTkFrame(root, width=150, height=650, corner_radius=0, fg_color="#e0e0e0")
    sidebar.place(x=0, y=0)  
 

    # Function to create sidebar buttons
    def create_sidebar_button(parent, image_path, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action=None):
        # img = ctk.CTkImage(light_image=Image.open(image_path), size=(icon_width, icon_height))
        btn = ctk.CTkButton(parent, image=load_iconctk(image_path,(icon_width, icon_height)),
                            fg_color="transparent", width=80, height=50, command=action, hover_color="#e0e0e0")
        btn.place(x=x_pos, y=y_pos)
        lbl = ctk.CTkLabel(parent, text=text, font=("Lato", 12), text_color="Black", justify="center")
        lbl.place(x= x_pos_lab, y= y_pos_lab)
        return btn


        # Sidebar Buttons
    buttons_data = [
        ("icons/pcds_logo.png", "", 16, 11, 100 ,100 , 0, 0, None),
        ("icons/home_icon.png", "Home", 41, 125, 50, 50, 57, 174, lambda: check_and_go_home(nroot)),
        ("icons/browse_car_icon.png", "Browse Cars", 41, 204, 50, 50, 41, 250, lambda: check_and_go_browse(nroot)),
        ("icons/manage_customer_icon.png", "Manage\nCustomer", 41, 293, 50, 50, 49, 347, lambda: check_and_go_manage_customers(nroot)),
        ("icons/manage_staff_icon.png", "Manage\nStaff", 41, 385, 50, 50, 51, 435, lambda: check_and_go_manage_staff(nroot)),
        ("icons/user-profile.png", "Profile &\nSettings", 41, 470, 50, 50, 49, 525, lambda: check_and_go_profile(nroot)),
        ("icons/logout_icon.png", "Log Out", 41, 560, 50, 50, 53, 614,  lambda: logout(root))
    ]

    for img, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action in buttons_data:
        create_sidebar_button(sidebar, img, text, x_pos, y_pos, icon_width, icon_height, x_pos_lab, y_pos_lab, action)

    open_admin_dashboard_main_frame(nroot)

# Functions for button actions

def logout(root):
    show_custom_confirm(
        "⚠️ Are you sure you want to logout?",
        on_yes=lambda: logout_user(root, main_frame),
        on_no=None,
        title="Confirm Logout",
        root=root
    )


def check_and_go_home(root):
    global current_page
    if current_page == "dashboard":
        open_admin_dashboard_main_frame(root)
    else:
        confirm_page_switch(root, "Go to Dashboard", lambda: [open_admin_dashboard_main_frame(root), set_page("dashboard")])

def check_and_go_browse(root):
    global current_page
    if current_page == "dashboard":
        open_browse_cars(root, main_frame)
        set_page("browse_cars")
    else:
        confirm_page_switch(root, "Go to Browse Cars", lambda: [open_browse_cars(root, main_frame), set_page("browse_cars")])

def set_page(page):
    global current_page
    current_page = page


def check_and_add_car_listing(root):
    global current_page
    if current_page == "dashboard":
        add_car_listing(root)
        set_page("add_car")
    else:
        confirm_page_switch(root, "Go to Add Car Listing", lambda: [add_car_listing(root), set_page("add_car")])


def check_and_go_manage_customers(root):
    global current_page
    if current_page == "dashboard":
        go_to_manage_customers(root)
        set_page("manage_customers")
    else:
        confirm_page_switch(root, "Go to Manage Customers", lambda: [go_to_manage_customers(root), set_page("manage_customers")])

def check_and_go_manage_staff(root):
    global current_page
    if current_page == "manage_staff":
        go_to_manage_staff(root)
    else:
        confirm_page_switch(root, "Go to Manage Staff", lambda: [go_to_manage_staff(root), set_page("manage_staff")])
        

def go_to_manage_staff(root):
    global main_frame
    main_frame.destroy()
    
    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Manage Staff Page...")  # ⏳ Show loader

    # Use a slight delay to simulate load and allow UI to update
    main_frame.after(700, lambda: [open_manage_staff(root, main_frame), hide_loader()])  # chicha-style reusable


def go_to_manage_customers(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Manage Customers Page...")

    main_frame.after(700, lambda: [open_manage_customers(root, main_frame), hide_loader()])



def add_car_listing(root):
    global main_frame
    main_frame.destroy()
    
    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Add Car Page...")  # ⏳ Show loader

    # Use a slight delay to simulate load and allow UI to update
    main_frame.after(700, lambda: [open_add_car_listing(root, main_frame), hide_loader()])  # chicha-style reusable


def go_to_manage_car_listing(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Manage Car Listings Page...")

    main_frame.after(700, lambda: [open_manage_car_listing(root, main_frame), hide_loader()])


def check_and_go_manage_car_listing(root):
    global current_page
    if current_page == "dashboard":
        go_to_manage_car_listing(root)
        set_page("manage_car_listing")
    else:
        confirm_page_switch(root, "Go to Manage Car Listings",
                            lambda: [go_to_manage_car_listing(root), set_page("manage_car_listing")])


def check_and_go_manage_test_drives(root):
    global current_page
    if current_page == "dashboard":
        go_to_manage_test_drives(root)
        set_page("manage_test_drives")
    else:
        confirm_page_switch(root, "Go to Manage Test Drives",
                            lambda: [go_to_manage_test_drives(root), set_page("manage_test_drives")])


def go_to_manage_test_drives(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Manage Test Drives Page...")

    main_frame.after(700, lambda: [open_manage_test_drives(root, main_frame), hide_loader()])


def check_and_go_manage_inquiries(root):
    global current_page
    if current_page == "dashboard":
        go_to_manage_inquiries(root)
        set_page("manage_inquiries")
    else:
        confirm_page_switch(root, "Go to Manage Inquiries",
                            lambda: [go_to_manage_inquiries(root), set_page("manage_inquiries")])

def go_to_manage_inquiries(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Manage Inquiries Page...")

    main_frame.after(700, lambda: [open_manage_inquiries(root, main_frame), hide_loader()])


def check_and_go_process_sale(root):
    global current_page
    if current_page == "dashboard":
        go_to_process_sale(root)
        set_page("process_sale")
    else:
        confirm_page_switch(root, "Go to Process Sale",
                            lambda: [go_to_process_sale(root), set_page("process_sale")])

def go_to_process_sale(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Process Sale Page...")

    main_frame.after(700, lambda: [open_process_sales(root, main_frame), hide_loader()])

def check_and_go_profile(root):
    global current_page
    if current_page == "dashboard":
        go_to_profile(root)
        set_page("profile")
    else:
        confirm_page_switch(root, "Go to Profile", lambda: [go_to_profile(root), set_page("profile")])

def go_to_profile(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Profile Page...")
    main_frame.after(700, lambda: [open_profile_settings(root, main_frame), hide_loader()])
    

def go_to_admin_reports(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Reports & Analytics...")
    main_frame.after(700, lambda: [open_admin_reports(root, main_frame), hide_loader()])


def check_and_go_sales_history(root):
    global current_page
    if current_page == "dashboard":
        go_to_sales_history(root)
        set_page("sales_history")
    else:
        confirm_page_switch(root, "Go to Sales History", lambda: [go_to_sales_history(root), set_page("sales_history")])

def go_to_sales_history(root):
    global main_frame
    main_frame.destroy()

    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    show_gif_loader(main_frame, message="Loading Sales History Page...")

    main_frame.after(700, lambda: [open_sales_history(root, main_frame), hide_loader()])


def manage_reviews(root):
    global main_frame
    main_frame.destroy()
    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)
    show_gif_loader(main_frame, message="Loading Manage Reviews Page...")
    main_frame.after(600, lambda: [open_manage_reviews(root, main_frame), hide_loader()])



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

    def yes_action():
        popup.destroy()
        on_yes_callback()

    def no_action():
        popup.destroy()

    ctk.CTkButton(popup, text="Yes", fg_color="#30b8a9", text_color="black", command=yes_action, width=80).place(x=70, y=100)
    ctk.CTkButton(popup, text="No", fg_color="#d9534f", text_color="white", command=no_action, width=80).place(x=200, y=100)



# Main Content Area
def open_admin_dashboard_main_frame(root):

    global main_frame
    # if main_frame is not None:
    #     main_frame.destroy()
    
    main_frame = ctk.CTkFrame(root, width=750, height=650, corner_radius=0, fg_color="#ffffff")
    main_frame.place(x=150, y=0)

    illustration_image_right = load_background("icons/default_bg.png", (750, 525), 0.2)
    illustration_label_right = ctk.CTkLabel(main_frame, image=illustration_image_right, text="")
    illustration_label_right.place(x=0, y=65)

    ctk.CTkLabel(main_frame, text="Admin Dashboard", font=("Lato", 30, "bold"),
                 text_color="#008080", fg_color="#ffffff").place(x=46, y=58)
    ctk.CTkLabel(main_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    dashboard_buttons = [
        ("icons/add_car_icon.png", "Add Car Listing", 46, 180, lambda: check_and_add_car_listing(root)),
        ("icons/manage_cars_icon.png", "Manage Car Listings", 222, 180, lambda: check_and_go_manage_car_listing(root)),
        ("icons/test_drive_icon.png", "Manage Test Drives", 398, 180, lambda: check_and_go_manage_test_drives(root)),
        ("icons/inquiry_icon.png", "Handle Inquiries", 574, 180, lambda: check_and_go_manage_inquiries(root)),
        ("icons/process_sale_icon.png", "Process a Sale", 46, 415, lambda: check_and_go_process_sale(root)),
        ("icons/sale_history_icon.png", "Sales History", 222, 415, lambda: check_and_go_sales_history(root)),
        ("icons/analytics_icon.png", "Reports & Analytics", 398, 415, lambda: go_to_admin_reports(root)),
        ("icons/reviews_icon.png", "Manage Reviews\n& Ratings", 574, 415, lambda: manage_reviews(root))
    ]

    for img, text, x, y, action in dashboard_buttons:
        img_obj = ctk.CTkImage(light_image=Image.open(img), size=(60, 60))
        ctk.CTkButton(main_frame, text=text, image=img_obj, compound="top", width=130, height=130, command=action,
                      bg_color="transparent", font=("Lato", 11), anchor="center", border_color="#808080", border_width=5,
                      fg_color="#ffffff", text_color="black", hover_color="#ffffff", corner_radius=10).place(x=x, y=y)

