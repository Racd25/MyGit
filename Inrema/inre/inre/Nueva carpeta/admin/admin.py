from kivy.app import App  
from kivy.uix.boxlayout import BoxLayout  
from kivy.uix.screenmanager import Screen  
from kivy.uix.recycleview.layout import LayoutSelectionBehavior  
from kivy.uix.recycleview.views import RecycleDataViewBehavior  
from kivy.properties import BooleanProperty  
from kivy.uix.recycleboxlayout import RecycleBoxLayout  
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import FocusBehavior  
from kivy.uix.recycleview import RecycleView  
from kivy.clock import Clock  
from kivy.lang import Builder  
from kivy.uix.popup import Popup
import os, csv
from datetime import datetime, timedelta
from pathlib import Path
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from kivy.uix.checkbox import CheckBox
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from kivy.uix.spinner import Spinner
from pymongo import MongoClient
from kivy.uix.boxlayout import BoxLayout as BoxLayoutBase
import certifi
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from kivy.uix.textinput import TextInput  
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import ListProperty
import re
import platform
import subprocess
# Conexión a MongoDB
def conectar_mongo():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Inrema']
        return db['operadores']  # Colección 'operadores'
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

Builder.load_file('admin/admin.kv')  
  
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):  
    touch_deselect_last = BooleanProperty(True)  
  
  



            
class AdminRV(RecycleView):  
    
    def __init__(self, **kwargs):  
        super(AdminRV, self).__init__(**kwargs)  
        self.data = []  
  
    def agregar_datos(self, datos):  
        for dato in datos:  
            dato['seleccionado'] = False  
            self.data.append(dato)  
        self.refresh_from_data()  
  
    def dato_seleccionado(self):  
        indice = -1  
        for i in range(len(self.data)):  
            if self.data[i]['seleccionado']:  
                indice = i  
                break  
        return indice  



class UsuarioPopup(Popup):
    def __init__(self, _agregar_callback, **kwargs):  
        super(UsuarioPopup, self).__init__(**kwargs)  
        self.agregar_usuario = _agregar_callback
        self.nivel_seleccionado = "1" 

    def abrir(self, agregar, usuario=None):
        if agregar:
            self.ids.usuario_info_1.text = 'Agregar Usuario Nuevo'
            self.ids.usuario_username.disabled = False
            # Restablecer a nivel 1 por defecto
            self.ids.radio_nivel_1.active = True
            self.ids.radio_nivel_2.active = False
            self.ids.radio_nivel_3.active = False
            self.nivel_seleccionado = "1"
        else:
            self.ids.usuario_info_1.text = 'Modificar Usuario'
            self.ids.usuario_username.text = usuario['username']
            self.ids.usuario_username.disabled = True
            self.ids.usuario_nombre.text = usuario['nombre']
            self.ids.usuario_password.text = usuario['password']

            # 🔑 Leer el nivel del usuario y marcar el radio correcto
            nivel_actual = str(usuario.get('nivel', '1'))  # Asegurar que sea string
            self.nivel_seleccionado = nivel_actual

            # Desmarcar todos primero
            self.ids.radio_nivel_1.active = False
            self.ids.radio_nivel_2.active = False
            self.ids.radio_nivel_3.active = False

            # Marcar el correcto
            if nivel_actual == '1':
                self.ids.radio_nivel_1.active = True
            elif nivel_actual == '2':
                self.ids.radio_nivel_2.active = True
            elif nivel_actual == '3':
                self.ids.radio_nivel_3.active = True

        self.open()

    def on_radio_change(self, nivel):
        self.nivel_seleccionado = nivel
        
    def verificar(self, usuario_username, usuario_nombre, usuario_password):
        alert1 = 'Falta '
        validado = {}

        if not usuario_username:
            alert1 += 'Username. '
            validado['username'] = False
        else:
            validado['username'] = usuario_username

        if not usuario_nombre:
            alert1 += 'Nombre.'
            validado['nombre'] = False
        else:
            validado['nombre'] = usuario_nombre.lower()

        if not usuario_password:
            alert1 += 'Password. '
            validado['password'] = False
        else:
            validado['password'] = usuario_password

        # Añadir nivel al validado
        validado['nivel'] = self.nivel_seleccionado

        valores = list(validado.values())

        if False in valores:
            self.ids.no_valid_notif.text = alert1
        else:
            self.ids.no_valid_notif.text = ''
            # Añadir tipo según nivel (opcional)
            if self.nivel_seleccionado == '1':
                validado['tipo'] = 'usuario'
            elif self.nivel_seleccionado == '2':
                validado['tipo'] = 'operador'
            else:
                validado['tipo'] = 'admin'

            self.agregar_usuario(True, validado)
            self.dismiss()
            

            
class SelectableUsersLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_nombre'].text = data.get('nombre', 'N/A')
        self.ids['_username'].text = data.get('username', 'N/A')
        self.ids['_contraseña'].text = data.get('password', 'N/A')
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
class VistaUsers(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Aseguramos que la carga se haga después de que KV cargue los widgets
        Clock.schedule_once(self.cargar_usuarios, 0.1)

    def cargar_usuarios(self, dt=None):
        """Carga los usuarios desde MongoDB Inrema -> colección 'users'"""
        try:
            # 🔐 Conexión a MongoDB Atlas o servidor remoto (usa tu cadena de conexión)
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['Inrema']
            self.collection = self.db['users']      # Colección

            # Obtener todos los usuarios
            usuarios = list(self.collection.find({}))

            # Limpiar datos anteriores
            self.ids.rv_usuarios.data = []

            # Preparar datos para el RecycleView
            usuarios_data = []
            for usuario in usuarios:
                # ✅ Incluir 'nivel' y 'tipo' si existen, o asignar valores por defecto
                usuarios_data.append({
                    'nombre': usuario.get('nombre', 'N/A'),
                    'username': usuario.get('username', 'N/A'),
                    'password': usuario.get('password', '******'),
                    'nivel': str(usuario.get('nivel', '1')),      # ← Añadido
                    'tipo': usuario.get('tipo', 'usuario')        # ← Opcional, pero útil
                })

            # 🖨️ Imprimir los datos antes de agregarlos al RecycleView
            print("📋 Datos de usuarios obtenidos:")
            for u in usuarios_data:
                print(u)

            # Agregar datos al RecycleView
            self.ids.rv_usuarios.agregar_datos(usuarios_data)  # Cerrar conexión
            print(f"✅ Cargados {len(usuarios_data)} usuarios desde MongoDB.")

        except Exception as e:
            print(f"❌ Error al conectar a MongoDB o cargar usuarios: {e}")
            self.ids.rv_usuarios.data = []
            # self.ids.notificacion.text = "Error al cargar usuarios"

    def agregar_usuario(self, agregar=False, validado=None):
        print("hekko")

        if agregar:
            try:
                client = MongoClient('mongodb://localhost:27017/')
                db = client['Inrema']
                coleccion = db['users']

                # Insertar el usuario validado en MongoDB
                coleccion.insert_one(validado)

                # Actualizar la vista en el RecycleView
                self.ids.rv_usuarios.data.append(validado)
                self.ids.rv_usuarios.refresh_from_data()

                client.close()
                print("✅ Usuario agregado correctamente a MongoDB.")

            except Exception as e:
                print(f"❌ Error al agregar usuario a MongoDB: {e}")

        else:
            popup = UsuarioPopup(self.agregar_usuario)
            popup.abrir(True)


    def modificar_usuario(self, modificar=False, validado=None):
        if modificar and validado:
            try:
                # Conexión a MongoDB
                client = MongoClient('mongodb://localhost:27017/')
                db = client['Inrema']
                coleccion = db['users']

                # Validar que los campos existen antes de actualizar
                campos_actualizar = {}
                for campo in ['nombre', 'username','password']:
                    if campo in validado:
                        campos_actualizar[campo] = validado[campo]

                if campos_actualizar:
                    resultado = coleccion.update_one(
                        {'username': validado['username']},
                        {'$set': campos_actualizar}
                    )

                    if resultado.modified_count > 0:
                        print(f"✅ Usuario '{validado['username']}' actualizado en MongoDB")
                    elif resultado.matched_count > 0:
                        print(f"⚠️ Usuario encontrado pero sin cambios (datos iguales)")
                    else:
                        print(f"❌ No se encontró el usuario '{validado['username']}'")

                    # Actualizar en la interfaz
                    for item in self.ids.rv_usuarios.data:
                        if item['username'] == validado['username']:
                            item.update(campos_actualizar)
                            break

                    self.ids.rv_usuarios.refresh_from_data()
                else:
                    print("⚠️ No hay campos válidos para actualizar")

                client.close()

            except Exception as e:
                print(f"❌ Error al modificar usuario: {e}")

        else:
            # Modo edición: abrir popup con usuario seleccionado
            indice = self.ids.rv_usuarios.dato_seleccionado()
            if indice >= 0:
                usuario = self.ids.rv_usuarios.data[indice]
                popup = UsuarioPopup(self.modificar_usuario)
                popup.abrir(False, usuario)
            else:
                print("❌ No hay ningún usuario seleccionado para modificar")

                

    def eliminar_usuario(self):
        print("Botón: Eliminar Usuario")
        
        # Obtener el índice del usuario seleccionado
        indice = self.ids.rv_usuarios.dato_seleccionado()
        
        if indice >= 0:
            usuario = self.ids.rv_usuarios.data[indice]
            username = usuario['username']  # Clave para buscar en MongoDB

            try:
                # 🔐 Conexión a MongoDB
                client = MongoClient('mongodb://localhost:27017/')
                db = client['Inrema']
                coleccion = db['users']

                # 🗑️ Eliminar de la base de datos
                resultado = coleccion.delete_one({'username': username})

                if resultado.deleted_count > 0:
                    print(f"✅ Usuario '{username}' eliminado de MongoDB")
                else:
                    print(f"❌ No se encontró el usuario '{username}' en la base de datos")

                # ✅ Eliminar de la interfaz
                self.ids.rv_usuarios.data.pop(indice)
                self.ids.rv_usuarios.refresh_from_data()

                client.close()

            except Exception as e:
                print(f"❌ Error al eliminar usuario de MongoDB: {e}")
        else:
            print("❌ No hay ningún usuario seleccionado para eliminar")
    def filtrar_usuarios(self, texto):
        """Filtra los usuarios por nombre o username"""
        if not texto.strip():
            # Si está vacío, recarga todos
            self.cargar_usuarios(None)
            return

        texto = texto.lower().strip()
        datos_filtrados = []
        for item in self.ids.rv_usuarios.data:
            if (texto in item['nombre'].lower()) or (texto in item['username'].lower()):
                datos_filtrados.append(item)

        self.ids.rv_usuarios.data = datos_filtrados
        self.ids.rv_usuarios.refresh_from_data()



class VistaFichas(Screen):
    
    tipos_disponibles = ListProperty(["Todas"])  # Correcto: propiedad observable de la clase
    fichas_originales = []  # Opcional: también puedes usar una propiedad normal

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_nivel = None
        # Carga los datos después de que el .kv haya cargado los widgets
        Clock.schedule_once(self.cargar_fichas, 0.1)
      
    def valor_nivel(self, nivel):
        print(f"Nivel: {nivel + 15}")
        pass
    def actualizar_boton_segun_nivel(self, nivel):
        """Llama a este método desde AdminWindow cuando cambia el usuario"""
        self.usuario_nivel = nivel
        if hasattr(self.ids, 'boton_agregar'):
            self.ids.boton_agregar.disabled = (nivel == 1)
            self.ids.boton_eliminar.disabled = (nivel == 1)  # Desactivado si nivel es 1
            print(f"🔧 Botón actualizado: nivel {nivel}, disabled = {nivel == 1}")
            self.valor_nivel(nivel)
            
            
            

    def cargar_fichas(self, dt=None):
        """Carga las fichas desde MongoDB y actualiza el dropdown de tipos"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['fichas']

            # Obtener todas las fichas
            fichas = list(collection.find({}).sort("numero_ficha", -1))

            # Extraer tipos únicos
            tipos = set()
            fichas_data = []
            for ficha in fichas:
                tipo = ficha.get('tipo_ficha', 'N/A').title()
                tipos.add(tipo)
                cliente = ficha.get('cliente', {})
                fichas_data.append({
                    '_id': f"#{ficha.get('numero_ficha', 'N/A')}",
                    '_nombre': cliente.get('nombre', 'N/A'),
                    '_tipo': tipo,
                    '_fecha': cliente.get('fecha_registro', 'N/A'),
                    '_estado': ficha.get('estado', 'N/A').capitalize(),
                    'seleccionado': False
                })

            # Guardar copia original para filtrado
            self.fichas_originales = fichas_data

            # Actualizar dropdown: "Todas" + tipos únicos ordenados
            self.tipos_disponibles = ["Todas"] + sorted(tipos)

            # Mostrar todas al inicio
            self.ids.rv_fichas.data = fichas_data
            self.ids.rv_fichas.refresh_from_data()

            client.close()
            print(f"✅ Cargadas {len(fichas_data)} fichas y {len(tipos)} tipos.")

        except Exception as e:
            print(f"❌ Error al cargar fichas: {e}")
            self.ids.rv_fichas.data = []
            self.tipos_disponibles = ["Todas"]
            

    def filtrar_combinado(self):
        """Filtra las fichas combinando tipo, ID, nombre del cliente y rango de fechas"""
        if not hasattr(self, 'fichas_originales') or not self.fichas_originales:
            return

        tipo_seleccionado = self.ids.filtro_tipo.text
        id_texto = self.ids.filtro_id.text.strip().lower()
        cliente_texto = self.ids.filtro_cliente.text.strip().lower()
        fecha_desde_str = self.ids.filtro_fecha_desde.text.strip()
        fecha_hasta_str = self.ids.filtro_fecha_hasta.text.strip()

        # Función auxiliar para convertir 'dd/mm/yyyy' a objeto datetime
        def parse_fecha(fecha_str):
            if not fecha_str:
                return None
            try:
                return datetime.strptime(fecha_str, "%d/%m/%Y")
            except ValueError:
                return None

        fecha_desde = parse_fecha(fecha_desde_str)
        fecha_hasta = parse_fecha(fecha_hasta_str)

        filtradas = []
        for ficha in self.fichas_originales:
            # Filtro por tipo
            if tipo_seleccionado != "Todas" and ficha['_tipo'] != tipo_seleccionado:
                continue

            # Filtro por ID
            id_ficha = ficha['_id'].lower()
            if id_texto and id_texto not in id_ficha:
                continue

            # Filtro por nombre del cliente
            nombre_cliente = ficha['_nombre'].lower()
            if cliente_texto and cliente_texto not in nombre_cliente:
                continue

            # Filtro por rango de fechas
            fecha_ficha_str = ficha['_fecha']
            fecha_ficha = parse_fecha(fecha_ficha_str)
            if fecha_ficha is None:
                # Si la fecha de la ficha no es válida, la excluimos si hay filtros de fecha
                if fecha_desde or fecha_hasta:
                    continue
            else:
                if fecha_desde and fecha_ficha < fecha_desde:
                    continue
                if fecha_hasta and fecha_ficha > fecha_hasta:
                    continue

            filtradas.append(ficha)

        self.ids.rv_fichas.data = filtradas
        self.ids.rv_fichas.refresh_from_data()
            
    def agregar_ficha(self):
        """Abre un popup con opciones para el tipo de ficha"""
        def on_tipo_seleccionado(tipo):
            print(f"✅ Se seleccionó: Ficha de {tipo.title()}")
            # Aquí puedes llamar a una función específica
            if tipo == 'reparacion':
                self.crear_ficha_reparacion()
            elif tipo == 'mantenimiento':
                self.crear_ficha_mantenimiento()

        popup = OpcionesFichaPopup(nivel=self.usuario_nivel, callback=None)
        popup.open()
    def modificar_ficha(self):
        indice = self.ids.rv_fichas.dato_seleccionado()

        if indice < 0:
            # ✅ Mostrar mensaje al usuario y salir
            print(" No se ha seleccionado ninguna ficha para modificar.")
            # Opcional: mostrar un popup o mensaje en pantalla
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.uix.boxlayout import BoxLayout

            contenido = BoxLayout(orientation='vertical', padding=10, spacing=10)
            contenido.add_widget(Label(text=" Seleccione una ficha\nde la lista para modificar."))
            btn = Button(text="Aceptar", size_hint_y=None, height=40)
            contenido.add_widget(btn)

            popup = Popup(
                title="Ninguna ficha seleccionada",
                content=contenido,
                size_hint=(0.3, 0.3),
                auto_dismiss=True
            )
            btn.bind(on_release=popup.dismiss)
            popup.open()
            return  # ← Salir sin hacer nada más

        # ✅ Si llegamos aquí, hay una ficha seleccionada
        ficha = self.ids.rv_fichas.data[indice]
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['fichas']
            numero_ficha = int(ficha['_id'][1:])  # Quita el '#'
            ficha_completa = collection.find_one({"numero_ficha": numero_ficha})

            if not ficha_completa:
                print("❌ Ficha no encontrada en la base de datos.")
                return

            tipo_ficha = ficha_completa.get('tipo_ficha', '').lower()
            if tipo_ficha == 'torno':
                popup = FichaTornoModificar(
                    ficha_datos=ficha_completa,
                    callback_guardado=self.actualizar_ficha_en_tabla,
                    nivel=self.usuario_nivel  # ← AQUÍ
                )
            else:
                popup = FichaRectificadoraModificar(
                    ficha_datos=ficha_completa,
                    callback_guardado=self.actualizar_ficha_en_tabla,
                    nivel=self.usuario_nivel )
            popup.open()
            client.close()

        except Exception as e:
            print(f"❌ Error al cargar ficha: {e}")
            # Opcional: mostrar error en popup
            

    def eliminar_ficha(self):
        indice = self.ids.rv_fichas.dato_seleccionado()
        if indice < 0:
            print("❌ Seleccione una ficha para eliminar.")
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.uix.boxlayout import BoxLayout
            contenido = BoxLayout(orientation='vertical', padding=10, spacing=10)
            contenido.add_widget(Label(text="Seleccione una ficha de la lista para eliminar."))
            btn = Button(text="Aceptar", size_hint_y=None, height=40)
            contenido.add_widget(btn)
            popup = Popup(title="Ninguna ficha seleccionada", content=contenido, size_hint=(0.3, 0.3))
            btn.bind(on_release=popup.dismiss)
            popup.open()
            return

        # ✅ Obtener el número de ficha DIRECTAMENTE de rv_fichas
        ficha_seleccionada = self.ids.rv_fichas.data[indice]
        numero_ficha_str = ficha_seleccionada['_id']  # Ej: "#105"
        try:
            numero_ficha = int(numero_ficha_str[1:])  # Quita el '#'
        except (ValueError, IndexError):
            print(f"❌ Formato inválido de ID de ficha: {numero_ficha_str}")
            return

        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            col_registro_rep = db['registro_repuestos']
            col_registro_trab = db['registro_trabajos']
            col_fichas = db['fichas']
            col_inventario = db['Repuestos']

            print(f"🗑️ Eliminando ficha completa #{numero_ficha}...")

            # 1. Devolver stock de todos los repuestos usados en esta ficha
            repuestos_ficha = list(col_registro_rep.find({"numero_ficha": numero_ficha}))
            for item in repuestos_ficha:
                codigo = item.get('codigo')
                cantidad = item.get('cantidad', 0)
                if codigo is not None and cantidad > 0:
                    # 👇 Convertir código a int para coincidir con el tipo en 'Repuestos'
                    try:
                        codigo_int = int(codigo) if isinstance(codigo, str) else codigo
                    except (ValueError, TypeError):
                        print(f"⚠️ Código de repuesto inválido: {codigo}")
                        continue

                    # Buscar y actualizar usando el tipo correcto
                    inventario_doc = col_inventario.find_one({"codigo": codigo_int})
                    if inventario_doc:
                        # ✅ Usar $inc para mayor seguridad y atomicidad
                        col_inventario.update_one(
                            {"codigo": codigo_int},
                            {"$inc": {"cantidad": cantidad}}
                        )
                        print(f"📦 Devolución: +{cantidad} de '{codigo}' → stock incrementado")
                    else:
                        print(f"⚠️ Repuesto con código '{codigo}' no encontrado en inventario.")

            # 2. Eliminar registros relacionados
            col_registro_rep.delete_many({"numero_ficha": numero_ficha})
            col_registro_trab.delete_many({"numero_ficha": numero_ficha})
            col_fichas.delete_one({"numero_ficha": numero_ficha})

            print(f"✅ Ficha #{numero_ficha} y sus registros eliminados.")

            # 3. Actualizar la vista
            self.cargar_fichas()

            client.close()
            if hasattr(self.ids, 'mensaje_estado'):
                self.ids.mensaje_estado.text = f"✅ Ficha #{numero_ficha} eliminada y stock reabastecido."

        except Exception as e:
            print(f"❌ Error al eliminar ficha completa: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self.ids, 'mensaje_estado'):
                self.ids.mensaje_estado.text = "❌ Error al eliminar la ficha."
            if 'client' in locals():
                client.close()


                
    def filtrar_fichas(self, texto):
        """Filtra las fichas por ID (#105) o por nombre del cliente"""
        texto = texto.strip().lower()
        if not texto:
            # Si no hay texto, recarga todas las fichas
            self.cargar_fichas()
            return

        # Obtener datos originales (deben estar guardados)
        if not hasattr(self, 'fichas_originales'):
            # Primera carga: guarda una copia
            self.fichas_originales = self.ids.rv_fichas.data.copy()

        # Filtrar
        fichas_filtradas = []
        for ficha in self.fichas_originales:
            id_match = texto in ficha['_id'].lower()
            nombre_match = texto in ficha['_nombre'].lower()
            if id_match or nombre_match:
                fichas_filtradas.append(ficha)

        # Actualizar RecycleView
        self.ids.rv_fichas.data = fichas_filtradas
        self.ids.rv_fichas.refresh_from_data()
        
    def actualizar_ficha_en_tabla(self, ficha_id, nuevos_datos):
        """Actualiza los datos en el RecycleView después de editar"""
        for item in self.ids.rv_fichas.data:
            if item['_id'] == ficha_id:
                item['_nombre'] = nuevos_datos['cliente']['nombre']
                item['_tipo'] = nuevos_datos['motor']['tipo'].title()
                item['_fecha'] = nuevos_datos['cliente']['fecha_registro']
                break
        self.ids.rv_fichas.refresh_from_data()
        print(f"✅ Tabla actualizada para ficha {ficha_id}")
        
    def agregar_nueva_ficha_a_tabla(self, nueva_ficha):
        """Agrega una nueva ficha al RecycleView sin recargar todo desde la BD"""
        try:
            cliente = nueva_ficha.get('cliente', {})
            nueva_fila = {
                '_id': f"#{nueva_ficha.get('numero_ficha', 'N/A')}",
                '_nombre': cliente.get('nombre', 'N/A'),
                '_tipo': nueva_ficha.get('tipo_ficha', 'N/A').title(),
                '_fecha': cliente.get('fecha_registro', 'N/A'),
                '_estado': nueva_ficha.get('estado', 'N/A').capitalize()
            }
            
            # Agregar al inicio de la lista (más reciente primero)
            self.ids.rv_fichas.data.insert(0, nueva_fila)
            
            # Actualizar la tabla original también (para filtros)
            if hasattr(self, 'fichas_originales'):
                self.fichas_originales.insert(0, nueva_fila)
            else:
                self.fichas_originales = self.ids.rv_fichas.data.copy()
            
            # Refrescar la vista
            self.ids.rv_fichas.refresh_from_data()
            
            print(f"✅ Nueva ficha #{nueva_ficha.get('numero_ficha')} agregada a la tabla")
            
        except Exception as e:
            print(f"❌ Error al agregar ficha a la tabla: {e}")
            
        
class SelectableFichaLabel(RecycleDataViewBehavior, BoxLayout):
    """
    Una fila en el RecycleView para la VistaFichas.
    Muestra: ID, Nombre, Tipo, Fecha, Estado.
    Permite selección.
    """
    # Propiedades para manejar selección
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los valores mostrados en cada celda."""
        self.index = index
        self.ids['_id'].text = data.get('_id', 'N/A')
        self.ids['_nombre'].text = data.get('_nombre', 'N/A')
        self.ids['_tipo'].text = data.get('_tipo', 'N/A')
        self.ids['_fecha'].text = data.get('_fecha', 'N/A')
        self.ids['_estado'].text = data.get('_estado', 'N/A')

        # Actualiza el fondo
        #self._actualizar_fondo()
        # Llama al método base
        return super().refresh_view_attrs(rv, index, data)


    def _actualizar_rect(self, instance, value):
        """Actualiza la posición y tamaño del rectángulo de fondo."""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        """Permite seleccionar la fila al hacer clic."""
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
        #self._actualizar_fondo()


class OpcionesFichaPopup(Popup):
    def __init__(self, callback=None, nivel=None, **kwargs):
        super().__init__(**kwargs)
        self.nivel = nivel 
        self.title = "Seleccionar Tipo de Ficha"
        self.size_hint = (0.25, 0.25)
        self.auto_dismiss = True
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Opción 1: Reparación
        btn_reparacion = Button(text="Ficha de Rectificación", size_hint_y=None, height=50)
        btn_reparacion.bind(on_release=lambda x: self.abrir_rectificadora())

        # Opción 2: Mantenimiento
        btn_mantenimiento = Button(text="Ficha de Torno", size_hint_y=None, height=50)
        btn_mantenimiento.bind(on_release=lambda x: self.abrir_torno())

        # Botón de cancelar
        btn_cancelar = Button(text="Cancelar", size_hint_y=None, height=50)
        btn_cancelar.bind(on_release=self.dismiss)

        # Añadir al layout
        layout.add_widget(btn_reparacion)
        layout.add_widget(btn_mantenimiento)
        layout.add_widget(btn_cancelar)

        self.content = layout

    def seleccionar(self, tipo):
        """Llama al callback con el tipo seleccionado y cierra el popup"""
        if self.callback:
            self.callback(tipo)
        self.dismiss()
    def abrir_torno(self):
            popup = FichaTorno(nivel= self.nivel)
            popup.open()
            self.dismiss()
            
    def abrir_rectificadora(self):
            popup = FichaRectificadora(nivel= self.nivel)
            popup.open()
            self.dismiss()
    
    
    

    
    
class CustomDropDown(DropDown):
    def __init__(self, cambiar_callback, admin_window, **kwargs):
        self._succ_cb = cambiar_callback
        self.admin_window = admin_window
        self.usuario_nivel = None
        super().__init__(**kwargs) 
        
    def vista(self, vista):
        if callable(self._succ_cb):
            self._succ_cb(True, vista)

    def salir2(self):
        if self.admin_window and hasattr(self.admin_window, 'salir'):
            self.admin_window.salir()  # ✅ Llama al salir() de la instancia real
        else:
            print("Error: admin_window no disponible")
        self.dismiss() 
        
    def a_operadores(self):
        if self.admin_window and hasattr(self.admin_window, 'operadores'):
            self.admin_window.operadores()  # ✅ Llama al salir() de la instancia real
        else:
            print("Error: admin_window no disponible")
        self.dismiss() 
        
    def ir_a_usuarios(self):
        # Usar el nombre exacto que está en el .kv
        self.admin_window.vista_manager.current = 'users'
        self.dismiss()
    def ir_a_fichas(self):
        # Usar el nombre exacto que está en el .kv
        self.admin_window.vista_manager.current = 'fichas'
        self.dismiss()
                

    def actualizar_visibilidad_por_nivel(self, nivel):
        # Ejemplo: ocultar "Usuarios" si nivel == 1
        if nivel == 1:
            self.ids.drop_usarios.disabled= True
            self.ids.drop_operadores.disabled= True
            self.ids.drop_inventario.disabled= False
            
        if nivel == 2:
            self.ids.drop_usarios.disabled= True
            self.ids.drop_inventario.disabled= True
            self.ids.drop_operadores.disabled= False

        if nivel == 3:
            self.ids.drop_usarios.disabled= False
            self.ids.drop_inventario.disabled= False
            self.ids.drop_operadores.disabled= False
          






class AdminWindow(BoxLayout):  
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        self.vista_actual = 'Agenda'  
        self.vista_manager = self.ids.vista_manager  

        # ✅ Pasa 'self' (la instancia actual) al dropdown
        self.dropdown = CustomDropDown(cambiar_callback=self.cambiar_vista, admin_window=self)
        
        self.ids.cambiar_vista.bind(on_release=self.dropdown.open)
        
        
            
    def cambiar_vista(self, cambio=False, vista=None):
        if cambio:
            self.vista_actual = vista
            self.vista_manager.current = self.vista_actual
            self.dropdown.dismiss()

    def salir(self):  
        # Asume que estás usando ScreenManager
        self.parent.parent.current = 'inventario'  
        print(str(self.parent.parent.current))
        
        
    def salirx(self):  
        self.parent.parent.current = 'signin'  
        
    def operadores(self):  
        # Asume que estás usando ScreenManager
        self.parent.parent.current = 'operadores'  

        
    def poner_usuario(self, usuario):
        """Guarda el usuario logueado y lo imprime en consola con todos sus datos"""

        print(f"🔒 Nivel:         {usuario.get('nivel', 'No especificado')}")

        # Guardar en la instancia para uso posterior
        self.usuario = usuario
        # Obtener el valor como cadena, luego convertirlo a int
        nivel_str = usuario.get('nivel', '1')  # Valor por defecto como cadena
        self.usuario_nivel = int(nivel_str)  # ←¡Conviértlo a entero!

        if hasattr(self, 'dropdown'):
            self.dropdown.actualizar_visibilidad_por_nivel(self.usuario_nivel)
        # Actualizar la pantalla de fichas según el nivel
        try:
            fichas_screen = self.vista_manager.get_screen('fichas')
            if hasattr(fichas_screen, 'actualizar_boton_segun_nivel'):
                fichas_screen.actualizar_boton_segun_nivel(self.usuario_nivel)
            else:
                # Si no existe el método, actualizamos manualmente el botón
                if hasattr(fichas_screen.ids, 'boton_agregar'):
                    fichas_screen.ids.boton_agregar.disabled = (self.usuario_nivel == 1)
                    fichas_screen.ids.boton_agregar.opacity = 0.5 if self.usuario_nivel == 1 else 1.0
        except Exception as e:
            print(f"⚠️  Error al actualizar botón de agregar ficha: {e}")
        
        print("✅ Sistema actualizado según nivel de usuario")
        print("="*60 + "\n")
        

def generar_pdf_trabajo(datos, filename="trabajo_detalle.pdf"):
    """
    Genera un PDF con los detalles del trabajo y la ficha asociada.
    """
    
    
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    base_folder = os.path.join(desktop, "Fichas")

    # Asegurarse de que el ID de ficha y trabajo sean strings
    id_ficha = str(datos['id_ficha'])
    id_trabajo = str(datos['id_trabajo'])

    # --- 2. Crear rutas ---
    ficha_folder = os.path.join(base_folder, f"Ficha Nº{id_ficha}")
    pdf_filename = f"Trabajo Nº{id_trabajo}.pdf"
    filepath = os.path.join(ficha_folder, pdf_filename)

    # --- 3. Crear carpetas si no existen ---
    os.makedirs(ficha_folder, exist_ok=True)

    # --- 4. Generar el PDF ---
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # --- Título ---
    titulo=  Paragraph(f"<b>Ficha Nº {datos['id_ficha']}</b>", styles['Heading1'])
    elements.append(titulo)
    elements.append(Spacer(1, 0.2*inch))    
    
    subtitulo = Paragraph(f"<b>TRABAJO Nº {datos['id_trabajo']}</b>", styles['Heading1'])
    elements.append(subtitulo)
    elements.append(Spacer(1, 0.2*inch))

    # --- Datos de la Ficha ---
    data_ficha = [
        
        ["Cliente:", datos['cliente'], "Fecha", datos['fecha_registro']],
        ["modelo", '', "Tipo Motor:", datos['tipo_motor']],
    ]

    tabla_ficha = Table(data_ficha, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch], rowHeights=0.3*inch)
    tabla_ficha.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
        ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
    ]))
    elements.append(tabla_ficha)
    elements.append(Spacer(1, 0.2*inch))

    # --- Datos del Trabajo ---
    data_trabajo = [
        ["Trabajo:", datos['trabajo'], "Operador:", datos['operador']],
        ["Cantidad:", str(datos['cantidad_horas']), "Fecha Inicio:", datos['fecha_inicio']],
    ]

    tabla_trabajo = Table(data_trabajo, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch], rowHeights=0.3*inch)
    tabla_trabajo.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
        ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
    ]))
    elements.append(tabla_trabajo)
    elements.append(Spacer(1, 0.2*inch))

    # --- Observación ---
    elements.append(Paragraph(f"Observación: {datos['observacion']}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # --- Repuestos ---
    if datos['repuestos']:
        elements.append(Paragraph("Repuestos Utilizados:", styles['Normal']))
        data_repuestos = [["Código", "Nombre", "Cantidad"]]
        for rep in datos['repuestos']:
            data_repuestos.append([
                rep['codigo'],
                rep['nombre'],
                str(rep['cantidad']),

            ])

        tabla_repuestos = Table(data_repuestos, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1*inch])
        tabla_repuestos.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ]))
        elements.append(tabla_repuestos)

    # Construir PDF
    doc.build(elements)
    print(f"✅ PDF generado: {filename}")




class SelectableTrabajoRow(RecycleDataViewBehavior, BoxLayout):
    """Fila seleccionable para mostrar trabajos."""
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    # Campos que mostrará la fila
    id_trabajo = StringProperty('')
    trabajo = StringProperty('')
    operador = StringProperty('')
    fecha_inicio = StringProperty('')
    estado = StringProperty('')
    total_general = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los valores mostrados."""
        self.index = index
        self.id_trabajo = str(data.get('id_trabajo', ''))
        self.trabajo = data.get('trabajo', '')
        self.operador = data.get('operador', '')
        self.fecha_inicio = data.get('fecha_inicio', '')
        self.estado = data.get('estado', 'En proceso')
        self.total_general = f"{float(data.get('total_general', 0)):,.2f}"
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Maneja el clic para selección."""
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




class AutocompleteMarcaInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.dropdown = DropDown()
        self.bind(focus=self.on_focus)
        self.db_marcas = None
        self._connect_to_db()

    def _connect_to_db(self):
        """Conecta a MongoDB y guarda referencia a la colección MarcasMotores"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            self.db_marcas = db['MarcasMotores']
            print("✅ Conexión a MarcasMotores establecida")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            self.db_marcas = None

    def on_text(self, instance, value):
        """Filtrar y mostrar sugerencias cuando el usuario escribe"""
        self.dropdown.dismiss()
        if len(value) < 1 or self.db_marcas is None:  # ← Desde la primera letra
            return

        try:
            # Buscar en campo "marca" que comience con el texto (insensible a mayúsculas)
            regex = f"^{re.escape(value)}"
            results = self.db_marcas.find(
                {"nombre": {"$regex": regex, "$options": "i"}}
            ).limit(10)

            suggestions = []
            for doc in results:
                marca = doc.get("nombre", "").strip()
                if marca and marca not in suggestions:
                    suggestions.append(marca)

            if not suggestions:
                suggestions = ["No se encontraron resultados"]

            self.dropdown.clear_widgets()
            for suggestion in suggestions:
                btn = Button(text=suggestion, size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: self.select_suggestion(btn.text))
                self.dropdown.add_widget(btn)

            # Mostrar el dropdown después de que el layout se actualice
            Clock.schedule_once(lambda dt: self.dropdown.open(self), 0.1)

        except Exception as e:
            print(f"❌ Error al buscar en MarcasMotores: {e}")
            self.dropdown.clear_widgets()
            btn = Button(text="Error de conexión", size_hint_y=None, height=40)
            btn.bind(on_release=lambda x: self.dropdown.dismiss())
            self.dropdown.add_widget(btn)
            Clock.schedule_once(lambda dt: self.dropdown.open(self), 0.1)

    def on_focus(self, instance, value):
        """Abrir dropdown si hay texto cuando recibe foco"""
        if value and self.text:
            self.on_text(self, self.text)

    def select_suggestion(self, text):
        """Selecciona una sugerencia y la pone en el TextInput"""
        if text != "No se encontraron resultados" and "Error" not in text:
            self.text = text
        self.dropdown.dismiss()


class DropdownTextInput(TextInput):
    def __init__(self, **kwargs):
        self.dropdown = DropDown()
        super().__init__(**kwargs)
        self.multiline = False

        # Opciones fijas
        opciones = ["1CL", "2CL", "3CL", "4CL", "5CL", "6CL", "8CL", "12CL", "18CL"]

        # Crear botones en el dropdown
        for opcion in opciones:
            btn = Button(text=opcion, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.seleccionar(btn.text))
            self.dropdown.add_widget(btn)

        # Vincular eventos
        self.bind(focus=self.on_focus)

    def on_focus(self, instance, value):
        """Mostrar el dropdown cuando el TextInput recibe foco"""
        if value:  # Si tiene foco
            # Programar para abrir después de que el layout esté listo
            Clock.schedule_once(self.abrir_dropdown, 0.1)

    def abrir_dropdown(self, dt):
        self.dropdown.open(self)

    def seleccionar(self, text):
        """Selecciona una opción y cierra el dropdown"""
        self.text = text
        self.dropdown.dismiss()

    def on_touch_down(self, touch):
        """También abrir el dropdown al tocar (si no está enfocado)"""
        if self.collide_point(*touch.pos):
            if not self.focus:
                self.focus = True  # Esto activará on_focus
            return True
        return super().on_touch_down(touch)

class AutocompleteTextInput(TextInput):
    def __init__(self, marca_input, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.dropdown = DropDown()
        self.bind(focus=self.on_focus)
        self.db_motores = None
        self.marca_input = marca_input  # Referencia al TextInput de marca
        self._connect_to_db()

    def _connect_to_db(self):
        """Conecta a MongoDB y guarda referencia a la colección BDmotores"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            self.db_motores = db['BDmotores']  # ← Colección con marca, modelo, cilindraje
            print("✅ Conexión a BDmotores establecida")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")

    def on_text(self, instance, value):
        """No se usa más. Solo se activa al hacer clic."""
        pass  # Ignoramos este evento

    def on_focus(self, instance, value):
        """Abrir dropdown si tiene foco"""
        if value and self.text == "":
            self.mostrar_sugerencias()

    def mostrar_sugerencias(self):
        """Muestra las sugerencias basadas en la marca seleccionada"""
        self.dropdown.dismiss()
        if self.db_motores is None:
            return

        try:
            # Obtener la marca desde el campo 'marca'
            marca = self.marca_input.text.strip()
            if not marca:
                # Si no hay marca, no mostrar nada
                return

            # Buscar todos los modelos para esa marca
            results = self.db_motores.find({"marca": {"$regex": f"^{re.escape(marca)}", "$options": "i"}}).limit(10)

            suggestions = []
            for doc in results:
                modelo = doc.get("modelo", "").strip()
                cilindraje = doc.get("cilindraje", "").strip()
                if modelo and modelo not in suggestions:
                    # Mostrar como: "Modelo - Cilindraje"
                    texto_sugerencia = f"{modelo} - {cilindraje}"
                    suggestions.append(texto_sugerencia)

            if not suggestions:
                suggestions = ["No se encontraron modelos para esta marca"]

            self.dropdown.clear_widgets()
            for suggestion in suggestions:
                btn = Button(text=suggestion, size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: self.select_suggestion(btn.text))
                self.dropdown.add_widget(btn)

            # Mostrar el dropdown después de que el layout se actualice
            Clock.schedule_once(lambda dt: self.dropdown.open(self), 0.1)

        except Exception as e:
            print(f"❌ Error al buscar en BDmotores: {e}")
            self.dropdown.clear_widgets()
            btn = Button(text="Error de conexión", size_hint_y=None, height=40)
            btn.bind(on_release=lambda x: self.dropdown.dismiss())
            self.dropdown.add_widget(btn)
            Clock.schedule_once(lambda dt: self.dropdown.open(self), 0.1)

    def select_suggestion(self, text):
        """Selecciona una sugerencia y la pone en el TextInput"""
        if text != "No se encontraron modelos para esta marca" and "Error" not in text:
            self.text = text.split(" - ")[0]  # Solo el modelo
        self.dropdown.dismiss()

def obtener_trabajos_operador(nombre_operador):
    """Devuelve una lista de nombres de trabajos para el operador dado."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Inrema']
        col_operadores = db['operadores']  # Asume que se llama así
        operador = col_operadores.find_one({"nombre": nombre_operador})
        if not operador or 'trabajos' not in operador:
            return []
        # Extraer solo los valores del objeto 'trabajos'
        trabajos_lista = list(operador['trabajos'].values())
        return trabajos_lista
    except Exception as e:
        print(f"❌ Error al obtener trabajos del operador '{nombre_operador}': {e}")
        return []
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.metrics import dp

class TrabajosOperadorPopup(Popup):
    def __init__(self, operador_nombre, callback, trabajos_preseleccionados=None, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Seleccionar Trabajos - {operador_nombre}"
        self.size_hint = (0.7, 0.6)
        self.operador_nombre = operador_nombre
        self.callback = callback
        self.trabajos_preseleccionados = set(trabajos_preseleccionados or [])

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        scroll = ScrollView()
        self.check_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.check_layout.bind(minimum_height=self.check_layout.setter('height'))

        # Cargar trabajos del operador (lista de strings)
        trabajos_db = obtener_trabajos_operador(operador_nombre) or []
        self.checks = []

        for trabajo_nombre in trabajos_db:
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
            cb = CheckBox(size_hint_x=None, width=dp(40))
            label = Label(
                text=trabajo_nombre,
                halign='left',
                valign='middle',
                size_hint_x=0.8,
                color=(1, 1, 1, 1)
            )
            label.bind(size=label.setter('text_size'))

            # ✅ Si el trabajo ya está en el cuerpo, cambiar el fondo del Label
            if trabajo_nombre in self.trabajos_preseleccionados:
                with label.canvas.before:
                    Color(0.2, 0.4, 0.8, 0.4)  # Azul semitransparente
                    rect = Rectangle(size=label.size, pos=label.pos)
                label._bg_rect = rect
                label.bind(pos=lambda inst, val, r=rect: setattr(r, 'pos', val),
                           size=lambda inst, val, r=rect: setattr(r, 'size', val))

            row.add_widget(cb)
            row.add_widget(label)
            self.check_layout.add_widget(row)
            self.checks.append((cb, trabajo_nombre))

        # ✅ Añadir la opción de "trabajo en blanco"
        row_blank = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
        self.cb_blank = CheckBox(size_hint_x=None, width=dp(40))
        label_blank = Label(
            text="(Agregar trabajo personalizado)",
            halign='left',
            valign='middle',
            size_hint_x=0.8,
            color=(0.8, 0.8, 0.8, 1)
        )
        label_blank.bind(size=label_blank.setter('text_size'))
        row_blank.add_widget(self.cb_blank)
        row_blank.add_widget(label_blank)
        self.check_layout.add_widget(row_blank)

        scroll.add_widget(self.check_layout)
        main_layout.add_widget(scroll)

        # Botones
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        btn_cancelar = Button(text='Cancelar')
        btn_agregar = Button(text='Agregar', background_color=(0.2, 0.7, 0.2, 1))

        btn_cancelar.bind(on_press=self.dismiss)
        btn_agregar.bind(on_press=self._on_agregar)

        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_agregar)
        main_layout.add_widget(btn_layout)

        self.content = main_layout

    def _on_agregar(self, instance):
        seleccionados = []
        for cb, trabajo_nombre in self.checks:
            if cb.active:
                seleccionados.append(trabajo_nombre)
        self.callback(seleccionados, self.cb_blank.active)
        self.dismiss()

class FichaRectificadora(Popup):
    def __init__(self, nivel=None, **kwargs):
        self.nivel_usuario = nivel
        super().__init__(**kwargs)
        Clock.schedule_once(self.inicializar_popup, 0)
        
        if self.nivel_usuario ==1 :
            self.ids.popup_operadores.disabled = True
            self.ids.generador_ficha.disabled = True
            self.ids.nota_entrega.disabled = True


            


    def inicializar_popup(self, dt):
        self.cargar_numero_ficha()
        self.configurar_autocompletado()


    def configurar_autocompletado(self):
        """Reemplaza los TextInput 'marca' y 'motor' con autocompletado, manteniendo size_hint_x"""
        try:
            
            # === AUTOCOMPLETADO PARA MARCA ===
            marca_input = self.ids.marca
            parent_marca = marca_input.parent
            index_marca = parent_marca.children.index(marca_input)

            # Guardar propiedades clave del widget original
            size_hint_x_marca = marca_input.size_hint_x
            height_marca = marca_input.height

            parent_marca.remove_widget(marca_input)

            auto_marca = AutocompleteMarcaInput(
                hint_text="Buscar marca...",
                size_hint_x=size_hint_x_marca,
                height=height_marca,
                size_hint_y=None  # Para que height sea respetado
            )
            parent_marca.add_widget(auto_marca, index_marca)
            self.ids.marca = auto_marca
            
            
            # === AUTOCOMPLETADO PARA MOTOR ===
            motor_input = self.ids.motor
            parent_motor = motor_input.parent
            index_motor = parent_motor.children.index(motor_input)

            # Guardar tamaño original
            size_hint_x = motor_input.size_hint_x
            height = motor_input.height

            parent_motor.remove_widget(motor_input)

            auto_motor = AutocompleteTextInput(
                marca_input=auto_marca,  # ← Aquí pasamos la referencia
                hint_text="Buscar modelo...",
                size_hint_x=size_hint_x,
                height=height,
                size_hint_y=None
            )
            parent_motor.add_widget(auto_motor, index_motor)
            self.ids.motor = auto_motor

                
                
            # === DROPDOWN PARA CILINDRAJE ===
            cilindraje_input = self.ids.Cilindraje
            parent_cil = cilindraje_input.parent
            index_cil = parent_cil.children.index(cilindraje_input)
            
            size_hint_x = cilindraje_input.size_hint_x
            height = cilindraje_input.height

            parent_cil.remove_widget(cilindraje_input)

            dropdown_cil = DropdownTextInput(
                hint_text=cilindraje_input.hint_text,
                size_hint_x=size_hint_x,
                height=height,
                size_hint_y=None
            )
            parent_cil.add_widget(dropdown_cil, index_cil)
            self.ids.Cilindraje = dropdown_cil

        except Exception as e:
            print(f"❌ Error al configurar autocompletado: {e}")
            self.ids.mensaje_estado.text = "Error al cargar autocompletado"
        

    def abrir_popup_clientes(self):
        """Abre el popup para seleccionar un cliente existente"""
        def on_cliente_seleccionado(cliente):
            # Extraer tipo de RIF (ej: "V-", "J-", etc.)
            rif_completo = cliente.get('rif', '')
            if len(rif_completo) >= 2 and rif_completo[1] == '-':
                tipo_rif = rif_completo[:2]
                numero_rif = rif_completo[2:]
            else:
                tipo_rif = 'V-'
                numero_rif = rif_completo

            # Llenar los campos
            self.ids.tipo_rif.text = tipo_rif
            self.ids.nuevo_rif.text = numero_rif
            self.ids.nuevo_cliente.text = cliente.get('nombre', '')
            self.ids.nuevo_telefono.text = cliente.get('telefono', '')
            self.ids.nueva_direccion.text = cliente.get('direccion', '')

            self.ids.mensaje_estado.text = f"✅ Cliente '{cliente.get('nombre', '')}' cargado."

        popup = ClientesPopup(callback=on_cliente_seleccionado)
        popup.open()
        
            
    def guardar_nuevo_cliente(self):
        """Guarda el cliente en la colección 'clientes'"""
        try:
            tipo_rif = self.ids.tipo_rif.text
            nuevo_rif = self.ids.nuevo_rif.text.strip()
            nombre = self.ids.nuevo_cliente.text.strip()
            telefono = self.ids.nuevo_telefono.text.strip()
            direccion = self.ids.nueva_direccion.text.strip()

            if not nuevo_rif:
                self.ids.mensaje_estado.text = "Por favor, ingrese el RIF."
                return
            if not nombre:
                self.ids.mensaje_estado.text = "Por favor, ingrese el nombre del cliente."
                return

            rif_completo = tipo_rif + nuevo_rif

            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['clientes']

            if collection.find_one({"rif": rif_completo}):
                self.ids.mensaje_estado.text = "Cliente con este RIF ya existe."
                client.close()
                return

            nuevo_cliente = {
                "rif": rif_completo,
                "nombre": nombre,
                "telefono": telefono,
                "direccion": direccion
            }

            collection.insert_one(nuevo_cliente)
            client.close()

            self.ids.mensaje_estado.text = f"✅ Cliente '{nombre}' guardado correctamente."

        except Exception as e:
            print(f"❌ Error al guardar cliente: {e}")
            self.ids.mensaje_estado.text = "Error al conectar con la base de datos."
    def cargar_numero_ficha(self):
        """Genera el siguiente número de ficha basado en el máximo existente + 1"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            col_fichas = db['fichas']
            
            # Buscar el número de ficha más alto en la base de datos
            ficha_maxima = col_fichas.find_one(
                {},
                sort=[("numero_ficha", -1)]  # Ordenar por numero_ficha descendente
            )
            
            # Si existe al menos una ficha, tomar el siguiente número
            if ficha_maxima and 'numero_ficha' in ficha_maxima:
                self.numero_ficha = ficha_maxima['numero_ficha'] + 1
            else:
                # Si no hay fichas, empezar desde 1
                self.numero_ficha = 1
            
            self.title = f'Ficha Rectificadora #{self.numero_ficha}'
            client.close()
            
            print(f"✅ Número de ficha asignado: {self.numero_ficha}")
            
        except Exception as e:
            print(f"❌ Error al obtener número de ficha: {e}")
            self.title = "Ficha Rectificadora #?"
            self.numero_ficha = 1  # Valor por defecto
        self.ids.nueva_fecha.text = datetime.now().strftime('%d/%m/%Y')
        

    def guardar_nueva_ficha(self):
        """Guarda o actualiza la ficha en MongoDB según el modo (nueva o modificación)"""
        motor_nombre = self.ids.motor.text.strip()
        if not motor_nombre:
            self.ids.mensaje_estado.text = "Por favor, seleccione o escriba un motor."
            return

        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            col_usuarios = db['usuarios']
            col_fichas = db['fichas']

            # === DATOS DEL CLIENTE ===
            tipo_rif = self.ids.tipo_rif.text
            nuevo_rif = self.ids.nuevo_rif.text.strip()
            nombre = self.ids.nuevo_cliente.text.strip()
            telefono = self.ids.nuevo_telefono.text.strip()
            direccion = self.ids.nueva_direccion.text.strip()
            fecha = self.ids.nueva_fecha.text

            if not nuevo_rif or not nombre:
                self.ids.mensaje_estado.text = "RIF y Nombre son obligatorios."
                client.close()
                return

            rif_completo = tipo_rif + nuevo_rif

            # Guardar cliente en 'usuarios' si no existe (solo en modo nueva ficha)
            if not getattr(self, 'es_modificacion', False):
                cliente_existente = col_usuarios.find_one({"rif": rif_completo})
                if not cliente_existente:
                    col_usuarios.insert_one({
                        "rif": rif_completo,
                        "nombre": nombre,
                        "telefono": telefono,
                        "direccion": direccion,
                        "tipo": "cliente"
                    })
                    print(f"✅ Cliente '{nombre}' guardado en 'usuarios'")

            # === DATOS DEL MOTOR ===
            tipo_motor = self.ids.tipo_motor.text
            serial_motor = self.ids.serial_motor.text.strip()
            marca_motor = self.ids.marca.text.strip()
            cilindraje_motor = self.ids.Cilindraje.text.strip()

            if tipo_motor == 'Seleccionar':
                self.ids.mensaje_estado.text = "Seleccione el tipo de motor."
                client.close()
                return
            if not motor_nombre or motor_nombre == 'Seleccionar Motor':
                self.ids.mensaje_estado.text = "Seleccione un motor válido."
                client.close()
                return

            # === PARTES RECIBIDAS ===
            partes_recibidas = []
            nombres_partes = [
                'ciguenal', 'bujias', 'polea', 'Multiple', 'bloque', 'bodis',
                'volante', 'Carter', 'tapas_de_bancada', 'puntas', 'engranajes', 'camisas',
                'arbol_de_leva', 'esparragos', 'balancines', 'camaras', 'tapa_valvulas', 'toma_de_agua',
                'valvulas_adm', 'bielas', 'chambers', 'valvulas_esc', 'tapas_de_vielas', 'bomba_de_aceite',
                'resortes', 'camarin', 'toma_de_agua2', 'cuñadas', 'pasador', 'base_de_agua'
            ]

            for i in range(1, 31):
                cantidad_id = f'cantidad_grid_{i}'
                if hasattr(self.ids, cantidad_id):
                    cantidad = getattr(self.ids, cantidad_id).text.strip()
                    nombre_parte = nombres_partes[i - 1] if i <= len(nombres_partes) else "Desconocida"
                    if cantidad and cantidad != '0':
                        partes_recibidas.append({"parte": nombre_parte, "cantidad": cantidad})

            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout:
                for widget in grid_layout.children:
                    if isinstance(widget, TextInput) and widget.hint_text == "Pieza":
                        idx = grid_layout.children.index(widget)
                        if idx + 1 < len(grid_layout.children):
                            cantidad_widget = grid_layout.children[idx + 1]
                            if isinstance(cantidad_widget, TextInput) and cantidad_widget.hint_text == "Cantidad":
                                nombre_pieza = widget.text.strip()
                                cantidad_pieza = cantidad_widget.text.strip()
                                if nombre_pieza and cantidad_pieza and cantidad_pieza != '0':
                                    partes_recibidas.append({"parte": nombre_pieza, "cantidad": cantidad_pieza})
                                    
                                    
                        # === OBSERVACIÓN DE PARTES RECIBIDAS ===
            observacion_partes_recibidas = ""
            if hasattr(self, '_observacion_partes_widget') and self._observacion_partes_widget:
                observacion_partes_recibidas = self._observacion_partes_widget.text.strip()

            # === MANO DE OBRA, REPUESTOS Y OBSERVACIONES ===
            mano_obra = []
            repuestos = []
            observaciones = []

            if hasattr(self.ids, 'grid_mano_obra'):
                operadores = list(self.ids.grid_mano_obra.children)
                operadores.reverse()

                for contenedor_mano_obra_completo in operadores:
                    if not contenedor_mano_obra_completo.children:
                        continue
                    contenedor_operador = contenedor_mano_obra_completo.children[0]
                    operador_nombre = "N/A"
                    for child in contenedor_operador.children:
                        if isinstance(child, BoxLayout):
                            for subchild in child.children:
                                if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                                    operador_nombre = limpiar_nombre_operador(subchild.text)
                                    break

                    # --- Trabajos ---
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        trabajos_container = contenedor_operador.trabajos_container
                        filas_trabajo = list(trabajos_container.children)
                        filas_trabajo.reverse()
                        for fila_layout in filas_trabajo:
                            if isinstance(fila_layout, BoxLayout) and len(fila_layout.children) == 6:
                                children = fila_layout.children
                                trabajo_widget = children[5]
                                cantidad_widget = children[4]
                                precio_widget = children[2]
                                total_widget = children[3]
                                terminado_widget = children[1]
                                if (hasattr(trabajo_widget, 'text') and
                                    hasattr(cantidad_widget, 'text') and
                                    hasattr(precio_widget, 'text') and
                                    hasattr(total_widget, 'text')):
                                    trabajo_texto = trabajo_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    precio_texto = precio_widget.text.strip()
                                    total_texto = total_widget.text.strip()
                                    terminado_estado = getattr(terminado_widget, 'active', False)
                                    if trabajo_texto:
                                        try:
                                            cantidad_num = float(cantidad_texto) if cantidad_texto else 0
                                            precio_num = float(precio_texto) if precio_texto else 0
                                            total_num = float(total_texto) if total_texto else 0
                                        except ValueError:
                                            cantidad_num = 0
                                            precio_num = 0
                                            total_num = 0
                                        mano_obra.append({
                                            'operador': operador_nombre,
                                            'descripcion': trabajo_texto,
                                            'cantidad': cantidad_num,
                                            'precio': total_num,# Aparecen al reves No lo cambies
                                            'total': precio_num, 
                                            'terminado': terminado_estado
                                            
                                           

                                        })

                    # --- Repuestos ---
                    if hasattr(contenedor_operador, 'repuestos_container'):
                        repuestos_container = contenedor_operador.repuestos_container
                        filas_repuesto = list(repuestos_container.children)
                        filas_repuesto.reverse()  # Mantener para orden visual correcto

                        # FILTRO MEJORADO: Excluir header, templates y filas completamente vacías (IGUAL QUE EN RECOPILAR_DATOS)
                        filas_datos = []
                        textos_header = ["Código", "Nombre", "Cantidad", "Precio", "Total", "Acción"]  # Ajusta si hay ":" o variaciones
                        
                        for f in filas_repuesto:
                            if not (isinstance(f, BoxLayout) and len(f.children) == 6):
                                continue  # No es una fila de datos válida
                            
                            children = f.children  # Accede una vez para eficiencia
                            
                            # Verificar si es header: busca Labels/TextInput con text/hint_text en textos_header
                            is_header = False
                            for child in children:
                                if (isinstance(child, (Label, TextInput)) and 
                                    (getattr(child, 'text', '').strip() in textos_header or 
                                    getattr(child, 'hint_text', '').strip() in textos_header)):
                                    is_header = True
                                    break
                            if is_header:
                                continue  # Excluir header
                            
                            # Verificar si es fila vacía/template (código y nombre vacíos)
                            codigo_widget = children[5] if len(children) > 5 else None
                            nombre_widget = children[4] if len(children) > 4 else None
                            if (not codigo_widget or not hasattr(codigo_widget, 'text') or 
                                not nombre_widget or not hasattr(nombre_widget, 'text') or
                                not codigo_widget.text.strip() and not nombre_widget.text.strip()):
                                continue  # Excluir filas en blanco
                            
                            # Si pasa, es válida
                            filas_datos.append(f)
                        
                        # Procesar solo filas válidas
                        for fila_repuesto in filas_datos:
                            children = fila_repuesto.children
                            codigo_widget = children[5]
                            nombre_widget = children[4]
                            cantidad_widget = children[3]
                            precio_widget = children[2]
                            total_widget = children[1]
                            
                            if (hasattr(codigo_widget, 'text') and 
                                hasattr(nombre_widget, 'text') and 
                                hasattr(cantidad_widget, 'text') and
                                hasattr(precio_widget, 'text') and
                                hasattr(total_widget, 'text')):
                                codigo_texto = codigo_widget.text.strip()
                                nombre_texto = nombre_widget.text.strip()
                                cantidad_texto = cantidad_widget.text.strip()
                                precio_texto = precio_widget.text.strip()
                                total_texto = total_widget.text.strip()
                                
                                # NUEVA VALIDACIÓN: Solo agregar si nombre válido Y algún valor numérico >0
                                if nombre_texto and nombre_texto not in textos_header:  # Excluir si es texto de header residual
                                    try:
                                        cantidad_num = float(cantidad_texto) if cantidad_texto else 0
                                        precio_num = float(precio_texto) if precio_texto else 0
                                        total_num = float(total_texto) if total_texto else 0
                                        
                                        if cantidad_num > 0 or precio_num > 0 or total_num > 0:  # Evita totals=0 puros
                                            repuestos.append({
                                                'operador': operador_nombre,
                                                'codigo': codigo_texto,
                                                'nombre': nombre_texto,
                                                'cantidad': cantidad_num,
                                                'precio': precio_num,
                                                'total': total_num
                                            })
                                            print(f"📦 Repuesto válido para '{operador_nombre}': {nombre_texto} (Total: {total_num})")
                                        else:
                                            print(f"⚠️ Fila ignorada (total=0): '{nombre_texto}'")
                                    except ValueError:
                                        print(f"⚠️ Error numérico en fila: '{nombre_texto}'")
                                else:
                                    print(f"⚠️ Fila ignorada (nombre inválido o header): '{nombre_texto}'")
     
                    # --- Observaciones ---
                    if hasattr(contenedor_operador, '_observacion_input'):
                        observacion_input = contenedor_operador._observacion_input
                        if hasattr(observacion_input, 'text'):
                            observacion_texto = observacion_input.text.strip()
                            if observacion_texto:
                                observaciones.append({
                                    'operador': operador_nombre,
                                    'texto': observacion_texto
                                })

            # === TOTALES ===
            def parse_money(text):
                try:
                    return float(text.replace('$', '').replace(',', '') or "0")
                except ValueError:
                    return 0.0

            total_mano_obra = parse_money(self.ids.total_mano_obra.text)
            total_repuestos = parse_money(self.ids.total_repuestos.text)
            subtotal = parse_money(self.ids.subtotal.text)
            iva = parse_money(self.ids.iva.text)
            total_general = parse_money(self.ids.total_general.text)
            anticipo = float(self.ids.anticipo.text or "0")
            abonos = float(self.ids.abonos.text or "0")
            saldo = parse_money(self.ids.saldo.text)

            # === CONSTRUIR DOCUMENTO ===
            documento_ficha = {
                "cliente": {
                    "rif": rif_completo,
                    "nombre": nombre,
                    "telefono": telefono,
                    "direccion": direccion,
                    "fecha_registro": fecha
                },
                "motor": {
                    "tipo": tipo_motor,
                    "marca": marca_motor,
                    "nombre": motor_nombre,
                    "cilindraje": cilindraje_motor,
                    "serial": serial_motor
                },
                "partes_recibidas": partes_recibidas,
                "observacion_partes_recibidas": observacion_partes_recibidas, 
                "mano_obra": mano_obra,
                "repuestos": repuestos,
                "observaciones": observaciones,
                "totales": {
                    "total_mano_obra": total_mano_obra,
                    "total_repuestos": total_repuestos,
                    "subtotal": subtotal,
                    "iva": iva,
                    "total_general": total_general,
                    "anticipo": anticipo,
                    "abonos": abonos,
                    "saldo": saldo
                },
                "tipo_ficha": "rectificadora",
            }


            # === GUARDAR DATOS ADICIONALES EN OTRAS COLECCIONES ===
            es_modificacion = getattr(self, 'es_modificacion', False)

            # --- 1. Guardar motor en BDmotores ---
            col_motores = db['BDmotores']
            motor_doc = {
                "marca": marca_motor,
                "nombre": motor_nombre,
                "cilindraje": cilindraje_motor,
                "serial": serial_motor,
                "fecha_registro": datetime.now().isoformat(),
                "numero_ficha": self.numero_ficha 
            }
            col_motores.insert_one(motor_doc)
            print(f"✅ Motor guardado en BDmotores para ficha #{self.numero_ficha}")

            # --- 2. Guardar marca en MarcasMotores (solo si no existe) ---
            col_marcas = db['MarcasMotores']
            if marca_motor and not col_marcas.find_one({"nombre": marca_motor}):
                col_marcas.insert_one({
                    "nombre": marca_motor,
                    "fecha_registro": datetime.now().isoformat()
                })
                print(f"✅ Marca '{marca_motor}' guardada en MarcasMotores")

            # --- 3. Guardar cliente en 'clientes' (si no existe) ---
            col_clientes = db['clientes']
            if not col_clientes.find_one({"rif": rif_completo}):
                col_clientes.insert_one({
                    "rif": rif_completo,
                    "nombre": nombre,
                    "telefono": telefono,
                    "direccion": direccion,
                    "fecha_registro": datetime.now().isoformat()
                })
                print(f"✅ Cliente '{nombre}' guardado en 'clientes'")

            # --- 4. Gestionar trabajos en registro_trabajos ---
            col_trabajos = db['registro_trabajos']
            
            if es_modificacion:
                # Eliminar trabajos antiguos de esta ficha
                col_trabajos.delete_many({"numero_ficha": self.numero_ficha})
                print(f"🗑️ Trabajos antiguos eliminados para ficha #{self.numero_ficha}")
            
            # Insertar los trabajos actuales
            for trabajo in mano_obra:
                trabajo_doc = {
                    "numero_ficha": self.numero_ficha,
                    "operador": trabajo['operador'],
                    "descripcion": trabajo['descripcion'],
                    "cantidad": trabajo['cantidad'],
                    "precio": trabajo['precio'],
                    "total": trabajo['total'],
                    "terminado": trabajo['terminado'],
                    "fecha_registro": datetime.now().isoformat(),
                    "tipo_ficha": "rectificadora"
                }
                col_trabajos.insert_one(trabajo_doc)
            print(f"✅ {len(mano_obra)} trabajos guardados en registro_trabajos")

            # --- 5. Gestionar repuestos en registro_repuestos ---
            col_repuestos_reg = db['registro_repuestos']
            
            if es_modificacion:
                # Eliminar repuestos antiguos de esta ficha
                col_repuestos_reg.delete_many({"numero_ficha": self.numero_ficha})
                print(f"🗑️ Repuestos antiguos eliminados para ficha #{self.numero_ficha}")
            
            # Insertar los repuestos actuales
            for repuesto in repuestos:
                repuesto_doc = {
                    "numero_ficha": self.numero_ficha,
                    "operador": repuesto['operador'],
                    "codigo": repuesto['codigo'],
                    "nombre": repuesto['nombre'],
                    "cantidad": repuesto['cantidad'],
                    "precio": repuesto['precio'],
                    "total": repuesto['total'],
                    "fecha_registro": datetime.now().isoformat(),
                    "tipo_ficha": "rectificadora"
                }
                col_repuestos_reg.insert_one(repuesto_doc)
            print(f"✅ {len(repuestos)} repuestos guardados en registro_repuestos")

            # === DECIDIR: INSERTAR O ACTUALIZAR ===
            es_modificacion = getattr(self, 'es_modificacion', False)

            if es_modificacion:
                # Modo: ACTUALIZAR ficha existente
                numero_ficha = self.numero_ficha
                documento_ficha["fecha_modificacion"] = datetime.now().isoformat()
                result = col_fichas.update_one(
                    {"numero_ficha": numero_ficha},
                    {"$set": documento_ficha}
                )
                if result.modified_count > 0:
                    print(f"✅ Ficha #{numero_ficha} actualizada correctamente.")
                    self.ids.mensaje_estado.text = f"✅ Ficha #{numero_ficha} actualizada correctamente."
                    if hasattr(self, 'callback_guardado') and self.callback_guardado:
                        self.callback_guardado()
                else:
                    print(f"⚠️ Ficha #{numero_ficha} no tuvo cambios o no se encontró.")
                    self.ids.mensaje_estado.text = f"⚠️ No se detectaron cambios en la ficha #{numero_ficha}."
            else:
                # Modo: INSERTAR nueva ficha
                documento_ficha["numero_ficha"] = self.numero_ficha
                documento_ficha["fecha_creacion"] = datetime.now().isoformat()
                documento_ficha["estado"] = "registrada"

                # Verificar que no exista (por seguridad)
                if col_fichas.find_one({"numero_ficha": self.numero_ficha}):
                    self.cargar_numero_ficha()  # Reasignar número
                    documento_ficha["numero_ficha"] = self.numero_ficha
                    documento_ficha["fecha_creacion"] = datetime.now().isoformat()

                col_fichas.insert_one(documento_ficha)
                print(f"✅ Ficha #{self.numero_ficha} creada correctamente.")
                self.ids.mensaje_estado.text = f"✅ Ficha #{self.numero_ficha} guardada correctamente."
                self._actualizar_vista_fichas(documento_ficha)

            client.close()
            self.dismiss()

        except Exception as e:
            print(f"❌ Error al guardar ficha: {e}")
            import traceback
            traceback.print_exc()
            self.ids.mensaje_estado.text = f"❌ Error al guardar en la base de datos: {str(e)}"
            
        client = MongoClient('mongodb://localhost:27017/')
        db = client['Inrema']
        col = db['fichas']
        textos_invalidos = ["Código", "Nombre", "Cantidad", "Precio", "Total", "Acción"]
        for ficha in col.find():
            if 'repuestos' in ficha:
                repuestos_limpios = [r for r in ficha['repuestos'] if r.get('nombre', '') not in textos_invalidos and r.get('total', 0) > 0]
                if len(repuestos_limpios) < len(ficha['repuestos']):
                    col.update_one({'_id': ficha['_id']}, {'$set': {'repuestos': repuestos_limpios}})
                    print(f"🧹 Limpiada ficha {ficha.get('numero_ficha')}: {len(ficha['repuestos'])} → {len(repuestos_limpios)}")
        client.close()
        


    def _actualizar_vista_fichas(self, nueva_ficha):
        """Actualiza la tabla de VistaFichas con la nueva ficha"""
        try:
            # Buscar la pantalla VistaFichas en el ScreenManager
            app = App.get_running_app()
            if app and hasattr(app, 'root'):
                # Buscar el ScreenManager
                for child in app.root.walk():
                    if hasattr(child, 'current') and hasattr(child, 'screens'):  # Es un ScreenManager
                        for screen in child.screens:
                            if screen.name == 'vista_fichas' or isinstance(screen, VistaFichas):
                                # Encontramos la pantalla VistaFichas
                                screen.agregar_nueva_ficha_a_tabla(nueva_ficha)
                                print("✅ VistaFichas actualizada automáticamente")
                                return
            
            print("ℹ️  No se pudo encontrar VistaFichas para actualizar")
            
        except Exception as e:
            print(f"❌ Error al actualizar VistaFichas: {e}")


    def _extraer_datos_operador_para_bd(self, contenedor_operador):
        """Extrae los datos de trabajos de un operador para guardar en BD (CORREGIDO)"""
        trabajos = []
        try:
            operador_nombre = "N/A"
            
            # Buscar el label del operador en el header
            for child in contenedor_operador.children:
                if isinstance(child, BoxLayout):  # Es el contenedor header
                    for subchild in child.children:
                        if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                            operador_nombre = subchild.text.replace("Operador:", "").strip()
                            break
            
            # Buscar las filas de trabajo (BoxLayout con orientación horizontal)
            for child in contenedor_operador.children:
                if isinstance(child, BoxLayout) and child.orientation == 'horizontal' and len(child.children) == 6:
                    # Esta es una fila de trabajo (6 widgets: trabajo, cantidad, precio, total, terminado, eliminar)
                    children = child.children
                    
                    # Los children están en orden inverso en Kivy
                    trabajo_widget = children[5]    # TextInput Trabajo
                    cantidad_widget = children[4]   # TextInput Cantidad  
                    precio_widget = children[3]     # TextInput Precio
                    total_widget = children[2]      # TextInput Total
                    terminado_widget = children[1]  # CheckBox
                    # children[0] es el botón eliminar
                    
                    print(f"  📝 Procesando fila:")
                    print(f"    - Trabajo: {getattr(trabajo_widget, 'text', 'N/A')}")
                    print(f"    - Cantidad: {getattr(cantidad_widget, 'text', 'N/A')}")
                    print(f"    - Precio: {getattr(precio_widget, 'text', 'N/A')}")
                    print(f"    - Total: {getattr(total_widget, 'text', 'N/A')}")
                    
                    # Validar que tengan los atributos necesarios
                    if (hasattr(trabajo_widget, 'text') and 
                        hasattr(cantidad_widget, 'text') and 
                        hasattr(precio_widget, 'text') and 
                        hasattr(total_widget, 'text')):
                        
                        trabajo_texto = trabajo_widget.text.strip()
                        
                        # ✅ Validar que no sea el placeholder y que tenga contenido
                        if (trabajo_texto and 
                            trabajo_texto != "Descripción del trabajo" and 
                            trabajo_texto != ""):
                            
                            try:
                                cantidad = float(cantidad_widget.text or 0)
                                precio = float(precio_widget.text or 0)
                                total = float(total_widget.text or 0)
                                terminado = getattr(terminado_widget, 'active', False) if hasattr(terminado_widget, 'active') else False
                                
                                trabajo_data = {
                                    'operador': operador_nombre,
                                    'descripcion': trabajo_texto,
                                    'cantidad': cantidad,
                                    'precio': precio,
                                    'total': total,
                                    'terminado': terminado,
                                    'fecha_creacion': datetime.now().isoformat()
                                }
                                
                                trabajos.append(trabajo_data)
                                print(f"    ✅ Trabajo guardado: {trabajo_texto}")
                                
                            except ValueError as ve:
                                print(f"    ❌ Error convirtiendo valores numéricos: {ve}")
                                continue
                        else:
                            print(f"    ⚠️  Trabajo vacío o placeholder")
                    else:
                        print(f"    ❌ Widgets no tienen atributo 'text'")
                                        
        except Exception as e:
            print(f"❌ Error extrayendo datos operador para BD: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"🎯 Total trabajos extraídos: {len(trabajos)}")
        return trabajos
        
    
    def _extraer_datos_repuesto_para_bd(self, fila_repuesto):
        """Extrae los datos de un repuesto para guardar en BD"""
        try:
            children = fila_repuesto.children
            if len(children) >= 5:  # nombre, cantidad, precio, total, botón eliminar
                # Los children están en orden inverso en Kivy
                nombre = children[-1].text if hasattr(children[-1], 'text') else "N/A"
                cantidad_text = children[-2].text if hasattr(children[-2], 'text') else "0"
                precio_text = children[-3].text if hasattr(children[-3], 'text') else "0"
                total_text = children[-4].text if hasattr(children[-4], 'text') else "0"
                
                try:
                    cantidad = float(cantidad_text or 0)
                    precio = float(precio_text or 0)
                    total = float(total_text or 0)
                    
                    if cantidad > 0 and nombre != "N/A":
                        return {
                            'nombre': nombre,
                            'cantidad': cantidad,
                            'precio': precio,
                            'total': total,
                            'fecha_agregado': datetime.now().isoformat()
                        }
                except ValueError as ve:
                    print(f"Error convirtiendo valores de repuesto: {ve}")
                    
        except Exception as e:
            print(f"❌ Error extrayendo datos repuesto para BD: {e}")
        
        return None
    
    def abrir_popup_operadores(self):
        """Abre el popup para seleccionar operador. Al seleccionar, crea el bloque completo con sus trabajos."""
        
        def on_operador_seleccionado(operador):
            nombre = operador['nombre']
            print(f"🖥️ Operador seleccionado: {nombre}")
            
            # ✅ Crear el bloque COMPLETO pasando el nombre
            self.crear_input_operador(nombre_operador=nombre)
            
            # Cerrar popup
            popup.dismiss()

        # Abrir el popup
        popup = OperadoresPopup(callback=on_operador_seleccionado)
        popup.open()


    def _actualizar_grid_altura(self):
        """Actualiza la altura del grid para mostrar todos los operadores"""
        try:
            if hasattr(self.ids, 'grid_mano_obra'):
                self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height
        except Exception as e:
            print(f"Error actualizando altura del grid: {e}")
                
    ultimas_filas_agregadas = []

    def agregar_fila_partes_recibidas(self):
        """
        Agrega una nueva fila de partes recibidas al GridLayout.
        La fila contiene un TextInput para cantidad, uno para nombre de la pieza y un botón de eliminar.
        """
        grid_layout = self.ids.get('grid_partes_recibidas')  # Asumiendo que tu GridLayout tiene id='grid_partes_recibidas'
        if not grid_layout:
            print("❌ Error: No se encontró el GridLayout 'grid_partes_recibidas'.")
            return

        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.metrics import dp

        # Crear los widgets
        textinput_cantidad = TextInput(
            hint_text="Cantidad",
            input_filter='float',  # Solo permite números
            size_hint_y=None,
            height=dp(30),  # Misma altura que las otras filas
            multiline=False
        )

        textinput_pieza = TextInput(
            hint_text="Pieza",
            size_hint_y=None,
            height=dp(30),  # Misma altura que las otras filas
            multiline=False
        )

        # Botón de eliminar
        btn_eliminar = Button(
            text='×',
            size_hint_y=None,
            height=dp(30),  # Misma altura que las otras filas
            width=dp(30),   # Ancho fijo para el botón
            size_hint_x=None, # Anular el tamaño proporcional en X
            background_color=(0.8, 0.2, 0.2, 1), # Rojo
            color=(1, 1, 1, 1), # Blanco
            bold=True,
            font_size=dp(16)
        )

        # Función para eliminar la fila específica
        def eliminar_fila(instance):
            # Remover los 3 widgets de la fila del GridLayout
            grid_layout.remove_widget(textinput_cantidad)
            grid_layout.remove_widget(textinput_pieza)
            grid_layout.remove_widget(btn_eliminar)
            # Opcional: Remover la fila de la lista si está allí
            if [textinput_cantidad, textinput_pieza, btn_eliminar] in self.ultimas_filas_agregadas:
                self.ultimas_filas_agregadas.remove([textinput_cantidad, textinput_pieza, btn_eliminar])
            print("🗑️ Fila de partes recibidas eliminada.")

        # Vincular el botón a la función de eliminación
        btn_eliminar.bind(on_press=eliminar_fila)

        # Añadirlos al GridLayout
        # El GridLayout distribuye los widgets en columnas automáticamente
        grid_layout.add_widget(textinput_cantidad)
        grid_layout.add_widget(textinput_pieza)
        grid_layout.add_widget(btn_eliminar) # Añadir el botón

        # Guardar la fila en la lista
        if not hasattr(self, 'ultimas_filas_agregadas'):
            self.ultimas_filas_agregadas = []
        self.ultimas_filas_agregadas.append([textinput_cantidad, textinput_pieza, btn_eliminar])

        print("✅ Fila de partes recibidas agregada con botón de eliminar.")


    def agregar_observacion_partes_recibidas(self):
        """Agrega un campo de observación debajo del grid de partes recibidas (solo si no existe ya)"""
        # Verificar si ya existe una observación
        if hasattr(self, '_observacion_partes_widget') and self._observacion_partes_widget:
            # Eliminar si ya existe (toggle)
            widget = self._observacion_partes_widget
            parent = widget.parent
            if parent:
                parent.remove_widget(widget)
            self._observacion_partes_widget = None
            print("🗑️ Observación eliminada.")
            return

        from kivy.uix.textinput import TextInput
        from kivy.metrics import dp

        # Crear el TextInput
        observacion_input = TextInput(
            hint_text="Observaciones sobre las partes recibidas...",
            size_hint_y=None,
            height=dp(80),  # Altura suficiente para varias líneas
            multiline=True,
            font_size=dp(14)
        )

        # Guardar referencia para futuras operaciones
        self._observacion_partes_widget = observacion_input

        # Encontrar el contenedor padre (el que contiene el GridLayout)
        contenedor = self.ids.grid_partes_recibidas.parent
        if not contenedor:
            print("❌ Error: No se encontró el contenedor padre del grid.")
            return

        # Insertar el TextInput justo después del GridLayout
        index = contenedor.children.index(self.ids.grid_partes_recibidas)
        contenedor.add_widget(observacion_input, index)  # Inserta en la posición siguiente

        print("✅ Campo de observación para partes recibidas agregado.")





    def eliminar_ultima_fila_partes_recibidas(self):
        """
        Elimina la última fila de partes recibidas agregada dinámicamente.
        """
        if not hasattr(self, 'ultimas_filas_agregadas') or not self.ultimas_filas_agregadas:
            print("⚠️ No hay filas dinámicas para eliminar.")
            return

        grid_layout = self.ids.get('grid_partes_recibidas')
        if not grid_layout:
            print("❌ Error: No se encontró el GridLayout 'grid_partes_recibidas'.")
            return

        # Obtener la última fila agregada
        ultima_fila = self.ultimas_filas_agregadas.pop() # Obtiene y remueve la última fila de la lista
        textinput_cantidad, textinput_pieza, btn_eliminar = ultima_fila

        # Remover los 3 widgets de la fila del GridLayout
        grid_layout.remove_widget(textinput_cantidad)
        grid_layout.remove_widget(textinput_pieza)
        grid_layout.remove_widget(btn_eliminar)

        print("🗑️ Última fila de partes recibidas agregada eliminada.")
        
    def crear_input_operador(self, nombre_operador=None):
        """Crea un bloque completo de operador con su nombre, botón X, tabla de trabajos y repuestos.
        El contenedor_operador es el único contenedor padre. El contenedor_trabajos es su hijo."""
        from kivy.uix.checkbox import CheckBox
        from kivy.metrics import dp
        from kivy.uix.widget import Widget
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.graphics import Color, Rectangle # Necesario para el fondo del Label
        from kivy.clock import Clock # Necesario para el schedule_once

        # ✅ 1. CREAR EL CONTENEDOR PRINCIPAL (¡UNO SOLO! QUE ENGLOBA TODO)
        contenedor_mano_obra_completo = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(370),  # Altura inicial estimada
            spacing=5,
            padding=[20, 10, 20, 10]
        )
        self.contenedor_mano_obra_completo = contenedor_mano_obra_completo 

        # ✅ 2. ENCABEZADO "MANO DE OBRA" (fuera del contenedor_operador, pero dentro del contenedor_mano_obra_completo)

        # ✅ 3. CREAR EL CONTENEDOR DEL OPERADOR (¡ESTE ES EL CONTENEDOR PADRE DE TODO LO DEL OPERADOR!)
        contenedor_operador = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(300),  # Altura inicial estimada (se ajustará dinámicamente)
            spacing=5,
            padding=[10, 10, 10, 10]
        ) #Mira estas aca mamañema trata de cambiar el espacio de este

        # ✅ 4. HEADER DEL OPERADOR (Nombre y Botón X) → ¡HIJO DIRECTO DE contenedor_operador!
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=10,
            padding=[0, 5, 0, 5]
        )

        nombre_mostrar = nombre_operador if nombre_operador else "(Seleccionar operador)"
        operador_label = Label(
            text=f"[b]Operador:[/b] {nombre_mostrar}",
            size_hint_x=0.8,
            size_hint_y=None,
            height=dp(35),
            font_size=16,
            text_size=(None, dp(35)),
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1),
            markup=True,
            bold=True
        )

        # Fondo sólido para evitar que se vea el texto detrás
        with operador_label.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            rect_label = Rectangle(size=operador_label.size, pos=operador_label.pos)
        operador_label._bg_rect_label = rect_label
        def actualizar_fondo_label(instance, value):
            if hasattr(instance, '_bg_rect_label'):
                instance._bg_rect_label.pos = instance.pos
                instance._bg_rect_label.size = instance.size
        operador_label.bind(pos=actualizar_fondo_label, size=actualizar_fondo_label)

        def eliminar_operador(instance):
            self.ids.grid_mano_obra.remove_widget(contenedor_mano_obra_completo)
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
            Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1) # Agregado para actualizar altura
            print("Operador eliminado y totales recalculados")

        btn_eliminar = Button(
            text='×',
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=18,
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_eliminar.bind(on_press=eliminar_operador)
        btn_observacion = Button(
            text='!',
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            background_color=(0.2, 0.2, 0.8, 1),
            font_size=18,
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_observacion.bind(on_press=lambda instance: self.agregar_bloque_observacion_a_operador(contenedor_operador, contenedor_mano_obra_completo))

        header_layout.add_widget(operador_label)
        header_layout.add_widget(btn_observacion)
        header_layout.add_widget(btn_eliminar)
        contenedor_operador.add_widget(header_layout)

        # ✅ 5. SEPARADOR VISUAL (entre el header y la tabla de trabajos)
        separador = Widget(
            size_hint_y=None,
            height=dp(10)
        )
        contenedor_operador.add_widget(separador)

        # ✅ 6. CONTENEDOR DE TRABAJOS → ¡ESTE ES UN HIJO DIRECTO DE contenedor_operador!
        contenedor_trabajos = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height= dp(35) + (3 * dp(37)) + dp(20), # Altura inicial
            spacing=3,
            padding=[0, 5, 0, 10]
        )

        # Headers de la tabla de trabajos
        headers_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35), # Corregido a dp(35) para que coincida con la altura de una fila
            spacing=2
        )

        headers = ['Trabajo', 'Cantidad', 'Precio', 'Total', 'Terminado']
        weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]

        for i, header in enumerate(headers):
            label = Label(
                text=header,
                size_hint_x=weights[i],
                color=(0.9, 0.9, 0.9, 1),
                bold=True,
                halign='center',
                valign='middle'
            )
            headers_layout.add_widget(label)

        # Botón para agregar trabajo
        btn_agregar_trabajo = Button(
            text='+',
            size_hint_x=weights[-1],
            size_hint_y=None,
            height=dp(35),
            background_color=(0.2, 0.7, 0.2, 1)
        )

        def abrir_popup_trabajos(instance):
            if not nombre_operador or nombre_operador == "(Seleccionar operador)":
                self.agregar_fila_trabajo2(contenedor_trabajos)
                return

            # ✅ Obtener los nombres de los trabajos YA agregados
            trabajos_actuales = []
            if hasattr(contenedor_operador, 'trabajos_container'):
                for fila in contenedor_operador.trabajos_container.children:
                    if len(fila.children) >= 6:
                        trabajo_input = fila.children[5]  # TextInput del trabajo
                        if hasattr(trabajo_input, 'text') and trabajo_input.text.strip():
                            trabajos_actuales.append(trabajo_input.text.strip())

            def on_trabajos_seleccionados(trabajos_seleccionados, custom_vacio):
                # Agregar trabajos normales
                for trabajo_nombre in trabajos_seleccionados:
                    self._crear_fila_trabajo_con_datos(contenedor_trabajos, contenedor_mano_obra_completo, nombre=trabajo_nombre)
                # Agregar fila vacía si se marcó la opción personalizada
                if custom_vacio:
                    self._crear_fila_trabajo_con_datos(contenedor_trabajos,contenedor_mano_obra_completo, nombre="")
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            popup = TrabajosOperadorPopup(
                operador_nombre=nombre_operador,
                callback=on_trabajos_seleccionados,
                trabajos_preseleccionados=trabajos_actuales
            )
            popup.open()

        btn_agregar_trabajo.bind(on_press=abrir_popup_trabajos)
        headers_layout.add_widget(btn_agregar_trabajo)
        contenedor_trabajos.add_widget(headers_layout)

        # ✅ 7. CONTENEDOR DE FILAS DE TRABAJO
        trabajos_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(0),  # Inicia en 0 si no quieres fila vacía
            spacing=2
        )
        contenedor_trabajos.add_widget(trabajos_container)
        contenedor_operador.add_widget(contenedor_trabajos)# ← ¡CLAVE! AÑADIR A contenedor_operador!

        # ✅ 8. ETIQUETA DE SECCIÓN DE REPUESTOS (dentro de contenedor_operador)
        repuestos_label = Label(
            text="REPUESTOS ASOCIADOS AL OPERADOR",
            size_hint_y=None,
            height=dp(25),
            font_size=12,
            bold=True,
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='middle',
            padding=[0, 5, 0, 0]
        )
        contenedor_operador.add_widget(repuestos_label)

        # ✅ 9. BOTÓN PARA AGREGAR REPUESTOS (dentro de contenedor_operador)
        btn_agregar_repuestos = Button(
            text='+ Agregar Repuesto',
            size_hint_y=None,
            height=dp(35),
            background_color=(0.2, 0.7, 0.2, 1),
            font_size=12
        )
        if self.nivel_usuario == 2 :
            btn_agregar_repuestos.disabled = True
    

        def abrir_popup_repuestos_para_operador(instance):
            def on_repuesto_seleccionado(repuesto):
                self.agregar_repuesto_a_operador(contenedor_operador, repuesto,contenedor_mano_obra_completo)
            popup = RepuestosPopup(callback=on_repuesto_seleccionado)
            popup.open()
        btn_agregar_repuestos.bind(on_press=abrir_popup_repuestos_para_operador)
        contenedor_operador.add_widget(btn_agregar_repuestos)

        # ✅ 10. GRID PARA LOS REPUESTOS (dentro de contenedor_operador)
        # Aquí se añadiría un grid/BoxLayout para repuestos, pero lo omitimos por concisión.

        # ✅ 11. GUARDAR REFERENCIAS CLAVE PARA USO POSTERIOR
        
        
        contenedor_operador.trabajos_container = trabajos_container
        contenedor_operador.operador_label = operador_label
        contenedor_operador.btn_eliminar = btn_eliminar

        contenedor_mano_obra_completo.add_widget(contenedor_operador)

        # ✅ OPCIONAL: agregar una fila vacía inicial
        if False:  # Cambia a False si no quieres fila inicial
            self._crear_fila_trabajo_con_datos(contenedor_trabajos, "", "0", "1")

        self.ids.grid_mano_obra.add_widget(contenedor_mano_obra_completo)
        Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)

        return {
            'label_operador': operador_label,
            'contenedor': contenedor_operador,
            'boton_eliminar': btn_eliminar,
            'trabajos_container': trabajos_container,
        }
    
    def agregar_fila_trabajo2(self, contenedor_trabajos):
        """Agrega una nueva fila de trabajo y ajusta todas las alturas"""
        from kivy.uix.checkbox import CheckBox
        from kivy.metrics import dp

        try:
            # ✅ Encontrar trabajos_container
            trabajos_container = None
            for child in contenedor_trabajos.children:
                if hasattr(child, 'orientation') and child.orientation == 'vertical':
                    trabajos_container = child
                    break
            if not trabajos_container:
                print("❌ No se encontró trabajos_container")
                return

            # ✅ Crear nueva fila
            weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]
            fila_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            trabajo_input = TextInput(
                text='',
                multiline=False,
                size_hint_x=weights[0],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )
            cantidad_input = TextInput(
                text="1",
                multiline=False,
                input_filter='float',
                size_hint_x=weights[1],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )
            precio_input = TextInput(
                text="0",
                multiline=False,
                input_filter='float',
                size_hint_x=weights[2],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )
            total_input = TextInput(
                text="0.00",
                multiline=False,
                readonly=True,
                size_hint_x=weights[3],
                background_color=(0.15, 0.15, 0.15, 1),
                foreground_color=(0.9, 0.9, 0.9, 1)
            )
            terminado_check = CheckBox(
                active=False,
                size_hint_x=weights[4],
                size_hint_y=None,
                height=dp(35)
            )
            btn_eliminar_fila = Button(
                text='×',
                size_hint_x=weights[5],
                size_hint_y=None,
                height=dp(35),
                background_color=(0.7, 0.3, 0.3, 1)
            )

            # Función para calcular total
            # ✅ Calcular total
            def calcular_total(*args):
                try:
                    c = float(cantidad_input.text or 0)
                    p = float(precio_input.text or 0)
                    total_input.text = f"{c * p:.2f}"
                except:
                    total_input.text = "0.00"
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            cantidad_input.bind(text=calcular_total)
            precio_input.bind(text=calcular_total)

            # ✅ Eliminación: reduce altura
            def eliminar_esta_fila(instance):
                try:
                    if fila_layout.parent:
                        padre = fila_layout.parent
                        padre.remove_widget(fila_layout)

                        # ✅ REDUCIR ALTURA DE TODOS LOS CONTENEDORES
                        padre.height -= dp(35)
                        contenedor_trabajos.height -= dp(35)
                        
                        # ✅ Buscar contenedor_operador
                        contenedor_operador = contenedor_trabajos.parent
                        if contenedor_operador:
                            contenedor_operador.height -= dp(35)

                        # ✅ Buscar contenedor_mano_obra_completo
                        if hasattr(contenedor_operador, 'parent'):
                            contenedor_mano_obra_completo = contenedor_operador.parent
                            if contenedor_mano_obra_completo:
                                contenedor_mano_obra_completo.height -= dp(35)

                        # ✅ Actualizar grid principal
                        Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)

                        print(f"✅ Fila eliminada. Nueva altura: {padre.height:.0f}dp")

                except Exception as e:
                    print(f"❌ Error eliminando fila: {e}")

            btn_eliminar_fila.bind(on_press=eliminar_esta_fila)

            # ✅ Agregar widgets a la fila
            fila_layout.add_widget(trabajo_input)
            fila_layout.add_widget(cantidad_input)
            fila_layout.add_widget(precio_input)
            fila_layout.add_widget(total_input)
            fila_layout.add_widget(terminado_check)
            fila_layout.add_widget(btn_eliminar_fila)

            # ✅ AÑADIR LA FILA AL CONTENEDOR
            trabajos_container.add_widget(fila_layout, index=0)  # Al inicio (arriba)

            # ✅ AUMENTAR ALTURA DE TODOS LOS CONTENEDORES EN LA CADENA
            trabajos_container.height += dp(35)
            contenedor_trabajos.height += dp(35)

            # ✅ Obtener contenedor_operador (el padre de contenedor_trabajos)
            contenedor_operador = contenedor_trabajos.parent
            contenedor_operador.height += dp(35)

            # ✅ Obtener contenedor_mano_obra_completo (el padre del operador)
            contenedor_mano_obra_completo = contenedor_operador.parent
            contenedor_mano_obra_completo.height += dp(35)

            # ✅ Forzar actualización del ScrollView
            Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)

            print(f"✅ Fila agregada. Nueva altura: {trabajos_container.height:.0f}dp")

        except Exception as e:
            print(f"❌ Error al agregar fila: {e}")
            import traceback
            traceback.print_exc()
                
    def agregar_bloque_observacion_a_operador(self, contenedor_operador, contenedor_mano_obra_completo):
        """Agrega un bloque de OBSERVACIÓN al final del contenedor de un operador específico."""
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.widget import Widget
        from kivy.metrics import dp
        from kivy.graphics import Color, Rectangle

        # Verificar si ya existe una observación para este operador
        if hasattr(contenedor_operador, '_observacion_widget'):
            self.ids.mensaje_estado.text = "Ya existe una observación para este operador."
            return

        altura_bloque = dp(100)
        altura_separador = dp(15)

        # ✅ Bloque principal de observación
        bloque_obs = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=altura_bloque,
            padding=[10, 5],
            spacing=5
        )

        # ✅ Header: "OBSERVACIÓN" + botón × (90% / 10%)
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25),
            spacing=5
        )

        # Label
        header_label = Label(
            text="[b]OBSERVACIÓN[/b]",
            size_hint_x=0.9,
            size_hint_y=None,
            height=dp(25),
            markup=True,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        header_label.bind(size=header_label.setter('text_size'))
        with header_label.canvas.before:
            Color(0.25, 0.25, 0.35, 1)
            rect = Rectangle(size=header_label.size, pos=header_label.pos)
        header_label._bg_rect = rect
        header_label.bind(
            pos=lambda inst, val: setattr(inst._bg_rect, 'pos', val),
            size=lambda inst, val: setattr(inst._bg_rect, 'size', val)
        )

        # ✅ ÚNICO botón × (10% del ancho)
        btn_eliminar_obs = Button(
            text='×',
            size_hint_x=0.1,
            size_hint_y=None,
            height=dp(25),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )

        text_input = TextInput(
            hint_text="Escriba observaciones...",
            multiline=True,
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10]
        )

        def eliminar_bloque(instance):
            if bloque_obs.parent:
                bloque_obs.parent.remove_widget(bloque_obs)
                if hasattr(contenedor_operador, '_observacion_widget'):
                    delattr(contenedor_operador, '_observacion_widget')
                    delattr(contenedor_operador, '_observacion_input')
                # Ajustar altura: restar altura del bloque y el separador
                contenedor_operador.height -= (altura_bloque + altura_separador)
                if contenedor_mano_obra_completo:
                    contenedor_mano_obra_completo.height -= (altura_bloque + altura_separador)
                Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
                print("🗑️ Observación del operador eliminada")

        btn_eliminar_obs.bind(on_press=eliminar_bloque)
        
        header_layout.add_widget(header_label)
        header_layout.add_widget(btn_eliminar_obs)

        # Ensamblar
        bloque_obs.add_widget(header_layout)
        bloque_obs.add_widget(text_input)

        # Guardar referencia
        contenedor_operador._observacion_widget = bloque_obs
        contenedor_operador._observacion_input = text_input

        # --- CORRECCIÓN AQUÍ ---
        # 1. Añadir SEPARADOR al contenedor_operador
        separador_superior = Widget(size_hint_y=None, height=altura_separador)
        contenedor_operador.add_widget(separador_superior)
        
        # 2. Añadir el BLOQUE DE OBSERVACIÓN al contenedor_operador (no al contenedor_trabajos)
        contenedor_operador.add_widget(bloque_obs)
        # --- FIN CORRECCIÓN ---

        # 3. Ajustar altura total del contenedor_operador y el contenedor_mano_obra_completo
        contenedor_operador.height += (altura_bloque + altura_separador)
        contenedor_mano_obra_completo.height += (altura_bloque + altura_separador)

        # 4. Actualizar grid principal
        Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
        print("✅ Bloque de observación agregado al operador")

        #contenedor_trabajos.add_widget(bloque_obs) 
        #contenedor_trabajos.height += bloque_obs.height
        
    def _actualizar_grid_altura(self):
        """Actualiza la altura del grid para mostrar todos los operadores"""
        try:
            if hasattr(self.ids, 'grid_mano_obra'):
                self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height
        except Exception as e:
            print(f"Error actualizando altura del grid: {e}")
                

    def calcular_todos_los_totales(self):
        """
        Recorre todos los bloques de operador en la interfaz, suma los campos 'Total'
        de cada fila de trabajo asumiendo que el campo 'Total' es el widget en el índice 3 
        de la lista de hijos de la fila (0=Trabajo, 1=Cantidad, 2=Precio, 3=Total, ...).
        Muestra el gran total en la consola.
        """
        grand_total = 0.0
        total_repuestos = 0.0  # 🔹 Definir aquí para evitar el error UnboundLocalError
        
        # Asume que self.ids.grid_mano_obra está disponible
        grid_mano_obra = self.ids.get('grid_mano_obra') 
        
        if not grid_mano_obra:
            print("Error: grid_mano_obra no encontrado. No se puede totalizar.")
            return

        # Iterar sobre cada contenedor_mano_obra_completo (bloque de operador)
        for contenedor_completo in grid_mano_obra.children:
            # 1. Obtener el contenedor_operador (asumido como el primer hijo)
            if not contenedor_completo.children:
                continue

            contenedor_operador = contenedor_completo.children[0]

            # 2. Obtener el contenedor que almacena las filas de trabajo usando la referencia guardada
            trabajos_container = None
            if hasattr(contenedor_operador, 'trabajos_container'):
                trabajos_container = contenedor_operador.trabajos_container
            else:
                # Si no se encuentra la propiedad, intenta navegar por la estructura (menos fiable)
                # Esto asume que contenedor_trabajos es el segundo elemento después del header
                if len(contenedor_operador.children) > 1 and isinstance(contenedor_operador.children[-2], BoxLayout):
                    contenedor_trabajos = contenedor_operador.children[-2]
                    # Asume que trabajos_container es el segundo hijo de contenedor_trabajos
                    if len(contenedor_trabajos.children) > 1:
                        trabajos_container = contenedor_trabajos.children[-2]

            
            if not trabajos_container:
                print("Advertencia: No se encontró trabajos_container para un operador. Se omite.")
                continue
                
            # 3. Iterar sobre las filas de trabajo (fila_layout es un BoxLayout horizontal)
            for fila_layout in trabajos_container.children:
                
                # Acceder al widget en la posición de "Total" (Índice 3)
                # El orden de los hijos en Kivy es inverso al que se añaden.
                # Para filas añadidas como: 1, 2, 3, 4(TOTAL), 5, 6
                # El orden de los hijos será: 6, 5, 4(TOTAL), 3, 2, 1
                
                # Pero en el código original, las filas se añaden en el orden 1, 2, 3, 4(TOTAL), 5, 6
                # Si el `fila_layout` mantiene ese orden:
                # Índice 0: trabajo_input
                # Índice 1: cantidad_input
                # Índice 2: precio_input
                # Índice 3: total_input   <-- USAMOS ESTE
                # Índice 4: terminado_check
                # Índice 5: btn_eliminar_fila
                
                TOTAL_INDEX = 2 # Según el orden especificado por el usuario
                
                if len(fila_layout.children) > TOTAL_INDEX:
                    total_input = fila_layout.children[TOTAL_INDEX]
                    try:
                        # Limpiar y sumar el total
                        # Asegurar que el widget es un TextInput antes de leer .text
                        if isinstance(total_input, TextInput):
                            # El input 'total_input' es readonly y tiene el valor con '.2f'
                            total_value = float(total_input.text.replace(',', '.')) 
                            grand_total += total_value
                        else:
                            print(f"Advertencia: El widget en el índice {TOTAL_INDEX} no es un TextInput. Se omite.")
                    except ValueError:
                        # Ignorar si el valor no es un número válido (ej. "")
                        pass
                else:
                    print("Advertencia: Fila incompleta. Se omite.")
            
            # Vamos a recorrer cada operador y buscar dentro de él los grids de repuestos (si existen)
            # total_repuestos ya está definido fuera del bucle

            # Recorremos todos los widgets hijos del contenedor_operador, excluyendo el bloque de observación

            for widget in contenedor_operador.children:
                # Verificar si el widget es el contenedor de observación o está relacionado con ella
                if (hasattr(contenedor_operador, '_observacion_widget') and 
                    (widget == contenedor_operador._observacion_widget or 
                    widget == contenedor_operador._observacion_input or
                    widget == getattr(contenedor_operador, '_observacion_header', None))):
                    # Saltar este widget y no procesarlo
                    continue

                # Si no es un bloque de observación, procesarlo normalmente
                if isinstance(widget, BoxLayout):
                    # Buscar layouts que representen filas de repuestos
                    # SOLO RECORRER LOS HIJOS DIRECTOS DEL WIDGET ACTUAL
                    for sub_widget in widget.children:  # <-- CAMBIADO A .children
                        if isinstance(sub_widget, BoxLayout):
                            # Solo consideramos BoxLayouts que contienen TextInputs (una fila de repuesto)
                            text_inputs = [w for w in sub_widget.children if isinstance(w, TextInput)]
                            if not text_inputs:
                                continue

                            # Invertir el orden (porque Kivy guarda los hijos de derecha a izquierda)
                            text_inputs = list(reversed(text_inputs))


                            # Detectar dinámicamente qué campos hay
                            campos = [ti.text.strip() for ti in text_inputs]
                            if len(campos) < 4:
                                continue  # Fila incompleta, la omitimos

                            try:
                                # Asumimos estructura: [codigo, nombre, cantidad, precio, total]
                                nombre = campos[1] if len(campos) > 1 else ""
                                total = campos[4] if len(campos) > 4 else "0"

                                # Verificamos si el total es un número válido
                                total_num = 0.0
                                try:
                                    total_num = float(total.replace(",", "."))
                                except ValueError:
                                    total_num = 0.0

                                # Mostrar solo filas que parezcan repuestos válidos
                                if nombre or total_num > 0:
                                    total_repuestos += total_num

                            except Exception as e:
                                print(f"   ⚠️ Error leyendo fila de repuesto: {e}")

                            
                            
        subtotal = grand_total + total_repuestos
        iva = subtotal * 0.16
        total_general = subtotal + iva

        try:
            anticipo = float(self.ids.anticipo.text or "0")
        except ValueError:
            anticipo = 0.0
        try:
            abonos = float(self.ids.abonos.text or "0")
        except ValueError:
            abonos = 0.0
        saldo = total_general - anticipo - abonos

        # 4. Imprimir el resultado final en la consola
        print("\n" + "="*40)
        print("--- RESULTADO DE LA TOTALIZACIÓN DE TRABAJOS ---")
        self.ids.total_mano_obra.text = f"${grand_total:,.2f}"
        self.ids.total_repuestos.text = f"${total_repuestos:,.2f}"
        self.ids.subtotal.text = f"${subtotal:,.2f}"
        self.ids.iva.text = f"${iva:,.2f}"
        self.ids.total_general.text = f"${total_general:,.2f}"
        self.ids.saldo.text = f"${saldo:,.2f}"


    def agregar_repuesto_a_operador(self, contenedor_operador, repuesto, contenedor_mano_obra_completo):
        """Agrega un repuesto al contenedor de repuestos usando lógica de altura dinámica como trata.py"""
        from kivy.metrics import dp

        # ✅ Buscar o crear el contenedor de repuestos
        repuestos_container = getattr(contenedor_operador, 'repuestos_container', None)

        if repuestos_container is None:
            # ✅ Crear contenedor con altura inicial (IGUAL QUE trata.py)
            repuestos_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(40),  # Altura inicial pequeña
                spacing=2,
                padding=[20, 0, 0, 0]
            )

            # Encabezado
            fila_encabezado = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            # Labels del encabezado (sin bind de text_size)
            for texto, ancho in [("Código", 0.2), ("Nombre", 0.3), ("Cant.", 0.15), ("Precio", 0.15), ("Total", 0.15)]:
                label = Label(
                    text=texto,
                    size_hint_x=ancho,
                    font_size=12,
                    color=(0.9, 0.9, 0.9, 1),
                    halign='center',
                    valign='middle',
                    bold=True
                )
                fila_encabezado.add_widget(label)

            repuestos_container.add_widget(fila_encabezado)
            setattr(contenedor_operador, 'repuestos_container', repuestos_container)
            contenedor_operador.add_widget(repuestos_container)

        # ✅ Crear fila de repuesto (TextInput sin text_size)
        fila_repuesto = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35),
            spacing=2
        )

        codigo_input = TextInput(
            text=str(repuesto.get('codigo', '')),
            multiline=False,
            readonly= True,
            size_hint_x=0.2,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        nombre_input = TextInput(
            text=repuesto.get('nombre', ''),
            multiline=False,
            readonly = True,
            size_hint_x=0.3,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        cantidad_input = TextInput(
            text="1" ,
            multiline=False,
            input_filter='float',
            size_hint_x=0.15,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        precio_input = TextInput(
            text=f"{repuesto.get('precio', 0):.2f}",
            multiline=False,
            input_filter='float',
            size_hint_x=0.15,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        total_input = TextInput(
            text="0.00",
            multiline=False,
            readonly=True,
            size_hint_x=0.15,
            font_size=12,
            foreground_color=(0.9, 0.9, 0.9, 1),
            background_color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(35)
        )

        btn_eliminar = Button(
            text='×',
            size_hint_x=0.05,
            size_hint_y=None,
            height=dp(35),
            background_color=(0.7, 0.3, 0.3, 1)
        )

        # Función para calcular total
        def calcular_total(*args):
            try:
                c = float(cantidad_input.text or 0)
                p = float(precio_input.text or 0)
                total_input.text = f"{c * p:.2f}"
            except:
                total_input.text = "0.00"
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

        cantidad_input.bind(text=calcular_total)
        precio_input.bind(text=calcular_total)

        # Función de eliminación con ajuste de altura
        def eliminar_fila(instance):
            if fila_repuesto.parent:
                # ✅ Quitar la fila
                fila_repuesto.parent.remove_widget(fila_repuesto)

                # ✅ Actualizar alturas como en trata.py
                repuestos_container.height -= dp(35)
                contenedor_mano_obra_completo.height -= dp(35)

                # ✅ Verificar si quedan filas de datos (excluyendo el encabezado)
                filas_datos = [
                    child for child in repuestos_container.children
                    if isinstance(child, BoxLayout) and len(child.children) == 6  # Fila de repuesto
                ]

                # ✅ Si NO quedan filas de datos, eliminar el encabezado y el contenedor
                if len(filas_datos) == 0:
                    # Buscar el encabezado y eliminarlo
                    for child in repuestos_container.children:
                        if isinstance(child, BoxLayout) and len(child.children) == 5:  # Tiene 5 widgets → es el encabezado
                            repuestos_container.remove_widget(child)
                            break

                    # ❌ Opcional: ¿También eliminar el contenedor? Depende de tu diseño
                    # Pero mejor dejarlo vacío con solo el encabezado pendiente
                    # No eliminamos el contenedor para evitar errores de referencia

                # ✅ Recalcular totales
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            else:
                print("❌ La fila ya fue eliminada o no tiene padre")
        btn_eliminar.bind(on_press=eliminar_fila)

        # Agregar widgets a la fila
        fila_repuesto.add_widget(codigo_input)
        fila_repuesto.add_widget(nombre_input)
        fila_repuesto.add_widget(cantidad_input)
        fila_repuesto.add_widget(precio_input)
        fila_repuesto.add_widget(total_input)
        fila_repuesto.add_widget(btn_eliminar)

        # ✅ Añadir fila y CRECER el contenedor (IGUAL QUE trata.py)
        repuestos_container.add_widget(fila_repuesto, index=0)
        repuestos_container.height += dp(35)
        contenedor_mano_obra_completo.height += dp(35)

        # Calcular total inicial
        calcular_total()

        print(f"✅ Repuesto añadido. Nueva altura: {repuestos_container.height:.0f}dp")


        
    def eliminar_repuesto_fila(self, fila_layout):
        """Elimina una fila de repuesto (encabezado o editable)"""
        if fila_layout.parent:
            fila_layout.parent.remove_widget(fila_layout)
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
            print("🗑️  Fila de repuesto eliminada")
    
            
    def _eliminar_fila_trabajo(self, contenedor_operador, fila_layout):
        """Elimina una fila de trabajo específica del contenedor correcto"""
        try:
            # Buscar manualmente el trabajos_container (igual que antes)
            trabajos_container = None
            for child in contenedor_operador.children:
                if isinstance(child, BoxLayout) and child.orientation == 'vertical':
                    for subchild in child.children:
                        if isinstance(subchild, BoxLayout) and subchild.orientation == 'vertical':
                            if fila_layout in subchild.children:
                                trabajos_container = subchild
                                break
                    if trabajos_container:
                        break

            if not trabajos_container:
                # Buscar recursivamente
                def buscar_fila_recursivo(widget):
                    if hasattr(widget, 'children'):
                        if fila_layout in widget.children:
                            return widget
                        for child in widget.children:
                            resultado = buscar_fila_recursivo(child)
                            if resultado:
                                return resultado
                    return None
                trabajos_container = buscar_fila_recursivo(contenedor_operador)

            # ✅ Eliminar la fila
            if trabajos_container and fila_layout in trabajos_container.children:
                trabajos_container.remove_widget(fila_layout)
                # ✅ ¡NO HACES NADA MÁS! ¡Kivy ajusta la altura automáticamente!
                print(f"✅ Fila eliminada correctamente. Quedan {len(trabajos_container.children)} filas")
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
                Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)
            else:
                print("❌ No se pudo encontrar la fila o el contenedor correcto")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            

   
    def _actualizar_scroll(self):
        """Fuerza la actualización del scroll para que reconozca los nuevos widgets"""
        # Buscar el ScrollView parent
        scroll_parent = self.ids.grid_mano_obra.parent
        while scroll_parent and not hasattr(scroll_parent, 'scroll_y'):
            scroll_parent = scroll_parent.parent
        
        if scroll_parent:
            # Forzar recálculo del contenido
            scroll_parent.scroll_to(widget=self.ids.grid_mano_obra.children[-1])


    def _scroll_to_bottom(self):
        """Hace scroll hasta abajo para mostrar el nuevo TextInput"""
        # Buscar el ScrollView
        scroll_view = None
        widget = self.ids.grid_mano_obra.parent
        while widget:
            if hasattr(widget, 'scroll_y'):
                scroll_view = widget
                break
            widget = widget.parent
        
        if scroll_view:
            scroll_view.scroll_y = 0  # Scroll hasta abajo

    def abrir_popup_repuestos(self):
        """Abre el popup para seleccionar repuesto. Al seleccionar, crea una fila de repuesto."""
        
        def on_repuesto_seleccionado(repuesto):
            # Crear fila de repuesto usando el método separado
            self.crear_fila_repuesto(repuesto)
            
            # Imprimir en consola (opcional, para depuración)
            print(f"🔧 Repuesto seleccionado: {repuesto['nombre']}")
            
            # Cerrar popup
            popup.dismiss()

        # Abrir el popup (usando RepuestosPopup como en EditarFicha)
        popup = RepuestosPopup(callback=on_repuesto_seleccionado)
        popup.open()
    def crear_fila_repuesto(self, repuesto):
        """Crea una fila simple de repuesto con 4 campos en una línea"""
        
        # ✅ CONTENEDOR HORIZONTAL simple (una sola fila)
        contenedor_repuesto = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=5,
            padding=[10, 5]
        )
        
        # ✅ Campo 1: Código del repuesto
        codigo = repuesto.get('codigo', '')
        codigo_str = str(codigo).strip() if codigo is not None else 'N/A'
        codigo_label = Label(
            text=codigo_str if codigo_str else 'N/A',
            size_hint_x=0.2,
            font_size=12,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        codigo_label.bind(size=codigo_label.setter('text_size'))
        
        # ✅ Campo 2: Nombre del repuesto
        nombre = repuesto.get('nombre', '')
        nombre_str = str(nombre).strip() if nombre is not None else 'N/A'
        nombre_label = Label(
            text=nombre_str if nombre_str else 'N/A',
            size_hint_x=0.2,
            font_size=12,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        nombre_label.bind(size=nombre_label.setter('text_size'))
        
        # ✅ Campo 3: Cantidad (TextInput)
        cantidad_input = TextInput(
            text=str(repuesto.get('cantidad', 1)),
            input_filter='float',
            multiline=False,
            font_size=12,
            size_hint_x=0.15
        )
        
        # ✅ Campo 4: Precio (TextInput)
        precio_input = TextInput(
            text=f"{repuesto.get('precio', 0.0):.2f}",
            input_filter='float',
            multiline=False,
            font_size=12,
            size_hint_x=0.15
        )
        
        # ✅ Campo 5: Total (Label)
        total_label = Label(
            text=f"{repuesto.get('total', 0.0):.2f}",
            font_size=12,
            color=(1, 1, 1, 1),
            size_hint_x=0.15,
            halign='center',
            valign='middle'
        )
        total_label.bind(size=total_label.setter('text_size'))
        
        # ✅ Botón X para eliminar
        def eliminar_repuesto(instance):
            """Elimina la fila del repuesto"""
            
            cantidad_input.text = "0"
            self.ids.grid_repuestos.remove_widget(contenedor_repuesto)
            print("🗑️ Repuesto eliminado")
        
        boton_eliminar = Button(
            text="X",
            size_hint=(None, None),
            size=(30, 30),
            background_color=(1, 0, 0, 1),  # Rojo
            color=(1, 1, 1, 1),  # Texto blanco
            font_size=14,
            bold=True,
            on_press=eliminar_repuesto
        )
        
        # ✅ FUNCIÓN para calcular total específica de esta fila

        def calcular_total_repuesto(instance, value):
            try:
                cantidad = float(cantidad_input.text or "0")
            except ValueError:
                cantidad = 0.0
            
            try:
                precio = float(precio_input.text or "0")
            except ValueError:
                precio = 0.0
            
            total = cantidad * precio
            total_label.text = f"{total:.2f}"
            
            # ✅ RECALCULAR TOTALES GENERALES
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
        
        # Vincular campos para cálculo automático
        cantidad_input.bind(text=calcular_total_repuesto)
        precio_input.bind(text=calcular_total_repuesto)
        
        # ✅ Agregar todos los widgets a la fila horizontal
        contenedor_repuesto.add_widget(nombre_label)    # Nombre
        contenedor_repuesto.add_widget(cantidad_input)  # Cantidad
        contenedor_repuesto.add_widget(precio_input)    # Precio
        contenedor_repuesto.add_widget(total_label)     # Total
        contenedor_repuesto.add_widget(boton_eliminar)  # Botón X
        
        # Calcular total inicial
        calcular_total_repuesto(None, None)
        
        # Añadir la fila al grid_repuestos
        self.ids.grid_repuestos.add_widget(contenedor_repuesto)
        
        # Scroll automático
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
        
        return {
            'contenedor': contenedor_repuesto,
            'nombre': nombre_label,
            'cantidad': cantidad_input,
            'precio': precio_input,
            'total': total_label,
            'repuesto_data': repuesto
        }
       
       
            
    def generar_nota_entrega(self, filename="nota_entrega.pdf"):
        """
        Genera un PDF con la nota de entrega basada en los datos de la FichaRectificadora.
        Extrae los datos exactamente como lo hace generar_ficha_pdf.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        import os

        try:
            # --- 1. Preparar datos ---
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            base_folder = os.path.join(desktop, "Fichas")

            # Obtener número de ficha
            numero_ficha = str(self.numero_ficha)

            # --- 2. Crear rutas ---
            ficha_folder = os.path.join(base_folder, f"Ficha Nº{numero_ficha}")
            pdf_filename = f"Nota de Entrega Nº{numero_ficha}.pdf"
            filepath = os.path.join(ficha_folder, pdf_filename)

            # --- 3. Crear carpetas si no existen ---
            os.makedirs(ficha_folder, exist_ok=True)

            # --- 4. Recopilar datos de la interfaz ---
            datos_cliente = {
                'rif': self.ids.tipo_rif.text + self.ids.nuevo_rif.text.strip(),
                'nombre': self.ids.nuevo_cliente.text.strip(),
                'telefono': self.ids.nuevo_telefono.text.strip(),
                'direccion': self.ids.nueva_direccion.text.strip(),
                'fecha': self.ids.nueva_fecha.text
            }

            datos_motor = {
                'tipo': self.ids.tipo_motor.text,
                'marca': self.ids.marca.text.strip(),
                'modelo': self.ids.motor.text.strip(),
                'cilindraje': self.ids.Cilindraje.text.strip(),
                'serial': self.ids.serial_motor.text.strip()
            }

            # --- 5. Recopilar partes recibidas ---
            # --- 5. Recopilar partes recibidas (fijas + dinámicas) ---
            partes_recibidas = []

            # a) Partes fijas (30 campos predefinidos)
            nombres_partes = [
                'Cigueñal', 'Bujias', 'Polea', 'Multiple', 'Bloque', 'Bodis',
                'Volante', 'Carter', 'Tapas de Bancada', 'Puntas', 'Engranajes', 'Camisas',
                'Árbol de Leva', 'Esparragos', 'Balancines', 'Cámaras', 'Tapa Válvulas', 'Toma de Agua',
                'Válvulas Adm', 'Bielas', 'Chambers', 'Válvulas Esc.', 'Tapas de Bielas', 'Bomba de Aceite',
                'Resortes', 'Camarin', 'Toma de Agua 2', 'Cuñadas', 'Pasador', 'Base de Agua'
            ]

            for i in range(1, 31):
                cantidad_id = f'cantidad_grid_{i}'
                if hasattr(self.ids, cantidad_id):
                    cantidad = getattr(self.ids, cantidad_id).text.strip()
                    if cantidad and cantidad != '0':
                        nombre_parte = nombres_partes[i - 1] if i <= len(nombres_partes) else f"Parte {i}"
                        partes_recibidas.append({
                            'nombre': nombre_parte,
                            'cantidad': cantidad
                        })

            # b) Partes dinámicas (agregadas con el botón "+")
            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout:
                # Los widgets están en orden inverso en children
                widgets = list(reversed(grid_layout.children))
                # Procesar de 3 en 3: [cantidad, pieza, botón]
                for i in range(0, len(widgets), 3):
                    if i + 2 < len(widgets):
                        cantidad_widget = widgets[i]      # TextInput Cantidad
                        pieza_widget = widgets[i + 1]     # TextInput Pieza
                        # Validar que sean los widgets correctos
                        if (isinstance(cantidad_widget, TextInput) and 
                            isinstance(pieza_widget, TextInput) and
                            getattr(cantidad_widget, 'hint_text', None) == "Cantidad" and
                            getattr(pieza_widget, 'hint_text', None) == "Pieza"):
                            cantidad = cantidad_widget.text.strip()
                            nombre_pieza = pieza_widget.text.strip()
                            if nombre_pieza and cantidad and cantidad != '0':
                                partes_recibidas.append({
                                    'nombre': nombre_pieza,
                                    'cantidad': cantidad
                                })

            # --- 6. Recopilar mano de obra y repuestos (EXACTAMENTE COMO EN generar_ficha_pdf) ---

            # Inicializar listas para el PDF
            mano_obra = []   # Para trabajos
            repuestos = []   # Para repuestos asociados a operadores
            observaciones = []  # Opcional: si quieres incluir observaciones

            if hasattr(self.ids, 'grid_mano_obra'):
                # Iterar sobre cada bloque de operador - INVERTIR EL ORDEN DE LOS OPERADORES
                operadores = list(self.ids.grid_mano_obra.children)
                operadores.reverse()  # Invierte la lista de operadores

                for contenedor_mano_obra_completo in operadores:
                    if not contenedor_mano_obra_completo.children:
                        continue
                    contenedor_operador = contenedor_mano_obra_completo.children[0]  # El contenedor del operador

                    # Extraer el nombre del operador
                    operador_nombre = "N/A"
                    for child in contenedor_operador.children:
                        if isinstance(child, BoxLayout):  # Es el header
                            for subchild in child.children:
                                if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                                    operador_nombre = subchild.text.replace("Operador:", "").strip()
                                    break

                    # --- SECCIÓN: TRABAJOS DEL OPERADOR ---
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        trabajos_container = contenedor_operador.trabajos_container
                        # Extraer los datos de las filas de trabajo - INVERTIR EL ORDEN DE LOS TRABAJOS
                        filas_trabajo = list(trabajos_container.children)  # Obtener la lista de filas
                        filas_trabajo.reverse()  # Invertir el orden
                        for fila_layout in filas_trabajo:  # Iterar sobre la lista invertida
                            if isinstance(fila_layout, BoxLayout) and len(fila_layout.children) == 6:
                                children = fila_layout.children
                                trabajo_widget = children[5]  # TextInput Trabajo
                                cantidad_widget = children[4]  # TextInput Cantidad
                                precio_widget = children[2]  # TextInput Precio
                                total_widget = children[3]  # TextInput Total
                                # Validar que tengan texto
                                if (hasattr(trabajo_widget, 'text') and 
                                    hasattr(cantidad_widget, 'text') and
                                    hasattr(precio_widget, 'text') and
                                    hasattr(total_widget, 'text')):
                                    trabajo_texto = trabajo_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    precio_texto = precio_widget.text.strip()
                                    total_texto = total_widget.text.strip()
                                    if trabajo_texto:  # Solo agregar si hay descripción
                                        # Convertir a números para cálculos
                                        try:
                                            cantidad_num = float(cantidad_texto) if cantidad_texto else 0
                                            precio_num = float(precio_texto) if precio_texto else 0
                                            total_num = float(total_texto) if total_texto else 0
                                        except ValueError:
                                            cantidad_num = 0
                                            precio_num = 0
                                            total_num = 0

                                        # Añadir a la lista de mano de obra para el PDF
                                        mano_obra.append({
                                            'operador': operador_nombre,
                                            'descripcion': trabajo_texto,
                                            'cantidad': cantidad_num,
                                            'precio': precio_num,
                                            'total': total_num
                                        })

                    # --- SECCIÓN: REPUESTOS ASOCIADOS AL OPERADOR ---
                    if hasattr(contenedor_operador, 'repuestos_container'):
                        repuestos_container = contenedor_operador.repuestos_container
                        # Extraer los datos de las filas de repuesto - INVERTIR EL ORDEN DE LOS REPUESTOS
                        filas_repuesto = list(repuestos_container.children)  # Obtener la lista de filas de repuesto
                        filas_repuesto.reverse()  # Invertir el orden
                        for fila_repuesto in filas_repuesto:  # Iterar sobre la lista invertida
                            if isinstance(fila_repuesto, BoxLayout) and len(fila_repuesto.children) == 6:
                                children = fila_repuesto.children
                                nombre_widget = children[4]  # Label Nombre (índice 5 en orden inverso)
                                cantidad_widget = children[3]  # TextInput Cantidad
                                precio_widget = children[2]  # TextInput Precio
                                total_widget = children[1]  # TextInput Total (ajustar según tu estructura)
                                # Validar que tengan texto
                                if (hasattr(nombre_widget, 'text') and 
                                    hasattr(cantidad_widget, 'text') and
                                    hasattr(precio_widget, 'text') and
                                    hasattr(total_widget, 'text')):
                                    nombre_texto = nombre_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    precio_texto = precio_widget.text.strip()
                                    total_texto = total_widget.text.strip()
                                    # Validar que haya nombre Y cantidad > 0
                                    if nombre_texto and cantidad_texto.strip():  # Asegurar que haya texto en cantidad
                                        try:
                                            cantidad_num = float(cantidad_texto)
                                            if cantidad_num <= 0:  # Ignorar si es 0 o negativo
                                                continue  # Salta esta fila
                                        except (ValueError, TypeError):
                                            continue  # Si no se puede convertir, ignorar

                                        try:
                                            precio_num = float(precio_texto) if precio_texto.strip() else 0.0
                                            total_num = float(total_texto) if total_texto.strip() else 0.0
                                        except (ValueError, TypeError):
                                            precio_num = 0.0
                                            total_num = 0.0

                                        # Añadir a la lista de repuestos para el PDF
                                        repuestos.append({
                                            'operador': operador_nombre,
                                            'nombre': nombre_texto,
                                            'cantidad': cantidad_num,
                                            'precio': precio_num,
                                            'total': total_num
                                        })
                    # --- SECCIÓN: OBSERVACIONES DEL OPERADOR (si existe) ---
                    if hasattr(contenedor_operador, '_observacion_input'):
                        observacion_input = contenedor_operador._observacion_input
                        if hasattr(observacion_input, 'text'):
                            observacion_texto = observacion_input.text.strip()
                            if observacion_texto:  # Solo si tiene contenido
                                observaciones.append({
                                    'operador': operador_nombre,
                                    'texto': observacion_texto
                                })

            # --- 7. Recopilar totales ---
            # Usar los valores ya calculados en la interfaz
            totales = {
                'total_mano_obra': self.ids.total_mano_obra.text,
                'total_repuestos': self.ids.total_repuestos.text,
                'subtotal': self.ids.subtotal.text,
                'iva': self.ids.iva.text,
                'total_general': self.ids.total_general.text,
                'anticipo': self.ids.anticipo.text,
                'saldo': self.ids.saldo.text
            }

            # --- 8. Generar el PDF ---
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            cell_style = styles["Normal"]
            cell_style.wordWrap = 'CJK' 

            # --- Título ---
            titulo = Paragraph(f"<b>NOTA DE ENTREGA</b>", styles['Heading1'])
            elements.append(titulo)
            elements.append(Spacer(1, 0.2*inch))

            subtitulo = Paragraph(f"<b>Rectificación Ficha Nº {numero_ficha}</b>", styles['Heading2'])
            elements.append(subtitulo)
            elements.append(Spacer(1, 0.2*inch))

            # --- Datos del Cliente ---
            elements.append(Paragraph("<b>DATOS DEL CLIENTE</b>", styles['Heading3']))
            data_cliente = [
                ["RIF:", datos_cliente['rif'], "Cliente:", datos_cliente['nombre']],
                ["Teléfono:", datos_cliente['telefono'], "Fecha:", datos_cliente['fecha']],
                ["Dirección:", datos_cliente['direccion'], "", ""],
            ]

            tabla_cliente = Table(data_cliente, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch], rowHeights=0.3*inch)
            tabla_cliente.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
            ]))
            elements.append(tabla_cliente)
            elements.append(Spacer(1, 0.2*inch))

            # --- Datos del Motor ---
            elements.append(Paragraph("<b>DATOS DEL MOTOR</b>", styles['Heading3']))
            data_motor = [
                ["Tipo:", datos_motor['tipo'], "Marca:", datos_motor['marca']],
                ["Modelo:", datos_motor['modelo'], "Cilindraje:", datos_motor['cilindraje']],
                ["Serial:", datos_motor['serial'], "", ""],
            ]

            tabla_motor = Table(data_motor, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch], rowHeights=0.3*inch)
            tabla_motor.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
            ]))
            elements.append(tabla_motor)
            elements.append(Spacer(1, 0.2*inch))

            # --- Partes Recibidas ---
            if partes_recibidas:
                elements.append(Paragraph("<b>PARTES RECIBIDAS</b>", styles['Heading3']))
                data_partes = [["Parte", "Cantidad"]]
                for parte in partes_recibidas:
                    data_partes.append([parte['nombre'], parte['cantidad']])
                
                tabla_partes = Table(data_partes, colWidths=[4*inch, 2*inch])
                tabla_partes.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                ]))
                elements.append(tabla_partes)
                elements.append(Spacer(1, 0.2*inch))

            # --- Mano de Obra ---
            if mano_obra:
                elements.append(Paragraph("<b>MANO DE OBRA</b>", styles['Heading3']))
                data_mano_obra = [["Trabajo", "Cantidad", "Precio", "Total"]]
                for trabajo in mano_obra:
                    descripcion = Paragraph(trabajo['descripcion'], cell_style)
                    data_mano_obra.append([
                        descripcion,
                        str(trabajo['cantidad']),
                        f"${trabajo['precio']:.2f}",
                        f"${trabajo['total']:.2f}"
                    ])
                
                tabla_mano_obra = Table(data_mano_obra, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch], repeatRows=1)
                tabla_mano_obra.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                ]))
                elements.append(tabla_mano_obra)
                elements.append(Spacer(1, 0.2*inch))

            # --- Repuestos ---
            if repuestos:
                elements.append(Paragraph("<b>REPUESTOS UTILIZADOS</b>", styles['Heading3']))
                data_repuestos = [["Nombre", "Cantidad", "Precio", "Total"]]
                for repuesto in repuestos:
                    nombre = Paragraph(repuesto['nombre'], cell_style)
                    data_repuestos.append([
                        nombre,
                        str(repuesto['cantidad']),
                        f"${repuesto['precio']:.2f}",
                        f"${repuesto['total']:.2f}"
                    ])
                
                tabla_repuestos = Table(data_repuestos, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch], repeatRows=1)
                tabla_repuestos.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                ]))
                elements.append(tabla_repuestos)
                elements.append(Spacer(1, 0.2*inch))

            # --- Observaciones (opcional) ---
            if observaciones:
                elements.append(Paragraph("<b>OBSERVACIONES</b>", styles['Heading3']))
                for obs in observaciones:
                    elements.append(Paragraph(f"<b>{obs['operador']}:</b> {obs['texto']}", styles['Normal']))
                    elements.append(Spacer(1, 0.1*inch))

            # --- Totales ---
            elements.append(Paragraph("<b>RESUMEN FINANCIERO</b>", styles['Heading3']))
            data_totales = [
                ["Total Mano de Obra:", totales['total_mano_obra']],
                ["Total Repuestos:", totales['total_repuestos']],
                ["Subtotal:", totales['subtotal']],
                ["I.V.A (16%):", totales['iva']],
                ["TOTAL GENERAL:", totales['total_general']],
                ["Anticipo:", totales['anticipo']],
                ["SALDO PENDIENTE:", totales['saldo']]
            ]
            
            tabla_totales = Table(data_totales, colWidths=[3*inch, 2*inch])
            tabla_totales.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (0, 4), (-1, 4), (0.8, 0.8, 0.8)),  # Total general
                ('BACKGROUND', (0, 7), (-1, 7), (1, 0.8, 0.8)),    # Saldo
            ]))
            elements.append(tabla_totales)

            # Construir PDF
            doc.build(elements)
            print(f"✅ Nota de entrega generada: {filepath}")
            self.ids.mensaje_estado.text = f"✅ Nota de entrega generada en el escritorio"

            # Abrir el PDF automáticamente
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(filepath)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", filepath])
                else:  # Linux y otros
                    subprocess.run(["xdg-open", filepath])
            except Exception as open_err:
                print(f"⚠️ No se pudo abrir el PDF automáticamente: {open_err}")

        except Exception as e:
            print(f"❌ Error al generar nota de entrega: {e}")
            if hasattr(self, 'ids') and hasattr(self.ids, 'mensaje_estado'):
                self.ids.mensaje_estado.text = f"❌ Error al generar PDF: {str(e)}"
    
    
    def generar_ficha_pdf(self, filename="ficha_rectificadora.pdf"):
        """
        Genera un PDF de la ficha rectificadora sin precios, solo información técnica.
        Organiza los datos por operador, como se muestra en la imagen.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        import os

        try:
            # --- 1. Preparar datos ---
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            base_folder = os.path.join(desktop, "Fichas")

            # Obtener número de ficha
            numero_ficha = str(self.numero_ficha)

            # --- 2. Crear rutas ---
            ficha_folder = os.path.join(base_folder, f"Ficha Nº{numero_ficha}")
            pdf_filename = f"Ficha Rectificadora Nº{numero_ficha}.pdf"
            filepath = os.path.join(ficha_folder, pdf_filename)

            # --- 3. Crear carpetas si no existen ---
            os.makedirs(ficha_folder, exist_ok=True)

            # --- 4. Recopilar datos de la interfaz ---
            datos_cliente = {
                'rif': self.ids.tipo_rif.text + self.ids.nuevo_rif.text.strip(),
                'nombre': self.ids.nuevo_cliente.text.strip(),
                'telefono': self.ids.nuevo_telefono.text.strip(),
                'direccion': self.ids.nueva_direccion.text.strip(),
                'fecha': self.ids.nueva_fecha.text
            }

            datos_motor = {
                'tipo': self.ids.tipo_motor.text,
                'marca': self.ids.marca.text.strip(),
                'modelo': self.ids.motor.text.strip(),
                'cilindraje': self.ids.Cilindraje.text.strip(),
                'serial': self.ids.serial_motor.text.strip()
            }

            # --- 5. Recopilar partes recibidas ---
            partes_recibidas = []


            # --- 6. Generar el PDF ---
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            cell_style = styles["Normal"]
            cell_style.wordWrap = 'CJK' 

            # --- Título ---
            titulo = Paragraph(f"<b>RECTIFICACIÓN: Ficha Nº {numero_ficha}</b>", styles['Heading1'])
            elements.append(titulo)
            elements.append(Spacer(1, 0.2*inch))

            # --- Datos del Cliente ---
            elements.append(Paragraph("<b>DATOS DEL CLIENTE</b>", styles['Heading3']))
            data_cliente = [
                ["Cliente:", datos_cliente['nombre'], "Fecha:", datos_cliente['fecha']],
                ["Tipo de Motor:", datos_motor['tipo'], "Marca:", datos_motor['marca']],
                ["Modelo:", datos_motor['modelo'], "Cilindraje:", datos_motor['cilindraje']]
            ]
            tabla_cliente = Table(data_cliente, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch], rowHeights=0.3*inch)
            tabla_cliente.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
            ]))
            elements.append(tabla_cliente)
            elements.append(Spacer(1, 0.2*inch))

            # --- Partes Recibidas ---
       

            # --- 7. PROCESAR CADA OPERADOR Y SUS TABLAS (como en la imagen) ---

            if hasattr(self.ids, 'grid_mano_obra'):
                # Iterar sobre cada bloque de operador - INVERTIR EL ORDEN DE LOS OPERADORES
                operadores = list(self.ids.grid_mano_obra.children)
                operadores.reverse()  # Invierte la lista de operadores
                for contenedor_mano_obra_completo in operadores:
                    if not contenedor_mano_obra_completo.children:
                        continue
                    contenedor_operador = contenedor_mano_obra_completo.children[0]  # El contenedor del operador

                    # Extraer el nombre del operador
                    operador_nombre = "N/A"
                    for child in contenedor_operador.children:
                        if isinstance(child, BoxLayout):
                            for subchild in child.children:
                                if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                                    # Limpiar etiquetas Kivy
                                    operador_raw = subchild.text.replace("Operador:", "").strip()
                                    operador_nombre = limpiar_etiquetas_kivy(operador_raw)
                                    break

                    # --- SECCIÓN: TRABAJOS DEL OPERADOR ---
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        trabajos_container = contenedor_operador.trabajos_container
                        # Extraer los datos de las filas de trabajo - INVERTIR EL ORDEN DE LOS TRABAJOS
                        trabajos = []
                        filas_trabajo = list(trabajos_container.children)  # Obtener la lista de filas
                        filas_trabajo.reverse()  # Invertir el orden
                        for fila_layout in filas_trabajo:  # Iterar sobre la lista invertida
                            if isinstance(fila_layout, BoxLayout) and len(fila_layout.children) == 6:
                                children = fila_layout.children
                                trabajo_widget = children[5]  # TextInput Trabajo
                                cantidad_widget = children[4]  # TextInput Cantidad
                                # Validar que tengan texto
                                if (hasattr(trabajo_widget, 'text') and 
                                    hasattr(cantidad_widget, 'text')):
                                    trabajo_texto = trabajo_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    if trabajo_texto:  # Solo agregar si hay descripción
                                        trabajos.append({
                                            'descripcion': trabajo_texto,
                                            'cantidad': cantidad_texto
                                        })

                        if trabajos:
                            # Añadir título del operador
                            elements.append(Paragraph(
                                f"<b>OPERADOR: {operador_nombre} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Ficha Nº {self.numero_ficha} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Fecha: {self.ids.nueva_fecha.text}</b>",
                                styles['Heading3']
                            ))
                            elements.append(Spacer(1, 0.1*inch))

                            # Tabla de trabajos - Invertir el orden de los trabajos en la tabla también
                            data_trabajos = [["Trabajo", "Cantidad"]]
                            for trabajo in trabajos:  # Invertir el orden de los trabajos para la tabla
                                descripcion_para_tabla = Paragraph(trabajo['descripcion'], cell_style)
                                data_trabajos.append([
                                    descripcion_para_tabla,
                                    trabajo['cantidad']
                                ])
                            tabla_trabajos = Table(data_trabajos, colWidths=[4*inch, 2*inch])
                            tabla_trabajos.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                                ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                            ]))
                            elements.append(tabla_trabajos)
                            elements.append(Spacer(1, 0.2*inch))

                    # --- SECCIÓN: REPUESTOS ASOCIADOS AL OPERADOR ---
                    if hasattr(contenedor_operador, 'repuestos_container'):
                        repuestos_container = contenedor_operador.repuestos_container
                        # Extraer los datos de las filas de repuesto - INVERTIR EL ORDEN DE LOS REPUESTOS
                        repuestos = []
                        filas_repuesto = list(repuestos_container.children)  # Obtener la lista de filas de repuesto
                        filas_repuesto.reverse()  # Invertir el orden
                        for fila_repuesto in filas_repuesto:  # Iterar sobre la lista invertida
                            if isinstance(fila_repuesto, BoxLayout) and len(fila_repuesto.children) == 6:
                                children = fila_repuesto.children
                                nombre_widget = children[4]  # Label Nombre (índice 5 en orden inverso)
                                cantidad_widget = children[3]  # TextInput Cantidad
                                # Validar que tengan texto
                                if (hasattr(nombre_widget, 'text') and 
                                    hasattr(cantidad_widget, 'text')):
                                    nombre_texto = nombre_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    if nombre_texto and cantidad_texto.strip():  # Asegurar que haya nombre y cantidad no vacía
                                        try:
                                            cantidad_num = float(cantidad_texto)
                                            if cantidad_num <= 0:  # Ignorar si es 0 o negativo
                                                continue  # Salta esta fila
                                        except (ValueError, TypeError):
                                            continue  # Si no se puede convertir, ignorar

                                        repuestos.append({
                                            'nombre': nombre_texto,
                                            'cantidad': str(int(cantidad_num)) if cantidad_num == int(cantidad_num) else str(cantidad_num)
                                        })

                        if repuestos:
                            # Añadir encabezado de repuestos
                            elements.append(Paragraph("<b>REPUESTOS ASOCIADOS</b>", styles['Heading3']))
                            elements.append(Spacer(1, 0.1*inch))

                            # Tabla de repuestos - Invertir el orden de los repuestos en la tabla también
                            data_repuestos = [["Nombre", "Cantidad"]]
                            for repuesto in repuestos:  # Invertir el orden de los repuestos para la tabla
                                nombre_para_tabla = Paragraph(repuesto['nombre'], cell_style)
                                data_repuestos.append([
                                    nombre_para_tabla,
                                    repuesto['cantidad']
                                ])
                            tabla_repuestos = Table(data_repuestos, colWidths=[4*inch, 2*inch])
                            tabla_repuestos.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                                ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                            ]))
                            elements.append(tabla_repuestos)
                            elements.append(Spacer(1, 0.2*inch))
                            

                    # --- SECCIÓN: OBSERVACIONES DEL OPERADOR (si existe) --- Aqui vas111111111111111111111111111111111111111111111111111
                    if hasattr(contenedor_operador, '_observacion_input'):
                        # Extraer el texto de la observación
                        observacion_input = contenedor_operador._observacion_input
                        if hasattr(observacion_input, 'text'):
                            observacion_texto = observacion_input.text.strip()
                            print(f"🔍 Texto de observación extraído: '{observacion_texto}'")
                            print(f"📝 Contenido del TextInput de observación: {observacion_input.text}")
                            if observacion_texto:  # Solo si tiene contenido
                                # Añadir encabezado
                                elements.append(Paragraph("<b>OBSERVACIONES</b>", styles['Heading3']))
                                elements.append(Spacer(1, 0.1*inch))

                                # Añadir el texto de la observación como un Paragraph
                                observacion_paragraph = Paragraph(
                                    f"{observacion_texto}",
                                    styles['Normal']
                                )
                                # Para que el texto se ajuste al ancho de la página, usamos un Table con una sola celda
                                tabla_observacion = Table([[observacion_paragraph]], colWidths=[6*inch])
                                tabla_observacion.setStyle(TableStyle([
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                                    ('BACKGROUND', (0, 0), (-1, -1), (0.9, 0.9, 0.9)),
                                ]))
                                elements.append(tabla_observacion)
                                elements.append(Spacer(1, 0.2*inch))

            # Construir PDF
            doc.build(elements)
            print(f"Ficha PDF generada: {filepath}")
            self.ids.mensaje_estado.text = f"Ficha PDF generada en el escritorio"

            # Abrir el PDF automáticamente
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(filepath)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", filepath])
                else:  # Linux y otros
                    subprocess.run(["xdg-open", filepath])
            except Exception as open_err:
                print(f"No se pudo abrir el PDF automáticamente: {open_err}")

        except Exception as e:
            print(f" Error al generar ficha PDF: {e}")
            if hasattr(self, 'ids') and hasattr(self.ids, 'mensaje_estado'):
                self.ids.mensaje_estado.text = f" Error al generar PDF: {str(e)}"

    def _crear_fila_trabajo_con_datos(self, contenedor_trabajos, contenedor_completo, nombre=""):
        """Crea una fila de trabajo con datos predefinidos (usado desde popup)."""
        from kivy.uix.checkbox import CheckBox
        from kivy.metrics import dp

        # Encontrar trabajos_container
        trabajos_container = None
        for child in contenedor_trabajos.children:
            if hasattr(child, 'orientation') and child.orientation == 'vertical':
                trabajos_container = child
                break
        if not trabajos_container:
            print("❌ No se encontró trabajos_container")
            return

        weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]
        fila_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35),
            spacing=2
        )

        trabajo_input = TextInput(
            text=nombre,
            multiline=False,
            size_hint_x=weights[0],
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        cantidad_input = TextInput(
            text="",
            multiline=False,
            input_filter='float',
            size_hint_x=weights[1],
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        precio_input = TextInput(
            text="",
            multiline=False,
            input_filter='float',
            size_hint_x=weights[2],
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1)

        )
        total_input = TextInput(
            text="0.00",
            multiline=False,
            readonly=True,
            size_hint_x=weights[3],
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(0.9, 0.9, 0.9, 1)
        )
        terminado_check = CheckBox(
            active=False,
            size_hint_x=weights[4],
            size_hint_y=None,
            height=dp(35)
        )
        btn_eliminar_fila = Button(
            text='×',
            size_hint_x=weights[5],
            size_hint_y=None,
            height=dp(35),
            background_color=(0.7, 0.3, 0.3, 1)
        )
        if self.nivel_usuario ==1 :
            precio_input.readonly = True

        def calcular_total(*args):
            try:
                c = float(cantidad_input.text or 0)
                p = float(precio_input.text or 0)
                total_input.text = f"{c * p:.2f}"
            except:
                total_input.text = "0.00"
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

        cantidad_input.bind(text=calcular_total)
        precio_input.bind(text=calcular_total)

        def eliminar_esta_fila(instance):
            if fila_layout.parent:
                padre = fila_layout.parent
                padre.remove_widget(fila_layout)
                trabajos_container.height -= dp(40)
                contenedor_trabajos.height -= dp(40)
                contenedor_completo.height -= dp(40)

        btn_eliminar_fila.bind(on_press=eliminar_esta_fila)

        fila_layout.add_widget(trabajo_input)
        fila_layout.add_widget(cantidad_input)
        fila_layout.add_widget(precio_input)
        fila_layout.add_widget(total_input)
        fila_layout.add_widget(terminado_check)
        fila_layout.add_widget(btn_eliminar_fila)

        trabajos_container.add_widget(fila_layout)
        # Actualiza alturas
        trabajos_container.height += dp(40)
        contenedor_trabajos.height += dp(40)
        contenedor_completo.height += dp(10)
        if contenedor_trabajos.parent:
            contenedor_trabajos.parent.height += dp(40)
        if contenedor_trabajos.parent and contenedor_trabajos.parent.parent:
            contenedor_trabajos.parent.parent.height += dp(30)
        Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.2)



def limpiar_nombre_operador(texto_con_markup):
    """Elimina etiquetas de markup de Kivy y el prefijo 'Operador:'"""
    # Eliminar etiquetas de markup como [b], [/b], [color=...], etc.
    sin_markup = re.sub(r'\[.*?\]', '', texto_con_markup)
    # Eliminar el prefijo "Operador:" (con o sin espacios)
    nombre_limpio = sin_markup.replace("Operador:", "").strip()
    return nombre_limpio

#Metodo para limpiar nombre (NO)
        
class FichaRectificadoraModificar(FichaRectificadora):
    def __init__(self, ficha_datos, callback_guardado, nivel=None, **kwargs):
        self.ficha_datos = ficha_datos
        self.callback_guardado = callback_guardado
        self.es_modificacion = True
        # Llamar al __init__ del padre SIN pasar `nivel` al super(), 
        # porque el padre ya lo maneja como parámetro propio
        super().__init__(nivel=nivel, **kwargs)

    def inicializar_popup(self, dt):
        # No generar nuevo número, usar el existente
        self.numero_ficha = self.ficha_datos['numero_ficha']
        self.title = f'Modificar Ficha Rectificadora #{self.numero_ficha}'
        self.configurar_autocompletado()
        # Cargar datos después de configurar autocompletado
        btn_guardar = Button(text='Guardar Modificaciones')
        btn_guardar.bind(on_press=self.guardar_modificaciones)
        Clock.schedule_once(self.cargar_datos_existentes, 0.2)


    def configurar_autocompletado(self):
        """Configura los autocompletados para los campos relevantes"""
        try:
            # Autocompletado para tipo de motor
            if hasattr(self.ids, 'tipo_motor'):
                # Supongamos que tienes una forma de obtener tipos de motores
                # Por ahora, usaremos una lista simple
                tipos_motores = ['4 cilindros', '6 cilindros', 'V8', 'Otro']
                # En una aplicación real, esto vendría de la base de datos
                # Podrías usar un Spinner o un TextInput con sugerencias
                pass # Implementar lógica de autocompletado

            # Autocompletado para tipo de RIF
            if hasattr(self.ids, 'tipo_rif'):
                tipos_rif = ['V-', 'J-', 'E-', 'G-']
                # Implementar lógica de autocompletado
                pass

            # Autocompletado para motor (nombre del motor)
            if hasattr(self.ids, 'motor'):
                # Supongamos que tienes una lista de nombres de motores
                # En una aplicación real, esto provendría de una consulta a la base de datos
                # o una lista precargada.
                pass # Implementar lógica de autocompletado

            print("✅ Autocompletado configurado")

        except Exception as e:
            print(f"❌ Error al configurar autocompletado: {e}")

    def cargar_datos_existentes(self, dt):
        """Carga los datos existentes de la ficha en todos los campos"""
        try:
            # === DATOS DEL CLIENTE ===
            cliente = self.ficha_datos.get('cliente', {})
            rif = cliente.get('rif', 'V-')
            self.ids.tipo_rif.text = rif[:2] if len(rif) > 2 else 'V-'
            self.ids.nuevo_rif.text = rif[2:] if len(rif) > 2 else ''
            self.ids.nuevo_cliente.text = cliente.get('nombre', '')
            self.ids.nuevo_telefono.text = cliente.get('telefono', '')
            self.ids.nueva_direccion.text = cliente.get('direccion', '')
            self.ids.nueva_fecha.text = cliente.get('fecha_registro', '')

            # === DATOS DEL MOTOR ===
            motor = self.ficha_datos.get('motor', {})
            self.ids.tipo_motor.text = motor.get('tipo', 'Seleccionar')
            
            # Para campos con autocompletado, establecer texto directamente
            if hasattr(self.ids, 'motor') and hasattr(self.ids.motor, 'text'):
                nombre_motor = motor.get('nombre', '')
                if nombre_motor:
                    self.ids.motor.text = nombre_motor
            
            self.ids.serial_motor.text = motor.get('serial', '')
            self.ids.marca.text = motor.get('marca', '')
            self.ids.Cilindraje.text = motor.get('cilindraje', '')

            # === PARTES RECIBIDAS (Estáticas y Dinámicas) ===
            partes = self.ficha_datos.get('partes_recibidas', [])
            partes_dict = {}
            partes_dinamicas = []

            for p in partes:
                nombre_parte = p['parte'].lower()
                nombres_partes_estaticas = [
                    'ciguenal', 'bujias', 'polea', 'multiple', 'bloque', 'bodis',
                    'volante', 'carter', 'tapas_de_bancada', 'puntas', 'engranajes', 'camisas',
                    'arbol_de_leva', 'esparragos', 'balancines', 'camaras', 'tapa_valvulas', 'toma_de_agua',
                    'valvulas_adm', 'bielas', 'chambers', 'valvulas_esc', 'tapas_de_vielas', 'bomba_de_aceite',
                    'resortes', 'camarin', 'toma_de_agua2', 'cuñadas', 'pasador', 'base_de_agua'
                ]
                
                if nombre_parte in [n.lower() for n in nombres_partes_estaticas]:
                    partes_dict[nombre_parte] = p['cantidad']
                else:
                    partes_dinamicas.append(p)

            # Cargar partes estáticas
            nombres_partes = [
                'ciguenal', 'bujias', 'polea', 'multiple', 'bloque', 'bodis',
                'volante', 'carter', 'tapas_de_bancada', 'puntas', 'engranajes', 'camisas',
                'arbol_de_leva', 'esparragos', 'balancines', 'camaras', 'tapa_valvulas', 'toma_de_agua',
                'valvulas_adm', 'bielas', 'chambers', 'valvulas_esc', 'tapas_de_vielas', 'bomba_de_aceite',
                'resortes', 'camarin', 'toma_de_agua2', 'cuñadas', 'pasador', 'base_de_agua'
            ]

            for i, nombre in enumerate(nombres_partes, 1):
                cantidad = partes_dict.get(nombre.lower(), '')
                cantidad_id = f'cantidad_grid_{i}'
                if hasattr(self.ids, cantidad_id):
                    getattr(self.ids, cantidad_id).text = str(cantidad)

            # Cargar partes dinámicas
            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout:
                for parte_dinamica in partes_dinamicas:
                    nombre_pieza = parte_dinamica['parte']
                    cantidad_pieza = parte_dinamica['cantidad']
                    self._agregar_fila_dinamica_desde_bd(grid_layout, nombre_pieza, cantidad_pieza)
                    

            # === OBSERVACIÓN DE PARTES RECIBIDAS (desde BD) ===
            observacion_partes_bd = self.ficha_datos.get('observacion_partes_recibidas', '').strip()
            if observacion_partes_bd:
                self.agregar_observacion_partes_recibidas()
                if hasattr(self, '_observacion_partes_widget') and self._observacion_partes_widget:
                    self._observacion_partes_widget.text = observacion_partes_bd
                    print(f"✅ Observación de partes recibidas cargada: {observacion_partes_bd[:50]}...")


            # === CARGAR MANO DE OBRA Y REPUESTOS (INTEGRADO POR OPERADOR) ===
            print(f"🔍 Cargando mano de obra y repuestos...")
            self.cargar_mano_obra_existente()  # Ahora carga trabajos Y repuestos por operador

            # === CARGAR OBSERVACIONES EXISTENTES (después de crear contenedores) ===
            observaciones = self.ficha_datos.get('observaciones', [])
            print(f"💬 Observaciones encontradas en la ficha: {len(observaciones)}")
            for o in observaciones:
                print(f"   - Operador: {o.get('operador', 'N/A')}, Texto: '{o.get('texto', '')}'")
            self.cargar_observaciones_existentes(observaciones)

            # === CARGAR TOTALES EXISTENTES ===
            totales = self.ficha_datos.get('totales', {})
            self.ids.total_mano_obra.text = f"${totales.get('total_mano_obra', 0):,.2f}"
            self.ids.total_repuestos.text = f"${totales.get('total_repuestos', 0):,.2f}"
            self.ids.subtotal.text = f"${totales.get('subtotal', 0):,.2f}"
            self.ids.iva.text = f"${totales.get('iva', 0):,.2f}"
            self.ids.total_general.text = f"${totales.get('total_general', 0):,.2f}"
            self.ids.anticipo.text = f"{totales.get('anticipo', 0):.2f}"
            self.ids.saldo.text = f"${totales.get('saldo', 0):,.2f}"
            self.ids.abonos.text = f"{totales.get('abonos', 0):.2f}"

            # Recalcular totales para asegurar consistencia visual (incluye repuestos cargados)
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.3)

            print(f" Datos cargados para ficha #{self.numero_ficha}")

        except Exception as e:
            print(f" Error al cargar datos existentes: {e}")
            import traceback
            traceback.print_exc()


    def cargar_mano_obra_existente(self):
        """Carga la mano de obra existente asociada a la ficha, incluyendo repuestos por operador"""
        try:
            # Los datos de mano de obra y repuestos están directamente en self.ficha_datos
            mano_obra_array = self.ficha_datos.get('mano_obra', [])
            repuestos_array = self.ficha_datos.get('repuestos', [])  # Repuestos desde la ficha
            
            print(f"🔍 Cargando mano de obra: {len(mano_obra_array)} elementos encontrados")
            print(f"📦 Cargando repuestos: {len(repuestos_array)} elementos encontrados")
            
            # Agrupar trabajos por operador
            operadores_trabajos = {}
            operadores_repuestos = {}  # NUEVO: Agrupar repuestos por operador
            
            for trabajo in mano_obra_array:
                operador_nombre = trabajo.get('operador', 'Sin operador')
                if operador_nombre not in operadores_trabajos:
                    operadores_trabajos[operador_nombre] = []
                operadores_trabajos[operador_nombre].append(trabajo)
            
            # NUEVO: Agrupar repuestos por operador (para cargarlos en el contenedor correcto)
            for repuesto in repuestos_array:
                operador_nombre = repuesto.get('operador', 'Sin operador')
                if operador_nombre not in operadores_repuestos:
                    operadores_repuestos[operador_nombre] = []
                operadores_repuestos[operador_nombre].append(repuesto)
            
            # Crear la interfaz para cada operador
            for operador_nombre, trabajos in operadores_trabajos.items():
                # ✅ 1. CREAR EL CONTENEDOR PRINCIPAL (igual que en crear_input_operador)
                contenedor_mano_obra_completo = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(370),  # Altura inicial estimada
                    spacing=5,
                    padding=[20, 10, 20, 10]
                )

                # ✅ 2. CREAR EL CONTENEDOR DEL OPERADOR
                contenedor_operador = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(300),  # Altura inicial estimada (se ajustará dinámicamente)
                    spacing=5,
                    padding=[10, 10, 10, 10]
                )

                # ✅ 3. HEADER DEL OPERADOR (Nombre y Botones)
                header_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40),
                    spacing=10,
                    padding=[0, 5, 0, 5]
                )

                operador_label = Label(
                    text=f"[b]Operador:[/b] {operador_nombre}",
                    size_hint_x=0.8,
                    size_hint_y=None,
                    height=dp(35),
                    font_size=16,
                    text_size=(None, dp(35)),
                    halign='left',
                    valign='middle',
                    color=(1, 1, 1, 1),
                    markup=True,
                    bold=True
                )

                # Fondo sólido para el label
                with operador_label.canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    rect_label = Rectangle(size=operador_label.size, pos=operador_label.pos)
                operador_label._bg_rect_label = rect_label
                def actualizar_fondo_label(instance, value):
                    if hasattr(instance, '_bg_rect_label'):
                        instance._bg_rect_label.pos = instance.pos
                        instance._bg_rect_label.size = instance.size
                operador_label.bind(pos=actualizar_fondo_label, size=actualizar_fondo_label)

                def eliminar_operador(instance):
                    self.ids.grid_mano_obra.remove_widget(contenedor_mano_obra_completo)
                    Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
                    Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
                    print("Operador eliminado y totales recalculados")

                btn_eliminar = Button(
                    text='×',
                    size_hint=(None, None),
                    size=(dp(35), dp(35)),
                    background_color=(0.8, 0.2, 0.2, 1),
                    font_size=18,
                    color=(1, 1, 1, 1),
                    bold=True
                )
                btn_eliminar.bind(on_press=eliminar_operador)

                btn_observacion = Button(
                    text='!',
                    size_hint=(None, None),
                    size=(dp(35), dp(35)),
                    background_color=(0.2, 0.2, 0.8, 1),
                    font_size=18,
                    color=(1, 1, 1, 1),
                    bold=True
                )
                btn_observacion.bind(on_press=lambda instance: self.agregar_bloque_observacion_a_operador(contenedor_operador, contenedor_mano_obra_completo))

                header_layout.add_widget(operador_label)
                header_layout.add_widget(btn_observacion)
                header_layout.add_widget(btn_eliminar)
                contenedor_operador.add_widget(header_layout)

                # ✅ 4. SEPARADOR VISUAL
                separador = Widget(
                    size_hint_y=None,
                    height=dp(10)
                )
                contenedor_operador.add_widget(separador)

                # ✅ 5. CONTENEDOR DE TRABAJOS
                contenedor_trabajos = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(35) + (len(trabajos) * dp(37)) + dp(20),  # Altura basada en trabajos
                    spacing=3,
                    padding=[0, 5, 0, 10]
                )

                # Headers de la tabla de trabajos
                headers_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(35),
                    spacing=2
                )

                headers = ['Trabajo', 'Cantidad', 'Precio', 'Total', 'Terminado']
                weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]

                for i, header in enumerate(headers):
                    label = Label(
                        text=header,
                        size_hint_x=weights[i],
                        color=(0.9, 0.9, 0.9, 1),
                        bold=True,
                        halign='center',
                        valign='middle'
                    )
                    headers_layout.add_widget(label)

                # Botón para agregar trabajo (heredado)
                btn_agregar_trabajo = Button(
                    text='+',
                    size_hint_x=weights[-1],
                    size_hint_y=None,
                    height=dp(35),
                    background_color=(0.2, 0.7, 0.2, 1)
                )
                
                if getattr(self, 'nivel_usuario', None) == 1:
                    btn_agregar_trabajo.disabled = True
                    btn_eliminar.disabled = True

                def abrir_popup_trabajos(instance, op_nombre=operador_nombre, cont_trab=contenedor_trabajos, cont_completo=contenedor_mano_obra_completo):
                    if not op_nombre or op_nombre == "(Seleccionar operador)":
                        self.agregar_fila_trabajo2(cont_trab)
                        return

                    # Obtener trabajos ya agregados
                    trabajos_actuales = []
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        for fila in contenedor_operador.trabajos_container.children:
                            if len(fila.children) >= 6:
                                trabajo_input = fila.children[5]
                                if hasattr(trabajo_input, 'text') and trabajo_input.text.strip():
                                    trabajos_actuales.append(trabajo_input.text.strip())

                    def on_trabajos_seleccionados(trabajos_seleccionados, custom_vacio):
                        for trabajo_nombre in trabajos_seleccionados:
                            # ✅ Aquí usamos LAS REFERENCIAS CORRECTAS capturadas por parámetro por defecto
                            self._crear_fila_trabajo_con_datos(cont_trab, cont_completo, nombre=trabajo_nombre)
                        if custom_vacio:
                            self._crear_fila_trabajo_con_datos(cont_trab, cont_completo, nombre="")
                        Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

                    popup = TrabajosOperadorPopup(
                        operador_nombre=op_nombre,
                        callback=on_trabajos_seleccionados,
                        trabajos_preseleccionados=trabajos_actuales
                    )
                    popup.open()

                btn_agregar_trabajo.bind(on_press=abrir_popup_trabajos)
                headers_layout.add_widget(btn_agregar_trabajo)
                contenedor_trabajos.add_widget(headers_layout)

                # ✅ 6. CONTENEDOR DE FILAS DE TRABAJO
                trabajos_container = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=len(trabajos) * dp(35),  # Altura basada en trabajos
                    spacing=2
                )
                contenedor_trabajos.add_widget(trabajos_container)
                contenedor_operador.add_widget(contenedor_trabajos)

                # ✅ 7. ETIQUETA DE SECCIÓN DE REPUESTOS
                repuestos_label = Label(
                    text="REPUESTOS ASOCIADOS AL OPERADOR",
                    size_hint_y=None,
                    height=dp(25),
                    font_size=12,
                    bold=True,
                    color=(0.9, 0.9, 0.9, 1),
                    halign='left',
                    valign='middle',
                    padding=[0, 5, 0, 0]
                )
                contenedor_operador.add_widget(repuestos_label)

                # ✅ 8. BOTÓN PARA AGREGAR REPUESTOS (heredado)
                btn_agregar_repuestos = Button(
                    text='+ Agregar Repuesto',
                    size_hint_y=None,
                    height=dp(35),
                    background_color=(0.2, 0.7, 0.2, 1),
                    font_size=12
                )
                if getattr(self, 'nivel_usuario', None) == 2:
                    btn_agregar_repuestos.disabled = True
                
                def abrir_popup_repuestos_para_operador(instance, cont_op=contenedor_operador, cont_completo=contenedor_mano_obra_completo):
                    def on_repuesto_seleccionado(repuesto):
                        self.agregar_repuesto_a_operador(cont_op, repuesto, cont_completo)
                    popup = RepuestosPopup(callback=on_repuesto_seleccionado)
                    popup.open()

                btn_agregar_repuestos.bind(on_press=abrir_popup_repuestos_para_operador)
                contenedor_operador.add_widget(btn_agregar_repuestos)

                # ✅ 9. CONTENEDOR DE REPUESTOS (con encabezado inicial)
                repuestos_container = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(40),  # Altura inicial para encabezado
                    spacing=2,
                    padding=[20, 0, 0, 0]
                )

                # Encabezado de repuestos
                fila_encabezado = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(35),
                    spacing=2
                )
                weights_rep = [0.2, 0.3, 0.15, 0.15, 0.15, 0.05]
                headers_rep = ['Código', 'Nombre', 'Cantidad', 'Precio', 'Total', 'Acción']
                for i, header in enumerate(headers_rep):
                    label = Label(
                        text=header,
                        size_hint_x=weights_rep[i],
                        color=(0.9, 0.9, 0.9, 1),
                        bold=True,
                        halign='center',
                        valign='middle'
                    )
                    fila_encabezado.add_widget(label)
                repuestos_container.add_widget(fila_encabezado)
                contenedor_operador.add_widget(repuestos_container)
                contenedor_operador.repuestos_container = repuestos_container  # Referencia clave

                # ✅ 10. GUARDAR REFERENCIAS CLAVE
                contenedor_operador.trabajos_container = trabajos_container
                contenedor_operador.operador_label = operador_label
                contenedor_operador.btn_eliminar = btn_eliminar

                # ✅ 11. AÑADIR EL CONTENEDOR DEL OPERADOR AL PRINCIPAL
                contenedor_mano_obra_completo.add_widget(contenedor_operador)

                # ✅ 12. AGREGAR TRABAJOS EXISTENTES (código original)
                for trabajo_data in trabajos:
                    self.agregar_trabajo_existente_cargado(contenedor_trabajos, trabajo_data)

                # ✅ NUEVO: AGREGAR REPUESTOS EXISTENTES PARA ESTE OPERADOR
                repuestos_del_operador = operadores_repuestos.get(operador_nombre, [])
                for repuesto_data in repuestos_del_operador:
                    self.agregar_repuesto_existente_a_operador(contenedor_operador, repuesto_data, contenedor_mano_obra_completo)

                # ✅ 13. AJUSTAR ALTURAS DINÁMICAS (para trabajos y repuestos)
                num_trabajos = len(trabajos)
                num_repuestos = len(repuestos_del_operador)
                trabajos_container.height = num_trabajos * dp(35)
                contenedor_trabajos.height = dp(35) + (num_trabajos * dp(37)) + dp(20)
                repuestos_container.height = dp(40) + (num_repuestos * dp(35))  # Encabezado + filas
                contenedor_operador.height = dp(300) + (num_trabajos * dp(35)) + (num_repuestos * dp(35))
                contenedor_mano_obra_completo.height = dp(370) + (num_trabajos * dp(35)) + (num_repuestos * dp(35))

                # ✅ 14. AÑADIR EL CONTENEDOR COMPLETO AL GRID
                self.ids.grid_mano_obra.add_widget(contenedor_mano_obra_completo)

                print(f"✅ Operador {operador_nombre} cargado: {num_trabajos} trabajos, {num_repuestos} repuestos")

            # ✅ 15. ACTUALIZAR ALTURA DEL GRID PRINCIPAL
            Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)

            print(f"✅ Mano de obra y repuestos cargados: {len(operadores_trabajos)} operadores")

        except Exception as e:
            print(f"❌ Error al cargar trabajos: {e}")

    def agregar_repuesto_existente_a_operador(self, contenedor_operador, repuesto_data, contenedor_mano_obra_completo):
        """Agrega un repuesto existente al contenedor de repuestos del operador (desde BD)"""
        try:
            from kivy.uix.textinput import TextInput
            from kivy.uix.button import Button
            from kivy.metrics import dp
            from kivy.clock import Clock

            # Obtener repuestos_container (debe existir desde cargar_mano_obra_existente)
            repuestos_container = getattr(contenedor_operador, 'repuestos_container', None)
            if not repuestos_container:
                print("❌ No se encontró repuestos_container para el operador")
                return

            # Crear fila de repuesto (estructura igual que en agregar_repuesto_a_operador)
            fila_repuesto = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            # Campo Código (desde BD)
            codigo_input = TextInput(
                text=str(repuesto_data.get('codigo', '')),
                multiline=False,
                readonly= True,
                size_hint_x=0.2,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Nombre (desde BD, readonly para evitar cambios accidentales, pero editable si quieres)
            nombre_input = TextInput(
                text=repuesto_data.get('nombre', ''),
                multiline=False,
                readonly = True,
                size_hint_x=0.3,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Cantidad (desde BD, editable)
            cantidad_input = TextInput(
                text=str(repuesto_data.get('cantidad', 1)),  # Valor de BD, no hardcoded "1"
                multiline=False,
                input_filter='float',
                size_hint_x=0.15,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Precio (desde BD, editable)
            precio_input = TextInput(
                text=f"{repuesto_data.get('precio', 0.0):.2f}",  # Valor de BD
                multiline=False,
                input_filter='float',
                size_hint_x=0.15,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Total (desde BD inicialmente, readonly pero se actualiza dinámicamente)
            total_input = TextInput(
                text=f"{repuesto_data.get('total', 0.0):.2f}",  # Valor de BD o calcular si no existe
                multiline=False,
                readonly=True,
                size_hint_x=0.15,
                font_size=12,
                foreground_color=(0.9, 0.9, 0.9, 1),
                background_color=(0.1, 0.1, 0.1, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Botón Eliminar
            btn_eliminar = Button(
                text='×',
                size_hint_x=0.05,
                size_hint_y=None,
                height=dp(35),
                background_color=(0.7, 0.3, 0.3, 1),
                color=(1, 1, 1, 1),
                bold=True,
                font_size=16
            )
            if getattr(self, 'nivel_usuario', None) == 2:
                precio_input.readonly = True
                precio_input.background_color = (0.15, 0.15, 0.15, 1)  
                precio_input.foreground_color = (0.6, 0.6, 0.6, 1)
                cantidad_input.readonly = True
                cantidad_input.background_color = (0.15, 0.15, 0.15, 1)  
                cantidad_input.foreground_color = (0.6, 0.6, 0.6, 1)
                btn_eliminar.disabled = True
            # Función para calcular total (igual que en la clase base)
            def calcular_total(*args):
                try:
                    c = float(cantidad_input.text or 0)
                    p = float(precio_input.text or 0)
                    nuevo_total = c * p
                    total_input.text = f"{nuevo_total:.2f}"
                except ValueError:
                    total_input.text = "0.00"
                # Recalcular totales globales
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            # Bindear eventos de cambio (editable como en la base)
            cantidad_input.bind(text=calcular_total)
            precio_input.bind(text=calcular_total)

            # Función de eliminación (igual que en la clase base, ajusta alturas)
            def eliminar_fila(instance):
                if fila_repuesto.parent:
                    # Remover la fila
                    fila_repuesto.parent.remove_widget(fila_repuesto)

                    # Reducir alturas de contenedores
                    repuestos_container.height -= dp(35)
                    contenedor_operador.height -= dp(35)
                    contenedor_mano_obra_completo.height -= dp(35)

                    # Verificar si quedan filas de datos (excluyendo encabezado)
                    filas_datos = [
                        child for child in repuestos_container.children
                        if isinstance(child, BoxLayout) and len(child.children) == 6  # Fila completa de repuesto
                    ]

                    # Si no quedan filas, opcionalmente remover encabezado (pero mantener contenedor vacío)
                    if len(filas_datos) == 0:
                        # Buscar y remover encabezado si quieres (opcional, para limpiar)
                        for child in repuestos_container.children:
                            if isinstance(child, BoxLayout) and len(child.children) == 5:  # Encabezado tiene 5 labels
                                repuestos_container.remove_widget(child)
                                break
                        repuestos_container.height = 0  # Ocultar si vacío

                    # Recalcular totales
                    Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

                    print(f"🗑️ Repuesto eliminado. Nueva altura repuestos_container: {repuestos_container.height:.0f}dp")

                else:
                    print("❌ La fila ya fue eliminada o no tiene padre")

            btn_eliminar.bind(on_press=eliminar_fila)

            # Agregar widgets a la fila (orden: código, nombre, cantidad, precio, total, botón)
            fila_repuesto.add_widget(codigo_input)
            fila_repuesto.add_widget(nombre_input)
            fila_repuesto.add_widget(cantidad_input)
            fila_repuesto.add_widget(precio_input)
            fila_repuesto.add_widget(total_input)
            fila_repuesto.add_widget(btn_eliminar)

            # Añadir la fila al contenedor (al inicio para orden inverso en Kivy)
            repuestos_container.add_widget(fila_repuesto, index=0)

            # Aumentar alturas de contenedores (igual que en la base)
            repuestos_container.height += dp(35)
            contenedor_operador.height += dp(35)
            contenedor_mano_obra_completo.height += dp(35)

            # Calcular total inicial (por si los datos de BD no coinciden)
            calcular_total()

            # Actualizar grid principal
            Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)

            print(f"✅ Repuesto existente agregado: {repuesto_data.get('nombre', 'N/A')} | Cant: {repuesto_data.get('cantidad', 1)} | Precio: {repuesto_data.get('precio', 0.0):.2f} | Total: {repuesto_data.get('total', 0.0):.2f}")

        except Exception as e:
            print(f"❌ Error al agregar repuesto existente a operador: {e}")
            import traceback
            traceback.print_exc()


    def agregar_trabajo_existente_cargado(self, contenedor_trabajos, trabajo_data):
        """Agrega una fila de trabajo existente desde la base de datos al contenedor de trabajos"""
        try:
            # Encontrar trabajos_container
            trabajos_container = None
            for child in contenedor_trabajos.children:
                if hasattr(child, 'orientation') and child.orientation == 'vertical':
                    trabajos_container = child
                    break
            if not trabajos_container:
                print("❌ No se encontró trabajos_container")
                return

            # Crear nueva fila
            weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]
            fila_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            trabajo_input = TextInput(
                text=trabajo_data.get('descripcion', ''),
                multiline=False,
                size_hint_x=weights[0],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )
            cantidad_input = TextInput(
                text=str(trabajo_data.get('cantidad', 1)),
                multiline=False,
                input_filter='float',
                size_hint_x=weights[1],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )
            precio_input = TextInput(
                text=f"{trabajo_data.get('precio', 0.0):.2f}",
                multiline=False,
                input_filter='float',
                size_hint_x=weights[2],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )
            total_input = TextInput(
                text=f"{trabajo_data.get('total', 0.0):.2f}",
                multiline=False,
                readonly=True,
                size_hint_x=weights[3],
                background_color=(0.15, 0.15, 0.15, 1),
                foreground_color=(0.9, 0.9, 0.9, 1)
            )
            terminado_check = CheckBox(
                active=trabajo_data.get('terminado', False),
                size_hint_x=weights[4],
                size_hint_y=None,
                height=dp(35)
            )
            btn_eliminar_fila = Button(
                text='×',
                size_hint_x=weights[5],
                size_hint_y=None,
                height=dp(35),
                background_color=(0.7, 0.3, 0.3, 1)
            )
            if getattr(self, 'nivel_usuario', None) == 1:
                precio_input.readonly = True
                precio_input.background_color = (0.15, 0.15, 0.15, 1)  
                precio_input.foreground_color = (0.6, 0.6, 0.6, 1)
                trabajo_input.readonly = True
                trabajo_input.background_color = (0.15, 0.15, 0.15, 1)  
                trabajo_input.foreground_color = (0.6, 0.6, 0.6, 1)
                cantidad_input.readonly = True
                cantidad_input.background_color = (0.15, 0.15, 0.15, 1)  
                cantidad_input.foreground_color = (0.6, 0.6, 0.6, 1)
                terminado_check.disabled = True
                btn_eliminar_fila.disabled = True

            # Función para calcular total
            def calcular_total(*args):
                try:
                    c = float(cantidad_input.text or 0)
                    p = float(precio_input.text or 0)
                    total_input.text = f"{c * p:.2f}"
                except:
                    total_input.text = "0.00"
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            cantidad_input.bind(text=calcular_total)
            precio_input.bind(text=calcular_total)

            # Eliminación: reduce altura
            def eliminar_esta_fila(instance):
                try:
                    if fila_layout.parent:
                        padre = fila_layout.parent
                        padre.remove_widget(fila_layout)

                        # REDUCIR ALTURA DE TODOS LOS CONTENEDORES
                        padre.height -= dp(35)
                        contenedor_trabajos.height -= dp(35)
                        
                        # Buscar contenedor_operador
                        contenedor_operador = contenedor_trabajos.parent
                        if contenedor_operador:
                            contenedor_operador.height -= dp(35)

                        # Buscar contenedor_mano_obra_completo
                        if hasattr(contenedor_operador, 'parent'):
                            contenedor_mano_obra_completo = contenedor_operador.parent
                            if contenedor_mano_obra_completo:
                                contenedor_mano_obra_completo.height -= dp(35)

                        # Actualizar grid principal
                        Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)

                        print(f"✅ Fila eliminada. Nueva altura: {padre.height:.0f}dp")

                except Exception as e:
                    print(f"❌ Error eliminando fila: {e}")

            btn_eliminar_fila.bind(on_press=eliminar_esta_fila)

            # Agregar widgets a la fila
            fila_layout.add_widget(trabajo_input)
            fila_layout.add_widget(cantidad_input)
            fila_layout.add_widget(precio_input)
            fila_layout.add_widget(total_input)
            fila_layout.add_widget(terminado_check)
            fila_layout.add_widget(btn_eliminar_fila)

            # AÑADIR LA FILA AL CONTENEDOR
            trabajos_container.add_widget(fila_layout, index=0)  # Al inicio (arriba)

            # AUMENTAR ALTURA DE TODOS LOS CONTENEDORES EN LA CADENA
            trabajos_container.height += dp(35)
            contenedor_trabajos.height += dp(35)

            # Obtener contenedor_operador (el padre de contenedor_trabajos)
            contenedor_operador = contenedor_trabajos.parent
            contenedor_operador.height += dp(35)

            # Obtener contenedor_mano_obra_completo (el padre del operador)
            contenedor_mano_obra_completo = contenedor_operador.parent
            contenedor_mano_obra_completo.height += dp(35)

            # Forzar actualización del ScrollView
            Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)

            print(f"✅ Fila de trabajo cargada. Nueva altura: {trabajos_container.height:.0f}dp")

        except Exception as e:
            print(f"❌ Error al agregar fila de trabajo existente: {e}")
    
    def cargar_observaciones_existentes(self, observaciones_array):
        """Carga las observaciones existentes asociadas a operadores desde la ficha"""
        try:
            print(f"🔍 Cargando observaciones: {len(observaciones_array)} elementos encontrados en total")
            
            if not observaciones_array:
                print("ℹ No hay observaciones para cargar.")
                return
            
            # Agrupar observaciones por operador
            operadores_observaciones = {}
            for obs in observaciones_array:
                operador_nombre = obs.get('operador', 'Sin operador')
                texto_obs = obs.get('texto', '').strip()
                if texto_obs:  # Solo agregar si tiene contenido
                    if operador_nombre not in operadores_observaciones:
                        operadores_observaciones[operador_nombre] = []
                    operadores_observaciones[operador_nombre].append(texto_obs)
            
            if not operadores_observaciones:
                print("ℹ No hay observaciones válidas después de filtrar.")
                return
            
            print(f"📋 Observaciones agrupadas por operador: {list(operadores_observaciones.keys())}")
            
            # Buscar cada contenedor de operador en la interfaz (creados en cargar_mano_obra_existente)
            if not hasattr(self.ids, 'grid_mano_obra') or not self.ids.grid_mano_obra.children:
                print("⚠️ No se encontraron contenedores de operadores en grid_mano_obra.")
                return
            
            num_cargadas = 0
            for contenedor_mano_obra_completo in self.ids.grid_mano_obra.children:
                if not contenedor_mano_obra_completo.children:
                    continue
                contenedor_operador = contenedor_mano_obra_completo.children[0]  # El contenedor del operador principal

                # Extraer el nombre del operador del header (Label con "Operador: Nombre")
                operador_nombre = "N/A"
                for child in contenedor_operador.children:
                    if isinstance(child, BoxLayout) and len(child.children) >= 3:  # Header con label + botones
                        for subchild in child.children:
                            if isinstance(subchild, Label) and hasattr(subchild, 'text') and "Operador:" in subchild.text:
                                operador_nombre = subchild.text.replace("[b]Operador:[/b] ", "").replace("Operador: ", "").strip()
                                break
                        if operador_nombre != "N/A":
                            break
                
                if operador_nombre == "N/A":
                    print(f"⚠️ No se pudo extraer nombre del operador para contenedor {contenedor_operador}")
                    continue
                
                # Verificar si hay observaciones para este operador
                observaciones_del_operador = operadores_observaciones.get(operador_nombre, [])
                if not observaciones_del_operador:
                    print(f"ℹ️ No hay observaciones para operador '{operador_nombre}'")
                    continue
                
                # Concatenar todas las observaciones del operador (separadas por salto de línea para legibilidad)
                texto_observacion = "\n".join(observaciones_del_operador)  # O usa " " para espacio simple
                print(f"📝 Observaciones para '{operador_nombre}': {len(observaciones_del_operador)} textos concatenados")
                
                # Verificar/crear el bloque de observación si no existe
                if not hasattr(contenedor_operador, '_observacion_widget'):
                    print(f"🔧 Creando bloque de observación para operador '{operador_nombre}'")
                    # Llamar al método heredado para crear el bloque (incluye input y botón eliminar)
                    self.agregar_bloque_observacion_a_operador(contenedor_operador, contenedor_mano_obra_completo)
                    # Esperar un tick para que se cree el input
                    Clock.schedule_once(lambda dt: self._setear_texto_observacion(contenedor_operador, texto_observacion), 0.1)
                    num_cargadas += 1
                else:
                    # El bloque ya existe, solo setear el texto
                    if hasattr(contenedor_operador, '_observacion_input'):
                        contenedor_operador._observacion_input.text = texto_observacion
                        print(f"✅ Observación actualizada para operador '{operador_nombre}': {len(texto_observacion)} caracteres")
                        num_cargadas += 1
                    else:
                        print(f"⚠️ Bloque de observación existe para '{operador_nombre}', pero no se encontró _observacion_input")
            
            print(f"✅ Carga de observaciones completada: {num_cargadas} operadores actualizados de {len(operadores_observaciones)} posibles")
            
        except Exception as e:
            print(f"❌ Error al cargar observaciones existentes: {e}")
            import traceback
            traceback.print_exc()

    def _setear_texto_observacion(self, contenedor_operador, texto):
        """Método auxiliar para setear texto de observación después de crear el bloque (privado)"""
        try:
            if hasattr(contenedor_operador, '_observacion_input'):
                contenedor_operador._observacion_input.text = texto
                # Ajustar altura si es necesario (opcional)
                if hasattr(contenedor_operador, 'height'):
                    contenedor_operador.height += len(texto.split('\n')) * 10  # Aproximado por líneas
            else:
                print("⚠️ _observacion_input no disponible aún")
        except Exception as e:
            print(f"❌ Error al setear texto de observación: {e}")

    def agregar_operador_con_trabajos_existentes(self, operador_data, trabajos_data):
        """Agrega un operador con sus trabajos existentes al grid de mano de obra"""
        try:
            # Crear contenedor principal para el operador
            operador_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(50) + len(trabajos_data) * dp(40) + dp(20),  # Header + trabajos + padding
                spacing=5,
                padding=[10, 5]
            )

            # Header del operador
            header_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=10
            )

            # Título del operador
            operador_label = Label(
                text=f"Operador: {operador_data.get('nombre', 'Sin nombre')}",
                size_hint_x=0.8,
                text_size=(None, None),
                halign='left',
                valign='middle',
                color=(1, 1, 1, 1)
            )

            # Botón para eliminar operador
            btn_eliminar = Button(
                text='X',
                size_hint=(None, None),
                size=(dp(30), dp(30)),
                background_color=(0.8, 0.2, 0.2, 1)
            )
            btn_eliminar.bind(on_press=lambda x: self.eliminar_operador(operador_container))

            header_layout.add_widget(operador_label)
            header_layout.add_widget(btn_eliminar)
            operador_container.add_widget(header_layout)

            # Headers de la tabla
            headers_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(30),
                spacing=2
            )

            headers = ['Trabajo', 'Cantidad', 'Precio', 'Total', 'Terminado']
            weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]

            for i, header in enumerate(headers):
                label = Label(
                    text=header,
                    size_hint_x=weights[i],
                    color=(0.9, 0.9, 0.9, 1),
                    bold=True
                )
                headers_layout.add_widget(label)

            # Botón para agregar trabajo
            btn_agregar = Button(
                text='+',
                size_hint_x=weights[-1],
                size_hint_y=None,
                height=dp(30),
                background_color=(0.2, 0.7, 0.2, 1)
            )
            btn_agregar.bind(on_press=lambda x: self.agregar_fila_trabajo(operador_container))
            headers_layout.add_widget(btn_agregar)

            operador_container.add_widget(headers_layout)

            # Agregar trabajos existentes
            for trabajo in trabajos_data:
                self.agregar_trabajo_existente(operador_container, trabajo)

            # Agregar el operador al grid principal
            self.ids.grid_mano_obra.add_widget(operador_container)
            self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height

            print(f"✅ Operador {operador_data['nombre']} agregado con {len(trabajos_data)} trabajos")

        except Exception as e:
            print(f"❌ Error al agregar operador con trabajos: {e}")

    def agregar_trabajo_existente(self, operador_container, trabajo_data):
        """Agrega una fila de trabajo existente"""
        try:
            fila_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]

            # Campo descripción del trabajo
            trabajo_input = TextInput(
                text=trabajo_data.get('descripcion', ''),
                multiline=False,
                size_hint_x=weights[0],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )

            # Campo cantidad
            cantidad_input = TextInput(
                text=str(trabajo_data.get('cantidad', 1)),
                multiline=False,
                input_filter='float',
                size_hint_x=weights[1],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )

            # Campo precio
            precio_input = TextInput(
                text=f"{trabajo_data.get('precio', 0.0):.2f}",
                multiline=False,
                input_filter='float',
                size_hint_x=weights[2],
                background_color=(0.2, 0.2, 0.2, 1),
                foreground_color=(1, 1, 1, 1)
            )

            # Campo total (calculado)
            total_input = TextInput(
                text=f"{trabajo_data.get('total', 0.0):.2f}",
                multiline=False,
                readonly=True,
                size_hint_x=weights[3],
                background_color=(0.15, 0.15, 0.15, 1),
                foreground_color=(0.9, 0.9, 0.9, 1)
            )

            # Checkbox terminado
            terminado_check = CheckBox(
                active=trabajo_data.get('terminado', False),
                size_hint_x=weights[4],
                size_hint_y=None,
                height=dp(35)
            )

            # Botón eliminar fila
            btn_eliminar_fila = Button(
                text='×',
                size_hint_x=weights[5],
                size_hint_y=None,
                height=dp(35),
                background_color=(0.7, 0.3, 0.3, 1)
            )

            # Función para calcular total
            def calcular_total(*args):
                try:
                    cantidad = float(cantidad_input.text or 0)
                    precio = float(precio_input.text or 0)
                    total_input.text = f"{cantidad * precio:.2f}"
                except:
                    total_input.text = "0.00"

            # Bind para cálculo automático
            cantidad_input.bind(text=calcular_total)
            precio_input.bind(text=calcular_total)

            # Bind para eliminar fila
            btn_eliminar_fila.bind(on_press=lambda x: self.eliminar_fila_trabajo(operador_container, fila_layout))

            # Agregar widgets a la fila
            fila_layout.add_widget(trabajo_input)
            fila_layout.add_widget(cantidad_input)
            fila_layout.add_widget(precio_input)
            fila_layout.add_widget(total_input)
            fila_layout.add_widget(terminado_check)
            fila_layout.add_widget(btn_eliminar_fila)

            # Agregar la fila al contenedor del operador
            operador_container.add_widget(fila_layout)

            print(f"✅ Trabajo agregado: {trabajo_data.get('descripcion', 'Sin descripción')}")

        except Exception as e:
            print(f"❌ Error al agregar trabajo existente: {e}")

    def eliminar_operador(self, operador_container):
        """Elimina un operador completo del grid"""
        self.ids.grid_mano_obra.remove_widget(operador_container)
        self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height

    def eliminar_fila_trabajo(self, operador_container, fila_layout):
        """Elimina una fila de trabajo específica"""
        operador_container.remove_widget(fila_layout)
        # Recalcular altura del contenedor del operador
        operador_container.height = dp(50) + (len(operador_container.children) - 2) * dp(35) + dp(20)
        self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height



    def guardar_modificaciones(self):
        """Guarda las modificaciones realizadas en la ficha existente (NO crea una nueva)"""
        try:
            # Recopilar todos los datos modificados
            datos_modificados = self.recopilar_datos_ficha()
            if not datos_modificados:
                print("❌ No hay datos válidos para guardar.")
                return

            # Asegurar que numero_ficha sea del tipo correcto (entero)
            numero_ficha = int(self.numero_ficha)

            # Conexión a MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            fichas_collection = db['fichas']

            # Verificar que la ficha existe antes de intentar actualizarla
            ficha_existente = fichas_collection.find_one({"numero_ficha": numero_ficha})
            if not ficha_existente:
                print(f"❌ La ficha #{numero_ficha} no existe en la base de datos. No se puede modificar.")
                client.close()
                return

            # Actualizar SOLO los campos modificables (sin tocar _id, fecha_creacion, etc.)
            result = fichas_collection.update_one(
                {"numero_ficha": numero_ficha},
                {"$set": datos_modificados}
            )

            if result.modified_count > 0:
                print(f"✅ Ficha #{numero_ficha} actualizada exitosamente.")
                if self.callback_guardado:
                    self.callback_guardado()
                self.dismiss()
            else:
                print(f"ℹ️ Ficha #{numero_ficha}: no hubo cambios detectados (no se modificó nada).")
                # Opcional: igual ejecutar callback si se desea reflejar "sin cambios"
                if self.callback_guardado:
                    self.callback_guardado()
                self.dismiss()

            client.close()

        except ValueError as ve:
            print(f"❌ Error de formato en número de ficha: {ve}")
        except Exception as e:
            print(f"❌ Error al guardar modificaciones: {e}")
            import traceback
            traceback.print_exc()


class OperadorBlock(BoxLayout):
    def __init__(self, operador_nombre, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=(0, 5, 0, 5), **kwargs)
        self.operador_nombre = operador_nombre
        self.trabajos_container = None  # Se inicializa abajo

        # --- NOMBRE DEL OPERADOR ---
        self.nombre_input = TextInput(
            text=operador_nombre,
            readonly=True,
            font_size=16,
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=40,
            padding=[10, 5]
        )
        self.add_widget(self.nombre_input)

        # --- CONTENEDOR DE TRABAJOS ---
        self.trabajos_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5
        )
        self.add_widget(self.trabajos_container)

        # --- FONDO SUAVE ---
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 0.1)  # Gris muy claro
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def agregar_trabajo(self):
        """Añade una nueva fila de trabajo: Trabajo | Cantidad | Precio | Total"""
        row = BoxLayout(size_hint_y=None, height=35, spacing=5)

        # Campos
        txt_trabajo = TextInput(hint_text='Nombre del trabajo', multiline=False, size_hint_x=0.4)
        txt_cantidad = TextInput(hint_text='Cant.', input_filter='float', multiline=False, size_hint_x=0.15)
        txt_precio = TextInput(hint_text='Precio', input_filter='float', multiline=False, size_hint_x=0.15)
        txt_total = TextInput(hint_text='Total', readonly=True, background_color=(0.95, 0.95, 0.95, 1), size_hint_x=0.2)

        # Vincular cálculo automático
        def calcular_total(*args):
            try:
                cant = float(txt_cantidad.text) if txt_cantidad.text else 0
                precio = float(txt_precio.text) if txt_precio.text else 0
                total = cant * precio
                txt_total.text = f"{total:.2f}"
            except ValueError:
                txt_total.text = "0.00"

        txt_cantidad.bind(text=calcular_total)
        txt_precio.bind(text=calcular_total)

        # Añadir a la fila
        row.add_widget(txt_trabajo)
        row.add_widget(txt_cantidad)
        row.add_widget(txt_precio)
        row.add_widget(txt_total)

        self.trabajos_container.add_widget(row)
        self.trabajos_container.height += 35  # Ajusta altura manualmente

        return row 


class SelectableRepuestoLabel(BoxLayout):
    def __init__(self, repuesto, seleccionar_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 30
        self.repuesto = repuesto
        self.seleccionar_callback = seleccionar_callback

        # Widgets
        self.add_widget(Label(text=str(repuesto.get('codigo', 'N/A')), size_hint_x=0.2))
        self.add_widget(Label(text=repuesto.get('nombre', 'N/A'), size_hint_x=0.4))
        self.add_widget(Label(text=f"{repuesto.get('precio', 0.0):.2f}", size_hint_x=0.2))
        self.add_widget(Label(text=str(repuesto.get('existencia', 0)), size_hint_x=0.2))

        btn = Button(text="Seleccionar", size_hint_x=0.2)
        btn.bind(on_release=self.on_seleccionar)
        self.add_widget(btn)

    def on_seleccionar(self, *args):
        self.seleccionar_callback(self.repuesto)


class RepuestosPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Seleccionar Repuesto"
        self.size_hint = (0.95, 0.85)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- DOS CAMPOS DE FILTRO: ID y NOMBRE ---
        filtros_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        self.filtro_id = TextInput(hint_text='Filtrar por ID', size_hint_x=0.45)
        self.filtro_id.bind(text=self.on_filtro_change)
        filtros_layout.add_widget(self.filtro_id)
        
        self.filtro_nombre = TextInput(hint_text='Filtrar por nombre', size_hint_x=0.45)
        self.filtro_nombre.bind(text=self.on_filtro_change)
        filtros_layout.add_widget(self.filtro_nombre)
        
        layout.add_widget(filtros_layout)

        # --- ENCABEZADOS ---
        header = BoxLayout(size_hint_y=None, height=40, spacing=5)
        header.add_widget(Label(text="ID", size_hint_x=0.15, bold=True))
        header.add_widget(Label(text="Nombre", size_hint_x=0.45, bold=True))
        header.add_widget(Label(text="Precio", size_hint_x=0.15, bold=True))
        header.add_widget(Label(text="Cantidad", size_hint_x=0.15, bold=True))
        header.add_widget(Label(text="Acción", size_hint_x=0.10, bold=True))
        layout.add_widget(header)

        # --- LISTA SCROLLABLE ---
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        # --- BOTÓN CANCELAR ---
        btn_cancelar = Button(text="Cancelar", size_hint_y=None, height=50)
        btn_cancelar.bind(on_release=self.dismiss)
        layout.add_widget(btn_cancelar)

        self.content = layout
        self.cargar_repuestos()

    def cargar_repuestos(self):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['Repuestos']
            self.todos_repuestos = list(collection.find({}))
            client.close()
            print(f"✅ Cargados {len(self.todos_repuestos)} repuestos de BD")  # Debug
            self.filtrar_repuestos()
        except Exception as e:
            print(f"❌ Error al cargar repuestos: {e}")
            self.todos_repuestos = []
            if hasattr(self, 'grid'):  # Verificar que grid exista
                self.grid.add_widget(Label(text="Error al cargar repuestos", color=(1, 0, 0, 1)))
            else:
                print("⚠️ Grid no disponible para mostrar error")


    def on_filtro_change(self, instance, value):
        # Debounce: retrasar la búsqueda 300ms para no saturar
        if hasattr(self, '_filtro_event'):
            self._filtro_event.cancel()
        from kivy.clock import Clock
        self._filtro_event = Clock.schedule_once(lambda dt: self.filtrar_repuestos(), 0.3)

    def filtrar_repuestos(self, *args):
        filtro_id = self.filtro_id.text.strip().lower()
        filtro_nombre = self.filtro_nombre.text.strip().lower()

        coincidentes = []
        for repuesto in self.todos_repuestos:
            # Normalizar código a string
            codigo_str = str(repuesto.get('codigo', '')).strip().lower()
            nombre_str = str(repuesto.get('nombre', '')).strip().lower()

            # Aplicar ambos filtros (si están vacíos, no filtran)
            coincide_id = (not filtro_id) or (filtro_id in codigo_str)
            coincide_nombre = (not filtro_nombre) or (filtro_nombre in nombre_str)

            if coincide_id and coincide_nombre:
                coincidentes.append(repuesto)

        # Limitar a 10 resultados
        coincidentes = coincidentes[:10]

        # Renderizar
        self.grid.clear_widgets()
        print(f"🔍 Mostrando {len(coincidentes)} repuestos (ID: '{filtro_id}', Nombre: '{filtro_nombre}')")

        for repuesto in coincidentes:
            codigo = str(repuesto.get('codigo', ''))
            nombre_ui = str(repuesto.get('nombre', ''))
            precio = repuesto.get('precio', 0)
            existencia = repuesto.get('cantidad', 0)
            minima = repuesto.get('cantidad_minima', 0)

            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            lbl_codigo = Label(text=codigo, size_hint_x=0.15, halign='center', valign='middle')
            lbl_codigo.bind(size=lbl_codigo.setter('text_size'))

            lbl_nombre = Label(text=nombre_ui, size_hint_x=0.45, halign='left', valign='middle', shorten=True)
            lbl_nombre.bind(size=lbl_nombre.setter('text_size'))

            lbl_precio = Label(text=f"{precio:.2f}", size_hint_x=0.15, halign='center', valign='middle')
            lbl_precio.bind(size=lbl_precio.setter('text_size'))

            lbl_cantidad = Label(text=str(existencia), size_hint_x=0.15, halign='center', valign='middle')
            lbl_cantidad.bind(size=lbl_cantidad.setter('text_size'))

            btn = Button(text="Usar", size_hint_x=0.10, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn, r=repuesto: self.on_seleccionar(r))

            # Sombrear si stock bajo
            if existencia < minima:
                color = (1, 1, 0, 0.3)
                self.sombrear_label(lbl_codigo, color)
                self.sombrear_label(lbl_nombre, color)
                self.sombrear_label(lbl_precio, color)
                self.sombrear_label(lbl_cantidad, color)

            row.add_widget(lbl_codigo)
            row.add_widget(lbl_nombre)
            row.add_widget(lbl_precio)
            row.add_widget(lbl_cantidad)
            row.add_widget(btn)

            self.grid.add_widget(row)

    def on_seleccionar(self, repuesto):
        if self.callback:
            self.callback(repuesto)
        self.dismiss()

    def sombrear_label(self, label, color=(1, 1, 0, 0.3)):
        """Aplica un fondo de color a un Label."""
        if hasattr(label, '_bg_rect'):
            label.canvas.before.remove(label._bg_rect)
        if hasattr(label, '_bg_color_inst'):
            label.canvas.before.remove(label._bg_color_inst)

        with label.canvas.before:
            label._bg_color_inst = Color(*color)
            label._bg_rect = Rectangle(size=label.size, pos=label.pos)

        def update_bg(instance, value):
            if hasattr(label, '_bg_rect'):
                label._bg_rect.pos = instance.pos
                label._bg_rect.size = instance.size

        label.bind(pos=update_bg, size=update_bg)



class ClientesPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Seleccionar Cliente"
        self.size_hint = (0.9, 0.8)
        self.auto_dismiss = False

        # --- LAYOUT PRINCIPAL ---
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- BARRA DE BÚSQUEDA ---
        self.buscar_input = TextInput(
            hint_text='Buscar por nombre o RIF',
            size_hint_y=None,
            height=40
        )
        self.buscar_input.bind(text=self.filtrar_clientes)
        layout.add_widget(self.buscar_input)

        # --- ENCABEZADOS ---
        header = BoxLayout(size_hint_y=None, height=40, spacing=5)
        header.add_widget(Label(text="RIF", size_hint_x=0.25, bold=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text="Nombre", size_hint_x=0.4, bold=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text="Teléfono", size_hint_x=0.2, bold=True, color=(1, 1, 1, 1)))
        header.add_widget(Label(text="Acción", size_hint_x=0.15, bold=True, color=(1, 1, 1, 1)))
        layout.add_widget(header)

        # --- SCROLLVIEW + GRID ---
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        # --- BOTÓN CANCELAR ---
        btn_cancelar = Button(text="Cancelar", size_hint_y=None, height=50)
        btn_cancelar.bind(on_release=self.dismiss)
        layout.add_widget(btn_cancelar)

        self.content = layout

        # --- CARGAR CLIENTES ---
        self.cargar_clientes()

    def cargar_clientes(self):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            # Puedes usar 'clientes' o 'usuarios' según tu esquema
            collection = db['clientes']  # o db['usuarios']
            self.todos_clientes = list(collection.find({}))
            client.close()
            print(f"✅ Cargados {len(self.todos_clientes)} clientes de la base de datos")
            self.filtrar_clientes()
        except Exception as e:
            print(f"❌ Error al cargar clientes: {e}")
            self.todos_clientes = []
            self.grid.clear_widgets()
            self.grid.add_widget(Label(text="Error al conectar con la base de datos", color=(1, 0, 0, 1)))

    def filtrar_clientes(self, *args):
        query = self.buscar_input.text.strip().lower()

        self.grid.clear_widgets()

        for cliente in self.todos_clientes:
            rif = cliente.get('rif', '')
            nombre = cliente.get('nombre', '')
            telefono = cliente.get('telefono', '')

            # Buscar en RIF o nombre (ignorar mayúsculas)
            if query and query not in rif.lower() and query not in nombre.lower():
                continue

            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            lbl_rif = Label(text=rif, size_hint_x=0.25, halign='left', valign='middle')
            lbl_rif.bind(size=lbl_rif.setter('text_size'))

            lbl_nombre = Label(text=nombre, size_hint_x=0.4, halign='left', valign='middle')
            lbl_nombre.bind(size=lbl_nombre.setter('text_size'))

            lbl_telefono = Label(text=telefono, size_hint_x=0.2, halign='left', valign='middle')
            lbl_telefono.bind(size=lbl_telefono.setter('text_size'))

            btn_seleccionar = Button(text="Seleccionar", size_hint_x=0.15)
            btn_seleccionar.bind(on_release=lambda btn, c=cliente: self.on_seleccionar(c))

            row.add_widget(lbl_rif)
            row.add_widget(lbl_nombre)
            row.add_widget(lbl_telefono)
            row.add_widget(btn_seleccionar)

            self.grid.add_widget(row)

    def on_seleccionar(self, cliente):
        if self.callback:
            self.callback(cliente)
        self.dismiss() 
        
class AñadirTrabajoPopup(Popup):
    def __init__(self, callback, ficha_id=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.ficha_id = ficha_id  # Guardamos el ID de la ficha
        self.operador_seleccionado = None
        self.todos_trabajos = []
        self.todos_operadores = {}

        self.cargar_trabajos()
        self.cargar_operadores()
        # Cargar datos

    def cargar_trabajos(self):
        """Carga trabajos desde MongoDB"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['mano_de_obra_recti']
            self.todos_trabajos = [doc['nombre'] for doc in collection.find({}, {'nombre': 1})]
            client.close()
        except Exception as e:
            print(f"❌ Error al cargar trabajos: {e}")
            self.todos_trabajos = []

    def cargar_operadores(self):
        """Carga operadores y sus tasas"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['operadores']
            operadores = list(collection.find({}, {'nombre': 1, 'porcentaje': 1}))
            client.close()

            # Diccionario: nombre → tasa
            self.todos_operadores = {op['nombre']: op['porcentaje'] for op in operadores}

            # Actualizar Spinner
            self.ids.spinner_operador.values = list(self.todos_operadores.keys())

        except Exception as e:
            print(f"❌ Error al cargar operadores: {e}")

    def cargar_datos_operador(self, nombre_operador):
        """Carga la tasa del operador seleccionado"""
        if nombre_operador in self.todos_operadores:
            tasa = self.todos_operadores[nombre_operador]
            self.ids.tasa_operador.text = f"{tasa:.2f}"
            self.operador_seleccionado = nombre_operador
            self.calcular_subtotal()


    def select_trabajo(self, row):
        """Se llama cuando se hace clic en una fila"""
        # Limpiar selección anterior
        rv = self.ids.rv_trabajos
        for child in rv.children:
            if hasattr(child, 'data'):
                for item in child.data:
                    item['selected'] = False

        # Marcar como seleccionado
        row.selected = True
        self.trabajo_seleccionado = {
            'id_trabajo': row.id_trabajo,
            'trabajo': row.trabajo,
            'operador': row.operador,
            'estado': row.estado,
            'total_general': row.total_general
        }
        print(f"✅ Trabajo seleccionado: {self.trabajo_seleccionado}")

    def calcular_subtotal(self, *args):
        """Calcula subtotal = horas × precio por hora"""
        try:
            horas = float(self.ids.cantidad_horas.text or 0)
            precio = float(self.ids.precio_por_hora.text or 0)
            subtotal = horas * precio
            self.ids.subtotal.text = f"{subtotal:.2f}"
        except:
            self.ids.subtotal.text = "0.00"

    def abrir_popup_repuestos(self):
        """Abre el popup de repuestos (puedes implementarlo después)"""
        print("👉 Botón 'Añadir Repuesto' presionado")
        # Aquí puedes abrir RepuestosPopup si ya está definido
        # popup = RepuestosPopup(callback=...)
        # popup.open()

    def guardar_trabajo(self):
        """Guarda el trabajo completo en la colección 'trabajos' de MongoDB"""
        # --- 1. Validar datos principales ---
        trabajo = self.ids.buscador_trabajo.text.strip()
        operador = self.operador_seleccionado
        horas = self.ids.cantidad_horas.text.strip()
        precio_hora = self.ids.precio_por_hora.text.strip()
        subtotal = self.ids.subtotal.text.strip()

        if not trabajo or not operador or not horas:
            print("⚠️ Faltan datos obligatorios: trabajo, operador o horas")
            return

        try:
            # --- 2. Conexión a MongoDB ---
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['trabajos']
            contadores = db['contadores']

            # --- 3. Obtener ID autoincremental para el trabajo ---
            contador = contadores.find_one_and_update(
                {'_id': 'trabajo_id'},
                {'$inc': {'seq': 1}},
                upsert=True,
                return_document=True
            )
            id_trabajo = contador['seq']

            # --- 4. Recopilar repuestos añadidos ---
            repuestos = []
            grid_repuestos = self.ids.grid_repuestos_trabajo

            # Recorremos los widgets del GridLayout (en orden inverso)
            widgets = grid_repuestos.children[::-1]  # Orden visual: de arriba a abajo
            num_widgets = len(widgets)
            
            # Saltamos los 5 encabezados
            start_index = 5
            for i in range(start_index, num_widgets, 5):
                if i + 4 >= num_widgets:
                    break
                # Cada grupo de 5 widgets forma una fila
                codigo_widget = widgets[i]
                nombre_widget = widgets[i + 1]
                cantidad_widget = widgets[i + 2]
                precio_widget = widgets[i + 3]
                total_widget = widgets[i + 4]

                # Extraemos el texto
                codigo = codigo_widget.text.strip()
                nombre = nombre_widget.text.strip()
                cantidad_text = cantidad_widget.text.strip()
                precio_text = precio_widget.text.strip()
                total_text = total_widget.text.strip()

                # Validación: saltar si está vacío o es encabezado
                if not cantidad_text or not precio_text:
                    continue
                if cantidad_text in ['Cant.', 'Cantidad'] or precio_text in ['Precio']:
                    continue

                # Conversión segura
                try:
                    cantidad_val = float(cantidad_text)
                    precio_val = float(precio_text)
                    total_val = float(total_text) if total_text else cantidad_val * precio_val

                    repuestos.append({
                        "codigo": codigo,
                        "nombre": nombre,
                        "cantidad": cantidad_val,
                        "precio": precio_val,
                        "total": total_val
                    })
                except ValueError as e:
                    print(f"⚠️ Error de conversión en repuesto: {e}")
                    continue

            # --- 5. Calcular totales ---
            total_repuestos = sum(r['total'] for r in repuestos)
            total_mano_obra = float(subtotal)
            total_general = total_repuestos + total_mano_obra

            # --- 6. Obtener otros datos ---
            observacion = self.ids.observacion.text.strip() or "Sin observaciones"
            ficha_id = self.ficha_id  # Debe ser pasado al crear el popup

            # --- 7. Documento a insertar ---
            nuevo_trabajo = {
                "id_trabajo": id_trabajo,
                "ficha_id": ficha_id,
                "trabajo": trabajo,
                "operador": operador,
                "cantidad": float(horas),
                "precio_por_trabajo": float(precio_hora),
                "subtotal_mano_obra": float(subtotal),
                "repuestos": repuestos,
                "total_repuestos": total_repuestos,
                "total_mano_obra": total_mano_obra,
                "total_general": total_general,
                "observacion": observacion,
                "estado": "En proceso",
                "repuestos_aprobados": "no",
                "fecha_inicio": datetime.now().strftime('%d/%m/%Y'),
                "tipo": "rectificadora"
            }

            # --- 8. Imprimir para depuración ---
            print("\n" + "="*50)
            print("✅ TRABAJO GUARDADO EN MONGODB")
            print("="*50)
            print(f"🆔 ID del Trabajo: {nuevo_trabajo['id_trabajo']}")
            print(f"📄 Ficha ID: {nuevo_trabajo['ficha_id']}")
            print(f"🔧 Trabajo: {nuevo_trabajo['trabajo']}")
            print(f"👷 Operador: {nuevo_trabajo['operador']}")
            print(f"⏱ Cantidad (horas): {nuevo_trabajo['cantidad']}")
            print(f"💰 Precio por trabajo: ${nuevo_trabajo['precio_por_trabajo']:.2f}")
            print(f"🧮 Subtotal mano de obra: ${nuevo_trabajo['subtotal_mano_obra']:.2f}")
            print(f"📦 Repuestos:")
            if nuevo_trabajo['repuestos']:
                for i, rep in enumerate(nuevo_trabajo['repuestos'], 1):
                    print(f"   {i}. {rep['nombre']} (x{rep['cantidad']}) @ ${rep['precio']:.2f} = ${rep['total']:.2f}")
            else:
                print("   No se agregaron repuestos.")
            print(f"📦 Total repuestos: ${nuevo_trabajo['total_repuestos']:.2f}")
            print(f"💼 Total mano de obra: ${nuevo_trabajo['total_mano_obra']:.2f}")
            print(f"📌 Total general: ${nuevo_trabajo['total_general']:.2f}")
            print(f"📝 Observación: {nuevo_trabajo['observacion']}")
            print(f"🔄 Estado: {nuevo_trabajo['estado']}")
            print(f"🛒 Repuestos aprobados: {nuevo_trabajo['repuestos_aprobados']}")
            print(f"📅 Fecha de inicio: {nuevo_trabajo['fecha_inicio']}")
            print(f"🏷 Tipo: {nuevo_trabajo['tipo']}")
            print("="*50 + "\n")

            # --- 9. Insertar en MongoDB ---
            result = collection.insert_one(nuevo_trabajo)
            print(f"✅ Documento insertado con ID: {result.inserted_id}")

            # --- 10. Llamar callback si existe ---
            if self.callback:
                try:
                    self.callback(nuevo_trabajo)
                except Exception as cb_error:
                    print(f"⚠️ Error al ejecutar callback: {cb_error}")

            # --- 11. Cerrar popup ---
            self.dismiss()

            client.close()

        except Exception as e:
            print(f"❌ Error al guardar en MongoDB: {e}")
    def abrir_popup_repuestos(self):
        """Abre el popup de repuestos para añadir uno al trabajo"""
        def on_repuesto_seleccionado(repuesto):
            # Añadir fila con el repuesto seleccionado
            self.agregar_fila_repuesto(repuesto)

        popup = RepuestosPopup(callback=on_repuesto_seleccionado)
        popup.open()


    def agregar_fila_repuesto(self, repuesto):
        """Añade una fila con los datos del repuesto"""
        grid = self.ids.grid_repuestos_trabajo

        # Crear los widgets
        codigo = TextInput(text=str(repuesto.get('codigo', '')), readonly=True, size_hint_x=0.2)
        nombre = TextInput(text=repuesto.get('nombre', ''), readonly=True, size_hint_x=0.3)
        cantidad = TextInput(text="1", input_filter='float', size_hint_x=0.15)
        precio = TextInput(text=f"{repuesto.get('precio', 0.0):.2f}", input_filter='float', size_hint_x=0.15)
        total = TextInput(readonly=True, size_hint_x=0.2)

        # Función para calcular total
        def calcular_total(*args):
            try:
                cant = float(cantidad.text or 0)
                prec = float(precio.text or 0)
                total.text = f"{cant * prec:.2f}"
            except:
                total.text = "0.00"

        cantidad.bind(text=calcular_total)
        precio.bind(text=calcular_total)
        calcular_total()

        # ✅ Añadir widgets directamente al GridLayout (una fila completa)
        grid.add_widget(codigo)
        grid.add_widget(nombre)
        grid.add_widget(cantidad)
        grid.add_widget(precio)
        grid.add_widget(total)

        # ✅ Actualizar altura
        grid.height = grid.minimum_height
            
    def limpiar_mensaje(self):
        """Limpia el mensaje de confirmación"""
        if hasattr(self.ids, 'mensaje_repuesto'):
            self.ids.mensaje_repuesto.text = ''



        
class FichaTorno(Popup):
    def __init__(self,nivel = None, **kwargs):
        self.nivel_usuario = nivel  
        super().__init__(**kwargs)
        # Programar la inicialización para después de que el widget se construya
        Clock.schedule_once(self.inicializar_popup, 0)
    
            
        if self.nivel_usuario ==1 :
            self.ids.popup_operadores.disabled = True
            self.ids.generador_ficha.disabled = True
            self.ids.nota_entrega.disabled = True



    def inicializar_popup(self, dt):
        self.cargar_numero_ficha()


            
            
    def guardar_nuevo_cliente(self):
        """Guarda el cliente en la colección 'clientes'"""
        try:
            tipo_rif = self.ids.tipo_rif.text
            nuevo_rif = self.ids.nuevo_rif.text.strip()
            nombre = self.ids.nuevo_cliente.text.strip()
            telefono = self.ids.nuevo_telefono.text.strip()
            direccion = self.ids.nueva_direccion.text.strip()

            if not nuevo_rif:
                self.ids.mensaje_estado.text = "Por favor, ingrese el RIF."
                return
            if not nombre:
                self.ids.mensaje_estado.text = "Por favor, ingrese el nombre del cliente."
                return

            rif_completo = tipo_rif + nuevo_rif

            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['clientes']

            if collection.find_one({"rif": rif_completo}):
                self.ids.mensaje_estado.text = "Cliente con este RIF ya existe."
                client.close()
                return

            nuevo_cliente = {
                "rif": rif_completo,
                "nombre": nombre,
                "telefono": telefono,
                "direccion": direccion
            }

            collection.insert_one(nuevo_cliente)
            client.close()

            self.ids.mensaje_estado.text = f"✅ Cliente '{nombre}' guardado correctamente."

        except Exception as e:
            print(f"❌ Error al guardar cliente: {e}")
            self.ids.mensaje_estado.text = "Error al conectar con la base de datos."
    def cargar_numero_ficha(self):
        """Genera el siguiente número de ficha basado en el máximo existente + 1"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            col_fichas = db['fichas']
            
            # Buscar el número de ficha más alto en la base de datos
            ficha_maxima = col_fichas.find_one(
                {},
                sort=[("numero_ficha", -1)]  # Ordenar por numero_ficha descendente
            )
            
            # Si existe al menos una ficha, tomar el siguiente número
            if ficha_maxima and 'numero_ficha' in ficha_maxima:
                self.numero_ficha = ficha_maxima['numero_ficha'] + 1
            else:
                # Si no hay fichas, empezar desde 1
                self.numero_ficha = 1
            
            self.title = f'Ficha Torno #{self.numero_ficha}'
            client.close()
            
            print(f"✅ Número de ficha asignado: {self.numero_ficha}")
            
        except Exception as e:
            print(f"❌ Error al obtener número de ficha: {e}")
            self.title = "Ficha Torno #?"
            self.numero_ficha = 1  # Valor por defecto
        self.ids.nueva_fecha.text = datetime.now().strftime('%d/%m/%Y')
        
    def guardar_nueva_ficha(self):
        """Guarda o actualiza la ficha en MongoDB según el modo (nueva o modificación) - SIN DATOS DEL MOTOR"""
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            col_usuarios = db['usuarios']
            col_fichas = db['fichas']

            # === DATOS DEL CLIENTE ===
            tipo_rif = self.ids.tipo_rif.text
            nuevo_rif = self.ids.nuevo_rif.text.strip()
            nombre = self.ids.nuevo_cliente.text.strip()
            telefono = self.ids.nuevo_telefono.text.strip()
            direccion = self.ids.nueva_direccion.text.strip()
            fecha = self.ids.nueva_fecha.text

            if not nuevo_rif or not nombre:
                self.ids.mensaje_estado.text = "RIF y Nombre son obligatorios."
                client.close()
                return

            rif_completo = tipo_rif + nuevo_rif

            # Guardar cliente en 'usuarios' si no existe (solo en modo nueva ficha)
            if not getattr(self, 'es_modificacion', False):
                cliente_existente = col_usuarios.find_one({"rif": rif_completo})
                if not cliente_existente:
                    col_usuarios.insert_one({
                        "rif": rif_completo,
                        "nombre": nombre,
                        "telefono": telefono,
                        "direccion": direccion,
                        "tipo": "cliente"
                    })
                    print(f"✅ Cliente '{nombre}' guardado en 'usuarios'")

            # === PARTES RECIBIDAS ===
            partes_recibidas = []
            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout and hasattr(grid_layout, 'children'):
                widgets_en_orden = list(reversed(grid_layout.children))
                for i in range(0, len(widgets_en_orden), 3):
                    if i + 2 < len(widgets_en_orden):
                        cantidad_widget = widgets_en_orden[i]
                        pieza_widget = widgets_en_orden[i + 1]
                        if (isinstance(cantidad_widget, TextInput) and 
                            isinstance(pieza_widget, TextInput) and
                            getattr(cantidad_widget, 'hint_text', None) == "Cantidad" and
                            getattr(pieza_widget, 'hint_text', None) == "Pieza"):
                            cantidad = cantidad_widget.text.strip()
                            nombre_pieza = pieza_widget.text.strip()
                            if nombre_pieza and cantidad and cantidad != '0':
                                partes_recibidas.append({
                                    "parte": nombre_pieza,
                                    "cantidad": cantidad
                                })

            # === OBSERVACIÓN DE PARTES RECIBIDAS ===
            observacion_partes_recibidas = ""
            if hasattr(self, '_observacion_partes_widget') and self._observacion_partes_widget:
                observacion_partes_recibidas = self._observacion_partes_widget.text.strip()

            # === MANO DE OBRA, REPUESTOS Y OBSERVACIONES ===
            mano_obra = []
            repuestos = []
            observaciones = []

            if hasattr(self.ids, 'grid_mano_obra'):
                operadores = list(self.ids.grid_mano_obra.children)
                operadores.reverse()

                for contenedor_mano_obra_completo in operadores:
                    if not contenedor_mano_obra_completo.children:
                        continue
                    contenedor_operador = contenedor_mano_obra_completo.children[0]
                    operador_nombre = "N/A"
                    for child in contenedor_operador.children:
                        if isinstance(child, BoxLayout):
                            for subchild in child.children:
                                if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                                    operador_nombre = limpiar_nombre_operador(subchild.text)
                                    break

                    # --- Trabajos ---
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        trabajos_container = contenedor_operador.trabajos_container
                        filas_trabajo = list(trabajos_container.children)
                        filas_trabajo.reverse()
                        for fila_layout in filas_trabajo:
                            if isinstance(fila_layout, BoxLayout) and len(fila_layout.children) == 6:
                                children = fila_layout.children
                                trabajo_widget = children[5]
                                cantidad_widget = children[4]
                                precio_widget = children[2]
                                total_widget = children[3]
                                terminado_widget = children[1]
                                if (hasattr(trabajo_widget, 'text') and
                                    hasattr(cantidad_widget, 'text') and
                                    hasattr(precio_widget, 'text') and
                                    hasattr(total_widget, 'text')):
                                    trabajo_texto = trabajo_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    precio_texto = precio_widget.text.strip()
                                    total_texto = total_widget.text.strip()
                                    terminado_estado = getattr(terminado_widget, 'active', False)
                                    if trabajo_texto:
                                        try:
                                            cantidad_num = float(cantidad_texto) if cantidad_texto else 0
                                            precio_num = float(precio_texto) if precio_texto else 0
                                            total_num = float(total_texto) if total_texto else 0
                                        except ValueError:
                                            cantidad_num = 0
                                            precio_num = 0
                                            total_num = 0
                                        mano_obra.append({
                                            'operador': operador_nombre,
                                            'descripcion': trabajo_texto,
                                            'cantidad': cantidad_num,
                                            'precio': total_num,  # Aparecen al revés — no lo cambies
                                            'total': precio_num,
                                            'terminado': terminado_estado
                                        })

                    # --- Repuestos ---
                    if hasattr(contenedor_operador, 'repuestos_container'):
                        repuestos_container = contenedor_operador.repuestos_container
                        filas_repuesto = list(repuestos_container.children)
                        filas_repuesto.reverse()

                        filas_datos = []
                        textos_header = ["Código", "Nombre", "Cantidad", "Precio", "Total", "Acción"]
                        
                        for f in filas_repuesto:
                            if not (isinstance(f, BoxLayout) and len(f.children) == 6):
                                continue
                            children = f.children
                            is_header = any(
                                isinstance(child, (Label, TextInput)) and 
                                (getattr(child, 'text', '').strip() in textos_header or 
                                getattr(child, 'hint_text', '').strip() in textos_header)
                                for child in children
                            )
                            if is_header:
                                continue
                            codigo_widget = children[5] if len(children) > 5 else None
                            nombre_widget = children[4] if len(children) > 4 else None
                            if (not codigo_widget or not hasattr(codigo_widget, 'text') or 
                                not nombre_widget or not hasattr(nombre_widget, 'text') or
                                (not codigo_widget.text.strip() and not nombre_widget.text.strip())):
                                continue
                            filas_datos.append(f)
                        
                        for fila_repuesto in filas_datos:
                            children = fila_repuesto.children
                            codigo_widget = children[5]
                            nombre_widget = children[4]
                            cantidad_widget = children[3]
                            precio_widget = children[2]
                            total_widget = children[1]
                            
                            if (hasattr(codigo_widget, 'text') and 
                                hasattr(nombre_widget, 'text') and 
                                hasattr(cantidad_widget, 'text') and
                                hasattr(precio_widget, 'text') and
                                hasattr(total_widget, 'text')):
                                codigo_texto = codigo_widget.text.strip()
                                nombre_texto = nombre_widget.text.strip()
                                cantidad_texto = cantidad_widget.text.strip()
                                precio_texto = precio_widget.text.strip()
                                total_texto = total_widget.text.strip()
                                
                                if nombre_texto and nombre_texto not in textos_header:
                                    try:
                                        cantidad_num = float(cantidad_texto) if cantidad_texto else 0
                                        precio_num = float(precio_texto) if precio_texto else 0
                                        total_num = float(total_texto) if total_texto else 0
                                        
                                        if cantidad_num > 0 or precio_num > 0 or total_num > 0:
                                            repuestos.append({
                                                'operador': operador_nombre,
                                                'codigo': codigo_texto,
                                                'nombre': nombre_texto,
                                                'cantidad': cantidad_num,
                                                'precio': precio_num,
                                                'total': total_num
                                            })
                                    except ValueError:
                                        pass

                    # --- Observaciones ---
                    if hasattr(contenedor_operador, '_observacion_input'):
                        observacion_input = contenedor_operador._observacion_input
                        if hasattr(observacion_input, 'text'):
                            observacion_texto = observacion_input.text.strip()
                            if observacion_texto:
                                observaciones.append({
                                    'operador': operador_nombre,
                                    'texto': observacion_texto
                                })

            # === TOTALES ===
            def parse_money(text):
                try:
                    return float(text.replace('$', '').replace(',', '') or "0")
                except ValueError:
                    return 0.0

            total_mano_obra = parse_money(self.ids.total_mano_obra.text)
            total_repuestos = parse_money(self.ids.total_repuestos.text)
            subtotal = parse_money(self.ids.subtotal.text)
            iva = parse_money(self.ids.iva.text)
            total_general = parse_money(self.ids.total_general.text)
            anticipo = float(self.ids.anticipo.text or "0")
            abonos = float(self.ids.abonos.text or "0")
            saldo = parse_money(self.ids.saldo.text)

            # === CONSTRUIR DOCUMENTO SIN DATOS DEL MOTOR ===
            documento_ficha = {
                "cliente": {
                    "rif": rif_completo,
                    "nombre": nombre,
                    "telefono": telefono,
                    "direccion": direccion,
                    "fecha_registro": fecha
                },
                "partes_recibidas": partes_recibidas,
                "observacion_partes_recibidas": observacion_partes_recibidas,
                "mano_obra": mano_obra,
                "repuestos": repuestos,
                "observaciones": observaciones,
                "totales": {
                    "total_mano_obra": total_mano_obra,
                    "total_repuestos": total_repuestos,
                    "subtotal": subtotal,
                    "iva": iva,
                    "total_general": total_general,
                    "anticipo": anticipo,
                    "abonos": abonos,
                    "saldo": saldo
                },
                "tipo_ficha": "Torno",
            }

            es_modificacion = getattr(self, 'es_modificacion', False)

            # ═══════════════════════════════════════════════════════════════════════════════════════════════
            # ✅ VALIDAR INVENTARIO ANTES DE GUARDAR CUALQUIER COSA
            # ═══════════════════════════════════════════════════════════════════════════════════════════════

            col_inventario = db['Repuestos']
            col_repuestos_reg = db['registro_repuestos']
            errores_inventario = []

            # Si es modificación, obtener repuestos anteriores para simular devolución
            repuestos_anteriores = []
            if es_modificacion:
                repuestos_anteriores = list(col_repuestos_reg.find({"numero_ficha": self.numero_ficha}))

            # Validar cada repuesto actual
            for repuesto in repuestos:
                codigo_str = repuesto.get('codigo')
                cantidad_usada = repuesto.get('cantidad', 0)

                if not codigo_str or cantidad_usada <= 0:
                    continue

                try:
                    codigo_int = int(codigo_str)
                except ValueError:
                    errores_inventario.append(f"Código '{codigo_str}' no es un número válido.")
                    continue

                # Buscar en inventario
                inv_doc = col_inventario.find_one({"codigo": codigo_int})
                if not inv_doc:
                    errores_inventario.append(f"Repuesto con código '{codigo_str}' no existe en inventario.")
                    continue

                stock_real = inv_doc.get('cantidad', 0)

                # Simular devolución del stock anterior (solo para validación)
                devolucion = 0
                for item_ant in repuestos_anteriores:
                    if item_ant.get('codigo') == codigo_str or item_ant.get('codigo') == codigo_int:
                        devolucion += item_ant.get('cantidad', 0)

                stock_disponible = stock_real + devolucion
                if stock_disponible < cantidad_usada:
                    nombre_rep = inv_doc.get('nombre', codigo_str)
                    errores_inventario.append(
                        f"Stock insuficiente para '{nombre_rep}': disponible {stock_disponible}, solicitado {cantidad_usada}"
                    )

            if errores_inventario:
                error_msg = "\n".join(errores_inventario)
                self.ids.mensaje_estado.text = f"❌ Error de inventario:\n{error_msg}"
                client.close()
                return  # ⛔ No se guarda nada si hay error

            # ═══════════════════════════════════════════════════════════════════════════════════════════════
            # ✅ AHORA SÍ: GUARDAR EN FICHA PRINCIPAL
            # ═══════════════════════════════════════════════════════════════════════════════════════════════

            if es_modificacion:
                numero_ficha = self.numero_ficha
                documento_ficha["fecha_modificacion"] = datetime.now().isoformat()
                result = col_fichas.update_one(
                    {"numero_ficha": numero_ficha},
                    {"$set": documento_ficha}
                )
                if result.modified_count > 0:
                    print(f"✅ Ficha #{numero_ficha} actualizada correctamente.")
                    self.ids.mensaje_estado.text = f"✅ Ficha #{numero_ficha} actualizada correctamente."
                    if hasattr(self, 'callback_guardado') and self.callback_guardado:
                        self.callback_guardado(numero_ficha, documento_ficha)
                else:
                    print(f"⚠️ Ficha #{numero_ficha} no tuvo cambios o no se encontró.")
                    self.ids.mensaje_estado.text = f"⚠️ No se detectaron cambios en la ficha #{numero_ficha}."
                    if hasattr(self, 'callback_guardado') and self.callback_guardado:
                        self.callback_guardado(numero_ficha, documento_ficha)
            else:
                documento_ficha["numero_ficha"] = self.numero_ficha
                documento_ficha["fecha_creacion"] = datetime.now().isoformat()
                documento_ficha["estado"] = "registrada"

                if col_fichas.find_one({"numero_ficha": self.numero_ficha}):
                    self.cargar_numero_ficha()
                    documento_ficha["numero_ficha"] = self.numero_ficha
                    documento_ficha["fecha_creacion"] = datetime.now().isoformat()

                col_fichas.insert_one(documento_ficha)
                print(f"✅ Ficha #{self.numero_ficha} creada correctamente.")
                self.ids.mensaje_estado.text = f"✅ Ficha #{self.numero_ficha} guardada correctamente."
                self._actualizar_vista_fichas(documento_ficha)

            # ═══════════════════════════════════════════════════════════════════════════════════════════════
            # ✅ GUARDAR EN COLECCIONES SEPARADAS
            # ═══════════════════════════════════════════════════════════════════════════════════════════════

            # --- Cliente en 'clientes' ---
            col_clientes = db['clientes']
            if not col_clientes.find_one({"rif": rif_completo}):
                col_clientes.insert_one({
                    "rif": rif_completo,
                    "nombre": nombre,
                    "telefono": telefono,
                    "direccion": direccion,
                    "fecha_registro": datetime.now().isoformat()
                })
                print(f"✅ Cliente '{nombre}' guardado en 'clientes'")

            # --- Trabajos en 'registro_trabajos' ---
            col_trabajos = db['registro_trabajos']
            if es_modificacion:
                col_trabajos.delete_many({"numero_ficha": self.numero_ficha})
                print(f"🗑️ Trabajos antiguos eliminados para ficha #{self.numero_ficha}")

            for trabajo in mano_obra:
                trabajo_doc = {
                    "numero_ficha": self.numero_ficha,
                    "operador": trabajo['operador'],
                    "cliente": nombre,
                    "descripcion": trabajo['descripcion'],
                    "cantidad": trabajo['cantidad'],
                    "precio": trabajo['precio'],
                    "total": trabajo['total'],
                    "terminado": trabajo['terminado'],
                    "fecha_registro": datetime.now().isoformat(),
                    "tipo_ficha": "torno"
                }
                col_trabajos.insert_one(trabajo_doc)
            print(f"✅ {len(mano_obra)} trabajos guardados en registro_trabajos")

            # --- Repuestos en 'registro_repuestos' ---
            if es_modificacion:
                col_repuestos_reg.delete_many({"numero_ficha": self.numero_ficha})
                print(f"🗑️ Repuestos antiguos eliminados para ficha #{self.numero_ficha}")

            for repuesto in repuestos:
                repuesto_doc = {
                    "numero_ficha": self.numero_ficha,
                    "operador": repuesto['operador'],
                    "codigo": repuesto['codigo'],
                    "nombre": repuesto['nombre'],
                    "cantidad": repuesto['cantidad'],
                    "precio": repuesto['precio'],
                    "total": repuesto['total'],
                    "fecha_registro": datetime.now().isoformat(),
                    "tipo_ficha": "torno"
                }
                col_repuestos_reg.insert_one(repuesto_doc)
            print(f"✅ {len(repuestos)} repuestos guardados en registro_repuestos")

            # ═══════════════════════════════════════════════════════════════════════════════════════════════
            # ✅ ACTUALIZAR INVENTARIO (ya validado que es posible)
            # ═══════════════════════════════════════════════════════════════════════════════════════════════

            # 1. Devolver stock anterior (solo en modificación)
            if es_modificacion:
                for item_ant in repuestos_anteriores:
                    codigo_ant = item_ant.get('codigo')
                    cantidad_ant = item_ant.get('cantidad', 0)
                    if codigo_ant and cantidad_ant > 0:
                        try:
                            codigo_ant_int = int(codigo_ant) if isinstance(codigo_ant, str) else codigo_ant
                            col_inventario.update_one(
                                {"codigo": codigo_ant_int},
                                {"$inc": {"cantidad": cantidad_ant}}
                            )
                            print(f"🔄 Devolución por modificación: +{cantidad_ant} de '{codigo_ant}'")
                        except (ValueError, TypeError):
                            continue

            # 2. Restar stock actual
            for repuesto in repuestos:
                codigo_str = repuesto.get('codigo')
                cantidad_usada = repuesto.get('cantidad', 0)

                if not codigo_str or cantidad_usada <= 0:
                    continue

                try:
                    codigo_int = int(codigo_str)
                except ValueError:
                    continue  # Ya validado, pero por seguridad

                col_inventario.update_one(
                    {"codigo": codigo_int},  # ✅ Tipo correcto (int)
                    {"$inc": {"cantidad": -cantidad_usada}}  # ✅ Más seguro y atómico
                )
                print(f"📦 Salida: -{cantidad_usada} de '{codigo_str}' → stock actualizado")

            print("✅ Inventario actualizado correctamente.")

            client.close()
            self.dismiss()

        except Exception as e:
            print(f"❌ Error al guardar ficha: {e}")
            import traceback
            traceback.print_exc()
            self.ids.mensaje_estado.text = f"❌ Error al guardar en la base de datos: {str(e)}"
            if 'client' in locals():
                client.close()

    def abrir_popup_clientes(self):
        """Abre el popup para seleccionar un cliente existente"""
        def on_cliente_seleccionado(cliente):
            # Extraer tipo de RIF (ej: "V-", "J-", etc.)
            rif_completo = cliente.get('rif', '')
            if len(rif_completo) >= 2 and rif_completo[1] == '-':
                tipo_rif = rif_completo[:2]
                numero_rif = rif_completo[2:]
            else:
                tipo_rif = 'V-'
                numero_rif = rif_completo

            # Llenar los campos
            self.ids.tipo_rif.text = tipo_rif
            self.ids.nuevo_rif.text = numero_rif
            self.ids.nuevo_cliente.text = cliente.get('nombre', '')
            self.ids.nuevo_telefono.text = cliente.get('telefono', '')
            self.ids.nueva_direccion.text = cliente.get('direccion', '')

            self.ids.mensaje_estado.text = f"✅ Cliente '{cliente.get('nombre', '')}' cargado."

        popup = ClientesPopup(callback=on_cliente_seleccionado)
        popup.open()
    
    def _actualizar_vista_fichas(self, nueva_ficha):
        """Actualiza la tabla de VistaFichas con la nueva ficha"""
        try:
            # Buscar la pantalla VistaFichas en el ScreenManager
            app = App.get_running_app()
            if app and hasattr(app, 'root'):
                # Buscar el ScreenManager
                for child in app.root.walk():
                    if hasattr(child, 'current') and hasattr(child, 'screens'):  # Es un ScreenManager
                        for screen in child.screens:
                            if screen.name == 'vista_fichas' or isinstance(screen, VistaFichas):
                                # Encontramos la pantalla VistaFichas
                                screen.agregar_nueva_ficha_a_tabla(nueva_ficha)
                                print("✅ VistaFichas actualizada automáticamente")
                                return
            
            print("ℹ️  No se pudo encontrar VistaFichas para actualizar")
            
        except Exception as e:
            print(f"❌ Error al actualizar VistaFichas: {e}")


    def _extraer_datos_operador_para_bd(self, contenedor_operador):
        """Extrae los datos de trabajos de un operador para guardar en BD (CORREGIDO)"""
        trabajos = []
        try:
            operador_nombre = "N/A"
            
            # Buscar el label del operador en el header
            for child in contenedor_operador.children:
                if isinstance(child, BoxLayout):  # Es el contenedor header
                    for subchild in child.children:
                        if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                            operador_nombre = subchild.text.replace("Operador:", "").strip()
                            break
            
            # Buscar las filas de trabajo (BoxLayout con orientación horizontal)
            for child in contenedor_operador.children:
                if isinstance(child, BoxLayout) and child.orientation == 'horizontal' and len(child.children) == 6:
                    # Esta es una fila de trabajo (6 widgets: trabajo, cantidad, precio, total, terminado, eliminar)
                    children = child.children
                    
                    # Los children están en orden inverso en Kivy
                    trabajo_widget = children[5]    # TextInput Trabajo
                    cantidad_widget = children[4]   # TextInput Cantidad  
                    precio_widget = children[3]     # TextInput Precio
                    total_widget = children[2]      # TextInput Total
                    terminado_widget = children[1]  # CheckBox
                    # children[0] es el botón eliminar
                    
                    print(f"  📝 Procesando fila:")
                    print(f"    - Trabajo: {getattr(trabajo_widget, 'text', 'N/A')}")
                    print(f"    - Cantidad: {getattr(cantidad_widget, 'text', 'N/A')}")
                    print(f"    - Precio: {getattr(precio_widget, 'text', 'N/A')}")
                    print(f"    - Total: {getattr(total_widget, 'text', 'N/A')}")
                    
                    # Validar que tengan los atributos necesarios
                    if (hasattr(trabajo_widget, 'text') and 
                        hasattr(cantidad_widget, 'text') and 
                        hasattr(precio_widget, 'text') and 
                        hasattr(total_widget, 'text')):
                        
                        trabajo_texto = trabajo_widget.text.strip()
                        
                        # ✅ Validar que no sea el placeholder y que tenga contenido
                        if (trabajo_texto and 
                            trabajo_texto != "Descripción del trabajo" and 
                            trabajo_texto != ""):
                            
                            try:
                                cantidad = float(cantidad_widget.text or 0)
                                precio = float(precio_widget.text or 0)
                                total = float(total_widget.text or 0)
                                terminado = getattr(terminado_widget, 'active', False) if hasattr(terminado_widget, 'active') else False
                                
                                trabajo_data = {
                                    'operador': operador_nombre,
                                    'descripcion': trabajo_texto,
                                    'cantidad': cantidad,
                                    'precio': precio,
                                    'total': total,
                                    'terminado': terminado,
                                    'fecha_creacion': datetime.now().isoformat()
                                }
                                
                                trabajos.append(trabajo_data)
                                print(f"    ✅ Trabajo guardado: {trabajo_texto}")
                                
                            except ValueError as ve:
                                print(f"    ❌ Error convirtiendo valores numéricos: {ve}")
                                continue
                        else:
                            print(f"    ⚠️  Trabajo vacío o placeholder")
                    else:
                        print(f"    ❌ Widgets no tienen atributo 'text'")
                                        
        except Exception as e:
            print(f"❌ Error extrayendo datos operador para BD: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"🎯 Total trabajos extraídos: {len(trabajos)}")
        return trabajos
        
    
    def _extraer_datos_repuesto_para_bd(self, fila_repuesto):
        """Extrae los datos de un repuesto para guardar en BD"""
        try:
            children = fila_repuesto.children
            if len(children) >= 5:  # nombre, cantidad, precio, total, botón eliminar
                # Los children están en orden inverso en Kivy
                nombre = children[-1].text if hasattr(children[-1], 'text') else "N/A"
                cantidad_text = children[-2].text if hasattr(children[-2], 'text') else "0"
                precio_text = children[-3].text if hasattr(children[-3], 'text') else "0"
                total_text = children[-4].text if hasattr(children[-4], 'text') else "0"
                
                try:
                    cantidad = float(cantidad_text or 0)
                    precio = float(precio_text or 0)
                    total = float(total_text or 0)
                    
                    if cantidad > 0 and nombre != "N/A":
                        return {
                            'nombre': nombre,
                            'cantidad': cantidad,
                            'precio': precio,
                            'total': total,
                            'fecha_agregado': datetime.now().isoformat()
                        }
                except ValueError as ve:
                    print(f"Error convirtiendo valores de repuesto: {ve}")
                    
        except Exception as e:
            print(f"❌ Error extrayendo datos repuesto para BD: {e}")
        
        return None
    
    def abrir_popup_operadores(self):
        """Abre el popup para seleccionar operador. Al seleccionar, crea el bloque completo con sus trabajos."""
        
        def on_operador_seleccionado(operador):
            nombre = operador['nombre']
            print(f"🖥️ Operador seleccionado: {nombre}")
            
            # ✅ Crear el bloque COMPLETO pasando el nombre
            self.crear_input_operador(nombre_operador=nombre)
            
            # Cerrar popup
            popup.dismiss()

        # Abrir el popup
        popup = OperadoresPopup(callback=on_operador_seleccionado)
        popup.open()


    def _actualizar_grid_altura(self):
        """Actualiza la altura del grid para mostrar todos los operadores"""
        try:
            if hasattr(self.ids, 'grid_mano_obra'):
                self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height
        except Exception as e:
            print(f"Error actualizando altura del grid: {e}")
                
    ultimas_filas_agregadas = []

    def agregar_fila_partes_recibidas(self):
        """
        Agrega una nueva fila de partes recibidas al GridLayout.
        La fila contiene un TextInput para cantidad, uno para nombre de la pieza y un botón de eliminar.
        """
        grid_layout = self.ids.get('grid_partes_recibidas')  # Asumiendo que tu GridLayout tiene id='grid_partes_recibidas'
        if not grid_layout:
            print("❌ Error: No se encontró el GridLayout 'grid_partes_recibidas'.")
            return

        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.metrics import dp

        # Crear los widgets
        textinput_cantidad = TextInput(
            hint_text="Cantidad",
            input_filter='float',  # Solo permite números
            size_hint_y=None,
            size_hint_x=0.10,
            height=dp(30),  # Misma altura que las otras filas
            multiline=False
        )

        textinput_pieza = TextInput(
            hint_text="Pieza",
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(30),  # Misma altura que las otras filas
            multiline=False
        )

        # Botón de eliminar
        btn_eliminar = Button(
            text='×',
            size_hint_y=None,
            height=dp(30),  # Misma altura que las otras filas
            width=dp(30),   # Ancho fijo para el botón
            size_hint_x=0.05, # Anular el tamaño proporcional en X
            background_color=(0.8, 0.2, 0.2, 1), # Rojo
            color=(1, 1, 1, 1), # Blanco
            bold=True,
            font_size=dp(16)
        )

        # Función para eliminar la fila específica
        def eliminar_fila(instance):
            # Remover los 3 widgets de la fila del GridLayout
            grid_layout.remove_widget(textinput_cantidad)
            grid_layout.remove_widget(textinput_pieza)
            grid_layout.remove_widget(btn_eliminar)
            # Opcional: Remover la fila de la lista si está allí
            if [textinput_cantidad, textinput_pieza, btn_eliminar] in self.ultimas_filas_agregadas:
                self.ultimas_filas_agregadas.remove([textinput_cantidad, textinput_pieza, btn_eliminar])
            print("🗑️ Fila de partes recibidas eliminada.")

        # Vincular el botón a la función de eliminación
        btn_eliminar.bind(on_press=eliminar_fila)

        # Añadirlos al GridLayout
        # El GridLayout distribuye los widgets en columnas automáticamente
        grid_layout.add_widget(textinput_pieza)
        grid_layout.add_widget(textinput_cantidad)
        grid_layout.add_widget(btn_eliminar) # Añadir el botón

        # Guardar la fila en la lista
        if not hasattr(self, 'ultimas_filas_agregadas'):
            self.ultimas_filas_agregadas = []
        self.ultimas_filas_agregadas.append([textinput_cantidad, textinput_pieza, btn_eliminar])

        print("✅ Fila de partes recibidas agregada con botón de eliminar.")


    def agregar_observacion_partes_recibidas(self):
        """Agrega un campo de observación debajo del grid de partes recibidas (solo si no existe ya)"""
        # Verificar si ya existe una observación
        if hasattr(self, '_observacion_partes_widget') and self._observacion_partes_widget:
            # Eliminar si ya existe (toggle)
            widget = self._observacion_partes_widget
            parent = widget.parent
            if parent:
                parent.remove_widget(widget)
            self._observacion_partes_widget = None
            print("🗑️ Observación eliminada.")
            return

        from kivy.uix.textinput import TextInput
        from kivy.metrics import dp

        # Crear el TextInput
        observacion_input = TextInput(
            hint_text="Observaciones sobre las partes recibidas...",
            size_hint_y=None,
            height=dp(80),  # Altura suficiente para varias líneas
            multiline=True,
            font_size=dp(14)
        )

        # Guardar referencia para futuras operaciones
        self._observacion_partes_widget = observacion_input

        # Encontrar el contenedor padre (el que contiene el GridLayout)
        contenedor = self.ids.grid_partes_recibidas.parent
        if not contenedor:
            print("❌ Error: No se encontró el contenedor padre del grid.")
            return

        # Insertar el TextInput justo después del GridLayout
        index = contenedor.children.index(self.ids.grid_partes_recibidas)
        contenedor.add_widget(observacion_input, index)  # Inserta en la posición siguiente

        print("✅ Campo de observación para partes recibidas agregado.")




    def eliminar_ultima_fila_partes_recibidas(self):
        """
        Elimina la última fila de partes recibidas agregada dinámicamente.
        """
        if not hasattr(self, 'ultimas_filas_agregadas') or not self.ultimas_filas_agregadas:
            print("⚠️ No hay filas dinámicas para eliminar.")
            return

        grid_layout = self.ids.get('grid_partes_recibidas')
        if not grid_layout:
            print("❌ Error: No se encontró el GridLayout 'grid_partes_recibidas'.")
            return

        # Obtener la última fila agregada
        ultima_fila = self.ultimas_filas_agregadas.pop() # Obtiene y remueve la última fila de la lista
        textinput_cantidad, textinput_pieza, btn_eliminar = ultima_fila

        # Remover los 3 widgets de la fila del GridLayout
        grid_layout.remove_widget(textinput_cantidad)
        grid_layout.remove_widget(textinput_pieza)
        grid_layout.remove_widget(btn_eliminar)

        print("🗑️ Última fila de partes recibidas agregada eliminada.")
        
    def crear_input_operador(self, nombre_operador=None):
        """Crea un bloque completo de operador con su nombre, botón X, tabla de trabajos y repuestos.
        El contenedor_operador es el único contenedor padre. El contenedor_trabajos es su hijo."""
        from kivy.uix.checkbox import CheckBox
        from kivy.metrics import dp
        from kivy.uix.widget import Widget
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.graphics import Color, Rectangle # Necesario para el fondo del Label
        from kivy.clock import Clock # Necesario para el schedule_once

        # ✅ 1. CREAR EL CONTENEDOR PRINCIPAL (¡UNO SOLO! QUE ENGLOBA TODO)
        contenedor_mano_obra_completo = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(370),  # Altura inicial estimada
            spacing=5,
            padding=[20, 10, 20, 10]
        )
        self.contenedor_mano_obra_completo = contenedor_mano_obra_completo 

        # ✅ 2. ENCABEZADO "MANO DE OBRA" (fuera del contenedor_operador, pero dentro del contenedor_mano_obra_completo)

        # ✅ 3. CREAR EL CONTENEDOR DEL OPERADOR (¡ESTE ES EL CONTENEDOR PADRE DE TODO LO DEL OPERADOR!)
        contenedor_operador = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(300),  # Altura inicial estimada (se ajustará dinámicamente)
            spacing=5,
            padding=[10, 10, 10, 10]
        ) #Mira estas aca mamañema trata de cambiar el espacio de este

        # ✅ 4. HEADER DEL OPERADOR (Nombre y Botón X) → ¡HIJO DIRECTO DE contenedor_operador!
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=10,
            padding=[0, 5, 0, 5]
        )

        nombre_mostrar = nombre_operador if nombre_operador else "(Seleccionar operador)"
        operador_label = Label(
            text=f"[b]Operador:[/b] {nombre_mostrar}",
            size_hint_x=0.8,
            size_hint_y=None,
            height=dp(35),
            font_size=16,
            text_size=(None, dp(35)),
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1),
            markup=True,
            bold=True
        )

        # Fondo sólido para evitar que se vea el texto detrás
        with operador_label.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            rect_label = Rectangle(size=operador_label.size, pos=operador_label.pos)
        operador_label._bg_rect_label = rect_label
        def actualizar_fondo_label(instance, value):
            if hasattr(instance, '_bg_rect_label'):
                instance._bg_rect_label.pos = instance.pos
                instance._bg_rect_label.size = instance.size
        operador_label.bind(pos=actualizar_fondo_label, size=actualizar_fondo_label)

        def eliminar_operador(instance):
            self.ids.grid_mano_obra.remove_widget(contenedor_mano_obra_completo)
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
            Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1) # Agregado para actualizar altura
            print("Operador eliminado y totales recalculados")

        btn_eliminar = Button(
            text='×',
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=18,
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_eliminar.bind(on_press=eliminar_operador)
        btn_observacion = Button(
            text='!',
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            background_color=(0.2, 0.2, 0.8, 1),
            font_size=18,
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_observacion.bind(on_press=lambda instance: self.agregar_bloque_observacion_a_operador(contenedor_operador, contenedor_mano_obra_completo))

        header_layout.add_widget(operador_label)
        header_layout.add_widget(btn_observacion)
        header_layout.add_widget(btn_eliminar)
        contenedor_operador.add_widget(header_layout)

        # ✅ 5. SEPARADOR VISUAL (entre el header y la tabla de trabajos)
        separador = Widget(
            size_hint_y=None,
            height=dp(10)
        )
        contenedor_operador.add_widget(separador)

        # ✅ 6. CONTENEDOR DE TRABAJOS → ¡ESTE ES UN HIJO DIRECTO DE contenedor_operador!
        contenedor_trabajos = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height= dp(35) + (3 * dp(37)) + dp(20), # Altura inicial
            spacing=3,
            padding=[0, 5, 0, 10]
        )

        # Headers de la tabla de trabajos
        headers_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35), # Corregido a dp(35) para que coincida con la altura de una fila
            spacing=2
        )

        headers = ['Trabajo', 'Cantidad', 'Precio', 'Total', 'Terminado']
        weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]

        for i, header in enumerate(headers):
            label = Label(
                text=header,
                size_hint_x=weights[i],
                color=(0.9, 0.9, 0.9, 1),
                bold=True,
                halign='center',
                valign='middle'
            )
            headers_layout.add_widget(label)

        # Botón para agregar trabajo
        btn_agregar_trabajo = Button(
            text='+',
            size_hint_x=weights[-1],
            size_hint_y=None,
            height=dp(35),
            background_color=(0.2, 0.7, 0.2, 1)
        )

        def abrir_popup_trabajos(instance):
            if not nombre_operador or nombre_operador == "(Seleccionar operador)":
                self.agregar_fila_trabajo2(contenedor_trabajos)
                return

            # ✅ Obtener los nombres de los trabajos YA agregados
            trabajos_actuales = []
            if hasattr(contenedor_operador, 'trabajos_container'):
                for fila in contenedor_operador.trabajos_container.children:
                    if len(fila.children) >= 6:
                        trabajo_input = fila.children[5]  # TextInput del trabajo
                        if hasattr(trabajo_input, 'text') and trabajo_input.text.strip():
                            trabajos_actuales.append(trabajo_input.text.strip())

            def on_trabajos_seleccionados(trabajos_seleccionados, custom_vacio):
                # Agregar trabajos normales
                for trabajo_nombre in trabajos_seleccionados:
                    self._crear_fila_trabajo_con_datos(contenedor_trabajos, contenedor_mano_obra_completo, nombre=trabajo_nombre)
                # Agregar fila vacía si se marcó la opción personalizada
                if custom_vacio:
                    self._crear_fila_trabajo_con_datos(contenedor_trabajos,contenedor_mano_obra_completo, nombre="")
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            popup = TrabajosOperadorPopup(
                operador_nombre=nombre_operador,
                callback=on_trabajos_seleccionados,
                trabajos_preseleccionados=trabajos_actuales
            )
            popup.open()

        btn_agregar_trabajo.bind(on_press=abrir_popup_trabajos)
        headers_layout.add_widget(btn_agregar_trabajo)
        contenedor_trabajos.add_widget(headers_layout)

        # ✅ 7. CONTENEDOR DE FILAS DE TRABAJO
        trabajos_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(0),  # Inicia en 0 si no quieres fila vacía
            spacing=2
        )
        contenedor_trabajos.add_widget(trabajos_container)
        contenedor_operador.add_widget(contenedor_trabajos)# ← ¡CLAVE! AÑADIR A contenedor_operador!

        # ✅ 8. ETIQUETA DE SECCIÓN DE REPUESTOS (dentro de contenedor_operador)
        repuestos_label = Label(
            text="REPUESTOS ASOCIADOS AL OPERADOR",
            size_hint_y=None,
            height=dp(25),
            font_size=12,
            bold=True,
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='middle',
            padding=[0, 5, 0, 0]
        )
        contenedor_operador.add_widget(repuestos_label)

        # ✅ 9. BOTÓN PARA AGREGAR REPUESTOS (dentro de contenedor_operador)
        btn_agregar_repuestos = Button(
            text='+ Agregar Repuesto',
            size_hint_y=None,
            height=dp(35),
            background_color=(0.2, 0.7, 0.2, 1),
            font_size=12
        )
        

        def abrir_popup_repuestos_para_operador(instance):
            def on_repuesto_seleccionado(repuesto):
                self.agregar_repuesto_a_operador(contenedor_operador, repuesto,contenedor_mano_obra_completo)
            popup = RepuestosPopup(callback=on_repuesto_seleccionado)
            popup.open()
        btn_agregar_repuestos.bind(on_press=abrir_popup_repuestos_para_operador)
        contenedor_operador.add_widget(btn_agregar_repuestos)

        # ✅ 10. GRID PARA LOS REPUESTOS (dentro de contenedor_operador)
        # Aquí se añadiría un grid/BoxLayout para repuestos, pero lo omitimos por concisión.

        # ✅ 11. GUARDAR REFERENCIAS CLAVE PARA USO POSTERIOR
        
        
        contenedor_operador.trabajos_container = trabajos_container
        contenedor_operador.operador_label = operador_label
        contenedor_operador.btn_eliminar = btn_eliminar

        contenedor_mano_obra_completo.add_widget(contenedor_operador)

        # ✅ OPCIONAL: agregar una fila vacía inicial
        if False:  # Cambia a False si no quieres fila inicial
            self._crear_fila_trabajo_con_datos(contenedor_trabajos, "", "0", "1")

        self.ids.grid_mano_obra.add_widget(contenedor_mano_obra_completo)
        Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)

        return {
            'label_operador': operador_label,
            'contenedor': contenedor_operador,
            'boton_eliminar': btn_eliminar,
            'trabajos_container': trabajos_container,
        }
    
    
    def agregar_bloque_observacion_a_operador(self, contenedor_operador, contenedor_mano_obra_completo):
        """Agrega un bloque de OBSERVACIÓN al final del contenedor de un operador específico."""
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.widget import Widget
        from kivy.metrics import dp
        from kivy.graphics import Color, Rectangle

        # Verificar si ya existe una observación para este operador
        if hasattr(contenedor_operador, '_observacion_widget'):
            self.ids.mensaje_estado.text = "Ya existe una observación para este operador."
            return

        altura_bloque = dp(100)
        altura_separador = dp(15)

        # ✅ Bloque principal de observación
        bloque_obs = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=altura_bloque,
            padding=[10, 5],
            spacing=5
        )

        # ✅ Header: "OBSERVACIÓN" + botón × (90% / 10%)
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25),
            spacing=5
        )

        # Label
        header_label = Label(
            text="[b]OBSERVACIÓN[/b]",
            size_hint_x=0.9,
            size_hint_y=None,
            height=dp(25),
            markup=True,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        header_label.bind(size=header_label.setter('text_size'))
        with header_label.canvas.before:
            Color(0.25, 0.25, 0.35, 1)
            rect = Rectangle(size=header_label.size, pos=header_label.pos)
        header_label._bg_rect = rect
        header_label.bind(
            pos=lambda inst, val: setattr(inst._bg_rect, 'pos', val),
            size=lambda inst, val: setattr(inst._bg_rect, 'size', val)
        )

        # ✅ ÚNICO botón × (10% del ancho)
        btn_eliminar_obs = Button(
            text='×',
            size_hint_x=0.1,
            size_hint_y=None,
            height=dp(25),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )

        text_input = TextInput(
            hint_text="Escriba observaciones...",
            multiline=True,
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 10]
        )

        def eliminar_bloque(instance):
            if bloque_obs.parent:
                bloque_obs.parent.remove_widget(bloque_obs)
                if hasattr(contenedor_operador, '_observacion_widget'):
                    delattr(contenedor_operador, '_observacion_widget')
                    delattr(contenedor_operador, '_observacion_input')
                # Ajustar altura: restar altura del bloque y el separador
                contenedor_operador.height -= (altura_bloque + altura_separador)
                if contenedor_mano_obra_completo:
                    contenedor_mano_obra_completo.height -= (altura_bloque + altura_separador)
                Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
                print("🗑️ Observación del operador eliminada")

        btn_eliminar_obs.bind(on_press=eliminar_bloque)
        
        header_layout.add_widget(header_label)
        header_layout.add_widget(btn_eliminar_obs)

        # Ensamblar
        bloque_obs.add_widget(header_layout)
        bloque_obs.add_widget(text_input)

        # Guardar referencia
        contenedor_operador._observacion_widget = bloque_obs
        contenedor_operador._observacion_input = text_input

        # --- CORRECCIÓN AQUÍ ---
        # 1. Añadir SEPARADOR al contenedor_operador
        separador_superior = Widget(size_hint_y=None, height=altura_separador)
        contenedor_operador.add_widget(separador_superior)
        
        # 2. Añadir el BLOQUE DE OBSERVACIÓN al contenedor_operador (no al contenedor_trabajos)
        contenedor_operador.add_widget(bloque_obs)
        # --- FIN CORRECCIÓN ---

        # 3. Ajustar altura total del contenedor_operador y el contenedor_mano_obra_completo
        contenedor_operador.height += (altura_bloque + altura_separador)
        contenedor_mano_obra_completo.height += (altura_bloque + altura_separador)

        # 4. Actualizar grid principal
        Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
        print("✅ Bloque de observación agregado al operador")

        #contenedor_trabajos.add_widget(bloque_obs) 
        #contenedor_trabajos.height += bloque_obs.height
        
    def _actualizar_grid_altura(self):
        """Actualiza la altura del grid para mostrar todos los operadores"""
        try:
            if hasattr(self.ids, 'grid_mano_obra'):
                self.ids.grid_mano_obra.height = self.ids.grid_mano_obra.minimum_height
        except Exception as e:
            print(f"Error actualizando altura del grid: {e}")
                

    def calcular_todos_los_totales(self):
        """
        Recorre todos los bloques de operador en la interfaz, suma los campos 'Total'
        de cada fila de trabajo asumiendo que el campo 'Total' es el widget en el índice 3 
        de la lista de hijos de la fila (0=Trabajo, 1=Cantidad, 2=Precio, 3=Total, ...).
        Muestra el gran total en la consola.
        """
        grand_total = 0.0
        total_repuestos = 0.0  # 🔹 Definir aquí para evitar el error UnboundLocalError
        
        # Asume que self.ids.grid_mano_obra está disponible
        grid_mano_obra = self.ids.get('grid_mano_obra') 
        
        if not grid_mano_obra:
            print("Error: grid_mano_obra no encontrado. No se puede totalizar.")
            return

        # Iterar sobre cada contenedor_mano_obra_completo (bloque de operador)
        for contenedor_completo in grid_mano_obra.children:
            # 1. Obtener el contenedor_operador (asumido como el primer hijo)
            if not contenedor_completo.children:
                continue

            contenedor_operador = contenedor_completo.children[0]

            # 2. Obtener el contenedor que almacena las filas de trabajo usando la referencia guardada
            trabajos_container = None
            if hasattr(contenedor_operador, 'trabajos_container'):
                trabajos_container = contenedor_operador.trabajos_container
            else:
                # Si no se encuentra la propiedad, intenta navegar por la estructura (menos fiable)
                # Esto asume que contenedor_trabajos es el segundo elemento después del header
                if len(contenedor_operador.children) > 1 and isinstance(contenedor_operador.children[-2], BoxLayout):
                    contenedor_trabajos = contenedor_operador.children[-2]
                    # Asume que trabajos_container es el segundo hijo de contenedor_trabajos
                    if len(contenedor_trabajos.children) > 1:
                        trabajos_container = contenedor_trabajos.children[-2]

            
            if not trabajos_container:
                print("Advertencia: No se encontró trabajos_container para un operador. Se omite.")
                continue
                
            # 3. Iterar sobre las filas de trabajo (fila_layout es un BoxLayout horizontal)
            for fila_layout in trabajos_container.children:
                
                # Acceder al widget en la posición de "Total" (Índice 3)
                # El orden de los hijos en Kivy es inverso al que se añaden.
                # Para filas añadidas como: 1, 2, 3, 4(TOTAL), 5, 6
                # El orden de los hijos será: 6, 5, 4(TOTAL), 3, 2, 1
                
                # Pero en el código original, las filas se añaden en el orden 1, 2, 3, 4(TOTAL), 5, 6
                # Si el `fila_layout` mantiene ese orden:
                # Índice 0: trabajo_input
                # Índice 1: cantidad_input
                # Índice 2: precio_input
                # Índice 3: total_input   <-- USAMOS ESTE
                # Índice 4: terminado_check
                # Índice 5: btn_eliminar_fila
                
                TOTAL_INDEX = 2 # Según el orden especificado por el usuario
                
                if len(fila_layout.children) > TOTAL_INDEX:
                    total_input = fila_layout.children[TOTAL_INDEX]
                    try:
                        # Limpiar y sumar el total
                        # Asegurar que el widget es un TextInput antes de leer .text
                        if isinstance(total_input, TextInput):
                            # El input 'total_input' es readonly y tiene el valor con '.2f'
                            total_value = float(total_input.text.replace(',', '.')) 
                            grand_total += total_value
                        else:
                            print(f"Advertencia: El widget en el índice {TOTAL_INDEX} no es un TextInput. Se omite.")
                    except ValueError:
                        # Ignorar si el valor no es un número válido (ej. "")
                        pass
                else:
                    print("Advertencia: Fila incompleta. Se omite.")
            
            # Vamos a recorrer cada operador y buscar dentro de él los grids de repuestos (si existen)
            # total_repuestos ya está definido fuera del bucle

            # Recorremos todos los widgets hijos del contenedor_operador, excluyendo el bloque de observación

            for widget in contenedor_operador.children:
                # Verificar si el widget es el contenedor de observación o está relacionado con ella
                if (hasattr(contenedor_operador, '_observacion_widget') and 
                    (widget == contenedor_operador._observacion_widget or 
                    widget == contenedor_operador._observacion_input or
                    widget == getattr(contenedor_operador, '_observacion_header', None))):
                    # Saltar este widget y no procesarlo
                    continue

                # Si no es un bloque de observación, procesarlo normalmente
                if isinstance(widget, BoxLayout):
                    # Buscar layouts que representen filas de repuestos
                    # SOLO RECORRER LOS HIJOS DIRECTOS DEL WIDGET ACTUAL
                    for sub_widget in widget.children:  # <-- CAMBIADO A .children
                        if isinstance(sub_widget, BoxLayout):
                            # Solo consideramos BoxLayouts que contienen TextInputs (una fila de repuesto)
                            text_inputs = [w for w in sub_widget.children if isinstance(w, TextInput)]
                            if not text_inputs:
                                continue

                            # Invertir el orden (porque Kivy guarda los hijos de derecha a izquierda)
                            text_inputs = list(reversed(text_inputs))


                            # Detectar dinámicamente qué campos hay
                            campos = [ti.text.strip() for ti in text_inputs]
                            if len(campos) < 4:
                                continue  # Fila incompleta, la omitimos

                            try:
                                # Asumimos estructura: [codigo, nombre, cantidad, precio, total]
                                nombre = campos[1] if len(campos) > 1 else ""
                                total = campos[4] if len(campos) > 4 else "0"

                                # Verificamos si el total es un número válido
                                total_num = 0.0
                                try:
                                    total_num = float(total.replace(",", "."))
                                except ValueError:
                                    total_num = 0.0

                                # Mostrar solo filas que parezcan repuestos válidos
                                if nombre or total_num > 0:
                                    total_repuestos += total_num

                            except Exception as e:
                                print(f"   ⚠️ Error leyendo fila de repuesto: {e}")

                            
                            
        subtotal = grand_total + total_repuestos
        iva = subtotal * 0.16
        total_general = subtotal + iva

        try:
            anticipo = float(self.ids.anticipo.text or "0")
        except ValueError:
            anticipo = 0.0
        try:
            abonos = float(self.ids.abonos.text or "0")
        except ValueError:
            abonos = 0.0
        saldo = total_general - anticipo - abonos

        # 4. Imprimir el resultado final en la consola
        print("\n" + "="*40)
        print("--- RESULTADO DE LA TOTALIZACIÓN DE TRABAJOS ---")
        self.ids.total_mano_obra.text = f"${grand_total:,.2f}"
        self.ids.total_repuestos.text = f"${total_repuestos:,.2f}"
        self.ids.subtotal.text = f"${subtotal:,.2f}"
        self.ids.iva.text = f"${iva:,.2f}"
        self.ids.total_general.text = f"${total_general:,.2f}"
        self.ids.saldo.text = f"${saldo:,.2f}"


    def agregar_repuesto_a_operador(self, contenedor_operador, repuesto, contenedor_mano_obra_completo):
        """Agrega un repuesto al contenedor de repuestos usando lógica de altura dinámica como trata.py"""
        from kivy.metrics import dp

        # ✅ Buscar o crear el contenedor de repuestos
        repuestos_container = getattr(contenedor_operador, 'repuestos_container', None)

        if repuestos_container is None:
            # ✅ Crear contenedor con altura inicial (IGUAL QUE trata.py)
            repuestos_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(40),  # Altura inicial pequeña
                spacing=2,
                padding=[20, 0, 0, 0]
            )

            # Encabezado
            fila_encabezado = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            # Labels del encabezado (sin bind de text_size)
            for texto, ancho in [("Código", 0.2), ("Nombre", 0.3), ("Cant.", 0.15), ("Precio", 0.15), ("Total", 0.15)]:
                label = Label(
                    text=texto,
                    size_hint_x=ancho,
                    font_size=12,
                    color=(0.9, 0.9, 0.9, 1),
                    halign='center',
                    valign='middle',
                    bold=True
                )
                fila_encabezado.add_widget(label)

            repuestos_container.add_widget(fila_encabezado)
            setattr(contenedor_operador, 'repuestos_container', repuestos_container)
            contenedor_operador.add_widget(repuestos_container)

        # ✅ Crear fila de repuesto (TextInput sin text_size)
        fila_repuesto = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35),
            spacing=2
        )

        codigo_input = TextInput(
            text=str(repuesto.get('codigo', '')),
            readonly = True,
            multiline=False,
            size_hint_x=0.2,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        nombre_input = TextInput(
            text=repuesto.get('nombre', ''),
            readonly = True,
            multiline=False,
            size_hint_x=0.3,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        cantidad_input = TextInput(
            text="1" ,
            multiline=False,
            input_filter='float',
            size_hint_x=0.15,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        precio_input = TextInput(
            text=f"{repuesto.get('precio', 0):.2f}",
            multiline=False,
            input_filter='float',
            size_hint_x=0.15,
            font_size=12,
            foreground_color=(1, 1, 1, 1),
            background_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(35)
        )

        total_input = TextInput(
            text="0.00",
            multiline=False,
            readonly=True,
            size_hint_x=0.15,
            font_size=12,
            foreground_color=(0.9, 0.9, 0.9, 1),
            background_color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(35)
        )

        btn_eliminar = Button(
            text='×',
            size_hint_x=0.05,
            size_hint_y=None,
            height=dp(35),
            background_color=(0.7, 0.3, 0.3, 1)
        )

        # Función para calcular total
        def calcular_total(*args):
            try:
                c = float(cantidad_input.text or 0)
                p = float(precio_input.text or 0)
                total_input.text = f"{c * p:.2f}"
            except:
                total_input.text = "0.00"
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

        cantidad_input.bind(text=calcular_total)
        precio_input.bind(text=calcular_total)

        # Función de eliminación con ajuste de altura
        def eliminar_fila(instance):
            if fila_repuesto.parent:
                # ✅ Quitar la fila
                fila_repuesto.parent.remove_widget(fila_repuesto)

                # ✅ Actualizar alturas como en trata.py
                repuestos_container.height -= dp(35)
                contenedor_mano_obra_completo.height -= dp(35)

                # ✅ Verificar si quedan filas de datos (excluyendo el encabezado)
                filas_datos = [
                    child for child in repuestos_container.children
                    if isinstance(child, BoxLayout) and len(child.children) == 6  # Fila de repuesto
                ]

                # ✅ Si NO quedan filas de datos, eliminar el encabezado y el contenedor
                if len(filas_datos) == 0:
                    # Buscar el encabezado y eliminarlo
                    for child in repuestos_container.children:
                        if isinstance(child, BoxLayout) and len(child.children) == 5:  # Tiene 5 widgets → es el encabezado
                            repuestos_container.remove_widget(child)
                            break

                    # ❌ Opcional: ¿También eliminar el contenedor? Depende de tu diseño
                    # Pero mejor dejarlo vacío con solo el encabezado pendiente
                    # No eliminamos el contenedor para evitar errores de referencia

                # ✅ Recalcular totales
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            else:
                print("❌ La fila ya fue eliminada o no tiene padre")
        btn_eliminar.bind(on_press=eliminar_fila)

        # Agregar widgets a la fila
        fila_repuesto.add_widget(codigo_input)
        fila_repuesto.add_widget(nombre_input)
        fila_repuesto.add_widget(cantidad_input)
        fila_repuesto.add_widget(precio_input)
        fila_repuesto.add_widget(total_input)
        fila_repuesto.add_widget(btn_eliminar)

        # ✅ Añadir fila y CRECER el contenedor (IGUAL QUE trata.py)
        repuestos_container.add_widget(fila_repuesto, index=0)
        repuestos_container.height += dp(35)
        contenedor_mano_obra_completo.height += dp(35)

        # Calcular total inicial
        calcular_total()

        print(f"✅ Repuesto añadido. Nueva altura: {repuestos_container.height:.0f}dp")


        
    def eliminar_repuesto_fila(self, fila_layout):
        """Elimina una fila de repuesto (encabezado o editable)"""
        if fila_layout.parent:
            fila_layout.parent.remove_widget(fila_layout)
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
            print("🗑️  Fila de repuesto eliminada")
    
            
    def _eliminar_fila_trabajo(self, contenedor_operador, fila_layout):
        """Elimina una fila de trabajo específica del contenedor correcto"""
        try:
            # Buscar manualmente el trabajos_container (igual que antes)
            trabajos_container = None
            for child in contenedor_operador.children:
                if isinstance(child, BoxLayout) and child.orientation == 'vertical':
                    for subchild in child.children:
                        if isinstance(subchild, BoxLayout) and subchild.orientation == 'vertical':
                            if fila_layout in subchild.children:
                                trabajos_container = subchild
                                break
                    if trabajos_container:
                        break

            if not trabajos_container:
                # Buscar recursivamente
                def buscar_fila_recursivo(widget):
                    if hasattr(widget, 'children'):
                        if fila_layout in widget.children:
                            return widget
                        for child in widget.children:
                            resultado = buscar_fila_recursivo(child)
                            if resultado:
                                return resultado
                    return None
                trabajos_container = buscar_fila_recursivo(contenedor_operador)

            # ✅ Eliminar la fila
            if trabajos_container and fila_layout in trabajos_container.children:
                trabajos_container.remove_widget(fila_layout)
                # ✅ ¡NO HACES NADA MÁS! ¡Kivy ajusta la altura automáticamente!
                print(f"✅ Fila eliminada correctamente. Quedan {len(trabajos_container.children)} filas")
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
                Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)
            else:
                print("❌ No se pudo encontrar la fila o el contenedor correcto")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        
   
    def _actualizar_scroll(self):
        """Fuerza la actualización del scroll para que reconozca los nuevos widgets"""
        # Buscar el ScrollView parent
        scroll_parent = self.ids.grid_mano_obra.parent
        while scroll_parent and not hasattr(scroll_parent, 'scroll_y'):
            scroll_parent = scroll_parent.parent
        
        if scroll_parent:
            # Forzar recálculo del contenido
            scroll_parent.scroll_to(widget=self.ids.grid_mano_obra.children[-1])


    def _scroll_to_bottom(self):
        """Hace scroll hasta abajo para mostrar el nuevo TextInput"""
        # Buscar el ScrollView
        scroll_view = None
        widget = self.ids.grid_mano_obra.parent
        while widget:
            if hasattr(widget, 'scroll_y'):
                scroll_view = widget
                break
            widget = widget.parent
        
        if scroll_view:
            scroll_view.scroll_y = 0  # Scroll hasta abajo

    def abrir_popup_repuestos(self):
        """Abre el popup para seleccionar repuesto. Al seleccionar, crea una fila de repuesto."""
        
        def on_repuesto_seleccionado(repuesto):
            # Crear fila de repuesto usando el método separado
            self.crear_fila_repuesto(repuesto)
            
            # Imprimir en consola (opcional, para depuración)
            print(f"🔧 Repuesto seleccionado: {repuesto['nombre']}")
            
            # Cerrar popup
            popup.dismiss()

        # Abrir el popup (usando RepuestosPopup como en EditarFicha)
        popup = RepuestosPopup(callback=on_repuesto_seleccionado)
        popup.open()
    def crear_fila_repuesto(self, repuesto):
        """Crea una fila simple de repuesto con 4 campos en una línea"""
        
        # ✅ CONTENEDOR HORIZONTAL simple (una sola fila)
        contenedor_repuesto = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=5,
            padding=[10, 5]
        )
        
        # ✅ Campo 1: Código del repuesto
        codigo = repuesto.get('codigo', '')
        codigo_str = str(codigo).strip() if codigo is not None else 'N/A'
        codigo_label = Label(
            text=codigo_str if codigo_str else 'N/A',
            size_hint_x=0.2,
            font_size=12,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        codigo_label.bind(size=codigo_label.setter('text_size'))
        
        # ✅ Campo 2: Nombre del repuesto
        nombre = repuesto.get('nombre', '')
        nombre_str = str(nombre).strip() if nombre is not None else 'N/A'
        nombre_label = Label(
            text=nombre_str if nombre_str else 'N/A',
            size_hint_x=0.2,
            font_size=12,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        nombre_label.bind(size=nombre_label.setter('text_size'))
        
        # ✅ Campo 3: Cantidad (TextInput)
        cantidad_input = TextInput(
            text=str(repuesto.get('cantidad', 1)),
            input_filter='float',
            multiline=False,
            font_size=12,
            size_hint_x=0.15
        )
        
        # ✅ Campo 4: Precio (TextInput)
        precio_input = TextInput(
            text=f"{repuesto.get('precio', 0.0):.2f}",
            input_filter='float',
            multiline=False,
            font_size=12,
            size_hint_x=0.15
        )
        
        # ✅ Campo 5: Total (Label)
        total_label = Label(
            text=f"{repuesto.get('total', 0.0):.2f}",
            font_size=12,
            color=(1, 1, 1, 1),
            size_hint_x=0.15,
            halign='center',
            valign='middle'
        )
        total_label.bind(size=total_label.setter('text_size'))
        
        # ✅ Botón X para eliminar
        def eliminar_repuesto(instance):
            """Elimina la fila del repuesto"""
            
            cantidad_input.text = "0"
            self.ids.grid_repuestos.remove_widget(contenedor_repuesto)
            print("🗑️ Repuesto eliminado")
        
        boton_eliminar = Button(
            text="X",
            size_hint=(None, None),
            size=(30, 30),
            background_color=(1, 0, 0, 1),  # Rojo
            color=(1, 1, 1, 1),  # Texto blanco
            font_size=14,
            bold=True,
            on_press=eliminar_repuesto
        )
        
        # ✅ FUNCIÓN para calcular total específica de esta fila

        def calcular_total_repuesto(instance, value):
            try:
                cantidad = float(cantidad_input.text or "0")
            except ValueError:
                cantidad = 0.0
            
            try:
                precio = float(precio_input.text or "0")
            except ValueError:
                precio = 0.0
            
            total = cantidad * precio
            total_label.text = f"{total:.2f}"
            
            # ✅ RECALCULAR TOTALES GENERALES
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
        
        # Vincular campos para cálculo automático
        cantidad_input.bind(text=calcular_total_repuesto)
        precio_input.bind(text=calcular_total_repuesto)
        
        # ✅ Agregar todos los widgets a la fila horizontal
        contenedor_repuesto.add_widget(nombre_label)    # Nombre
        contenedor_repuesto.add_widget(cantidad_input)  # Cantidad
        contenedor_repuesto.add_widget(precio_input)    # Precio
        contenedor_repuesto.add_widget(total_label)     # Total
        contenedor_repuesto.add_widget(boton_eliminar)  # Botón X
        
        # Calcular total inicial
        calcular_total_repuesto(None, None)
        
        # Añadir la fila al grid_repuestos
        self.ids.grid_repuestos.add_widget(contenedor_repuesto)
        
        # Scroll automático
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
        
        return {
            'contenedor': contenedor_repuesto,
            'nombre': nombre_label,
            'cantidad': cantidad_input,
            'precio': precio_input,
            'total': total_label,
            'repuesto_data': repuesto
        }
       
       
                
    def generar_nota_entrega(self, filename="nota_entrega.pdf"):
        """
        Genera un PDF con la nota de entrega basada en los datos de la FichaRectificadora.
        Extrae los datos exactamente como lo hace generar_ficha_pdf.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        import os
        import platform
        import subprocess

        try:
            # --- 1. Preparar datos ---
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            base_folder = os.path.join(desktop, "Fichas")

            # Obtener número de ficha
            numero_ficha = str(self.numero_ficha)

            # --- 2. Crear rutas ---
            ficha_folder = os.path.join(base_folder, f"Ficha Nº{numero_ficha}")
            pdf_filename = f"Nota de Entrega Nº{numero_ficha}.pdf"
            filepath = os.path.join(ficha_folder, pdf_filename)

            # --- 3. Crear carpetas si no existen ---
            os.makedirs(ficha_folder, exist_ok=True)

            # --- 4. Recopilar datos de la interfaz ---
            datos_cliente = {
                'rif': self.ids.tipo_rif.text + self.ids.nuevo_rif.text.strip(),
                'nombre': self.ids.nuevo_cliente.text.strip(),
                'telefono': self.ids.nuevo_telefono.text.strip(),
                'direccion': self.ids.nueva_direccion.text.strip(),
                'fecha': self.ids.nueva_fecha.text
            }

            # --- 5. Partes recibidas ---
            partes_recibidas = []
            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout and hasattr(grid_layout, 'children'):
                widgets_en_orden = list(reversed(grid_layout.children))
                for i in range(0, len(widgets_en_orden), 3):
                    if i + 2 < len(widgets_en_orden):
                        cantidad_widget = widgets_en_orden[i]
                        pieza_widget = widgets_en_orden[i + 1]
                        if (isinstance(cantidad_widget, TextInput) and 
                            isinstance(pieza_widget, TextInput) and
                            getattr(cantidad_widget, 'hint_text', None) == "Cantidad" and
                            getattr(pieza_widget, 'hint_text', None) == "Pieza"):
                            cantidad = cantidad_widget.text.strip()
                            nombre_pieza = pieza_widget.text.strip()
                            if nombre_pieza and cantidad:
                                try:
                                    if float(cantidad) <= 0:
                                        continue
                                except (ValueError, TypeError):
                                    continue
                                partes_recibidas.append({
                                    "parte": nombre_pieza,
                                    "cantidad": cantidad
                                })

            # --- 6. Recopilar mano de obra y repuestos ---
            mano_obra = []
            repuestos = []
            observaciones = []

            if hasattr(self.ids, 'grid_mano_obra'):
                operadores = list(self.ids.grid_mano_obra.children)
                operadores.reverse()

                for contenedor_mano_obra_completo in operadores:
                    if not contenedor_mano_obra_completo.children:
                        continue
                    contenedor_operador = contenedor_mano_obra_completo.children[0]

                    operador_nombre = "N/A"
                    for child in contenedor_operador.children:
                        if isinstance(child, BoxLayout):
                            for subchild in child.children:
                                if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                                    operador_nombre = subchild.text.replace("Operador:", "").strip()
                                    break

                    # --- TRABAJOS ---
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        filas_trabajo = list(contenedor_operador.trabajos_container.children)
                        filas_trabajo.reverse()
                        for fila_layout in filas_trabajo:
                            if isinstance(fila_layout, BoxLayout) and len(fila_layout.children) == 6:
                                children = fila_layout.children
                                trabajo_widget = children[5]
                                cantidad_widget = children[4]
                                precio_widget = children[2]
                                total_widget = children[3]
                                if (hasattr(trabajo_widget, 'text') and 
                                    hasattr(cantidad_widget, 'text') and
                                    hasattr(precio_widget, 'text') and
                                    hasattr(total_widget, 'text')):
                                    trabajo_texto = trabajo_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    precio_texto = precio_widget.text.strip()
                                    total_texto = total_widget.text.strip()
                                    if trabajo_texto and cantidad_texto:
                                        try:
                                            cantidad_num = float(cantidad_texto)
                                            if cantidad_num <= 0:
                                                continue
                                            precio_num = float(precio_texto) if precio_texto else 0.0
                                            total_num = float(total_texto) if total_texto else 0.0
                                        except ValueError:
                                            continue
                                        mano_obra.append({
                                            'operador': operador_nombre,
                                            'descripcion': trabajo_texto,
                                            'cantidad': cantidad_num,
                                            'precio': precio_num,
                                            'total': total_num
                                        })

                    # --- REPUESTOS ---
                    if hasattr(contenedor_operador, 'repuestos_container'):
                        filas_repuesto = list(contenedor_operador.repuestos_container.children)
                        filas_repuesto.reverse()
                        for fila_repuesto in filas_repuesto:
                            if isinstance(fila_repuesto, BoxLayout) and len(fila_repuesto.children) == 6:
                                children = fila_repuesto.children
                                nombre_widget = children[4]
                                cantidad_widget = children[3]
                                precio_widget = children[2]
                                total_widget = children[1]
                                if (hasattr(nombre_widget, 'text') and 
                                    hasattr(cantidad_widget, 'text') and
                                    hasattr(precio_widget, 'text') and
                                    hasattr(total_widget, 'text')):
                                    nombre_texto = nombre_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    precio_texto = precio_widget.text.strip()
                                    total_texto = total_widget.text.strip()
                                    if nombre_texto and cantidad_texto:
                                        try:
                                            cantidad_num = float(cantidad_texto)
                                            if cantidad_num <= 0:
                                                continue
                                            precio_num = float(precio_texto) if precio_texto else 0.0
                                            total_num = float(total_texto) if total_texto else 0.0
                                        except ValueError:
                                            continue
                                        repuestos.append({
                                            'operador': operador_nombre,
                                            'nombre': nombre_texto,
                                            'cantidad': cantidad_num,
                                            'precio': precio_num,
                                            'total': total_num
                                        })

                    # --- OBSERVACIONES ---
                    if hasattr(contenedor_operador, '_observacion_input'):
                        observacion_input = contenedor_operador._observacion_input
                        if hasattr(observacion_input, 'text'):
                            observacion_texto = observacion_input.text.strip()
                            if observacion_texto:
                                observaciones.append({
                                    'operador': operador_nombre,
                                    'texto': observacion_texto
                                })

            # --- 7. Totales ---
            totales = {
                'total_mano_obra': self.ids.total_mano_obra.text,
                'total_repuestos': self.ids.total_repuestos.text,
                'subtotal': self.ids.subtotal.text,
                'iva': self.ids.iva.text,
                'total_general': self.ids.total_general.text,
                'anticipo': self.ids.anticipo.text,
                'saldo': self.ids.saldo.text
            }

            # --- 8. Generar PDF ---
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            cell_style = styles["Normal"]
            cell_style.wordWrap = 'CJK'

            # Título
            elements.append(Paragraph("<b>NOTA DE ENTREGA</b>", styles['Heading1']))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"<b>Tornería Ficha Nº {numero_ficha}</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))

            # Datos del cliente
            elements.append(Paragraph("<b>DATOS DEL CLIENTE</b>", styles['Heading3']))
            data_cliente = [
                ["RIF:", datos_cliente['rif'], "Cliente:", datos_cliente['nombre']],
                ["Teléfono:", datos_cliente['telefono'], "Fecha:", datos_cliente['fecha']],
                ["Dirección:", datos_cliente['direccion'], "", ""],
            ]
            tabla_cliente = Table(data_cliente, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
            tabla_cliente.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
            ]))
            elements.append(tabla_cliente)
            elements.append(Spacer(1, 0.2*inch))

            # Partes recibidas
            if partes_recibidas:
                elements.append(Paragraph("<b>PARTES RECIBIDAS</b>", styles['Heading3']))
                data_partes = [["Parte", "Cantidad"]]
                for parte in partes_recibidas:
                    parte_nombre = Paragraph(parte['parte'], cell_style)
                    data_partes.append([parte_nombre, parte['cantidad']])
                tabla_partes = Table(data_partes, colWidths=[4*inch, 2*inch])
                tabla_partes.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(tabla_partes)
                elements.append(Spacer(1, 0.2*inch))

            # Mano de obra
            if mano_obra:
                elements.append(Paragraph("<b>MANO DE OBRA</b>", styles['Heading3']))
                data_mano_obra = [["Trabajo", "Cantidad", "Precio", "Total"]]
                for trabajo in mano_obra:
                    desc = Paragraph(trabajo['descripcion'], cell_style)
                    data_mano_obra.append([
                        desc,
                        str(int(trabajo['cantidad'])) if trabajo['cantidad'].is_integer() else str(trabajo['cantidad']),
                        f"${trabajo['precio']:.2f}",
                        f"${trabajo['total']:.2f}"
                    ])
                tabla_mano_obra = Table(data_mano_obra, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
                tabla_mano_obra.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(tabla_mano_obra)
                elements.append(Spacer(1, 0.2*inch))

            # Repuestos
            if repuestos:
                elements.append(Paragraph("<b>REPUESTOS UTILIZADOS</b>", styles['Heading3']))
                data_repuestos = [["Nombre", "Cantidad", "Precio", "Total"]]
                for repuesto in repuestos:
                    nombre = Paragraph(repuesto['nombre'], cell_style)
                    data_repuestos.append([
                        nombre,
                        str(int(repuesto['cantidad'])) if repuesto['cantidad'].is_integer() else str(repuesto['cantidad']),
                        f"${repuesto['precio']:.2f}",
                        f"${repuesto['total']:.2f}"
                    ])
                tabla_repuestos = Table(data_repuestos, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
                tabla_repuestos.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(tabla_repuestos)
                elements.append(Spacer(1, 0.2*inch))

            # Observaciones
            if observaciones:
                elements.append(Paragraph("<b>OBSERVACIONES</b>", styles['Heading3']))
                for obs in observaciones:
                    elements.append(Paragraph(f"<b>{obs['operador']}:</b> {obs['texto']}", styles['Normal']))
                    elements.append(Spacer(1, 0.1*inch))

            # Totales
            elements.append(Paragraph("<b>RESUMEN FINANCIERO</b>", styles['Heading3']))
            data_totales = [
                ["Total Mano de Obra:", totales['total_mano_obra']],
                ["Total Repuestos:", totales['total_repuestos']],
                ["Subtotal:", totales['subtotal']],
                ["I.V.A (16%):", totales['iva']],
                ["TOTAL GENERAL:", totales['total_general']],
                ["Anticipo:", totales['anticipo']],
                ["SALDO PENDIENTE:", totales['saldo']]
            ]
            tabla_totales = Table(data_totales, colWidths=[3*inch, 2*inch])
            tabla_totales.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (0, 4), (-1, 4), (0.8, 0.8, 0.8)),
                ('BACKGROUND', (0, 6), (-1, 6), (1, 0.8, 0.8)),
            ]))
            elements.append(tabla_totales)

            # Construir PDF
            doc.build(elements)
            print(f"✅ Nota de entrega generada: {filepath}")
            self.ids.mensaje_estado.text = "✅ Nota de entrega generada en el escritorio"

            # Abrir PDF automáticamente
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(filepath)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", filepath])
                else:  # Linux
                    subprocess.run(["xdg-open", filepath])
            except Exception as open_err:
                print(f"⚠️ No se pudo abrir el PDF: {open_err}")

        except Exception as e:
            print(f"❌ Error al generar nota de entrega: {e}")
            if hasattr(self, 'ids') and hasattr(self.ids, 'mensaje_estado'):
                self.ids.mensaje_estado.text = f"❌ Error al generar PDF: {str(e)}"
        
    def generar_ficha_pdf(self, filename="ficha_Torneria.pdf"):
        """
        Genera un PDF de la ficha rectificadora sin precios, solo información técnica.
        Organiza los datos por operador, como se muestra en la imagen.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        import os
        import platform
        import subprocess

        try:
            # --- 1. Preparar datos ---
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            base_folder = os.path.join(desktop, "Fichas")

            # Obtener número de ficha
            numero_ficha = str(self.numero_ficha)

            # --- 2. Crear rutas ---
            ficha_folder = os.path.join(base_folder, f"Ficha Nº{numero_ficha}")
            pdf_filename = f"Ficha Tornería Nº{numero_ficha}.pdf"
            filepath = os.path.join(ficha_folder, pdf_filename)

            # --- 3. Crear carpetas si no existen ---
            os.makedirs(ficha_folder, exist_ok=True)

            # --- 4. Recopilar datos de la interfaz ---
            datos_cliente = {
                'rif': self.ids.tipo_rif.text + self.ids.nuevo_rif.text.strip(),
                'nombre': self.ids.nuevo_cliente.text.strip(),
                'telefono': self.ids.nuevo_telefono.text.strip(),
                'direccion': self.ids.nueva_direccion.text.strip(),
                'fecha': self.ids.nueva_fecha.text
            }

            # --- 5. Partes recibidas ---
            partes_recibidas = []
            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout and hasattr(grid_layout, 'children'):
                widgets_en_orden = list(reversed(grid_layout.children))
                for i in range(0, len(widgets_en_orden), 3):
                    if i + 2 < len(widgets_en_orden):
                        cantidad_widget = widgets_en_orden[i]
                        pieza_widget = widgets_en_orden[i + 1]
                        if (isinstance(cantidad_widget, TextInput) and 
                            isinstance(pieza_widget, TextInput) and
                            getattr(cantidad_widget, 'hint_text', None) == "Cantidad" and
                            getattr(pieza_widget, 'hint_text', None) == "Pieza"):
                            cantidad = cantidad_widget.text.strip()
                            nombre_pieza = pieza_widget.text.strip()
                            if nombre_pieza and cantidad:
                                try:
                                    if float(cantidad) <= 0:
                                        continue
                                except (ValueError, TypeError):
                                    continue
                                partes_recibidas.append({
                                    'nombre': nombre_pieza,
                                    'cantidad': cantidad
                                })

            # --- 6. Generar PDF ---
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            cell_style = styles["Normal"]
            cell_style.wordWrap = 'CJK'

            # --- Estilo personalizado para encabezado de operador (sin <b>) ---
            operador_header_style = ParagraphStyle(
                name='OperadorHeader',
                parent=styles['Heading3'],
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=14,
                alignment=1  # Centrado
            )

            # --- Título principal ---
            titulo = Paragraph(f"Tornería: Ficha Nº {numero_ficha}", styles['Heading1'])
            elements.append(titulo)
            elements.append(Spacer(1, 0.2*inch))

            # --- Datos del Cliente ---
            elements.append(Paragraph("DATOS DEL CLIENTE", styles['Heading3']))
            data_cliente = [
                ["Cliente:", datos_cliente['nombre'], "Fecha:", datos_cliente['fecha']]
            ]
            tabla_cliente = Table(data_cliente, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
            tabla_cliente.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 0), (0, -1), (0.9, 0.9, 0.9)),
                ('BACKGROUND', (2, 0), (2, -1), (0.9, 0.9, 0.9)),
            ]))
            elements.append(tabla_cliente)
            elements.append(Spacer(1, 0.2*inch))

            # --- Partes Recibidas ---
            if partes_recibidas:
                elements.append(Paragraph("PARTES RECIBIDAS", styles['Heading3']))
                elements.append(Spacer(1, 0.1*inch))
                data_partes = [["Parte", "Cantidad"]]
                for parte in partes_recibidas:
                    nombre_para_tabla = Paragraph(parte['nombre'], cell_style)
                    data_partes.append([nombre_para_tabla, parte['cantidad']])
                tabla_partes = Table(data_partes, colWidths=[4*inch, 2*inch])
                tabla_partes.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(tabla_partes)
                elements.append(Spacer(1, 0.2*inch))

            # --- Procesar operadores ---
            if hasattr(self.ids, 'grid_mano_obra'):
                operadores = list(self.ids.grid_mano_obra.children)
                operadores.reverse()

                for contenedor_mano_obra_completo in operadores:
                    if not contenedor_mano_obra_completo.children:
                        continue
                    contenedor_operador = contenedor_mano_obra_completo.children[0]

                    operador_nombre = "N/A"
                    for child in contenedor_operador.children:
                        if isinstance(child, BoxLayout):
                            for subchild in child.children:
                                if hasattr(subchild, 'text') and "Operador:" in str(subchild.text):
                                    # Limpiar etiquetas Kivy
                                    operador_raw = subchild.text.replace("Operador:", "").strip()
                                    operador_nombre = limpiar_etiquetas_kivy(operador_raw)
                                    break

                    # --- Trabajos ---
                    trabajos = []
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        filas_trabajo = list(contenedor_operador.trabajos_container.children)
                        filas_trabajo.reverse()
                        for fila_layout in filas_trabajo:
                            if isinstance(fila_layout, BoxLayout) and len(fila_layout.children) == 6:
                                children = fila_layout.children
                                trabajo_widget = children[5]
                                cantidad_widget = children[4]
                                if (hasattr(trabajo_widget, 'text') and hasattr(cantidad_widget, 'text')):
                                    trabajo_texto = trabajo_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    if trabajo_texto and cantidad_texto:
                                        try:
                                            cantidad_num = float(cantidad_texto)
                                            if cantidad_num <= 0:
                                                continue
                                        except (ValueError, TypeError):
                                            continue
                                        trabajos.append({
                                            'descripcion': trabajo_texto,
                                            'cantidad': str(int(cantidad_num)) if cantidad_num.is_integer() else str(cantidad_num)
                                        })

                    # --- Repuestos ---
                    repuestos = []
                    if hasattr(contenedor_operador, 'repuestos_container'):
                        filas_repuesto = list(contenedor_operador.repuestos_container.children)
                        filas_repuesto.reverse()
                        for fila_repuesto in filas_repuesto:
                            if isinstance(fila_repuesto, BoxLayout) and len(fila_repuesto.children) == 6:
                                children = fila_repuesto.children
                                nombre_widget = children[4]
                                cantidad_widget = children[3]
                                if (hasattr(nombre_widget, 'text') and hasattr(cantidad_widget, 'text')):
                                    nombre_texto = nombre_widget.text.strip()
                                    cantidad_texto = cantidad_widget.text.strip()
                                    if nombre_texto and cantidad_texto:
                                        try:
                                            cantidad_num = float(cantidad_texto)
                                            if cantidad_num <= 0:
                                                continue
                                        except (ValueError, TypeError):
                                            continue
                                        repuestos.append({
                                            'nombre': nombre_texto,
                                            'cantidad': str(int(cantidad_num)) if cantidad_num.is_integer() else str(cantidad_num)
                                        })

                    # --- Observaciones ---
                    observacion_texto = ""
                    if hasattr(contenedor_operador, '_observacion_input'):
                        observacion_input = contenedor_operador._observacion_input
                        if hasattr(observacion_input, 'text'):
                            observacion_texto = observacion_input.text.strip()

                    # --- Solo agregar sección si hay datos ---
                    if trabajos or repuestos or observacion_texto:
                        # Encabezado del operador SIN <b>
                        header_text = f"OPERADOR: {operador_nombre} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Ficha Nº {self.numero_ficha} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Fecha: {self.ids.nueva_fecha.text}"
                        elements.append(Paragraph(header_text, operador_header_style))
                        elements.append(Spacer(1, 0.1*inch))

                        # Trabajos
                        if trabajos:
                            data_trabajos = [["Trabajo", "Cantidad"]]
                            for trabajo in trabajos:
                                desc = Paragraph(trabajo['descripcion'], cell_style)
                                data_trabajos.append([desc, trabajo['cantidad']])
                            tabla_trabajos = Table(data_trabajos, colWidths=[4*inch, 2*inch])
                            tabla_trabajos.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                                ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ]))
                            elements.append(tabla_trabajos)
                            elements.append(Spacer(1, 0.2*inch))

                        # Repuestos
                        if repuestos:
                            elements.append(Paragraph("REPUESTOS ASOCIADOS", styles['Heading3']))
                            elements.append(Spacer(1, 0.1*inch))
                            data_repuestos = [["Nombre", "Cantidad"]]
                            for repuesto in repuestos:
                                nombre = Paragraph(repuesto['nombre'], cell_style)
                                data_repuestos.append([nombre, repuesto['cantidad']])
                            tabla_repuestos = Table(data_repuestos, colWidths=[4*inch, 2*inch])
                            tabla_repuestos.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                                ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ]))
                            elements.append(tabla_repuestos)
                            elements.append(Spacer(1, 0.2*inch))

                        # Observaciones
                        if observacion_texto:
                            elements.append(Paragraph("OBSERVACIONES", styles['Heading3']))
                            elements.append(Spacer(1, 0.1*inch))
                            observacion_paragraph = Paragraph(observacion_texto, cell_style)
                            tabla_observacion = Table([[observacion_paragraph]], colWidths=[6*inch])
                            tabla_observacion.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                                ('BACKGROUND', (0, 0), (-1, -1), (0.9, 0.9, 0.9)),
                                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                                ('TOPPADDING', (0, 0), (-1, -1), 6),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ]))
                            elements.append(tabla_observacion)
                            elements.append(Spacer(1, 0.2*inch))

            # Construir PDF
            doc.build(elements)
            print(f"✅ Ficha PDF generada: {filepath}")
            self.ids.mensaje_estado.text = f"✅ Ficha PDF generada en el escritorio"

            # Abrir PDF automáticamente
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(filepath)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", filepath])
                else:  # Linux
                    subprocess.run(["xdg-open", filepath])
            except Exception as open_err:
                print(f"⚠️ No se pudo abrir el PDF automáticamente: {open_err}")

        except Exception as e:
            print(f"❌ Error al generar ficha PDF: {e}")
            if hasattr(self, 'ids') and hasattr(self.ids, 'mensaje_estado'):
                self.ids.mensaje_estado.text = f"❌ Error al generar PDF: {str(e)}"

    def _crear_fila_trabajo_con_datos(self, contenedor_trabajos, contenedor_completo, nombre=""):
        """Crea una fila de trabajo con datos predefinidos (usado desde popup)."""
        from kivy.uix.checkbox import CheckBox
        from kivy.metrics import dp

        # Encontrar trabajos_container
        trabajos_container = None
        for child in contenedor_trabajos.children:
            if hasattr(child, 'orientation') and child.orientation == 'vertical':
                trabajos_container = child
                break
        if not trabajos_container:
            print("❌ No se encontró trabajos_container")
            return

        weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]
        fila_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35),
            spacing=2
        )

        trabajo_input = TextInput(
            text=nombre,
            multiline=False,
            size_hint_x=weights[0],
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        cantidad_input = TextInput(
            text="",
            multiline=False,
            input_filter='float',
            size_hint_x=weights[1],
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        precio_input = TextInput(
            text="",
            multiline=False,
            input_filter='float',
            size_hint_x=weights[2],
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        total_input = TextInput(
            text="0.00",
            multiline=False,
            readonly=True,
            size_hint_x=weights[3],
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(0.9, 0.9, 0.9, 1)
        )
        terminado_check = CheckBox(
            active=False,
            size_hint_x=weights[4],
            size_hint_y=None,
            height=dp(35)
        )
        btn_eliminar_fila = Button(
            text='×',
            size_hint_x=weights[5],
            size_hint_y=None,
            height=dp(35),
            background_color=(0.7, 0.3, 0.3, 1)
        )

        def calcular_total(*args):
            try:
                c = float(cantidad_input.text or 0)
                p = float(precio_input.text or 0)
                total_input.text = f"{c * p:.2f}"
            except:
                total_input.text = "0.00"
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

        cantidad_input.bind(text=calcular_total)
        precio_input.bind(text=calcular_total)

        def eliminar_esta_fila(instance):
            if fila_layout.parent:
                padre = fila_layout.parent
                padre.remove_widget(fila_layout)
                trabajos_container.height -= dp(40)
                contenedor_trabajos.height -= dp(40)
                contenedor_completo.height -= dp(40)

        btn_eliminar_fila.bind(on_press=eliminar_esta_fila)

        fila_layout.add_widget(trabajo_input)
        fila_layout.add_widget(cantidad_input)
        fila_layout.add_widget(precio_input)
        fila_layout.add_widget(total_input)
        fila_layout.add_widget(terminado_check)
        fila_layout.add_widget(btn_eliminar_fila)

        trabajos_container.add_widget(fila_layout)
        # Actualiza alturas
        trabajos_container.height += dp(40)
        contenedor_trabajos.height += dp(40)
        contenedor_completo.height += dp(10)
        if contenedor_trabajos.parent:
            contenedor_trabajos.parent.height += dp(40)
        if contenedor_trabajos.parent and contenedor_trabajos.parent.parent:
            contenedor_trabajos.parent.parent.height += dp(30)
        Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.2)





class FichaTornoModificar(FichaTorno):
    def __init__(self, ficha_datos, callback_guardado=None, nivel=None, **kwargs):
        self.ficha_datos = ficha_datos
        self.es_modificacion = True
        
        # ✅ Envolver el callback para pasar los parámetros correctos
        def wrapped_callback(numero_ficha, datos_actualizados):
            if callback_guardado:
                callback_guardado(numero_ficha, datos_actualizados)
        
        self.callback_guardado = wrapped_callback
        super().__init__(nivel=nivel,**kwargs)

    def inicializar_popup(self, dt):
        # Usar el número de ficha existente
        self.numero_ficha = self.ficha_datos['numero_ficha']
        self.title = f'Modificar Ficha Torno #{self.numero_ficha}'
        # Cargar datos después de que la interfaz esté lista
        Clock.schedule_once(self.cargar_datos_existentes, 0.2)

    def cargar_datos_existentes(self, dt):
        """Carga los datos de la ficha seleccionada en la interfaz"""
        try:
            # === DATOS DEL CLIENTE ===
            cliente = self.ficha_datos.get('cliente', {})
            rif = cliente.get('rif', 'V-')
            self.ids.tipo_rif.text = rif[:2] if len(rif) > 2 else 'V-'
            self.ids.nuevo_rif.text = rif[2:] if len(rif) > 2 else ''
            self.ids.nuevo_cliente.text = cliente.get('nombre', '')
            self.ids.nuevo_telefono.text = cliente.get('telefono', '')
            self.ids.nueva_direccion.text = cliente.get('direccion', '')
            self.ids.nueva_fecha.text = cliente.get('fecha_registro', '')

            # === PARTES RECIBIDAS DINÁMICAS ===
            partes = self.ficha_datos.get('partes_recibidas', [])
            grid_layout = self.ids.get('grid_partes_recibidas')
            if grid_layout and partes:
                for parte in partes:
                    nombre_pieza = parte.get('parte', '')
                    cantidad_pieza = parte.get('cantidad', '1')
                    self._agregar_fila_dinamica_desde_bd(grid_layout, nombre_pieza, cantidad_pieza)

            # === OBSERVACIÓN DE PARTES RECIBIDAS (desde BD) ===
            observacion_partes_bd = self.ficha_datos.get('observacion_partes_recibidas', '').strip()
            if observacion_partes_bd:
                self.agregar_observacion_partes_recibidas()
                if hasattr(self, '_observacion_partes_widget') and self._observacion_partes_widget:
                    self._observacion_partes_widget.text = observacion_partes_bd
                    print(f"✅ Observación de partes recibidas cargada: {observacion_partes_bd[:50]}...")

            # === MANO DE OBRA Y REPUESTOS POR OPERADOR ===
            print("🔍 Cargando mano de obra y repuestos por operador...")
            self.cargar_mano_obra_y_repuestos()

            # === OBSERVACIONES ===
            observaciones = self.ficha_datos.get('observaciones', [])
            self.cargar_observaciones_existentes(observaciones)

            # === TOTALES ===
            totales = self.ficha_datos.get('totales', {})
            self.ids.total_mano_obra.text = f"${totales.get('total_mano_obra', 0):,.2f}"
            self.ids.total_repuestos.text = f"${totales.get('total_repuestos', 0):,.2f}"
            self.ids.subtotal.text = f"${totales.get('subtotal', 0):,.2f}"
            self.ids.iva.text = f"${totales.get('iva', 0):,.2f}"
            self.ids.total_general.text = f"${totales.get('total_general', 0):,.2f}"
            self.ids.anticipo.text = f"{totales.get('anticipo', 0):.2f}"
            self.ids.abonos.text = f"{totales.get('abonos', 0):.2f}"
            self.ids.saldo.text = f"${totales.get('saldo', 0):,.2f}"

            # Recalcular para asegurar coherencia visual
            Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.3)
            print(f"✅ Datos cargados para ficha Torno #{self.numero_ficha}")

        except Exception as e:
            print(f"❌ Error al cargar datos existentes: {e}")
            import traceback
            traceback.print_exc()


    def cargar_mano_obra_y_repuestos(self):
        """Carga la mano de obra existente asociada a la ficha, incluyendo repuestos por operador (igual que FichaRectificadoraModificar)"""
        try:
            # Los datos de mano de obra y repuestos están directamente en self.ficha_datos
            mano_obra_array = self.ficha_datos.get('mano_obra', [])
            repuestos_array = self.ficha_datos.get('repuestos', [])
            print(f"🔍 Cargando mano de obra: {len(mano_obra_array)} elementos encontrados")
            print(f"📦 Cargando repuestos: {len(repuestos_array)} elementos encontrados")

            # Agrupar trabajos por operador
            operadores_trabajos = {}
            operadores_repuestos = {}
            for trabajo in mano_obra_array:
                operador_nombre = trabajo.get('operador', 'Sin operador')
                if operador_nombre not in operadores_trabajos:
                    operadores_trabajos[operador_nombre] = []
                operadores_trabajos[operador_nombre].append(trabajo)

            # Agrupar repuestos por operador
            for repuesto in repuestos_array:
                operador_nombre = repuesto.get('operador', 'Sin operador')
                if operador_nombre not in operadores_repuestos:
                    operadores_repuestos[operador_nombre] = []
                operadores_repuestos[operador_nombre].append(repuesto)

            # Crear la interfaz para cada operador
            for operador_nombre, trabajos in operadores_trabajos.items():
                # ✅ 1. CREAR EL CONTENEDOR PRINCIPAL
                contenedor_mano_obra_completo = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(370),
                    spacing=5,
                    padding=[20, 10, 20, 10]
                )

                # ✅ 2. CREAR EL CONTENEDOR DEL OPERADOR
                contenedor_operador = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(300),
                    spacing=5,
                    padding=[10, 10, 10, 10]
                )

                # ✅ 3. HEADER DEL OPERADOR
                header_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40),
                    spacing=10,
                    padding=[0, 5, 0, 5]
                )
                operador_label = Label(
                    text=f"[b]Operador:[/b] {operador_nombre}",
                    size_hint_x=0.8,
                    size_hint_y=None,
                    height=dp(35),
                    font_size=16,
                    text_size=(None, dp(35)),
                    halign='left',
                    valign='middle',
                    color=(1, 1, 1, 1),
                    markup=True,
                    bold=True
                )
                with operador_label.canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    rect_label = Rectangle(size=operador_label.size, pos=operador_label.pos)
                operador_label._bg_rect_label = rect_label
                def actualizar_fondo_label(instance, value):
                    if hasattr(instance, '_bg_rect_label'):
                        instance._bg_rect_label.pos = instance.pos
                        instance._bg_rect_label.size = instance.size
                operador_label.bind(pos=actualizar_fondo_label, size=actualizar_fondo_label)

                def eliminar_operador(instance):
                    self.ids.grid_mano_obra.remove_widget(contenedor_mano_obra_completo)
                    Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)
                    Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
                    print("Operador eliminado y totales recalculados")

                btn_eliminar = Button(
                    text='×',
                    size_hint=(None, None),
                    size=(dp(35), dp(35)),
                    background_color=(0.8, 0.2, 0.2, 1),
                    font_size=18,
                    color=(1, 1, 1, 1),
                    bold=True
                )
                btn_eliminar.bind(on_press=eliminar_operador)

                btn_observacion = Button(
                    text='!',
                    size_hint=(None, None),
                    size=(dp(35), dp(35)),
                    background_color=(0.2, 0.2, 0.8, 1),
                    font_size=18,
                    color=(1, 1, 1, 1),
                    bold=True
                )
                btn_observacion.bind(on_press=lambda instance: self.agregar_bloque_observacion_a_operador(contenedor_operador, contenedor_mano_obra_completo))

                header_layout.add_widget(operador_label)
                header_layout.add_widget(btn_observacion)
                header_layout.add_widget(btn_eliminar)
                contenedor_operador.add_widget(header_layout)

                # ✅ 4. SEPARADOR
                separador = Widget(size_hint_y=None, height=dp(10))
                contenedor_operador.add_widget(separador)

                # ✅ 5. CONTENEDOR DE TRABAJOS
                contenedor_trabajos = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(35) + (len(trabajos) * dp(37)) + dp(20),
                    spacing=3,
                    padding=[0, 5, 0, 10]
                )

                # Headers
                headers_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=2)
                headers = ['Trabajo', 'Cantidad', 'Precio', 'Total', 'Terminado']
                weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]
                for i, header in enumerate(headers):
                    label = Label(text=header, size_hint_x=weights[i], color=(0.9, 0.9, 0.9, 1), bold=True, halign='center', valign='middle')
                    headers_layout.add_widget(label)

                btn_agregar_trabajo = Button(
                    text='+',
                    size_hint_x=weights[-1],
                    size_hint_y=None,
                    height=dp(35),
                    background_color=(0.2, 0.7, 0.2, 1)
                )
                
                
                if getattr(self, 'nivel_usuario', None) == 1:
                    btn_agregar_trabajo.disabled = True
                    btn_eliminar.disabled = True

                def abrir_popup_trabajos(instance):
                    if not operador_nombre or operador_nombre == "(Seleccionar operador)":
                        self.agregar_fila_trabajo2(contenedor_trabajos)
                        return

                    # ✅ Obtener los nombres de los trabajos YA agregados
                    trabajos_actuales = []
                    if hasattr(contenedor_operador, 'trabajos_container'):
                        for fila in contenedor_operador.trabajos_container.children:
                            if len(fila.children) >= 6:
                                trabajo_input = fila.children[5]  # TextInput del trabajo
                                if hasattr(trabajo_input, 'text') and trabajo_input.text.strip():
                                    trabajos_actuales.append(trabajo_input.text.strip())

                    def on_trabajos_seleccionados(trabajos_seleccionados, custom_vacio):
                        # Agregar trabajos normales
                        for trabajo_nombre in trabajos_seleccionados:
                            self._crear_fila_trabajo_con_datos(contenedor_trabajos, contenedor_mano_obra_completo, nombre=trabajo_nombre)
                        # Agregar fila vacía si se marcó la opción personalizada
                        if custom_vacio:
                            self._crear_fila_trabajo_con_datos(contenedor_trabajos,contenedor_mano_obra_completo, nombre="")
                        Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

                    popup = TrabajosOperadorPopup(
                        operador_nombre=operador_nombre,
                        callback=on_trabajos_seleccionados,
                        trabajos_preseleccionados=trabajos_actuales
                    )
                    popup.open()

                btn_agregar_trabajo.bind(on_press=abrir_popup_trabajos)

                headers_layout.add_widget(btn_agregar_trabajo)
                contenedor_trabajos.add_widget(headers_layout)

                # ✅ 6. CONTENEDOR DE FILAS DE TRABAJO
                trabajos_container = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=len(trabajos) * dp(35),
                    spacing=2
                )
                contenedor_trabajos.add_widget(trabajos_container)
                contenedor_operador.add_widget(contenedor_trabajos)

                # ✅ 7. SECCIÓN DE REPUESTOS
                repuestos_label = Label(
                    text="REPUESTOS ASOCIADOS AL OPERADOR",
                    size_hint_y=None,
                    height=dp(25),
                    font_size=12,
                    bold=True,
                    color=(0.9, 0.9, 0.9, 1),
                    halign='left',
                    valign='middle',
                    padding=[0, 5, 0, 0]
                )
                contenedor_operador.add_widget(repuestos_label)

                btn_agregar_repuestos = Button(
                    text='+ Agregar Repuesto',
                    size_hint_y=None,
                    height=dp(35),
                    background_color=(0.2, 0.7, 0.2, 1),
                    font_size=12
                )
                
                if getattr(self, 'nivel_usuario', None) == 2:
                    btn_agregar_repuestos.disabled = True
        
                def abrir_popup_repuestos_para_operador(instance):
                    def on_repuesto_seleccionado(repuesto):
                        self.agregar_repuesto_a_operador(contenedor_operador, repuesto, contenedor_mano_obra_completo)
                    popup = RepuestosPopup(callback=on_repuesto_seleccionado)
                    popup.open()
                btn_agregar_repuestos.bind(on_press=abrir_popup_repuestos_para_operador)
                contenedor_operador.add_widget(btn_agregar_repuestos)

                # ✅ 8. CONTENEDOR DE REPUESTOS (con encabezado)
                repuestos_container = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(40),
                    spacing=2,
                    padding=[20, 0, 0, 0]
                )
                fila_encabezado = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=2)
                weights_rep = [0.2, 0.3, 0.15, 0.15, 0.15, 0.05]
                headers_rep = ['Código', 'Nombre', 'Cantidad', 'Precio', 'Total', 'Acción']
                for i, header in enumerate(headers_rep):
                    label = Label(text=header, size_hint_x=weights_rep[i], color=(0.9, 0.9, 0.9, 1), bold=True, halign='center', valign='middle')
                    fila_encabezado.add_widget(label)
                repuestos_container.add_widget(fila_encabezado)
                contenedor_operador.add_widget(repuestos_container)
                contenedor_operador.repuestos_container = repuestos_container

                # ✅ 9. REFERENCIAS
                contenedor_operador.trabajos_container = trabajos_container
                contenedor_operador.operador_label = operador_label
                contenedor_operador.btn_eliminar = btn_eliminar

                # ✅ 10. AÑADIR AL CONTENEDOR PRINCIPAL
                contenedor_mano_obra_completo.add_widget(contenedor_operador)

                # ✅ 11. AGREGAR TRABAJOS EXISTENTES
                for trabajo_data in trabajos:
                    self.agregar_trabajo_existente_cargado(contenedor_trabajos, trabajo_data)

                # ✅ 12. AGREGAR REPUESTOS EXISTENTES
                repuestos_del_operador = operadores_repuestos.get(operador_nombre, [])
                for repuesto_data in repuestos_del_operador:
                    self.agregar_repuesto_existente_a_operador(contenedor_operador, repuesto_data, contenedor_mano_obra_completo)

                # ✅ 13. AJUSTAR ALTURAS
                num_trabajos = len(trabajos)
                num_repuestos = len(repuestos_del_operador)
                trabajos_container.height = num_trabajos * dp(35)
                contenedor_trabajos.height = dp(35) + (num_trabajos * dp(37)) + dp(20)
                repuestos_container.height = dp(40) + (num_repuestos * dp(35))
                contenedor_operador.height = dp(300) + (num_trabajos * dp(35)) + (num_repuestos * dp(35))
                contenedor_mano_obra_completo.height = dp(370) + (num_trabajos * dp(35)) + (num_repuestos * dp(35))

                # ✅ 14. AÑADIR AL GRID
                self.ids.grid_mano_obra.add_widget(contenedor_mano_obra_completo)
                print(f"✅ Operador {operador_nombre} cargado: {num_trabajos} trabajos, {num_repuestos} repuestos")

            Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)
            print(f"✅ Mano de obra y repuestos cargados: {len(operadores_trabajos)} operadores")

        except Exception as e:
            print(f"❌ Error al cargar trabajos: {e}")
            import traceback
            traceback.print_exc()




    def agregar_trabajo_existente_cargado(self, contenedor_trabajos, trabajo_data):
        """Agrega una fila de trabajo existente desde la base de datos al contenedor de trabajos"""
        try:
            trabajos_container = None
            for child in contenedor_trabajos.children:
                if hasattr(child, 'orientation') and child.orientation == 'vertical':
                    trabajos_container = child
                    break
            if not trabajos_container:
                print("❌ No se encontró trabajos_container")
                return

            weights = [0.35, 0.15, 0.15, 0.15, 0.15, 0.05]
            fila_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=2)
            trabajo_input = TextInput(text=trabajo_data.get('descripcion', ''), multiline=False, size_hint_x=weights[0], background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1))
            cantidad_input = TextInput(text=str(trabajo_data.get('cantidad', 1)), multiline=False, input_filter='float', size_hint_x=weights[1], background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1))
            precio_input = TextInput(text=f"{trabajo_data.get('precio', 0.0):.2f}", multiline=False, input_filter='float', size_hint_x=weights[2], background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1))
            total_input = TextInput(text=f"{trabajo_data.get('total', 0.0):.2f}", multiline=False, readonly=True, size_hint_x=weights[3], background_color=(0.15, 0.15, 0.15, 1), foreground_color=(0.9, 0.9, 0.9, 1))
            terminado_check = CheckBox(active=trabajo_data.get('terminado', False), size_hint_x=weights[4], size_hint_y=None, height=dp(35))
            btn_eliminar_fila = Button(text='×', size_hint_x=weights[5], size_hint_y=None, height=dp(35), background_color=(0.7, 0.3, 0.3, 1))
            
            if getattr(self, 'nivel_usuario', None) == 1:
                precio_input.readonly = True
                precio_input.background_color = (0.15, 0.15, 0.15, 1)  
                precio_input.foreground_color = (0.6, 0.6, 0.6, 1)
                trabajo_input.readonly = True
                trabajo_input.background_color = (0.15, 0.15, 0.15, 1)  
                trabajo_input.foreground_color = (0.6, 0.6, 0.6, 1)
                cantidad_input.readonly = True
                cantidad_input.background_color = (0.15, 0.15, 0.15, 1)  
                cantidad_input.foreground_color = (0.6, 0.6, 0.6, 1)
                terminado_check.disabled = True
                btn_eliminar_fila.disabled = True

            def calcular_total(*args):
                try:
                    c = float(cantidad_input.text or 0)
                    p = float(precio_input.text or 0)
                    total_input.text = f"{c * p:.2f}"
                except:
                    total_input.text = "0.00"
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            cantidad_input.bind(text=calcular_total)
            precio_input.bind(text=calcular_total)

            def eliminar_esta_fila(instance):
                try:
                    if fila_layout.parent:
                        padre = fila_layout.parent
                        padre.remove_widget(fila_layout)
                        padre.height -= dp(35)
                        contenedor_trabajos.height -= dp(35)
                        contenedor_operador = contenedor_trabajos.parent
                        if contenedor_operador:
                            contenedor_operador.height -= dp(35)
                        contenedor_mano_obra_completo = contenedor_operador.parent if hasattr(contenedor_operador, 'parent') else None
                        if contenedor_mano_obra_completo:
                            contenedor_mano_obra_completo.height -= dp(35)
                        Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)
                        print(f"✅ Fila eliminada. Nueva altura: {padre.height:.0f}dp")
                except Exception as e:
                    print(f"❌ Error eliminando fila: {e}")

            btn_eliminar_fila.bind(on_press=eliminar_esta_fila)

            fila_layout.add_widget(trabajo_input)
            fila_layout.add_widget(cantidad_input)
            fila_layout.add_widget(precio_input)
            fila_layout.add_widget(total_input)
            fila_layout.add_widget(terminado_check)
            fila_layout.add_widget(btn_eliminar_fila)
            trabajos_container.add_widget(fila_layout, index=0)

            trabajos_container.height += dp(35)
            contenedor_trabajos.height += dp(35)
            contenedor_operador = contenedor_trabajos.parent
            contenedor_operador.height += dp(35)
            contenedor_mano_obra_completo = contenedor_operador.parent if hasattr(contenedor_operador, 'parent') else None
            if contenedor_mano_obra_completo:
                contenedor_mano_obra_completo.height += dp(35)
            Clock.schedule_once(lambda dt: setattr(self.ids.grid_mano_obra, 'height', self.ids.grid_mano_obra.minimum_height), 0.2)
            print(f"✅ Fila de trabajo cargada. Nueva altura: {trabajos_container.height:.0f}dp")

        except Exception as e:
            print(f"❌ Error al agregar fila de trabajo existente: {e}")
            import traceback
            traceback.print_exc()
 
    def agregar_repuesto_existente_a_operador(self, contenedor_operador, repuesto_data, contenedor_mano_obra_completo):
        """Agrega un repuesto existente al contenedor de repuestos del operador (desde BD)"""
        try:
            from kivy.uix.textinput import TextInput
            from kivy.uix.button import Button
            from kivy.metrics import dp
            from kivy.clock import Clock

            # Obtener repuestos_container (debe existir desde cargar_mano_obra_existente)
            repuestos_container = getattr(contenedor_operador, 'repuestos_container', None)
            if not repuestos_container:
                print("❌ No se encontró repuestos_container para el operador")
                return

            # Crear fila de repuesto (estructura igual que en agregar_repuesto_a_operador)
            fila_repuesto = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=2
            )

            # Campo Código (desde BD)
            codigo_input = TextInput(
                text=str(repuesto_data.get('codigo', 'Me la pelas')),
                multiline=False,
                readonly = True,
                size_hint_x=0.2,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Nombre (desde BD, readonly para evitar cambios accidentales, pero editable si quieres)
            nombre_input = TextInput(
                text=repuesto_data.get('nombre', ''),
                multiline=False,
                readonly = True,
                size_hint_x=0.3,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Cantidad (desde BD, editable)
            cantidad_input = TextInput(
                text=str(repuesto_data.get('cantidad', 1)),  # Valor de BD, no hardcoded "1"
                multiline=False,
                input_filter='float',
                size_hint_x=0.15,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Precio (desde BD, editable)
            precio_input = TextInput(
                text=f"{repuesto_data.get('precio', 0.0):.2f}",  # Valor de BD
                multiline=False,
                input_filter='float',
                size_hint_x=0.15,
                font_size=12,
                foreground_color=(1, 1, 1, 1),
                background_color=(0.15, 0.15, 0.15, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Campo Total (desde BD inicialmente, readonly pero se actualiza dinámicamente)
            total_input = TextInput(
                text=f"{repuesto_data.get('total', 0.0):.2f}",  # Valor de BD o calcular si no existe
                multiline=False,
                readonly=True,
                size_hint_x=0.15,
                font_size=12,
                foreground_color=(0.9, 0.9, 0.9, 1),
                background_color=(0.1, 0.1, 0.1, 1),
                size_hint_y=None,
                height=dp(35)
            )

            # Botón Eliminar
            btn_eliminar = Button(
                text='×',
                size_hint_x=0.05,
                size_hint_y=None,
                height=dp(35),
                background_color=(0.7, 0.3, 0.3, 1),
                color=(1, 1, 1, 1),
                bold=True,
                font_size=16
            )
            if getattr(self, 'nivel_usuario', None) == 2:
                precio_input.readonly = True
                precio_input.background_color = (0.15, 0.15, 0.15, 1)  
                precio_input.foreground_color = (0.6, 0.6, 0.6, 1)
                cantidad_input.readonly = True
                cantidad_input.background_color = (0.15, 0.15, 0.15, 1)  
                cantidad_input.foreground_color = (0.6, 0.6, 0.6, 1)
                btn_eliminar.disabled = True

            # Función para calcular total (igual que en la clase base)
            def calcular_total(*args):
                try:
                    c = float(cantidad_input.text or 0)
                    p = float(precio_input.text or 0)
                    nuevo_total = c * p
                    total_input.text = f"{nuevo_total:.2f}"
                except ValueError:
                    total_input.text = "0.00"
                # Recalcular totales globales
                Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

            # Bindear eventos de cambio (editable como en la base)
            cantidad_input.bind(text=calcular_total)
            precio_input.bind(text=calcular_total)

            # Función de eliminación (igual que en la clase base, ajusta alturas)
            def eliminar_fila(instance):
                if fila_repuesto.parent:
                    # Remover la fila
                    fila_repuesto.parent.remove_widget(fila_repuesto)

                    # Reducir alturas de contenedores
                    repuestos_container.height -= dp(35)
                    contenedor_operador.height -= dp(35)
                    contenedor_mano_obra_completo.height -= dp(35)

                    # Verificar si quedan filas de datos (excluyendo encabezado)
                    filas_datos = [
                        child for child in repuestos_container.children
                        if isinstance(child, BoxLayout) and len(child.children) == 6  # Fila completa de repuesto
                    ]

                    # Si no quedan filas, opcionalmente remover encabezado (pero mantener contenedor vacío)
                    if len(filas_datos) == 0:
                        # Buscar y remover encabezado si quieres (opcional, para limpiar)
                        for child in repuestos_container.children:
                            if isinstance(child, BoxLayout) and len(child.children) == 5:  # Encabezado tiene 5 labels
                                repuestos_container.remove_widget(child)
                                break
                        repuestos_container.height = 0  # Ocultar si vacío

                    # Recalcular totales
                    Clock.schedule_once(lambda dt: self.calcular_todos_los_totales(), 0.1)

                    print(f"🗑️ Repuesto eliminado. Nueva altura repuestos_container: {repuestos_container.height:.0f}dp")

                else:
                    print("❌ La fila ya fue eliminada o no tiene padre")

            btn_eliminar.bind(on_press=eliminar_fila)

            # Agregar widgets a la fila (orden: código, nombre, cantidad, precio, total, botón)
            fila_repuesto.add_widget(codigo_input)
            fila_repuesto.add_widget(nombre_input)
            fila_repuesto.add_widget(cantidad_input)
            fila_repuesto.add_widget(precio_input)
            fila_repuesto.add_widget(total_input)
            fila_repuesto.add_widget(btn_eliminar)

            # Añadir la fila al contenedor (al inicio para orden inverso en Kivy)
            repuestos_container.add_widget(fila_repuesto, index=0)

            # Aumentar alturas de contenedores (igual que en la base)
            repuestos_container.height += dp(35)
            contenedor_operador.height += dp(35)
            contenedor_mano_obra_completo.height += dp(35)

            # Calcular total inicial (por si los datos de BD no coinciden)
            calcular_total()

            # Actualizar grid principal
            Clock.schedule_once(lambda dt: self._actualizar_grid_altura(), 0.1)

            print(f"✅ Repuesto existente agregado: {repuesto_data.get('nombre', 'N/A')} | Cant: {repuesto_data.get('cantidad', 1)} | Precio: {repuesto_data.get('precio', 0.0):.2f} | Total: {repuesto_data.get('total', 0.0):.2f}")

        except Exception as e:
            print(f"❌ Error al agregar repuesto existente a operador: {e}")
            import traceback
            traceback.print_exc()



    def cargar_observaciones_existentes(self, observaciones_array):
        """Carga observaciones por operador (igual que en FichaRectificadoraModificar)"""
        try:
            if not observaciones_array:
                return

            # Agrupar por operador
            obs_por_operador = {}
            for obs in observaciones_array:
                op = obs.get('operador', 'Sin operador')
                texto = obs.get('texto', '').strip()
                if texto:
                    obs_por_operador.setdefault(op, []).append(texto)

            # Buscar contenedores de operadores ya creados
            for contenedor_completo in self.ids.grid_mano_obra.children:
                contenedor_operador = contenedor_completo.children[0]
                # Extraer nombre del operador
                op_nombre = "N/A"
                for child in contenedor_operador.children:
                    if isinstance(child, BoxLayout):
                        for sub in child.children:
                            if hasattr(sub, 'text') and "Operador:" in sub.text:
                                op_nombre = sub.text.replace("[b]Operador:[/b] ", "").replace("Operador: ", "").strip()
                                break

                # Si hay observaciones para este operador
                if op_nombre in obs_por_operador:
                    texto_obs = "\n".join(obs_por_operador[op_nombre])
                    if not hasattr(contenedor_operador, '_observacion_widget'):
                        self.agregar_bloque_observacion_a_operador(contenedor_operador, contenedor_completo)
                        Clock.schedule_once(
                            lambda dt, c=contenedor_operador, t=texto_obs: setattr(c._observacion_input, 'text', t),
                            0.1
                        )
                    else:
                        contenedor_operador._observacion_input.text = texto_obs

        except Exception as e:
            print(f"❌ Error al cargar observaciones: {e}")
            import traceback
            traceback.print_exc()

    # Reutilizar métodos ya existentes en FichaTorno:
    # - agregar_repuesto_existente_a_operador
    # - agregar_trabajo_existente_cargado
    # - calcular_todos_los_totales
    # - _actualizar_grid_altura
    # - guardar_nueva_ficha (funciona en modo modificación gracias a `es_modificacion`)

    def guardar_nueva_ficha(self):
        """Reutiliza el método de FichaTorno, que ya soporta modo modificación"""
        super().guardar_nueva_ficha()


class OperadoresPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Seleccionar Operador"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- BARRA DE BÚSQUEDA ---
        self.buscar_input = TextInput(hint_text='Buscar por nombre', size_hint_y=None, height=40)
        self.buscar_input.bind(text=self.filtrar_operadores)
        layout.add_widget(self.buscar_input)

        # --- ENCABEZADOS ---
        header = BoxLayout(size_hint_y=None, height=40)
        header.add_widget(Label(text="Nombre", size_hint_x=0.5, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="%", size_hint_x=0.25, bold=True, color=(1,1,1,1)))
        header.add_widget(Label(text="Tasa", size_hint_x=0.25, bold=True, color=(1,1,1,1)))
        layout.add_widget(header)

        # --- SCROLLVIEW + GRID ---
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        # --- BOTÓN CANCELAR ---
        btn_cancelar = Button(text="Cancelar", size_hint_y=None, height=50)
        btn_cancelar.bind(on_release=self.dismiss)
        layout.add_widget(btn_cancelar)

        self.content = layout
        self.cargar_operadores()

    def cargar_operadores(self):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['Inrema']
            collection = db['operadores']  # ✅ CORRECTO: colección 'operadores'
            self.todos_operadores = list(collection.find({}))
            client.close()
            self.filtrar_operadores()  # Llena el grid
            print(f"✅ Cargados {len(self.todos_operadores)} operadores")
        except Exception as e:
            print(f"❌ Error al cargar operadores: {e}")
            self.todos_operadores = []
            self.grid.add_widget(Label(text="Error al cargar operadores", color=(1,0,0,1)))

    def filtrar_operadores(self, *args):
        text = self.buscar_input.text.lower().strip() if hasattr(self, 'buscar_input') else ''
        self.grid.clear_widgets()

        for operador in self.todos_operadores:
            nombre = operador.get('nombre', '').lower()
            if text and text not in nombre:
                continue

            # --- Crear fila ---
            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            # Datos
            lbl_nombre = Label(text=operador.get('nombre', 'N/A'), size_hint_x=0.5)
            lbl_porcentaje = Label(text=str(operador.get('porcentaje', 0)) + ' %', size_hint_x=0.25)
            lbl_tasa = Label(text=f"{operador.get('tasa', 0.0):.2f}", size_hint_x=0.25)

            # Botón de selección
            btn = Button(text="Usar", size_hint_x=0.2)

            # --- ✅ FONDO AMARILLO si porcentaje < 10% ---
            if operador.get('porcentaje', 0) < 10:
                with row.canvas.before:
                    Color(1, 1, 0, 0.3)  # Fondo amarillo
                    self.rect = Rectangle(size=row.size, pos=row.pos)
                    row.bind(size=lambda r, val: setattr(self.rect, 'size', val),
                             pos=lambda r, val: setattr(self.rect, 'pos', val))

            # Añadir widgets
            row.add_widget(lbl_nombre)
            row.add_widget(lbl_porcentaje)
            row.add_widget(lbl_tasa)
            row.add_widget(btn)

            # Evento del botón
            btn.bind(on_release=lambda btn, op=operador: self.on_seleccionar(op))

            self.grid.add_widget(row)

    def on_seleccionar(self, operador):
        if self.callback:
            self.callback(operador)
        self.dismiss()
  
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):  
    touch_deselect_last = BooleanProperty(True)  
  

class AdminApp(App):  
    def build(self):  
        return AdminWindow()  
  
def limpiar_etiquetas_kivy(texto):
    """Elimina etiquetas de formato de Kivy como [b], [/b], [i], etc."""
    return re.sub(r'\[/?[bius]\]', '', texto)
  
if __name__ == "__main__":  
    AdminApp().run()

