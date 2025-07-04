import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message
from session import current_user
from database_utils import update_inquiry_message, withdraw_inquiry, fetch_customer_inquiries

def open_customer_inquiries(root, parent_frame):
    global nroot, main_frame
    nroot=root
    main_frame = parent_frame
    # Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Background Image
    bg_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=bg_image, text="").place(x=0, y=65)

    # Welcome + Title
    ctk.CTkLabel(parent_frame, image=load_iconctk("icons/inquiry_icon.png", (50, 50)),
                 text="  My Inquiries", font=("Lato", 30, "bold"),
                 text_color="#008080", fg_color="#ffffff", compound="left").place(x=46, y=58)

    ctk.CTkLabel(parent_frame, text=f"Welcome, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=425, y=80)

    # --- Fetch Real Customer Inquiries ---
    all_inquiries = fetch_customer_inquiries(cust_id=current_user['user_id'])
    recent_inquiries = []
    past_inquiries = []

    for inquiry in all_inquiries:
        inquiry_entry = {
            "inquiry_id": inquiry['message_id'],
            "created_at": inquiry['created_at'].strftime("%m/%d/%Y") if inquiry['created_at'] else "",
            "car_details": f"{inquiry['car_make']} {inquiry['car_model']} {inquiry['car_year']}",
            "message_text": inquiry['message_text'],
            "status": inquiry['status'],
            "updated_at": inquiry['updated_at'] if inquiry['updated_at'] else ""
        }

        if inquiry['status'] == "Pending":
            recent_inquiries.append(inquiry_entry)
        elif inquiry['status'] == "Responded":
            past_inquiries.append(inquiry_entry)

    # --- Create Sections ---
    create_inquiries_section(parent_frame, "Recent Inquiries", recent_inquiries, y_start=130)
    create_inquiries_section(parent_frame, "Past Inquiries", past_inquiries, y_start=365)

# --- Helper function to Create Inquiries Section ---
def create_inquiries_section(parent, label_text, entries, y_start):
    headers = ["Inquiry Date", "Car Details", "Message", "Status", "Last Updated", "Actions"]
    col_widths = [80, 130, 200, 60, 110, 100]
    text_padding = 10

    # Section Title
    ctk.CTkLabel(parent, text=label_text, font=("Lato", 16)).place(x=32, y=y_start)

    # Outer Frame
    frame = ctk.CTkFrame(parent, width=700, height=170, fg_color="#ffffff",
                         corner_radius=10, border_color="#808080", border_width=5)
    frame.place(x=31, y=y_start + 30)

    # Table Header
    header = ctk.CTkFrame(frame, fg_color="#BABABA", height=30, width=680, corner_radius=0)
    header.place(x=12, y=10)

    for i, text in enumerate(headers):
        ctk.CTkLabel(header, text=text, anchor="w", justify="left",
                     font=("Lato", 12, "bold"), width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=0)

    # Scrollable Table
    scrollable = ctk.CTkScrollableFrame(frame, width=665, height=110, fg_color="white", scrollbar_button_color="#D9D9D9")
    scrollable._scrollbar.configure(height=110)
    scrollable.place(x=6, y=40)

    # Populate Rows
    if entries:
        for entry in entries:
            create_single_inquiry_row(scrollable, entry)
    else:
        ctk.CTkLabel(scrollable, text=f"No {label_text.lower()} found.",
                    font=("Lato", 14), text_color="#888888").pack(pady=30)


# --- Create Single Inquiry Row ---
def create_single_inquiry_row(parent, entry):
    col_widths = [80, 130, 200, 60, 110, 100]
    text_padding = 10

    row = ctk.CTkFrame(parent, fg_color="#F3F3F3", height=30, width=670, corner_radius=0)
    row.pack(pady=3)

    # Define the field order
    fields_to_display = [
        entry["created_at"],
        entry["car_details"],
        entry["message_text"],
        entry["status"],
        entry["updated_at"]
    ]

    for i, val in enumerate(fields_to_display):
        ctk.CTkLabel(row, text=val, font=("Lato", 11), anchor="w", width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=3)

    status = entry["status"] # Status column (Pending / Responded / Withdrawn)

    if status == "Pending":
        # ✏️ Edit Icon
        edit_icon = load_iconctk("icons/edit_inquiry_icon.png", (20, 20))
        edit_label = ctk.CTkLabel(row, image=edit_icon, text="", cursor="hand2")
        edit_label.image = edit_icon
        edit_label.place(x=605, y=5)
        edit_label.bind("<Button-1>", lambda e, inquiry=entry: open_edit_inquiry_popup(parent, inquiry))  # 🛠️ Pass inquiry and parent_frame

        # 🗑️ Delete Icon (Withdraw)
        delete_icon = load_iconctk("icons/delete_inquiry_icon.png", (20, 20))
        delete_label = ctk.CTkLabel(row, image=delete_icon, text="", cursor="hand2")
        delete_label.image = delete_icon
        delete_label.place(x=635, y=5)
        delete_label.bind("<Button-1>", lambda e, inquiry=entry: open_withdraw_inquiry_popup(parent, inquiry))

    elif status == "Responded" or status == "Withdrawn":
        # 🔎 View Response Icon
        view_icon = load_iconctk("icons/response_icon.png", (20, 20))
        view_label = ctk.CTkLabel(row, image=view_icon, text="", cursor="hand2")
        view_label.image = view_icon
        view_label.place(x=620, y=5)
        view_label.bind("<Button-1>", lambda e, inquiry=entry: open_view_response_popup(parent, inquiry))



def open_edit_inquiry_popup(parent_frame, inquiry):
    popup_width = 450
    popup_height = 300

    # Center over parent_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    edit_popup = ctk.CTkToplevel()
    edit_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    edit_popup.title("Edit Your Inquiry")
    edit_popup.resizable(False, False)
    edit_popup.grab_set()

    ctk.CTkLabel(edit_popup, text="Edit Your Inquiry Message:", font=("Lato", 16)).place(x=40, y=30)

    message_textbox = ctk.CTkTextbox(edit_popup, width=370, height=120, font=("Lato", 13))
    message_textbox.place(x=40, y=70)

    # Pre-fill existing message
    message_textbox.insert("1.0", inquiry["message_text"])

    def submit_edit():
        new_message = message_textbox.get("1.0", "end").strip()

        if not new_message:
            show_custom_message("Warning", "Message cannot be empty.", type="warning")
            return

        success, message = update_inquiry_message(inquiry["inquiry_id"], new_message, by_role="customer")

        if success:
            edit_popup.destroy()
            show_custom_message("Success", "Inquiry updated successfully!")
            # Reload Customer Inquiries page cleanly
            open_customer_inquiries(nroot, main_frame)
        else:
            show_custom_message("Error", message, type="error")

    ctk.CTkButton(edit_popup, text="Update", width=150, height=35, command=submit_edit).place(x=150, y=220)


def open_withdraw_inquiry_popup(parent_frame, inquiry):
    popup_width = 400
    popup_height = 220

    # Center over parent_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    withdraw_popup = ctk.CTkToplevel()
    withdraw_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    withdraw_popup.title("Withdraw Inquiry")
    withdraw_popup.resizable(False, False)
    withdraw_popup.grab_set()

    # Label
    ctk.CTkLabel(withdraw_popup, text="Are you sure you want to withdraw this inquiry?", 
                 font=("Lato", 16), wraplength=360, justify="center").pack(pady=40)

    def confirm_withdraw():
        success, message = withdraw_inquiry(inquiry["inquiry_id"], by_role="customer")

        if success:
            withdraw_popup.destroy()
            show_custom_message("Success", "Inquiry withdrawn successfully!")
            # Reload Customer Inquiries page cleanly
            open_customer_inquiries(nroot, main_frame)
        else:
            withdraw_popup.destroy()
            show_custom_message("Error", message, type="error")
            

    # Yes and No Buttons
    ctk.CTkButton(withdraw_popup, text="Yes", width=100, command=confirm_withdraw).place(x=90, y=140)
    ctk.CTkButton(withdraw_popup, text="No", width=100, fg_color="#A9A9A9", command=withdraw_popup.destroy).place(x=210, y=140)


def open_view_response_popup(parent_frame, inquiry):
    popup_width = 500
    popup_height = 400

    # Center over parent_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    view_popup = ctk.CTkToplevel()
    view_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    view_popup.title("Inquiry and Response")
    view_popup.resizable(False, False)
    view_popup.grab_set()

    # --- Fetch latest inquiry and response text ---
    details = fetch_customer_inquiries(message_id = inquiry["inquiry_id"])

    inquiry_message = details["message_text"] if details else "No message found."
    response_message = details["response_text"] if details and details["response_text"] else "No response provided yet."

    # Inquiry Section
    ctk.CTkLabel(view_popup, text="Your Inquiry:", font=("Lato", 16)).place(x=40, y=30)

    inquiry_textbox = ctk.CTkTextbox(view_popup, width=400, height=100, font=("Lato", 13))
    inquiry_textbox.place(x=40, y=70)
    inquiry_textbox.insert("1.0", inquiry_message)
    inquiry_textbox.configure(state="disabled")

    # Response Section
    ctk.CTkLabel(view_popup, text="Response:", font=("Lato", 16)).place(x=40, y=190)

    response_textbox = ctk.CTkTextbox(view_popup, width=400, height=100, font=("Lato", 13))
    response_textbox.place(x=40, y=230)
    response_textbox.insert("1.0", response_message)
    response_textbox.configure(state="disabled")

    # OK Button
    ctk.CTkButton(view_popup, text="OK", width=150, height=35, command=view_popup.destroy).place(x=175, y=350)
