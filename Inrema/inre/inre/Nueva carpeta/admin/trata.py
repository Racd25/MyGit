from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView

class ContenedorCentrado(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None  # ← Para controlar altura manualmente
        self.height = dp(80)   # Altura inicial pequeña
        self.padding = [10, 10]
        self.spacing = 5
        self.pos_hint = {'center_x': 0.5}  # ← Centra horizontalmente
        self.size_hint_x = 0.6             # ← Ocupa el 60% del ancho

        # Fondo negro
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Negro
            self.rect = Rectangle(pos=self.pos, size=self.size)

        # Vincular actualización del fondo al tamaño/posición
        self.bind(pos=self._actualizar_rect, size=self._actualizar_rect)

    def _actualizar_rect(self, instance, value):
        """Actualiza el rectángulo de fondo cuando cambia posición o tamaño"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def agregar_label(self):
        """Añade un label con texto blanco"""
        label = Label(
            text=f"Nuevo trabajo {len(self.children)}",
            color=(1, 1, 1, 1),  # Texto blanco
            size_hint_y=None,
            height=dp(30),
            font_size=14,
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        self.add_widget(label, index=0)  # Añadir arriba
        self.height += dp(30)           # Hacer crecer el contenedor
        print(f"✅ Label añadido. Nueva altura: {self.height:.0f}dp")

class InterfazApp(App):
    def build(self):
        # Layout principal (vertical)
        layout_principal = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=10
        )

        # Fondo blanco para toda la ventana
        with layout_principal.canvas.before:
            Color(1, 1, 1, 1)  # Blanco
            self.rect_fondo = Rectangle(pos=layout_principal.pos, size=layout_principal.size)
        layout_principal.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

        # ✅ CONTENEDOR VERDE (arriba)
        contenedor_verde = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[10, 5],
            spacing=5
        )
        with contenedor_verde.canvas.before:
            Color(0, 0.7, 0.3, 1)  # Verde oscuro
            self.rect_verde = Rectangle(pos=contenedor_verde.pos, size=contenedor_verde.size)
        contenedor_verde.bind(pos=self._actualizar_rect, size=self._actualizar_rect)

        # Añadir contenido al contenedor verde (opcional)
        label_verde = Label(
            text="Encabezado Verde",
            color=(1, 1, 1, 1),
            font_size=16,
            bold=True
        )
        contenedor_verde.add_widget(label_verde)

        # ✅ CONTENEDOR NEGRO (pequeño, centrado en el resto del espacio)
        self.contenedor_negro = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(40),  # Altura inicial pequeña
            padding=[10, 5],
            spacing=2
        )
        with self.contenedor_negro.canvas.before:
            Color(0, 0, 0, 1)  # Negro
            self.rect_negro = Rectangle(pos=self.contenedor_negro.pos, size=self.contenedor_negro.size)
        self.contenedor_negro.bind(pos=self._actualizar_rect, size=self._actualizar_rect)

        # ✅ BOTÓN PARA AÑADIR LABELS
        btn = Button(
            text="➕ Añadir Trabajo",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=16
        )
        btn.bind(on_press=self.on_presionar_boton)

        # Agregar ambos contenedores al layout principal
        layout_principal.add_widget(contenedor_verde)
        layout_principal.add_widget(self.contenedor_negro)
        layout_principal.add_widget(btn)

        return layout_principal

    def _actualizar_fondo(self, instance, value):
        """Actualiza el fondo blanco si cambia tamaño o posición"""
        self.rect_fondo.pos = instance.pos
        self.rect_fondo.size = instance.size

    def _actualizar_rect(self, instance, value):
        """Actualiza el rectángulo de fondo cuando cambia tamaño o posición"""
        if hasattr(self, 'rect_verde') and instance == self.root.children[2]:
            self.rect_verde.pos = instance.pos
            self.rect_verde.size = instance.size
        elif hasattr(self, 'rect_negro') and instance == self.contenedor_negro:
            self.rect_negro.pos = instance.pos
            self.rect_negro.size = instance.size

    def on_presionar_boton(self, instance):
        """Añade un Label con texto blanco al contenedor negro"""
        label = Label(
            text=f"Trabajo #{len(self.contenedor_negro.children)}",
            color=(1, 1, 1, 1),  # Texto blanco
            size_hint_y=None,
            height=dp(30),
            font_size=14,
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))

        # Añadir al inicio (arriba) para que nuevos labels aparezcan arriba
        self.contenedor_negro.add_widget(label, index=0)

        # ✅ Hacer crecer el contenedor negro
        self.contenedor_negro.height += dp(30)

        print(f"✅ Label añadido. Nueva altura: {self.contenedor_negro.height:.0f}dp")

if __name__ == '__main__':
    InterfazApp().run()