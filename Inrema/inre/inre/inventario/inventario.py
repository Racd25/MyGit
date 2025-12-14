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
from kivy.uix.screenmanager import Screen 







def conectar_mongo1():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['Inrema']
        return db['Repuestos']  # Colección "Repuestos"
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None


class SelectableInventarioLabel(RecycleDataViewBehavior, BoxLayoutBase):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.data = data  # Guardar para usar después

        # Actualizar texto
        self.ids['_idrepuesto'].text = str(1 + index)
        self.ids['_repuesto'].text = data['nombre'].capitalize()
        self.ids['_grupo'].text = data.get('grupo', 'N/A')
        self.ids['_unidad'].text = data.get('unidad', 'N/A')
        self.ids['_existencia'].text = str(data['cantidad'])
        self.ids['_costo'].text = "{:.2f}".format(data.get('costo', 0.0))
        self.ids['_precio'].text = "{:.2f}".format(data['precio'])

        # Dibujar fondo
        self._dibujar_fondo()

        # Vincular actualización
        self.bind(pos=self._dibujar_fondo, size=self._dibujar_fondo)

        return super().refresh_view_attrs(rv, index, data)


    def _dibujar_fondo(self, *args):
        """Dibuja el fondo considerando selección y stock bajo"""
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle

            # Definir color según estado
            if self.selected:
                # Si está seleccionado, siempre azul (prioridad máxima)
                Color(0.8, 1, 1, 1)  # Azul claro
            else:
                cantidad = self.data.get('cantidad', 0)
                cantidad_minima = self.data.get('cantidad_minima', 0)
                if cantidad < cantidad_minima:
                    Color(1, 0.9, 0.4, 1)  # Amarillo suave
                else:
                    Color(0.94, 0.94, 0.94, 1)  # Gris claro

            # Dibujar rectángulo
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

# === Popup para Agregar/Modificar Producto ===


class InventarioPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = ''  # El título se define en .kv
        self.size_hint = (0.5, 0.5)
        self.auto_dismiss = False

    def abrir(self, es_nuevo=True, producto=None):
        self.ids.no_valid_notif.text = ""

        if es_nuevo:
            self.ids.producto_info_1.text = 'Agregar producto nuevo'
            self.ids.repuesto_codigo.disabled = False
            self.ids.repuesto_codigo.text = ""
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
            self.ids.repuesto_codigo.text = str(producto['codigo'])
            self.ids.repuesto_codigo.disabled = True
            self.ids.repuesto_nombre.text = producto['nombre']
            self.ids.repuesto_grupo.text = producto.get('grupo', '')
            self.ids.repuesto_unidad.text = producto.get('unidad', '')
            self.ids.repuesto_existencia.text = str(producto['cantidad'])
            self.ids.repuesto_minimo.text = str(producto.get('cantidad_minima', ''))
            self.ids.repuesto_máximo.text = str(producto.get('cantidad_maxima', ''))
            self.ids.repuesto_costo.text = str(producto.get('costo', ''))
            self.ids.repuesto_precio.text = str(producto['precio'])

        self.open()

    def verificar(self, codigo, nombre, cantidad, precio):
        """Valida los datos y llama al callback"""
        self.ids.no_valid_notif.text = ""

        # Validaciones básicas (código, nombre, cantidad, precio)
        if not codigo:
            self.ids.no_valid_notif.text = "Falta código."
            return
        try:
            codigo = int(codigo)
        except:
            self.ids.no_valid_notif.text = "Código debe ser un número entero."
            return

        if not nombre:
            self.ids.no_valid_notif.text += " Falta nombre."
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

        # Validar y obtener Cantidad Mínima
        minimo_text = self.ids.repuesto_minimo.text.strip()
        try:
            minimo = int(minimo_text) if minimo_text else 0
        except:
            self.ids.no_valid_notif.text += " Cantidad mínima debe ser un número entero."
            return

        # Validar y obtener Cantidad Máxima
        maximo_text = self.ids.repuesto_máximo.text.strip()
        try:
            maximo = int(maximo_text) if maximo_text else 0
        except:
            self.ids.no_valid_notif.text += " Cantidad máxima debe ser un número entero."
            return

        # Si hay error acumulado, no continuar
        if self.ids.no_valid_notif.text:
            return

        # ✅ Datos validados y listos para guardar
        data = {
            'codigo': codigo,
            'nombre': nombre.lower().strip(),
            'grupo': self.ids.repuesto_grupo.text.strip(),
            'unidad': self.ids.repuesto_unidad.text.strip(),
            'cantidad': cantidad,
            'cantidad_minima': minimo,
            'cantidad_maxima': maximo,
            'costo': float(self.ids.repuesto_costo.text.strip()) if self.ids.repuesto_costo.text.strip() else 0.0,
            'precio': precio
        }

        # Llamar al callback y cerrar
        self.callback(True, data)
        self.dismiss()

# === Vista Principal: VistaProductos ===

class VistaInventario(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Programar carga después de que el .kv esté listo
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
            productos = collection.find()
            data = []
            for prod in productos:
                data.append({
                    'codigo': prod['codigo'],
                    'nombre': prod['nombre'],
                    'grupo' : prod ['grupo'],
                    'unidad' : prod ['unidad'],
                    'cantidad': prod['cantidad'],
                    'costo': prod['costo'],
                    'precio': prod['precio'],
                    'cantidad_minima': prod['cantidad_minima'],
                    'cantidad_maxima': prod['cantidad_maxima'],

                    
                    'seleccionado': False
                })
            self.ids.rv_productos.data = data
            self.ids.rv_productos.refresh_from_data()
        except Exception as e:
            print(f"Error al cargar productos: {e}")

    def agregar_producto(self, agregar=False, validado=None):
        if agregar and validado:
            collection = conectar_mongo1()
            if collection is None:
                return

            # Evitar duplicados por código
            if collection.find_one({"codigo": validado['codigo']}):
                print("Producto con este código ya existe.")
                return

            collection.insert_one(validado)
            validado['seleccionado'] = False
            self.ids.rv_productos.data.append(validado)
            self.ids.rv_productos.refresh_from_data()
        else:
            popup = InventarioPopup(self.agregar_producto)
            popup.abrir(es_nuevo=True)

    def modificar_producto(self, modificar=False, validado=None):
        indice = self.ids.rv_productos.dato_seleccionado()
        if modificar and validado:
            collection = conectar_mongo1()
            if  collection is None:
                return

            producto_actual = self.ids.rv_productos.data[indice]
            collection.update_one(
                {"codigo": producto_actual['codigo']},
                {"$set": validado}
            )
            # Actualizar en la interfaz
            self.ids.rv_productos.data[indice].update(validado)
            self.ids.rv_productos.refresh_from_data()
        else:
            if indice >= 0:
                producto = self.ids.rv_productos.data[indice]
                popup = InventarioPopup(self.modificar_producto)
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
  



class AdminRV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

    def dato_seleccionado(self):
        for i, item in enumerate(self.data):
            if item.get('seleccionado'):
                return i
        return -1
        
class InventarioApp(App):  
    def build(self):  
        return VistaInventario()  
  
if __name__ == "__main__":  
    InventarioApp().run()