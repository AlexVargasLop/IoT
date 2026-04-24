import adafruit_dht
from RPi import GPIO

import time
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
import board

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
class PantallaDHT11:
    def __init__(self, estado):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.sensor = adafruit_dht.DHT11(board.D12)
        self.estado = estado

    def read(self):
        try:
            return self.sensor.temperature, self.sensor.humidity
        except RuntimeError as e:
            print(f"Error de lectura DHT11: {e}")
            return None, None


    def ejecutar(self):
        mcp.output(3, 1)

        lcd.begin(16, 2)

        try:
            while True:
                temp, hum = self.read()
                lcd.clear()
                lcd.setCursor(0, 0)

                motor_on = self.estado.get_motor_on()

                if temp is not None and hum is not None:
                    lcd.message(f'Temp: {temp:.1f} C')
                    motor_str = "On" if motor_on else "Off"
                    lcd.setCursor(0, 1)
                    lcd.message(f'H: {hum}%  Mtr: {motor_str}')
                    self.estado.set_sensor_data(temperature=temp, humidity=hum)
                else:
                    lcd.message('Lectura')
                    lcd.setCursor(0, 1)
                    lcd.message('Invalida...')

                time.sleep(5)

                door_open, id = self.estado.get_door_state()


                if door_open and id:
                    lcd.clear()

                    lcd.setCursor(0, 0)
                    lcd.message(f'Bienvenido')
                    lcd.setCursor(0, 1)
                    lcd.message(f'{id}')
                    time.sleep(5)

        except KeyboardInterrupt:
            print("Interrupción por teclado. Saliendo...")
            GPIO.cleanup()
            lcd.clear()
            self.sensor.exit()

        finally:
            print("Limpiando...")
            GPIO.cleanup()
            lcd.clear()
            self.sensor.exit()
