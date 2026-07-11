class ConversorMoneda:
    def __init__(self):
        # Aquí defines tus tasas (deberás actualizarlas manualmente o por API)
        self.tasas = {
            "bsv": 630,   # Tasa BCV
            "usdt": 710.00,  # Tasa USDT
            "euro": 795.00   # Tasa Euro
        }

    def imprimir_tasas_equivalentes( self,monto_usd):
        # Definimos las tasas actuales
        # Calculamos las equivalencias
        monto_usd=float(monto_usd)  # Aseguramos que sea un float
        print(f"\n--- 💱 EQUIVALENCIAS PARA ${monto_usd:.2f} ---")
        resultado_bcv = monto_usd * self.tasas["bsv"]
        resultado_euro = resultado_bcv / self.tasas["euro"]
        resultado_usdt = resultado_bcv / self.tasas["usdt"]
        print(f"💵 Canidad Bs (BCV): {resultado_bcv:.2f} | Cantidad en $  {monto_usd:.2f}")
        print(f"{'='*40}")
        print(f"💵 En Bs (EURO): {resultado_bcv:.2f} | Cantidad en € {resultado_euro:.2f}")
        print(f"{'='*40}")
        print(f"💵 En Bs (USDT): {resultado_bcv:.2f} | Cantidad en $ {resultado_usdt:.2f}")
        print(f"{'='*40}")
        print("------------------------------------------")
        