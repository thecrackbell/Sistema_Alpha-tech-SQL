from datetime import datetime
class Equipo:
    def __init__(self, id_orden, cliente, dispositivo, falla, presupuesto_usd, estado="Recibido (En Espera)", fecha_ingreso=None):
        self.__id_orden = id_orden
        self.__cliente = cliente
        self.__dispositivo = dispositivo
        self.__falla = falla
        self.__presupuesto_usd = presupuesto_usd
        self.fecha_ingreso = fecha_ingreso or datetime.now().strftime("%Y-%m-%d")
        self.__pagos = [] # Lista para guardar los abonos: [monto_usd, moneda]
        self.estado = estado
        self.siguiente = None 

    def obtener_id(self): return self.__id_orden
    def obtener_cliente(self): return self.__cliente
    def obtener_dispositivo(self): return self.__dispositivo
    def obtener_falla(self): return self.__falla
    def obtener_presupuesto(self): return self.__presupuesto_usd
    def registrar_pago(self, monto, moneda):
        fecha_pago = datetime.now().strftime("%Y-%m-%d %H:%M") # Fecha y hora exacta
        if monto > 0:
            self.__pagos.append({"monto": monto, "moneda": moneda, "fecha": fecha_pago})
            return True
        return False
    # MÉTODO DE LECTURA (Getter): Devuelve una copia, no la lista original
    def obtener_historial_pagos(self):
        return list(self.__pagos) 
    def obtener_total_abonado(self):
        return sum(pago["monto"] for pago in self.__pagos)
    def cargar_pago_historico(self, monto, moneda, fecha):
        # Este método no cambia la fecha, la respeta
        self.__pagos.append({"monto": monto, "moneda": moneda, "fecha": fecha})