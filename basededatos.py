import sqlite3

class GestorBD:
    def __init__(self, nombre_db="alphatech.db"):
        self.conn = sqlite3.connect(nombre_db)
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                dispositivo TEXT NOT NULL,
                falla TEXT,
                costo REAL,
                estado TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def insertar_orden(self, cliente, dispositivo, falla, costo, estado):
        self.cursor.execute("INSERT INTO ordenes (cliente, dispositivo, falla, costo, estado) VALUES (?, ?, ?, ?, ?)", 
                            (cliente, dispositivo, falla, costo, estado))
        self.conn.commit()
    def obtener_todas(self):
       # Especificamos el orden exacto para que coincida con tu Treeview
        # Seleccionamos todas las columnas en el orden correcto
        self.cursor.execute("SELECT id, cliente, dispositivo, falla, costo, estado, fecha FROM ordenes")
        return self.cursor.fetchall()

    def modificar_estado(self, id_orden, nuevo_estado):
        self.cursor.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, id_orden))
        self.conn.commit()
    def eliminar_orden(self, id_orden):
        # El signo '?' es vital para evitar errores de seguridad
        self.cursor.execute("DELETE FROM ordenes WHERE id = ?", (id_orden,))
        self.conn.commit()
    def buscar_ordenes(self, termino):
        query = f"%{termino}%"
        # Mismo orden que en obtener_todas
        self.cursor.execute("""
            SELECT id, cliente, dispositivo, falla, costo, estado, fecha 
            FROM ordenes 
            WHERE cliente LIKE ? OR dispositivo LIKE ?
        """, (query, query))
        return self.cursor.fetchall()
    def obtener_estadisticas(self):
        # Cuenta cuántas órdenes hay por cada estado
        self.cursor.execute("SELECT estado, COUNT(*) FROM ordenes GROUP BY estado")
        return self.cursor.fetchall()
    def obtener_todo_para_exportar(self):
        # Traemos todo para generar el reporte completo
        self.cursor.execute("SELECT * FROM ordenes")
        return self.cursor.fetchall()
    