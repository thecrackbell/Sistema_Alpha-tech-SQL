import sqlite3

class GestorBD:
    def __init__(self, nombre_db="alphatech.db"):
        self.conn = sqlite3.connect(nombre_db)
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        # Definimos nuestra tabla con los campos necesarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                dispositivo TEXT NOT NULL,
                estado TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def insertar_orden(self, cliente, dispositivo, estado):
        self.cursor.execute("INSERT INTO ordenes (cliente, dispositivo, estado) VALUES (?, ?, ?)", 
                            (cliente, dispositivo, estado))
        self.conn.commit()

    def obtener_todas(self):
        self.cursor.execute("SELECT * FROM ordenes")
        return self.cursor.fetchall()

    def modificar_estado(self, id_orden, nuevo_estado):
        self.cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, id_orden))
        self.conn.commit()