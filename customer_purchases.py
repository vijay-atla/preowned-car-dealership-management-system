# customer_purchases.py (Refactored)

import customtkinter as ctk
from utils import load_background, load_iconctk
from session import current_user
from database_utils import get_customer_purchases  # (You can mock if needed.)
import platform, subprocess, os

def open_customer_purchases(root, parent_frame):
    # Clear the frame first
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Background Illustration
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=illustration_image, text="").place(x=0, y=65)

    # Welcome Title
    ctk.CTkLabel(
        parent_frame, image=load_iconctk("icons/my_purchases_icon.png", (60, 60)), text=" My Purchases", font=("Lato", 30, "bold"),
        text_color="#008080", fg_color="#ffffff", compound="left").place(x=61, y=59)

    ctk.CTkLabel( parent_frame, text=f"Welcome, {current_user['full_name'].title()}!", font=("Lato", 20), fg_color="#ffffff" ).place(x=425, y=73)

    # Purchase History Label
    ctk.CTkLabel( parent_frame, text="Purchase History", font=("Lato", 16), width=138, height=22 ).place(x=60, y=153)

    # Table Frame
    table_frame = ctk.CTkFrame(parent_frame, width=619, height=316, fg_color="#ffffff",
                               corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=65, y=178)

    # Table Header
    headers = ["Car Details", "Date", "Price", "Payment Method", "Invoice Number", ""]
    col_widths = [140, 80, 70, 110, 140, 40]
    text_padding = 10

    header_frame = ctk.CTkFrame(table_frame, fg_color="#BABABA", height=30, width=570, corner_radius=0)
    header_frame.place(x=15, y=15)

    for i, text in enumerate(headers):
        lbl = ctk.CTkLabel(header_frame, text=text, anchor="w", justify="left",
                           font=("Lato", 12, "bold"), width=col_widths[i])
        lbl.place(x=sum(col_widths[:i]) + text_padding, y=0)

    # Scrollable Content
    scrollable_frame = ctk.CTkScrollableFrame(table_frame, width=580, height=250,
                                              fg_color="white", scrollbar_button_color="#D9D9D9")
    scrollable_frame.place(x=5, y=45)

    invoice_icon = load_iconctk("icons/download_invoide_icon.png", (20, 20))

    # --- Fetch Purchases ---
    try:
        purchases = get_customer_purchases(current_user["user_id"])  # 🛑 Replace with DB call
    except:
        purchases = []  # Fallback if error

    # If no purchases, show a nice message
    if not purchases:
        ctk.CTkLabel( scrollable_frame, text="😢 No Purchases Found Yet!", font=("Lato", 18, "bold"), text_color="gray" ).pack(pady=80)
        return

    # Populate Purchases
    for purchase in purchases:
        row = ctk.CTkFrame(scrollable_frame, fg_color="#D9D9D9", height=30, width=570, corner_radius=0)
        row.pack(pady=3)

        for i, val in enumerate(purchase):
            # Add '#' before Invoice Number (which is at index 4)
            if i == 4:
                val = f"#{val}" if not str(val).startswith("#") else val
            lbl = ctk.CTkLabel(row, text=val, font=("Lato", 11), anchor="w", justify="left", width=col_widths[i])
            lbl.place(x=sum(col_widths[:i]) + text_padding, y=0)

        # Invoice Download Button
        icon_lbl = ctk.CTkLabel(row, image=invoice_icon, text="", cursor="hand2")
        icon_lbl.image = invoice_icon
        icon_lbl.place(x=sum(col_widths[:5]), y=0)
        icon_lbl.bind("<Button-1>", lambda e, inv=purchase[4]: download_invoice(inv))

def download_invoice(invoice_number):
    from utils import show_custom_message
    from generate_invoice_pdf import generate_invoice_pdf
    from generate_invoice import generate_invoice

    # # Remove '#' if it's prefixed
    # invoice_number = invoice_number.lstrip("#")

    # Generate the invoice PDF
    filepath = generate_invoice(invoice_number)

    if filepath:
        show_custom_message("Success", f"Invoice downloaded successfully!\nSaved at:\n{filepath}", type="success")

        # === Auto-open the PDF after download! 🚀 ===
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(("open", filepath))
            else:  # Linux
                subprocess.call(("xdg-open", filepath))
        except Exception as e:
            print(f"[Warning] Could not auto-open invoice: {e}")
    else:
        show_custom_message("Error", "Failed to generate invoice.", type="error")

