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
from database_utils import fetch_sales_kpis, fetch_sales_reports, get_sales_trend_data, get_sales_by_payment_method

# === Reusable Utility ===
def get_download_path():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def open_file(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        print("Auto-open failed:", e)

# === Generate Graph for PDF ===
def generate_sales_trend_graph(start_date, end_date, output_path):
    delta_days = (end_date - start_date).days
    if delta_days <= 45:
        group_by = "day"
    elif delta_days <= 365:
        group_by = "month"
    else:
        group_by = "year"

    trend_data = get_sales_trend_data(start_date, end_date, group_by)
    dates = list(trend_data.keys())
    counts = list(trend_data.values())

    if not dates or not counts:
        return False

    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=100)
    ax.plot(dates, counts, marker='o', linestyle='-', color='teal')
    ax.set_title("Sales Trend", fontsize=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Number of Sales", fontsize=10)
    ax.grid(True)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=30, ha='right', fontsize=9)
    plt.tight_layout()

    fig.savefig(output_path)
    plt.close(fig)
    return True

# === Main Export Function ===
def download_report(start_date, end_date, selected_range_label, format_selected):
    downloads_folder = get_download_path()
    os.makedirs(downloads_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"Sales_Report_{selected_range_label.replace(' ', '_')}_{timestamp}"
    ext_map = {"CSV": ".csv", "Excel": ".xlsx", "PDF": ".pdf"}
    full_path = os.path.join(downloads_folder, base_filename + ext_map[format_selected])

    kpi_data = fetch_sales_kpis(start_date=start_date, end_date=end_date)
    records = fetch_sales_reports(start_date, end_date)
    payment_data = get_sales_by_payment_method(start_date, end_date)

    if not records:
        print("[INFO] No records to export.")
        return

    if format_selected == "CSV":
        import zipfile, shutil
        temp_dir = os.path.join(downloads_folder, f"sales_csv_temp_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)

        pd.DataFrame([
            ["Cars Sold", kpi_data["cars_sold"]],
            ["Revenue", f"${int(kpi_data['revenue']):,}"],
            ["Average Price", f"${int(kpi_data['avg_price']):,}"]
        ], columns=["Metric", "Value"]).to_csv(os.path.join(temp_dir, "sales_kpis.csv"), index=False)

        pd.DataFrame(records).to_csv(os.path.join(temp_dir, "sales_records.csv"), index=False)
        pd.DataFrame(payment_data.items(), columns=["Payment Method", "Count"]).to_csv(os.path.join(temp_dir, "payment_breakdown.csv"), index=False)

        with zipfile.ZipFile(full_path, "w") as zipf:
            for filename in os.listdir(temp_dir):
                zipf.write(os.path.join(temp_dir, filename), arcname=filename)

        shutil.rmtree(temp_dir)

    elif format_selected == "Excel":
        df_kpis = pd.DataFrame([
            {"Metric": "Cars Sold", "Value": kpi_data["cars_sold"]},
            {"Metric": "Revenue", "Value": f"${int(kpi_data['revenue']):,}"},
            {"Metric": "Average Price", "Value": f"${int(kpi_data['avg_price']):,}"}
        ])

        df_records = pd.DataFrame(records)
        df_payment = pd.DataFrame(payment_data.items(), columns=["Payment Method", "Count"])

        with pd.ExcelWriter(full_path) as writer:
            df_kpis.to_excel(writer, sheet_name="KPIs", index=False)
            df_records.to_excel(writer, sheet_name="Sales Records", index=False)
            df_payment.to_excel(writer, sheet_name="Payment Breakdown", index=False)

    elif format_selected == "PDF":
        graph_path = os.path.join(downloads_folder, "temp_sales_graph.png")
        generate_sales_trend_graph(start_date, end_date, graph_path)

        c = canvas.Canvas(full_path, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Sales Report")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Date Range: {start_date} to {end_date}")
        y -= 25

        # KPIs
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Key Performance Indicators:")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"- Cars Sold: {kpi_data['cars_sold']}")
        y -= 15
        c.drawString(60, y, f"- Revenue: ${int(kpi_data['revenue']):,}")
        y -= 15
        c.drawString(60, y, f"- Average Price: ${int(kpi_data['avg_price']):,}")
        y -= 25

        y -= 145
        # Chart: Sales Trend
        if os.path.exists(graph_path):
            if y < 250:
                c.showPage()
                y = height - 50
            c.drawImage(ImageReader(graph_path), 50, y - 150, width=500)
            y -= 229  # Extra padding after sales chart
            if y < 250:
                c.showPage()
                y = height - 50
            os.remove(graph_path)

        # Chart: Payment Method Pie
        if payment_data:
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            ax.pie(payment_data.values(), labels=payment_data.keys(), autopct='%1.1f%%', startangle=140)
            ax.set_title("Sales by Payment Method", fontsize=10)
            ax.axis('equal')
            pie_path = os.path.join(downloads_folder, "temp_payment_pie.png")
            fig.savefig(pie_path)
            plt.close(fig)

            if y < 250:
                c.showPage()
                y = height - 50
            c.drawImage(ImageReader(pie_path), 50, y - 150, width=500)
            y -= 300
            os.remove(pie_path)

        # Table: Payment Method Breakdown
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Payment Method Breakdown:")
        y -= 15
        c.setFont("Helvetica", 9)
        for method, count in payment_data.items():
            c.drawString(60, y, f"{method}: {count}")
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

        # Table: First 15 sales records
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Sample Sales Records:")
        y -= 15
        c.setFont("Helvetica", 8)
        headers = list(records[0].keys())
        for i, col in enumerate(headers[:5]):
            c.drawString(50 + i * 100, y, col)
        y -= 12
        for row in records[:15]:
            for i, val in enumerate(list(row.values())[:5]):
                c.drawString(50 + i * 100, y, str(val))
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

        c.save()

    open_file(full_path)
