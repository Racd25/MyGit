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
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.app import App

app = App.get_running_app()
nivel = getattr(app, 'usuario_nivel', 1) 




# Cargar el archivo .kv
Builder.load_file('inventario/inventariox.kv')
def conectar_mongo1():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['Inrema']
        return db['Repuestos']
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

def obtener_siguiente_codigo():
    """Devuelve el siguiente código autoincremental para Repuestos."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Inrema']
    counters = db['counters']

    resultado = counters.find_one_and_update(
        {"_id": "repuestos_codigo"},
        {"$inc": {"seq": 1}},
        upsert=False,  # ← Ya no necesitamos crearlo aquí
        return_document=True
    )
    client.close()
    
    if resultado is None:
        raise Exception("❌ El contador 'repuestos_codigo' no existe en 'counters'. Ejecuta el script de corrección.")
    
    return resultado['seq']

def previsualizar_proximo_codigo():
    """Devuelve el próximo código SIN incrementar el contador."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Inrema']
    counters = db['counters']
    counter_doc = counters.find_one({"_id": "repuestos_codigo"})
    if counter_doc:
        proximo = counter_doc['seq']
    else:
        repuestos = db['Repuestos']
        max_codigo = repuestos.aggregate([
            {"$group": {"_id": None, "max": {"$max": "$codigo"}}}
        ]).next().get("max", 0)
        proximo = max_codigo + 1
    client.close()
    return proximo


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """Añade comportamiento de selección y foco al RecycleBoxLayout."""
    touch_deselect_last = BooleanProperty(True)

class SelectableInventarioLabel(RecycleDataViewBehavior, BoxLayoutBase):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.data = data

        # Actualizar texto
        self.ids['_idrepuesto'].text = str(data['codigo'])
        self.ids['_repuesto'].text = data['nombre'].capitalize()
        self.ids['_grupo'].text = data.get('grupo', 'N/A')
        self.ids['_unidad'].text = data.get('unidad', 'N/A')
        self.ids['_existencia'].text = str(data['cantidad'])
        self.ids['_costo'].text = "{:.2f}".format(data.get('costo', 0.0))
        self.ids['_precio'].text = "{:.2f}".format(data['precio'])

        # Dibujar fondo
        self._dibujar_fondo()
        self.bind(pos=self._dibujar_fondo, size=self._dibujar_fondo)

        return super().refresh_view_attrs(rv, index, data)

    def _dibujar_fondo(self, *args):
        """Dibuja el fondo considerando selección y stock bajo"""
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle

            if self.selected:
                Color(0.8, 1, 1, 1)  # Azul claro
            else:
                cantidad = self.data.get('cantidad', 0)
                cantidad_minima = self.data.get('cantidad_minima', 0)
                if cantidad < cantidad_minima:
                    Color(1, 0.9, 0.4, 1)  # Amarillo suave
                else:
                    Color(0.94, 0.94, 0.94, 1)  # Gris claro

            self.rect = Rectangle(pos=self.pos, size=self.size)
            
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]['seleccionado'] = is_selected
        self._dibujar_fondo()

class InventarioPopup2(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = ''
        self.size_hint = (0.7, 0.6)
        self.auto_dismiss = False
        self.es_nuevo = True 

    def abrir(self, es_nuevo=True, producto=None):
        self.ids.no_valid_notif.text = ""
        self.es_nuevo = es_nuevo  # ← guardar estado

        if es_nuevo:
            self.ids.producto_info_1.text = 'Agregar producto nuevo'
            self.ids.layout_codigo.opacity = 1
            self.ids.layout_codigo.size_hint_y = None
            self.ids.layout_codigo.height = 40

            # ✅ Mostrar el PRÓXIMO código SIN consumirlo
            proximo = previsualizar_proximo_codigo()
            self.ids.repuesto_codigo.text = str(proximo)
            self.ids.repuesto_codigo.disabled = True

            # Limpiar otros campos...
            self.ids.repuesto_nombre.text = ""
            self.ids.repuesto_grupo.text = ""
            self.ids.repuesto_unidad.text = ""
            self.ids.repuesto_existencia.text = ""
            self.ids.repuesto_minimo.text = ""
            self.ids.repuesto_máximo.text = ""
            self.ids.repuesto_costo.text = ""
            self.ids.repuesto_precio.text = ""
        else:
            self.ids.producto_info_1.text = 'Modificar producto'
            self.ids.layout_codigo.opacity = 1
            self.ids.layout_codigo.size_hint_y = None
            self.ids.layout_codigo.height = 40

            self.ids.repuesto_codigo.text = str(producto['codigo'])
            self.ids.repuesto_codigo.disabled = True  # Siempre deshabilitado en edición
            self.ids.repuesto_nombre.text = producto['nombre']
            self.ids.repuesto_grupo.text = producto.get('grupo', '')
            self.ids.repuesto_unidad.text = producto.get('unidad', '')
            self.ids.repuesto_existencia.text = str(producto['cantidad'])
            self.ids.repuesto_minimo.text = str(producto.get('cantidad_minima', ''))
            self.ids.repuesto_máximo.text = str(producto.get('cantidad_maxima', ''))
            self.ids.repuesto_costo.text = str(producto.get('costo', ''))
            self.ids.repuesto_precio.text = str(producto['precio'])

        self.open()
    
    def verificar(self, nombre, cantidad, precio):
        """Valida los datos y llama al callback. El código se asigna automáticamente si es nuevo."""
        self.ids.no_valid_notif.text = ""

        if not nombre:
            self.ids.no_valid_notif.text = "Falta nombre."
            return

        if not cantidad:
            self.ids.no_valid_notif.text += " Falta existencia."
            return
        try:
            cantidad = int(cantidad)
        except:
            self.ids.no_valid_notif.text += " Existencia debe ser número entero."
            return

        if not precio:
            self.ids.no_valid_notif.text += " Falta precio."
            return
        try:
            precio = float(precio)
        except:
            self.ids.no_valid_notif.text += " Precio debe ser número."
            return

        # Validar mínimos/máximos (igual que antes)
        minimo_text = self.ids.repuesto_minimo.text.strip()
        try:
            minimo = int(minimo_text) if minimo_text else 0
        except:
            self.ids.no_valid_notif.text += " Cantidad mínima debe ser un número entero."
            return

        maximo_text = self.ids.repuesto_máximo.text.strip()
        try:
            maximo = int(maximo_text) if maximo_text else 0
        except:
            self.ids.no_valid_notif.text += " Cantidad máxima debe ser un número entero."
            return

        if self.ids.no_valid_notif.text:
            return

        data = {
            'nombre': nombre.lower().strip(),
            'grupo': self.ids.repuesto_grupo.text.strip(),
            'unidad': self.ids.repuesto_unidad.text.strip(),
            'cantidad': cantidad,
            'cantidad_minima': minimo,
            'cantidad_maxima': maximo,
            'costo': float(self.ids.repuesto_costo.text.strip()) if self.ids.repuesto_costo.text.strip() else 0.0,
            'precio': precio
        }

        # ❌ ELIMINADO: NO asignamos 'codigo' aquí
        # if self.es_nuevo:
        #     data['codigo'] = obtener_siguiente_codigo()

        self.callback(True, data)
        self.dismiss()


class VistaInventario(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todos_los_productos = []  # Almacena todos los productos en memoria
        Clock.schedule_once(self.inicializar, 0.1)

    def inicializar(self, dt):
        """Se llama después de que el .kv haya cargado los widgets"""
        self.cargar_productos()

    def cargar_productos(self, *args):
        """Carga todos los productos desde MongoDB"""
        collection = conectar_mongo1()
        if collection is None:
            print("No se pudo conectar a MongoDB")
            return

        try:
            productos = list(collection.find())
            self.todos_los_productos = []
            for prod in productos:
                self.todos_los_productos.append({
                    'codigo': prod['codigo'],
                    'nombre': prod['nombre'],
                    'grupo': prod['grupo'],
                    'unidad': prod['unidad'],
                    'cantidad': prod['cantidad'],
                    'costo': prod['costo'],
                    'precio': prod['precio'],
                    'cantidad_minima': prod['cantidad_minima'],
                    'cantidad_maxima': prod['cantidad_maxima'],
                    'seleccionado': False
                })
            # Aplicar filtros iniciales (vacíos → mostrar todos)
            self.aplicar_filtros()
        except Exception as e:
            print(f"Error al cargar productos: {e}")

    def aplicar_filtros(self, *args):
        """Filtra los productos según los 4 campos de texto"""
        # Obtener textos de los filtros (en minúsculas para comparación insensible)
        filtro_id = self.ids.filtro_id.text.strip().lower()
        filtro_nombre = self.ids.filtro_nombre.text.strip().lower()
        filtro_grupo = self.ids.filtro_grupo.text.strip().lower()
        filtro_unidad = self.ids.filtro_unidad.text.strip().lower()

        filtrados = []
        for prod in self.todos_los_productos:
            coincide = True

            # Filtro por ID (código)
            if filtro_id and filtro_id not in str(prod['codigo']).lower():
                coincide = False

            # Filtro por Nombre
            if filtro_nombre and filtro_nombre not in prod['nombre'].lower():
                coincide = False

            # Filtro por Grupo
            if filtro_grupo and filtro_grupo not in prod['grupo'].lower():
                coincide = False

            # Filtro por Unidad
            if filtro_unidad and filtro_unidad not in prod['unidad'].lower():
                coincide = False

            if coincide:
                filtrados.append(prod)

        self.ids.rv_productos.data = filtrados
        self.ids.rv_productos.refresh_from_data()

    def agregar_producto(self, agregar=False, validado=None):
        if agregar and validado:
            collection = conectar_mongo1()
            if collection is None:
                return

            # ✅ OBTENER EL VALOR ACTUAL DEL CONTADOR SIN INCREMENTARLO
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            counters = db['counters']
            counter_doc = counters.find_one({"_id": "repuestos_codigo"})
            if not counter_doc:
                print("❌ Contador no existe.")
                return
            codigo_asignado = counter_doc['seq']

            # ✅ ASIGNAR ESE VALOR AL PRODUCTO
            validado['codigo'] = codigo_asignado

            # ✅ INSERTAR EN LA BASE DE DATOS
            collection.insert_one(validado)

            # ✅ INCREMENTAR EL CONTADOR AHORA SÍ
            counters.update_one(
                {"_id": "repuestos_codigo"},
                {"$inc": {"seq": 1}}
            )
            client.close()

            # ✅ RECARGAR LA LISTA
            self.cargar_productos()
        else:
            popup = InventarioPopup2(self.agregar_producto)
            popup.abrir(es_nuevo=True)
    def modificar_producto(self, modificar=False, validado=None):
        indice = self.ids.rv_productos.dato_seleccionado()
        if modificar and validado:
            collection = conectar_mongo1()
            if collection is None:
                return

            producto_actual = self.ids.rv_productos.data[indice]
            collection.update_one(
                {"codigo": producto_actual['codigo']},
                {"$set": validado}
            )
            self.cargar_productos()
        else:
            if indice >= 0:
                producto = self.ids.rv_productos.data[indice]
                popup = InventarioPopup2(self.modificar_producto)
                popup.abrir(es_nuevo=False, producto=producto)

    def eliminar_producto(self):
        indice = self.ids.rv_productos.dato_seleccionado()
        if indice < 0:
            print("No hay producto seleccionado")
            return

        producto = self.ids.rv_productos.data[indice]
        collection = conectar_mongo1()
        if collection is None:
            return

        collection.delete_one({"codigo": producto['codigo']})
        self.ids.rv_productos.data.pop(indice)
        self.ids.rv_productos.refresh_from_data()
    def actualizar_vista(self):
        """Recarga todos los productos desde la base de datos."""
        self.cargar_productos()

from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty

class SelectableRegistroLabel(RecycleDataViewBehavior, BoxLayout):
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_ficha'].text = str(data.get('numero_ficha', 'N/A'))
        self.ids['_id_repuesto'].text = str(data.get('codigo', 'N/A'))  
        self.ids['_repuesto'].text = data.get('nombre', 'N/A')
        self.ids['_operador'].text = data.get('operador', 'N/A')
        self.ids['_cantidad'].text = str(data.get('cantidad', '0'))
        self.ids['_precio'].text = f"{data.get('precio', 0):.2f}"
        self.ids['_total'].text = f"{data.get('total', 0):.2f}"
        self.ids['_fecha'].text = data.get('fecha_registro_str', 'N/A')
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False



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




class RepuestoFila(RecycleDataViewBehavior, BoxLayout):
    """Fila optimizada con botón 'Usar' y sombreado condicional."""
    index = None
    codigo = StringProperty()
    nombre = StringProperty()
    precio = NumericProperty()
    cantidad = NumericProperty()
    cantidad_minima = NumericProperty()
    repuesto_data = ObjectProperty()

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.codigo = str(data.get('codigo', ''))
        self.nombre = data.get('nombre', '')
        self.precio = float(data.get('precio', 0))
        self.cantidad = int(data.get('cantidad', 0))
        self.cantidad_minima = int(data.get('cantidad_minima', 0))
        self.repuesto_data = data
        self._actualizar_fondo()
        return super().refresh_view_attrs(rv, index, data)

    def _actualizar_fondo(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.cantidad < self.cantidad_minima:
                Color(1, 1, 0, 0.3)  # Amarillo si bajo stock
            else:
                Color(0, 0, 0, 0)    # Transparente
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._actualizar_rect, size=self._actualizar_rect)

    def _actualizar_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_usar(self, instance):
        # Llama al callback del popup con el repuesto completo
        rv = self.parent.recycleview
        if hasattr(rv.parent.parent, 'on_seleccionar'):
            rv.parent.parent.on_seleccionar(self.repuesto_data)

class RepuestosPopup(Popup):
    def __init__(self, callback, 
                 filtro_id_inicial='', 
                 filtro_nombre_inicial='', 
                 seleccionados_iniciales=None, 
                 **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Seleccionar Repuestos"
        self.size_hint = (0.95, 0.85)
        self.auto_dismiss = False

        self.seleccionados = set(seleccionados_iniciales or [])
        self.filtro_id_inicial = filtro_id_inicial
        self.filtro_nombre_inicial = filtro_nombre_inicial


        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- DOS CAMPOS DE FILTRO: ID y NOMBRE ---
        filtros_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.filtro_id = TextInput(hint_text='Filtrar por ID', size_hint_x=0.10)
        self.filtro_id.text = self.filtro_id_inicial
        self.filtro_id.bind(text=self.on_filtro_change)
        filtros_layout.add_widget(self.filtro_id)
        
        self.filtro_nombre = TextInput(hint_text='Filtrar por nombre', size_hint_x=0.80)
        self.filtro_nombre.text = self.filtro_nombre_inicial
        self.filtro_nombre.bind(text=self.on_filtro_change)
        filtros_layout.add_widget(self.filtro_nombre)
        layout.add_widget(filtros_layout)

        # --- ENCABEZADOS (SIN STOCK) ---
        header = BoxLayout(size_hint_y=None, height=40, spacing=5)
        header.add_widget(Label(text="ID", size_hint_x=0.12, bold=True))
        header.add_widget(Label(text="Nombre", size_hint_x=0.47, bold=True))  # ↑ aumentado de 0.40 a 0.47
        header.add_widget(Label(text="Precio", size_hint_x=0.13, bold=True))
        header.add_widget(Label(text="Cantidad", size_hint_x=0.13, bold=True))
        header.add_widget(Label(text="Seleccionar", size_hint_x=0.15, bold=True))  # ↑ aumentado de 0.08 a 0.15
        layout.add_widget(header)

        # --- LISTA SCROLLABLE ---
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        # --- BOTONES ---
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_deseleccionar = Button(text="Deseleccionar todos")
        btn_deseleccionar.bind(on_release=self.deseleccionar_todos)
        btn_layout.add_widget(btn_deseleccionar)
        
        btn_aplicar = Button(text="Aplicar Selección")
        btn_aplicar.bind(on_release=self.on_aplicar)
        btn_layout.add_widget(btn_aplicar)
        
        btn_cancelar = Button(text="Cancelar")
        btn_cancelar.bind(on_release=self.dismiss)
        btn_layout.add_widget(btn_cancelar)
        
        layout.add_widget(btn_layout)

        self.content = layout
        self.checkbox_map = {}
        self.cargar_repuestos()

    def deseleccionar_todos(self, instance):
        self.seleccionados.clear()
        for cb in self.checkbox_map.values():
            cb.active = False

    def cargar_repuestos(self):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['Repuestos']
            self.todos_repuestos = list(collection.find({}))
            client.close()
            print(f"✅ Cargados {len(self.todos_repuestos)} repuestos de BD")
            self.filtrar_repuestos()
        except Exception as e:
            print(f"❌ Error al cargar repuestos: {e}")
            self.todos_repuestos = []
            self.grid.clear_widgets()
            self.grid.add_widget(Label(text="Error al cargar repuestos", color=(1, 0, 0, 1)))

    def on_filtro_change(self, instance, value):
        if hasattr(self, '_filtro_event'):
            self._filtro_event.cancel()
        from kivy.clock import Clock
        self._filtro_event = Clock.schedule_once(lambda dt: self.filtrar_repuestos(), 0.3)

    def filtrar_repuestos(self, *args):
        filtro_id = self.filtro_id.text.strip().lower()
        filtro_nombre = self.filtro_nombre.text.strip().lower()

        # Separar seleccionados y no seleccionados
        seleccionados_lista = []
        no_seleccionados_lista = []

        for repuesto in self.todos_repuestos:
            codigo_str = str(repuesto.get('codigo', '')).strip().lower()
            nombre_str = str(repuesto.get('nombre', '')).strip().lower()
            coincide_id = (not filtro_id) or (filtro_id in codigo_str)
            coincide_nombre = (not filtro_nombre) or (filtro_nombre in nombre_str)
            if coincide_id and coincide_nombre:
                nombre = repuesto.get('nombre', 'Sin nombre')
                if nombre in self.seleccionados:
                    seleccionados_lista.append(repuesto)
                else:
                    no_seleccionados_lista.append(repuesto)

        # Concatenar: primero los seleccionados, luego los demás
        coincidentes = seleccionados_lista + no_seleccionados_lista
        coincidentes = coincidentes[:10]  # Límite visual

        self.grid.clear_widgets()
        self.checkbox_map = {}

        for repuesto in coincidentes:
            nombre = repuesto.get('nombre', 'Sin nombre')
            codigo = str(repuesto.get('codigo', ''))
            precio = repuesto.get('precio', 0)
            existencia = repuesto.get('cantidad', 0)

            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            lbl_codigo = Label(text=codigo, size_hint_x=0.12, halign='center', valign='middle')
            lbl_codigo.bind(size=lbl_codigo.setter('text_size'))

            lbl_nombre = Label(text=nombre, size_hint_x=0.47, halign='left', valign='middle', shorten=True)
            lbl_nombre.bind(size=lbl_nombre.setter('text_size'))

            lbl_precio = Label(text=f"{precio:.2f}", size_hint_x=0.13, halign='center', valign='middle')
            lbl_precio.bind(size=lbl_precio.setter('text_size'))

            lbl_cantidad = Label(text=str(existencia), size_hint_x=0.13, halign='center', valign='middle')
            lbl_cantidad.bind(size=lbl_cantidad.setter('text_size'))

            cb = CheckBox(size_hint_x=0.15)
            cb.nombre = nombre
            cb.bind(active=self.on_checkbox_toggle)
            if nombre in self.seleccionados:
                cb.active = True
            self.checkbox_map[nombre] = cb

            row.add_widget(lbl_codigo)
            row.add_widget(lbl_nombre)
            row.add_widget(lbl_precio)
            row.add_widget(lbl_cantidad)
            row.add_widget(cb)

            self.grid.add_widget(row)

    def on_checkbox_toggle(self, checkbox, value):
        nombre = checkbox.nombre
        if value:
            self.seleccionados.add(nombre)
        else:
            self.seleccionados.discard(nombre)

    def on_aplicar(self, instance):
        seleccionados = list(self.seleccionados)
        if self.callback:
            self.callback(seleccionados)
        self.dismiss()


class VistaRegistro(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operadores_seleccionados = ["Todos"]
        self.repuestos_seleccionados = None
        self.filtro_repuesto_id = ''
        self.filtro_repuesto_nombre = ''
        self.tipo_ficha_seleccionado = "Ambas"
        Clock.schedule_once(self.inicializar_repuestos, 0.1)

    # ——————————————————————————————
    # Gestión de fechas (máscara sin problemas de cursor)
    # ——————————————————————————————

    def solo_digitos(self, texto, from_undo=False):
        """Permite solo dígitos en campos de fecha."""
        return ''.join(filter(str.isdigit, texto))

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
        """Aplica filtros de operadores (múltiples) y fechas."""
        if hasattr(self, 'filtros_programados'):
            self.filtros_programados = False

        fecha_desde = self.parse_fecha(self.ids.fecha_desde_rep.text)
        fecha_hasta = self.parse_fecha(self.ids.fecha_hasta_rep.text)

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            print("❌ Rango de fechas inválido.")
            return

        self.cargar_repuestos_filtrados(
            operadores_filtro=self.operadores_seleccionados,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
            
    def cargar_repuestos_filtrados(self, operadores_filtro=None, fecha_desde=None, fecha_hasta=None):
            """Carga repuestos con filtros desde MongoDB."""
            try:
                client = MongoClient('mongodb://localhost:27017/')
                db = client['Inrema']
                collection = db['registro_repuestos']

                query = {}

                # Filtro por operadores
                if operadores_filtro and "Todos" not in operadores_filtro:
                    query["operador"] = {"$in": operadores_filtro}

                # Filtro por repuestos (nombre)
                if self.repuestos_seleccionados:
                    query["nombre"] = {"$in": self.repuestos_seleccionados}

                # Filtro por fechas
                if fecha_desde or fecha_hasta:
                    rango = {}
                    if fecha_desde:
                        rango["$gte"] = fecha_desde.isoformat()
                    if fecha_hasta:
                        fin_dia = fecha_hasta.replace(hour=23, minute=59, second=59, microsecond=999999)
                        rango["$lte"] = fin_dia.isoformat()
                    if rango:
                        query["fecha_registro"] = rango

                # ✅ FILTRO POR TIPO DE FICHA (directo en MongoDB)
                tipo = self.tipo_ficha_seleccionado
                if tipo != "Ambas":
                    # Convertimos a minúsculas para coincidir con los valores en DB
                    tipo_db = tipo.lower()  # → "rectificadora" o "torno"
                    query["tipo_ficha"] = tipo_db

                # Obtener datos
                repuestos = list(collection.find(query).sort("fecha_registro", -1))

                data = []
                total_general = 0.0

                for r in repuestos:
                    fecha_str = "N/A"
                    if 'fecha_registro' in r:
                        try:
                            dt = datetime.fromisoformat(r['fecha_registro'].replace('Z', '+00:00'))
                            fecha_str = dt.strftime("%d/%m/%Y")
                        except:
                            fecha_str = str(r['fecha_registro'])[:10]

                    total_valor = r.get('total', 0.0)
                    total_general += total_valor

                    data.append({
                        'numero_ficha': r.get('numero_ficha', 'N/A'),
                        'codigo': r.get('codigo', 'N/A'),
                        'nombre': r.get('nombre', 'N/A'),
                        'operador': r.get('operador', 'N/A'),
                        'cantidad': r.get('cantidad', 0),
                        'precio': r.get('precio', 0.0),
                        'total': total_valor,
                        'fecha_registro_str': fecha_str,
                        'seleccionado': False,
                        '_id': r.get('_id')
                    })

                self.ids.rv_repuestos.data = data
                client.close()

                if hasattr(self.ids, 'lbl_total_general'):
                    self.ids.lbl_total_general.text = f"$ {total_general:,.2f}"

            except Exception as e:
                print(f"❌ Error al cargar repuestos filtrados: {e}")
                self.ids.rv_repuestos.data = []
                if hasattr(self.ids, 'lbl_total_general'):
                    self.ids.lbl_total_general.text = "$ 0.00"
    # ——————————————————————————————
    # Inicialización
    # ——————————————————————————————

    def inicializar_repuestos(self, dt):
        """Carga todos los repuestos inicialmente."""
        self.cargar_repuestos()

    def cargar_repuestos(self, *args):
        """Carga todos los repuestos (sin filtros)."""
        self.operadores_seleccionados = ["Todos"]
        if hasattr(self.ids, 'btn_filtro_operador'):
            self.ids.btn_filtro_operador.text = "Operadores: Todos"
        self.aplicar_filtros()

    # ——————————————————————————————
    # Selección múltiple de operadores
    # ——————————————————————————————

    def abrir_popup_operadores(self):
        """Abre el popup para seleccionar múltiples operadores."""
        popup = OperadoresPopup(callback=self.on_operadores_seleccionados)
        popup.open()

    def on_operadores_seleccionados(self, nombres_seleccionados):
        """Actualiza el botón con los nombres de los operadores seleccionados."""
        if not nombres_seleccionados:
            self.operadores_seleccionados = ["Todos"]
            texto_boton = "Operadores: Todos"
        else:
            self.operadores_seleccionados = nombres_seleccionados
            total = len(nombres_seleccionados)

            if total == 1:
                texto_boton = f"Operadores: {nombres_seleccionados[0]}"
            elif total <= 3:
                # Mostrar todos los nombres
                texto_boton = "Operadores: " + ", ".join(nombres_seleccionados)
            else:
                # Mostrar los primeros 2 + "y X más"
                primeros = ", ".join(nombres_seleccionados[:2])
                texto_boton = f"Operadores: {primeros} y {total - 2} más"

        # Actualizar el texto del botón
        if hasattr(self.ids, 'btn_filtro_operador'):
            self.ids.btn_filtro_operador.text = texto_boton

        # Aplicar los filtros inmediatamente
        self.aplicar_filtros()
        # ——————————————————————————————
    # Eliminación (opcional)
    # ——————————————————————————————
    def abrir_popup_repuestos(self):
        popup = RepuestosPopup(
            callback=self.on_repuestos_seleccionados,
            filtro_id_inicial=self.filtro_repuesto_id,
            filtro_nombre_inicial=self.filtro_repuesto_nombre,
            seleccionados_iniciales=self.repuestos_seleccionados
        )
        # Guardar referencia si quieres reutilizar, o usar bind para capturar cambios al cerrar
        popup.bind(on_dismiss=self.guardar_estado_repuestos_popup)
        popup.open()
    def guardar_estado_repuestos_popup(self, popup):
        """Opcional: si quieres recordar filtros incluso si cancelas."""
        self.filtro_repuesto_id = popup.filtro_id.text
        self.filtro_repuesto_nombre = popup.filtro_nombre.text
        
    def on_repuestos_seleccionados(self, nombres_seleccionados):
        """Recibe lista de nombres de repuestos seleccionados y actualiza el botón."""
        self.repuestos_seleccionados = nombres_seleccionados if nombres_seleccionados else None

        # Actualizar texto del botón de repuestos
        if hasattr(self.ids, 'btn_filtro_repuesto'):
            if not nombres_seleccionados:
                texto_boton = "Filtrar por repuesto"
            else:
                total = len(nombres_seleccionados)
                if total == 1:
                    texto_boton = "1 repuesto seleccionado"
                else:
                    texto_boton = f"{total} repuestos seleccionados"
            self.ids.btn_filtro_repuesto.text = texto_boton

        # Aplicar los filtros inmediatamente
        self.aplicar_filtros()

    def dato_seleccionado(self):
        for i, item in enumerate(self.ids.rv_repuestos.data):
            if item.get('seleccionado', False):
                return i
        return -1

    def eliminar_repuesto(self):
        indice = self.dato_seleccionado()
        if indice < 0:
            print("❌ Seleccione un repuesto.")
            return
        repuesto = self.ids.rv_repuestos.data[indice]
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            db['registro_repuestos'].delete_one({'_id': repuesto['_id']})
            self.ids.rv_repuestos.data.pop(indice)
            self.ids.rv_repuestos.refresh_from_data()
            client.close()
            print("✅ Repuesto eliminado.")
        except Exception as e:
            print(f"❌ Error al eliminar: {e}")
            
    def on_tipo_ficha_change(self, tipo):
        """Actualiza el filtro por tipo de ficha y aplica."""
        # Guardamos el valor tal cual para mostrarlo, pero usamos lower() en la consulta
        self.tipo_ficha_seleccionado = tipo
        self.aplicar_filtros()

    def actualizar_vista(self):
        """
        Recarga los datos aplicando los filtros actuales.
        Útil para refrescar la vista tras cambios externos (ej: eliminación, edición).
        """
        self.aplicar_filtros()
            
            
            

class VistaMenuI(Screen):
    def ir_a(self, pantalla):
        # El parent de esta pantalla es el ScreenManager
        self.parent.current = pantalla

class VistaUsuarios(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CustomDropDown2(DropDown):
    def __init__(self, cambiar_callback, admin_window1, **kwargs):
        self._succ_cb = cambiar_callback
        self.admin_window = admin_window1  # ✅ Guardamos la referencia
        super(CustomDropDown2, self).__init__(**kwargs)
        #self.actualizar_visibilidad_por_nivel()

    def vista(self, vista):
        if callable(self._succ_cb):
            self._succ_cb(True, vista)

    def salir2(self):
        if self.admin_window and hasattr(self.admin_window, 'inventario'):
            print("D")  # ✅ Llama al salir() de la instancia real
        else:
            pass
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
        
        if nivel == 1:
            self.ids.drop_operadores.disabled = True
        else:
            self.ids.drop_operadores.disabled = False
            
            

class AdminI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vista_actual = 'inventario'
        self.dropdown = CustomDropDown2(cambiar_callback=self.cambiar_vista, admin_window1=self)
        self.ids.cambiar_vista.bind(on_release=self.dropdown.open)
        self.usuario_nivel = None  # ← nuevo

    def actualizar_nivel_usuario(self, nivel):
        self.usuario_nivel = nivel
        if hasattr(self, 'dropdown'):
            self.dropdown.actualizar_visibilidad_por_nivel(nivel)  
    def cambiar_vista(self):
        pass

    def salir(self):
        self.parent.parent.current = 'signin'  
        
    def operadores(self):  
        # Asume que estás usando ScreenManager
        print("Me cague")
        self.parent.parent.current = 'operadores'  
    def pacientes(self):  
        # Asume que estás usando ScreenManager
        print("Me cague")
        self.parent.parent.current = 'admin'  
        
    def salir2(self):
        sm = self.ids.vista_manager1
        sm.current = 'menu'


class AdminRV1(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

    def dato_seleccionado(self):
        for i, item in enumerate(self.data):
            if item.get('seleccionado'):
                return i
        return -1
        
class MiApp(App):  
    def build(self):  
        return AdminI()  
  
if __name__ == "__main__":  
    MiApp().run()