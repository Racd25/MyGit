from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from signin.signin import SigninWindow
from admin.admin import AdminWindow
from inventario.inventario import AdminI
from operadores.operadores import AdminO
from datetime import datetime, timedelta

from kivymd.app import MDApp

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        self.admin_widget = AdminWindow()
        self.inventario_widget = AdminI()
        self.operadores_widget = AdminO()


        self.usuario_nivel = None

        def manejar_usuario(usuario):
            nivel = int(usuario.get('nivel', '1'))  
            self.usuario_nivel = nivel
            self.admin_widget.poner_usuario(usuario)
            self.inventario_widget.actualizar_nivel_usuario(nivel)
            self.operadores_widget.actualizar_nivel_usuario(nivel)

        # Crear el widget de login con el callback
        self.signin_widget = SigninWindow(manejar_usuario)

        # Añadir los widgets a sus respectivos Screens
        self.ids.scrn_signin.add_widget(self.signin_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)
        self.ids.scrn_inventario.add_widget(self.inventario_widget)
        self.ids.scrn_operadores.add_widget(self.operadores_widget)

class MainApp(MDApp):
    def build(self):
        
        return MainWindow()


if __name__ == "__main__":

    MainApp().run()