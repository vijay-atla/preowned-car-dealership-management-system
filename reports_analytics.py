from session import current_user
from utils import load_iconctk, show_custom_message
import customtkinter as ctk
from database_utils import (fetch_sales_kpis, get_sales_trend_data, fetch_sales_reports, fetch_operations_kpis, get_test_drive_trend_data, 
                            get_inquiry_status_breakdown, fetch_inventory_kpis, get_brand_distribution, fetch_available_car_records, 
                            fetch_sold_car_records, get_fuel_type_distribution, get_sales_by_payment_method)
from tkcalendar import DateEntry
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import timedelta, datetime
from matplotlib.ticker import MaxNLocator
from datetime import date
import os, csv, pandas as pd, platform, subprocess
from report_exporter import download_report
from download_operations_report import download_operations_report
from download_inventory_report import download_inventory_report


# Track custom range
custom_range = {"start": None, "end": None}


def open_admin_reports(root, parent_frame):
    global selected_range, file_format, report_frame
    report_frame = parent_frame

    # Clear old frame content
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # === Title Section ===
    ctk.CTkLabel( parent_frame, image=load_iconctk("icons/analytics_icon.png", (55, 55)), text=" Reports & Analytics", font=("Lato", 30, "bold"),
        text_color="#008080", compound="left" ).place(x=35, y=40)

    ctk.CTkLabel( parent_frame, text=f"Welcome Admin, {current_user['full_name'].title()}!", font=("Lato", 20) ).place(x=440, y=73)

    # === Full Unified Table Frame ===
    report_frame = ctk.CTkFrame(parent_frame, width=675, height=500, fg_color="#ffffff",
                                corner_radius=10, border_color="#808080", border_width=5)
    report_frame.place(x=35, y=130)

    filter_options = ["Last 1 Day", "Last 7 Days", "Last 30 Days", "Last 6 Months", "Last 1 Year", "All Time", "Custom Range"]
    selected_range = ctk.StringVar(value="Last 30 Days")

    def on_filter_change(choice):
        selected_range.set(choice)
        today = date.today()

        if choice == "Custom Range":
            open_custom_date_popup()
            return

        # Determine start and end dates based on filter
        if choice == "All Time":
            start = date(2000, 1, 1)
            end = today
        else:
            days_map = {
                "Last 1 Day": 1, "Last 7 Days": 7, "Last 30 Days": 30,
                "Last 6 Months": 180, "Last 1 Year": 365
            }
            start = today - timedelta(days=days_map.get(choice, 30))
            end = today

        # Re-render the currently selected tab
        if selected_tab.get() == "Sales":
            update_kpis(start, end)
        elif selected_tab.get() == "Operations":
            update_operations_tab(start, end)
        elif tab == "Inventory":
            update_inventory_tab(start, end)



    # === Filter Dropdown with Border ===
    filter_border = ctk.CTkFrame(report_frame, width=169, height=34, fg_color="white", border_color="#808080", border_width=2, corner_radius=10)
    filter_border.place(x=485, y=19)

    date_filter_dropdown = ctk.CTkOptionMenu( master= filter_border, values=filter_options, variable=selected_range, command=on_filter_change,
        width=160, font=("Lato", 13), fg_color="#eeeeee", button_color="#cccccc", dropdown_font=("Lato", 12), text_color="black", corner_radius=10)
    date_filter_dropdown.place(x=5, y=3)

    # === 🔘 Tabs at the Top ===
    tabs = ["Sales", "Operations", "Inventory"]
    selected_tab = ctk.StringVar(value="Sales")
    tab_buttons = {}

    def switch_tab(tab):
        selected_tab.set(tab)
        today = date.today()

        if selected_range.get() == "Custom Range" and custom_range["start"] and custom_range["end"]:
            start = custom_range["start"]
            end = custom_range["end"]
        elif selected_range.get() == "All Time":
            start = date(2000, 1, 1)
            end = today
        else:
            days_map = {
                "Last 1 Day": 1, "Last 7 Days": 7, "Last 30 Days": 30,
                "Last 6 Months": 180, "Last 1 Year": 365
            }
            start = today - timedelta(days=days_map.get(selected_range.get(), 30))
            end = today
            update_kpis(start, end)

        if tab == "Sales":
            update_kpis(start, end)
   
        elif tab == "Operations":
            update_operations_tab(start, end)
        elif tab == "Inventory":
            update_inventory_tab(start, end)
        else:
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            ctk.CTkLabel(scroll_frame, text="📦 New analytics coming soon...", font=("Lato", 14), text_color="gray").pack(pady=20)

        # 🔁 Update tab button colors
        for t, button in tab_buttons.items():
            button.configure(fg_color="#20b2aa" if t == tab else "#cccccc")

    x_offset = 20
    for tab in tabs:
        btn = ctk.CTkButton( report_frame, text=tab, width=100, height=30, corner_radius=5, font=("Lato", 13, "bold"),
            fg_color="#20b2aa" if tab == selected_tab.get() else "#cccccc", text_color="black", command=lambda t=tab: switch_tab(t))
        btn.place(x=x_offset, y=15)
        tab_buttons[tab] = btn  # 🔁 Save button reference
        x_offset += 115

    # === 🧠 Placeholder for KPI / Chart section ===
    ctk.CTkLabel(report_frame, text="📊 KPI Visuals & Charts go here...",
                 font=("Lato", 16, "italic"), text_color="gray").place(x=230, y=200)

    # === Top Row KPI Tiles ===
    kpi_tile_width = 190
    kpi_tile_height = 80
    kpi_y = 65
    kpi_x_start = 33
    kpi_gap = 20

    scroll_frame = ctk.CTkScrollableFrame(report_frame, width=630, height=350, fg_color="white")
    scroll_frame.place(x=15, y=75)


    def update_kpis(start=None, end=None):
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        # Determine grouping logic
        group_by = "day"
        if selected_range.get() == "Custom Range" and start and end:
            delta = (end - start).days
            if delta <= 45:
                group_by = "day"
            elif delta <= 365:
                group_by = "month"
            else:
                group_by = "year"
        elif selected_range.get() in ["Last 6 Months", "Last 1 Year"]:
            group_by = "month"
        elif selected_range.get() == "All Time":
            group_by = "year"

        kpi_data = fetch_sales_kpis(start_date=start, end_date=end)

        # --- KPI Tiles ---
        kpi_values = [
            ("🚗 Cars Sold", str(kpi_data["cars_sold"])),
            ("💰 Revenue", f"${int(kpi_data['revenue']):,}"),
            ("💲 Average Price", f"${int(kpi_data['avg_price']):,}")
        ]

        kpi_row = ctk.CTkFrame(scroll_frame, fg_color="white")
        kpi_row.pack(pady=10)

        for label, value in kpi_values:
            tile = ctk.CTkFrame(kpi_row, width=190, height=80, fg_color="#f5f5f5",
                                corner_radius=8, border_width=2, border_color="#20b2aa")
            tile.pack(side="left", padx=10)
            tile.kpi_tile = True
            ctk.CTkLabel(tile, text=label, font=("Lato", 14, "bold"), text_color="#333333").place(x=12, y=8)
            ctk.CTkLabel(tile, text=value, font=("Lato", 20, "bold"), text_color="#008080").place(relx=0.5, y=50, anchor="center")

        # --- Chart Section ---
        trend_data = get_sales_trend_data(start, end, group_by=group_by)

        if not trend_data:
            lbl = ctk.CTkLabel(scroll_frame, text="📉 No sales data to show.",
                            font=("Lato", 14), text_color="gray")
            lbl.pack(pady=20)
            lbl.graph_widget = True
            return

        dates = list(trend_data.keys())
        counts = list(trend_data.values())

        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=100)
        ax.plot(dates, counts, marker='o', linestyle='-', color='teal')
        ax.set_title("Sales Trend", fontsize=12)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Number of Sales", fontsize=10)
        ax.grid(True)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=30, ha='right', fontsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=scroll_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(pady=20)
        canvas_widget.graph_widget = True
        canvas.draw()


        # --- New Chart: Sales by Payment Method (Pie Chart) ---
        payment_data = get_sales_by_payment_method(start, end)
        if payment_data:
            fig2, ax2 = plt.subplots(figsize=(5, 3.5), dpi=100)
            ax2.pie(payment_data.values(), labels=payment_data.keys(), autopct='%1.1f%%', startangle=140)
            ax2.set_title("Sales by Payment Method", fontsize=12)
            ax2.axis('equal')  # Ensures it stays a circle

            canvas2 = FigureCanvasTkAgg(fig2, master=scroll_frame)
            canvas_widget2 = canvas2.get_tk_widget()
            canvas_widget2.pack(pady=10)
            canvas_widget2.graph_widget = True
            canvas2.draw()



    # ⬇ Auto-load default Sales tab on open
    today = date.today()
    start = today - timedelta(days=30)
    end = today
    update_kpis(start, end)





    def open_custom_date_popup():
        popup = ctk.CTkToplevel(scroll_frame)
        popup.geometry("380x200")
        popup.title("Select Custom Date Range")
        popup.attributes("-topmost", True)

        # 💡 Center it relative to report_frame
        popup.update_idletasks()
        x = scroll_frame.winfo_rootx() + scroll_frame.winfo_width() // 2 - 190
        y = scroll_frame.winfo_rooty() + scroll_frame.winfo_height() // 2 - 100
        popup.geometry(f"+{x}+{y}")

        today = date.today()

        ctk.CTkLabel(popup, text="Start Date", font=("Lato", 14)).place(x=40, y=30)
        start_cal = DateEntry(popup, width=16, background='darkblue', foreground='white', borderwidth=2, maxdate=today)
        start_cal.set_date(today - timedelta(days=30))
        start_cal.place(x=150, y=45)

        ctk.CTkLabel(popup, text="End Date", font=("Lato", 14)).place(x=40, y=80)
        end_cal = DateEntry(popup, width=16, background='darkblue', foreground='white', borderwidth=2, maxdate=today)
        end_cal.set_date(today)
        end_cal.place(x=150, y=105)

        def apply_custom_filter():
            start = start_cal.get_date()
            end = end_cal.get_date()
            custom_range["start"] = start
            custom_range["end"] = end

            popup.destroy()
            update_kpis(start=start, end=end)

        ctk.CTkButton(popup, text="Apply", command=apply_custom_filter, width=100).place(x=140, y=140)


    file_format = ctk.StringVar(value="PDF")
    file_options = ["CSV", "Excel", "PDF"]

    ctk.CTkLabel(report_frame, text="Export Format:", font=("Lato", 13)).place(x=25, y=450)

    format_dropdown = ctk.CTkOptionMenu( report_frame, values=file_options, variable=file_format, width=100, font=("Lato", 13), fg_color="#eeeeee",
        button_color="#cccccc", dropdown_font=("Lato", 12), text_color="black" )
    format_dropdown.place(x=135, y=450)



    def handle_download():
        # Determine start and end based on current selection
        if selected_range.get() == "Custom Range" and custom_range["start"] and custom_range["end"]:
            start_date = custom_range["start"]
            end_date = custom_range["end"]
        elif selected_range.get() == "All Time":
            start_date = date(2000, 1, 1)
            end_date = date.today()
        else:
            days_map = {
                "Last 1 Day": 1, "Last 7 Days": 7, "Last 30 Days": 30,
                "Last 6 Months": 180, "Last 1 Year": 365
            }
            today = date.today()
            start_date = today - timedelta(days=days_map.get(selected_range.get(), 30))
            end_date = today

        # Call the universal download function
        if selected_tab.get() == "Sales":
            download_report(start_date, end_date, selected_range.get(), file_format.get())
        elif selected_tab.get() == "Operations":
            download_operations_report(start_date, end_date, selected_range.get(), file_format.get())
        elif selected_tab.get() == "Inventory":
            download_inventory_report(start_date, end_date, selected_range.get(), file_format.get())


        show_custom_message("Download Complete", f"{file_format.get()} report has been saved and opened from Downloads.")




    ctk.CTkButton( report_frame, text="⬇ Download Report", width=150, height=30, font=("Lato", 12), fg_color="#008080", text_color="white",
    command=lambda: handle_download()).place(x=480, y=450)



    def update_operations_tab(start_date, end_date):
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        # === Grouping Logic ===
        delta = (end_date - start_date).days
        if delta <= 45:
            group_by = "day"
        elif delta <= 365:
            group_by = "month"
        else:
            group_by = "year"

        # === KPIs ===
        kpis = fetch_operations_kpis(start_date, end_date)
        td_total = kpis["test_drives_total"]
        td_completed = kpis["test_drives_completed"]
        iq_total = kpis["inquiries_total"]
        iq_responded = kpis["inquiries_responded"]

        td_rate = f"{(td_completed / td_total * 100):.1f}%" if td_total else "0%"
        iq_rate = f"{(iq_responded / iq_total * 100):.1f}%" if iq_total else "0%"

        values = [
            ("🚘 Total Test Drives", td_total),
            ("✅ Completed Test Drives", td_completed),
            ("📈 Completion Rate", td_rate),
            ("📬 Inquiries Received", iq_total),
            ("💬 Inquiries Responded", iq_responded),
            ("🔁 Response Rate", iq_rate)
        ]

        # === KPI Tiles in 2 rows using .pack() ===
        for row in range(2):
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="white")
            row_frame.pack(pady=(10 if row == 0 else 0))
            for col in range(3):
                idx = row * 3 + col
                if idx < len(values):
                    label, value = values[idx]
                    tile = ctk.CTkFrame(row_frame, width=190, height=80,
                                        fg_color="#f5f5f5", corner_radius=8,
                                        border_width=2, border_color="#20b2aa")
                    tile.pack(side="left", padx=10)
                    tile.kpi_tile = True
                    ctk.CTkLabel(tile, text=label, font=("Lato", 13, "bold"), text_color="#333333").place(x=12, y=8)
                    ctk.CTkLabel(tile, text=str(value), font=("Lato", 20, "bold"), text_color="#008080").place(relx=0.5, y=50, anchor="center")

        # === Line Chart: Test Drive Trend ===
        trend = get_test_drive_trend_data(start_date, end_date, group_by)
        if trend:
            fig1, ax1 = plt.subplots(figsize=(5.8, 3), dpi=100)
            ax1.plot(list(trend.keys()), list(trend.values()), marker='o', linestyle='-', color='teal')
            ax1.set_title("Test Drive Booking Trend", fontsize=12)
            ax1.set_xlabel("Date", fontsize=10)
            ax1.set_ylabel("Bookings", fontsize=10)
            ax1.grid(True)
            ax1.set_xticks(range(len(trend)))
            ax1.set_xticklabels(trend.keys(), rotation=30, ha='right', fontsize=8)
            ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax1.set_ylim(bottom=0)
            plt.tight_layout()

            chart1 = FigureCanvasTkAgg(fig1, master=scroll_frame)
            widget1 = chart1.get_tk_widget()
            widget1.pack(pady=20)
            widget1.graph_widget = True
            chart1.draw()

        # === Bar Chart: Inquiry Status Breakdown ===
        status_data = get_inquiry_status_breakdown(start_date, end_date)
        if status_data:
            fig2, ax2 = plt.subplots(figsize=(5.8, 3), dpi=100)
            ax2.bar(list(status_data.keys()), list(status_data.values()), color="orange")
            ax2.set_title("Inquiry Status Breakdown", fontsize=12)
            ax2.set_xlabel("Status", fontsize=10)
            ax2.set_ylabel("Count", fontsize=10)
            ax2.grid(True, axis='y')
            ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax2.set_ylim(bottom=0)  # ✅ Optional but good for visual balance
            plt.tight_layout()

            chart2 = FigureCanvasTkAgg(fig2, master=scroll_frame)
            widget2 = chart2.get_tk_widget()
            widget2.pack(pady=10)
            widget2.graph_widget = True
            chart2.draw()



    def update_inventory_tab(start_date, end_date):
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        # === Grouping Logic ===
        delta = (end_date - start_date).days
        group_by = "day" if delta <= 45 else "month" if delta <= 365 else "year"

        # === KPIs ===
        kpis = fetch_inventory_kpis(start_date, end_date)
        values = [
            ("🚗 Total In Stock", kpis["total_in_stock"]),
            ("🆕 New Arrivals", kpis["new_arrivals"]),
            ("📦 Sold This Period", kpis["sold_this_period"]),
            ("📅 Older Stock (>60d)", kpis["older_stock"]),
            ("📊 Avg. Days in Stock", kpis["avg_days_in_stock"])
        ]

        for row in range(2):
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="white")
            row_frame.pack(pady=(10 if row == 0 else 0))
            for col in range(3):
                idx = row * 3 + col
                if idx < len(values):
                    label, value = values[idx]
                    tile = ctk.CTkFrame(row_frame, width=190, height=80,
                                        fg_color="#f5f5f5", corner_radius=8,
                                        border_width=2, border_color="#20b2aa")
                    tile.pack(side="left", padx=10)
                    tile.kpi_tile = True
                    ctk.CTkLabel(tile, text=label, font=("Lato", 13, "bold"), text_color="#333333").place(x=12, y=8)
                    ctk.CTkLabel(tile, text=str(value), font=("Lato", 20, "bold"), text_color="#008080").place(relx=0.5, y=50, anchor="center")

        # === Chart: Brand Distribution ===
        brand_data = get_brand_distribution()
        if brand_data:
            fig, ax = plt.subplots(figsize=(5.8, 3), dpi=100)
            ax.bar(brand_data.keys(), brand_data.values(), color='steelblue')
            ax.set_title("Car Stock by Brand", fontsize=12)
            ax.set_xlabel("Brand", fontsize=10)
            ax.set_ylabel("Stock", fontsize=10)
            ax.grid(True, axis='y')
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xticks(rotation=30, ha='right', fontsize=9)
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=scroll_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(pady=20)
            canvas_widget.graph_widget = True
            canvas.draw()


        # === Chart: Fuel Type Distribution ===
        fuel_data = get_fuel_type_distribution()
        if fuel_data:
            fig2, ax2 = plt.subplots(figsize=(5.8, 3), dpi=100)
            ax2.bar(fuel_data.keys(), fuel_data.values(), color='seagreen')
            ax2.set_title("Stock by Fuel Type", fontsize=12)
            ax2.set_xlabel("Fuel Type", fontsize=10)
            ax2.set_ylabel("Count", fontsize=10)
            ax2.grid(True, axis='y')
            ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xticks(rotation=30, ha='right', fontsize=9)
            plt.tight_layout()

            canvas2 = FigureCanvasTkAgg(fig2, master=scroll_frame)
            canvas2_widget = canvas2.get_tk_widget()
            canvas2_widget.pack(pady=10)
            canvas2_widget.graph_widget = True
            canvas2.draw()
