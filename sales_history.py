import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message, show_gif_loader, hide_loader
from session import current_user  # To get user role and name
from database_utils import get_distinct_payment_methods, get_distinct_sale_years, fetch_sales_records
from datetime import datetime, timedelta
from generate_invoice_pdf import generate_invoice_pdf
import os, subprocess

def open_sales_history(root, parent_frame):
    # 1. Clear Parent Frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Background Illustration
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.2)
    ctk.CTkLabel(parent_frame, image=illustration_image, text="").place(x=0, y=65)

    # 3. Title: Sales History
    ctk.CTkLabel(
        parent_frame, image=load_iconctk("icons/sale_history_icon.png", (60, 60)), text="  Sales History", font=("Lato", 30, "bold"),
        text_color="#008080", fg_color="#ffffff", compound="left" ).place(x=16, y=45)

    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)

    # 5. Table Headers
    headers = ["Sale Date", "Car Details", "Customer", "VIN Number", "Price", "Payment", "Invoice No", ""]
    header_widths = [65, 120, 85, 130, 50, 75, 120, 40]
    text_padding = 10


    # === Fetch Sales Data from DB ===
    all_sales = fetch_sales_records()

    today = datetime.now().strftime("%m/%d/%Y")
    recent_sales = [sale for sale in all_sales if sale["formatted_sale_date"] == today]

    # Create "Recent Sales" Section
    create_sales_section(parent_frame, "Recent Sales", headers, header_widths, text_padding, y_start=115, sales_data=recent_sales)

    # Create "All Sales" Section (with Search)
    controls, all_sales_scroll = create_sales_section(parent_frame, "All Sales", headers, header_widths, text_padding, y_start=300, include_search=True, sales_data=all_sales)

    # Save for Search function
    global all_sales_controls, all_sales_scroll_frame
    all_sales_controls = controls
    all_sales_scroll_frame = all_sales_scroll

# 6. Function to create each table section
def create_sales_section(parent_frame, title, headers, header_widths, text_padding, y_start, include_search=False, sales_data=[]):
    ctk.CTkLabel(parent_frame, text=title, font=("Lato", 16)).place(x=18, y=y_start)

    col_widths  = [65, 120, 85, 130, 50, 75, 120, 40]

    frame_height = 280 if include_search else 150
    scroll_height = 187 if include_search else 93
    frame = ctk.CTkFrame(parent_frame, width=717, height=frame_height, fg_color="white",
                            border_color="#808080", border_width=5, corner_radius=10)
    frame.place(x=16, y=y_start + 30)

    y_offset = 10
    controls = {}

    if include_search:
        controls = create_sales_search_row(frame)
        y_offset = 45

    # Header Row
    header_frame = ctk.CTkFrame(frame, fg_color="#BABABA", height=30, width=695, corner_radius=0)
    header_frame.place(x=10, y=y_offset)

    for i, title in enumerate(headers):
        ctk.CTkLabel(header_frame, text=title, font=("Lato", 12, "bold"), anchor="w",
                        width=header_widths[i]).place(x=sum(header_widths[:i]) + text_padding, y=1)

    # Scrollable Table Content
    scroll = ctk.CTkScrollableFrame(frame, width=680, height=scroll_height, fg_color="white", scrollbar_button_color="#D9D9D9")
    scroll._scrollbar.configure(height=scroll_height)
    scroll.place(x=5, y=y_offset + 25)

    if sales_data:
        for sale in sales_data:
            row_data = [
                sale["formatted_sale_date"],
                sale["car_details"],
                sale["customer_name"].title(),
                sale["vin_number"],
                sale["formatted_price"],
                sale["payment_method"],
                sale["invoice_number"]
            ]
            create_sales_row(scroll, row_data, col_widths, text_padding)
    else:
        ctk.CTkLabel(scroll, text=f"No records found.",
                     font=("Lato", 14, "bold"), text_color="#888888").pack(pady=20)

    if include_search:
        # Return search controls and scroll separately
        return controls, scroll
    


def create_sales_row(scroll, sale_data, col_widths, text_padding):
    row = ctk.CTkFrame(scroll, fg_color="#F3F3F3", height=30, width=680, corner_radius=0)
    row.pack(pady=3)

    for i, value in enumerate(sale_data):
        # Special handling for Customer Name
        if i == 1:  # Customer column
            if len(value) > 18:
                value = value[:16] + "..."
        if i == 2:  # Customer column
            if len(value) > 13:
                value = value[:11] + "..."
        if i == 6:  # Invoice Number column
            invoice_no = value  # Save this
            value = f"#{value}"  # Add # before invoice number
        ctk.CTkLabel(row, text=value, font=("Lato", 11), anchor="w", width=col_widths[i]).place(x=sum(col_widths[:i]) + text_padding, y=3)

    download_icon = load_iconctk("icons/download_invoide_icon.png", (20, 20))
    icon_lbl = ctk.CTkLabel(row, image=download_icon, text="", cursor="hand2")
    icon_lbl.image = download_icon
    icon_lbl.place(x=655, y=5)

    if invoice_no:
        icon_lbl.bind("<Button-1>", lambda e: download_invoice(invoice_no.strip("#")))


def create_sales_search_row(frame):
    search_frame = ctk.CTkFrame(frame, fg_color="#d9d9d9", height=30, width=695, corner_radius=5)
    search_frame.place(x=10, y=10)

    # ====== Fetch Dynamic Values ======
    payment_methods = get_distinct_payment_methods() or []
    sale_years = get_distinct_sale_years() or []

    # Only values, no "Payment:" inside options
    payment_filter_options = ["All"] + payment_methods
    year_filter_options = ["All"] + sale_years

    # ====== Payment Filter ======
    funnel_icon = load_iconctk("icons/filter_icon.png", (20, 20))
    ctk.CTkLabel(search_frame, image=funnel_icon, text=" Payment:", compound="left", font=("Lato", 12)).place(x=10, y=1)

    payment_dropdown = ctk.CTkOptionMenu(
        search_frame,
        values=payment_filter_options,
        width=110, height=20,
        fg_color="white", text_color="#008080", font=("Lato", 12)
    )
    payment_dropdown.place(x=90, y=4)
    payment_dropdown.set("All")

    # ====== Year Filter ======
    calendar_icon = load_iconctk("icons/calendar_icon.png", (20, 20))
    ctk.CTkLabel(search_frame, image=calendar_icon, text=" Year:", compound="left", font=("Lato", 12)).place(x=210, y=1)

    year_dropdown = ctk.CTkOptionMenu(
        search_frame,
        values=year_filter_options,
        width=100, height=20,
        fg_color="white", text_color="#008080", font=("Lato", 12)
    )
    year_dropdown.place(x=280, y=4)
    year_dropdown.set("All")

    # ====== Search Box ======
    search_icon = load_iconctk("icons/search_icon.png", (20, 20))
    ctk.CTkLabel(search_frame, text="", image=search_icon, fg_color="#d9d9d9").place(x=400, y=1)

    search_entry = ctk.CTkEntry(
        search_frame, width=160, height=20, corner_radius=15,
        fg_color="white", text_color="#008080", font=("Lato", 12)
    )
    search_entry.place(x=425, y=4)

    # ====== Search Button ======
    ctk.CTkButton(
        search_frame, text="Search", font=("Lato", 12,"bold"), text_color="white",
        width=50, height=20, fg_color="#008080", command= perform_sales_search
    ).place(x=600, y=3)

    # ===== Debounce Logic =====
    search_timer_id = [None]  # List so we can modify inside nested function

    def on_search_typing(event):
        if search_timer_id[0] is not None:
            frame.after_cancel(search_timer_id[0])  # cancel previous timer

        search_timer_id[0] = frame.after(600, perform_sales_search)  # 600ms delay

    search_entry.bind("<KeyRelease>", on_search_typing)
    payment_dropdown.configure(command=lambda _: perform_sales_search())
    year_dropdown.configure(command=lambda _: perform_sales_search())



    return {
        "payment_dropdown": payment_dropdown,
        "year_dropdown": year_dropdown,
        "search_entry": search_entry
    }



def perform_sales_search():
    selected_payment = all_sales_controls["payment_dropdown"].get()
    selected_year = all_sales_controls["year_dropdown"].get()
    search_text = all_sales_controls["search_entry"].get()

    # Normalize
    if selected_payment == "All":
        selected_payment = None
    if selected_year == "All":
        selected_year = None
    if not search_text.strip():
        search_text = None

    # Fetch new filtered results
    filtered_sales = fetch_sales_records(
        payment_filter=selected_payment,
        year_filter=selected_year,
        search_value=search_text
    )

    # ==== Clear old scroll content ====
    for widget in all_sales_scroll_frame.winfo_children():
        widget.destroy()

    # ==== Re-populate scroll ====
    if filtered_sales:
        for sale in filtered_sales:
            row_data = [
                sale["formatted_sale_date"],
                sale["car_details"],
                sale["customer_name"].title(),
                sale["vin_number"],
                sale["formatted_price"],
                sale["payment_method"],
                sale["invoice_number"]
            ]
            create_sales_row(all_sales_scroll_frame, row_data, [65, 120, 85, 130, 50, 75, 120, 40], 10)
    else:
        ctk.CTkLabel(all_sales_scroll_frame, text=f"No records found.", font=("Lato", 14, "bold"), text_color="#888888").pack(pady=20)



def download_invoice(invoice_no):
    try:
        from generate_invoice import generate_invoice
        pdf_path = generate_invoice(invoice_no)
        if pdf_path:
            show_custom_message("Invoice Downloaded", f"Invoice #{invoice_no} saved to your Downloads folder!")
            
            # Auto-open the downloaded PDF
            if os.name == 'nt':  # For Windows
                os.startfile(pdf_path)
            elif os.name == 'posix':  # For Mac/Linux
                subprocess.Popen(['open', pdf_path])
            else:
                subprocess.Popen(['xdg-open', pdf_path])

        else:
            show_custom_message("Download Failed", "Invoice not found!")
    except Exception as e:
        show_custom_message("Error", f"Failed to download invoice:\n{str(e)}")
