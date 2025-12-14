from reportlab.lib.pagesizes import letter  # Tamaño carta (8.5" x 11") vertical
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

def generar_pdf_vertical(datos, filename="historia_clinica_vertical.pdf"):
    """
    Genera un PDF en orientación vertical con los datos del paciente y del médico.
    
    :param datos: Diccionario con todos los campos a mostrar.
    :param filename: Nombre del archivo PDF de salida.
    """
    # Crear documento en orientación vertical (por defecto)
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # --- Encabezado con logos y título ---
    logo_path = "logo.jpeg"  # Asegúrate de tener este archivo
    try:
        from reportlab.lib.utils import ImageReader
        logo = ImageReader(logo_path)
    except:
        logo = None

    data_encabezado = [
        [
            logo and [logo, 0.8*inch] or " ",  # Logo izquierdo
            Paragraph("<b>Mary's Pet</b><br/>Clínica Veterinaria", styles['Heading1']),
            logo and [logo, 0.8*inch] or " "  # Logo derecho
        ]
    ]

    tabla_encabezado = Table(data_encabezado, colWidths=[1.2*inch, 3.6*inch, 1.2*inch])
    tabla_encabezado.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, 0), (0, 0)),  # Logo izq
        ('SPAN', (2, 0), (2, 0)),  # Logo der
        ('LINEBELOW', (0, 0), (-1, 0), 1, (0, 0, 0)),
    ]))
    elements.append(tabla_encabezado)

    # Espaciado
    elements.append(Paragraph("<br/>", styles['Normal']))

    # --- Sección de datos: dos columnas ---
    data_cuerpo = [
        [
            Paragraph("<b>Dr.:</b>", styles['Normal']),
            Paragraph(str(datos.get('dr_paciente', 'N/A')), styles['Normal']),
            Paragraph("<b>Dr.:</b>", styles['Normal']),
            Paragraph(str(datos.get('dr_medico', 'N/A')), styles['Normal'])
        ],
        [
            Paragraph("<b>C.I.:</b>", styles['Normal']),
            Paragraph(str(datos.get('ci_paciente', 'N/A')), styles['Normal']),
            Paragraph("<b>C.I.:</b>", styles['Normal']),
            Paragraph(str(datos.get('ci_medico', 'N/A')), styles['Normal'])
        ],
        [
            Paragraph("<b>MPPS:</b>", styles['Normal']),
            Paragraph(str(datos.get('mpps_paciente', 'N/A')), styles['Normal']),
            Paragraph("<b>MPPS:</b>", styles['Normal']),
            Paragraph(str(datos.get('mpps_medico', 'N/A')), styles['Normal'])
        ],
        [
            Paragraph("<b>Paciente:</b>", styles['Normal']),
            Paragraph(str(datos.get('nombre_paciente', 'N/A')), styles['Normal']),
            Paragraph("<b>Paciente:</b>", styles['Normal']),
            Paragraph(str(datos.get('nombre_medico', 'N/A')), styles['Normal'])
        ],
    ]

    tabla_cuerpo = Table(data_cuerpo, colWidths=[1*inch, 2*inch, 1*inch, 2*inch], rowHeights=0.3*inch)
    tabla_cuerpo.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, (0.8, 0.8, 0.8)),
        ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
        ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
    ]))
    elements.append(tabla_cuerpo)

    # Espacio antes de firmas
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # --- Firmas ---
    data_firmas = [
        [
            Paragraph("Firma del Médico", styles['Italic']),
            "",
            Paragraph("Firma del Médico", styles['Italic']),
        ]
    ]
    tabla_firmas = Table(data_firmas, colWidths=[2*inch, 0.5*inch, 2*inch])
    tabla_firmas.setStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEABOVE', (0, 0), (0, 0), 1, (0, 0, 0)),
        ('LINEABOVE', (2, 0), (2, 0), 1, (0, 0, 0)),
    ])
    elements.append(tabla_firmas)

    # --- Pie de página ---
    elements.append(Paragraph("<br/>", styles['Normal']))
    direccion = "Av. El progreso, Jardines Alto Barinas, Conj. Apamates, Locales 8-A1 y B-2."
    telefono = "04143573522 / 04126920264"
    email = "maryspetbarinas@gmail.com"

    pie = f"""
    <para align=center>
        <b>Dirección:</b> {direccion}<br/>
        <b>Teléfono:</b> {telefono}<br/>
        <b>Email:</b> {email}
    </para>
    """
    elements.append(Paragraph(pie, styles['Normal']))

    # Construir el PDF
    doc.build(elements)
    print(f"✅ PDF generado: {filename}")


# === Ejemplo de uso ===
datos_ejemplo = {
    'dr_paciente': 'Dr. Juan Pérez',
    'ci_paciente': 'V-12.345.678',
    'mpps_paciente': 'MPPS-12345',
    'nombre_paciente': 'Raul Alberto',

    'dr_medico': 'Dr. Carlos Gómez',
    'ci_medico': 'V-98.765.432',
    'mpps_medico': 'MPPS-98765',
    'nombre_medico': 'Rex (Perro)'
}

# Generar el PDF
generar_pdf_vertical(datos_ejemplo)