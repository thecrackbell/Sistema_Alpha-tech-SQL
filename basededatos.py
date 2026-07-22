import sqlite3
from conversor import ConversorMoneda  # Importamos la clase Conversor

class GestorBD:

  def __init__(self, nombre_db="alphatech.db"):
    self.conn = sqlite3.connect(nombre_db)
    self.cursor = self.conn.cursor()
    self.crear_tabla()

  def crear_tabla(self):
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                dispositivo TEXT NOT NULL,
                falla TEXT,
                costo REAL,
                abono REAL DEFAULT 0.0,
                estado TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ruta_foto TEXT
            )
        """)

    # Migración de seguridad por si la BD ya existía sin estas columnas
    for columna, tipo in [("abono", "REAL DEFAULT 0.0"), ("ruta_foto", "TEXT")]:
      try:
        self.cursor.execute(f"ALTER TABLE ordenes ADD COLUMN {columna} {tipo}")
      except sqlite3.OperationalError:
        pass  # La columna ya existe

    self.conn.commit()

  def insertar_orden(
      self,
      cliente,
      dispositivo,
      falla,
      costo,
      abono=0.0,
      estado="En espera",
      ruta_foto="",
  ):
    self.cursor.execute(
        """
            INSERT INTO ordenes (cliente, dispositivo, falla, costo, abono, estado, ruta_foto) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (cliente, dispositivo, falla, costo, abono, estado, ruta_foto),
    )
    self.conn.commit()

  def obtener_todas(self):
    # SQL calcula (costo - abono) dinámicamente como 'pendiente'
    self.cursor.execute("""
            SELECT id, cliente, dispositivo, falla, costo, abono, (costo - abono) AS pendiente, estado, fecha, ruta_foto 
            FROM ordenes
        """)
    return self.cursor.fetchall()

  def actualizar_orden(
      self,
      id_orden,
      cliente,
      dispositivo,
      falla,
      costo,
      abono,
      estado,
      ruta_foto,
  ):
    self.cursor.execute(
        """
            UPDATE ordenes 
            SET cliente = ?, dispositivo = ?, falla = ?, costo = ?, abono = ?, estado = ?, ruta_foto = ?
            WHERE id = ?
        """,
        (
            cliente,
            dispositivo,
            falla,
            costo,
            abono,
            estado,
            ruta_foto,
            id_orden,
        ),
    )
    self.conn.commit()

  def buscar_ordenes(self, termino):
    query = f"%{termino}%"
    self.cursor.execute(
        """
            SELECT id, cliente, dispositivo, falla, costo, abono, (costo - abono) AS pendiente, estado, fecha, ruta_foto 
            FROM ordenes 
            WHERE cliente LIKE ? OR dispositivo LIKE ?
        """,
        (query, query),
    )
    return self.cursor.fetchall()

  def agregar_abono(self, id_orden, monto_abono_usd):
    """Suma un nuevo abono en USD al saldo acumulado de la orden."""
    self.cursor.execute(
        """
            UPDATE ordenes 
            SET abono = COALESCE(abono, 0) + ? 
            WHERE id = ?
        """,
        (monto_abono_usd, id_orden),
    )
    self.conn.commit()  # <-- Corregido (antes decia self.conexion)

  def modificar_estado(self, id_orden, nuevo_estado):
    self.cursor.execute(
        "UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, id_orden)
    )
    self.conn.commit()

  def eliminar_orden(self, id_orden):
    self.cursor.execute("DELETE FROM ordenes WHERE id = ?", (id_orden,))
    self.conn.commit()

  def obtener_estadisticas(self):
    self.cursor.execute("SELECT estado, COUNT(*) FROM ordenes GROUP BY estado")
    return self.cursor.fetchall()

  def obtener_todo_para_exportar(self):
    self.cursor.execute("SELECT * FROM ordenes")
    return self.cursor.fetchall()

  def obtener_total_recaudado_por_mes(self, mes, anio):
    self.cursor.execute(
        """
            SELECT SUM(costo) FROM ordenes 
            WHERE strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?
        """,
        (mes, anio),
    )
    resultado = self.cursor.fetchone()[0]
    return resultado if resultado else 0.0

  def obtener_total_recaudado_por_fecha(self, fecha):
    self.cursor.execute(
        """
            SELECT SUM(costo) FROM ordenes 
            WHERE DATE(fecha) = ?
        """,
        (fecha,),
    )
    resultado = self.cursor.fetchone()[0]
    return resultado if resultado else 0.0



