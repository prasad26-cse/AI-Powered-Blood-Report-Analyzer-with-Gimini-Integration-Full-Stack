from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

def create_dummy_blood_report(username=None):
    """Create a dummy blood test report PDF for testing. Patient name is set to the given username."""
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate("data/dummy_blood_report.pdf", pagesize=letter)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Add title
    story.append(Paragraph("COMPREHENSIVE BLOOD TEST REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Patient information
    patient_info = [
        ["Patient Name:", username if username else "John Doe"],
        ["Date of Birth:", "15/03/1985"],
        ["Patient ID:", "P123456"],
        ["Test Date:", "28/06/2025"],
        ["Report Date:", "28/06/2025"],
        ["Lab:", "Medical Diagnostic Center"]
    ]
    
    patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 20))
    
    # Blood test results
    story.append(Paragraph("BLOOD TEST RESULTS", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Complete Blood Count (CBC)
    story.append(Paragraph("COMPLETE BLOOD COUNT (CBC)", styles['Heading3']))
    
    cbc_data = [
        ["Test", "Result", "Reference Range", "Units", "Status"],
        ["White Blood Cells (WBC)", "7.2", "4.5-11.0", "K/µL", "Normal"],
        ["Red Blood Cells (RBC)", "4.8", "4.5-5.9", "M/µL", "Normal"],
        ["Hemoglobin (HGB)", "14.2", "13.5-17.5", "g/dL", "Normal"],
        ["Hematocrit (HCT)", "42.5", "41.0-50.0", "%", "Normal"],
        ["Mean Corpuscular Volume (MCV)", "88.5", "80.0-100.0", "fL", "Normal"],
        ["Mean Corpuscular Hemoglobin (MCH)", "29.6", "27.0-33.0", "pg", "Normal"],
        ["Mean Corpuscular Hemoglobin Concentration (MCHC)", "33.4", "32.0-36.0", "g/dL", "Normal"],
        ["Platelets", "250", "150-450", "K/µL", "Normal"],
        ["Neutrophils", "65", "40-70", "%", "Normal"],
        ["Lymphocytes", "25", "20-40", "%", "Normal"],
        ["Monocytes", "8", "2-10", "%", "Normal"],
        ["Eosinophils", "2", "1-4", "%", "Normal"],
        ["Basophils", "0.5", "0-1", "%", "Normal"]
    ]
    
    cbc_table = Table(cbc_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 0.8*inch, 1*inch])
    cbc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (4, -1), 'CENTER'),
    ]))
    
    story.append(cbc_table)
    story.append(Spacer(1, 20))
    
    # Comprehensive Metabolic Panel (CMP)
    story.append(Paragraph("COMPREHENSIVE METABOLIC PANEL (CMP)", styles['Heading3']))
    
    cmp_data = [
        ["Test", "Result", "Reference Range", "Units", "Status"],
        ["Glucose (Fasting)", "95", "70-100", "mg/dL", "Normal"],
        ["Blood Urea Nitrogen (BUN)", "15", "7-20", "mg/dL", "Normal"],
        ["Creatinine", "0.9", "0.7-1.3", "mg/dL", "Normal"],
        ["Sodium", "140", "135-145", "mEq/L", "Normal"],
        ["Potassium", "4.0", "3.5-5.0", "mEq/L", "Normal"],
        ["Chloride", "102", "96-106", "mEq/L", "Normal"],
        ["CO2 (Bicarbonate)", "24", "22-28", "mEq/L", "Normal"],
        ["Calcium", "9.5", "8.5-10.5", "mg/dL", "Normal"],
        ["Total Protein", "7.2", "6.0-8.3", "g/dL", "Normal"],
        ["Albumin", "4.2", "3.5-5.0", "g/dL", "Normal"],
        ["Total Bilirubin", "0.8", "0.3-1.2", "mg/dL", "Normal"],
        ["Alkaline Phosphatase", "70", "44-147", "U/L", "Normal"],
        ["AST (SGOT)", "25", "10-40", "U/L", "Normal"],
        ["ALT (SGPT)", "30", "7-56", "U/L", "Normal"]
    ]
    
    cmp_table = Table(cmp_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 0.8*inch, 1*inch])
    cmp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (4, -1), 'CENTER'),
    ]))
    
    story.append(cmp_table)
    story.append(Spacer(1, 20))
    
    # Lipid Panel
    story.append(Paragraph("LIPID PANEL", styles['Heading3']))
    
    lipid_data = [
        ["Test", "Result", "Reference Range", "Units", "Status"],
        ["Total Cholesterol", "180", "<200", "mg/dL", "Normal"],
        ["HDL Cholesterol", "55", ">40", "mg/dL", "Normal"],
        ["LDL Cholesterol", "100", "<100", "mg/dL", "Normal"],
        ["Triglycerides", "120", "<150", "mg/dL", "Normal"],
        ["Cholesterol/HDL Ratio", "3.3", "<5.0", "", "Normal"]
    ]
    
    lipid_table = Table(lipid_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 0.8*inch, 1*inch])
    lipid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (4, -1), 'CENTER'),
    ]))
    
    story.append(lipid_table)
    story.append(Spacer(1, 20))
    
    # Thyroid Function Tests
    story.append(Paragraph("THYROID FUNCTION TESTS", styles['Heading3']))
    
    thyroid_data = [
        ["Test", "Result", "Reference Range", "Units", "Status"],
        ["TSH (Thyroid Stimulating Hormone)", "2.5", "0.4-4.0", "µIU/mL", "Normal"],
        ["Free T4", "1.2", "0.8-1.8", "ng/dL", "Normal"],
        ["Free T3", "3.2", "2.3-4.2", "pg/mL", "Normal"]
    ]
    
    thyroid_table = Table(thyroid_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 0.8*inch, 1*inch])
    thyroid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (4, -1), 'CENTER'),
    ]))
    
    story.append(thyroid_table)
    story.append(Spacer(1, 20))
    
    # Summary and interpretation
    story.append(Paragraph("SUMMARY AND INTERPRETATION", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    summary_text = """
    <b>Overall Assessment:</b> All blood test results are within normal reference ranges.
    
    <b>Key Findings:</b>
    • Complete Blood Count (CBC): All parameters normal, indicating healthy blood cell production
    • Comprehensive Metabolic Panel (CMP): Normal kidney and liver function, balanced electrolytes
    • Lipid Panel: Excellent cholesterol profile with low cardiovascular risk
    • Thyroid Function: Normal thyroid hormone levels
    
    <b>Recommendations:</b>
    • Continue current lifestyle and diet
    • Maintain regular exercise routine
    • Schedule follow-up in 6-12 months for routine monitoring
    
    <b>Notes:</b>
    This report represents a comprehensive health assessment. All values are within normal limits, indicating good overall health status.
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Footer
    footer_text = """
    <b>Report Generated By:</b> Medical Diagnostic Center<br/>
    <b>Lab Director:</b> Dr. Sarah Johnson, MD<br/>
    <b>Phone:</b> (555) 123-4567<br/>
    <b>Email:</b> lab@medicaldiagnostic.com<br/>
    <b>Address:</b> 123 Medical Center Dr, Healthcare City, HC 12345
    """
    
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print("Dummy blood test report created: data/dummy_blood_report.pdf")

if __name__ == "__main__":
    create_dummy_blood_report() 