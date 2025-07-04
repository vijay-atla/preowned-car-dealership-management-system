# customer_my_test_drives.py (Refactored)

import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message
from session import current_user
from database_utils import get_customer_test_drives, update_test_drive_schedule, cancel_test_drive
from schedule_popup import open_schedule_popup





def open_customer_my_test_drives(root, parent_frame):
    global nroot
    nroot = root
    # 1. Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Background Illustration
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=illustration_image, text="").place(x=0, y=65)

    # 3. Welcome Title
    ctk.CTkLabel( parent_frame, image=load_iconctk("icons/test_drive_icon.png", (50, 50)), text="  My Test Drives", font=("Lato", 30, "bold"),
        text_color="#008080", fg_color="#ffffff", compound="left" ).place(x=61, y=50)

    ctk.CTkLabel( parent_frame, text=f"Welcome, {current_user['full_name'].title()}!", font=("Lato", 20), fg_color="#ffffff"
    ).place(x=425, y=73)

    # 4. Fetch Test Drive Data
    all_test_drives = get_customer_test_drives(current_user['user_id'])

    # Separate into Ongoing and History
    ongoing_data = []
    history_data = []

    for drive in all_test_drives:
        entry = [
            drive["slot_datetime"],
            drive["car_info"],
            drive["status"],
            drive["last_modified"],
            drive["test_drive_id"],
            drive["cancellation_reason"]
        ]

        if drive["status"] in ["Pending", "Confirmed"]:
            ongoing_data.append(entry)
        else:
            history_data.append(entry)

    ongoing_icons = ["icons/reschedule_icon.png", "icons/cancel_icon.png"]
    history_icons = ["icons/comment_icon.png"]

    # 5. Render the sections
    create_table_section(parent_frame, "Ongoing Test Drives", ongoing_data, ongoing_icons, y_start=135)
    create_table_section(parent_frame, "Test Drive History", history_data, history_icons, y_start=355)

# ----------------------------------------------------------------------
# Helper Function to Create Each Table Section
def create_table_section(parent, label_text, entries, icon_paths, y_start):
    headers = ["Slot Date & Time", "Car Make & Model", "Status", "Last Modified on", ""]
    col_widths = [130, 150, 80, 130, 80]
    text_padding = 10

    # Section Label
    ctk.CTkLabel(parent, text=label_text, font=("Lato", 16)).place(x=65, y=y_start)

    # Frame for Table
    frame = ctk.CTkFrame(parent, width=619, height=150, fg_color="#ffffff", corner_radius=10, border_color="#808080", border_width=5)
    frame.place(x=65, y=y_start + 30)

    # Header
    header = ctk.CTkFrame(frame, fg_color="#BABABA", height=30, width=580, corner_radius=0)
    header.place(x=12, y=10)

    for i, text in enumerate(headers):
        lbl = ctk.CTkLabel(header, text=text, anchor="w", justify="left",
                           font=("Lato", 12, "bold"), width=col_widths[i])
        lbl.place(x=sum(col_widths[:i]) + text_padding, y=0)

    # Scrollable Table
    scrollable = ctk.CTkScrollableFrame(frame, width=580, height=90, fg_color="white", scrollbar_button_color="#D9D9D9")
    scrollable._scrollbar.configure(height=80)
    scrollable.place(x=5, y=40)

    if not entries:
        ctk.CTkLabel(scrollable, text=f"No {label_text.lower()} found.",
                 font=("Lato", 14), text_color="#888888").pack(pady=30)
        return

    # Populate Rows
    for idx, entry in enumerate(entries):
        row = ctk.CTkFrame(scrollable, fg_color="#F3F3F3", height=25, width=580, corner_radius=0)
        row.pack(pady=3)

        for i, val in enumerate(entry[:4]):
            lbl = ctk.CTkLabel(row, text=val, font=("Lato", 11), anchor="w", justify="left", width=col_widths[i])
            lbl.place(x=sum(col_widths[:i]) + text_padding, y=0)

        # Action icons
        for icon_idx, icon_path in enumerate(icon_paths):
            icon = load_iconctk(icon_path, (20, 20))
            icon_lbl = ctk.CTkLabel(row, image=icon, text="", cursor="hand2")
            icon_lbl.image = icon
            icon_lbl.place(x=510 + (icon_idx * 35), y=0)
            if "reschedule" in icon_path.lower():
                icon_lbl.bind("<Button-1>", lambda e, drive_id=entry[4]: reschedule_test_drive(drive_id, root=nroot, parent_frame=parent))
            if "cancel" in icon_path.lower():
                icon_lbl.bind("<Button-1>", lambda e, drive_id=entry[4]: cancel_test_drive_booking(drive_id, parent))
            if "comment" in icon_path.lower():
                icon_lbl.bind("<Button-1>", lambda e, drive=entry: show_cancellation_reason_popup(drive, parent))

# New function to handle rescheduling
def reschedule_test_drive(test_drive_id, root, parent_frame):
    open_schedule_popup(
        root,
        title="Reschedule Test Drive",
        on_confirm=lambda date, time: save_reschedule(test_drive_id, date, time, parent_frame)
    )

def save_reschedule(test_drive_id, new_date, new_time, parent_frame):
    success, message = update_test_drive_schedule(test_drive_id, new_date, new_time)
    if success:
        from utils import show_custom_message
        show_custom_message("Success", "Test Drive rescheduled successfully!", type="success")
        open_customer_my_test_drives(nroot, parent_frame)  # Reload page
    else:
        from utils import show_custom_message
        show_custom_message("Error", message, type="error")


def cancel_test_drive_booking(test_drive_id, parent_frame):
    popup_width = 450
    popup_height = 300

    # Center over parent_frame
    parent_x = parent_frame.winfo_rootx()
    parent_y = parent_frame.winfo_rooty()
    parent_width = parent_frame.winfo_width()
    parent_height = parent_frame.winfo_height()

    popup_x = parent_x + (parent_width - popup_width) // 2
    popup_y = parent_y + (parent_height - popup_height) // 2

    reason_popup = ctk.CTkToplevel()
    reason_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    reason_popup.title("Cancel Test Drive")
    reason_popup.resizable(False, False)
    reason_popup.grab_set()

    ctk.CTkLabel(reason_popup, text="Please provide a reason for cancelling:", font=("Lato", 16)).place(x=40, y=30)

    # ✅ Use Textbox instead of Entry
    reason_textbox = ctk.CTkTextbox(reason_popup, width=370, height=120, font=("Lato", 13))
    reason_textbox.place(x=40, y=70)

    def submit_cancellation():
        reason = reason_textbox.get("1.0", "end").strip()

        if not reason:
            from utils import show_custom_message
            show_custom_message("Warning", "Please enter a reason for cancellation.", type="warning")
            return

        result, message = cancel_test_drive(test_drive_id, reason)

        if result:
            from utils import show_custom_message
            reason_popup.destroy()
            show_custom_message("Success", "Test Drive cancelled successfully!", type="success")
            open_customer_my_test_drives(nroot, parent_frame)  # ✅ Reload after cancel
        else:
            from utils import show_custom_message
            show_custom_message("Error", message, type="error")

    ctk.CTkButton(reason_popup, text="Submit", width=150, height=35, command=submit_cancellation).place(x=150, y=220)



def show_cancellation_reason_popup(drive_entry, parent_frame):
    reason = drive_entry[5]  # Assuming the cancellation_reason is stored at index 5
    status = drive_entry[2]
    if status == "Cancelled":
        popup_width = 450
        popup_height = 300

        # Center over parent_frame
        parent_x = parent_frame.winfo_rootx()
        parent_y = parent_frame.winfo_rooty()
        parent_width = parent_frame.winfo_width()
        parent_height = parent_frame.winfo_height()

        popup_x = parent_x + (parent_width - popup_width) // 2
        popup_y = parent_y + (parent_height - popup_height) // 2

        reason_popup = ctk.CTkToplevel()
        reason_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
        reason_popup.title("Cancellation Reason")
        reason_popup.resizable(False, False)
        reason_popup.grab_set()

        ctk.CTkLabel(reason_popup, text="Cancellation Reason:", font=("Lato", 16)).place(x=40, y=30)
        # Textbox (readonly)
        reason_textbox = ctk.CTkTextbox(reason_popup, width=370, height=120, font=("Lato", 13))
        reason_textbox.place(x=40, y=70)
        reason_textbox.insert("1.0", reason)
        reason_textbox.configure(state="disabled")  # Read-only
        ctk.CTkButton(reason_popup, text="OK", width=150, height=35, command=reason_popup.destroy).place(x=150, y=220)
    else:
        # Show info message for Completed bookings
        show_custom_message("Info", "No cancellation reason available for Completed bookings.", type="info")