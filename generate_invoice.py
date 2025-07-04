from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from datetime import datetime
import qrcode
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os, webbrowser
from database_utils import fetch_invoice_data

# === Register Verdana Fonts ===
pdfmetrics.registerFont(TTFont("Verdana", "fonts/Verdana.ttf"))
pdfmetrics.registerFont(TTFont("Verdana-Bold", "fonts/Verdana_Bold.ttf"))
pdfmetrics.registerFont(TTFont("Verdana-Italic", "fonts/Verdana_Italic.ttf"))
pdfmetrics.registerFont(TTFont("Verdana-BoldItalic", "fonts/Verdana_Bold_Italic.ttf"))


def get_downloads_folder():
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


# === Main: Generate PDF Invoice ===
def generate_invoice(invoice_number):
    invoice_data = fetch_invoice_data(invoice_number)
    if not invoice_data:
        print("Invoice not found.")
        return

    file_path = os.path.join(get_downloads_folder(), f"INV_#{invoice_number}.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=40, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    # === Custom Styles ===
    heading = ParagraphStyle("Heading", fontSize=20, spaceAfter=10, alignment=TA_CENTER)
    bold = ParagraphStyle("Bold", parent=styles["Normal"], fontName="Helvetica-Bold")
    italic = ParagraphStyle("Italic", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=9)
    right = ParagraphStyle("Right", parent=styles["Normal"], alignment=TA_RIGHT)
    gray = ParagraphStyle("Gray", parent=styles["Normal"], textColor=colors.gray, fontSize=9)

    # === Header: Logo + Title ===
    logo_img = Image("icons/pcds_logo.png", width=50, height=50)
    title_para = Paragraph("SALE INVOICE", heading)

    dealership_info = Paragraph(
        "<b>Pre-Owned Car Dealership System</b><br/>"
        "<font color='white'>_            _</font>1011 S Main St, <br/>"
        "<font color='white'>_            _</font>Mt Pleasant,    <br/>"
        "<font color='white'>_            _</font>MI, USA - 48858 <br/>"
        "<font color='white'>_            _</font>+1 9876543210   <br/>"
        "<font color='white'>_            _</font><font color='blue'>cars@pcds.com</font>", gray
    )
    # === Logo (left) + Title (centered) in a table ===
    header_table = Table([["", logo_img, title_para, dealership_info]], colWidths=[0, 150, 270, 150])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))


    elements.append(header_table)

    elements.append(Spacer(1, 40))  # ⬅️ Pushes content ~30 points lower

    # === Customer + Invoice Info Table ===
    customer_name = invoice_data["customer_name"]
    customer_address = invoice_data["customer_address"]
    phone = invoice_data["customer_phone"]
    email = invoice_data["customer_email"]

    customer_info = [
        [Paragraph("<b>CUSTOMER DETAILS:</b>", bold), ""],
        [Paragraph(customer_name, styles["Normal"]),
         Paragraph(f"<b>Invoice Number:</b> #{invoice_number}", right)],
        [Paragraph(customer_address.upper(), styles["Normal"]),
         Paragraph(f"<b>Invoice Date:</b><font color='white'>_         _</font>" f"{invoice_data['sale_date'].strftime('%B %d, %Y')}<font color='white'>_               _</font>", right)],
        [Paragraph(phone, styles["Normal"]), ""],
        [Paragraph(email, styles["Normal"]), ""]
    ]
    t1 = Table(customer_info, colWidths=[300, 200])
    elements.append(t1)
    elements.append(Spacer(1, 12))

    elements.append(Spacer(1, 30))  # ⬅️ Pushes content ~30 points lower


    # === Car Info Section ===
    # Prepare styled paragraphs with line breaks
    car_info = Paragraph(
        f"<b>{invoice_data['car_make']} {invoice_data['car_model']} {invoice_data['car_year']}</b> {invoice_data['car_color']} {invoice_data['car_fuel']}<br/><br/>"
        f"VIN: {invoice_data['car_vin']} | {invoice_data.get('car_transmission', 'Manual')} | {invoice_data['car_mileage']} mi. | {invoice_data['car_title']} Title",
        styles["Normal"]
    )

    price_para = Paragraph(f"${invoice_data['listing_price']:,.2f}", right)
    elements.append(Paragraph("<b>CAR INFORMATION:</b>", bold))
    elements.append(Spacer(1, 6))

    # Wrap price into a nested table to allow vertical + horizontal center alignment
    price_table = Table([[price_para]], colWidths=[70], rowHeights=[48])
    price_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    # Full car info table: [left details, right price block]
    car_info_table = Table([
        [car_info, price_table]
    ], colWidths=[420, 100], rowHeights=[55])  # ⬅️ Taller row

    car_info_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.white),
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 8),
        ('RIGHTPADDING', (0, 0), (0, 0), 8),
        ('TOPPADDING', (0, 0), (0, 0), 6),
        ('BOTTOMPADDING', (0, 0), (0, 0), 4),
    ]))

    elements.append(car_info_table)
    elements.append(Spacer(1, 8))

    # Prepare the two left-aligned lines
    payment_lines = [
        Paragraph("<br/>", styles["Normal"]),
        Paragraph("<b>Payment Information</b>", bold),
        Paragraph(f"Payment method: {invoice_data['payment_method']}", styles["Normal"]),
        Paragraph(f"Ref. Number: {invoice_data['payment_reference']}", styles["Normal"])
    ]

    # Combine them into a paragraph list block
    left_payment_block = Table([[p] for p in payment_lines], colWidths=[300])
    left_payment_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12)
    ]))

    # Amounts block (no listing price)
    amount_table = Table([
        [Paragraph(f"Discount""<font color='white'>_       _</font>", right), Paragraph(f"-${invoice_data['discount']:,.2f}", right)],
        [Paragraph("Tax (6.00%)", right), Paragraph(f"${invoice_data['tax_amount']:,.2f}", right)],
        [Paragraph("<b>Total Price</b>", right), Paragraph(f"<b>${invoice_data['total_price']:,.2f}</b>", right)]
    ], colWidths=[100, 100])

    amount_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (1, 2), (1, 2), 1, colors.black),
    ]))

    # Combine both into a 2-column master table
    summary_table = Table([[left_payment_block, amount_table]], colWidths=[285, 215])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 50))

    elements.append(Spacer(1, 30))
    # Save QR image
    qr_path = f"temp_images/temp_qr_{invoice_number}.png"
    qrcode.make(invoice_number).save(qr_path)
    text = f"Invoice: {invoice_number}\nAmount: ${invoice_data['total_price']:,}\nDate: {invoice_data['sale_date'].strftime('%B %d, %Y')}"
    qrcode.make(text).save(qr_path)

    # Load image
    qr_img = Image(qr_path, width=100, height=100)



    # === Signature Section (optional image) ===
    signature_img = Image("icons/signature.png", width=150, height=60)
    auth_text = Paragraph("<i>Authorized by:</i> " + invoice_data['staff_name'], italic)

    right_signature_block = Table([[signature_img], [auth_text]], colWidths=[200])
    right_signature_block.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))


    qr_sig_table = Table([
        ["", qr_img, right_signature_block]
    ], colWidths=[30, 250, 220])  # Adjust width as needed

    qr_sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(Spacer(1, 20))
    elements.append(qr_sig_table)
    elements.append(Spacer(1, 30))





    elements.append(Spacer(1, 30))
    # === Footer Notes ===
    elements.append(Paragraph(
        "<i>Note: This is a computer-generated receipt. No physical signature is required.</i>",
        italic
    ))
    elements.append(Paragraph(
        "<i>You can also download this invoice online by logging into your customer portal using your email and default password 'Customer@123'.</i>",
        italic
    ))

    # === Build PDF ===
    doc.build(elements)
    if os.path.exists(qr_path):
        os.remove(qr_path)

    webbrowser.open(f"file://{file_path}")
    return file_path