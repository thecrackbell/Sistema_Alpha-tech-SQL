import csv
from datetime import datetime
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from basededatos import GestorBD  # Modulo de BD
from conversor import ConversorMoneda  # Importamos la clase Conversor
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class AlphaTechApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Alpha Tech v5.0 - Profesional SQL")
    self.root.geometry("750x650")

    self.sistema = GestorBD()  # Inicializamos la BD

    self.main_frame = tb.Frame(self.root, padding=20)
    self.main_frame.pack(fill=BOTH, expand=YES)

    tb.Label(
        self.main_frame,
        text="Panel de Gestión SQL",
        font=("Helvetica", 18, "bold"),
    ).pack(pady=10)

    # Botones principales
    self.crear_boton("Registrar Orden", self.abrir_registro)
    self.crear_boton("Registrar Abono", self.registrar_abono)
    self.crear_boton("Ver Reporte", self.mostrar_reporte)
    self.crear_boton("Exportar Reporte (.CSV)", self.exportar_reporte)
    self.crear_boton("Cierre Diario", self.realizar_cierre_caja)
    self.crear_boton("Cierre Mensual", self.realizar_cierre_mensual)
    self.crear_boton("Cerrar", self.cerrar_sistema)

    self.configurar_tabla()
    self.configurar_menu_contextual()
    self.refrescar_tabla()

  def configurar_tabla(self):
    self.search_entry = tb.Entry(self.main_frame, bootstyle="info")
    self.search_entry.pack(fill="x", pady=10)
    self.search_entry.bind("<KeyRelease>", self.filtrar_tabla)

    # Mapeo exacto de las columnas con los datos de SQL
    columnas = (
        "ID",
        "Cliente",
        "Dispositivo",
        "Falla",
        "Costo",
        "Abono",
        "Pendiente",
        "Estado",
        "Fecha",
    )

    self.tree = tb.Treeview(
        self.main_frame, columns=columnas, show="headings", bootstyle="info"
    )

    for col in columnas:
      self.tree.heading(col, text=col)
      self.tree.column(col, width=85, anchor="center")

    self.tree.pack(fill="both", expand=True, pady=10)
    self.tree.bind("<Double-1>", lambda event: self.editar_orden())

  def refrescar_tabla(self):
    for i in self.tree.get_children():
      self.tree.delete(i)
    for fila in self.sistema.obtener_todas():
      self.tree.insert("", "end", values=fila)

  def actualizar_status(self, nuevo_estado):
    seleccion = self.tree.selection()
    if not seleccion:
      return

    id_orden = self.tree.item(seleccion[0], "values")[0]
    self.sistema.modificar_estado(id_orden, nuevo_estado)
    self.refrescar_tabla()

  def eliminar_orden(self):
    seleccion = self.tree.selection()
    if not seleccion:
      return

    id_orden = self.tree.item(seleccion[0], "values")[0]
    if messagebox.askyesno("Confirmar", "¿Eliminar orden?"):
      self.sistema.eliminar_orden(id_orden)
      self.refrescar_tabla()

  def ver_detalles_orden(self):
    seleccion = self.tree.selection()
    if not seleccion:
      return
    id_orden = self.tree.item(seleccion[0], "values")[0]
    messagebox.showinfo("Detalle", f"Mostrando detalles del ID: {id_orden}")

  def configurar_menu_contextual(self):
    self.menu_contextual = tb.Menu(self.root, tearoff=0)
    self.menu_contextual.add_command(
        label="Marcar como Reparado",
        command=lambda: self.actualizar_status("Reparado"),
    )
    self.menu_contextual.add_command(
        label="Marcar como Entregado",
        command=lambda: self.actualizar_status("Entregado"),
    )
    self.menu_contextual.add_separator()
    self.menu_contextual.add_command(
        label="Eliminar Orden", command=self.eliminar_orden
    )

    self.tree.bind("<Button-3>", self.mostrar_menu)

  def mostrar_menu(self, event):
    item = self.tree.identify_row(event.y)
    if item:
      self.tree.selection_set(item)
      self.menu_contextual.post(event.x_root, event.y_root)

  def abrir_registro(self):
    top = tb.Toplevel(self.root)
    top.title("Registrar Nueva Orden")

    entradas = {}
    for campo in ["Cliente", "Dispositivo", "Falla", "Costo"]:
      frame = tb.Frame(top, padding=5)
      frame.pack(fill="x")
      tb.Label(frame, text=campo, width=10).pack(side="left")
      entry = tb.Entry(frame)
      entry.pack(side="right", expand=True, fill="x")
      entradas[campo] = entry

    self.ruta_foto_temp = ""

    def elegir():
      self.ruta_foto_temp = self.seleccionar_foto()

    tb.Button(
        top, text="Seleccionar Foto del Equipo", command=elegir
    ).pack(pady=5)

    def guardar():
      cliente = entradas["Cliente"].get().strip()
      dispositivo = entradas["Dispositivo"].get().strip()
      falla = entradas["Falla"].get().strip()
      costo_str = entradas["Costo"].get().strip()

      if not cliente or not dispositivo or not falla or not costo_str:
        messagebox.showwarning(
            "Campos Vacíos", "Por favor, completa todos los campos."
        )
        return

      try:
        costo = float(costo_str)
      except ValueError:
        messagebox.showerror(
            "Error de Formato",
            "Por favor, ingresa un valor válido para el costo.",
        )
        return

      ruta_destino = ""
      if self.ruta_foto_temp:
        if not os.path.exists("fotos_equipos"):
          os.makedirs("fotos_equipos")
        nombre_archivo = (
            f"foto_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        )
        ruta_destino = os.path.join("fotos_equipos", nombre_archivo)
        shutil.copy(self.ruta_foto_temp, ruta_destino)

      # Se especifica abono inicial = 0.0 y estado por defecto
      self.sistema.insertar_orden(
          cliente,
          dispositivo,
          falla,
          costo,
          abono=0.0,
          estado="En espera",
          ruta_foto=ruta_destino,
      )

      self.refrescar_tabla()
      top.destroy()

    tb.Button(
        top, text="Guardar", command=guardar, bootstyle="success"
    ).pack(pady=10)

  def crear_boton(self, texto, comando):
    tb.Button(
        self.main_frame,
        text=texto,
        command=comando,
        width=30,
        bootstyle="info",
    ).pack(pady=4)

  def filtrar_tabla(self, event):
    query = self.search_entry.get()
    for i in self.tree.get_children():
      self.tree.delete(i)

    resultados = self.sistema.buscar_ordenes(query)
    for fila in resultados:
      self.tree.insert("", "end", values=fila)

  def mostrar_reporte(self):
    datos = self.sistema.obtener_estadisticas()
    mensaje = "Resumen de reparaciones:\n"
    for estado, cantidad in datos:
      mensaje += f"- {estado}: {cantidad}\n"

    messagebox.showinfo("Reporte de Taller", mensaje)

  def exportar_reporte(self):
    datos = self.sistema.obtener_todo_para_exportar()
    if not datos:
      messagebox.showwarning("Exportar", "No hay datos para exportar.")
      return

    try:
      with open(
          "reporte_taller.csv", "w", newline="", encoding="utf-8-sig"
      ) as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "ID",
            "Cliente",
            "Dispositivo",
            "Falla",
            "Costo",
            "Abono",
            "Estado",
            "Fecha",
            "Foto",
        ])
        writer.writerows(datos)

      messagebox.showinfo(
          "Éxito",
          "Reporte guardado como 'reporte_taller.csv'.\nÁbrelo con Excel.",
      )
    except Exception as e:
      messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

  def editar_orden(self):
    seleccion = self.tree.selection()
    if not seleccion:
      messagebox.showwarning("Atención", "Selecciona una orden de la tabla.")
      return

    valores = self.tree.item(seleccion[0], "values")
    if not valores:
      return

    id_orden = valores[0]
    # Posición 9 es la ruta de la foto en la tupla devuelta por SQL
    self.ruta_foto_edicion = valores[9] if len(valores) > 9 else ""

    top = tb.Toplevel(self.root)
    top.title(f"Editando Orden #{id_orden}")
    top.geometry("400x620")

    entradas = {}
    campos = ["Cliente", "Dispositivo", "Falla", "Costo", "Abono", "Estado"]
    valores_actuales = [
        valores[1],  # Cliente
        valores[2],  # Dispositivo
        valores[3],  # Falla
        valores[4],  # Costo
        valores[5],  # Abono
        valores[7],  # Estado
    ]

    for i, campo in enumerate(campos):
      frame = tb.Frame(top, padding=5)
      frame.pack(fill="x")
      tb.Label(frame, text=campo, width=12).pack(side="left")
      entry = tb.Entry(frame)
      entry.insert(0, valores_actuales[i])
      entry.pack(side="right", expand=True, fill="x")
      entradas[campo] = entry

    lbl_img = tb.Label(top)
    lbl_img.pack(pady=5)

    def actualizar_vista_imagen(ruta):
      if ruta and os.path.exists(ruta):
        img = Image.open(ruta)
        img = img.resize((130, 130))
        foto_tk = ImageTk.PhotoImage(img)
        lbl_img.config(image=foto_tk, text="")
        lbl_img.image = foto_tk
      else:
        lbl_img.config(image="", text="[ Sin foto registrada ]")

    actualizar_vista_imagen(self.ruta_foto_edicion)

    def cambiar_foto():
      nueva_foto = self.seleccionar_foto()
      if nueva_foto:
        nombre_archivo = f"foto_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        ruta_destino = os.path.join("fotos_equipos", nombre_archivo)
        shutil.copy(nueva_foto, ruta_destino)
        self.ruta_foto_edicion = ruta_destino
        actualizar_vista_imagen(self.ruta_foto_edicion)

    tb.Button(
        top,
        text="Cambiar / Agregar Foto",
        command=cambiar_foto,
        bootstyle="secondary-outline",
    ).pack(pady=5)

    def guardar_cambios():
      cliente = entradas["Cliente"].get().strip()
      dispositivo = entradas["Dispositivo"].get().strip()
      falla = entradas["Falla"].get().strip()
      costo_str = entradas["Costo"].get().strip()
      abono_str = entradas["Abono"].get().strip()
      estado = entradas["Estado"].get().strip()

      if (
          not cliente
          or not dispositivo
          or not falla
          or not costo_str
          or not abono_str
          or not estado
      ):
        messagebox.showwarning(
            "Campos Vacíos", "Por favor, no dejes ningún campo en blanco."
        )
        return

      try:
        costo = float(costo_str)
        abono = float(abono_str)
      except ValueError:
        messagebox.showerror(
            "Error de Formato",
            "El costo y el abono deben ser números válidos.",
        )
        return

      self.sistema.actualizar_orden(
          id_orden,
          cliente,
          dispositivo,
          falla,
          costo,
          abono,
          estado,
          self.ruta_foto_edicion,
      )

      self.refrescar_tabla()
      top.destroy()
      messagebox.showinfo("Éxito", "Orden actualizada correctamente.")

    tb.Button(
        top,
        text="Guardar Cambios",
        command=guardar_cambios,
        bootstyle="warning",
    ).pack(pady=10)

  def realizar_cierre_caja(self):
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    total_bs = self.sistema.obtener_total_recaudado_por_fecha(fecha_hoy)

    if total_bs == 0:
      messagebox.showinfo(
          "Cierre de Caja",
          f"No hay ingresos registrados para hoy ({fecha_hoy}).",
      )
      return

    top = tb.Toplevel(self.root)
    top.title(f"Cierre de Caja - {fecha_hoy}")
    top.geometry("350x280")
    top.grab_set()

    tb.Label(
        top,
        text=f"Total Recaudado: {total_bs:,.2f} Bs",
        font=("Helvetica", 10, "bold"),
    ).pack(pady=10)

    tb.Label(top, text="Tasa Dólar (BCV):").pack()
    entry_bcv = tb.Entry(top)
    entry_bcv.pack(pady=5)

    tb.Label(top, text="Tasa Dólar (USDT):").pack()
    entry_usdt = tb.Entry(top)
    entry_usdt.pack(pady=5)

    def procesar_cierre():
      try:
        tasa_bcv = float(entry_bcv.get().replace(",", "."))
        tasa_usdt = float(entry_usdt.get().replace(",", "."))

        if tasa_bcv <= 0 or tasa_usdt <= 0:
          raise ValueError

        bs_total = total_bs * tasa_bcv
        total_usd = bs_total / tasa_usdt

        mensaje = (
            f"--- CIERRE DE CAJA ({fecha_hoy}) ---\n\n"
            f"Total en Bolívares: {bs_total:,.2f} Bs\n"
            f"Tasa BCV: {tasa_bcv:,.2f}\n"
            f"Tasa USDT: {tasa_usdt:,.2f}\n"
            f"----------------------------\n"
            f"Total en USDT: ${total_usd:,.2f}"
        )

        messagebox.showinfo("Reporte Final", mensaje)
        top.destroy()
      except ValueError:
        messagebox.showerror(
            "Error",
            "Por favor, ingresa tasas numéricas válidas y mayores a cero.",
        )

    tb.Button(
        top, text="Calcular Cierre", command=procesar_cierre, bootstyle="success"
    ).pack(pady=20)

  def realizar_cierre_mensual(self):
    mes_actual = datetime.now().strftime("%m")
    anio_actual = datetime.now().strftime("%Y")
    total_bs = self.sistema.obtener_total_recaudado_por_mes(
        mes_actual, anio_actual
    )

    if total_bs == 0:
      messagebox.showinfo(
          "Cierre Mensual", "No hay ingresos registrados este mes."
      )
      return

    top = tb.Toplevel(self.root)
    top.title("Tasas para Cierre Mensual")
    top.geometry("350x250")
    top.grab_set()

    tb.Label(
        top, text=f"Total Bs: {total_bs:,.2f}", font=("Helvetica", 10, "bold")
    ).pack(pady=10)

    tb.Label(top, text="Tasa BCV:").pack()
    entry_bcv = tb.Entry(top)
    entry_bcv.pack(pady=5)

    tb.Label(top, text="Tasa USDT:").pack()
    entry_usdt = tb.Entry(top)
    entry_usdt.pack(pady=5)

    def procesar_tasas():
      try:
        tasa_bcv = float(entry_bcv.get().replace(",", "."))
        tasa_usdt = float(entry_usdt.get().replace(",", "."))

        bs_total = total_bs * tasa_bcv
        total_usd = bs_total / tasa_usdt

        mensaje = (
            f"--- RESUMEN MENSUAL ---\n\n"
            f"Total Bs: {total_bs:,.2f} Bs\n"
            f"Total en BCV: ${bs_total:,.2f}\n"
            f"Total en USDT: ${total_usd:,.2f}"
        )

        messagebox.showinfo("Reporte Final", mensaje)
        top.destroy()
      except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa tasas válidas.")

    tb.Button(
        top, text="Calcular", command=procesar_tasas, bootstyle="success"
    ).pack(pady=20)

  def seleccionar_foto(self):
    archivo = filedialog.askopenfilename(
        filetypes=[("Imágenes", "*.jpg *.png *.jpeg")]
    )
    if archivo:
      if not os.path.exists("fotos_equipos"):
        os.makedirs("fotos_equipos")
      return archivo
    return ""

  def hacer_backup(self):
    if os.path.exists("alphatech.db"):
      shutil.copy(
          "alphatech.db",
          f"alphatech_backup_{datetime.now().strftime('%Y%m%d')}.db",
      )
      messagebox.showinfo(
          "Backup", "Copia de seguridad creada correctamente."
      )
    else:
      messagebox.showwarning(
          "Backup", "No se encontró el archivo de base de datos."
      )

  def cerrar_sistema(self):
    archivo_fecha = "ultimo_backup.txt"
    fecha_hoy = datetime.now()

    # 1. Leer cuándo fue el último backup
    ultima_fecha = None
    if os.path.exists(archivo_fecha):
      try:
        with open(archivo_fecha, "r") as f:
          contenido = f.read().strip()
          if contenido:
            ultima_fecha = datetime.strptime(contenido, "%Y-%m-%d")
      except Exception:
        ultima_fecha = None

    # 2. Verificar si han pasado 7 días o más
    if ultima_fecha is None or (fecha_hoy - ultima_fecha).days >= 7:
      if not os.path.exists("backups"):
        os.makedirs("backups")

      nombre_backup = f"alphatech_backup_{fecha_hoy.strftime('%Y-%m-%d')}.db"
      if os.path.exists("alphatech.db"):
        shutil.copy("alphatech.db", os.path.join("backups", nombre_backup))

      # 3. Guardar la fecha de hoy
      with open(archivo_fecha, "w") as f:
        f.write(fecha_hoy.strftime("%Y-%m-%d"))

      print("Backup semanal realizado con éxito.")
    else:
      print("Aún no es necesario realizar el backup semanal.")

    self.root.destroy()

  def registrar_abono(self):
    seleccion = self.tree.selection()
    if not seleccion:
      messagebox.showwarning(
          "Atención",
          "Selecciona una orden de la lista para registrar un abono.",
      )
      return

    valores = self.tree.item(seleccion[0], "values")

    # Mapeo ajustado: ID[0], Cliente[1], Costo[4], Abono[5], Pendiente[6]
    id_orden = valores[0]
    cliente = valores[1]
    costo_total = float(valores[4])
    abono_actual = float(valores[5]) if valores[5] else 0.0
    pendiente_usd = float(valores[6])

    if pendiente_usd <= 0:
      messagebox.showinfo(
          "Orden Pagada",
          f"La orden #{id_orden} ya se encuentra pagada en su totalidad.",
      )
      return

    # Ventana de diálogo
    top = tb.Toplevel(self.root)
    top.title(f"Registrar Abono - Orden #{id_orden}")
    top.geometry("420x520")
    top.grab_set()

    # Información básica
    tb.Label(
        top, text=f"Cliente: {cliente}", font=("Helvetica", 11, "bold")
    ).pack(pady=(10, 2))
    tb.Label(
        top,
        text=(
            f"Costo Total: ${costo_total:,.2f} | Abonado: ${abono_actual:,.2f}"
        ),
    ).pack()

    lbl_pendiente = tb.Label(
        top,
        text=f"Saldo Pendiente: ${pendiente_usd:,.2f}",
        bootstyle="danger",
        font=("Helvetica", 10, "bold"),
    )
    lbl_pendiente.pack(pady=5)

    # Selección de Moneda
    tb.Label(top, text="Moneda del Pago:").pack(pady=(10, 2))
    moneda_var = tk.StringVar(value="USD")

    frame_radio = tb.Frame(top)
    frame_radio.pack()

    # Entradas de texto
    tb.Label(top, text="Monto abonado:").pack(pady=(10, 2))
    entry_monto = tb.Entry(top)
    entry_monto.pack(pady=2)

    lbl_tasa = tb.Label(top, text="Tasa del día (Bs / $):")
    lbl_tasa.pack(pady=(5, 2))
    entry_tasa = tb.Entry(top)
    entry_tasa.pack(pady=2)

    # Etiqueta para mostrar la conversión en vivo
    lbl_calculo = tb.Label(
        top,
        text="",
        font=("Helvetica", 9, "italic"),
        bootstyle="info",
        justify="center",
    )
    lbl_calculo.pack(pady=10)

    def toggle_moneda():
      if moneda_var.get() == "USD":
        entry_tasa.config(state="disabled")
      else:
        entry_tasa.config(state="normal")
      calcular_conversion()

    tb.Radiobutton(
        frame_radio,
        text="Dólares ($)",
        variable=moneda_var,
        value="USD",
        command=toggle_moneda,
    ).pack(side="left", padx=10)
    tb.Radiobutton(
        frame_radio,
        text="Bolívares (Bs)",
        variable=moneda_var,
        value="BS",
        command=toggle_moneda,
    ).pack(side="left", padx=10)

    def calcular_conversion(*args):
      try:
        monto = float(entry_monto.get().replace(",", "."))
        moneda = moneda_var.get()

        if moneda == "USD":
          monto_usd = monto
          restante = max(0.0, pendiente_usd - monto_usd)

          if entry_tasa.get():
            tasa = float(entry_tasa.get().replace(",", "."))
            lbl_calculo.config(
                text=(
                    f"Equivalente: {monto_usd * tasa:,.2f} Bs\nNuevo saldo:"
                    f" ${restante:,.2f} ({restante * tasa:,.2f} Bs)"
                )
            )
          else:
            lbl_calculo.config(
                text=f"Nuevo saldo restante: ${restante:,.2f}"
            )

        else:  # Pago en Bolívares
          tasa = float(entry_tasa.get().replace(",", "."))
          if tasa <= 0:
            lbl_calculo.config(text="La tasa debe ser mayor a 0")
            return

          monto_usd = monto * tasa
          restante_usd = max(0.0, pendiente_usd - monto_usd)
          restante_bs = restante_usd * tasa

          lbl_calculo.config(
              text=(
                  f"Abono equivalente a: ${monto_usd:,.2f} USD\nNuevo saldo"
                  f" restante: ${restante_usd:,.2f} USD ({restante_bs:,.2f} Bs)"
              )
          )
      except ValueError:
        lbl_calculo.config(text="")

    entry_monto.bind("<KeyRelease>", calcular_conversion)
    entry_tasa.bind("<KeyRelease>", calcular_conversion)
    toggle_moneda()

    def procesar_guardado():
      try:
        monto = float(entry_monto.get().replace(",", "."))
        if monto <= 0:
          messagebox.showerror("Error", "El monto debe ser mayor a cero.")
          return

        if moneda_var.get() == "USD":
          monto_usd = monto
        else:
          tasa = float(entry_tasa.get().replace(",", "."))
          if tasa <= 0:
            raise ValueError
          monto_usd = monto / tasa

        if monto_usd > (pendiente_usd + 0.05):
          messagebox.showwarning(
              "Atención",
              f"El abono (${monto_usd:,.2f}) sobrepasa el saldo pendiente"
              f" (${pendiente_usd:,.2f}).",
          )
          return

        self.sistema.agregar_abono(id_orden, monto_usd)
        self.refrescar_tabla()

        messagebox.showinfo(
            "Abono Exitoso",
            f"Se registraron ${monto_usd:,.2f} USD abonados a la orden"
            f" #{id_orden}.",
        )
        top.destroy()

      except ValueError:
        messagebox.showerror(
            "Error", "Ingresa montos y tasa numéricos válidos."
        )

    tb.Button(
        top,
        text="Confirmar Abono",
        command=procesar_guardado,
        bootstyle="success",
    ).pack(pady=15)


if __name__ == "__main__":
  root = tb.Window(themename="superhero")
  app = AlphaTechApp(root)
  root.mainloop()