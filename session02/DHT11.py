import RPi.GPIO as GPIO
import board
import adafruit_dht
import time


class SensorDHT11:
    def __init__(self, pin=board.D12):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.sensor = adafruit_dht.DHT11(pin)

    def read(self):
        """
        Devuelve (temperatura_c, humedad) o (None, None) si la lectura es inválida.
        """
        try:
            temperature_C = self.sensor.temperature
            humidity = self.sensor.humidity
            return temperature_C, humidity
        except RuntimeError as e:
            # Errores típicos de lectura del DHT11
            print(f"Error de lectura DHT11: {e}")
            return None, None

    def close(self):
        """
        Libera recursos del sensor y limpia GPIO.
        """
        try:
            self.sensor.exit()  # recomendado por Adafruit
        except Exception:
            pass
        GPIO.cleanup()


def main():
    s = SensorDHT11(board.D12)

    try:
        while True:
            temp, hum = s.read()
            if temp is not None and hum is not None:
                print(f"Temp: {temp:.1f} C, Humidity: {hum}%")
            else:
                print("Lectura inválida. Reintentando...")

            time.sleep(3)

    except KeyboardInterrupt:
        print("Interrupción por teclado. Saliendo...")

    finally:
        print("Limpiando configuración de GPIO...")
        s.close()


if __name__ == "__main__":
    main()

