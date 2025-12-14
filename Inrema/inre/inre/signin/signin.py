from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from sqlqueries import QueriesSQLite
from kivy.config import Config
from pymongo import MongoClient





Builder.load_file('signin/signin.kv')

class SigninWindow(BoxLayout):
    def __init__(self, poner_usuario_callback, **kwargs):
        super().__init__(**kwargs)
        self.poner_usuario = poner_usuario_callback
        # Conexión a MongoDB (local por defecto)
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['Inrema']
        self.collection = self.db['users']

    def verificar_usuario(self, username, password):
        # Validación de campos vacíos
        if username == '' or password == '':
            self.ids.signin_notificacion.text = 'Falta nombre de usuario y/o contraseña'
            return

        try:
            # Buscar el usuario en la colección 'users'
            user = self.collection.find_one({"username": username})

            if user:
                # Verificar contraseña
                if user.get("password") == password:
                    # Limpiar campos
                    self.ids.username.text = ''
                    self.ids.password.text = ''
                    self.ids.signin_notificacion.text = ''

                    # Cambiar de pantalla (suponiendo que usas ScreenManager)
                    self.parent.parent.current = 'admin'

                    # Llamar callback con los datos del usuario
                    usuario_data = {
                        'nombre': user.get('nombre', ''),
                        'username': user['username'],
                        'password': user['password'],  # Opcional: evita pasarla si no es necesario
                        'tipo': user.get('tipo', 'usuario')  # Valor por defecto
                    }
                    self.poner_usuario(usuario_data)
                else:
                    self.ids.signin_notificacion.text = 'Usuario o contraseña incorrecta'
            else:
                self.ids.signin_notificacion.text = 'Usuario o contraseña incorrecta'

        except Exception as e:
            print(f"Error al conectar con MongoDB: {e}")
            self.ids.signin_notificacion.text = 'Error de conexión con la base de datos'


class SigninAppx(App):
    def build(self):
        return SigninWindow()

if __name__ == "__main__":
    SigninAppx().run()