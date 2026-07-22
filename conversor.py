class ConversorMoneda:

  def __init__(self):
    self.tasas = {
        "bcv": 738.00,  # Corregido 'bsv' por 'bcv'
        "usdt": 855.00,
        "euro": 840.00,
    }

  def imprimir_tasas_equivalentes(self, monto_usd):
    monto_usd = float(monto_usd)
    print(f"\n--- 💱 EQUIVALENCIAS PARA ${monto_usd:.2f} ---")
    resultado_bcv = monto_usd * self.tasas["bcv"]
    resultado_euro = resultado_bcv / self.tasas["euro"]
    resultado_usdt = resultado_bcv / self.tasas["usdt"]

    print(
        f"💵 Cantidad Bs (BCV): {resultado_bcv:,.2f} | Cantidad en $"
        f"  {monto_usd:.2f}"
    )
    print(f"{'='*40}")
    print(
        f"💶 En Bs (EURO): {resultado_bcv:,.2f} | Cantidad en €"
        f" {resultado_euro:.2f}"
    )
    print(f"{'='*40}")
    print(
        f"💵 En Bs (USDT): {resultado_bcv:,.2f} | Cantidad en $"
        f" {resultado_usdt:.2f}"
    )
    print(f"{'='*40}")
    print("------------------------------------------")