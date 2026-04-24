import time as t
from ReadNFCData import *
from Servomotor import *

# ✅ Lista de IDs válidos — configurar antes de ejecutar
VALID_IDS = [
    "ID:12345678A",
    "ID:87654321B",
    "ID:11223344C",
    "ID:44162780X"
]


def validate_card(card_date_str, card_id):
    """
    Valida la fecha de caducidad y el ID de la tarjeta.
    Retorna True si ambas condiciones son correctas, False en caso contrario.
    """
    # Validar fecha
    try:
        card_date = datetime.strptime(card_date_str.split("Date:")[1].strip(), "%d-%m-%Y")
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    except (ValueError, IndexError) as e:
        print(f"Error al interpretar la fecha: {e}")
        return False

    if card_date < today:
        print(f"Tarjeta caducada. Fecha de validez: {card_date.strftime('%d-%m-%Y')}")
        return False

    # Validar ID
    if card_id not in VALID_IDS:
        print(f"ID no autorizado: {card_id}")
        return False

    return True


class NFCManager:
    def __init__(self, estado):
        self.estado = estado

    def ejecutar(self):
        # ✅ Inicializar servomotor
        setup()

        # Inicializar lector NFC
        pn532 = get_reader_id()

        try:
            while True:
                print("\n--- Esperando tarjeta... ---")

                # Leer la información de la tarjeta
                card_date_str, card_id = read_tachograph_info_from_card(pn532)
                print(f"Fecha de caducidad: {card_date_str}")
                print(f"ID del titular:     {card_id}")

                # Validar y actuar
                if validate_card(card_date_str, card_id):
                    print("✅ Tarjeta válida: abriendo servomotor a 90°")
                    self.estado.set_door_open(True, id = card_id)
                    setAngle(90)  # ✅ setAngle en minúscula, igual que en Servomotor.py
                else:
                    print("❌ Tarjeta inválida: servomotor permanece a 0°")
                    self.estado.set_door_open(False, id = card_id)
                    setAngle(0)

                t.sleep(10)

        except KeyboardInterrupt:
            print("\nSaliendo del programa...")
        finally:
            setAngle(0)  # ✅ Dejar el servo en posición segura antes de limpiar
            GPIO.cleanup()

if __name__ == "__main__":
    NFCManager.ejecutar()