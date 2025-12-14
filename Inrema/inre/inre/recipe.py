from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf(datos):
    """
    Genera un PDF con los datos de la historia clínica.
    
    :param datos: Diccionario con los datos del paciente y el médico.
    """
    # Crear el archivo PDF
    c = canvas.Canvas("recipe.pdf", pagesize=landscape(letter))
    
    # Configuración básica
    width, height = landscape(letter)
    margen_izquierdo = 0.5 * inch
    margen_superior = 0.5 * inch
    centro = width / 2
    margen_x = 0.5 * inch
    margen_y = 0.5 * inch
    centro = width / 2
    pie_y = margen_y + 0.6 * inch

    # Datos del paciente
    nombre = datos.get('nombre', 'N/A')
    ci = datos.get('ci', 'N/A')
    cmvb = datos.get('cmvb', 'N/A')
    mpps= datos.get('mpps', 'N/A')
    paciente = datos.get('paciente', 'N/A')
    rp = datos.get('rp', 'N/A')
    ind = datos.get('ind', 'N/A')


    # Datos del médico



    # Logos y encabezados
    logo_path = "Logo.jpeg"  # Reemplaza con la ruta al logo
    try:
        # Imagen en la columna izquierda
        x_logo_izq = margen_izquierdo
        y_logo = height - 1.5 * inch
        logo_size = 1.5 * inch
        c.drawImage(logo_path, x_logo_izq, y_logo, width=logo_size, height=logo_size)

        # Texto al lado de la imagen (columna izquierda)
        x_texto_izq = x_logo_izq + logo_size + 0.2 * inch  # Espacio entre imagen y texto
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_texto_izq, y_logo + 1 * inch, f"Dr.: {nombre}")
        c.drawString(x_texto_izq, y_logo + 0.8 * inch, f"C.I.: V-{ci}")
        c.drawString(x_texto_izq, y_logo + 0.6 * inch, f"CMVB: {cmvb}")
        c.drawString(x_texto_izq, y_logo + 0.4 * inch, f"MPPS: {mpps}")
        c.drawString(x_texto_izq, y_logo + 0.2 * inch, f"Paciente: {paciente}")

        # Imagen en la columna derecha
        x_logo_der = centro + margen_izquierdo
        c.drawImage(logo_path, x_logo_der, y_logo, width=logo_size, height=logo_size)

        # Texto al lado de la imagen (columna derecha)
        x_texto_der = x_logo_der + logo_size + 0.2 * inch  # Espacio entre imagen y texto
        c.drawString(x_texto_der, y_logo + 1 * inch, f"Dr.: {nombre}")
        c.drawString(x_texto_der, y_logo + 0.8 * inch, f"C.I.: V- {ci}")
        c.drawString(x_texto_der, y_logo  + 0.6 * inch, f"CMVB: {cmvb}")
        c.drawString(x_texto_der, y_logo + 0.4 *inch, f"MPPS: {mpps}")
        c.drawString(x_texto_der, y_logo + 0.2 * inch, f"Paciente: {paciente}")
        
    except Exception as e:
        print(f"Advertencia: No se pudo cargar el logo: {e}")

    # Encabezado personalizado
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margen_izquierdo, height - 1.5 * inch, f"Medicina Interna y Cirugia")
    c.drawString(width / 2 + margen_izquierdo, height - 1.5 * inch, f"Medicina Interna y Cirugia")

    c.setFont("Helvetica-Bold", 8)
    c.drawString(margen_izquierdo + 0.15 * inch, height - 1.6 * inch, f"de Tejidos Blandos")
    c.drawString(width / 2 + margen_izquierdo +0.15 *inch, height - 1.6 * inch, f"de Tejidos Blandos")

    c.drawString(margen_izquierdo+ 0.25 * inch, height - 1.7 * inch, f"en Mascotas.")
    c.drawString(width / 2 + margen_izquierdo + 0.25*inch,  height - 1.7 * inch, f"en Mascotas.")

    c.drawString(margen_izquierdo, height - 1.9 * inch, f"Consulta, Cirugias, PetShop, Peluquería Canina, Hospitalización, Hospedaje, Laboratorio")
    c.drawString(width / 2 + margen_izquierdo, height - 1.9 * inch, f"Consulta, Cirugias, PetShop, Peluquería Canina, Hospitalización, Hospedaje, Laboratorio")
    

    # Línea separadora
    c.line(0, height - 2.0 * inch, 792, height - 2.0 * inch)
    c.line(396, 612, 396, 0)  # línea vertical de arriba hacia abajo
    c.line(275, pie_y, 375, pie_y)
    
    c.drawString(290, pie_y- 0.1 * inch, " Firma Del Médico")
    
    x = 0.5 * inch
    y = 1.75 * inch
    ancho = 4 * inch
    alto = 4 * inch

# Aplicar efecto de marca de agua
    c.saveState()
    c.setFillAlpha(0.2)  # Transparencia del contenido dibujado después
    c.drawImage("Logo.jpeg", x, y, width=ancho, height=alto, mask='auto')
    c.drawImage("Logo.jpeg", x + centro, y, width=ancho, height=alto, mask='auto')
    c.restoreState()




    
    c.line(275+ width/2, pie_y, 375+ width/2, pie_y)
    c.drawString(290 + width/2, pie_y- 0.1 * inch, " Firma Del Médico")
    


    # Sección central
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen_izquierdo, height - 2.2 * inch, "Rp.")
    c.drawString(width / 2 + margen_izquierdo, height - 2.2 * inch, "Ind.")

    # Pie de página
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margen_x + 1 * inch, pie_y - 0.4 *inch, " 04143573522 / 04126920264 / 04127649580")
    c.drawString(margen_x + 1.4*inch, pie_y - 0.6 * inch, " maryspetbarinas@gmail.com")
    c.drawString(margen_x+0.4*inch, pie_y - 0.8 * inch, "Av. El progreso, Jardines Alto Barinas. Conj. Apamates, Locales 8-A1 y B-2.")


    # Derecha
    c.drawString(centro + margen_x + 1 * inch,  pie_y - 0.4 *inch, "04143573522 / 04126920264 / 04127649580")
    c.drawString(centro + margen_x + 1.4*inch, pie_y - 0.6 * inch, " maryspetbarinas@gmail.com")
    c.drawString(centro + margen_x + 0.4 * inch, pie_y - 0.8 * inch, "Av. El progreso, Jardines Alto Barinas. Conj. Apamates, Locales 8-A1 y B-2.")

    text = c.beginText()
    text.setTextOrigin(x, y) 
    text.setFont("Helvetica", 12)

    estilos = getSampleStyleSheet()
    estilo = estilos["Normal"]

    # Crear el párrafo
    parrafo = Paragraph(rp, estilo)

    # Definir el área donde se dibujará el texto
    frame = Frame(x1=0.5*inch, y1=1.4*inch, width=4.5*inch, height=4.8*inch, showBoundary=0)

    # Dibujar el párrafo en el canvas
    frame.addFromList([parrafo], c)
    
    
    parrafo2 = Paragraph(ind, estilo)

    # Definir el área donde se dibujará el texto
    frame = Frame(x1=0.5*inch+centro, y1=1.4*inch, width=4.5*inch, height=4.8*inch, showBoundary=0)

    # Dibujar el párrafo en el canvas
    frame.addFromList([parrafo2], c)


    # Guardar el PDF
    c.save()
    print("✅ PDF generado: historia_clinica_con_texto_al_lado_de_la_imagen.pdf")


# === Datos de ejemplo ===
datos = {
    'nombre': 'Reinaldo X',
    'ci': '12.345.678',
    'cmvb': 'Unellez',
    'mpps': 'MPPS-12345',
    'paciente': 'Kimba',
    'rp': 'Amoxicilina + Ácido Clavulánico 250 mg \n'
'Administrar 1 tableta cada 12 horas por 7 días.\n'
'Meloxicam 1.5 mg/ml\n'
'Administrar 0.1 ml por cada 5 kg de peso, una vez al día por 5 días.\n'
'Omeprazol 10 mg Administrar 1 cápsula en ayunas cada 24 horas por 5 días.',

   'ind': 'Mantener al paciente en reposo relativo.\n'
'Evitar exposición al sol y al calor excesivo.\n'
'Dieta blanda durante el tratamiento.\n'
'Reevaluar en consulta dentro de 7 días.'

}

# Generar el PDF
generar_pdf(datos)
print(inch)

'''
parrafo = Paragraph(texto_largo, estilos["Normal"])
contenido.append(parrafo)
contenido.append(Spacer(1, 12))  # Espacio entre párrafos
'''
