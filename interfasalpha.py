import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb 
from ttkbootstrap.constants import *
from basededatos import GestorBD # Solo necesitamos la BD
import csv # Asegúrate de importar esto al principio de tu archivo
from tkinter import filedialog
import shutil
import os   
from tkinter import simpledialog
from datetime import datetime
from PIL import Image, ImageTk

class AlphaTechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alpha Tech v5.0 - Profesional SQL")
        self.root.geometry("600x600")
        
        self.sistema = GestorBD() # Inicializamos la BD
        
        self.main_frame = tb.Frame(self.root, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)

        tb.Label(self.main_frame, text="Panel de Gestión SQL", font=("Helvetica", 18, "bold")).pack(pady=10)
        # ¡AQUÍ ESTÁ EL TRUCO! Debes llamar a los botones, si no, no aparecerán
        self.crear_boton("Registrar Orden", self.abrir_registro)
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
        # Aquí conectaremos el filtro SQL en breve
        self.search_entry.bind('<KeyRelease>', self.filtrar_tabla)
        self.tree = tb.Treeview(self.main_frame, columns=("ID", "Cliente", "Dispositivo","Falla", "Costo", "Estado", "Fecha"), show="headings", bootstyle="info")
        for col in ("ID", "Cliente", "Dispositivo", "Falla", "Costo", "Estado", "Fecha"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True, pady=10)
        
        self.tree.bind("<Double-1>", lambda event: self.editar_orden())

    def refrescar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in self.sistema.obtener_todas():
            self.tree.insert("", "end", values=fila)

    def actualizar_status(self, nuevo_estado):
        # Esta función usa el método modificar_estado de tu GestorBD
        seleccion = self.tree.selection()
        if not seleccion: 
            return
        
        id_orden = self.tree.item(seleccion[0], "values")[0]
        self.sistema.modificar_estado(id_orden, nuevo_estado)
        self.refrescar_tabla()

    def eliminar_orden(self):
        # Esta función usa el método eliminar_orden de tu GestorBD
        seleccion = self.tree.selection()
        if not seleccion: 
            return
        
        id_orden = self.tree.item(seleccion[0], "values")[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar orden?"):
            self.sistema.eliminar_orden(id_orden)
            self.refrescar_tabla()

    def ver_detalles_orden(self):
        # Nota: En tu database.py, asegúrate de tener un método 'buscar_por_id'
        seleccion = self.tree.selection()
        if not seleccion: 
            return
        id_orden = self.tree.item(seleccion[0], "values")[0]
        
        # Aquí llamarías a: self.sistema.buscar_por_id(id_orden)
        messagebox.showinfo("Detalle", f"Mostrando detalles del ID: {id_orden}")
    def configurar_menu_contextual(self):
        # Creamos el menú que aparecerá al hacer clic derecho
        self.menu_contextual = tb.Menu(self.root, tearoff=0)
        self.menu_contextual.add_command(label="Marcar como Reparado", 
                                         command=lambda: self.actualizar_status("Reparado"))
        self.menu_contextual.add_command(label="Marcar como Entregado", 
                                         command=lambda: self.actualizar_status("Entregado"))
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="Eliminar Orden", 
                                         command=self.eliminar_orden)
        
        # Vinculamos el clic derecho (Button-3) a la tabla
        self.tree.bind("<Button-3>", self.mostrar_menu)

    def mostrar_menu(self, event):
        # Identifica la fila donde hiciste clic
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item) # Selecciona la fila
            self.menu_contextual.post(event.x_root, event.y_root) # Muestra el menú
    def abrir_registro(self):
        # Esta función llama a tu base de datos para crear la nueva orden
        top = tb.Toplevel(self.root)
        top.title("Registrar Nueva Orden")
        
        # Campos de entrada
        entradas = {}
        for campo in ["Cliente", "Dispositivo", "Falla", "Costo"]:
            frame = tb.Frame(top, padding=5)
            frame.pack(fill="x")
            tb.Label(frame, text=campo, width=10).pack(side="left")
            entry = tb.Entry(frame)
            entry.pack(side="right", expand=True, fill="x")
            entradas[campo] = entry
        self.ruta_foto_temp = ""
        def elegir(): self.ruta_foto_temp = self.seleccionar_foto()
        tb.Button(top, text="Seleccionar Foto del Equipo", command=elegir).pack(pady=5)
        
        def guardar():
            # 1. Obtenemos los valores
            cliente = entradas["Cliente"].get().strip()
            dispositivo = entradas["Dispositivo"].get().strip()
            falla = entradas["Falla"].get().strip()
            costo_str = entradas["Costo"].get().strip()
            
            # 2. VALIDACIÓN
            if not cliente or not dispositivo or not falla or not costo_str:
                messagebox.showwarning("Campos Vacíos", "Por favor, completa todos los campos.")
                return 
            
            # 3. Conversión de costo
            try:
                costo = float(costo_str)
            except ValueError:
                messagebox.showerror("Error de Formato", "Por favor, ingresa un valor válido para el costo.")
                return

            # 4. Procesamiento de imagen
            ruta_destino = ""
            if self.ruta_foto_temp:
                if not os.path.exists("fotos_equipos"):
                    os.makedirs("fotos_equipos")
                nombre_archivo = f"foto_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                ruta_destino = os.path.join("fotos_equipos", nombre_archivo)
                shutil.copy(self.ruta_foto_temp, ruta_destino)
            
            # 5. UNA SOLA INSERCIÓN
            self.sistema.insertar_orden(cliente, dispositivo, falla, costo, "En espera", ruta_destino)
            
            # 6. Actualizamos y cerramos
            self.refrescar_tabla()
            top.destroy()
            
        tb.Button(top, text="Guardar", command=guardar, bootstyle="success").pack(pady=10)
    def crear_boton(self, texto, comando):
        # Nota: aquí también usamos 'self.main_frame' en lugar de 'self.root'
        tb.Button(self.main_frame, text=texto, command=comando, width=30, bootstyle="info").pack(pady=5)
        
    def filtrar_tabla(self, event):
        query = self.search_entry.get()
        # 1. Limpiamos la tabla
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # 2. Obtenemos datos filtrados desde SQL
        resultados = self.sistema.buscar_ordenes(query)
        
        # 3. Insertamos los resultados
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
            # Usamos el modo 'w' (write) y newline='' para que Excel no deje filas vacías
            with open("reporte_taller.csv", "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=';') # <--- ESTA ES LA CLAVE
                # Escribimos los encabezados de las columnas
                writer.writerow(["ID", "Cliente", "Dispositivo", "Estado", "Fecha"])
                # Escribimos todas las filas de la base de datos
                writer.writerows(datos)
        
            messagebox.showinfo("Éxito", "Reporte guardado como 'reporte_taller.csv'.\nÁbrelo con Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")
    def editar_orden(self):
        # 1. Verificar si hay algo seleccionado
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una orden de la tabla.")
            return
        
        # 2. Obtener los valores de la fila
        valores = self.tree.item(seleccion[0], 'values')
        if not valores:
            return

        id_orden = valores[0]
        
        # 3. Crear UNA SOLA ventana de edición
        top = tb.Toplevel(self.root)
        top.title(f"Editando Orden #{id_orden}")
        
        entradas = {}
        campos = ["Cliente", "Dispositivo", "Falla", "Costo", "Estado"]
        valores_actuales = [valores[1], valores[2], valores[3], valores[4], valores[5]]
        
        for i, campo in enumerate(campos):
            frame = tb.Frame(top, padding=5)
            frame.pack(fill="x")
            tb.Label(frame, text=campo, width=10).pack(side="left")
            entry = tb.Entry(frame)
            entry.insert(0, valores_actuales[i]) # Precarga del dato
            entry.pack(side="right", expand=True, fill="x")
            entradas[campo] = entry
        ruta_img = valores[7] 
        if ruta_img and os.path.exists(ruta_img):
            img = Image.open(ruta_img)
            img = img.resize((150, 150))
            foto_tk = ImageTk.PhotoImage(img)
            lbl_img = tb.Label(top, image=foto_tk)
            lbl_img.image = foto_tk # ¡Indispensable para que se vea la imagen!
            lbl_img.pack()
        
        # 4. Función interna para guardar
        def guardar_cambios():
            self.sistema.actualizar_orden(
                id_orden,
                entradas["Cliente"].get(),
                entradas["Dispositivo"].get(),
                entradas["Falla"].get(),
                entradas["Costo"].get(),
                entradas["Estado"].get(),
                ruta_img  # Mantener la ruta de la foto actual
            )
            self.refrescar_tabla()
            top.destroy()
            messagebox.showinfo("Éxito", "Orden actualizada correctamente.")
            
        tb.Button(top, text="Guardar Cambios", command=guardar_cambios, bootstyle="warning").pack(pady=10)
    def realizar_cierre_caja(self):
        # 1. Obtener fecha de hoy
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        total_bs = self.sistema.obtener_total_recaudado_por_fecha(fecha_hoy)
        
        if total_bs == 0:
            messagebox.showinfo("Cierre de Caja", f"No hay ingresos registrados para hoy ({fecha_hoy}).")
            return
        
        # 2. Crear ventana personalizada para las tasas
        top = tb.Toplevel(self.root)
        top.title(f"Cierre de Caja - {fecha_hoy}")
        top.geometry("350x280")
        top.grab_set()

        tb.Label(top, text=f"Total Recaudado: {total_bs:,.2f} Bs", font=("Helvetica", 10, "bold")).pack(pady=10)

        # Campos de entrada
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
                
                # Lógica de cálculo
                bs_total = total_bs * tasa_bcv
                total_usd = bs_total / tasa_usdt
                
                mensaje = (f"--- CIERRE DE CAJA ({fecha_hoy}) ---\n\n"
                           f"Total en Bolívares: {bs_total:,.2f} Bs\n"
                           f"Tasa BCV: {tasa_bcv:,.2f}\n"
                           f"Tasa USDT: {tasa_usdt:,.2f}\n"
                           f"----------------------------\n"
                           f"Total en USDT: ${total_usd:,.2f}")
                
                messagebox.showinfo("Reporte Final", mensaje)
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingresa tasas numéricas válidas y mayores a cero.")

        tb.Button(top, text="Calcular Cierre", command=procesar_cierre, bootstyle="success").pack(pady=20)
    def realizar_cierre_mensual(self):
        mes_actual = datetime.now().strftime('%m')
        anio_actual = datetime.now().strftime('%Y')
        total_bs = self.sistema.obtener_total_recaudado_por_mes(mes_actual, anio_actual)
        
        if total_bs == 0:
            messagebox.showinfo("Cierre Mensual", "No hay ingresos registrados este mes.")
            return

        # 1. Crear ventana personalizada
        top = tb.Toplevel(self.root)
        top.title("Tasas para Cierre Mensual")
        top.geometry("350x250")
        top.grab_set() # Bloquea la ventana principal hasta cerrar esta

        tb.Label(top, text=f"Total Bs: {total_bs:,.2f}", font=("Helvetica", 10, "bold")).pack(pady=10)

        # Campos de entrada
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
                
                mensaje = (f"--- RESUMEN MENSUAL ---\n\n"
                           f"Total Bs: {total_bs:,.2f} Bs\n"
                           f"Total en BCV: ${bs_total:,.2f}\n"
                           f"Total en USDT: ${total_usd:,.2f}")
                
                messagebox.showinfo("Reporte Final", mensaje)
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingresa tasas válidas.")

        tb.Button(top, text="Calcular", command=procesar_tasas, bootstyle="success").pack(pady=20)
    def seleccionar_foto(self):
        archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
        if archivo:
            if not os.path.exists("fotos_equipos"):
                os.makedirs("fotos_equipos")
            return archivo
        return ""
    def hacer_backup(self):
        shutil.copy("alphatech.db", f"alphatech_backup_{datetime.now().strftime('%Y%m%d')}.db")
        messagebox.showinfo("Backup", "Copia de seguridad creada correctamente.")
   


    def cerrar_sistema(self):
        archivo_fecha = "ultimo_backup.txt"
        fecha_hoy = datetime.now()
    
    # 1. Leer cuándo fue el último backup
        ultima_fecha = None
        if os.path.exists(archivo_fecha):
         with open(archivo_fecha, "r") as f:
                ultima_fecha = datetime.strptime(f.read().strip(), "%Y-%m-%d")

        # 2. Verificar si han pasado 7 días o más
        if ultima_fecha is None or (fecha_hoy - ultima_fecha).days >= 7:
            if not os.path.exists("backups"):
                os.makedirs("backups")
            
            nombre_backup = f"alphatech_backup_{fecha_hoy.strftime('%Y-%m-%d')}.db"
            shutil.copy("alphatech.db", os.path.join("backups", nombre_backup))
        
         # 3. Guardar la fecha de hoy como la última vez que se hizo el backup
            with open(archivo_fecha, "w") as f:
                f.write(fecha_hoy.strftime("%Y-%m-%d"))
            
            print("Backup semanal realizado con éxito.")
        else:
            print("Aún no es necesario realizar el backup semanal.")
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename="superhero") # Usamos una ventana de ttkbootstrap
    app = AlphaTechApp(root)
    root.mainloop()