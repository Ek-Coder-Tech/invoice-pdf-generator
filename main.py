import csv
import os
from collections import defaultdict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
    )
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    # Create output folder
os.makedirs("invoices", exist_ok=True)

    # Load invoice data
invoices = defaultdict(list)
with open("invoices.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            invoices[row['invoice_number']].append(row)

    # Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='InvoiceTitle', fontSize=18, leading=22, spaceAfter=12))
styles.add(ParagraphStyle(name='ClientInfo', fontSize=10, leading=14, spaceAfter=6))
bold_style = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold')

    # Generate PDFs
for invoice_number, rows in invoices.items():
        first = rows[0]
        client_name = first['client_name']
        client_email = first['client_email']
        date = first['date']

        filename = f"invoices/{invoice_number}.pdf"
        doc = SimpleDocTemplate(
            filename, pagesize=A4,
            leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40
        )
        elements = []

        # Add logo if available
        if os.path.isfile("logo.png"):
            elements.append(Image("logo.png", width=100, height=40))
            elements.append(Spacer(1, 12))

        # Header info
        elements.append(Paragraph(f"Invoice #{invoice_number}", styles['InvoiceTitle']))
        elements.append(Paragraph(f"Date: {date}", styles['ClientInfo']))
        elements.append(Paragraph(f"Bill To: {client_name} &lt;{client_email}&gt;", styles['ClientInfo']))
        elements.append(Spacer(1, 10))

        # Table content
        data = [["Description", "Qty", "Unit Price", "Total"]]
        total = 0
        for item in rows:
            qty = int(item["quantity"])
            price = float(item["unit_price"])
            line_total = qty * price
            total += line_total
            data.append([item["item_description"], qty, f"${price:.2f}", f"${line_total:.2f}"])

        # Grand total row with clear formatting
        data.append(["", "", "Grand Total:", f"${total:.2f}"])

        # Table styling
        table = Table(data, colWidths=[220, 60, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#333333")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            # Grand Total style
            ('FONTNAME', (2, -1), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, -1), (3, -1), 'Helvetica-Bold'),
            ('ALIGN', (3, -1), (3, -1), 'RIGHT'),
        ]))

        elements.append(table)
        doc.build(elements)
        print(f"✅ Styled invoice created: {filename}")
