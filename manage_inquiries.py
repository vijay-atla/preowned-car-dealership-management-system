import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message
from session import current_user
from database_utils import fetch_customer_inquiries, update_inquiry_message

def open_manage_inquiries(root, parent_frame, car_id = None):
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
                 text="  Manage Inquiries", font=("Lato", 30, "bold"),
                 text_color="#008080", fg_color="#ffffff", compound="left").place(x=46, y=58)

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    # --- Fetch All Inquiries ---
    all_inquiries = fetch_customer_inquiries(car_id = car_id)

    ongoing_inquiries = []
    past_inquiries = []

    for inquiry in all_inquiries:
        inquiry_entry = {
            "inquiry_id": inquiry['message_id'],
            "created_at": inquiry['created_at'].strftime("%m/%d/%Y") if inquiry['created_at'] else "",
            "customer_name": inquiry['customer_name'].title(),
            "car_details": f"{inquiry['car_make']} {inquiry['car_model']} {inquiry['car_year']}",
            "message_text": inquiry['message_text'],
            "status": inquiry['status'],
            "updated_at": inquiry['updated_at'] if inquiry['updated_at'] else ""
        }

        if inquiry['status'] == "Pending":
            ongoing_inquiries.append(inquiry_entry)
        else:
            past_inquiries.append(inquiry_entry)

    # Create Sections
    create_manage_inquiries_section(parent_frame, "Ongoing Inquiries", ongoing_inquiries, y_start=130, include_filter=False)
    create_manage_inquiries_section(parent_frame, "Past Inquiries", past_inquiries, y_start=350, include_filter=True)

# --- Create Scrollable Section Helper ---
def create_manage_inquiries_section(parent, label_text, entries, y_start, include_filter=False):
    global previous_inquiries_scrollable
    headers = ["Inquiry Date", "Customer Name", "Car Details", "Message", "Status", "Last Updated", "Actions"]
    col_widths = [75, 100, 120, 160, 50, 90, 70]
    text_padding = 10

    # Section Title
    ctk.CTkLabel(parent, text=label_text, font=("Lato", 16)).place(x=25, y=y_start)

    frame_height = 230 if include_filter else 160
    # Outer Frame
    frame = ctk.CTkFrame(parent, width=700, height=frame_height, fg_color="#ffffff",
                         corner_radius=10, border_color="#808080", border_width=5)
    frame.place(x=24, y=y_start + 30)

    # --- Filter Row (only for Previous Inquiries Section) ---
    if include_filter:
        create_inquiries_filter_row(frame)

    header_y = 40 if include_filter else 10
    scroll_y = header_y + 30
    scroll_height = 135 if include_filter else 100

    # Table Header
    header = ctk.CTkFrame(frame, fg_color="#BABABA", height=30, width=675, corner_radius=0)
    header.place(x=12, y=header_y)

    for i, text in enumerate(headers):
        ctk.CTkLabel(header, text=text, anchor="w", justify="left",
                     font=("Lato", 12, "bold"), width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=0)

    # Scrollable Table
    scrollable = ctk.CTkScrollableFrame(frame, width=665, height=scroll_height, fg_color="white", scrollbar_button_color="#D9D9D9")
    scrollable._scrollbar.configure(height=scroll_height)
    scrollable.place(x=6, y=scroll_y)

    if include_filter:
        previous_inquiries_scrollable = scrollable

    # Populate Rows
    if entries:
        for entry in entries:
            create_single_inquiry_row(scrollable, entry)
    else:
        ctk.CTkLabel(scrollable, text=f"No {label_text.lower()} found.",
                     font=("Lato", 14), text_color="#888888").pack(pady=30)

# --- Create Single Inquiry Row ---
def create_single_inquiry_row(parent, entry):
    col_widths = [70, 90, 120, 150, 60, 100, 70]
    text_padding = 10

    row = ctk.CTkFrame(parent, fg_color="#F3F3F3", height=30, width=670, corner_radius=0)
    row.pack(pady=3)

    fields_to_display = [
        "created_at",
        "customer_name",
        "car_details",
        "message_text",
        "status",
        "updated_at"
    ]

    for i, field in enumerate(fields_to_display):
        val = entry.get(field, "")
        ctk.CTkLabel(row, text=val, font=("Lato", 11), anchor="w", width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=3)

    # (Icons will be placed later here!)
    status = entry["status"]
    if status == "Pending":
        # 📝 Respond Icon
        respond_icon = load_iconctk("icons/response_icon.png", (20, 20))
        respond_label = ctk.CTkLabel(row, image=respond_icon, text="", cursor="hand2")
        respond_label.image = respond_icon
        respond_label.place(x=610, y=5)
        respond_label.bind("<Button-1>", lambda e, inquiry=entry: open_respond_inquiry_popup(parent.master, inquiry))

        # 🗑️ Withdraw Icon
        withdraw_icon = load_iconctk("icons/delete_inquiry_icon.png", (20, 20))
        withdraw_label = ctk.CTkLabel(row, image=withdraw_icon, text="", cursor="hand2")
        withdraw_label.image = withdraw_icon
        withdraw_label.place(x=640, y=5)
        withdraw_label.bind("<Button-1>", lambda e, inquiry=entry: open_withdraw_inquiry_popup(parent.master, inquiry, by_role="staff"))

    else:
        # 🔎 View Response Icon
        view_icon = load_iconctk("icons/response_icon.png", (20, 20))
        view_label = ctk.CTkLabel(row, image=view_icon, text="", cursor="hand2")
        view_label.image = view_icon
        view_label.place(x=610, y=5)
        view_label.bind("<Button-1>", lambda e, inquiry=entry: open_view_inquiry_response_popup(parent.master, inquiry))

        # 🗑️ Withdraw Icon
        withdraw_icon = load_iconctk("icons/delete_inquiry_icon.png", (20, 20))
        withdraw_label = ctk.CTkLabel(row, image=withdraw_icon, text="", cursor="hand2")
        withdraw_label.image = withdraw_icon
        withdraw_label.place(x=640, y=5)
        withdraw_label.bind("<Button-1>", lambda e, inquiry=entry: open_withdraw_inquiry_popup(parent.master, inquiry, by_role="staff"))





def create_inquiries_filter_row(frame):
    global inquiries_filter_vars
    inquiries_filter_vars = {
        "status_var": None,
        "search_var": None,
        "timer_id": None
    }

    filter_row = ctk.CTkFrame(frame, fg_color="#d9d9d9", height=30, width=677)
    filter_row.place(x=12, y=8)

    # Filter By Label + Icon
    funnel_icon = load_iconctk("icons/filter_icon.png", (20, 20))
    ctk.CTkLabel(filter_row, text=" Filter by", image=funnel_icon, compound="left", font=("Lato", 12)).place(x=10, y=1)

    # Status Dropdown
    inquiries_filter_vars["status_var"] = ctk.StringVar()
    status_menu = ctk.CTkOptionMenu(filter_row, values=["All", "Responded", "Withdrawn"], width=120, height=20,
                                    fg_color="white", text_color="#008080", font=("Lato", 12), variable=inquiries_filter_vars["status_var"])
    status_menu.place(x=80, y=4)
    status_menu.set("All")
    status_menu.configure(command=lambda choice: trigger_inquiries_filter_reload())

    # Search Box
    search_icon = load_iconctk("icons/search_icon.png", (20, 20))
    ctk.CTkLabel(filter_row, image=search_icon, text="", fg_color="#d9d9d9").place(x=230, y=1)

    inquiries_filter_vars["search_var"] = ctk.StringVar()
    search_entry = ctk.CTkEntry(filter_row, width=200, height=20, corner_radius=15, fg_color="white",
                                text_color="#008080", font=("Lato", 12), textvariable=inquiries_filter_vars["search_var"])
    search_entry.place(x=260, y=4)

    search_entry.bind("<KeyRelease>", on_inquiries_search_keypress)

    # Search Button
    ctk.CTkButton(filter_row, text="Search", font=("Lato", 12), width=120, height=20,
                  fg_color="#008080", command=trigger_inquiries_filter_reload).place(x=480, y=3)


def on_inquiries_search_keypress(event=None):
    if inquiries_filter_vars["timer_id"]:
        event.widget.after_cancel(inquiries_filter_vars["timer_id"])
    inquiries_filter_vars["timer_id"] = event.widget.after(400, trigger_inquiries_filter_reload)

def trigger_inquiries_filter_reload():
    status = inquiries_filter_vars["status_var"].get()
    search = inquiries_filter_vars["search_var"].get()

    if status == "All":
        status = None

    all_inquiries = fetch_customer_inquiries(status_filter=status, search_text=search)

    past_inquiries = []
    for inquiry in all_inquiries:
        if inquiry["status"] in ["Responded", "Withdrawn"]:
            inquiry_entry = {
                "inquiry_id": inquiry['message_id'],
                "created_at": inquiry['created_at'].strftime("%m/%d/%Y") if inquiry['created_at'] else "",
                "customer_name": inquiry['customer_name'].title(),
                "car_details": f"{inquiry['car_make']} {inquiry['car_model']} {inquiry['car_year']}",
                "message_text": inquiry['message_text'],
                "status": inquiry['status'],
                "updated_at": inquiry['updated_at'].strftime("%m/%d/%Y") if inquiry['updated_at'] else ""
            }
            past_inquiries.append(inquiry_entry)

    refresh_previous_inquiries_section(past_inquiries)

def refresh_previous_inquiries_section(entries):
    if previous_inquiries_scrollable:
        for widget in previous_inquiries_scrollable.winfo_children():
            widget.destroy()

        if entries:
            for entry in entries:
                create_single_inquiry_row(previous_inquiries_scrollable, entry)
        else:
            ctk.CTkLabel(previous_inquiries_scrollable, text="No past inquiries found.",
                         font=("Lato", 14, "bold"), text_color="#888888").pack(pady=20)




def open_respond_inquiry_popup(parent_frame, inquiry):
    popup_width = 500
    popup_height = 400

    # Center over parent_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    respond_popup = ctk.CTkToplevel()
    respond_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    respond_popup.title("Respond to Inquiry")
    respond_popup.resizable(False, False)
    respond_popup.grab_set()

    # Labels
    ctk.CTkLabel(respond_popup, text="Inquiry:", font=("Lato", 16)).place(x=40, y=20)
    ctk.CTkLabel(respond_popup, text="Your Response:", font=("Lato", 16)).place(x=40, y=170)

    # Inquiry Textbox (Readonly)
    inquiry_textbox = ctk.CTkTextbox(respond_popup, width=400, height=80, font=("Lato", 13))
    inquiry_textbox.place(x=40, y=50)
    inquiry_textbox.insert("1.0", inquiry["message_text"])
    inquiry_textbox.configure(state="disabled")

    # Response Textbox (Editable)
    response_textbox = ctk.CTkTextbox(respond_popup, width=400, height=80, font=("Lato", 13))
    response_textbox.place(x=40, y=200)

    def submit_response():
        new_response = response_textbox.get("1.0", "end").strip()

        if not new_response:
            show_custom_message("Warning", "Response message cannot be empty.", type="warning")
            return

        success, message = update_inquiry_message(inquiry["inquiry_id"], new_response, by_role=current_user["role"], user_id=current_user["user_id"])

        if success:
            respond_popup.destroy()
            show_custom_message("Success", "Inquiry responded successfully!")
            open_manage_inquiries(nroot, main_frame)
        else:
            show_custom_message("Error", message, type="error")

    # Submit Button
    ctk.CTkButton(respond_popup, text="Submit Response", width=180, height=35, command=submit_response).place(x=160, y=320)


from database_utils import withdraw_inquiry
from utils import show_custom_message

def open_withdraw_inquiry_popup(parent_frame, inquiry, by_role="staff"):
    if inquiry["status"] == "Withdrawn":
        show_custom_message("Info", "This inquiry has already been withdrawn/deleted.", type="info")
        return

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

    # Confirmation Label
    ctk.CTkLabel(withdraw_popup, text="Are you sure you want to withdraw this inquiry?", 
                 font=("Lato", 16), wraplength=360, justify="center").pack(pady=40)

    def confirm_withdraw():
        success, message = withdraw_inquiry(inquiry["inquiry_id"], by_role=current_user["role"])

        if success:
            withdraw_popup.destroy()
            show_custom_message("Success", "Inquiry withdrawn successfully!")
            open_manage_inquiries(nroot, main_frame)
        else:
            show_custom_message("Error", message, type="error")
            withdraw_popup.destroy()

    # Yes and No Buttons
    ctk.CTkButton(withdraw_popup, text="Yes", width=100, command=confirm_withdraw).place(x=90, y=140)
    ctk.CTkButton(withdraw_popup, text="No", width=100, fg_color="#A9A9A9", command=withdraw_popup.destroy).place(x=210, y=140)



def open_view_inquiry_response_popup(parent_frame, inquiry):
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

    # --- Fetch latest inquiry details ---
    details = fetch_customer_inquiries(message_id=inquiry["inquiry_id"])
    inquiry_message = details["message_text"] if details else "No inquiry message found."
    response_message = details["response_text"] if details and details["response_text"] else "No response provided yet."
    staff_id = f"Staff ID: {details["staff_id"]}" if details and details["staff_id"] else ""

    # Inquiry Section
    ctk.CTkLabel(view_popup, text="Customer Inquiry:", font=("Lato", 16)).place(x=40, y=20)

    inquiry_textbox = ctk.CTkTextbox(view_popup, width=400, height=80, font=("Lato", 13))
    inquiry_textbox.place(x=40, y=50)
    inquiry_textbox.insert("1.0", inquiry_message)
    inquiry_textbox.configure(state="disabled")

    # Response Section
    ctk.CTkLabel(view_popup, text="Staff Response:", font=("Lato", 16)).place(x=40, y=170)

    response_textbox = ctk.CTkTextbox(view_popup, width=400, height=80, font=("Lato", 13))
    response_textbox.place(x=40, y=200)
    response_textbox.insert("1.0", f"{staff_id}\n\n {response_message}")
    response_textbox.configure(state="disabled")

    # OK Button
    ctk.CTkButton(view_popup, text="OK", width=150, height=35, command=view_popup.destroy).place(x=175, y=320)
