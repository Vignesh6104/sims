from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report_card(student, marks_data, exam_name="Report Card"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"{exam_name} - {student.full_name}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Student Info
    elements.append(Paragraph(f"<b>Roll Number:</b> {student.roll_number}", styles['Normal']))
    
    class_name = 'N/A'
    if hasattr(student, 'classroom') and student.classroom:
        class_name = student.classroom.name
        
    elements.append(Paragraph(f"<b>Class:</b> {class_name}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Marks Table
    data = [['Subject', 'Score', 'Max Score', 'Grade']]
    total_obtained = 0.0
    total_max = 0.0
    
    for mark in marks_data:
        subject_name = mark.subject 
        obtained = mark.score
        max_marks = mark.max_score
        
        # Calculate grade
        percentage = (obtained / max_marks) * 100 if max_marks > 0 else 0
        grade = "F"
        if percentage >= 90: grade = "A+"
        elif percentage >= 80: grade = "A"
        elif percentage >= 70: grade = "B"
        elif percentage >= 60: grade = "C"
        elif percentage >= 50: grade = "D"

        data.append([subject_name, str(obtained), str(max_marks), grade])
        total_obtained += obtained
        total_max += max_marks

    # Total Row
    data.append(['Total', str(total_obtained), str(total_max), ''])

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
