from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, text
from database import get_session
from typing import Dict, Any
import pandas as pd
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, date

app = FastAPI()

@app.get("/reports/stats")
def get_stats(session: Session = Depends(get_session)):
    # Total equipment
    total_equipment = session.exec(text("SELECT COUNT(*) FROM equipment")).one()[0]
    # Equipment by status
    status_counts = session.exec(text("SELECT status, COUNT(*) FROM equipment GROUP BY status")).all()
    # Total maintenance cost
    total_cost = session.exec(text("SELECT SUM(cost) FROM maintenance")).one()[0]
    
    return {
        "total_equipment": total_equipment,
        "equipment_by_status": {s: c for s, c in status_counts},
        "total_maintenance_cost": total_cost or 0
    }

@app.get("/reports/export/excel")
def export_excel(session: Session = Depends(get_session)):
    # Fetch data
    query = text("SELECT * FROM equipment")
    result = session.exec(query).all()
    # Convert to dict list
    data = [dict(row._mapping) for row in result]
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Equipment')
    
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="inventory_report.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.get("/reports/export/pdf")
def export_pdf(session: Session = Depends(get_session)):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("Reporte de Inventario IT", styles['Title']))
    elements.append(Spacer(1, 20))
    
    # 1. Estado del equipo
    elements.append(Paragraph("Estado del equipo", styles['Heading2']))
    status_data = session.exec(text("SELECT status, COUNT(*) FROM equipment GROUP BY status")).all()
    total_eq = sum([c for s, c in status_data])
    
    table_data = [['Estado', 'Cantidad', 'Porcentaje (%)']]
    for status, count in status_data:
        pct = (count / total_eq * 100) if total_eq > 0 else 0
        table_data.append([status, str(count), f"{pct:.2f}"])
        
    t = Table(table_data, colWidths=[200, 100, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # 2. Costos de mantenimiento (12 meses)
    elements.append(Paragraph("Costos de mantenimiento (12 meses)", styles['Heading2']))
    # Note: SQLite/Postgres syntax difference might be tricky. Assuming Postgres as per docker-compose.
    maint_query = text("""
        SELECT to_char(date, 'YYYY-MM') as month, SUM(cost) 
        FROM maintenance 
        WHERE date >= CURRENT_DATE - INTERVAL '1 year' 
        GROUP BY month 
        ORDER BY month DESC
    """)
    maint_data = session.exec(maint_query).all()
    
    if not maint_data:
        elements.append(Paragraph("No data available.", styles['Normal']))
    else:
        table_data = [['Mes', 'Costo Total']]
        for month, cost in maint_data:
            table_data.append([month, f"${cost:,.2f}"])
            
        t = Table(table_data, colWidths=[200, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
    elements.append(Spacer(1, 20))

    # 3. Equipos por ubicación
    elements.append(Paragraph("Equipos por ubicación", styles['Heading2']))
    loc_data = session.exec(text("SELECT location, COUNT(*) FROM equipment GROUP BY location")).all()
    
    table_data = [['Ubicación', 'Cantidad de equipos']]
    for loc, count in loc_data:
        table_data.append([loc or "Sin ubicación", str(count)])
        
    t = Table(table_data, colWidths=[300, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # 4. Mantenimientos por tipo
    elements.append(Paragraph("Mantenimientos por tipo", styles['Heading2']))
    type_data = session.exec(text("SELECT type, COUNT(*), SUM(cost) FROM maintenance GROUP BY type")).all()
    
    table_data = [['Tipo de mantenimiento', 'Cantidad', 'Costo total']]
    for m_type, count, cost in type_data:
        table_data.append([m_type, str(count), f"{cost:,.2f}"])
        
    t = Table(table_data, colWidths=[200, 100, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # 5. Antigüedad del equipo
    elements.append(Paragraph("Antigüedad del equipo", styles['Heading2']))
    dates = session.exec(text("SELECT purchase_date FROM equipment")).all()
    
    age_buckets = {
        "<1 year": 0,
        "1-3 years": 0,
        "3-5 years": 0,
        "5-10 years": 0,
        "10+ years": 0
    }
    
    today = date.today()
    for (p_date,) in dates:
        if p_date:
            # Calculate age in years roughly
            age = (today - p_date).days / 365.25
            if age < 1:
                age_buckets["<1 year"] += 1
            elif age < 3:
                age_buckets["1-3 years"] += 1
            elif age < 5:
                age_buckets["3-5 years"] += 1
            elif age < 10:
                age_buckets["5-10 years"] += 1
            else:
                age_buckets["10+ years"] += 1
                
    table_data = [['Rango de antigüedad', 'Cantidad de equipos']]
    for bucket, count in age_buckets.items():
        table_data.append([bucket, str(count)])
        
    t = Table(table_data, colWidths=[200, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    
    doc.build(elements)
    buffer.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="inventory_report.pdf"'
    }
    return StreamingResponse(buffer, headers=headers, media_type='application/pdf')
