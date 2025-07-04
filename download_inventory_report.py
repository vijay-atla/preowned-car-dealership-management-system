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
from database_utils import (fetch_inventory_kpis, get_brand_distribution, fetch_available_car_records, 
                            fetch_sold_car_records, get_fuel_type_distribution)

def download_inventory_report(start_date, end_date, selected_range_label, format_selected):
    downloads_folder = get_download_path()
    os.makedirs(downloads_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"Inventory_Report_{selected_range_label.replace(' ', '_')}_{timestamp}"
    full_path = os.path.join(downloads_folder, base_filename + {
        "CSV": ".zip", "Excel": ".xlsx", "PDF": ".pdf"
    }[format_selected])

    # Fetch data
    kpis = fetch_inventory_kpis(start_date, end_date)
    brand_data = get_brand_distribution()
    fuel_data = get_fuel_type_distribution()
    available_cars = fetch_available_car_records(start_date, end_date)
    sold_cars = fetch_sold_car_records(start_date, end_date)

    # KPIs
    kpi_rows = [
        ["Metric", "Value"],
        ["Total In Stock", kpis["total_in_stock"]],
        ["New Arrivals", kpis["new_arrivals"]],
        ["Sold This Period", kpis["sold_this_period"]],
        ["Older Stock (>60 days)", kpis["older_stock"]],
        ["Avg. Days in Stock", kpis["avg_days_in_stock"]],
    ]

    # CSV (multi-file ZIP)
    if format_selected == "CSV":
        import zipfile, shutil
        temp_dir = os.path.join(downloads_folder, f"inv_csv_temp_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)

        pd.DataFrame(kpi_rows[1:], columns=kpi_rows[0]).to_csv(os.path.join(temp_dir, "inventory_kpis.csv"), index=False)
        pd.DataFrame(brand_data.items(), columns=["Brand", "Count"]).to_csv(os.path.join(temp_dir, "brand_distribution.csv"), index=False)
        pd.DataFrame(fuel_data.items(), columns=["Fuel Type", "Count"]).to_csv(os.path.join(temp_dir, "fuel_distribution.csv"), index=False)
        pd.DataFrame(available_cars).to_csv(os.path.join(temp_dir, "available_cars.csv"), index=False)
        pd.DataFrame(sold_cars).to_csv(os.path.join(temp_dir, "sold_cars.csv"), index=False)

        with zipfile.ZipFile(full_path, "w") as zipf:
            for filename in os.listdir(temp_dir):
                zipf.write(os.path.join(temp_dir, filename), arcname=filename)

        shutil.rmtree(temp_dir)

    # Excel multi-sheet
    elif format_selected == "Excel":
        with pd.ExcelWriter(full_path) as writer:
            pd.DataFrame(kpi_rows[1:], columns=kpi_rows[0]).to_excel(writer, sheet_name="KPIs", index=False)
            pd.DataFrame(brand_data.items(), columns=["Brand", "Count"]).to_excel(writer, sheet_name="Brand Distribution", index=False)
            pd.DataFrame(fuel_data.items(), columns=["Fuel Type", "Count"]).to_excel(writer, sheet_name="Fuel Distribution", index=False)
            if available_cars:
                pd.DataFrame(available_cars).to_excel(writer, sheet_name="Available Cars", index=False)
            if sold_cars:
                pd.DataFrame(sold_cars).to_excel(writer, sheet_name="Sold Cars", index=False)

    # PDF
    elif format_selected == "PDF":
        c = canvas.Canvas(full_path, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Inventory Report")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Date Range: {start_date} to {end_date}")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Key Performance Indicators (KPIs):")
        y -= 18
        c.setFont("Helvetica", 10)
        for label, value in kpi_rows[1:]:
            c.drawString(60, y, f"- {label}: {value}")
            y -= 15

        def draw_chart(data_dict, title, y_offset):
            fig, ax = plt.subplots(figsize=(6, 2.8), dpi=100)
            ax.bar(data_dict.keys(), data_dict.values(), color='teal')
            ax.set_title(title, fontsize=10)
            ax.grid(True, axis='y')
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xticks(range(len(data_dict)))
            ax.set_xticklabels(data_dict.keys(), rotation=30, ha='right', fontsize=6)
            plt.tight_layout()

            img_path = os.path.join(downloads_folder, f"temp_{title.replace(' ', '_')}.png")
            fig.savefig(img_path)
            plt.close(fig)

            if y_offset < 250:
                c.showPage()
                y_offset = height - 50

            c.drawImage(ImageReader(img_path), 50, y_offset - 150, width=500)
            os.remove(img_path)
            return y_offset - 170

        y = draw_chart(brand_data, "Brand Distribution", y)
        y -= 100  # ⬅️ Add vertical gap before next chart
        y = draw_chart(fuel_data, "Fuel Type Distribution", y)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Sample Available Cars:")
        y -= 15
        c.setFont("Helvetica", 8)
        for row in available_cars[:10]:
            c.drawString(60, y, str(row))
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Sample Sold Cars:")
        y -= 15
        c.setFont("Helvetica", 8)
        for row in sold_cars[:10]:
            c.drawString(60, y, str(row))
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

        c.save()

    open_file(full_path)
