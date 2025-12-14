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

# Cargar el archivo .kv
Builder.load_file('inventario/inventariox.kv')
def conectar_mongo2():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client['Inrema']
        return db['Fichas']
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None
