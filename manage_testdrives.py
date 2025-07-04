import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message, show_gif_loader, hide_loader
from session import current_user
from database_utils import get_ongoing_test_drives, get_previous_test_drives, update_test_drive_schedule, cancel_test_drive, update_test_drive_status
from schedule_popup import open_schedule_popup

def open_manage_test_drives(root, parent_frame, car_id=None):
    global main_frame
    main_frame = parent_frame
    # 1. Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Background and Titles
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=illustration_image, text="").place(x=0, y=65)

    ctk.CTkLabel(parent_frame, image=load_iconctk("icons/test_drive_icon.png", (50, 50)),
                 text="  Manage Test Drive Bookings", font=("Lato", 30, "bold"),
                 text_color="#008080", fg_color="#ffffff", compound="left").place(x=18, y=30)

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=425, y=80)

    # Fetch Ongoing Bookings
    ongoing_entries = []
    ongoing_rows = get_ongoing_test_drives(car_id)

    for row in ongoing_rows:
        ongoing_entries.append({
        "test_drive_id": row["test_drive_id"],
        "slot_datetime": row["slot_datetime"],
        "preferred_date": row["preferred_date"],
        "preferred_time": row["preferred_time"],
        "customer_name": row["customer_name"].title(),
        "car_info": row["car_info"],
        "status": row["status"],
        "updated_at": row["updated_at"]
    })

    create_manage_testdrives_section(  parent=parent_frame, label_text="Ongoing Test Drive Bookings", entries=ongoing_entries,
        icon_paths=["icons/confirm_icon.png", "icons/reschedule_icon.png", "icons/cancel_icon.png", "icons/mark_complete_icon.png"],
        y_start=132, include_filter=False )
 
    # Fetch Previous Bookings
    previous_entries = []
    previous_rows = get_previous_test_drives(car_id)

    for row in previous_rows:
        previous_entries.append({
            "slot_datetime": row["slot_datetime"],
            "customer_name": row["customer_name"].title(),
            "car_info": row["car_info"],
            "status": row["status"],
            "updated_at": row["updated_at"],
            "cancellation_reason": row.get("cancellation_reason", "")
        })

    create_manage_testdrives_section( parent=parent_frame, label_text="Previous Test Drive Bookings",  entries=previous_entries,
        icon_paths=["icons/comment_icon.png"], y_start=322, include_filter=True )

# Create Table Section
def create_manage_testdrives_section(parent, label_text, entries, icon_paths, y_start, include_filter=False):
    global previous_section_scrollable

    headers = ["Slot Date & Time", "Customer Name", "Car Details", "Status", "Last Modified on", "Actions"]
    col_widths = [125, 95, 145, 60, 140, 120]
    text_padding = 10

    # Section Title
    ctk.CTkLabel(parent, text=label_text, font=("Lato", 16)).place(x=20, y=y_start)

    # Outer Frame
    frame_height = 256 if include_filter else 150
    frame = ctk.CTkFrame(parent, width=707, height=frame_height, fg_color="#ffffff", corner_radius=10, border_color="#808080", border_width=5)
    frame.place(x=18, y=y_start + 30)

    # Filter Row (only for Previous Section)
    if include_filter:
        create_filter_row(frame)


    header_y = 40 if include_filter else 10
    scroll_y = header_y + 30
    scroll_height = 165 if include_filter else 90

    # Header
    header = ctk.CTkFrame(frame, fg_color="#BABABA", height=30, width=667, corner_radius=0)
    header.place(x=12, y=header_y)

    for i, text in enumerate(headers):
        ctk.CTkLabel(header, text=text, anchor="w", justify="left",
                     font=("Lato", 12, "bold"), width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=0)

    # Scrollable Table 
    scrollable = ctk.CTkScrollableFrame(frame, width=670, height=scroll_height, fg_color="white", scrollbar_button_color="#D9D9D9")
    scrollable._scrollbar.configure(height=scroll_height)
    scrollable.place(x=5, y=scroll_y)

    if include_filter:
        previous_section_scrollable = scrollable

    # Populate Entries
    if entries:
        for entry in entries:
            create_single_booking_row(scrollable, entry, icon_paths)
    else:
        no_data_message = "No previous test drive bookings found." if include_filter else "No ongoing test drive bookings found."
        ctk.CTkLabel(scrollable, text=no_data_message,
                    font=("Lato", 14, "bold"), text_color="#888888").pack(pady=20)


# Create Single Row
def create_single_booking_row(parent, entry, icon_paths):
    col_widths = [125, 95, 145, 60, 140, 120]
    text_padding = 10

    
    row = ctk.CTkFrame(parent, fg_color="#F3F3F3", height=30, width=667, corner_radius=0)
    row.pack(pady=3)

    # --- Display Fields ---
    display_values = [
        entry["slot_datetime"],
        entry["customer_name"],
        entry["car_info"],
        entry["status"],
        entry["updated_at"]
    ]

    for i, val in enumerate(display_values):
        if i == 2:  # Customer column
            if len(val) > 25:
                val = val[:22] + "..."
        ctk.CTkLabel(row, text=val, font=("Lato", 11), anchor="w", width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=3)


    # Action Icons
    if len(icon_paths) == 1:
        icon = load_iconctk(icon_paths[0], (20, 20))
        action_icon = ctk.CTkLabel(row, image=icon, text="", cursor="hand2")
        action_icon.place(x=585, y=3)
        # Bind Comment icon click
        if entry["status"] == "Cancelled":
            action_icon.bind("<Button-1>", lambda e, reason=entry.get("cancellation_reason", "No reason provided"): open_comment_popup(parent.master, reason))
        else:
            # For Completed status
            action_icon.bind("<Button-1>", lambda e: show_custom_message("Info", "No cancellation reason available for Completed bookings.", type="info"))
    else:
        for idx, path in enumerate(icon_paths):
            icon = load_iconctk(path, (20, 20))
            action_icon=ctk.CTkLabel(row, image=icon, text="", cursor="hand2")

            if idx == 0:  # Confirm Icon
                action_icon.bind("<Button-1>", lambda e, td_id=entry["test_drive_id"]: handle_test_drive_action(parent.master, td_id, "confirm"))
            if idx == 1:  # Reschedule Icon
                action_icon.bind("<Button-1>", lambda e, td_id=entry["test_drive_id"], ex_date=entry["preferred_date"], ex_time=entry["preferred_time"]: open_reschedule_popup(parent.master, td_id, ex_date, ex_time))
            if idx == 2:  # Cancel
                action_icon.bind("<Button-1>", lambda e, td_id=entry["test_drive_id"]: open_cancel_popup(parent.master, td_id))
            if idx == 3:  # Mark Complete Icon
                action_icon.bind("<Button-1>", lambda e, td_id=entry["test_drive_id"]: handle_test_drive_action(parent.master, td_id, "complete"))

            action_icon.place(x=560 + (idx * 28), y=3)




# Create Filter Row for Previous Section
def create_filter_row(frame):
    global filter_vars
    filter_vars = {
        "status_var": None,
        "search_var": None,
        "timer_id": None
    }

    filter_row = ctk.CTkFrame(frame, fg_color="#d9d9d9", height=30, width=690)
    filter_row.place(x=12, y=8)

    # --- Filter by (Dropdown) ---
    funnel_icon = load_iconctk("icons/filter_icon.png", (20, 20))  # Assuming you have a filter funnel icon
    ctk.CTkLabel(filter_row, text=" Filter by", image=funnel_icon, compound="left", font=("Lato", 12)).place(x=10, y=1)

    filter_vars["status_var"] = ctk.StringVar()
    status_menu = ctk.CTkOptionMenu(filter_row, values=["All", "Completed", "Cancelled"], width=120, height=20, 
                                    fg_color="white", text_color="#008080", font=("Lato", 12), variable=filter_vars["status_var"])
    status_menu.place(x=80, y=4)
    status_menu.set("All")

    status_menu.configure(command=lambda choice: trigger_filter_reload())

    # --- Search Value (Entry) ---
    search_icon = load_iconctk("icons/search_icon.png", (20, 20))  # Assuming you have a search magnifier icon
    ctk.CTkLabel(filter_row, image=search_icon, text="", fg_color="#d9d9d9").place(x=230, y=1)

    filter_vars["search_var"] = ctk.StringVar()
    search_entry = ctk.CTkEntry(filter_row, width=200, height=20, corner_radius=15, fg_color="white", text_color="#008080", font=("Lato", 12),
                                textvariable=filter_vars["search_var"])
    search_entry.place(x=260, y=4)

    search_entry.bind("<KeyRelease>", on_search_keypress)

    # --- Search Button ---
    ctk.CTkButton(filter_row, text="Search", font=("Lato", 12), width=120, height=20, fg_color="#008080", command=trigger_filter_reload).place(x=480, y=3)


# Debounce Search Typing
def on_search_keypress(event=None):
    if filter_vars["timer_id"]:
        event.widget.after_cancel(filter_vars["timer_id"])
    filter_vars["timer_id"] = event.widget.after(400, trigger_filter_reload)


# Refresh Previous Section After Filter
def trigger_filter_reload():
    status = filter_vars["status_var"].get()
    search = filter_vars["search_var"].get()

    if status == "All":
        status = None

    previous_rows = get_previous_test_drives(car_id=None, status_filter=status, search_text=search)

    previous_entries = []
    for row in previous_rows:
        previous_entries.append({
            "slot_datetime": row["slot_datetime"],
            "customer_name": row["customer_name"].title(),
            "car_info": row["car_info"],
            "status": row["status"],
            "updated_at": row["updated_at"],
            "cancellation_reason": row.get("cancellation_reason", "No reason provided")
        })

    refresh_previous_section(previous_entries)


def refresh_previous_section(previous_entries):
    if previous_section_scrollable:
        for widget in previous_section_scrollable.winfo_children():
            widget.destroy()

        if previous_entries:
            for entry in previous_entries:
                create_single_booking_row(previous_section_scrollable, entry, ["icons/comment_icon.png"])
        else:
            ctk.CTkLabel(previous_section_scrollable, text="No test drive bookings found.",
                         font=("Lato", 14, "bold"), text_color="#888888").pack(pady=20)


def open_reschedule_popup(root, test_drive_id, existing_date, existing_time):
    def on_confirm(new_date, new_time):
        success, message = update_test_drive_schedule(test_drive_id, new_date, new_time)
        if success:
            show_custom_message("Success", "Test drive rescheduled successfully!")
            
            open_manage_test_drives(root, main_frame)
        else:
            show_custom_message("Error", f"Failed to reschedule: {message}", type="error")

    open_schedule_popup(root, title="Reschedule Test Drive", on_confirm=on_confirm, existing_date=existing_date, existing_time=existing_time)    




def open_cancel_popup(root, test_drive_id):
    # Create Popup Window
    popup_width = 450
    popup_height = 300

    # Center over main_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    popup = ctk.CTkToplevel()
    popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    popup.title("Cancel Test Drive")
    popup.resizable(False, False)
    popup.grab_set()

    # Label
    ctk.CTkLabel(popup, text="Reason for Cancelling:", font=("Lato", 16)).place(x=40, y=30)

    # Multiline Textbox
    reason_textbox = ctk.CTkTextbox(popup, width=370, height=120, font=("Lato", 13))
    reason_textbox.place(x=40, y=70)

    # Submit Button
    def submit_cancel():
        reason = reason_textbox.get("1.0", "end").strip()

        if not reason:
            show_custom_message("Warning", "Please enter a reason for cancellation.", type="warning")
            return

        success, message = cancel_test_drive(test_drive_id, reason)

        if success:
            popup.destroy()
            show_custom_message("Success", "Test Drive cancelled successfully!")

            open_manage_test_drives(root, main_frame)
        else:
            show_custom_message("Error", f"Failed to cancel: {message}", type="error")

    ctk.CTkButton(popup, text="Submit", width=150, height=35, command=submit_cancel).place(x=150, y=220)



def handle_test_drive_action(root, test_drive_id, action_type):
    if action_type == "confirm":
        new_status = "Confirmed"
        confirmation_message = "Are you sure you want to confirm this Test Drive?"
    elif action_type == "complete":
        new_status = "Completed"
        confirmation_message = "Are you sure you want to mark this Test Drive as Completed?"
    else:
        return  # Invalid action

    # Popup dimensions
    popup_width = 400
    popup_height = 200

    # Center over main_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    # Create Confirmation Popup
    confirm_popup = ctk.CTkToplevel()
    confirm_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    confirm_popup.title("Confirmation")
    confirm_popup.resizable(False, False)
    confirm_popup.grab_set()

    ctk.CTkLabel(confirm_popup, text=confirmation_message, font=("Lato", 14), wraplength=360, justify="center").pack(pady=40)

    def confirm_action():
        success, message = update_test_drive_status(test_drive_id, new_status)
        if success:
            confirm_popup.destroy()
            show_custom_message("Success", f"Test drive {action_type}ed successfully!")
            open_manage_test_drives(root, main_frame)
        else:
            confirm_popup.destroy()
            show_custom_message("Error", f"Failed to {action_type} test drive: {message}", type="error")

    ctk.CTkButton(confirm_popup, text="Yes", width=100, command=confirm_action).place(x=80, y=130)
    ctk.CTkButton(confirm_popup, text="No", width=100, fg_color="#A9A9A9", command=confirm_popup.destroy).place(x=220, y=130)



def open_comment_popup(root, reason_text):
    # Create Popup Window
    popup_width = 450
    popup_height = 300

    # Center over main_frame
    parent_x = main_frame.winfo_rootx()
    parent_y = main_frame.winfo_rooty()
    parent_width = main_frame.winfo_width()
    parent_height = main_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    popup = ctk.CTkToplevel()
    popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    popup.title("Cancellation Reason")
    popup.resizable(False, False)
    popup.grab_set()

    # Label
    ctk.CTkLabel(popup, text="Cancellation Reason:", font=("Lato", 16)).place(x=40, y=30)

    # Read-only Textbox
    reason_textbox = ctk.CTkTextbox(popup, width=370, height=120, font=("Lato", 13))
    reason_textbox.place(x=40, y=70)
    reason_textbox.insert("1.0", reason_text)
    reason_textbox.configure(state="disabled")  # Make it read-only

    # OK Button
    ctk.CTkButton(popup, text="OK", width=150, height=35, command=popup.destroy).place(x=150, y=220)









