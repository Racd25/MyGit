from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from sqlqueries import QueriesSQLite
from signin.signin import SigninWindow
from admin.admin import AdminWindow


import json
import os
from datetime import datetime, timedelta

# Archivo donde se guarda el estado y la fecha de inicio
ARCHIVO_ESTADO = "estado_variable.json"

def cargar_estado():
    if not os.path.exists(ARCHIVO_ESTADO):
        estado = {
            "valor": True,
            "fecha_inicio": datetime.now()
        }
        guardar_estado(estado)

        return estado
    
    with open(ARCHIVO_ESTADO, 'r') as f:
        estado = json.load(f)
        estado["fecha_inicio"] = datetime.fromisoformat(estado["fecha_inicio"])  # ✅ Aquí se corrige
        return estado

def guardar_estado(estado):
    estado_mod = estado.copy()
    estado_mod["fecha_inicio"] = estado["fecha_inicio"].isoformat()  # ✅ Guardar como string
    with open(ARCHIVO_ESTADO, 'w') as f:
        json.dump(estado_mod, f, indent=4)

def obtener_valor():
    estado = cargar_estado()
    ahora = datetime.now()
    seis_meses = timedelta(days=180)

    if ahora - estado["fecha_inicio"] >= seis_meses:
        if estado["valor"] is True:
            estado["valor"] = False
            guardar_estado(estado)

        return False
    else:

        return True
    
    
class MainWindow(BoxLayout):
    QueriesSQLite.create_tables()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin_widget = AdminWindow()
        self.signin_widget = SigninWindow(self.admin_widget.poner_usuario)  # Pasar directamente a admin
        self.ids.scrn_signin.add_widget(self.signin_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)



class MainApp(App):
    def build(self):
        
        return MainWindow()



if __name__ == "__main__":
    valor_actual = obtener_valor()

    MainApp().run()

    
