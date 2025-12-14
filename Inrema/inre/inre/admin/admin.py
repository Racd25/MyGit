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
from sqlqueries import QueriesSQLite  
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
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
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from kivy.uix.spinner import Spinner
from pymongo import MongoClient
from kivy.uix.boxlayout import BoxLayout as BoxLayoutBase

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
  
  
class SelectableHistoriaLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)  # ✅ Necesario

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_fecha'].text = data.get('fecha', 'N/A')
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectableHistoriaLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False
    
class SelectableUsuarioLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)

        # ✅ Verifica si 'tipo_registro' existe
        tipo_registro = data.get('tipo_registro', 'desconocido')

        if tipo_registro == 'usuario':
            self.ids['_nombre'].text = data.get('nombre', 'N/A').title()
            self.ids['_username'].text = data.get('username', 'N/A')
            self.ids['_tipo'].text = data.get('tipo', 'N/A')
            self.ids['_ci2'].text = '' # Mostrar CI2 en _username
            self.ids['_cmvb'].text = ''
            self.ids['_mpps'].text = ''
        elif tipo_registro == 'veterinario':
            self.ids['_nombre'].text = data['nombre'].title()
            self.ids['_ci2'].text = data['ci']  # Mostrar CI2 en _username
            self.ids['_tipo'].text = 'Veterinario'
            self.ids['_username'].text = ''
            self.ids['_cmvb'].text = data['cmvb'] 
            self.ids['_mpps'].text = data['mpps'] 
        else:
            # Caso de emergencia
            self.ids['_nombre'].text = 'Error'
            self.ids['_username'].text = 'Datos inválidos'
            self.ids['_tipo'].text = 'N/A'

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


class SelectablePacienteLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_nombre_propietario'].text = str(data.get('nombre_propietario', 'N/A'))
        self.ids['_ci'].text = str(data.get('ci', 'N/A'))
        self.ids['_nombre_mascota'].text = str(data.get('nombre_mascota', 'N/A'))
        self.ids['_telefono'].text = str(data.get('telefono', 'N/A'))
        return super(SelectablePacienteLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectablePacienteLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False

class DetallePacientePopup(Popup):
    def __init__(self, paciente_data, actualizar_callback=None, **kwargs):
        super(DetallePacientePopup, self).__init__(**kwargs)
        self.paciente_data = paciente_data
        self.actualizar_callback = actualizar_callback
        self.modo_edicion = False
        self.poblar_datos()

    def poblar_datos(self):
        # Rellenar todos los campos con los datos del paciente
        self.ids.detalle_propietario.text = str(self.paciente_data.get('nombre_propietario', ''))
        self.ids.detalle_ci.text = str(self.paciente_data.get('ci', ''))
        self.ids.detalle_telefono.text = str(self.paciente_data.get('telefono', ''))
        self.ids.detalle_direccion.text = str(self.paciente_data.get('direccion', ''))
        self.ids.detalle_motivo.text = str(self.paciente_data.get('motivo_consulta', ''))
        self.ids.detalle_nombre_mascota.text = str(self.paciente_data.get('nombre_mascota', ''))
        self.ids.detalle_especie.text = str(self.paciente_data.get('especie', ''))
        self.ids.detalle_raza.text = str(self.paciente_data.get('raza', ''))
        self.ids.detalle_sexo.text = str(self.paciente_data.get('sexo', ''))
        self.ids.detalle_edad.text = str(self.paciente_data.get('edad', ''))
        self.ids.detalle_pelaje.text = str(self.paciente_data.get('pelaje', ''))
        self.ids.detalle_cc.text = str(self.paciente_data.get('cc', ''))
        self.ids.detalle_enfermedad.text = str(self.paciente_data.get('enfermedad', ''))
        self.ids.detalle_tratamiento.text = str(self.paciente_data.get('tratamiento', ''))
       

    def toggle_edicion(self):
        self.modo_edicion = not self.modo_edicion
        
        # Cambiar entre Label y TextInput para todos los campos
        campos = [
            'detalle_propietario', 'detalle_ci', 'detalle_telefono', 'detalle_direccion',
            'detalle_motivo', 'detalle_nombre_mascota', 'detalle_especie', 'detalle_raza',
            'detalle_sexo', 'detalle_edad', 'detalle_pelaje', 'detalle_cc',
            'detalle_enfermedad', 'detalle_tratamiento'
        ]
        
        for campo in campos:
            widget = self.ids[campo]
            if self.modo_edicion:
                # Cambiar a modo edición
                widget.readonly = False
                widget.background_color = (1, 1, 1, 1)  # Fondo blanco
            else:
                # Cambiar a modo solo lectura
                widget.readonly = True
                widget.background_color = (0.9, 0.9, 0.9, 1)  # Fondo gris claro
        
        # Cambiar texto del botón
        if self.modo_edicion:
            self.ids.btn_editar.text = 'Cancelar'
            self.ids.btn_guardar.opacity = 1
            self.ids.btn_guardar.disabled = False
        else:
            self.ids.btn_editar.text = 'Editar'
            self.ids.btn_guardar.opacity = 0
            self.ids.btn_guardar.disabled = True
            # Restaurar datos originales si se cancela
            self.poblar_datos()

    def guardar_cambios(self):
        # Recopilar datos editados
        datos_editados = {
            'nombre_propietario': self.ids.detalle_propietario.text,
            'ci': self.ids.detalle_ci.text,
            'telefono': self.ids.detalle_telefono.text,
            'direccion': self.ids.detalle_direccion.text,
            'motivo_consulta': self.ids.detalle_motivo.text,
            'nombre_mascota': self.ids.detalle_nombre_mascota.text,
            'especie': self.ids.detalle_especie.text,
            'raza': self.ids.detalle_raza.text,
            'sexo': self.ids.detalle_sexo.text,
            'edad': self.ids.detalle_edad.text,
            'pelaje': self.ids.detalle_pelaje.text,
            'cc': self.ids.detalle_cc.text,
            'enfermedad': self.ids.detalle_enfermedad.text,
            'tratamiento': self.ids.detalle_tratamiento.text,
        }
        
        # Validar campos obligatorios
        if not datos_editados['nombre_propietario'].strip():
            self.ids.mensaje_estado.text = "Error: El nombre del propietario es obligatorio"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)  # Rojo
            return
        
        if not datos_editados['ci'].strip():
            self.ids.mensaje_estado.text = "Error: La C.I. es obligatoria"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)  # Rojo
            return
        
        # Actualizar en la base de datos
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        query = """
        UPDATE consultas SET 
            nombre_propietario = ?, ci = ?, telefono = ?, direccion = ?,
            motivo_consulta = ?, nombre_mascota = ?, especie = ?, raza = ?,
            sexo = ?, edad = ?, pelaje = ?, cc = ?, enfermedad = ?, tratamiento = ?
        WHERE id = ?
        """
        
        parametros = (
            datos_editados['nombre_propietario'],
            datos_editados['ci'],
            datos_editados['telefono'],
            datos_editados['direccion'],
            datos_editados['motivo_consulta'],
            datos_editados['nombre_mascota'],
            datos_editados['especie'],
            datos_editados['raza'],
            datos_editados['sexo'],
            datos_editados['edad'],
            datos_editados['pelaje'],
            datos_editados['cc'],
            datos_editados['enfermedad'],
            datos_editados['tratamiento'],
            self.paciente_data['id']
        )
        
        try:
            QueriesSQLite.execute_query(connection, query, parametros)
            self.ids.mensaje_estado.text = "Datos actualizados correctamente"
            self.ids.mensaje_estado.color = (0, 1, 0, 1)  # Verde
            
            # Actualizar datos locales
            self.paciente_data.update(datos_editados)
            
            # Salir del modo edición
            self.toggle_edicion()
            
            # Actualizar la lista en VistaPacientes si se proporcionó callback
            if self.actualizar_callback:
                self.actualizar_callback()
                
        except Exception as e:
            self.ids.mensaje_estado.text = f"Error al actualizar: {str(e)}"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)  # Rojo

    def eliminar_paciente(self):
        popup = RecipesPopup(self.paciente_data)
        popup.open()
        
        
    def mostrar_examenes_clinicos(self):
        popup = ExamenesClinicosPopup(self.paciente_data)
        popup.open()
        
    def mostrar_historias_medicas(self):
        popup = HistoriasMedicasPopup(self.paciente_data)
        popup.open()
        
        
class RecipesPopup(Popup):
    def __init__(self, paciente_data, **kwargs):
        super(RecipesPopup, self).__init__(**kwargs)
        self.paciente_data = paciente_data
        self.title = f"Recetas - {paciente_data.get('nombre_mascota', 'Paciente')}"
        self.size_hint = (0.8, 0.9)
        self.auto_dismiss = False
        self.cargar_recetas()

    def cargar_recetas(self):
        """Carga las recetas desde la base de datos"""
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        SELECT ID, CI, Nombre, CMVB, MPPS, Paciente, rp, ind, fecha
        FROM recipes
        WHERE id_consulta = ?
        ORDER BY fecha DESC
        """
        recetas = QueriesSQLite.execute_read_query(connection, query, (self.paciente_data['id'],))

        # ✅ Asegúrate de que recetas no sea None
        if recetas is None:
            recetas = []

        data = []
        for idx, receta in enumerate(recetas):
            data.append({
                'id': receta[0],
                'ci': receta[1],
                'nombre': receta[2],
                'cmvb': receta[3],
                'mpps': receta[4],
                'paciente': receta[5],
                'rp': receta[6],
                'ind': receta[7],
                'fecha': receta[8] if receta[8] else 'N/A',
                'seleccionado': False
            })

        self.ids.rv_examenes.data = data
        connection.close()
    def ver_detalle_recipe(self):
        """Abre el popup de detalle para ver y editar la receta seleccionada"""
        rv = self.ids.rv_examenes
        indice = rv.dato_seleccionado() if hasattr(rv, 'dato_seleccionado') else -1
        if indice < 0:
            # Mostrar mensaje: "Seleccione una receta"
            print("Debe seleccionar una receta")
            return

        receta = rv.data[indice]
        popup = DetalleRecetaPopup(
            receta_data=receta,
            callback_guardado=self.cargar_recetas  # Para refrescar la lista tras guardar
        )
        popup.open()
    def eliminar_recipe(self):
        """Elimina la receta seleccionada"""
        rv = self.ids.rv_examenes
        indice = rv.dato_seleccionado() if hasattr(rv, 'dato_seleccionado') else -1
        if indice < 0:
            # Mostrar mensaje: "Seleccione una receta"
            return

        receta = rv.data[indice]
        receta_id = receta['id']

        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        try:
            QueriesSQLite.execute_query(connection, "DELETE FROM recipes WHERE ID = ?", (receta_id,))
            del rv.data[indice]
            rv.refresh_from_data()
            # Opcional: mostrar mensaje
        except Exception as e:
            print(f"Error al eliminar receta: {e}")
        finally:
            if connection:
                connection.close()

    def nuevo_examen(self):
        popup = NuevaRecetaPopup(
            paciente_data=self.paciente_data,
            callback_guardado=self.cargar_recetas
        )
        popup.open()

class SelectableRecipeLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    
    
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)

        # Formatear la fecha si está presente
        fecha_raw = data.get('fecha', 'N/A')
        try:
            fecha_obj = datetime.strptime(fecha_raw, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
        except:
            fecha_formateada = fecha_raw  # Si falla, mostrar la original

        self.ids['_fecha'].text = fecha_formateada
        self.ids['_Doctor'].text = f"{data.get('nombre', 'N/A')}"
        self.ids['_Rp'].text = str(data.get('rp', 'N/A'))
        self.ids['_Ind'].text = str(data.get('ind', 'N/A'))

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


class NuevaRecetaPopup(Popup):
    def __init__(self, paciente_data, callback_guardado=None, **kwargs):
        super().__init__(**kwargs)
        self.paciente_data = paciente_data
        self.callback_guardado = callback_guardado
        self.title = "Nueva Receta"
        self.size_hint = (0.8, 0.9)
        self.auto_dismiss = False

        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # --- SELECCIÓN DE VETERINARIO ---
        layout.add_widget(Label(
            text="1. Seleccione el Veterinario:",
            size_hint_y=None,
            height=30,
            bold=True,
            color=(1, 1, 1, 1)
        ))

        self.dropdown = DropDown()

        # Cargar veterinarios desde la base de datos
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = "SELECT CI2, Nombre, CMVB, MPPS FROM veterinarios ORDER BY Nombre"
        veterinarios = QueriesSQLite.execute_read_query(connection, query)
        connection.close()

        # Botón principal del dropdown
        self.dropdown_button = Button(
            text="Elegir Veterinario",
            size_hint_y=None,
            height=45,
            background_color=(0.3, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.dropdown_button)

        if not veterinarios:
            layout.add_widget(Label(
                text=" No hay veterinarios registrados.",
                color=(1, 0, 0, 1),
                size_hint_y=None,
                height=30
            ))
        else:
            for vet in veterinarios:
                btn = Button(
                    text=f"{vet[1]} (CMVB: {vet[2]})",
                    size_hint_y=None,
                    height=40,
                    background_color=(0.9, 0.95, 1, 1),
                    color=(1, 1, 1, 1)
                )
                btn.bind(on_release=lambda btn, data=vet: self.seleccionar_veterinario(data))
                self.dropdown.add_widget(btn)

            # Asociar el dropdown al botón
            self.dropdown_button.bind(on_release=self.dropdown.open)

        # --- DATOS DEL VETERINARIO SELECCIONADO ---
        self.lbl_vet_nombre = Label(text="", size_hint_y=None, height=25, bold=True)
        self.lbl_vet_datos = Label(text="", size_hint_y=None, height=25)

        # Contenedor para datos del veterinario (inicialmente oculto)
        self.layout_datos_vet = BoxLayout(orientation='vertical', size_hint_y=None, height=60, spacing=2)
        self.layout_datos_vet.add_widget(self.lbl_vet_nombre)
        self.layout_datos_vet.add_widget(self.lbl_vet_datos)
        self.layout_datos_vet.opacity = 0  # Oculto al inicio
        self.layout_datos_vet.disabled = True

        layout.add_widget(self.layout_datos_vet)

        # --- DATOS DEL PACIENTE ---
        layout.add_widget(Label(
            text="2. Paciente:",
            size_hint_y=None,
            height=30,
            bold=True
        ))
        layout.add_widget(Label(
            text=f"{paciente_data.get('nombre_mascota', 'N/A')}",
            size_hint_y=None,
            height=25,
            color=(1, 1, 1, 1)
        ))

        # --- CAMPOS DE LA RECETA ---
        layout.add_widget(Label(
            text="3. Tratamiento (Rp):",
            size_hint_y=None,
            height=30,
            bold=True
        ))
        self.rp = TextInput(multiline=True, hint_text="Escriba el tratamiento...")
        layout.add_widget(self.rp)

        layout.add_widget(Label(
            text="4. Indicaciones (Ind):",
            size_hint_y=None,
            height=30,
            bold=True
        ))
        self.ind = TextInput(multiline=True, hint_text="Escriba las indicaciones...")
        layout.add_widget(self.ind)

        # --- BOTONES ---
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_cancelar = Button(
            text="Cancelar",
            background_color=(0.6, 0.6, 0.6, 1)
        )
        btn_cancelar.bind(on_release=self.dismiss)

        btn_guardar = Button(
            text="Guardar Receta",
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_guardar.bind(on_release=self.guardar_receta)

        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_guardar)
        layout.add_widget(btn_layout)

        self.content = layout

        # Estado interno
        self.veterinario_seleccionado = None

    def seleccionar_veterinario(self, data):
        """Se llama al seleccionar un veterinario del dropdown"""
        self.veterinario_seleccionado = {
            'ci': data[0],
            'nombre': data[1],
            'cmvb': data[2],
            'mpps': data[3]
        }
        self.dropdown_button.text = f"{data[1]} (CMVB: {data[2]})"
        self.dropdown.dismiss()

        # Mostrar datos del veterinario
        self.lbl_vet_nombre.text = f"Dr(a). {data[1]}"
        self.lbl_vet_datos.text = f"CMVB: {data[2]} | MPPS: {data[3]}"
        self.layout_datos_vet.opacity = 1
        self.layout_datos_vet.disabled = False

    def guardar_receta(self, *args):
        """Guarda la receta en la base de datos"""
        if not self.veterinario_seleccionado:
            # Puedes mostrar un mensaje en el popup
            print("Debe seleccionar un veterinario")
            return

        if not self.rp.text.strip():
            print("El campo Rp es obligatorio")
            return

        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        INSERT INTO recipes (id_consulta, CI, Nombre, CMVB, MPPS, Paciente, rp, ind, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'))
        """
        try:
            QueriesSQLite.execute_query(connection, query, (
                self.paciente_data['id'],
                self.veterinario_seleccionado['ci'],
                self.veterinario_seleccionado['nombre'],
                self.veterinario_seleccionado['cmvb'],
                self.veterinario_seleccionado['mpps'],
                self.paciente_data['nombre_mascota'],
                self.rp.text.strip(),
                self.ind.text.strip()
            ))
            if self.callback_guardado:
                self.callback_guardado()
            self.dismiss()
        except Exception as e:
            print(f"Error al guardar receta: {e}")
        finally:
            if connection:
                connection.close()


class DetalleRecetaPopup(Popup):
    def __init__(self, receta_data, callback_guardado=None, **kwargs):
        super().__init__(**kwargs)
        self.receta_data = receta_data
        self.callback_guardado = callback_guardado
        self.modo_edicion = False  # Estado inicial: solo lectura
        self.title = f"Receta - {receta_data['fecha']}"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Campos editables
        self.lbl_veterinario = Label(text=f"Veterinario: {receta_data['nombre']}", bold=True)
        self.lbl_cmvb = Label(text=f"CMVB: {receta_data['cmvb']} | MPPS: {receta_data['mpps']}")
        self.lbl_paciente = Label(text=f"Paciente: {receta_data['paciente']}", bold=True)

        self.rp = TextInput(text=receta_data['rp'], multiline=True)
        self.ind = TextInput(text=receta_data['ind'], multiline=True)

        # Botones
        self.btn_editar = Button(
            text="Editar Receta",
            background_color=(0.3, 0.5, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        self.btn_editar.bind(on_release=self.toggle_edicion)

        self.btn_guardar = Button(
            text="Guardar Cambios",
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=None,
            height=50
        )
        self.btn_guardar.bind(on_release=self.guardar_cambios)
        self.btn_guardar.opacity = 0
        self.btn_guardar.disabled = True

        self.btn_imprimir = Button(
            text="Imprimir Receta",
            background_color=(0.8, 0.5, 0.2, 1),
            size_hint_y=None,
            height=50
        )
        self.btn_imprimir.bind(on_release=self.imprimir_receta)

        # ✅ Botón Cerrar añadido
        self.btn_cerrar = Button(
            text="Cerrar",
            background_color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=50
        )
        self.btn_cerrar.bind(on_release=self.dismiss)  # Cierra el popup

        # Añadir widgets al layout
        self.layout.add_widget(self.lbl_veterinario)
        self.layout.add_widget(self.lbl_cmvb)
        self.layout.add_widget(self.lbl_paciente)
        self.layout.add_widget(Label(text="Rp (Tratamiento):", bold=True))
        self.layout.add_widget(self.rp)
        self.layout.add_widget(Label(text="Ind (Indicaciones):", bold=True))
        self.layout.add_widget(self.ind)
        self.layout.add_widget(self.btn_editar)
        self.layout.add_widget(self.btn_guardar)
        self.layout.add_widget(self.btn_imprimir)
        self.layout.add_widget(self.btn_cerrar)  # ✅ Añadido al final

        self.content = self.layout

    def toggle_edicion(self, *args):
        """Alterna entre modo edición y solo lectura"""
        self.modo_edicion = not self.modo_edicion

        if self.modo_edicion:
            self.btn_editar.text = "Cancelar"
            self.btn_guardar.opacity = 1
            self.btn_guardar.disabled = False
            self.rp.readonly = False
            self.ind.readonly = False
            self.rp.background_color = (1, 1, 1, 1)
            self.ind.background_color = (1, 1, 1, 1)
        else:
            self.btn_editar.text = "Editar Receta"
            self.btn_guardar.opacity = 0
            self.btn_guardar.disabled = True
            self.rp.readonly = True
            self.ind.readonly = True
            self.rp.background_color = (0.95, 0.95, 0.95, 1)
            self.ind.background_color = (0.95, 0.95, 0.95, 1)

    def guardar_cambios(self, *args):
        """Guarda los cambios en la base de datos"""
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        UPDATE recipes
        SET rp = ?, ind = ?
        WHERE ID = ?
        """
        try:
            QueriesSQLite.execute_query(connection, query, (
                self.rp.text.strip(),
                self.ind.text.strip(),
                self.receta_data['id']
            ))
            # Actualizar datos locales
            self.receta_data['rp'] = self.rp.text.strip()
            self.receta_data['ind'] = self.ind.text.strip()
            if self.callback_guardado:
                self.callback_guardado()
            self.toggle_edicion()
        except Exception as e:
            print(f"Error al guardar cambios: {e}")
        finally:
            if connection:
                connection.close()

    def imprimir_receta(self, *args):
        """Genera un PDF de la receta"""
        # Aquí puedes llamar a la función que genera el PDF
        datos = {
            'nombre': self.receta_data['nombre'],
            'ci': self.receta_data['ci'],
            'cmvb': self.receta_data['cmvb'],
            'mpps': self.receta_data['mpps'],
            'paciente': self.receta_data['paciente'],
            'rp': self.receta_data['rp'],
            'ind': self.receta_data['ind'],
            'fecha':self.receta_data['fecha']
        }
        print(datos.get('ci', 'N/A'))
        generar_pdf(datos)
        self.dismiss()
        
        
def generar_pdf(datos):
    """
    Genera un PDF con los datos de la historia clínica.
    
    :param datos: Diccionario con los datos del paciente y el médico.
    """
    # Crear el archivo PDF
    escritorio = Path.home() / "Desktop"  # Ruta al escritorio (funciona en todos los sistemas)
    carpeta_pdf = escritorio / "MarysPet_Recetas"

    # Crear la carpeta si no existe
    carpeta_pdf.mkdir(exist_ok=True)  # 'exist_ok=True' evita errores si ya existe

    
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
    fecha = datos.get('fecha','N/A')
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_formateada = fecha_obj.strftime("%d-%m-%Y")
    except ValueError:
        fecha_formateada = fecha  # Si el formato es incorrecto, usa el valor crudo

    # Nombre del archivo
    nombre_archivo = f"recipe_{paciente}_{fecha_formateada}.pdf"
    ruta_completa = carpeta_pdf / nombre_archivo

    # --- 3. Crear el PDF ---
    c = canvas.Canvas(str(ruta_completa), pagesize=landscape(letter))
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
    c.drawString(margen_x + 1.5 * inch, pie_y - 0.4 *inch, " 04143573522 / 04126920264 ")
    c.drawString(margen_x + 1.4*inch, pie_y - 0.6 * inch, " maryspetbarinas@gmail.com")
    c.drawString(margen_x+0.4*inch, pie_y - 0.8 * inch, "Av. El progreso, Jardines Alto Barinas. Conj. Apamates, Locales 8-A1 y B-2.")


    # Derecha
    c.drawString(centro + margen_x + 1.5 * inch,  pie_y - 0.4 *inch, "04143573522 / 04126920264 ")
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





class SelectableExamenLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_fecha'].text = str(data.get('fecha_examen', 'N/A'))
        self.ids['_peso'].text = str(data.get('peso', 'N/A'))
        self.ids['_anamnesis'].text = str(data.get('anamnesis', 'N/A'))
        self.ids['_diagnostico'].text = str(data.get('diag_definitivo', 'N/A'))[:50] + "..." if len(str(data.get('diag_definitivo', ''))) > 50 else str(data.get('diag_definitivo', 'N/A'))
        return super(SelectableExamenLabel, self).refresh_view_attrs(rv, index, data)
    def on_touch_down(self, touch):
        if super(SelectableExamenLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado'] = True
        else:
            rv.data[index]['seleccionado'] = False
  
class ExamenesClinicosPopup(Popup):
    def __init__(self, paciente_data, **kwargs):
        super(ExamenesClinicosPopup, self).__init__(**kwargs)
        self.paciente_data = paciente_data
        self.cargar_examenes()
        
        
    def cargar_examenes(self):
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        SELECT id, desparasitaciones, vacuna, alimentacion, anamnesis,
            peso, temperatura, fc, fr, p_femoral, yugular, tpg, ps, pd, pam,
            mucosas, ganglios, palp_abdominal, patron_lesion, genitales,
            procedimiento_diagnos, pruebas_comple, diag_diferencial, diag_definitivo,
            tratamiento_apli, tratamiento_indi, proxi_consulta, fecha_examen, lab,
                        hb,
                        eosi,
                        urea,
                        alt,
                        otras_20,
                    
                        hto,
                        plaq,
                        creat,
                        ast,
                        otras_30,
                  
                        leuc,
                        vcm,
                        bun,
                        fa,
                        otras_40,
                   
                        neut,
                        hcm,
                        pt,
                        bt,
                        otras_50,
                      
                        lint,
                        chcm,
                        alb,
                        bi,
                        otras_60,
                  
                        mon,
                        descar,
                        glo,
                        bd,
                        otras_70
        FROM examen_clinico 
        WHERE id_consulta = ?
        ORDER BY fecha_examen DESC
        """
        
        examenes = QueriesSQLite.execute_read_query(connection, query, (self.paciente_data['id'],))
        
        self.ids.rv_examenes.data = []  # Limpiar datos anteriores
        
        if examenes:
            examenes_data = []
            for examen in examenes:
                examen_dict = {
                    'id': examen[0],
                    'desparasitaciones': examen[1],
                    'vacuna': examen[2],
                    'alimentacion': examen[3],
                    'anamnesis': examen[4],
                    'peso': examen[5],
                    'temperatura': examen[6],
                    'fc': examen[7],
                    'fr': examen[8],
                    'p_femoral': examen[9],
                    'yugular': examen[10],
                    'tpg': examen[11],
                    'ps': examen[12],
                    'pd': examen[13],
                    'pam': examen[14],
                    'mucosas': examen[15],
                    'ganglios': examen[16],
                    'palp_abdominal': examen[17],
                    'patron_lesion': examen[18],
                    'genitales': examen[19],
                    'procedimiento_diagnos': examen[20],
                    'pruebas_comple': examen[21],
                    'diag_diferencial': examen[22],
                    'diag_definitivo': examen[23],
                    'tratamiento_apli': examen[24],
                    'tratamiento_indi': examen[25],
                    'proxi_consulta': examen[26],
                    'fecha_examen': examen[27],
                    'lab': examen[28],
                    'hb' : examen[29],
                    'eosi' : examen[30],
                    'urea' : examen[31],
                    'alt' : examen[32],
                    'otras_20': examen[33],

                    'hto' : examen[34],
                    'plaq': examen[35],
                    'creat' : examen[36],
                    'ast' : examen[37],
                    'otras_30' : examen[38],
          
                    'leuc' : examen[39],
                    'vcm' : examen[40],
                    'bun' : examen[41],
                    'fa' : examen[42],
                    'otras_40' : examen[43],
               
                    'neut' : examen[44],
                    'hcm' : examen[45],
                    'pt' : examen[46],
                    'bt' : examen[47],
                    'otras_50' : examen[48],
              
                    'lint' : examen[49],
                    'chcm' : examen[50],
                    'alb' : examen[51],
                    'bi' : examen[52],
                    'otras_60' : examen[53],
             
                    'mon' : examen[54],
                    'descar' : examen[55],
                    'glo' : examen[56],
                    'bd' : examen[57],
                    'otras_70' : examen[58],
                    'seleccionado': False
                }
                examenes_data.append(examen_dict)
            
            self.ids.rv_examenes.agregar_datos(examenes_data)
    def nuevo_examen(self):
        popup = RecepcionPartesPopup()
        popup.open()
    def ver_detalle_examen(self):
        indice = self.ids.rv_examenes.dato_seleccionado()
        if indice >= 0:
            examen_seleccionado = self.ids.rv_examenes.data[indice]
            popup = DetalleExamenPopup(examen_seleccionado)
            popup.open()
        else:
            print("No hay examen seleccionado")  
  
# ✅ NUEVO MÉTODO: Eliminar examen con confirmación
    def eliminar_examen(self):
        """Elimina el examen clínico seleccionado después de confirmación"""
        # Verificar que hay un examen seleccionado
        indice = self.ids.rv_examenes.dato_seleccionado()
        
        if indice < 0:
            self.mostrar_mensaje("Error: Debe seleccionar un examen para eliminar", (1, 0, 0, 1))
            return
        
        # Obtener datos del examen seleccionado
        examen_seleccionado = self.ids.rv_examenes.data[indice]
        
        # Crear popup de confirmación
        popup_confirmacion = ConfirmacionEliminarPopup(
            examen_data=examen_seleccionado,
            callback_eliminar=self.confirmar_eliminacion
        )
        popup_confirmacion.open()
    # ✅ MÉTODO: Confirmar y ejecutar eliminación
    def confirmar_eliminacion(self, examen_id):
        """Ejecuta la eliminación del examen en la base de datos"""
        try:
            resultado = self.eliminar_examen_bd(examen_id)
            
            if resultado:
                # Mostrar mensaje de éxito
                self.mostrar_mensaje("Examen eliminado correctamente", (0, 1, 0, 1))
                
                # Recargar la lista de exámenes
                self.cargar_examenes()
                
                print(f"✅ Examen con ID {examen_id} eliminado correctamente")
            else:
                self.mostrar_mensaje("Error al eliminar el examen", (1, 0, 0, 1))
                
        except Exception as e:
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", (1, 0, 0, 1))
            print(f"💥 Error al eliminar examen: {e}")
    # ✅ MÉTODO: Eliminar de base de datos
    def eliminar_examen_bd(self, examen_id):
        """Elimina físicamente el examen de la base de datos"""
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        try:
            # Query para eliminar el examen
            query = "DELETE FROM examen_clinico WHERE id = ?"
            
            print(f"🗑️  Eliminando examen con ID: {examen_id}")
            
            # Ejecutar eliminación
            QueriesSQLite.execute_query(connection, query, (examen_id,))
            
            return True
            
        except Exception as e:
            print(f"💥 Error en base de datos al eliminar examen: {e}")
            return False
        finally:
            if connection:
                connection.close()
    # ✅ MÉTODO AUXILIAR: Mostrar mensajes
    def mostrar_mensaje(self, mensaje, color):
        """Muestra un mensaje en el popup (requiere Label mensaje_estado en .kv)"""
        if hasattr(self.ids, 'mensaje_estado'):
            self.ids.mensaje_estado.text = mensaje
            self.ids.mensaje_estado.color = color
        else:
            print(f"MENSAJE: {mensaje}")
  
class ConfirmacionEliminarPopup(Popup):
    """Popup para confirmar la eliminación de un examen"""
    
    def __init__(self, examen_data, callback_eliminar, **kwargs):
        super(ConfirmacionEliminarPopup, self).__init__(**kwargs)
        self.examen_data = examen_data
        self.callback_eliminar = callback_eliminar
        
        # Configurar popup
        self.title = " Confirmar Eliminación"
        self.size_hint = (0.6, 0.4)
        self.auto_dismiss = False
        
        # Crear contenido
        self.create_content()

    def create_content(self):
        """Crea el contenido del popup de confirmación"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Mensaje de advertencia
        warning_label = Label(
            text=f"¿Está seguro que desea eliminar este examen?\n\n"
                 f"Fecha: {self.examen_data.get('fecha_examen', 'N/A')}\n"
                 f" Esta acción NO se puede deshacer",
            text_size=(None, None),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(warning_label)
        
        # Botones de acción
        buttons_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        
        # Botón Cancelar
        btn_cancelar = Button(
            text=' Cancelar',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        btn_cancelar.bind(on_release=self.dismiss)
        buttons_layout.add_widget(btn_cancelar)
        
        # Botón Eliminar
        btn_eliminar = Button(
            text=' Eliminar',
            background_color=(0.9, 0.3, 0.3, 1)
        )
        btn_eliminar.bind(on_release=self.ejecutar_eliminacion)
        buttons_layout.add_widget(btn_eliminar)
        
        main_layout.add_widget(buttons_layout)
        self.content = main_layout

    def ejecutar_eliminacion(self, instance):
        """Ejecuta la eliminación y cierra el popup"""
        examen_id = self.examen_data['id']
        
        # Llamar al callback para eliminar
        self.callback_eliminar(examen_id)
        
        # Cerrar popup
        self.dismiss()
  
class NuevoExamenPopup(Popup):
    def __init__(self, paciente_data, actualizar_callback=None, **kwargs):
        super(NuevoExamenPopup, self).__init__(**kwargs)
        self.paciente_data = paciente_data
        self.actualizar_callback = actualizar_callback
        self.title = f"Nuevo Examen - {paciente_data.get('nombre_mascota', 'N/A')}"

    def guardar_examen(self):
        try:
            peso = self.ids.nuevo_peso.text.strip()
            temperatura = self.ids.nuevo_temperatura.text.strip()
            
            if not peso or not temperatura:
                self.ids.mensaje_estado.text = "Error: Peso y temperatura son obligatorios"
                self.ids.mensaje_estado.color = (1, 0, 0, 1)
                return
            
            peso_float = float(peso)
            temperatura_float = float(temperatura)
            
        except ValueError:
            self.ids.mensaje_estado.text = "Error: Peso y temperatura deben ser números válidos"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)
            return
        except AttributeError as e:
            self.ids.mensaje_estado.text = f"Error: Campo no encontrado - {str(e)}"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)
            return
        
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        try:
            datos_clinicos = (
                self.paciente_data['id'],
                self.ids.nuevo_desparasitaciones.text.strip(),
                self.ids.nuevo_vacuna.text.strip(),
                self.ids.nuevo_alimentacion.text.strip(),
                self.ids.nuevo_anamnesis.text.strip(),
                peso_float,
                temperatura_float,
                self.ids.nuevo_fc.text.strip(),
                self.ids.nuevo_fr.text.strip(),
                self.ids.nuevo_p_femoral.text.strip(),
                self.ids.nuevo_yugular.text.strip(),
                self.ids.nuevo_tpg.text.strip(),
                self.ids.nuevo_ps.text.strip(),
                self.ids.nuevo_pd.text.strip(),
                self.ids.nuevo_pam.text.strip(),
                self.ids.nuevo_mucosas.text.strip(),
                self.ids.nuevo_ganglios.text.strip(),
                self.ids.nuevo_palp_abdominal.text.strip(),
                self.ids.nuevo_patron_lesion.text.strip(),
                self.ids.nuevo_genitales.text.strip(),
                self.ids.nuevo_procedimiento_diagnos.text.strip(),
                self.ids.nuevo_pruebas_comple.text.strip(),
                self.ids.nuevo_diag_diferencial.text.strip(),
                self.ids.nuevo_diag_definitivo.text.strip(),
                self.ids.nuevo_tratamiento_apli.text.strip(),
                self.ids.nuevo_tratamiento_indi.text.strip(),
                self.ids.nuevo_proxi_consulta.text.strip(),
                datetime.now().strftime('%d-%m-%y'),  # ✅ fecha_examen (ahora incluida en query)
                self.ids.nuevo_examen_lab.text.strip(),
                self.ids.nuevo_examen_Hb.text.strip(),
                self.ids.nuevo_examen_eosi.text.strip(),
                self.ids.nuevo_examen_urea.text.strip(),
                self.ids.nuevo_examen_alt.text.strip(),
                self.ids.nuevo_otras_20.text.strip(),
                self.ids.nuevo_examen_hto.text.strip(),
                self.ids.nuevo_examen_plaq.text.strip(),
                self.ids.nuevo_examen_creat.text.strip(),
                self.ids.nuevo_examen_ast.text.strip(),
                self.ids.nuevo_otras_30.text.strip(),
                self.ids.nuevo_examen_leuc.text.strip(),
                self.ids.nuevo_examen_vcm.text.strip(),
                self.ids.nuevo_examen_bun.text.strip(),
                self.ids.nuevo_examen_fa.text.strip(),
                self.ids.nuevo_otras_40.text.strip(),
                self.ids.nuevo_examen_neut.text.strip(),
                self.ids.nuevo_examen_hcm.text.strip(),
                self.ids.nuevo_examen_pt.text.strip(),
                self.ids.nuevo_examen_bt.text.strip(),
                self.ids.nuevo_otras_50.text.strip(),
                self.ids.nuevo_examen_lint.text.strip(),
                self.ids.nuevo_examen_chcm.text.strip(),
                self.ids.nuevo_examen_alb.text.strip(),
                self.ids.nuevo_examen_bi.text.strip(),
                self.ids.nuevo_otras_60.text.strip(),
                self.ids.nuevo_examen_mon.text.strip(),
                self.ids.nuevo_examen_descar.text.strip(),
                self.ids.nuevo_examen_glo.text.strip(),
                self.ids.nuevo_examen_bd.text.strip(),
                self.ids.nuevo_otras_70.text.strip()
            )
            
            # ✅ CONSULTA CORREGIDA - Incluye fecha_examen
            query_clinico = """
                INSERT INTO examen_clinico (
                    id_consulta, desparasitaciones, vacuna, alimentacion, anamnesis,
                    peso, temperatura, fc, fr, p_femoral, yugular, tpg, ps, pd, pam,
                    mucosas, ganglios, palp_abdominal, patron_lesion, genitales,
                    procedimiento_diagnos, pruebas_comple, diag_diferencial, diag_definitivo,
                    tratamiento_apli, tratamiento_indi, proxi_consulta, fecha_examen,
                    lab, hb, eosi, urea, alt, otras_20,
                    hto, plaq, creat, ast, otras_30,
                    leuc, vcm, bun, fa, otras_40,
                    neut, hcm, pt, bt, otras_50,
                    lint, chcm, alb, bi, otras_60,
                    mon, descar, glo, bd, otras_70  
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # DEBUG: Verificar coincidencia
            print(f"🔍 Columnas en query: {query_clinico.count('?')}")
            print(f"🔍 Parámetros en tupla: {len(datos_clinicos)}")
            
            if query_clinico.count('?') != len(datos_clinicos):
                print("❌ ERROR: No coinciden los parámetros")
                return
            
            # Ejecutar inserción
            resultado = QueriesSQLite.execute_query(connection, query_clinico, datos_clinicos)
            
            self.ids.mensaje_estado.text = "Examen guardado correctamente"
            self.ids.mensaje_estado.color = (0, 1, 0, 1)
            
            if self.actualizar_callback:
                self.actualizar_callback()
                
            Clock.schedule_once(lambda dt: self.dismiss(), 1.5)
            
        except AttributeError as e:
            self.ids.mensaje_estado.text = f"Error: Campo no encontrado - {str(e)}"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)
            print(f"Error de ID de widget: {str(e)}")
            
        except Exception as e:
            self.ids.mensaje_estado.text = f"Error al guardar: {str(e)}"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)
            print(f"Error general: {str(e)}")
            
        finally:
            connection.close()
            
class DetalleExamenPopup(Popup):
    def __init__(self, examen_data, actualizar_callback=None, **kwargs):
        super(DetalleExamenPopup, self).__init__(**kwargs)
        self.examen_data = examen_data
        self.actualizar_callback = actualizar_callback  # ✅ Callback para actualizar lista
        self.modo_edicion = False  # ✅ Estado de edición
        self.title = f"Detalle Examen - {examen_data.get('fecha_examen', 'N/A')[:10]}"
        self.cargar_todos_los_datos()
        
    def cargar_todos_los_datos(self):
        """
        Carga datos de examen_clinico (directo del examen_data)
        y examen_laboratorio (de la base de datos) y los muestra en los TextInput.
        """
        # 1. Cargar datos del examen clínico (usando id: detalle_examen_*)
        self.cargar_datos_clinicos()
        # 2. Cargar datos del laboratorio (usando id: detalle_*)
    def cargar_todos_los_datos(self):
        """
        Carga datos de examen_clinico (directo del examen_data)
        y examen_laboratorio (de la base de datos) y los muestra en los TextInput.
        """
        # 1. Cargar datos del examen clínico (usando id: detalle_examen_*)
        self.cargar_datos_clinicos()

        # 2. Cargar datos del laboratorio (usando id: detalle_*)

    def cargar_datos_clinicos(self):
        """Llena los campos clínicos con prefijo 'detalle_examen_'"""
        campos_clinicos = {
            'desparasitaciones': 'detalle_examen_desparasitaciones',
            'vacuna': 'detalle_examen_vacuna',
            'alimentacion': 'detalle_examen_alimentacion',
            'anamnesis': 'detalle_examen_anamnesis',
            'peso': 'detalle_examen_peso',
            'temperatura': 'detalle_examen_temperatura',
            'fc': 'detalle_examen_fc',
            'fr': 'detalle_examen_fr',
            'p_femoral': 'detalle_examen_p_femoral',
            'yugular': 'detalle_examen_yugular',
            'tpg': 'detalle_examen_tpg',
            'ps': 'detalle_examen_ps',
            'pd': 'detalle_examen_pd',
            'pam': 'detalle_examen_pam',
            'mucosas': 'detalle_examen_mucosas',
            'ganglios': 'detalle_examen_ganglios',
            'palp_abdominal': 'detalle_examen_palp_abdominal',
            'patron_lesion': 'detalle_examen_patron_lesion',
            'genitales': 'detalle_examen_genitales',
            'procedimiento_diagnos': 'detalle_examen_procedimiento_diagnos',
            'pruebas_comple': 'detalle_examen_pruebas_comple',
            'diag_diferencial': 'detalle_examen_diag_diferencial',
            'diag_definitivo': 'detalle_examen_diag_definitivo',
            'tratamiento_apli': 'detalle_examen_tratamiento_apli',
            'tratamiento_indi': 'detalle_examen_tratamiento_indi',
            'proxi_consulta': 'detalle_examen_proxi_consulta',
            'fecha_examen': 'detalle_examen_fecha',
            # -- Fila 2
            'lab': 'detalle_lab',
             'hb': 'detalle_hb',
             'eosi': 'detalle_eosi',
             'urea': 'detalle_urea',
             'alt': 'detalle_alt',
             'otras_20': 'detalle_otras_20',
                 #   -- Fila 3
             'hto': 'detalle_hto',
             'plaq':  'detalle_plaq',
             'creat':  'detalle_creat',
             'ast': 'detalle_ast',
            'otras_30':  'detalle_otras_30',
                  #  -- Fila 4
             'leuc': 'detalle_leuc',
             'vcm': 'detalle_vcm',
             'bun': 'detalle_bun',
             'fa': 'detalle_fa',
             'otras_40': 'detalle_otras_40' ,
                   # -- Fila 5
             'neut': 'detalle_neut',
             'hcm': 'detalle_hcm',
             'pt':  'detalle_pt',
             'bt': 'detalle_pt',
             'otras_50': 'detalle_otras_50',
                    #-- Fila 6
             'lint': 'detalle_lint',
             'chcm': 'detalle_chcm',
             'alb': 'detalle_alb',
             'bi': 'detalle_bi',
             'otras_60':  'detalle_otras_60',
                    #--Fila 7
             'mon': 'detalle_mon',
             'descar': 'detalle_descar',
             'glo': 'detalle_glo',
             'bd': 'detalle_bd',
             'otras_70': 'detalle_otras_70'
        }

        for campo_db, widget_id in campos_clinicos.items():
            valor = self.examen_data.get(campo_db, '')
            if hasattr(self.ids, widget_id):
                self.ids[widget_id].text = str(valor) if valor is not None else ''

    def toggle_edicion(self):
            """Cambia entre modo visualización y modo edición"""
            self.modo_edicion = not self.modo_edicion
            
            # Lista de todos los campos editables
            campos_editables = [
                'detalle_examen_desparasitaciones', 'detalle_examen_vacuna', 
                'detalle_examen_alimentacion', 'detalle_examen_anamnesis',
                'detalle_examen_peso', 'detalle_examen_temperatura',
                'detalle_examen_fc', 'detalle_examen_fr', 'detalle_examen_p_femoral',
                'detalle_examen_yugular', 'detalle_examen_tpg', 'detalle_examen_ps',
                'detalle_examen_pd', 'detalle_examen_pam', 'detalle_examen_mucosas',
                'detalle_examen_ganglios', 'detalle_examen_palp_abdominal',
                'detalle_examen_patron_lesion', 'detalle_examen_genitales',
                'detalle_examen_procedimiento_diagnos', 'detalle_examen_pruebas_comple',
                'detalle_examen_diag_diferencial', 'detalle_examen_diag_definitivo',
                'detalle_examen_tratamiento_apli', 'detalle_examen_tratamiento_indi',
                'detalle_examen_proxi_consulta',
                # Campos de laboratorio
                'detalle_lab', 'detalle_hb', 'detalle_eosi', 'detalle_urea', 'detalle_alt',
                'detalle_otras_20', 'detalle_hto', 'detalle_plaq', 'detalle_creat',
                'detalle_ast', 'detalle_otras_30', 'detalle_leuc', 'detalle_vcm',
                'detalle_bun', 'detalle_fa', 'detalle_otras_40', 'detalle_neut',
                'detalle_hcm', 'detalle_pt', 'detalle_bt', 'detalle_otras_50',
                'detalle_lint', 'detalle_chcm', 'detalle_alb', 'detalle_bi',
                'detalle_otras_60', 'detalle_mon', 'detalle_descar', 'detalle_glo',
                'detalle_bd', 'detalle_otras_70'
            ]
            
            # Cambiar propiedades de todos los campos
            for campo_id in campos_editables:
                if hasattr(self.ids, campo_id):
                    widget = self.ids[campo_id]
                    if self.modo_edicion:
                        # Modo edición: habilitar
                        widget.readonly = False
                        widget.background_color = (1, 1, 1, 1)  # Fondo blanco
                        widget.foreground_color = (0, 0, 0, 1)  # Texto negro
                    else:
                        # Modo solo lectura: deshabilitar
                        widget.readonly = True
                        widget.background_color = (0.95, 0.95, 0.95, 1)  # Fondo gris claro
                        widget.foreground_color = (0.3, 0.3, 0.3, 1)  # Texto gris
            
            # Cambiar texto y visibilidad de botones
            if self.modo_edicion:
                # Entrar en modo edición
                if hasattr(self.ids, 'btn_editar'):
                    self.ids.btn_editar.text = 'Cancelar Edición'
                if hasattr(self.ids, 'btn_guardar'):
                    self.ids.btn_guardar.opacity = 1
                    self.ids.btn_guardar.disabled = False
                
                # Cambiar título
                self.title = f"EDITANDO Examen - {self.examen_data.get('fecha_examen', 'N/A')[:10]}"
                
            else:
                # Salir de modo edición
                if hasattr(self.ids, 'btn_editar'):
                    self.ids.btn_editar.text = 'Editar Examen'
                if hasattr(self.ids, 'btn_guardar'):
                    self.ids.btn_guardar.opacity = 0
                    self.ids.btn_guardar.disabled = True
                
                # Restaurar título
                self.title = f"Detalle Examen - {self.examen_data.get('fecha_examen', 'N/A')[:10]}"
                
                # Restaurar datos originales (cancelar cambios)
                self.cargar_todos_los_datos()
        # ✅ NUEVO MÉTODO: Guardar cambios
    def guardar_cambios(self):
        """Guarda los cambios realizados en el examen"""
        try:
            # Validar campos obligatorios
            peso = self.ids.detalle_examen_peso.text.strip()
            temperatura = self.ids.detalle_examen_temperatura.text.strip()
            
            if not peso or not temperatura:
                self.mostrar_mensaje("Error: Peso y temperatura son obligatorios", (1, 0, 0, 1))
                return
            
            # Validar que sean números válidos
            try:
                peso_float = float(peso)
                temperatura_float = float(temperatura)
            except ValueError:
                self.mostrar_mensaje("Error: Peso y temperatura deben ser números válidos", (1, 0, 0, 1))
                return
            
            # Recopilar todos los datos editados
            datos_actualizados = {
                # Campos clínicos
                'desparasitaciones': self.ids.detalle_examen_desparasitaciones.text.strip(),
                'vacuna': self.ids.detalle_examen_vacuna.text.strip(),
                'alimentacion': self.ids.detalle_examen_alimentacion.text.strip(),
                'anamnesis': self.ids.detalle_examen_anamnesis.text.strip(),
                'peso': peso_float,
                'temperatura': temperatura_float,
                'fc': self.ids.detalle_examen_fc.text.strip(),
                'fr': self.ids.detalle_examen_fr.text.strip(),
                'p_femoral': self.ids.detalle_examen_p_femoral.text.strip(),
                'yugular': self.ids.detalle_examen_yugular.text.strip(),
                'tpg': self.ids.detalle_examen_tpg.text.strip(),
                'ps': self.ids.detalle_examen_ps.text.strip(),
                'pd': self.ids.detalle_examen_pd.text.strip(),
                'pam': self.ids.detalle_examen_pam.text.strip(),
                'mucosas': self.ids.detalle_examen_mucosas.text.strip(),
                'ganglios': self.ids.detalle_examen_ganglios.text.strip(),
                'palp_abdominal': self.ids.detalle_examen_palp_abdominal.text.strip(),
                'patron_lesion': self.ids.detalle_examen_patron_lesion.text.strip(),
                'genitales': self.ids.detalle_examen_genitales.text.strip(),
                'procedimiento_diagnos': self.ids.detalle_examen_procedimiento_diagnos.text.strip(),
                'pruebas_comple': self.ids.detalle_examen_pruebas_comple.text.strip(),
                'diag_diferencial': self.ids.detalle_examen_diag_diferencial.text.strip(),
                'diag_definitivo': self.ids.detalle_examen_diag_definitivo.text.strip(),
                'tratamiento_apli': self.ids.detalle_examen_tratamiento_apli.text.strip(),
                'tratamiento_indi': self.ids.detalle_examen_tratamiento_indi.text.strip(),
                'proxi_consulta': self.ids.detalle_examen_proxi_consulta.text.strip(),
                # Campos de laboratorio
                'lab': self.ids.detalle_lab.text.strip(),
                'hb': self.ids.detalle_hb.text.strip(),
                'eosi': self.ids.detalle_eosi.text.strip(),
                'urea': self.ids.detalle_urea.text.strip(),
                'alt': self.ids.detalle_alt.text.strip(),
                'otras_20': self.ids.detalle_otras_20.text.strip(),
                'hto': self.ids.detalle_hto.text.strip(),
                'plaq': self.ids.detalle_plaq.text.strip(),
                'creat': self.ids.detalle_creat.text.strip(),
                'ast': self.ids.detalle_ast.text.strip(),
                'otras_30': self.ids.detalle_otras_30.text.strip(),
                'leuc': self.ids.detalle_leuc.text.strip(),
                'vcm': self.ids.detalle_vcm.text.strip(),
                'bun': self.ids.detalle_bun.text.strip(),
                'fa': self.ids.detalle_fa.text.strip(),
                'otras_40': self.ids.detalle_otras_40.text.strip(),
                'neut': self.ids.detalle_neut.text.strip(),
                'hcm': self.ids.detalle_hcm.text.strip(),
                'pt': self.ids.detalle_pt.text.strip(),
                'bt': self.ids.detalle_bt.text.strip(),
                'otras_50': self.ids.detalle_otras_50.text.strip(),
                'lint': self.ids.detalle_lint.text.strip(),
                'chcm': self.ids.detalle_chcm.text.strip(),
                'alb': self.ids.detalle_alb.text.strip(),
                'bi': self.ids.detalle_bi.text.strip(),
                'otras_60': self.ids.detalle_otras_60.text.strip(),
                'mon': self.ids.detalle_mon.text.strip(),
                'descar': self.ids.detalle_descar.text.strip(),
                'glo': self.ids.detalle_glo.text.strip(),
                'bd': self.ids.detalle_bd.text.strip(),
                'otras_70': self.ids.detalle_otras_70.text.strip(),
            }
            
            # Ejecutar actualización en la base de datos
            resultado = self.actualizar_examen_bd(datos_actualizados)
            
            if resultado:
                # Actualizar datos locales
                self.examen_data.update(datos_actualizados)
                
                # Salir del modo edición
                self.toggle_edicion()
                
                # Mostrar mensaje de éxito
                self.mostrar_mensaje("Examen actualizado correctamente", (0, 1, 0, 1))
                
                # Actualizar lista en el popup padre si existe callback
                if self.actualizar_callback:
                    self.actualizar_callback()
            else:
                self.mostrar_mensaje("Error al actualizar examen", (1, 0, 0, 1))
                
        except AttributeError as e:
            self.mostrar_mensaje(f"Error: Campo no encontrado - {str(e)}", (1, 0, 0, 1))
            print(f"Error de ID de widget: {str(e)}")
        except Exception as e:
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", (1, 0, 0, 1))
            print(f"Error general: {str(e)}")
    # ✅ NUEVO MÉTODO: Actualizar en base de datos
    def actualizar_examen_bd(self, datos):
        """Actualiza el examen en la base de datos"""
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        try:
            query = """
            UPDATE examen_clinico SET 
                desparasitaciones = ?, vacuna = ?, alimentacion = ?, anamnesis = ?,
                peso = ?, temperatura = ?, fc = ?, fr = ?, p_femoral = ?, yugular = ?,
                tpg = ?, ps = ?, pd = ?, pam = ?, mucosas = ?, ganglios = ?,
                palp_abdominal = ?, patron_lesion = ?, genitales = ?,
                procedimiento_diagnos = ?, pruebas_comple = ?, diag_diferencial = ?,
                diag_definitivo = ?, tratamiento_apli = ?, tratamiento_indi = ?,
                proxi_consulta = ?, lab = ?, hb = ?, eosi = ?, urea = ?, alt = ?,
                otras_20 = ?, hto = ?, plaq = ?, creat = ?, ast = ?, otras_30 = ?,
                leuc = ?, vcm = ?, bun = ?, fa = ?, otras_40 = ?, neut = ?,
                hcm = ?, pt = ?, bt = ?, otras_50 = ?, lint = ?, chcm = ?,
                alb = ?, bi = ?, otras_60 = ?, mon = ?, descar = ?, glo = ?,
                bd = ?, otras_70 = ?
            WHERE id = ?
            """
            
            parametros = (
                datos['desparasitaciones'], datos['vacuna'], datos['alimentacion'], datos['anamnesis'],
                datos['peso'], datos['temperatura'], datos['fc'], datos['fr'], datos['p_femoral'],
                datos['yugular'], datos['tpg'], datos['ps'], datos['pd'], datos['pam'],
                datos['mucosas'], datos['ganglios'], datos['palp_abdominal'], datos['patron_lesion'],
                datos['genitales'], datos['procedimiento_diagnos'], datos['pruebas_comple'],
                datos['diag_diferencial'], datos['diag_definitivo'], datos['tratamiento_apli'],
                datos['tratamiento_indi'], datos['proxi_consulta'], datos['lab'], datos['hb'],
                datos['eosi'], datos['urea'], datos['alt'], datos['otras_20'], datos['hto'],
                datos['plaq'], datos['creat'], datos['ast'], datos['otras_30'], datos['leuc'],
                datos['vcm'], datos['bun'], datos['fa'], datos['otras_40'], datos['neut'],
                datos['hcm'], datos['pt'], datos['bt'], datos['otras_50'], datos['lint'],
                datos['chcm'], datos['alb'], datos['bi'], datos['otras_60'], datos['mon'],
                datos['descar'], datos['glo'], datos['bd'], datos['otras_70'],
                self.examen_data['id']  # WHERE id = ?
            )
            
            QueriesSQLite.execute_query(connection, query, parametros)
            return True
            
        except Exception as e:
            print(f"Error al actualizar examen: {e}")
            return False
        finally:
            if connection:
                connection.close()
    # ✅ MÉTODO AUXILIAR: Mostrar mensajes
    def mostrar_mensaje(self, mensaje, color):
        """Muestra un mensaje en el popup"""
        if hasattr(self.ids, 'mensaje_estado'):
            self.ids.mensaje_estado.text = mensaje
            self.ids.mensaje_estado.color = color
        else:
            print(f"MENSAJE: {mensaje}")




class HistoriasMedicasPopup(Popup):
    def __init__(self, paciente_data, **kwargs):
        super(HistoriasMedicasPopup, self).__init__(**kwargs)
        self.paciente_data = paciente_data
        self.cargar_historias_dermatologicas()
                
    def cargar_historias_dermatologicas(self):
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        SELECT id, fecha_registro, diag_diferencial
        FROM historia_dermatologica 
        WHERE id_consulta = ?
        ORDER BY fecha_registro DESC
        """
        historias = QueriesSQLite.execute_read_query(connection, query, (self.paciente_data['id'],))

        # ✅ Usa una lista temporal
        historias_data = []
        if historias:
            for idx, historia in enumerate(historias, 1):
                historias_data.append({
                    'id': historia[0],
                    'numero': idx,
                    'fecha': historia[1][:10] if historia[1] else 'N/A',
                    'diagnostico': historia[2] if historia[2] else 'Sin diagnóstico',
                    'seleccionado': False
                })

            # ✅ Usa agregar_datos si existe, o asigna a data
            rv = self.ids.rv_historias_dermatologicas
            if hasattr(rv, 'agregar_datos'):
                rv.agregar_datos(historias_data)
            else:
                rv.data = historias_data  # Esto ya funciona si AdminRV tiene data

            print(f"✅ Cargadas {len(historias_data)} historias dermatológicas")
            self.ids.mensaje_estado.text = f"Se encontraron {len(historias_data)} historias"
            self.ids.mensaje_estado.color = (0, 0.7, 0, 1)
        else:
            print("📋 No hay historias dermatológicas para este paciente")
            self.ids.mensaje_estado.text = "No hay historias registradas"
            self.ids.mensaje_estado.color = (0.7, 0.5, 0, 1)

        if connection:
            connection.close()


    def eliminar_historia_dermatologica(self):
        """Elimina la historia dermatológica seleccionada"""
        indice = self._obtener_indice_seleccionado()
        if indice < 0:
            self.ids.mensaje_estado.text = "Debe seleccionar una historia para eliminar"
            self.ids.mensaje_estado.color = (1, 0.5, 0, 1)
            return

        historia = self.ids.rv_historias_dermatologicas.data[indice]
        historia_id = historia['id']
        fecha = historia['fecha']

        # Confirmación (opcional: usar popup de confirmación)
        # Por ahora, eliminamos directamente
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        try:
            QueriesSQLite.execute_query(
                connection,
                "DELETE FROM historia_dermatologica WHERE id = ?",
                (historia_id,)
            )
            # Eliminar de la interfaz
            self.ids.rv_historias_dermatologicas.data.pop(indice)
            self.ids.rv_historias_dermatologicas.refresh_from_data()

            self.ids.mensaje_estado.text = f"Historia del {fecha} eliminada"
            self.ids.mensaje_estado.color = (0, 1, 0, 1)  # Verde

            # Recargar para renumerar
            self.cargar_historias_dermatologicas()

        except Exception as e:
            self.ids.mensaje_estado.text = f"Error al eliminar: {str(e)}"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)
        finally:
            if connection:
                connection.close()

    def _obtener_indice_seleccionado(self):
        """Obtiene el índice del elemento seleccionado en el RecycleView"""
        rv = self.ids.rv_historias_dermatologicas
        if hasattr(rv, 'dato_seleccionado'):
            return rv.dato_seleccionado()
        # Búsqueda manual
        for i, item in enumerate(rv.data):
            if item.get('seleccionado', False):
                return i
        return -1
    
    def editar_historia_dermatologica(self):
        """Abre el formulario para editar la historia dermatológica seleccionada"""
        indice = self._obtener_indice_seleccionado()
        if indice < 0:
            self.ids.mensaje_estado.text = "Debe seleccionar una historia para editar"
            self.ids.mensaje_estado.color = (1, 0.5, 0, 1)
            return

        historia = self.ids.rv_historias_dermatologicas.data[indice]

        # Cargar datos desde la base de datos para tener todos los campos
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        SELECT * FROM historia_dermatologica WHERE id = ?
        """
        fila = QueriesSQLite.execute_read_query(connection, query, (historia['id'],))
        connection.close()

        if not fila:
            self.ids.mensaje_estado.text = "No se encontraron datos para editar"
            self.ids.mensaje_estado.color = (1, 0, 0, 1)
            return

        # Mapear los datos de la fila a un diccionario
        columnas = [
            'id', 'id_consulta', 'fecha_registro', 'prurito_escala', 'control_ectoparasitos', 'otros_animales_afectados',
            'estilo_vida', 'paseos', 'banos', 'frecuencia', 'productos_usados',
            'tratamientos_previos', 'examen_fisico', 'estado_actual', 'simetrico', 'asimetrico',
            'generalizado', 'focal', 'multifocal', 'regional', 'grid1', 'grid2', 'grid3', 'grid4',
            'grid5', 'grid6', 'grid7', 'grid8', 'grid9', 'grid10', 'grid11', 'grid12', 'grid13',
            'grid14', 'grid15', 'grid16', 'grid17', 'grid18', 'grid19', 'grid20', 'grid21', 'grid22',
            'grid23', 'grid24', 'diag_diferencial', 'anagen', 'teogen', 'tricomexis', 'melanina',
            'demodex', 'tricografia', 'lampara_woo', 'agentes', 'cabeza', 'cuello', 'abdomen',
            'dd', 'di', 'pd', 'pi', 'otras', 'notas'
        ]
        historia_completa = dict(zip(columnas, fila[0]))
        
        # ✅ Abrir el popup de edición
        popup = FichaRectificadora(
            paciente_data=self.paciente_data,
            actualizar_callback=self.cargar_historias_dermatologicas,
            historia_editar=historia_completa  # Pasar los datos a editar
        )
        popup.open()
    def nueva_historia_der(self):
        popup = FichaRectificadora()
        popup.open()

class FichaRectificadora(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Establecer la fecha actual al abrir el popup
        self.ids.nueva_fecha.text = datetime.now().strftime('%d/%m/%Y')

    def guardar_recepcion(self):
        # Aquí iría la lógica para guardar los datos
        cliente = self.ids.nuevo_cliente.text
        if not cliente.strip():
            self.ids.mensaje_estado.text = "Por favor, ingrese el nombre del cliente."
            return

        # Datos de Partes Recibidas
        partes_recibidas_data = []
        for categoria in ['motor', 'bloque', 'arbol_levas']:
            for i in range(1, 4):  # Ejemplo con 3 columnas por categoría
                parte_id = getattr(self.ids, f'partes_{categoria}_{i}')
                cantidad_id = getattr(self.ids, f'cantidad_{categoria}_{i}')
                parte = parte_id.text
                cantidad = cantidad_id.text
                partes_recibidas_data.append({
                    'categoria': categoria.capitalize(),
                    'parte': parte,
                    'cantidad': cantidad
                })

        # Guardar en MongoDB u otra base de datos
        print("Datos guardados:", {
            "cliente": cliente,
            "fecha": self.ids.nueva_fecha.text,
            "partes_recibidas": partes_recibidas_data
        })
        self.dismiss()  # Cierra el popup

    def guardar_nuevo_cliente(self):
        # Lógica para guardar un nuevo cliente
        pass

    def incluir_repuestos(self):
        # Lógica para incluir repuestos
        pass

    def incluir_servicios_especiales(self):
        # Lógica para incluir servicios especiales
        pass

    def imprimir_ficha(self):
        # Lógica para imprimir la ficha
        pass


            
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
    def __init__(self,_agregar_callback, **kwargs):  
        super(UsuarioPopup,self).__init__(**kwargs)  
        self.agregar_usuario = _agregar_callback
        
    def abrir (self, agregar, usuario = None):
        if agregar:
            self.ids.usuario_info_1.text = 'Agregar Usuario Nuevo'
            self.ids.usuario_username.disabled=False
        else:
            self.ids.usuario_info_1.text = 'Modificar Usuario'
            self.ids.usuario_username.text= usuario ['username']
            self.ids.usuario_username.disabled= True
            self.ids.usuario_nombre.text= usuario ['nombre']
            self.ids.usuario_password.text=usuario ['password']
            if usuario ['tipo'] == 'admin':
                self.ids.admin_tipo.state= 'down'
            else:
                self.ids.trabajador_tipo.state='down'
        self.open()
    
    def verificar(self, usuario_username, usuario_nombre, usuario_password,admin_tipo,trabajador_tipo):
        alert1 = 'Falta '
        validado = {}
        
        if not usuario_username:
            alert1 += 'Username. '
            validado ['username'] = False
        else:
            validado ['username'] = usuario_username
            
        if  not usuario_nombre:
            alert1 += 'Nombre.'
            validado['nombre'] = False
        else:
            validado['nombre'] = usuario_nombre.lower()
        
        if not usuario_password:
            alert1 += 'Password. '
            validado ['password'] = False
        
        else: 
            validado['password'] = usuario_password
            
        if admin_tipo =='normal' and trabajador_tipo=='normal':
            alert1 += 'Tipo. '
            validado['tipo'] = False
        
        else: 
            
            if admin_tipo== 'down':
                validado ['tipo'] = 'admin'
            else:
                validado ['tipo'] = 'trabajador'
            
        valores = list(validado.values())

        if False in valores:
            self.ids.no_valid_notif.text=alert1
            
        else:
            
            self.ids.no_valid_notif.text =''
            self.agregar_usuario(True,validado)
            self.dismiss()
            
            
class VetPopup(Popup):
    def __init__(self,_agregar_callback, **kwargs):  
        super(VetPopup,self).__init__(**kwargs)  
        self.agregar_vet = _agregar_callback
        
    def abrir(self, agregar, usuario=None):
        if agregar:
            self.ids.vet_info_1.text = 'Agregar Veterinario Nuevo'
            self.ids.vet_ci.disabled = False
            # ✅ Limpiar campos
            self.ids.vet_ci.text = ''
            self.ids.vet_nombre.text = ''
            self.ids.CMVB.text = ''
            self.ids.MPPS.text = ''
        else:
            self.ids.vet_info_1.text = 'Modificar Veterinario'
            self.ids.vet_ci.text = usuario['ci']
            self.ids.vet_ci.disabled = True
            self.ids.vet_nombre.text = usuario['nombre']
            self.ids.CMVB.text = usuario['cmvb']
            self.ids.MPPS.text = usuario['mpps']
        self.open()
    
    def verificar1(self, CI, Nombre, CMVB, MPPS):
        alert1 = 'Falta: '
        validado = {}

        if not CI:
            alert1 += 'CI. '
            validado['CI'] = False
        else:
            validado['CI'] = CI.strip()

        if not Nombre:
            alert1 += 'Nombre. '
            validado['nombre'] = False
        else:
            validado['nombre'] = Nombre.strip().lower()

        if not CMVB:
            alert1 += 'CMVB. '
            validado['CMVB'] = False
        else:
            validado['CMVB'] = CMVB.strip()

        if not MPPS:
            alert1 += 'MPPS. '
            validado['MPPS'] = False
        else:
            validado['MPPS'] = MPPS.strip()

        valores = list(validado.values())
        if False in valores:
            self.ids.no_valid_notif.text = alert1
        else:
            self.ids.no_valid_notif.text = ''
            self.agregar_vet(True, validado)
            self.dismiss()
            
            
            
class VistaUsuarios(Screen):  
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        Clock.schedule_once(self.cargar_usuarios, 1)  
  
    def cargar_usuarios(self, *args):
        _usuarios = []
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")

        # Cargar usuarios normales
        usuarios_sql = QueriesSQLite.execute_read_query(connection, "SELECT * FROM usuarios")
        for u in usuarios_sql:
            _usuarios.append({
                'tipo_registro': 'usuario',           # Tipo para diferenciar
                'nombre': u[1],
                'username': u[0],
                'password': u[2],
                'tipo': u[3],                         # admin/trabajador
                'ci': '',                             # Vacío para usuarios
                'cmvb': '',
                'mpps': ''
            })

        # Cargar veterinarios
        vets_sql = QueriesSQLite.execute_read_query(connection, "SELECT * FROM veterinarios")
        for v in vets_sql:
            _usuarios.append({
                'tipo_registro': 'veterinario',       # Tipo para diferenciar
                'nombre': v[2],                       # Nombre
                'username': 'N/A',                   # No aplica
                'password': 'N/A',                   # No aplica
                'tipo': 'veterinario',               # Etiqueta para mostrar
                'ci': str(v[1]) if v[1] else '',     # CI2
                'cmvb': v[3] if v[3] else '',
                'mpps': v[4] if v[4] else ''
            })

        self.ids.rv_usuarios.agregar_datos(_usuarios)

    def agregar_usuario(self, agregar=False, validado=None):
        if agregar:
            usuario_tuple = (validado['username'], validado['nombre'], validado['password'], validado['tipo'])
            connection = QueriesSQLite.create_connection('pdvDB.sqlite')
            crear_usuario = """
            INSERT INTO usuarios (username, nombre, password, tipo)
            VALUES (?, ?, ?, ?);
            """
            QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple)

            # ✅ Añadir al RecycleView con 'tipo_registro'
            nuevo_usuario = {
                'tipo_registro': 'usuario',
                'nombre': validado['nombre'],
                'username': validado['username'],
                'password': validado['password'],
                'tipo': validado['tipo'],
                'ci': '',
                'cmvb': '',
                'mpps': ''
            }
            self.ids.rv_usuarios.data.append(nuevo_usuario)
            self.ids.rv_usuarios.refresh_from_data()
        else:
            popup = UsuarioPopup(self.agregar_usuario)
            popup.abrir(True)

    def agregar_vet(self, agregar=False, validado=None):
        if agregar:
            vet_tuple = (validado['CI'], validado['nombre'], validado['CMVB'], validado['MPPS'])
            connection = QueriesSQLite.create_connection('pdvDB.sqlite')
            crear_vet = """
            INSERT INTO veterinarios (CI2, Nombre, CMVB, MPPS)
            VALUES (?, ?, ?, ?);
            """
            try:
                QueriesSQLite.execute_query(connection, crear_vet, vet_tuple)

                # ✅ Añadir al RecycleView con 'tipo_registro'
                nuevo_vet = {
                    'tipo_registro': 'veterinario',
                    'nombre': validado['nombre'],
                    'username': 'N/A',
                    'password': 'N/A',
                    'tipo': 'veterinario',
                    'ci': str(validado['CI']),
                    'cmvb': validado['CMVB'],
                    'mpps': validado['MPPS']
                }
                self.ids.rv_usuarios.data.append(nuevo_vet)
                self.ids.rv_usuarios.refresh_from_data()
            except Exception as e:
                print(f"Error al agregar veterinario: {e}")
        else:
            popup = VetPopup(self.agregar_vet)
            popup.abrir(True)
            
            
            
    def modificar_usuario(self, modificar=False, validado=None):
        indice = self.ids.rv_usuarios.dato_seleccionado()
        if modificar:
            usuario_tuple=(validado['nombre'],validado['password'],validado['tipo'],validado['username'])
            connection=QueriesSQLite.create_connection("pdvDB.sqlite")
            actualizar = """
            
            UPDATE
               usuarios
            SET 
               nombre = ?, password= ? , tipo = ?
            WHERE
            
            username =?
            """
            QueriesSQLite.execute_query(connection, actualizar, usuario_tuple)
            self.ids.rv_usuarios.data[indice]['nombre']=validado['nombre']
            self.ids.rv_usuarios.data[indice]['tipo']=validado['tipo']  
            self.ids.rv_usuarios.data[indice]['password']=validado['password']
            self.ids.rv_usuarios.refresh_from_data()
        else:
            if indice >= 0:
                usuario = self.ids.rv_usuarios.data[indice]
                popup = UsuarioPopup(self.modificar_usuario)
                popup.abrir(False,usuario)      
        
            

    def modificar_vet(self, modificar=False, validado=None):
        indice = self.ids.rv_usuarios.dato_seleccionado()
        if modificar:
            # ✅ Usar minúsculas como en los datos
            connection = QueriesSQLite.create_connection("pdvDB.sqlite")
            query = """
            UPDATE veterinarios 
            SET Nombre = ?, CMVB = ?, MPPS = ?
            WHERE CI2 = ?
            """
            params = (
                validado['nombre'],  # minúscula
                validado['CMVB'],
                validado['MPPS'],
                validado['CI']       # CI viene del popup
            )
            try:
                QueriesSQLite.execute_query(connection, query, params)

                # ✅ Actualizar en el RecycleView
                self.ids.rv_usuarios.data[indice].update({
                    'nombre': validado['nombre'],
                    'ci': validado['CI'],
                    'cmvb': validado['CMVB'],
                    'mpps': validado['MPPS']
                })
                self.ids.rv_usuarios.refresh_from_data()

                # ✅ Mensaje de éxito
                if hasattr(self.ids, 'mensaje_estado'):
                    self.ids.mensaje_estado.text = "Veterinario actualizado correctamente"
                    self.ids.mensaje_estado.color = (0, 0.7, 0, 1)
            except Exception as e:
                print(f"Error al actualizar veterinario: {e}")
                if hasattr(self.ids, 'mensaje_estado'):
                    self.ids.mensaje_estado.text = "Error al actualizar veterinario"
                    self.ids.mensaje_estado.color = (1, 0, 0, 1)
        else:
            if indice >= 0:
                item = self.ids.rv_usuarios.data[indice]
                if item.get('tipo_registro') == 'veterinario':
                    popup = VetPopup(self.modificar_vet)  # ✅ Callback correcto
                    popup.abrir(False, item)
                else:
                    if hasattr(self.ids, 'mensaje_estado'):
                        self.ids.mensaje_estado.text = "Debe seleccionar un veterinario"
                        self.ids.mensaje_estado.color = (1, 0.5, 0, 1)
            else:
                if hasattr(self.ids, 'mensaje_estado'):
                    self.ids.mensaje_estado.text = "Debe seleccionar un veterinario"
                    self.ids.mensaje_estado.color = (1, 0.5, 0, 1)

        
    def eliminar_usuario(self):
        indice = self.ids.rv_usuarios.dato_seleccionado()
        if indice>=0:
            usuario_tuple=(self.ids.rv_usuarios.data[indice]['username'],)
            connection=QueriesSQLite.create_connection("pdvDB.sqlite")
            borrar = """DELETE from usuarios where username = ?"""
            QueriesSQLite.execute_query(connection, borrar, usuario_tuple)
            self.ids.rv_usuarios.data.pop(indice)
            self.ids.rv_usuarios.refresh_from_data()
            
    def eliminar_vet(self):
        indice = self.ids.rv_usuarios.dato_seleccionado()
        if indice>=0:
            usuario_tuple=(self.ids.rv_usuarios.data[indice]['ci'],)
            connection=QueriesSQLite.create_connection("pdvDB.sqlite")
            borrar = """DELETE from veterinarios where CI2 = ?"""
            QueriesSQLite.execute_query(connection, borrar, usuario_tuple)
            self.ids.rv_usuarios.data.pop(indice)
            self.ids.rv_usuarios.refresh_from_data()
            


class VistaConsultas(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def siguiente(self):
        # Validación de ids
        if not hasattr(self, 'ids') or not self.ids:
            print("Los IDs no están disponibles todavía.")
            return

        nombre_propietario = self.ids.propietario.text.strip()
        ci = self.ids.ci.text.strip()
        telefono = self.ids.telefono.text.strip()
        direccion = self.ids.direccion.text.strip()
        motivo_consulta = self.ids.motivo_consulta.text.strip()
        nombre_mascota = self.ids.nombre_animal.text.strip()
        especie = self.ids.especie.text.strip()
        raza = self.ids.raza.text.strip()
        sexo = self.ids.sexo.text.strip()
        edad = self.ids.edad.text.strip()
        pelaje = self.ids.pelaje.text.strip()
        cc = self.ids.cc.text.strip()
        enfermedad = self.ids.enfermedad.text.strip()
        tratamiento = self.ids.tratamiento.text.strip()

        # Validación básica
        if not nombre_propietario:
            if hasattr(self.ids, 'notificacion'):
                self.ids.notificacion.text = "Por favor, completa los campos obligatorios"
            else:
                print("Advertencia: No se encontró el id 'notificacion'")
            return
        else:
            if hasattr(self.ids, 'notificacion'):
                self.ids.notificacion.text = ""


        # Preparar datos
        consulta_data = (
            nombre_propietario,
            ci,
            telefono,
            direccion,
            motivo_consulta,
            nombre_mascota,
            especie,
            raza,
            sexo,
            edad,
            pelaje,
            cc,
            enfermedad,
            tratamiento,
        )

        # Guardar en la base de datos
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")

        insert_query = """
        INSERT INTO consultas (
            nombre_propietario, ci, telefono, direccion, motivo_consulta,
            nombre_mascota, especie, raza, sexo, edad, pelaje, cc,
            enfermedad, tratamiento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        QueriesSQLite.execute_query(connection, insert_query, consulta_data)

        print("Consulta guardada correctamente")
        self.limpiar()
    def limpiar(self):
        self.ids.propietario.text = ""
        self.ids.ci.text = ""
        self.ids.telefono.text = ""
        self.ids.direccion.text = ""
        self.ids.motivo_consulta.text = ""
        self.ids.nombre_animal.text = ""
        self.ids.especie.text = ""
        self.ids.raza.text = ""
        self.ids.sexo.text = ""
        self.ids.edad.text = ""
        self.ids.pelaje.text = ""
        self.ids.cc.text = ""
        self.ids.enfermedad.text = ""
        self.ids.tratamiento.text = ""



    
class CustomDropDown(DropDown):
    def __init__(self, cambiar_callback, **kwargs):
        self._succ_cb = cambiar_callback
        super(CustomDropDown, self).__init__(**kwargs)

    def vista(self, vista):
        if callable(self._succ_cb):
            self._succ_cb(True, vista)    

class VistaPacientes(Screen):
    def __init__(self, **kwargs):
        super(VistaPacientes, self).__init__(**kwargs)
        Clock.schedule_once(self.cargar_pacientes, 0.1)

    def cargar_pacientes(self, dt=None):
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        query = """
        SELECT id, nombre_propietario, ci, nombre_mascota, telefono, 
               direccion, motivo_consulta, especie, raza, sexo, edad, 
               pelaje, cc, enfermedad, tratamiento,  fecha_registro
        FROM consultas
        ORDER BY fecha_registro DESC
        """
        
        pacientes = QueriesSQLite.execute_read_query(connection, query)
        
        if pacientes:
            self.ids.rv_pacientes.data = []  # Limpiar datos anteriores
            pacientes_data = []
            
            for paciente in pacientes:
                paciente_dict = {
                    'id': paciente[0],
                    'nombre_propietario': paciente[1],
                    'ci': paciente[2],
                    'nombre_mascota': paciente[3],
                    'telefono': paciente[4],
                    'direccion': paciente[5],
                    'motivo_consulta': paciente[6],
                    'especie': paciente[7],
                    'raza': paciente[8],
                    'sexo': paciente[9],
                    'edad': paciente[10],
                    'pelaje': paciente[11],
                    'cc': paciente[12],
                    'enfermedad': paciente[13],
                    'tratamiento': paciente[14],
                    'fecha_registro': paciente[15],
                    'seleccionado': False
                }
                pacientes_data.append(paciente_dict)
            
            self.ids.rv_pacientes.agregar_datos(pacientes_data)

    def filtrar_pacientes(self):
        filtro_propietario = self.ids.filtro_propietario.text.strip().lower()
        filtro_ci = self.ids.filtro_ci.text.strip()
        filtro_mascota = self.ids.filtro_mascota.text.strip().lower()

        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        # Construir query dinámicamente según los filtros
        query = """
        SELECT id, nombre_propietario, ci, nombre_mascota, telefono, 
               direccion, motivo_consulta, especie, raza, sexo, edad, 
               pelaje, cc, enfermedad, tratamiento,  fecha_registro
        FROM consultas WHERE 1=1
        """
        params = []

        if filtro_propietario:
            query += " AND LOWER(nombre_propietario) LIKE ?"
            params.append(f"%{filtro_propietario}%")

        if filtro_ci:
            query += " AND ci LIKE ?"
            params.append(f"%{filtro_ci}%")

        if filtro_mascota:
            query += " AND LOWER(nombre_mascota) LIKE ?"
            params.append(f"%{filtro_mascota}%")

        query += " ORDER BY fecha_registro DESC"

        pacientes = QueriesSQLite.execute_read_query(connection, query, tuple(params))
        
        # Limpiar datos anteriores
        self.ids.rv_pacientes.data = []
        
        if pacientes:
            pacientes_data = []
            for paciente in pacientes:
                paciente_dict = {
                    'id': paciente[0],
                    'nombre_propietario': paciente[1],
                    'ci': paciente[2],
                    'nombre_mascota': paciente[3],
                    'telefono': paciente[4],
                    'direccion': paciente[5],
                    'motivo_consulta': paciente[6],
                    'especie': paciente[7],
                    'raza': paciente[8],
                    'sexo': paciente[9],
                    'edad': paciente[10],
                    'pelaje': paciente[11],
                    'cc': paciente[12],
                    'enfermedad': paciente[13],
                    'tratamiento': paciente[14],
                    'fecha_registro': paciente[15],
                    'seleccionado': False
                }
                pacientes_data.append(paciente_dict)
            
            self.ids.rv_pacientes.agregar_datos(pacientes_data)

    def limpiar_filtros(self):
        self.ids.filtro_propietario.text = ""
        self.ids.filtro_ci.text = ""
        self.ids.filtro_mascota.text = ""
        self.cargar_pacientes()

    def mostrar_detalle_paciente(self):
            indice = self.ids.rv_pacientes.dato_seleccionado()
            if indice >= 0:
                paciente_seleccionado = self.ids.rv_pacientes.data[indice]
                # Pasar el callback para actualizar la lista después de editar
                popup = DetallePacientePopup(paciente_seleccionado, self.cargar_pacientes)
                popup.open()
            else:
                print("No hay paciente seleccionado")

    def eliminar_paciente(self):
        """Elimina el paciente seleccionado y todos sus exámenes clínicos asociados"""
        # Verificar que hay un paciente seleccionado
        indice = self.ids.rv_pacientes.dato_seleccionado()
        
        if indice < 0:
            self.mostrar_mensaje("Error: Debe seleccionar un paciente para eliminar", (1, 0, 0, 1))
            return
        
        # Obtener datos del paciente seleccionado
        paciente_seleccionado = self.ids.rv_pacientes.data[indice]
        
        # Verificar cuántos exámenes tiene asociados
        num_examenes = self.contar_examenes_paciente(paciente_seleccionado['id'])
        
        # Crear popup de confirmación
        popup_confirmacion = ConfirmacionEliminarPacientePopup(
            paciente_data=paciente_seleccionado,
            num_examenes=num_examenes,
            callback_eliminar=self.confirmar_eliminacion_paciente
        )
        popup_confirmacion.open()
    # ✅ MÉTODO: Contar exámenes del paciente
    def contar_examenes_paciente(self, paciente_id):
        """Cuenta cuántos exámenes clínicos tiene el paciente"""
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        try:
            query = "SELECT COUNT(*) FROM examen_clinico WHERE id_consulta = ?"
            resultado = QueriesSQLite.execute_read_query(connection, query, (paciente_id,))
            
            if resultado:
                return resultado[0][0]
            return 0
            
        except Exception as e:
            print(f"Error al contar exámenes: {e}")
            return 0
        finally:
            if connection:
                connection.close()
    # ✅ MÉTODO: Confirmar y ejecutar eliminación
    def confirmar_eliminacion_paciente(self, paciente_id):
        """Ejecuta la eliminación del paciente y sus exámenes en la base de datos"""
        try:
            resultado = self.eliminar_paciente_completo_bd(paciente_id)
            
            if resultado:
                # Mostrar mensaje de éxito
                self.mostrar_mensaje("Paciente y exámenes eliminados correctamente", (0, 1, 0, 1))
                
                # Recargar la lista de pacientes
                self.cargar_pacientes()
                
                print(f" Paciente con ID {paciente_id} eliminado completamente")
            else:
                self.mostrar_mensaje("Error al eliminar el paciente", (1, 0, 0, 1))
                
        except Exception as e:
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", (1, 0, 0, 1))
            print(f"💥 Error al eliminar paciente: {e}")
    # ✅ MÉTODO: Eliminar de base de datos (paciente + exámenes)
    def eliminar_paciente_completo_bd(self, paciente_id):
        """Elimina físicamente el paciente y todos sus exámenes de la base de datos"""
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        
        try:
            # Iniciar transacción
            connection.execute("BEGIN TRANSACTION")
            
            print(f" Eliminando paciente con ID: {paciente_id}")
            
            # 1. Primero eliminar todos los exámenes clínicos asociados
            query_examenes = "DELETE FROM examen_clinico WHERE id_consulta = ?"
            QueriesSQLite.execute_query(connection, query_examenes, (paciente_id,))
            print(f" Exámenes clínicos eliminados para paciente ID: {paciente_id}")
            
            # 2. Luego eliminar el paciente (consulta)
            query_paciente = "DELETE FROM consultas WHERE id = ?"
            QueriesSQLite.execute_query(connection, query_paciente, (paciente_id,))
            
            
            query_paciente = "DELETE FROM recipes WHERE id = ?"
            QueriesSQLite.execute_query(connection, query_paciente, (paciente_id,))

            
            query_paciente = "DELETE FROM historia_dermatologica WHERE id = ?"
            QueriesSQLite.execute_query(connection, query_paciente, (paciente_id,))

            
            # Confirmar transacción
            connection.commit()
            print("✅ Transacción completada exitosamente")
            
            return True
            
        except Exception as e:
            # Revertir transacción en caso de error
            connection.rollback()
            print(f" Error en base de datos, transacción revertida: {e}")
            return False
        finally:
            if connection:
                connection.close()
    # ✅ MÉTODO AUXILIAR: Mostrar mensajes
    def mostrar_mensaje(self, mensaje, color):
        """Muestra un mensaje en la vista (requiere Label mensaje_estado en .kv)"""
        if hasattr(self.ids, 'mensaje_estado'):
            self.ids.mensaje_estado.text = mensaje
            self.ids.mensaje_estado.color = color
        else:
            print(f"MENSAJE: {mensaje}")
    
class ConfirmacionEliminarPacientePopup(Popup):
    """Popup para confirmar la eliminación de un paciente y sus exámenes"""
    
    def __init__(self, paciente_data, num_examenes, callback_eliminar, **kwargs):
        super(ConfirmacionEliminarPacientePopup, self).__init__(**kwargs)
        self.paciente_data = paciente_data
        self.num_examenes = num_examenes
        self.callback_eliminar = callback_eliminar
        
        # Configurar popup
        self.title = " ELIMINAR PACIENTE Y EXÁMENES"
        self.size_hint = (0.7, 0.5)
        self.auto_dismiss = False
        
        # Crear contenido
        self.create_content()

    def create_content(self):
        """Crea el contenido del popup de confirmación"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Mensaje de advertencia principal
        warning_label = Label(
            text=f"¿Está seguro que desea eliminar este paciente?\n\n"
                 f" Propietario: {self.paciente_data.get('nombre_propietario', 'N/A')}\n"
                 f" C.I.: {self.paciente_data.get('ci', 'N/A')}\n"
                 f" Mascota: {self.paciente_data.get('nombre_mascota', 'N/A')}\n\n"
                 f" Exámenes clínicos asociados: {self.num_examenes}\n\n"
                 f" SE ELIMINARÁN TODOS LOS DATOS:\n"
                 f" Información del paciente\n"
                 f" Todos los exámenes clínicos ({self.num_examenes})\n"
                 f" Datos de laboratorio asociados\n\n"
                 f" Esta acción NO se puede deshacer",
            text_size=(None, None),
            halign='center',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1)
        )
        main_layout.add_widget(warning_label)
        
        # Advertencia adicional si tiene exámenes
        if self.num_examenes > 0:
            extra_warning = Label(
                text=f" ATENCIÓN: Este paciente tiene {self.num_examenes} exámen(es) clínico(s)\n"
                     f"que también serán eliminados permanentemente.",
                size_hint_y=None,
                height=60,
                color=(0.8, 0.2, 0.2, 1),
                bold=True
            )
            main_layout.add_widget(extra_warning)
        
        # Botones de acción
        buttons_layout = BoxLayout(size_hint_y=None, height=60, spacing=20)
        
        # Botón Cancelar
        btn_cancelar = Button(
            text=' Cancelar',
            background_color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.4
        )
        btn_cancelar.bind(on_release=self.dismiss)
        buttons_layout.add_widget(btn_cancelar)
        
        # Espacio
        buttons_layout.add_widget(BoxLayout(size_hint_x=0.2))
        
        # Botón Eliminar
        btn_eliminar = Button(
            text=f'🗑️ ELIMINAR TODO\n({self.num_examenes} exámenes)',
            background_color=(0.9, 0.2, 0.2, 1),
            size_hint_x=0.4
        )
        btn_eliminar.bind(on_release=self.ejecutar_eliminacion)
        buttons_layout.add_widget(btn_eliminar)
        
        main_layout.add_widget(buttons_layout)
        self.content = main_layout

    def ejecutar_eliminacion(self, instance):
        """Ejecuta la eliminación y cierra el popup"""
        paciente_id = self.paciente_data['id']
        
        # Llamar al callback para eliminar
        self.callback_eliminar(paciente_id)
        
        # Cerrar popup
        self.dismiss()
    
    
class VistaOperador(Screen):
    def __init__(self, **kwargs):
        super(VistaOperador, self).__init__(**kwargs)
        # Programar la inicialización después de que el widget esté construido
        Clock.schedule_once(self.inicializar_despues_kv, 0.1)

    def inicializar_despues_kv(self, dt):
        """Se llama después de que el .kv haya cargado los widgets"""
        try:
            self.rv = self.ids.rv_operador  # Ahora sí está disponible
            self.cargar_operadores()  # Cargar datos inmediatamente
        except KeyError:
            print("Error: No se encontró el widget con id: rv_operador")
            # Si quieres, puedes mostrar un mensaje en pantalla más adelante

    def cargar_operadores(self, *args):
        """Carga los operadores desde MongoDB"""
        collection = conectar_mongo()
        
        try:
            operadores = list(collection.find())
            data = []
            for op in operadores:
                data.append({
                    'nombre': op['nombre'],
                    'porcentaje': op['porcentaje'],
                    'tasa': op['tasa'],
                    'seleccionado': False,
                    '_id': op['_id']
                })
            self.rv.data = data
            # ✅ Eliminado: self.ids.contador_citas.text = f"Operadores: {len(data)}"
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






class AdminWindow(BoxLayout):  
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        self.vista_actual = 'Agenda'  
        self.vista_manager = self.ids.vista_manager  
        self.dropdown = CustomDropDown(self.cambiar_vista)
        self.ids.cambiar_vista.bind(on_release=self.dropdown.open)
            
    def cambiar_vista(self, cambio=False, vista=None):
        if cambio:
            self.vista_actual = vista
            self.vista_manager.current = self.vista_actual
            self.dropdown.dismiss()
    def salir(self):  
        self.parent.parent.current = 'signin'  
  

    def poner_usuario(self, usuario):
        print("Usuario logueado:", usuario)
        self.usuario = usuario
    def actualizar_productos(self, productos):
        self.ids.vista_productos.actualizar_productos(productos)
        

class RecepcionPartesPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Establecer la fecha actual al abrir el popup
        self.ids.nueva_fecha.text = datetime.now().strftime('%d/%m/%Y')

    def guardar_recepcion(self):
        # Aquí iría la lógica para guardar los datos
        cliente = self.ids.nuevo_cliente.text
        if not cliente.strip():
            self.ids.mensaje_estado.text = "Por favor, ingrese el nombre del cliente."
            return

        # Datos de Mano de Obra
        mano_obra_data = []
        for i in range(1, 4):  # Ejemplo con 3 filas
            mano_obra = getattr(self.ids, f'mano_obra_{i}').text
            operarios = getattr(self.ids, f'operarios_{i}').text
            cantidad = getattr(self.ids, f'cantidad_{i}').text
            precio = getattr(self.ids, f'precio_{i}').text
            porcentaje = getattr(self.ids, f'porcentaje_{i}').text
            mano_obra_data.append({
                'mano_obra': mano_obra,
                'operarios': operarios,
                'cantidad': cantidad,
                'precio': precio,
                'porcentaje': porcentaje
            })

        # Datos de Partes Recibidas
        partes_recibidas_data = []
        for i in range(1, 4):  # Ejemplo con 3 filas
            parte = getattr(self.ids, f'partes_recibidas_{i}').text
            cantidad = getattr(self.ids, f'cantidad_partes_{i}').text
            partes_recibidas_data.append({
                'parte': parte,
                'cantidad': cantidad
            })

        # Guardar en MongoDB u otra base de datos
        print("Datos guardados:", {
            "cliente": cliente,
            "fecha": self.ids.nueva_fecha.text,
            "mano_obra": mano_obra_data,
            "partes_recibidas": partes_recibidas_data
        })
        self.dismiss()  # Cierra el popup

    def guardar_nuevo_cliente(self):
        # Lógica para guardar un nuevo cliente
        pass

    def incluir_repuestos(self):
        # Lógica para incluir repuestos
        pass

    def incluir_servicios_especiales(self):
        # Lógica para incluir servicios especiales
        pass

    def imprimir_ficha(self):
        # Lógica para imprimir la ficha
        pass
    
    def agregar_fila_mano_obra(self):
        # Obtén el GridLayout por su id
        grid = self.ids.grid_mano_obra  # Asegúrate de darle un id en .kv

        # Crear un BoxLayout para la nueva fila
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

        # Crear los widgets
        spinner = Spinner(
            text='Seleccionar',
            values=['Torno', 'Soldadura', 'Otros'],
            size_hint_x=0.3
        )
        operarios = TextInput(
            input_filter='int',
            size_hint_x=0.1
        )
        cantidad = TextInput(
            input_filter='float',
            size_hint_x=0.1
        )
        precio = TextInput(
            input_filter='float',
            size_hint_x=0.1
        )
        porcentaje = TextInput(
            input_filter='float',
            size_hint_x=0.1
        )
        total_mano_obra = TextInput(
            readonly=True,
            size_hint_x=0.2
        )

        # Asignar IDs dinámicos (opcional, para acceder después)
        # No puedes usar .ids con nombres dinámicos, pero puedes guardar en un dict si necesitas
        row.add_widget(spinner)
        row.add_widget(operarios)
        row.add_widget(cantidad)
        row.add_widget(precio)
        row.add_widget(porcentaje)
        row.add_widget(total_mano_obra)

        # Añadir la fila al GridLayout
        grid.add_widget(row)

        # Incrementar contador
        self.fila_count += 1
  
  
  
  
  
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):  
    touch_deselect_last = BooleanProperty(True)  
  
def conectar_mongo1():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['Inrema']
        return db['Repuestos']  # Colección "Repuestos"
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None


# === Widgets Personalizados ===

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

class VistaInventario(Screen):
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
  
  
class AdminApp(App):  
    def build(self):  
        return AdminWindow()  
  
if __name__ == "__main__":  
    AdminApp().run()

