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
from kivy.properties import ObjectProperty
Builder.load_file("ventas/ventas.kv")


# Cargar el archivo .kv
Builder.load_file("ventas/ventas.kv")

# === Datos simulados (sin base de datos) ===
PRODUCTOS_SIMULADOS = [
    {'codigo': 'P001', 'nombre': 'Tornillo M6', 'precio': 1.50, 'cantidad': 100, 'tipo_registro': 'producto'},
    {'codigo': 'P002', 'nombre': 'Tuercas', 'precio': 0.80, 'cantidad': 200, 'tipo_registro': 'producto'},
    {'codigo': 'P003', 'nombre': 'Arandela', 'precio': 0.20, 'cantidad': 500, 'tipo_registro': 'producto'},
]

SERVICIOS_SIMULADOS = [
    {'codigo': 'S001', 'nombre': 'Soldadura', 'precio': 25.00, 'cantidad': 0, 'tipo_registro': 'servicio'},
    {'codigo': 'S002', 'nombre': 'Torno', 'precio': 30.00, 'cantidad': 0, 'tipo_registro': 'servicio'},
    {'codigo': 'S003', 'nombre': 'Pintura', 'precio': 40.00, 'cantidad': 0, 'tipo_registro': 'servicio'},
]


# === Widgets Personalizados ===

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """Añade selección y foco."""
    touch_deselect_last = BooleanProperty(True)


class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_por_articulo'].text = "{:.2f}".format(data['precio'])
        self.ids['_precio'].text = "{:.2f}".format(data['precio_total'])
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]['seleccionado'] = is_selected


class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    stock_level = ObjectProperty('normal')

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = "{:.2f}".format(data['precio'])

        # Simular nivel de stock
        if data.get('tipo_registro') == 'producto':
            cantidad = int(data['cantidad'])
            if cantidad < 2:
                self.stock_level = 'critical'
            elif cantidad < 5:
                self.stock_level = 'warning'
            else:
                self.stock_level = 'normal'
        else:
            self.stock_level = 'normal'

        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]['seleccionado'] = is_selected


# === RecycleView para el carrito ===

class RV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.modificar_producto = None

    def agregar_articulo(self, articulo):
        articulo['seleccionado'] = False
        articulo['tipo_registro'] = articulo.get('tipo_registro', 'producto')
        articulo['cantidad_carrito'] = articulo.get('cantidad_carrito', 1)
        articulo['precio_total'] = articulo['precio'] * articulo['cantidad_carrito']

        # Buscar si ya existe
        for item in self.data:
            if item['codigo'] == articulo['codigo'] and item['tipo_registro'] == 'producto':
                item['cantidad_carrito'] += 1
                item['precio_total'] = item['precio'] * item['cantidad_carrito']
                self.refresh_from_data()
                return

        self.data.append(articulo)
        self.refresh_from_data()

    def articulo_seleccionado(self):
        for i, item in enumerate(self.data):
            if item.get('seleccionado'):
                return i
        return -1

    def eliminar_articulo(self):
        indice = self.articulo_seleccionado()
        precio = 0
        if indice >= 0:
            item = self.data.pop(indice)
            precio = item['precio_total']
            self.refresh_from_data()
        return precio

    def modificar_articulo(self):
        indice = self.articulo_seleccionado()
        if indice >= 0:
            popup = CambiarCantidadPopup(self.data[indice], self.actualizar_articulo)
            popup.open()
        else:
            print("No hay artículo seleccionado")

    def actualizar_articulo(self, valor):
        indice = self.articulo_seleccionado()
        if indice >= 0:
            if valor == 0:
                self.data.pop(indice)
            else:
                self.data[indice]['cantidad_carrito'] = valor
                self.data[indice]['precio_total'] = self.data[indice]['precio'] * valor
            self.refresh_from_data()
            nuevo_total = sum(item['precio_total'] for item in self.data)
            if self.modificar_producto:
                self.modificar_producto(False, nuevo_total)


# === Popups ===

class ProductoPorNombrePopup(Popup):
    def __init__(self, input_nombre, agregar_producto_callback, **kwargs):
        super().__init__(**kwargs)
        self.input_nombre = input_nombre.lower()
        self.agregar_producto = agregar_producto_callback
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        self.title = "Buscar Producto/Servicio"

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # RecycleView
        self.rvs = RV()
        layout.add_widget(self.rvs)

        # Botones
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_seleccionar = Button(text="Seleccionar", on_release=self.seleccionar_articulo, size_hint_x=0.5)
        btn_cancelar = Button(text="Cancelar", on_release=self.dismiss, size_hint_x=0.5)
        btn_layout.add_widget(btn_seleccionar)
        btn_layout.add_widget(btn_cancelar)
        layout.add_widget(btn_layout)

        self.content = layout
        self.mostrar_articulos()

    def mostrar_articulos(self):
        # Mostrar productos y servicios simulados
        todos = PRODUCTOS_SIMULADOS + SERVICIOS_SIMULADOS
        for item in todos:
            nombre = item['nombre'].lower()
            if self.input_nombre in nombre:
                producto = {
                    'codigo': item['codigo'],
                    'nombre': item['nombre'],
                    'precio': item['precio'],
                    'cantidad': item['cantidad'],
                    'tipo_registro': item['tipo_registro']
                }
                self.rvs.agregar_articulo(producto)

    def seleccionar_articulo(self, *args):
        indice = self.rvs.articulo_seleccionado()
        if indice >= 0:
            _articulo = self.rvs.data[indice]
            articulo = {
                'codigo': _articulo['codigo'],
                'nombre': _articulo['nombre'],
                'precio': _articulo['precio'],
                'cantidad_carrito': 1,
                'cantidad_inventario': _articulo['cantidad'],
                'precio_total': _articulo['precio'],
                'tipo_registro': _articulo['tipo_registro']
            }
            if callable(self.agregar_producto):
                self.agregar_producto(articulo)
            self.dismiss()


class CambiarCantidadPopup(Popup):
    def __init__(self, data, actualizar_callback, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.actualizar_callback = actualizar_callback
        self.title = "Modificar Cantidad"
        self.size_hint = (0.6, 0.4)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=f"Producto: {data['nombre'].capitalize()}"))
        layout.add_widget(Label(text=f"Cantidad actual: {data['cantidad_carrito']}"))

        self.input = TextInput(text=str(data['cantidad_carrito']), multiline=False, input_filter='int')
        layout.add_widget(self.input)

        self.notificacion = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.notificacion)

        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_layout.add_widget(Button(text="Guardar", on_release=self.guardar))
        btn_layout.add_widget(Button(text="Cancelar", on_release=self.dismiss))
        layout.add_widget(btn_layout)

        self.content = layout

    def guardar(self, *args):
        try:
            nueva_cantidad = int(self.input.text.strip())
            if nueva_cantidad < 0:
                self.notificacion.text = "La cantidad no puede ser negativa"
                return
            self.actualizar_callback(nueva_cantidad)
            self.dismiss()
        except ValueError:
            self.notificacion.text = "Cantidad no válida"


class PagarPopup(Popup):
    def __init__(self, total, pagado_callback, **kwargs):
        super().__init__(**kwargs)
        self.total = total
        self.pagado = pagado_callback
        self.title = "Pagar"
        self.size_hint = (0.6, 0.5)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=f"Total: ${total:.2f}"))

        self.recibido = TextInput(hint_text="Cantidad recibida", multiline=False)
        self.recibido.bind(text=self.mostrar_cambio)
        layout.add_widget(self.recibido)

        self.cambio = Label(text="Cambio: ")
        layout.add_widget(self.cambio)

        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        self.boton_pagar = Button(text="Pagar", disabled=True, on_release=self.on_pagar)
        btn_layout.add_widget(self.boton_pagar)
        btn_layout.add_widget(Button(text="Cancelar", on_release=self.dismiss))
        layout.add_widget(btn_layout)

        self.content = layout

    def mostrar_cambio(self, instance, value):
        try:
            recibido = float(value)
            cambio = recibido - self.total
            self.cambio.text = f"Cambio: ${cambio:.2f}"
            self.boton_pagar.disabled = cambio < 0
        except ValueError:
            self.cambio.text = "Cambio: Inválido"
            self.boton_pagar.disabled = True

    def on_pagar(self, *args):
        self.pagado()
        self.dismiss()


class NuevaCompraPopup(Popup):
    def __init__(self, nueva_compra_callback, **kwargs):
        super().__init__(**kwargs)
        self.nueva_compra = nueva_compra_callback
        self.title = "Nueva Compra"
        self.size_hint = (0.6, 0.4)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="¿Desea iniciar una nueva compra?"))
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_layout.add_widget(Button(text="Sí", on_release=self.confirmar))
        btn_layout.add_widget(Button(text="No", on_release=self.dismiss))
        layout.add_widget(btn_layout)
        self.content = layout

    def confirmar(self, *args):
        self.nueva_compra(desde_popup=True)
        self.dismiss()


# === Ventana Principal ===

class VentasWindow(BoxLayout):
    def __init__(self, actualizar_productos_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.total = 0.0
        self.actualizar_productos = actualizar_productos_callback
        self.usuario = {'nombre': 'Demo', 'username': 'demo', 'tipo': 'admin'}
        self.ahora = datetime.now()

        # Programar inicialización después del .kv
        Clock.schedule_once(self.inicializar_despues_kv, 0)

    def inicializar_despues_kv(self, dt):
        try:
            self.ids.rvs.modificar_producto = self.modificar_producto
            self.ids.fecha.text = self.ahora.strftime("%d/%m/%y")
            self.ids.hora.text = self.ahora.strftime("%H:%M:%S")
            Clock.schedule_interval(self.actualizar_hora, 1)
        except Exception as e:
            print(f"Error al inicializar: {e}")

    def actualizar_hora(self, *args):
        self.ahora += timedelta(seconds=1)
        self.ids.hora.text = self.ahora.strftime("%H:%M:%S")

    def agregar_producto_codigo(self, codigo):
        # Buscar en productos simulados
        todos = PRODUCTOS_SIMULADOS + SERVICIOS_SIMULADOS
        for item in todos:
            if item['codigo'] == codigo:
                articulo = {
                    'codigo': item['codigo'],
                    'nombre': item['nombre'],
                    'precio': item['precio'],
                    'cantidad_carrito': 1,
                    'cantidad_inventario': item.get('cantidad', 0),
                    'precio_total': item['precio'],
                    'tipo_registro': item['tipo_registro']
                }
                self.agregar_producto(articulo)
                self.ids.buscar_codigo.text = ''
                return

    def agregar_producto_nombre(self, nombre):
        self.ids.buscar_nombre.text = ''
        popup = ProductoPorNombrePopup(nombre, self.agregar_producto)
        popup.open()

    def agregar_producto(self, articulo):
        self.total += articulo['precio']
        self.ids.sub_total.text = f'$ {self.total:.2f}'
        self.ids.rvs.agregar_articulo(articulo)

    def eliminar_producto(self):
        menos_precio = self.ids.rvs.eliminar_articulo()
        self.total -= menos_precio
        self.ids.sub_total.text = f'$ {self.total:.2f}'

    def modificar_producto(self, cambio=True, nuevo_total=None):
        if cambio:
            self.ids.rvs.modificar_articulo()
        else:
            self.total = nuevo_total
            self.ids.sub_total.text = f'$ {self.total:.2f}'

    def pagar(self):
        if self.ids.rvs.data:
            popup = PagarPopup(self.total, self.pagado)
            popup.open()
        else:
            self.ids.notificacion_falla.text = 'No hay nada que pagar'

    def pagado(self):
        self.ids.notificacion_exito.text = 'Compra realizada con éxito'
        self.ids.notificacion_falla.text = ''
        self.ids.total.text = f'{self.total:.2f}'
        self.ids.buscar_codigo.disabled = True
        self.ids.buscar_nombre.disabled = True
        self.ids.pagar.disabled = True

        # Simular guardado (no hace nada)
        print("Venta registrada (simulado):", self.total)

        if self.actualizar_productos:
            self.actualizar_productos([])

    def nueva_compra(self, desde_popup=False):
        if desde_popup:
            self.ids.rvs.data = []
            self.ids.rvs.refresh_from_data()
            self.total = 0.0
            self.ids.sub_total.text = '$ 0.00'
            self.ids.total.text = '0.00'
            self.ids.notificacion_exito.text = ""
            self.ids.notificacion_falla.text = ''
            self.ids.buscar_codigo.disabled = False
            self.ids.buscar_nombre.disabled = False
            self.ids.pagar.disabled = False
        else:
            popup = NuevaCompraPopup(self.nueva_compra)
            popup.open()

    def poner_usuario(self, usuario):
        self.ids.bienvenido_label.text = f'Bienvenido {usuario["nombre"]}'
        self.usuario = usuario
        self.ids.admin_boton.disabled = usuario['tipo'] == 'trabajador'


class VentasApp(App):
    def build(self):
        return VentasWindow()


if __name__ == '__main__':
    VentasApp().run()
    print("Aplicación finalizada")