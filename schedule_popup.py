import customtkinter as ctk
import tkinter as tk
from tkcalendar import Calendar
import datetime
from database_utils import get_available_time_slots
from utils import show_custom_message

def open_schedule_popup(root, title="Schedule Test Drive", on_confirm=None, existing_date=None, existing_time=None):
    popup = ctk.CTkToplevel(root)
    popup.geometry("600x420")
    popup.title(title)
    popup.resizable(False, False)
    popup.grab_set()

    selected_date = tk.StringVar()
    selected_time = tk.StringVar()

    # === Split popup into two frames ===
    left_frame = ctk.CTkFrame(popup, width=280, height=320, corner_radius=10)
    left_frame.place(x=10, y=5)

    right_frame = ctk.CTkFrame(popup, width=280, height=320, corner_radius=10)
    right_frame.place(x=300, y=5)

    # === Calendar on Left Side ===
    today = datetime.date.today()
    cal = Calendar( left_frame, selectmode="day", year=today.year, month=today.month, day=today.day, date_pattern='yyyy-mm-dd', mindate=today,
                font=("Lato", 13), headersbackground='gray', background='white', foreground='black'
    )
    cal.place(x=5, y=5)

    selected_date_label = ctk.CTkLabel(popup, text="", font=("Lato", 14, "bold"), text_color="black")
    selected_date_label.place(x=210, y=335)





    # Pre-fill date if editing
    if existing_date:
        try:
            year, month, day = map(int, existing_date.split("-"))
            cal.selection_set(datetime.date(year, month, day))
        except:
            pass

    # === Right Side - Available Slots + Address ===
    slots_frame = ctk.CTkFrame(right_frame, width=265, height=190, fg_color="white", corner_radius=5)
    slots_frame.place(x=5, y=5)

    address_label = ctk.CTkLabel( right_frame, text="📍 PCDS,\n1011 S Main St, \nMt Pleasant, \nMI, USA - 48858", font=("Lato", 13), text_color="black", justify = "left")
    address_label.place(x=30, y=220)

    # === Function to Load Slots when Date Selected ===
    def load_slots_for_selected_date(event=None):
        for widget in slots_frame.winfo_children():
            widget.destroy()

        picked_date = cal.get_date()

        if not picked_date:
            return

        selected_date.set(picked_date)

        # ✅ Update the selected date label dynamically
        selected_date_label.configure(text=f"                 🚗    {picked_date}")

        available_slots = get_available_time_slots(picked_date)

        if not available_slots:
            ctk.CTkLabel(slots_frame, text="No slots available!", font=("Lato", 13), text_color="gray").place(x=30, y=50)
            return

        y_pos = 10
        for slot in available_slots:
            btn = ctk.CTkRadioButton(
                slots_frame, text=slot,
                variable=selected_time, value=slot,
                font=("Lato", 13)
            )
            btn.bind("<ButtonRelease-1>", lambda e : selected_date_label.configure(text=f"🚗 {picked_date} : {selected_time.get()}")  )
            btn.place(x=30, y=y_pos)
            y_pos += 35

        if existing_time and existing_time in available_slots:
            selected_time.set(existing_time)
            

    # Load slots for today's date on opening
    load_slots_for_selected_date()

    # Bind calendar selection
    cal.bind("<<CalendarSelected>>", load_slots_for_selected_date)

    # === Confirm Button at Bottom Center ===
    def confirm_selection():
        if not selected_date.get():
            show_custom_message("Warning", "Please select a date.", type="warning")
            return
        if not selected_time.get():
            show_custom_message("Warning", "Please select a time slot.", type="warning")
            return

        if on_confirm:
            popup.destroy()
            on_confirm(selected_date.get(), selected_time.get())

        popup.destroy()

    ctk.CTkButton( popup, text="Confirm", width=200, command=confirm_selection ).place(x=200, y=380)
