import os
import csv
import pandas as pd
import platform
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
from matplotlib.ticker import MaxNLocator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from database_utils import fetch_operations_kpis, get_test_drive_trend_data, get_inquiry_status_breakdown
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from report_exporter import get_download_path, open_file
from database_utils import (
    fetch_operations_kpis, get_test_drive_trend_data, get_inquiry_status_breakdown,
    fetch_testdrive_records, fetch_inquiry_records  # ✅ Add these
)

def download_operations_report(start_date, end_date, selected_range_label, format_selected):
    downloads_folder = get_download_path()
    os.makedirs(downloads_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"Operations_Report_{selected_range_label.replace(' ', '_')}_{timestamp}"
    ext_map = {"CSV": ".csv", "Excel": ".xlsx", "PDF": ".pdf"}
    full_path = os.path.join(downloads_folder, base_filename + ext_map[format_selected])

    # === Fetch Data ===
    kpis = fetch_operations_kpis(start_date, end_date)

    delta = (end_date - start_date).days
    group_by = "day" if delta <= 45 else "month" if delta <= 365 else "year"

    td_trend = get_test_drive_trend_data(start_date, end_date, group_by)
    iq_breakdown = get_inquiry_status_breakdown(start_date, end_date)

    # === Format KPI values ===
    td_total = kpis["test_drives_total"]
    td_completed = kpis["test_drives_completed"]
    iq_total = kpis["inquiries_total"]
    iq_responded = kpis["inquiries_responded"]

    td_rate = f"{(td_completed / td_total * 100):.1f}%" if td_total else "0%"
    iq_rate = f"{(iq_responded / iq_total * 100):.1f}%" if iq_total else "0%"

    kpi_rows = [
        ["Metric", "Value"],
        ["Total Test Drives Booked", td_total],
        ["Test Drives Completed", td_completed],
        ["Completion Rate (%)", td_rate],
        ["Customer Inquiries Received", iq_total],
        ["Inquiries Responded", iq_responded],
        ["Inquiry Response Rate (%)", iq_rate]
    ]

    # === Export ===
    if format_selected == "CSV":
        # Prepare dataframes
        df_kpi = pd.DataFrame([
            ["Metric", "Value"],
            ["Total Test Drives Booked", td_total],
            ["Test Drives Completed", td_completed],
            ["Completion Rate (%)", td_rate],
            ["Customer Inquiries Received", iq_total],
            ["Inquiries Responded", iq_responded],
            ["Inquiry Response Rate (%)", iq_rate]
        ])

        df_td_trend = pd.DataFrame(td_trend.items(), columns=["Period", "Test Drive Bookings"])
        df_iq_breakdown = pd.DataFrame(iq_breakdown.items(), columns=["Status", "Count"])

        # Create temp folder for CSV files
        temp_dir = os.path.join(downloads_folder, f"ops_csv_temp_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)

        df_kpi.to_csv(os.path.join(temp_dir, "operations_kpis.csv"), index=False, header=False)
        df_td_trend.to_csv(os.path.join(temp_dir, "test_drive_trend.csv"), index=False)
        df_iq_breakdown.to_csv(os.path.join(temp_dir, "inquiry_breakdown.csv"), index=False)

        # Create ZIP
        full_path = os.path.join(downloads_folder, f"{base_filename}.zip")
        import zipfile
        with zipfile.ZipFile(full_path, "w") as zipf:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                zipf.write(file_path, arcname=filename)

        # Clean up temp CSV folder
        import shutil
        shutil.rmtree(temp_dir)

    elif format_selected == "Excel":
        # KPIs
        df_kpi = pd.DataFrame([
            {"Metric": "Total Test Drives Booked", "Value": td_total},
            {"Metric": "Test Drives Completed", "Value": td_completed},
            {"Metric": "Completion Rate (%)", "Value": td_rate},
            {"Metric": "Customer Inquiries Received", "Value": iq_total},
            {"Metric": "Inquiries Responded", "Value": iq_responded},
            {"Metric": "Inquiry Response Rate (%)", "Value": iq_rate}
        ])

        df_td_trend = pd.DataFrame(td_trend.items(), columns=["Period", "Test Drive Bookings"])
        df_iq_breakdown = pd.DataFrame(iq_breakdown.items(), columns=["Status", "Count"])

        # Load full test drive and inquiry records
        td_records = fetch_testdrive_records(start_date, end_date)
        iq_records = fetch_inquiry_records(start_date, end_date)

        df_td_full = pd.DataFrame(td_records)
        df_iq_full = pd.DataFrame(iq_records)

        with pd.ExcelWriter(full_path) as writer:
            df_kpi.to_excel(writer, sheet_name="KPIs", index=False)
            df_td_trend.to_excel(writer, sheet_name="Test_Drive_Trend", index=False)
            df_iq_breakdown.to_excel(writer, sheet_name="Inquiry_Breakdown", index=False)

            # ✅ All raw data
            if not df_td_full.empty:
                df_td_full.to_excel(writer, sheet_name="Test_Drive_Records", index=False)
            if not df_iq_full.empty:
                df_iq_full.to_excel(writer, sheet_name="Inquiry_Records", index=False)

    elif format_selected == "PDF":
        # Prepare chart images
        graph_path_1 = os.path.join(downloads_folder, "temp_ops_trend.png")
        graph_path_2 = os.path.join(downloads_folder, "temp_ops_status.png")

        # --- Chart 1: Test Drive Trend
        fig1, ax1 = plt.subplots(figsize=(6, 2.8), dpi=100)
        ax1.plot(list(td_trend.keys()), list(td_trend.values()), marker='o', linestyle='-', color='teal')
        ax1.set_title("Test Drive Booking Trend", fontsize=10)
        ax1.set_xlabel("Date", fontsize=8)
        ax1.set_ylabel("Count", fontsize=8)
        ax1.grid(True)
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.set_ylim(bottom=0)
        ax1.set_xticks(range(len(td_trend)))
        ax1.set_xticklabels(td_trend.keys(), rotation=30, ha='right', fontsize=6)
        plt.tight_layout()
        fig1.savefig(graph_path_1)
        plt.close(fig1)

        # --- Chart 2: Inquiry Status Breakdown
        fig2, ax2 = plt.subplots(figsize=(6, 2.8), dpi=100)
        ax2.bar(list(iq_breakdown.keys()), list(iq_breakdown.values()), color='orange')
        ax2.set_title("Inquiry Status Breakdown", fontsize=10)
        ax2.set_xlabel("Status", fontsize=8)
        ax2.set_ylabel("Count", fontsize=8)
        ax2.grid(True, axis='y')
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.tight_layout()
        fig2.savefig(graph_path_2)
        plt.close(fig2)

        # === Generate PDF ===
        c = canvas.Canvas(full_path, pagesize=letter)
        width, height = letter
        y = height - 50

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Operations Report")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Date Range: {start_date} to {end_date}")
        y -= 30

        # KPIs Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Key Performance Indicators (KPIs):")
        y -= 18  # Extra space

        c.setFont("Helvetica", 10)
        for label, value in kpi_rows[1:]:
            c.drawString(60, y, f"- {label}: {value}")
            y -= 15

        y -= 20  # Add vertical gap before first chart

        # Insert Test Drive Chart
        if os.path.exists(graph_path_1):
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "📈 Test Drive Booking Trend")
            y -= 5
            c.drawImage(ImageReader(graph_path_1), 50, y - 150, width=500, preserveAspectRatio=True)
            y -= 170

        # Insert Inquiry Chart
        if os.path.exists(graph_path_2):
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "📊 Inquiry Status Breakdown")
            y -= 5
            c.drawImage(ImageReader(graph_path_2), 50, y - 150, width=500, preserveAspectRatio=True)
            y -= 170

        # Data Table: Test Drive Trend
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "📋 Test Drive Trend Data")
        y -= 15
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Period")
        c.drawString(200, y, "Bookings")
        y -= 15
        c.setFont("Helvetica", 9)
        for label, count in td_trend.items():
            c.drawString(60, y, str(label))
            c.drawString(200, y, str(count))
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "📋 Inquiry Status Breakdown Data")
        y -= 15
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "Status")
        c.drawString(200, y, "Count")
        y -= 15
        c.setFont("Helvetica", 9)
        for status, count in iq_breakdown.items():
            c.drawString(60, y, str(status))
            c.drawString(200, y, str(count))
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

        c.save()

        # Cleanup images
        for img in [graph_path_1, graph_path_2]:
            if os.path.exists(img):
                os.remove(img)

    open_file(full_path)
