import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap as tb  # <-- Cambiamos tkinter.ttk por esto
from ttkbootstrap.constants import *
from reparaciones import ListaReparaciones
from basededatos import GestorBD

class AlphaTechApp:
    def __init__(self, root):
       self.root = root
       self.root.title("Alpha Tech v5.0 - Professional")
       self.root.geometry("600x600") # Un poco más grande para que quepa todo
        
        # 1. Crear el contenedor principal (Frame)
        # Esto agrupa todo y evita que los elementos queden flotando
       self.main_frame = tb.Frame(self.root, padding=20)
       self.main_frame.pack(fill=BOTH, expand=YES)

        # 2. Título dentro del Frame
       tb.Label(self.main_frame, text="Panel de Gestión", font=("Helvetica", 18, "bold")).pack(pady=10)

        # 3. Botones (ahora los ponemos dentro del main_frame, no de root)
       self.crear_boton("Registrar Orden", self.abrir_registro)
       self.crear_boton("Cerrar y Guardar", self.cerrar_sistema)

        # 4. Tabla (también dentro del main_frame)
       self.configurar_tabla()
       self.configurar_menu_contextual() # <--- ¡Añade esta línea!
        # 5. Carga de datos
       self.sistema = ListaReparaciones()
       self.sistema.cargar_desde_json()
       self.refrescar_tabla()

    def crear_boton(self, texto, comando):
        # Nota: aquí también usamos 'self.main_frame' en lugar de 'self.root'
        tb.Button(self.main_frame, text=texto, command=comando, width=30, bootstyle="info").pack(pady=5)

    def configurar_tabla(self):
        # 1. Primero el buscador (para que quede arriba)
        self.search_entry = tb.Entry(self.main_frame, bootstyle="info")
        self.search_entry.pack(fill="x", pady=10)
        self.search_entry.bind('<KeyRelease>', self.filtrar_tabla)

        # 2. Luego la tabla (para que quede abajo del buscador)
        self.tree = tb.Treeview(self.main_frame, columns=("ID", "Cliente", "Dispositivo", "Estado"), show="headings", bootstyle="info")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Dispositivo", text="Dispositivo")
        self.tree.heading("Estado", text="Estado")
        
        
        self.tree.column("ID", width=50)
        
        # 3. Solo un pack para la tabla
        self.tree.pack(fill="both", expand=True, pady=10)
        # Añade esta línea al final de la función:
        self.tree.bind("<Double-1>", lambda event: self.ver_detalles_orden())

    def refrescar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        actual = self.sistema.cabeza
        while actual:
            self.tree.insert("", "end", values=(actual.obtener_id(), actual.obtener_cliente(), actual.obtener_dispositivo(), actual.estado))
            actual = actual.siguiente

    def abrir_registro(self):
        top = tk.Toplevel(self.root)
        top.title("Registrar Nueva Orden")
        campos = {}
        etiquetas = ["Cliente", "Dispositivo", "Falla", "Costo"]
        for i, campo in enumerate(etiquetas):
            tk.Label(top, text=f"{campo}:").grid(row=i, column=0, padx=10, pady=5)
            campos[campo] = tk.Entry(top)
            campos[campo].grid(row=i, column=1, padx=10, pady=5)
        
        def guardar_datos():
            try:
                p = float(campos["Costo"].get())
                self.sistema.registrar_equipo(campos["Cliente"].get(), campos["Dispositivo"].get(), campos["Falla"].get(), p)
                self.refrescar_tabla()
                messagebox.showinfo("Éxito", "Orden registrada")
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "El costo debe ser un número")
        
        tk.Button(top, text="Guardar Registro", command=guardar_datos).grid(row=4, columnspan=2, pady=10)

    def filtrar_tabla(self, event):
        query = self.search_entry.get().lower()
    
    # Limpiamos tabla
        for i in self.tree.get_children():
            self.tree.delete(i)
        
    # Recorremos la lista lógica
        actual = self.sistema.cabeza
        while actual:
        # Filtramos por cliente (puedes añadir más condiciones)
            if query in actual.obtener_cliente().lower():
                self.tree.insert("", "end", values=(
                    actual.obtener_id(), 
                    actual.obtener_cliente(), 
                    actual.obtener_dispositivo(), 
                    actual.estado
             ))
            actual = actual.siguiente
    def configurar_menu_contextual(self):
        # Creamos el menú que será invisible hasta que hagamos clic
        self.menu_contextual = tb.Menu(self.root, tearoff=0)
        self.menu_contextual.add_command(label="Marcar como Reparado", command=lambda: self.actualizar_status("Reparado (listo para entrega)"))
        self.menu_contextual.add_command(label="Marcar como Entregado", command=lambda: self.actualizar_status("Entregado al cliente"))
        self.menu_contextual.add_separator() # Una rayita para separar
        self.menu_contextual.add_command(label="Eliminar Orden", command=self.eliminar_orden)
        
        # Vinculamos el clic derecho (Button-3) a la tabla
        self.tree.bind("<Button-3>", self.mostrar_menu)

    def mostrar_menu(self, event):
        # Identifica la fila donde hiciste clic
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item) # Selecciona la fila automáticamente
            self.menu_contextual.post(event.x_root, event.y_root) # Muestra el menú ahí mismo
    def actualizar_status(self, nuevo_estado):
        # 1. Obtener la fila seleccionada
        seleccion = self.tree.selection()
        if not seleccion:
            print("No hay ninguna fila seleccionada.")
            return
            
        item = seleccion[0]
        valores = self.tree.item(item, "values")
        
        # 2. Captura segura del ID (compararemos como texto para evitar errores de tipo)
        id_orden = str(valores[0]) 
        
        print(f"Intentando actualizar ID: {id_orden} a estado: {nuevo_estado}")
        
        # 3. Actualizar en la lógica del sistema
        # NOTA: Asegúrate de que tu lógica soporte la comparación de strings 
        # o convierte el ID dentro de tu función modificar_estado_equipo.
        resultado = self.sistema.modificar_estado_equipo(id_orden, nuevo_estado)
        
        if resultado:
            # 4. Guardar en JSON si el cambio fue exitoso
            self.sistema.guardar_en_json()
            # 5. Refrescar la tabla para ver el cambio visual
            self.refrescar_tabla()
            print("¡Actualización exitosa!")
        else:
            print("Error: No se pudo encontrar el ID en la lista lógica.")
    
    def ver_detalles_orden(self):
        # 1. Obtener la fila seleccionada
        seleccion = self.tree.selection()
        if not seleccion:
            return
            
        item = seleccion[0]
        id_orden = self.tree.item(item, "values")[0]
        
        # 2. Buscar los datos completos en la lógica
        orden = self.sistema.buscar_orden(id_orden)
        
        if orden:
            # 3. Crear ventana emergente (Toplevel)
            ventana_detalle = tb.Toplevel(self.root)
            ventana_detalle.title(f"Detalle de Orden #{id_orden}")
            ventana_detalle.geometry("400x450")
            
            # Contenedor con margen
            frame = tb.Frame(ventana_detalle, padding=20)
            frame.pack(fill="both", expand=True)
            
            # Título dentro de la ventana
            tb.Label(frame, text="INFORMACIÓN DE LA REPARACIÓN", font=("Helvetica", 12, "bold"), bootstyle="info").pack(pady=10)
            
            # Datos a mostrar
            detalles = [
                ("ID de Orden:", orden.obtener_id()),
                ("Cliente:", orden.obtener_cliente()),
                ("Dispositivo:", orden.obtener_dispositivo()),
                ("Estado Actual:", orden.estado),
                ("Falla:", orden.obtener_falla()),
            ]
            
            for etiqueta, valor in detalles:
                f_dato = tb.Frame(frame)
                f_dato.pack(fill="x", pady=5)
                tb.Label(f_dato, text=etiqueta, font=("Helvetica", 10, "bold")).pack(side="left")
                tb.Label(f_dato, text=valor, font=("Helvetica", 10)).pack(side="right")

            # Botón para cerrar
            tb.Button(frame, text="Cerrar", bootstyle="danger-outline", command=ventana_detalle.destroy).pack(pady=20)   
    def eliminar_orden(self):
        item = self.tree.selection()[0]
        self.tree.delete(item)
        print("Orden eliminada")
   

    def cerrar_sistema(self):
        self.sistema.guardar_en_json()
        self.root.destroy()
    

if __name__ == "__main__":
    root = tk.Tk()
    app = AlphaTechApp(root)
    root.mainloop()