import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb 
from ttkbootstrap.constants import *
from basededatos import GestorBD # Solo necesitamos la BD
import csv # Asegúrate de importar esto al principio de tu archivo

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
        self.tree.bind("<Double-1>", lambda event: self.ver_detalles_orden())

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
        
        def guardar():
            # 1. Obtenemos los valores
            cliente = entradas["Cliente"].get().strip()
            dispositivo = entradas["Dispositivo"].get().strip()
            falla = entradas["Falla"].get().strip()
            costo_str = entradas["Costo"].get().strip()
            
            # 2. VALIDACIÓN: Comprobamos primero. Si falta algo, lanzamos el error y 'return'
            if not cliente or not dispositivo or not falla or not costo_str:
                messagebox.showwarning("Campos Vacíos", "Por favor, completa todos los campos.")
                return # El return detiene la función aquí, no guarda nada y no cierra la ventana
            
            # 3. Solo si pasó la validación, procedemos a guardar
            try:
                costo = float(costo_str)
                self.sistema.insertar_orden(cliente, dispositivo, falla, costo, "En espera")
            except ValueError:
                messagebox.showerror("Error de Formato", "Por favor, ingresa un valor válido para el costo.")
                return
            
            # 4. Actualizamos y cerramos
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


    def cerrar_sistema(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename="superhero") # Usamos una ventana de ttkbootstrap
    app = AlphaTechApp(root)
    root.mainloop()