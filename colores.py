class Colores:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

# Ejemplo de uso en tu menú:
print(f"{Colores.AZUL}--- 🛠️ ALPHA TECH (v4.0) ---{Colores.RESET}")
print(f"{Colores.VERDE}1. Registrar nueva orden{Colores.RESET}")
print(f"{Colores.ROJO}❌ [ERROR]: El nombre no puede estar vacío.{Colores.RESET}")