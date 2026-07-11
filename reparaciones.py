import json
import os
import shutil
from equipo import Equipo
from datetime import datetime
from colores import Colores

class ListaReparaciones:
    def __init__(self):
        self.cabeza = None
        self.proximo_id = 1001

    def registrar_equipo(self, cliente, dispositivo, falla, presupuesto_usd):
        id_actual = str(self.proximo_id)
        self.proximo_id += 1
        nuevo_equipo = Equipo(id_actual, cliente, dispositivo, falla, presupuesto_usd)
        self._insertar_al_final(nuevo_equipo)
        print(f"📌 Orden #{id_actual} registrada correctamente.")
        return True

    def _insertar_al_final(self, nuevo_equipo):
        if self.cabeza is None:
            self.cabeza = nuevo_equipo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo_equipo

    def _agregar_nodo_manual(self, id_o, cli, dev, fal, pre, est, pagos,fecha):
        nuevo_equipo = Equipo(id_o, cli, dev, fal, pre, est,fecha_ingreso=fecha)
        for p in pagos:
            nuevo_equipo.cargar_pago_historico(p['monto'], p['moneda'], p['fecha'])
        self._insertar_al_final(nuevo_equipo)

    def modificar_estado_equipo(self, id_orden, nuevo_estado):
        actual = self.cabeza
        while actual is not None:
            if actual.obtener_id() == id_orden:
                actual.estado = nuevo_estado
                return True
            actual = actual.siguiente
        return False

    def guardar_en_json(self, nombre_archivo="taller_datos.json"):
        datos_a_guardar = {"proximo_id": self.proximo_id, "equipos": []}
        actual = self.cabeza
        while actual is not None:
            datos_a_guardar["equipos"].append({
                "id_orden": actual.obtener_id(),
                "cliente": actual.obtener_cliente(),
                "dispositivo": actual.obtener_dispositivo(),
                "falla": actual.obtener_falla(),
                "presupuesto_usd": actual.obtener_presupuesto(),
                "estado": actual.estado,
                "pagos": actual.obtener_historial_pagos(),
                "fecha_ingreso": actual.fecha_ingreso  # <--- Agregamos la fecha
            })
            actual = actual.siguiente
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos_a_guardar, archivo, indent=4, ensure_ascii=False)
        print("💾 Datos y contador guardados en disco.")

    def cargar_desde_json(self, nombre_archivo="taller_datos.json"):
        try:
            with open(nombre_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                
                # 1. Blindaje del contador de ID
                self.proximo_id = int(datos.get("proximo_id", 1001))
                self.cabeza = None
                
                # 2. Iteración defensiva
                equipos = datos.get("equipos", [])
                for e in equipos:
                    # Validamos que el ID sea procesable
                    id_orden = str(e.get("id_orden", "N/A"))
                    
                    # Si el ID es "N/A", es un dato corrupto, lo saltamos
                    if id_orden == "N/A":
                        print(f"{Colores.AMARILLO}⚠️ Alerta: Se encontró una orden sin ID válido. Saltando.{Colores.RESET}")
                        continue
                        
                    # 3. Conversión segura de tipos
                    cliente = str(e.get("cliente", "Desconocido"))
                    dispositivo = str(e.get("dispositivo", "N/A"))
                    falla = str(e.get("falla", "N/A"))
                    try:
                        presupuesto = float(e.get("presupuesto_usd", 0))
                    except ValueError:
                        presupuesto = 0.0
                    
                    estado = str(e.get("estado", "Recibido (En Espera)"))
                    pagos = e.get("pagos", [])
                    fecha = e.get("fecha_ingreso", datetime.now().strftime("%Y-%m-%d"))

                    # Inyectamos los datos validados
                    self._agregar_nodo_manual(
                        id_orden, cliente, dispositivo, falla, 
                        presupuesto, estado, pagos, fecha
                    )
            print("✅ Datos cargados correctamente.")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Archivo no encontrado o corrupto ({e}). Iniciando sistema en limpio.")
            self.proximo_id = 1001
            self.cabeza = None

    def mostrar_taller_activo(self):
        if self.cabeza is None:
            print("\n📭 Taller vacío.")
            return
        print("\n📋 LISTADO DE ÓRDENES:")
        actual = self.cabeza
        while actual is not None:
            print(f"🆔 #{actual.obtener_id()} | Ingreso: {actual.fecha_ingreso} | {actual.obtener_dispositivo()} | "
                  f"Estado: {actual.estado} | Cliente: {actual.obtener_cliente()} | "
                  f"Falla: {actual.obtener_falla()} | Presupuesto: ${actual.obtener_presupuesto():.2f}")
            actual = actual.siguiente   

    def generar_reporte_rendimiento(self):
        total_ingresos = 0.0
        conteo_estados = {}
        actual = self.cabeza
        while actual is not None:
            total_ingresos += actual.obtener_presupuesto()
            estado = actual.estado
            conteo_estados[estado] = conteo_estados.get(estado, 0) + 1
            actual = actual.siguiente
        print("\n📊 --- REPORTE DE RENDIMIENTO ALPHA TECH ---")
        print(f"💰 Ingreso total proyectado: ${total_ingresos:.2f}")
        print("📈 Estado de las órdenes:")
        for estado, cantidad in conteo_estados.items():
            print(f"   - {estado}: {cantidad}")
        print("============================================")

    def buscar_orden(self, id_orden):
        actual = self.cabeza
        while actual is not None:
            if actual.obtener_id() == id_orden:
                return actual
            actual = actual.siguiente
        return None

    def buscar_orden_por_nombre(self, nombre_buscado):
        resultados = []
        nombre_buscado = nombre_buscado.lower().strip()
        actual = self.cabeza
        while actual is not None:
            nombre_cliente = actual.obtener_cliente().lower()
            if nombre_cliente.startswith(nombre_buscado) or nombre_buscado in nombre_cliente:
                resultados.append(actual)
            actual = actual.siguiente
        return resultados

    def ver_pagos(self, id_orden):
        equipo = self.buscar_orden(id_orden)
        if equipo is None:
            print(f"❌ Orden #{id_orden} no encontrada.")
            return
        # AGREGAR ESTA LÍNEA PARA MOSTRAR LA FECHA:
        print(f"\n📅 Fecha de ingreso del equipo: {equipo.fecha_ingreso}")
        historial = equipo.obtener_historial_pagos()
        if not historial:
            print(f"📭 No hay pagos registrados para la orden #{id_orden}.")
            return
        print(f"\n💳 Historial de pagos para la orden #{id_orden}:")
        for pago in historial:
           # Mostramos la fecha guardada en el diccionario
            fecha = pago.get('fecha', 'Fecha no registrada')
            print(f"   - {fecha} | Monto: {pago['monto']:.2f} {pago['moneda']}")
        total_abonado = equipo.obtener_total_abonado()
        saldo_pendiente = equipo.obtener_presupuesto() - total_abonado
        print(f"💰 Total abonado: ${total_abonado:.2f}")
        print(f"💵 Saldo pendiente: ${saldo_pendiente:.2f}")

    def registrar_pago(self, id_busqueda, monto, moneda):
        actual = self.cabeza
        while actual:
            if actual.obtener_id() == id_busqueda: 
                return actual.registrar_pago(monto, moneda)
            actual = actual.siguiente
        return False
    def generar_cierre_caja(self):
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        total_usd = 0.0
        total_bs = 0.0
        hubo_movimientos = False
        
        actual = self.cabeza
        while actual:
            # Obtenemos la lista de pagos de este equipo
            historial = actual.obtener_historial_pagos()
            
            for pago in historial:
                # Extraemos solo la fecha (los primeros 10 caracteres: YYYY-MM-DD)
                fecha_pago_corta = pago['fecha'][:10]
                
                # <--- ¿Qué sale aquí?
                # Comparamos estrictamente
                if fecha_pago_corta == fecha_hoy:
                    hubo_movimientos = True
                    if pago['moneda'] == "USD":
                        total_usd += pago['monto']
                    elif pago['moneda'] == "BS":
                        total_bs += pago['monto']
            
            actual = actual.siguiente
        
        # Ahora el print está fuera del while
        if hubo_movimientos:
            print(f"\n📊 --- RESUMEN DE CIERRE DEL DÍA ({fecha_hoy}) ---")
            print(f"💵 Total USD: ${total_usd:.2f}")
            print(f"💳 Total BS:  Bs {total_bs:.2f}")
            print("------------------------------------------")
        else:
            print("\nℹ️ No se registraron pagos el día de hoy.")
    def crear_backup(self):
        # 1. Aseguramos que la carpeta exista
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        # 2. Creamos el nombre del archivo con fecha y hora
        fecha_backup = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nombre_archivo = f"backups/taller_backup_{fecha_backup}.json"
        
        # 3. Copiamos el archivo actual
        try:
            shutil.copyfile("taller_datos.json", nombre_archivo)
            print(f"✅ Backup creado: {nombre_archivo}")
        except FileNotFoundError:
            print("⚠️ No se encontró el archivo principal para el backup.")
    def verificar_morosidad(self, dias_limite=10):
        hoy = datetime.now()
        morosos = []
        actual = self.cabeza
    
        while actual:
            # Convertimos la fecha guardada (string) a objeto datetime
            fecha_ing = datetime.strptime(actual.fecha_ingreso, "%Y-%m-%d")
            diferencia = (hoy - fecha_ing).days
        
            if diferencia > dias_limite and actual.estado.lower() != "entregado" and actual.estado.lower() == "reparado (listo para entregar)":
             morosos.append(actual)
            
            actual = actual.siguiente
        return morosos
    def mostrar_equipos_retrasados(self):
        hoy = datetime.now()
        # Simplificamos la lógica: solo nos importa que NO esté entregado
        print(f"\n{Colores.ROJO}⚠️ EQUIPOS CON MÁS DE 10 DÍAS SIN Reparar:{Colores.RESET}")
        
        contador = 0
        actual = self.cabeza
        while actual:
            try:
                fecha_ing = datetime.strptime(actual.fecha_ingreso, "%Y-%m-%d")
                diferencia = (hoy - fecha_ing).days
                
                # Blindaje: Usamos .lower() para evitar errores de mayúsculas/minúsculas
                if diferencia > 10 and actual.estado.lower() != "entregado" and actual.estado.lower() == "recibido (en espera)":
                    print(f"🆔 #{actual.obtener_id()} | Estado: {actual.estado} | ⏳ {diferencia} días")
                    contador += 1
            except ValueError:
                continue # Si la fecha en el JSON está mal, saltamos ese equipo
            actual = actual.siguiente
    def exportar_reporte_txt(self):
        nombre_archivo = f"reporte_taller_{datetime.now().strftime('%Y-%m-%d')}.txt"
        with open(nombre_archivo, "w") as f:
            f.write("--- REPORTE DE TALLER ALPHA TECH ---\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            actual = self.cabeza
            while actual:
                f.write(f"ID: {actual.obtener_id()} | Cliente: {actual.obtener_cliente()} | "
                        f"Estado: {actual.estado} | Falla: {actual.obtener_falla()}\n")
                actual = actual.siguiente
        print(f"\n{Colores.VERDE}💾 Reporte guardado como: {nombre_archivo}{Colores.RESET}")