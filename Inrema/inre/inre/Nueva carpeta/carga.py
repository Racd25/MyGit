from pymongo import MongoClient

# Conexión a MongoDB (ajusta el URI si usas autenticación o conexión remota)
client = MongoClient("mongodb://localhost:27017/")
db = client["Inrema"]
collection = db["MarcasMotores"]

# Lista de marcas únicas (puedes reemplazarla por una carga desde archivo si lo prefieres)
marcas = [
    "ARAUCA CHERRY", "AVA", "AVEO", "BELARUS", "BELARUSO", "BOBCAT", "BOMBA", "CARGO", "CASE", "CAT",
    "CCHERRY", "CHANGAN", "CHERRY", "CHERY", "CHEVRLET", "CHEVROLER", "CHEVROLET", "COLORADO88",
    "COMPRESOR", "CORSA", "CETO", "CRUZ", "CUMINS", "CUMMNIS", "CUMMINS", "DAEWO", "DAEWOO",
    "DAVID BROWR", "DEUTZ", "DEUZ", "DETROIT", "DITROI", "DODGE", "DODGER", "DOMOSA", "DON FENG",
    "DONFEND", "DONGENG", "DONGFENG", "ESPAR", "EXPLORET", "FIAT", "FORD", "FORD NEW HORLLAND",
    "FORD NEW NEW HORLA", "FORDSON", "FREIGHTLINER", "FR", "GALION", "GENESIS", "GREAT WALL",
    "GRAND CHEROKE", "GRAND MURALLA", "GRAND TIGO", "GRAND VITARA", "GS", "HAIMA", "HANSUR MAYER",
    "HIUNDAY", "HINO", "HONDA", "HOWO", "HUSQVARNA", "INTERNACIONAL", "ISUZU", "ISUZO", "IVECO",
    "IZUZO", "JACK", "JCB", "JEEP", "JHON", "JHON DEER", "JHON DEERE", "JHON DERE", "JHONDEERE",
    "JOHN DEERE", "JVC", "KAWASAKI", "KEY", "KIAT", "KIA", "KODIA", "KODIACK", "KTM", "LANDINI",
    "LANDINIS", "LEILA", "LEVI", "LISTEN", "LIMBARDINI", "LOMBARDINI", "LOMBARDINIS", "LOVARDINI",
    "MADAZ", "MAZDA", "MAZVEN", "MASSEY FERGUN", "MARSEY FERGUN", "MATIZ", "MACK", "MACK RENOL",
    "MERCEDEZ", "MERCEDEZ BENZ", "MERCEDES BENZ", "MITSUBISHI", "MITSUBUSHI", "MONTA CARGA",
    "MOTSUBISHI", "MTSUBISHI", "MWM", "NEF", "NEUHOLLAM", "NEW HOLLAND", "NEXT", "NISSA", "NISSAN",
    "NIVA", "NIVAD", "OPEL", "PEUGEOT", "PERKINS", "PLANTA", "RENAULT", "RENOL", "RENOLD", "SHANGHAI",
    "SHIBAURA", "SISU", "SITAER", "SIZU", "SAME", "SUZUKI", "SINOTRUCK", "TERIO", "TOOTA", "TOYOTA",
    "TUFLON", "TUFLO", "VALTRA", "VELARUS", "VELARUZ", "VENALTI", "VENIRRAM", "VERINA", "VOLTE",
    "VOLKSWAGEN", "VOLVO", "WARTSILA", "YANMAR", "YAMAHA", "YAMZ", "ZUSUKI", "ZUZUKI"
]

# Insertar cada marca como documento individual
for marca in marcas:
    collection.insert_one({"nombre": marca})

print(f"Se insertaron {len(marcas)} marcas en la colección 'MarcasMotores'.")