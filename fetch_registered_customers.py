import customtkinter as ctk
import tkinter as tk
from utils import load_background, load_iconctk
from database_utils import get_customers

def open_fetch_customers_popup(root, callback_on_select):
    popup = ctk.CTkToplevel(root)
    popup.geometry("720x550")
    popup.title("Select Registered Customer")
    popup.configure(fg_color="white")
    popup.attributes("-topmost", True)
    popup.lift()

    x = root.winfo_rootx() + 150
    y = root.winfo_rooty() + 100
    popup.geometry(f"+{x}+{y}")

    search_var = tk.StringVar()
    search_debounce_timer = [None]  # Using list so it’s mutable inside nested functions

    def on_search_change(*args):
        if search_debounce_timer[0] is not None:
            root.after_cancel(search_debounce_timer[0])

        def delayed_reload():
            reload_cards()

        search_debounce_timer[0] = root.after(400, delayed_reload)

    search_var.trace_add("write", on_search_change)


    def reload_cards():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        customers = get_customers(search_var.get(), "Active")

        if not customers:
            ctk.CTkLabel(scrollable_frame, text="😢 No customers found.", font=("Lato", 15, "bold")).pack(pady=40)
            return

        for customer in customers:
            full_name = f"{customer['first_name']} {customer['last_name']}".title()
            card = ctk.CTkFrame(scrollable_frame, width=620, height=90, fg_color="#f4f4f4", corner_radius=10, border_color="#808080", 
                                border_width=1)
            card.pack(padx=8, pady=5)

            ctk.CTkLabel(card, text=full_name, font=("Lato", 16, "bold")).place(x=20, y=10)
            ctk.CTkLabel(card, text=f"📧 {customer['email']}", font=("Lato", 14)).place(x=20, y=35)
            ctk.CTkLabel(card, text=f"📞 {customer['phone']}", font=("Lato", 14)).place(x=20, y=60)
            ctk.CTkLabel(card, text=f"🆔 ID: {customer['user_id']}", font=("Lato", 13)).place(x=400, y=10)

            def select_this(cust=customer):
                callback_on_select(cust)
                popup.destroy()

            ctk.CTkButton(card, text="Select", width=80, fg_color="#a855f7", text_color="black", border_color="#808080", border_width=1,
                          hover_color="#8b3cd3", command=select_this).place(x=500, y=50)
            

    # Search Frame
    search_frame = ctk.CTkFrame(popup, width=655, height=40, fg_color="#bababa",
                                corner_radius=10, border_color="#808080", border_width=1)
    search_frame.place(x=25, y=15)

    search_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/search_icon.png", (25, 25)), text="")
    search_icon_label.place(x=110, y=7)
    # Search Entry
    search_box = ctk.CTkEntry(search_frame, width=350, textvariable=search_var, placeholder_text="Search customers...", corner_radius=15)
    search_box.place(x=140, y=7)
    ctk.CTkButton(search_frame, text="Go", width=60, fg_color="#30b8a9", text_color="black", command=reload_cards).place(x=500, y=7)

    # Scrollable card area
    scroll_container = ctk.CTkFrame(popup, width=660, height=450, fg_color="white")
    scroll_container.place(x=25, y=60)

    scrollable_frame = ctk.CTkScrollableFrame(scroll_container, width=635, height=400, fg_color="white", corner_radius=10, border_color="#808080",
                                              border_width=5)
    scrollable_frame.pack()
    scrollable_frame._scrollbar.grid_configure(padx=(0, 10))

    reload_cards()
