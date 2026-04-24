import signal
import threading
import RPi.GPIO as GPIO

import LCDDHT11
import NFCManager
import dcmotor
import InterruptsCopy

class EstadoContenedor:
    def __init__(self):
        self.lock = threading.Lock()

        self.door_open = False
        self.last_id = None

        self.temperature = 25.1
        self.humidity = 0.0

        self.motor_on = False

    # ---- NFC Avisa puerta abierta ---------------
    def set_door_open(self, is_open: bool, id: str = None):
        with self.lock:
            self.door_open = is_open
            if id:
                self.last_id = id
            else:
                self.last_id = None

    def get_door_state(self):
        with self.lock:
            return self.door_open, self.last_id

    # --- DHT11 Envía temperatura -------------

    def set_sensor_data(self, temperature: float, humidity: float):
        with self.lock:
            self.temperature = temperature
            self.humidity = humidity

    def get_sensor_data(self):
        with self.lock:
            return self.temperature, self.humidity

    # ------ MOTOR Envía su  estado --------------
    def set_motor_on(self, is_on: bool):
        with self.lock:
            self.motor_on = is_on

    def get_motor_on(self):
        with self.lock:
            return self.motor_on



def run_container():
    estado = EstadoContenedor()

    mi_Boton = InterruptsCopy.Button()

    miPantalla = LCDDHT11.PantallaDHT11(estado)
    miNFCManager = NFCManager.NFCManager(estado)
    miMotor = dcmotor.ControlMotorDC(pin_a = 5, pin_b = 6, pin_e = 13, estado=estado)

    velocidad_actual = 80

    print("Lanzando los threads del contenedor")

    #t1 = threading.Thread(target=miPantalla.ejecutar, daemon=True)
    #t1.start()
    print("He lanzado el thread de la pantalla")

    t2 = threading.Thread(target=miMotor.cambiar_velocidad, args=(velocidad_actual,), daemon=True)
    t2.start()
    print("He lanzado el thread del motor")

    # En el PDF aparece un ejemplo con target=NFCManager.ejecutar, pero lo correcto
    # es usar el objeto miNFCManager.
    #t3 = threading.Thread(target=miNFCManager.ejecutar, daemon=True)
    #t3.start()
    print("He lanzado el thread del lector NFC")

    t4 = threading.Thread(target=mi_Boton.ejecutar())
    t4.start()
    print("He lanzado el thread del Boton")

    try:
        # El enunciado usa join() para que el main espere a los hilos :contentReference[oaicite:1]{index=1}
        #t1.join()
        t2.join()
        #t3.join()
        t4.join()

    except KeyboardInterrupt:
        print("\nCancelacion detectada (Ctrl+C). Saliendo...")
        GPIO.cleanup()

    finally:
        # Cleanup de emergencia por si algun hilo no limpia (al estar en daemon)
        GPIO.cleanup()


if __name__ == "__main__":
    run_container()