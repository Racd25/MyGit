from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.button import Button
from datetime import datetime,timedelta
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from pymongo import MongoClient
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout as BoxLayoutBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.checkbox import CheckBox
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from kivymd.uix.pickers import MDDatePicker
from kivymd.app import MDApp
import sys
import subprocess
from datetime import datetime, timedelta, time

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """Añade selección a RecycleBoxLayout"""
    touch_deselect_last = BooleanProperty(True)

# Cargar el archivo .kv
def conectar_mongo():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Inrema']
        return db['operadores']  # Colección 'operadores'
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None




class OperadoresPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Seleccionar Operadores"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- BARRA DE BÚSQUEDA ---
        self.buscar_input = TextInput(hint_text='Buscar por nombre', size_hint_y=None, height=40)
        self.buscar_input.bind(text=self.filtrar_operadores)
        layout.add_widget(self.buscar_input)

        # --- ENCABEZADOS (sin columna "Stock") ---
        header = BoxLayout(size_hint_y=None, height=40)
        header.add_widget(Label(text="Seleccionar", size_hint_x=0.25, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="Nombre", size_hint_x=0.45, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="%", size_hint_x=0.15, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="Tasa", size_hint_x=0.15, bold=True, color=(1,1,1,1)))
        layout.add_widget(header)

        # --- SCROLLVIEW + GRID ---
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        # --- BOTONES ---
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.btn_aplicar = Button(text="Aplicar Selección (0)")  # ← Dinámico
        self.btn_aplicar.bind(on_release=self.on_aplicar)
        btn_cancelar = Button(text="Cancelar")
        btn_cancelar.bind(on_release=self.dismiss)
        btn_layout.add_widget(self.btn_aplicar)
        btn_layout.add_widget(btn_cancelar)
        layout.add_widget(btn_layout)

        self.content = layout
        self.seleccionados = set()
        self.checkbox_map = {}
        self.cargar_operadores()

    def cargar_operadores(self):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['operadores']
            self.todos_operadores = list(collection.find({}))
            client.close()
            self.filtrar_operadores()
            print(f"✅ Cargados {len(self.todos_operadores)} operadores")
        except Exception as e:
            print(f"❌ Error al cargar operadores: {e}")
            self.todos_operadores = []
            self.grid.add_widget(Label(text="Error al cargar operadores", color=(1,0,0,1)))

    def filtrar_operadores(self, *args):
        text = self.buscar_input.text.lower().strip()
        self.grid.clear_widgets()
        self.checkbox_map = {}

        # --- Ordenar: seleccionados primero ---
        def prioridad(operador):
            nombre = operador.get('nombre', '')
            return (0 if nombre in self.seleccionados else 1, nombre.lower())

        operadores_ordenados = sorted(self.todos_operadores, key=prioridad)

        for operador in operadores_ordenados:
            nombre = operador.get('nombre', '')
            if text and text not in nombre.lower():
                continue

            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            # Checkbox
            cb = CheckBox(size_hint_x=0.25)
            cb.bind(active=lambda checkbox, value, n=nombre: self.toggle_seleccion(n, value))
            if nombre in self.seleccionados:
                cb.active = True
            self.checkbox_map[nombre] = cb

            # Datos
            lbl_nombre = Label(text=nombre, size_hint_x=0.45)
            lbl_porcentaje = Label(text=f"{operador.get('porcentaje', 0)} %", size_hint_x=0.15)
            lbl_tasa = Label(text=f"{operador.get('tasa', 0.0):.2f}", size_hint_x=0.15)

            # Fondo amarillo si porcentaje < 10%
            if operador.get('porcentaje', 0) < 10:
                with row.canvas.before:
                    Color(1, 1, 0, 0.3)
                    rect = Rectangle(size=row.size, pos=row.pos)
                    row.bind(size=lambda r, val, rect=rect: setattr(rect, 'size', val),
                             pos=lambda r, val, rect=rect: setattr(rect, 'pos', val))

            row.add_widget(cb)
            row.add_widget(lbl_nombre)
            row.add_widget(lbl_porcentaje)
            row.add_widget(lbl_tasa)
            self.grid.add_widget(row)

        # Actualizar texto del botón
        self.actualizar_boton_aplicar()

    def toggle_seleccion(self, nombre, activo):
        if activo:
            self.seleccionados.add(nombre)
        else:
            self.seleccionados.discard(nombre)
        self.actualizar_boton_aplicar()

    def actualizar_boton_aplicar(self):
        count = len(self.seleccionados)
        self.btn_aplicar.text = f"Aplicar Selección ({count})"

    def on_aplicar(self, instance):
        seleccionados = list(self.seleccionados)
        if self.callback:
            self.callback(seleccionados)
        self.dismiss()




Builder.load_file('operadores/operadores.kv')  
def conectar_mongo_operadores():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Inrema']
        return db['operadores']
    except Exception as e:
        print(f"Error al conectar a operadores: {e}")
        return None
    
class SelectableOperadorLabel(RecycleDataViewBehavior, BoxLayout):
    """Una fila en la lista de operadores que puede ser seleccionada."""
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los atributos de la vista cuando cambia el dato."""
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_nombre'].text = data.get('nombre', 'N/A')
        self.ids['_porcentaje'].text = str(data.get('porcentaje', '0')) + ' %'
        self.ids['_tasa'].text = str(data.get('tasa', '0.0'))

        # Llama al método base
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Permite la selección al hacer clic."""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Actualiza el estado de selección."""
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False

class SelectablePagosLabel(RecycleDataViewBehavior, BoxLayout):
    """Una fila en la lista de pagos que puede ser seleccionada."""
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los atributos de la vista cuando cambia el dato."""
        self.index = index
        self.ids['_id_ficha'].text = str(data.get('numero_ficha', 'N/A'))
        self.ids['_operador'].text = data.get('operador', 'N/A')
        self.ids['_descripcion'].text = data.get('descripcion', 'N/A')
        self.ids['_cantidad'].text = str(data.get('cantidad', '0'))
        self.ids['_precio'].text = f"{data.get('precio', 0):.2f}"
        self.ids['_total'].text = f"{data.get('total', 0):.2f}"
        self.ids['_fecha'].text = data.get('fecha_registro_str', 'N/A')
        self.ids['_neto'].text = f"{data.get('neto_a_pagar', 0):.2f}"  # ← Añadido

        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Permite la selección al hacer clic."""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Actualiza el estado de selección."""
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False


class VistaOperador(Screen):

    def on_kv_post(self, base_widget):
        """Se llama después de que el .kv haya sido aplicado"""
        print("✅ VistaOperador: .kv aplicado, inicializando...")
        try:
            self.rv = self.ids.rv_operador
            if self.rv is None:
                print("❌ Error: rv_operador es None")
            else:
                print("✅ rv_operador encontrado, cargando operadores...")
                self.cargar_operadores()
        except Exception as e:
            print(f"❌ Error en on_kv_post: {e}")


    def cargar_operadores(self, *args):
        collection = conectar_mongo()
        try:
            operadores = list(collection.find())
            data = []
            for op in operadores:
                # Asegurar que 'trabajos' exista
                if 'trabajos' not in op:
                    op['trabajos'] = {}
                data.append({
                    'nombre': op['nombre'],
                    'porcentaje': op['porcentaje'],
                    'tasa': op['tasa'],
                    'seleccionado': False,
                    '_id': op['_id'],
                    'trabajos': op['trabajos']  # ← Incluirlo explícitamente
                })
            self.rv.data = data
        except Exception as e:
            print(f"Error al cargar operadores: {e}")

    def nuevo_operador(self):
        """Abre el popup para agregar un nuevo operador"""
        popup = NuevoOperadorPopup(callback_guardado=self.agregar_a_tabla)
        popup.open()

    def agregar_a_tabla(self, data):
        """Agrega un nuevo operador a la tabla"""
        self.rv.data.append({
            'nombre': data['nombre'],
            'porcentaje': data['porcentaje'],
            'tasa': data['tasa'],
            'seleccionado': False,
            '_id': data['_id']
        })
        self.rv.refresh_from_data()
        # ✅ Eliminado contador

    def editar_operador(self):
        """Abre el popup para editar el operador seleccionado"""
        indice = self.rv.dato_seleccionado()
        if indice < 0:
            print("Seleccione un operador")
            return

        operador = self.rv.data[indice]
        popup = NuevoOperadorPopup(operador_data=operador, callback_guardado=self.actualizar_tabla)
        popup.open()

    def actualizar_tabla(self, data):
        """Actualiza la fila en la tabla"""
        for i, op in enumerate(self.rv.data):
            if op['_id'] == data['_id']:
                self.rv.data[i].update({
                    'nombre': data['nombre'],
                    'porcentaje': data['porcentaje'],
                    'tasa': data['tasa']
                })
                break
        self.rv.refresh_from_data()

    def eliminar_operador(self):
        """Elimina el operador seleccionado de MongoDB y la tabla"""
        indice = self.rv.dato_seleccionado()
        if indice < 0:
            print("Seleccione un operador")
            return

        operador = self.rv.data[indice]
        collection = conectar_mongo()
        if collection is not None:
            collection.delete_one({'_id': operador['_id']})
            self.rv.data.pop(indice)
            self.rv.refresh_from_data()
            # ✅ Eliminado contador


    def añadir_trabajos(self):
        """Abre una vista para gestionar los trabajos del operador seleccionado"""
        indice = self.rv.dato_seleccionado()
        if indice < 0:
            print("❌ Seleccione un operador primero.")
            return

        operador_tabla = self.rv.data[indice]
        
        # ✅ RECARGAR EL OPERADOR DIRECTAMENTE DE LA BASE DE DATOS
        collection = conectar_mongo()
        if collection is None:
            print("❌ No se pudo conectar a la base de datos.")
            return

        operador_db = collection.find_one({'_id': operador_tabla['_id']})
        if not operador_db:
            print("❌ Operador no encontrado en la base de datos.")
            return

        # Asegurar que tenga el campo 'trabajos'
        if 'trabajos' not in operador_db:
            operador_db['trabajos'] = {}

        # Abrir popup con datos frescos de la BD
        popup = TrabajosOperadorPopup(
            operador=operador_db,
            callback_actualizar=self.actualizar_operador_en_tabla
        )
        popup.open()

    def actualizar_operador_en_tabla(self, operador_actualizado):
        """Actualiza el operador en la tabla después de modificar sus trabajos"""
        for i, op in enumerate(self.rv.data):
            if op['_id'] == operador_actualizado['_id']:
                self.rv.data[i] = operador_actualizado
                break
        self.rv.refresh_from_data()
        print(f"✅ Operador '{operador_actualizado['nombre']}' actualizado en tabla.")

class VistaPagos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operador_seleccionado = None
        self.formateando_fecha = False  # ← mismo nombre que en VistaTrabajos
        self.filtros_programados = False  # ← mismo nombre
        Clock.schedule_once(self.cargar_datos_iniciales, 0.1)

    def cargar_datos_iniciales(self, dt):
        self.ids.rv_pagos.data = []
        
        hoy = datetime.now().date()
        una_semana_atras = hoy - timedelta(days=7)
        
        self.fecha_desde = una_semana_atras
        self.fecha_hasta = hoy
        hoy2 = hoy.strftime("%d/%m/%Y")
        self.ids.lbl_fecha_actual.text = f"Fecha de Hoy: {hoy2}"

        # Mostrar fechas en los botones
        self.ids.btn_fecha_desde.text = una_semana_atras.strftime("%d/%m/%Y")
        self.ids.btn_fecha_hasta.text = hoy.strftime("%d/%m/%Y")
    

    def on_fecha_input(self, widget, tipo):
        """Maneja la máscara de fecha con salto automático."""
        if self.formateando_fecha:
            return

        digitos = ''.join(filter(str.isdigit, widget.text))[:8]
        mascara = list("__/__/____")
        posiciones = [0, 1, 3, 4, 6, 7, 8, 9]

        for i, d in enumerate(digitos):
            if i < len(posiciones):
                mascara[posiciones[i]] = d

        nuevo_texto = ''.join(mascara)

        if widget.text != nuevo_texto:
            self.formateando_fecha = True
            widget.text = nuevo_texto

            n = len(digitos)
            if n == 2:
                cursor_pos = 3  # después de DD/
            elif n == 4:
                cursor_pos = 6  # después de DD/MM/
            else:
                cursor_pos = next((i for i, c in enumerate(nuevo_texto) if c == '_'), len(nuevo_texto))

            widget.cursor = (cursor_pos, 0)
            self.formateando_fecha = False

            if not self.filtros_programados:
                self.filtros_programados = True
                Clock.schedule_once(self.aplicar_filtros, 0.5)

    def parse_fecha(self, fecha_str):
        """Convierte '__/__/____' → datetime si tiene 8 dígitos."""
        digitos = ''.join(filter(str.isdigit, fecha_str))
        if len(digitos) != 8:
            return None
        try:
            return datetime.strptime(digitos, "%d%m%Y")
        except ValueError:
            return None

    # ——————————————————————————————
    # Filtros y carga de datos
    # ——————————————————————————————

    def aplicar_filtros(self, dt=None):
        # ❗ Solo cargar si hay operador seleccionado
        if self.operador_seleccionado is None:
            self.ids.rv_pagos.data = []
            if hasattr(self.ids, 'lbl_total_general'):
                self.ids.lbl_total_general.text = "$ 0.00"
            if hasattr(self.ids, 'lbl_neto_general'):
                self.ids.lbl_neto_general.text = "$ 0.00"
            return

        self.cargar_trabajos_terminados(
            operador_filtro=self.operador_seleccionado,
            fecha_desde=self.fecha_desde,
            fecha_hasta=self.fecha_hasta
    )
        
    def cargar_trabajos_terminados(self, operador_filtro=None, fecha_desde=None, fecha_hasta=None):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['registro_trabajos']
            
            query = {"terminado": True}
            
            if operador_filtro:
                query["operador"] = operador_filtro
            
            if fecha_desde or fecha_hasta:
                rango = {}
                if fecha_desde:
                    rango["$gte"] = fecha_desde.isoformat()
                if fecha_hasta:
                    # Combina la fecha con la hora final del día
                    fin_dia = datetime.combine(fecha_hasta, time(23, 59, 59, 999999))
                    rango["$lte"] = fin_dia.isoformat()
                if rango:
                    query["fecha_registro"] = rango

            trabajos = list(collection.find(query))
            data = []
            total_general = 0.0
            neto_general = 0.0

            for t in trabajos:
                # Obtener porcentaje del operador
                porcentaje = 0.0
                operador_nombre = t.get('operador', '')
                if operador_nombre:
                    operador_doc = db['operadores'].find_one({"nombre": operador_nombre})
                    if operador_doc and 'porcentaje' in operador_doc:
                        porcentaje = float(operador_doc['porcentaje']) / 100.0

                # Calcular neto a pagar
                total_trabajo = t.get('total', 0.0)
                neto_a_pagar = total_trabajo * porcentaje

                # Formatear fecha
                fecha_str = "N/A"
                fecha_reg = t.get('fecha_registro')
                if fecha_reg:
                    try:
                        if isinstance(fecha_reg, str):
                            if fecha_reg.endswith('Z'):
                                fecha_reg = fecha_reg[:-1] + '+00:00'
                            dt_obj = datetime.fromisoformat(fecha_reg)
                        elif isinstance(fecha_reg, datetime):
                            dt_obj = fecha_reg
                        else:
                            raise ValueError("Tipo de fecha no soportado")
                        fecha_str = dt_obj.strftime("%d/%m/%Y")
                    except Exception as e:
                        print(f"⚠️ Error al formatear fecha: {e}")
                        fecha_str = str(fecha_reg)[:10]

                data.append({
                    'numero_ficha': t.get('numero_ficha', 'N/A'),
                    'operador': t.get('operador', 'N/A'),
                    'descripcion': t.get('descripcion', 'N/A'),
                    'cantidad': t.get('cantidad', 0),
                    'precio': t.get('precio', 0.0),
                    'total': total_trabajo,
                    'fecha_registro_str': fecha_str,
                    'neto_a_pagar': neto_a_pagar,
                    'seleccionado': False,
                    '_id': t.get('_id')
                })

                total_general += total_trabajo
                neto_general += neto_a_pagar

            self.ids.rv_pagos.data = data
            client.close()

            # Actualizar totales
            if hasattr(self.ids, 'lbl_total_general'):
                self.ids.lbl_total_general.text = f"$ {total_general:,.2f}"
            if hasattr(self.ids, 'lbl_neto_general'):
                self.ids.lbl_neto_general.text = f"$ {neto_general:,.2f}"

        except Exception as e:
            print(f"❌ Error al cargar trabajos terminados: {e}")
            self.ids.rv_pagos.data = []
            if hasattr(self.ids, 'lbl_total_general'):
                self.ids.lbl_total_general.text = "$ 0.00"
            if hasattr(self.ids, 'lbl_neto_general'):
                self.ids.lbl_neto_general.text = "$ 0.00"

    def abrir_popup_operadores(self):
        popup = OperadorSimplePopup(callback=self.on_operador_seleccionado)
        popup.open()

    def on_operador_seleccionado(self, nombre_operador):
        self.operador_seleccionado = nombre_operador
        self.ids.btn_filtro_operador.text = f"Operador: {nombre_operador}"
        self.aplicar_filtros()

    # ——————————————————————————————
    # Selección y acciones
    # ——————————————————————————————

    def dato_seleccionado(self):
        for i, item in enumerate(self.ids.rv_pagos.data):
            if item.get('seleccionado', False):
                return i
        return -1


    def abrir_popup_operadores(self):
        """Abre popup para seleccionar UN operador."""
        popup = OperadorSimplePopup(callback=self.on_operador_seleccionado)
        popup.open()


    def on_operador_seleccionado(self, nombre_operador):
        """Recibe el nombre del operador seleccionado."""
        self.operador_seleccionado = nombre_operador
        self.ids.btn_filtro_operador.text = f"Operador: {nombre_operador}"
        self.aplicar_filtros()
        

    def generar_pago(self):
        """Genera un PDF con los trabajos seleccionados o todos los filtrados."""
        if not self.operador_seleccionado:
            print("❌ Seleccione un operador primero.")
            return

        # Obtener rango de fechas
        fecha_desde = self.fecha_desde
        fecha_hasta = self.fecha_hasta
        if not hasattr(self, 'fecha_desde') or not hasattr(self, 'fecha_hasta'):
            print("❌ Fechas no inicializadas.")
            return

        # Validar fechas
        if not fecha_desde or not fecha_hasta:
            print("❌ Especifique un rango de fechas válido.")
            return

        # Obtener datos de trabajos filtrados
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection_trabajos = db['registro_trabajos']
            collection_fichas = db['fichas']

            query = {
                "terminado": True,
                "operador": self.operador_seleccionado
            }
            if fecha_desde or fecha_hasta:
                rango = {}
                if fecha_desde:
                    rango["$gte"] = fecha_desde.isoformat()
                if fecha_hasta:
                    # Cambia esto: combina la fecha con la hora final del día
                    fin_dia = datetime.combine(fecha_hasta, time(23, 59, 59, 999999))
                    rango["$lte"] = fin_dia.isoformat()
                query["fecha_registro"] = rango

            trabajos = list(collection_trabajos.find(query))

            # Obtener porcentaje del operador
            operador_doc = db['operadores'].find_one({"nombre": self.operador_seleccionado})
            porcentaje_operador = float(operador_doc.get('porcentaje', 0)) / 100.0 if operador_doc else 0.0

            # Preparar datos para la tabla
            data = []
            total_neto = 0.0

            # Encabezado de la tabla
            encabezado = [
                "Ficha", "Descripción", "Cliente", "Precio", "Cantidad", "SubTotal", "Porc (%)", "Neto a Pagar"
            ]
            data.append(encabezado)

            for t in trabajos:
                numero_ficha = t.get('numero_ficha', 'N/A')
                descripcion = t.get('descripcion', 'N/A')
                precio = t.get('precio', 0.0)
                cantidad = t.get('cantidad', 0)
                subtotal = precio * cantidad
                neto_a_pagar = subtotal * porcentaje_operador
                total_neto += neto_a_pagar

                # Obtener cliente desde la ficha
                ficha_doc = collection_fichas.find_one({"numero_ficha": numero_ficha})
                cliente = ficha_doc.get('cliente', {}).get('nombre', 'N/A') if ficha_doc else 'N/A'

                fila = [
                    str(numero_ficha),
                    descripcion,
                    cliente,
                    f"{precio:.2f}",
                    str(cantidad),
                    f"{subtotal:.2f}",
                    f"{porcentaje_operador * 100:.0f}%",
                    f"{neto_a_pagar:.2f}"
                ]
                data.append(fila)

            client.close()

            # Generar PDF
            self.generar_pdf_pagos(
                operador=self.operador_seleccionado,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                datos=data,
                total_neto=total_neto
            )

        except Exception as e:
            print(f"❌ Error al generar PDF: {e}")
            import traceback
            traceback.print_exc()
      

    def abrir_calendario_desde(self):
        hoy = datetime.now().date()
        una_semana_atras = hoy - timedelta(days=7)
        MDDatePicker(
            primary_color="teal",
            selector_color="lightgreen",
            text_toolbar_color="white",
            text_color="black",
            text_current_color="teal",
            min_date=datetime(2020, 1, 1).date(),
            max_date=self.fecha_hasta or hoy,
            year=una_semana_atras.year,
            month=una_semana_atras.month,
            day=una_semana_atras.day,
        ).bind(on_save=self.on_fecha_desde_seleccionada)
        picker = MDDatePicker()
        picker.bind(on_save=self.on_fecha_desde_seleccionada)
        picker.open()

    def abrir_calendario_hasta(self):
        hoy = datetime.now().date()
        MDDatePicker(
            primary_color="teal",
            selector_color="lightgreen",
            text_toolbar_color="white",
            text_color="black",
            text_current_color="teal",
            min_date=self.fecha_desde or (hoy - timedelta(days=365)),
            max_date=hoy + timedelta(days=1),
            year=hoy.year,
            month=hoy.month,
            day=hoy.day,
        ).bind(on_save=self.on_fecha_hasta_seleccionada)
        picker = MDDatePicker()
        picker.bind(on_save=self.on_fecha_hasta_seleccionada)
        picker.open()

    def on_fecha_desde_seleccionada(self, instance, value, date_range):
        self.fecha_desde = value
        self.ids.btn_fecha_desde.text = value.strftime("%d/%m/%Y")  # ← Actualizar texto del botón
        self.aplicar_filtros()

    def on_fecha_hasta_seleccionada(self, instance, value, date_range):
        self.fecha_hasta = value
        self.ids.btn_fecha_hasta.text = value.strftime("%d/%m/%Y")  # ← Actualizar texto del botón
        self.aplicar_filtros()
        
        
class OperadorSimplePopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Seleccionar Operador"
        self.size_hint = (0.3, 0.7)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Título
        layout.add_widget(Label(text="Haga clic en un operador:", size_hint_y=None, height=30))

        # Lista scrollable de operadores
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        grid.bind(minimum_height=grid.setter('height'))

        # Cargar operadores desde MongoDB
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['operadores']
            operadores = collection.find({}, {"nombre": 1}).sort("nombre", 1)
            for op in operadores:
                nombre = op.get('nombre', 'Sin nombre')
                btn = Button(
                    text=nombre,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.95, 0.95, 0.95, 1),
                    color=(1, 1, 1, 1)
                )
                btn.bind(on_release=lambda btn, n=nombre: self.seleccionar_operador(n))
                grid.add_widget(btn)
            client.close()
        except Exception as e:
            print(f"❌ Error al cargar operadores en popup: {e}")
            grid.add_widget(Label(text="Error al cargar operadores", color=(1, 0, 0, 1)))

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # Botón Cancelar
        btn_cancelar = Button(text="Cancelar", size_hint_y=None, height=40)
        btn_cancelar.bind(on_release=self.dismiss)
        layout.add_widget(btn_cancelar)

        self.content = layout

    def seleccionar_operador(self, nombre):
        if self.callback:
            self.callback(nombre)
        self.dismiss()
    
    
    
from kivy.clock import Clock
from datetime import datetime

class VistaTrabajos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operadores_seleccionados = ["Todos"]
        self.tipo_ficha_seleccionado = "Ambas"
        self.formateando_fecha = False
        self.filtros_programados = False
        self.estado_terminado_seleccionado = "Ambos"


    def on_kv_post(self, base_widget):
        print("✅ VistaTrabajos: .kv aplicado, inicializando...")
        try:
            # Inicializar botones con texto neutro

            self.ids.btn_filtro_operador.text = "Operadores: Todos"
            self.ids.spinner_tipo_ficha.text = "Ambas"
            self.ids.spinner_estado_terminado.text = "Ambos"

            # Establecer estado lógico
            self.operadores_seleccionados = ["Todos"]
            self.tipo_ficha_seleccionado = "Ambas"
            self.estado_terminado_seleccionado = "Ambos"

            # Cargar todos los datos
            self.cargar_trabajos()
        except Exception as e:
            print(f"❌ Error en on_kv_post: {e}")

    # ——————————————————————————————
    # Gestión de fechas (igual que en VistaRegistro)
    # ——————————————————————————————

    def solo_digitos(self, texto, from_undo=False):
        return ''.join(filter(str.isdigit, texto))

    def on_fecha_input(self, widget, tipo):
        if self.formateando_fecha:
            return

        digitos = ''.join(filter(str.isdigit, widget.text))[:8]
        mascara = list("__/__/____")
        posiciones = [0, 1, 3, 4, 6, 7, 8, 9]

        for i, d in enumerate(digitos):
            if i < len(posiciones):
                mascara[posiciones[i]] = d

        nuevo_texto = ''.join(mascara)

        if widget.text != nuevo_texto:
            self.formateando_fecha = True
            widget.text = nuevo_texto

            n = len(digitos)
            if n == 2:
                cursor_pos = 3
            elif n == 4:
                cursor_pos = 6
            else:
                cursor_pos = next((i for i, c in enumerate(nuevo_texto) if c == '_'), len(nuevo_texto))

            widget.cursor = (cursor_pos, 0)
            self.formateando_fecha = False

            if not self.filtros_programados:
                self.filtros_programados = True
                Clock.schedule_once(self.aplicar_filtros, 0.5)

    def parse_fecha(self, fecha_str):
        # Aceptar tanto "dd/mm/yyyy" como "ddmmyyyy"
        clean = fecha_str.replace("/", "").replace("_", "").strip()
        if len(clean) != 8 or not clean.isdigit():
            return None
        try:
            return datetime.strptime(clean, "%d%m%Y")
        except ValueError:
            return None

    # ——————————————————————————————
    # Filtros
    # ——————————————————————————————

    def on_tipo_ficha_change(self, tipo):
        self.tipo_ficha_seleccionado = tipo
        self.aplicar_filtros()

    def abrir_popup_operadores(self):
        popup = OperadoresPopup(callback=self.on_operadores_seleccionados)
        popup.open()

    def on_operadores_seleccionados(self, nombres_seleccionados):
        if not nombres_seleccionados:
            self.operadores_seleccionados = ["Todos"]
            texto_boton = "Operadores: Todos"
        else:
            self.operadores_seleccionados = nombres_seleccionados
            total = len(nombres_seleccionados)
            if total == 1:
                texto_boton = f"Operadores: {nombres_seleccionados[0]}"
            elif total <= 3:
                texto_boton = "Operadores: " + ", ".join(nombres_seleccionados)
            else:
                primeros = ", ".join(nombres_seleccionados[:2])
                texto_boton = f"Operadores: {primeros} y {total - 2} más"

        if hasattr(self.ids, 'btn_filtro_operador'):
            self.ids.btn_filtro_operador.text = texto_boton

        self.aplicar_filtros()


    def aplicar_filtros(self, dt=None):
        if hasattr(self, 'filtros_programados'):
            self.filtros_programados = False

        # Extraer texto de los botones
        texto_desde = self.ids.btn_fecha_desde.text
        texto_hasta = self.ids.btn_fecha_hasta.text

        # Detectar si hay valor real de fecha
        fecha_desde_str = None
        fecha_hasta_str = None

        if texto_desde and not texto_desde.startswith("Desde"):
            fecha_desde_str = texto_desde.strip()
        if texto_hasta and not texto_hasta.startswith("Hasta"):
            fecha_hasta_str = texto_hasta.strip()

        # Parsear solo si hay string válido
        fecha_desde = self.parse_fecha(fecha_desde_str) if fecha_desde_str else None
        fecha_hasta = self.parse_fecha(fecha_hasta_str) if fecha_hasta_str else None

        # Validar rango
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            print("❌ Rango de fechas inválido.")
            return

        # Aplicar filtros (si no hay fechas, se omiten)
        self.cargar_trabajos_filtrados(
            operadores_filtro=self.operadores_seleccionados,
            tipo_ficha=self.tipo_ficha_seleccionado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )

    def cargar_trabajos_filtrados(self, operadores_filtro=None, tipo_ficha="Ambas", fecha_desde=None, fecha_hasta=None):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['registro_trabajos']

            query = {}

            # Filtro por operador
            if operadores_filtro and "Todos" not in operadores_filtro:
                query["operador"] = {"$in": operadores_filtro}

            # Filtro por tipo de ficha
            if tipo_ficha != "Ambas":
                query["tipo_ficha"] = tipo_ficha.lower()

            # Filtro por estado de terminación
            estado = self.estado_terminado_seleccionado
            if estado == "Terminados":
                query["terminado"] = True
            elif estado == "No Terminados":
                query["terminado"] = False
            # Si es "Ambos", no se aplica filtro

            # Filtro por fecha
            if fecha_desde or fecha_hasta:
                rango = {}
                if fecha_desde:
                    rango["$gte"] = fecha_desde.isoformat()
                if fecha_hasta:
                    fin_dia = fecha_hasta.replace(hour=23, minute=59, second=59, microsecond=999999)
                    rango["$lte"] = fin_dia.isoformat()
                if rango:
                    query["fecha_registro"] = rango

            trabajos = list(collection.find(query))
            data = []
            total_general = 0.0

            for t in trabajos:
                total_valor = t.get('total', 0.0)
                total_general += total_valor
                data.append({
                    'numero_ficha': t.get('numero_ficha', 'N/A'),
                    'operador': t.get('operador', 'N/A'),
                    'descripcion': t.get('descripcion', 'N/A'),
                    'cantidad': t.get('cantidad', 0),
                    'precio': t.get('precio', 0.0),
                    'total': total_valor,
                    'terminado': t.get('terminado', False),
                    'seleccionado': False,
                    '_id': t.get('_id')
                })

            self.ids.rv_trabajos.data = data

            # Actualizar total
            if hasattr(self.ids, 'lbl_total_general'):
                self.ids.lbl_total_general.text = f"$ {total_general:,.2f}"

            client.close()

        except Exception as e:
            print(f"❌ Error al cargar trabajos filtrados: {e}")
            self.ids.rv_trabajos.data = []
            if hasattr(self.ids, 'lbl_total_general'):
                self.ids.lbl_total_general.text = "$ 0.00"

    # ——————————————————————————————
    # Métodos existentes (sin cambios)
    # ——————————————————————————————


    def cargar_trabajos(self, *args):
        # Valores por defecto: sin filtros
        self.operadores_seleccionados = ["Todos"]
        self.tipo_ficha_seleccionado = "Ambas"
        self.estado_terminado_seleccionado = "Ambos"
        
        # Aplicar (esto ya no intenta acceder a widgets fuera de lugar)
        self.aplicar_filtros()
        
    def dato_seleccionado(self):
        for i, item in enumerate(self.ids.rv_trabajos.data):
            if item.get('seleccionado', False):
                return i
        return -1

    def actualizar(self):
        """
        Recarga los trabajos desde la base de datos aplicando los filtros actuales.
        Útil para refrescar la vista tras cambios externos.
        """
        print("🔄 Actualizando vista de trabajos...")
        fecha_desde = self.parse_fecha(self.ids.fecha_desde.text)
        fecha_hasta = self.parse_fecha(self.ids.fecha_hasta.text)

        # Validar rango de fechas
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            print("❌ Rango de fechas inválido. No se actualizó.")
            return

        # Reaplicar los mismos filtros actuales
        self.cargar_trabajos_filtrados(
            operadores_filtro=self.operadores_seleccionados,
            tipo_ficha=self.tipo_ficha_seleccionado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
            
    def on_estado_terminado_change(self, estado):
        """Actualiza el filtro por estado de terminación y aplica."""
        self.estado_terminado_seleccionado = estado
        self.aplicar_filtros()            



    def abrir_calendario_desde(self):
        hoy = datetime.now().date()
        picker = MDDatePicker()
        picker.bind(on_save=self.on_fecha_desde_seleccionada)
        picker.open()

    def abrir_calendario_hasta(self):
        hoy = datetime.now().date()
        picker = MDDatePicker()
        picker.bind(on_save=self.on_fecha_hasta_seleccionada)
        picker.open()

    def on_fecha_desde_seleccionada(self, instance, value, date_range):
        self.ids.btn_fecha_desde.text = value.strftime("%d/%m/%Y")
        self.aplicar_filtros()

    def on_fecha_hasta_seleccionada(self, instance, value, date_range):
        self.ids.btn_fecha_hasta.text = value.strftime("%d/%m/%Y")
        self.aplicar_filtros()


            
class SelectableTrabajosLabel(RecycleDataViewBehavior, BoxLayout):
    """Una fila en la lista de trabajos que puede ser seleccionada."""
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    terminado = BooleanProperty(False) 

    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los atributos de la vista cuando cambia el dato."""
        self.index = index
        self.ids['_id_ficha'].text = str(data.get('numero_ficha', 'N/A'))
        self.ids['_operador'].text = data.get('operador', 'N/A')
        self.ids['_descripcion'].text = data.get('descripcion', 'N/A')
        self.ids['_cantidad'].text = str(data.get('cantidad', '0'))
        self.ids['_precio'].text = f"{data.get('precio', 0):.2f}"
        self.ids['_total'].text = f"{data.get('total', 0):.2f}"
        estado = data.get('terminado', False)
        self.ids['_terminado'].text = "Terminado" if data.get('terminado', False) else "Sin Terminar"
        self.terminado = estado 

        # Llama al método base
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Permite la selección al hacer clic."""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Actualiza el estado de selección."""
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False


class TrabajosOperadorPopup(Popup):
    def __init__(self, operador, callback_actualizar, **kwargs):
        super().__init__(**kwargs)
        self.operador = operador.copy()
        self.callback_actualizar = callback_actualizar
        self.title = f"Trabajos de {operador.get('nombre', 'Operador')}"
        self.size_hint = (0.9, 0.8)
        self.auto_dismiss = False

        # --- Guardar referencias a los TextInput por clave ---
        self.text_inputs = {}  # {clave: TextInput}

        # --- Layout principal ---
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- Encabezado ---
        header = BoxLayout(size_hint_y=None, height=40, spacing=5)
        header.add_widget(Label(text="ID", size_hint_x=0.1, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="Trabajo", size_hint_x=0.7, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="Acción", size_hint_x=0.2, bold=True, color=(1,1,1,1)))
        layout.add_widget(header)

        # --- ScrollView + Grid ---
        scroll = ScrollView()
        self.grid_trabajos = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.grid_trabajos.bind(minimum_height=self.grid_trabajos.setter('height'))
        scroll.add_widget(self.grid_trabajos)
        layout.add_widget(scroll)

        # --- Botón para agregar trabajo ---
        btn_agregar = Button(text=" Agregar Trabajo", size_hint_y=None, height=50)
        btn_agregar.bind(on_release=self.agregar_trabajo)
        layout.add_widget(btn_agregar)

        # --- Botones Cancelar / Guardar ---
        footer = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancelar = Button(text="Cancelar", background_color=(0.7, 0.2, 0.2, 1))
        btn_cancelar.bind(on_release=self.dismiss)
        btn_guardar = Button(text="Guardar Cambios", background_color=(0.2, 0.7, 0.2, 1))
        btn_guardar.bind(on_release=self.guardar_cambios)

        footer.add_widget(btn_cancelar)
        footer.add_widget(btn_guardar)
        layout.add_widget(footer)

        self.content = layout
        self.cargar_trabajos()

    def cargar_trabajos(self):
        """Carga los trabajos y crea TextInput con referencias"""
        self.grid_trabajos.clear_widgets()
        self.text_inputs.clear()  # Reiniciar referencias
        trabajos = self.operador.get('trabajos', {})
        items = sorted(trabajos.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)

        for clave, trabajo in items:
            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            lbl_id = Label(text=str(clave), size_hint_x=0.1, halign='center', valign='middle')
            lbl_id.bind(size=lbl_id.setter('text_size'))

            txt_trabajo = TextInput(
                text=str(trabajo),
                size_hint_x=0.7,
                size_hint_y=None,
                height=40,
                multiline=False
            )

            # Guardar referencia
            self.text_inputs[clave] = txt_trabajo

            btn_eliminar = Button(text="-", size_hint_x=0.2, size_hint_y=None, height=40)
            btn_eliminar.bind(on_release=lambda btn, k=clave: self.eliminar_trabajo(k))

            row.add_widget(lbl_id)
            row.add_widget(txt_trabajo)
            row.add_widget(btn_eliminar)

            self.grid_trabajos.add_widget(row)

    def agregar_trabajo(self, *args):
        trabajos = self.operador.get('trabajos', {})
        claves_numericas = [int(k) for k in trabajos.keys() if k.isdigit()]
        nueva_clave = str(max(claves_numericas) + 1 if claves_numericas else 1)
        
        # Agregar el nuevo trabajo vacío al modelo
        trabajos[nueva_clave] = ""
        self.operador['trabajos'][nueva_clave] = ""

        # ✅ Crear solo la nueva fila visual (sin recargar todo)
        row = BoxLayout(size_hint_y=None, height=40, spacing=5)

        lbl_id = Label(text=nueva_clave, size_hint_x=0.1, halign='center', valign='middle')
        lbl_id.bind(size=lbl_id.setter('text_size'))

        txt_trabajo = TextInput(
            text="",  # vacío
            size_hint_x=0.7,
            size_hint_y=None,
            height=40,
            multiline=False
        )

        # Guardar referencia del nuevo TextInput
        self.text_inputs[nueva_clave] = txt_trabajo

        btn_eliminar = Button(text="-", size_hint_x=0.2, size_hint_y=None, height=40)
        btn_eliminar.bind(on_release=lambda btn, k=nueva_clave: self.eliminar_trabajo(k))

        row.add_widget(lbl_id)
        row.add_widget(txt_trabajo)
        row.add_widget(btn_eliminar)

        # ✅ Añadir solo esta fila al grid, sin borrar las demás
        self.grid_trabajos.add_widget(row)

        print(f"✅ Trabajo agregado con ID: {nueva_clave}")

    def eliminar_trabajo(self, clave):
        # Eliminar del modelo
        if clave in self.operador['trabajos']:
            del self.operador['trabajos'][clave]

        # Eliminar del diccionario de referencias
        if clave in self.text_inputs:
            del self.text_inputs[clave]

        # ✅ Eliminar visualmente la fila del grid
        # Recorrer los hijos de grid_trabajos y encontrar la fila con ese ID
        for child in self.grid_trabajos.children[:]:  # copia para evitar modificar durante iteración
            if isinstance(child, BoxLayout):
                # Asumimos que el primer widget es el Label con el ID
                if len(child.children) >= 3:
                    id_label = child.children[-1]  # porque Kivy añade en orden inverso
                    if isinstance(id_label, Label) and id_label.text == clave:
                        self.grid_trabajos.remove_widget(child)
                        break

        print(f"✅ Trabajo ID {clave} eliminado.")

    def guardar_cambios(self, *args):
        """✅ Guarda el texto ACTUAL de todos los TextInput"""
        try:
            # Actualizar los trabajos con el texto actual de los inputs
            for clave, txt_widget in self.text_inputs.items():
                texto_actual = txt_widget.text.strip()
                if texto_actual:
                    self.operador['trabajos'][clave] = texto_actual
                else:
                    # Opcional: eliminar si está vacío
                    if clave in self.operador['trabajos']:
                        del self.operador['trabajos'][clave]

            # Guardar en MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['operadores']
            
            result = collection.update_one(
                {'_id': self.operador['_id']},
                {'$set': {'trabajos': self.operador['trabajos']}}
            )
            client.close()

            if result.modified_count > 0:
                print(f"✅ Trabajos de '{self.operador['nombre']}' guardados en BD.")
                if self.callback_actualizar:
                    self.callback_actualizar(self.operador)
                self.dismiss()
            else:
                print("⚠️ No se detectaron cambios.")
                
        except Exception as e:
            print(f"❌ Error al guardar trabajos: {e}")
            # Nota: este popup no tiene 'mensaje_estado', así que omitimos esa línea


class NuevoOperadorPopup(Popup):
    def __init__(self, operador_data=None, callback_guardado=None, **kwargs):
        super().__init__(**kwargs)
        self.callback_guardado = callback_guardado
        self.operador_data = operador_data or {}

        self.title = "Agregar Operador" if not operador_data else "Editar Operador"
        self.size_hint = (0.6, 0.6)
        self.auto_dismiss = False

        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Campos
        self.nombre_input = TextInput(text=self.operador_data.get('nombre', ''), multiline=False)
        self.porcentaje_input = TextInput(text=str(self.operador_data.get('porcentaje', '')), multiline=False, input_filter='float')
        self.tasa_input = TextInput(text=str(self.operador_data.get('tasa', '')), multiline=False, input_filter='float')

        layout.add_widget(Label(text="Nombre:", size_hint_y=None, height=30))
        layout.add_widget(self.nombre_input)
        layout.add_widget(Label(text="Porcentaje %:", size_hint_y=None, height=30))
        layout.add_widget(self.porcentaje_input)
        layout.add_widget(Label(text="Tasa:", size_hint_y=None, height=30))
        layout.add_widget(self.tasa_input)

        # Mensaje de estado
        self.mensaje_estado = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=30)
        layout.add_widget(self.mensaje_estado)

        # Botones
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_guardar = Button(text="Guardar", on_release=self.guardar)
        btn_cancelar = Button(text="Cancelar", on_release=self.dismiss)
        btn_layout.add_widget(btn_guardar)
        btn_layout.add_widget(btn_cancelar)
        layout.add_widget(btn_layout)

        self.content = layout

    def guardar(self, *args):
        nombre = self.nombre_input.text.strip()
        porcentaje = self.porcentaje_input.text.strip()
        tasa = self.tasa_input.text.strip()

        if not nombre:
            self.mensaje_estado.text = "El nombre es obligatorio"
            return
        if not porcentaje or not tasa:
            self.mensaje_estado.text = "Porcentaje y Tasa son obligatorios"
            return

        try:
            porcentaje = float(porcentaje)
            tasa = float(tasa)
        except ValueError:
            self.mensaje_estado.text = "Porcentaje y Tasa deben ser números"
            return

        # Datos a guardar
        data = {
            'nombre': nombre,
            'porcentaje': porcentaje,
            'tasa': tasa
        }

        # Insertar o actualizar en MongoDB
        collection = conectar_mongo()

        # ✅ CORREGIDO: Usa 'is None' en lugar de 'not collection'
        if collection is None:
            self.mensaje_estado.text = "Error de conexión con la base de datos"
            return

        if self.operador_data.get('_id'):  # Editar
            collection.update_one({'_id': self.operador_data['_id']}, {'$set': data})
        else:  # Nuevo
            result = collection.insert_one(data)
            data['_id'] = result.inserted_id  # Guardamos el ID generado

        # Notificar al callback
        if self.callback_guardado:
            self.callback_guardado(data)

        self.dismiss()



class VistaMenuO(Screen):
    def ir_a(self, pantalla):
        # El parent de esta pantalla es el ScreenManager
        self.parent.current = pantalla
    def pagos(self):
        self.parent.current = 'pagos'
        
class CustomDropDown1(DropDown):
    def __init__(self, cambiar_callback, admin_window1, **kwargs):
        self._succ_cb = cambiar_callback
        self.admin_window = admin_window1  # ✅ Guardamos la referencia
        super(CustomDropDown1, self).__init__(**kwargs)

    def vista(self, vista):
        if callable(self._succ_cb):
            self._succ_cb(True, vista)

    def salir2(self):
        if self.admin_window and hasattr(self.admin_window, 'inventario'):
            self.admin_window.inventario()  # ✅ Llama al salir() de la instancia real
        else:
            print("Error: admin_window no disponible")
        self.dismiss() 
        
    def pacientes(self):
        if self.admin_window and hasattr(self.admin_window, 'pacientes'):
            self.admin_window.pacientes()  # ✅ Llama al salir() de la instancia real
        else:
            print("Error: admin_window no disponible")
        self.dismiss() 
        
    def a_operadores(self):
        if self.admin_window and hasattr(self.admin_window, 'operadores'):
            self.admin_window.operadores()  # ✅ Llama al salir() de la instancia real
        else:
            print("Error: admin_window no disponible")
        self.dismiss() 

    def actualizar_visibilidad_por_nivel(self, nivel):
        nivel = getattr(self.admin_window, 'usuario_nivel', None)
        
        if nivel == 2:
            self.ids.drop_inventario.disabled = True
        else:
            self.ids.drop_inventario.disabled = False
            

        
class AdminO(BoxLayout):  # ← No ScreenManager
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vista_actual = 'operadores'
        self.usuario_nivel = None
        self.dropdown = CustomDropDown1(cambiar_callback=self.cambiar_vista, admin_window1=self)
        
        self.ids.cambiar_vista.bind(on_release=self.dropdown.open)
        
        
    def actualizar_nivel_usuario(self, nivel):
        """Recibe el nivel del usuario desde MainWindow"""
        self.usuario_nivel = nivel
        if hasattr(self, 'dropdown'):
            self.dropdown.actualizar_visibilidad_por_nivel(nivel) 
            print("PASE EL NIVEL")

    def cambiar_vista(self):
        """Cambia entre vistas en el ScreenManager interno"""
        sm = self.ids.vista_manager2
        if sm.current == 'menu':
            sm.current = 'operadores'
        else:
            sm.current = 'operadores'
        print(str(sm.current))

    def salir2(self):
        """Cambia entre 'menu' y 'operadores'"""
        sm = self.ids.vista_manager2

        sm.current = 'menu'
        print(f"✅ Vista actual: {sm.current}")
    def salir3(self):
        print("xyz")
        
    def salirx(self):  
        self.parent.parent.current = 'signin'  
    def cambiar_vista(self, cambio=False, vista=None):
        if cambio:
            self.vista_actual = vista
            self.vista_manager.current = self.vista_actual
            self.dropdown.dismiss()
            
    def inventario(self):  
        # Asume que estás usando ScreenManager
        print("Me cague")
        self.parent.parent.current = 'inventario'  
    def pacientes(self):  
        # Asume que estás usando ScreenManager
        print("Me cague")
        self.parent.parent.current = 'admin'  


        
class AdminRV2(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

    def dato_seleccionado(self):
        for i, item in enumerate(self.data):
            if item.get('seleccionado'):
                return i
        return -1


class MiApp(MDApp):  
    def build(self):  
        return AdminO()  
  
if __name__ == "__main__":  
    MiApp().run()