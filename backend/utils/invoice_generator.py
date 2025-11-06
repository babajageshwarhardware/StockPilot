from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(sale_data: dict) -> bytes:
    """Generate PDF invoice for a sale"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4b5563')
    )
    
    # Title
    title = Paragraph("INVOICE", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Company Info and Invoice Details
    invoice_info = [
        ["<b>StockPilot</b>", "", f"<b>Invoice No:</b> {sale_data['invoiceNumber']}"],
        ["Store Management System", "", f"<b>Date:</b> {sale_data['saleDate'].strftime('%d-%m-%Y %H:%M')}"],
        ["support@stockpilot.com", "", f"<b>Payment:</b> {sale_data['paymentMode'].upper()}"],
    ]
    
    info_table = Table(invoice_info, colWidths=[2.5*inch, 1*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer Info
    if sale_data.get('customerName'):
        customer_heading = Paragraph("<b>Bill To:</b>", heading_style)
        elements.append(customer_heading)
        
        customer_data = [
            [f"<b>{sale_data['customerName']}</b>"],
        ]
        if sale_data.get('customerPhone'):
            customer_data.append([f"Phone: {sale_data['customerPhone']}"])
        
        customer_table = Table(customer_data, colWidths=[6*inch])
        customer_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#4b5563')),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Items Table
    items_heading = Paragraph("<b>Items:</b>", heading_style)
    elements.append(items_heading)
    
    # Table headers
    table_data = [
        ['#', 'Product', 'SKU', 'Qty', 'Price', 'Discount', 'Tax', 'Total']
    ]
    
    # Add items
    for idx, item in enumerate(sale_data['items'], 1):
        discount_str = f"₹{item['discount']:.2f}" if item['discountType'] == 'fixed' else f"{item['discount']}%"
        table_data.append([
            str(idx),
            item['productName'][:30],
            item['sku'],
            f"{item['quantity']:.2f}",
            f"₹{item['unitPrice']:.2f}",
            discount_str,
            f"₹{item.get('taxAmount', 0):.2f}",
            f"₹{item['lineTotal']:.2f}"
        ])
    
    # Create table
    items_table = Table(table_data, colWidths=[0.4*inch, 2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.9*inch])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#4b5563')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totals
    totals_data = [
        ['', '', '', '', '', '', '<b>Subtotal:</b>', f"₹{sale_data['subtotal']:.2f}"],
    ]
    
    if sale_data.get('discountAmount', 0) > 0:
        totals_data.append([
            '', '', '', '', '', '', '<b>Discount:</b>', f"-₹{sale_data['discountAmount']:.2f}"
        ])
    
    if sale_data.get('taxAmount', 0) > 0:
        totals_data.append([
            '', '', '', '', '', '', '<b>Tax:</b>', f"₹{sale_data['taxAmount']:.2f}"
        ])
    
    totals_data.append([
        '', '', '', '', '', '', '<b>TOTAL:</b>', f"<b>₹{sale_data['total']:.2f}</b>"
    ])
    
    if sale_data.get('amountPaid', 0) > 0:
        totals_data.append([
            '', '', '', '', '', '', '<b>Paid:</b>', f"₹{sale_data['amountPaid']:.2f}"
        ])
        balance = sale_data['total'] - sale_data['amountPaid']
        if balance > 0:
            totals_data.append([
                '', '', '', '', '', '', '<b>Balance:</b>', f"<b>₹{balance:.2f}</b>"
            ])
    
    totals_table = Table(totals_data, colWidths=[0.4*inch, 2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.9*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
        ('ALIGN', (7, 0), (7, -1), 'RIGHT'),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('LINEABOVE', (6, -1), (7, -1), 2, colors.HexColor('#1f2937')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Notes
    if sale_data.get('notes'):
        notes_heading = Paragraph("<b>Notes:</b>", heading_style)
        elements.append(notes_heading)
        notes_text = Paragraph(sale_data['notes'], normal_style)
        elements.append(notes_text)
        elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    footer = Paragraph("Thank you for your business!", footer_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get the PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
