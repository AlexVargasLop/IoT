import adafruit_dht
from RPi import GPIO

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
import board
import time

PCF8574_address = 0x27 #I2C address of the PCF8574 chip
PCF8574A_address = 0x3F # I2C address of the PCF8574A chip.

# Crear adaptador PCF8574 GPIO
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print('I2C Address Error')
        exit(1)

###################################
# Crear LCD, passing in MCP GPIO adapter
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

# -- Clase Sensor -------
class SensorDHT11:
    def __init__(self, pin=board.D12):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.sensor = adafruit_dht.DHT11(board.D12)

    def read(self):
        try:
            return self.sensor.temperature, self.sensor.humidity
        except RuntimeError as e:
            print(f"Error de lectura DHT11: {e}")
            return None, None

    def close(self):
        try:
            self.sensor.exit()
        except Exception:
            pass
        GPIO.cleanup()


def main():
    mcp.output(3,1)

    lcd.begin(16,2)

    s = SensorDHT11(board.D12)

    try:
        while True:
            temp, hum = s.read()
            lcd.clear()
            lcd.setCursor(0,0)

            if temp is not None and hum is not None:
                lcd.message(f'Temp: {temp:.1f} C')
                lcd.setCursor(0,1)
                lcd.message(f'Humedad: {hum}%')
            else:
                lcd.message('Lectura')
                lcd.setCursor(0,1)
                lcd.message('Invalida...')

            time.sleep(3)
    except KeyboardInterrupt:
        print("Interrupción por teclado. Saliendo...")

    finally:
        print("Limpiando...")
        lcd.clear()
        s.close()



if __name__ == '__main__':
    main()