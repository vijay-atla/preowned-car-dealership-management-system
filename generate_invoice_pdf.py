from fpdf import FPDF
import os
from database_utils import fetch_invoice_data
from datetime import datetime

def get_downloads_folder():
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

class InvoicePDF(FPDF):
    def header(self):
        logo_path = "icons/pcds_logo.png"  # Adjust your logo path
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        self.set_font("Arial", "B", 20)
        self.cell(0, 10, "INVOICE", ln=True, align="R")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Pre-Owned Car Dealership System", ln=True, align="R")
        self.cell(0, 5, "1011 S Main St, Mt Pleasant, MI, USA - 48858", ln=True, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "I", 9)
        self.multi_cell(0, 5,
            "Note: This is a computer-generated receipt. No physical signature is required.\n"
            "You can also download this invoice online by logging into your customer portal using your email and default password 'Customer@123'.",
            align="C"
        )

def generate_invoice_pdf(invoice_number):
    invoice_data = fetch_invoice_data(invoice_number)
    if not invoice_data:
        print("No invoice data found!")
        return None

    pdf = InvoicePDF()
    pdf.add_page()

    # --- Invoice and Order Info ---
    pdf.set_font("Arial", "", 12)
    sale_date = invoice_data['sale_date']
    if isinstance(sale_date, datetime):
        sale_date = sale_date.strftime("%B %d, %Y")
    else:
        sale_date = datetime.strptime(sale_date, "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y")
    
    pdf.cell(100, 8, f"Invoice Number: #{invoice_data['invoice_number']}")
    pdf.cell(0, 8, f"Invoice Date: {sale_date}", ln=True)

    pdf.ln(8)

    # --- Customer Information ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Billing Address", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, f"{invoice_data['customer_name']}\n{invoice_data['customer_address'].upper()}\nPhone: {invoice_data['customer_phone']}\nEmail: {invoice_data['customer_email']}")
    
    pdf.ln(5)

    # --- Car Information ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Car Information", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Make: {invoice_data['car_make']}", ln=True)
    pdf.cell(0, 7, f"Model: {invoice_data['car_model']}", ln=True)
    pdf.cell(0, 7, f"Color: {invoice_data['car_color']}", ln=True)
    pdf.cell(0, 7, f"VIN: {invoice_data['car_vin']}", ln=True)

    pdf.ln(8)

    # --- Price Table ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Price Details", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(230, 230, 230)  # Light Gray
    pdf.cell(100, 8, "Description", border=1, fill=True)
    pdf.cell(0, 8, "Amount", border=1, fill=True, ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(100, 8, "Listing Price", border=1)
    pdf.cell(0, 8, f"${float(invoice_data['listing_price']):,.2f}", border=1, ln=True)

    pdf.cell(100, 8, "Discount", border=1)
    pdf.cell(0, 8, f"- ${float(invoice_data['discount']):,.2f}", border=1, ln=True)

    pdf.cell(100, 8, f"Tax ({invoice_data['tax_percent']}%)", border=1)
    pdf.cell(0, 8, f"${float(invoice_data['tax_amount']):,.2f}", border=1, ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(100, 8, "Total Price", border=1)
    pdf.cell(0, 8, f"${float(invoice_data['total_price']):,.2f}", border=1, ln=True)

    pdf.ln(10)

    # --- Payment Information ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Payment Information", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Payment Method: {invoice_data['payment_method']}", ln=True)
    pdf.cell(0, 8, f"Reference Number: {invoice_data['payment_reference']}", ln=True)

    pdf.ln(10)

    # --- Authorized By (Staff) ---
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 8, f"Authorized by: {invoice_data['staff_name']}", ln=True)

    # --- Save to Downloads ---
    downloads_folder = get_downloads_folder()
    os.makedirs(downloads_folder, exist_ok=True)

    filename = os.path.join(downloads_folder, f"Invoice #{invoice_number}.pdf")
    pdf.output(filename)

    return filename
