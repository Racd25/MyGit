from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors

def generar_pdf_vertical(datos, filename="historia_clinica_vertical.pdf"):
    """
    Genera un PDF en orientación vertical con los datos del paciente y del médico.
    
    :param datos: Diccionario con todos los campos a mostrar.
    :param filename: Nombre del archivo PDF de salida.
    """
    # Crear documento
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    ficha_numero = datos.get('ficha_numero', 'N/A')

    # --- Encabezado con logos y título ---
    titulo = "<b>Inrema</b><br/>Ficha Nº"
    if ficha_numero is not None:
        titulo += f" {ficha_numero}"

    data_encabezado = [
        [Paragraph(titulo, styles['Heading1'])]
    ]
    tabla_encabezado = Table(data_encabezado, colWidths=[1.2*inch, 3.6*inch, 1.2*inch])
    tabla_encabezado.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(tabla_encabezado)

    # Espacio
    elements.append(Spacer(1, 0.2*inch))

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
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
        ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
    ]))
    elements.append(tabla_cuerpo)

    # Espacio antes de firmas
    elements.append(Spacer(1, 0.3*inch))

    # --- Firmas ---
    data_firmas = [
        [
            Paragraph("Firma del Médico", styles['Italic']),
            "",
            Paragraph("Firma del Paciente", styles['Italic']),
        ]
    ]
    tabla_firmas = Table(data_firmas, colWidths=[2*inch, 0.5*inch, 2*inch])
    tabla_firmas.setStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),
        ('LINEABOVE', (2, 0), (2, 0), 1, colors.black),
    ])
    elements.append(tabla_firmas)

    # --- Pie de página ---
    elements.append(Spacer(1, 0.2*inch))
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
    'Cliente': 'Pepe',
    'Marca': 'V-12.345.678',
    'mpps_paciente': 'MPPS-12345',
    'nombre_paciente': 'Raul Alberto',

    'dr_medico': 'Dr. Carlos Gómez',
    'ci_medico': 'V-98.765.432',
    'mpps_medico': 'MPPS-98765',
    'nombre_medico': 'Rex (Perro)',
    'ficha_numero': '10'
}

# Generar el PDF
generar_pdf_vertical(datos_ejemplo)