import RPi.GPIO as GPIO
import time
import datetime

dc_motor_object = None


def move_dc_motor(requested_speed):
    requested_speed = int(max(0, min(100, requested_speed)))
    dc_motor_object.ChangeDutyCycle(requested_speed)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Speed = {requested_speed}/100")

def calcular_velocidad(temperatura):
    if temperatura <= 25:
        return 0
    velocidad = 80 + (temperatura - 25) * 2
    return min(velocidad, 100)

def destroy():
    GPIO.cleanup()

class ControlMotorDC:
    def __init__(self, pin_a, pin_b, pin_e, estado):
        self.estado = estado
        self.motor1A = pin_a
        self.motor1B = pin_b
        self.motor1E = pin_e

    def cambiar_velocidad(self, v_actual):
        global dc_motor_object

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.motor1A, GPIO.OUT)
        GPIO.setup(self.motor1B, GPIO.OUT)
        GPIO.setup(self.motor1E, GPIO.OUT)
        GPIO.output(self.motor1A, GPIO.HIGH)
        GPIO.output(self.motor1B, GPIO.LOW)

        dc_motor_object = GPIO.PWM(self.motor1E, 100)
        dc_motor_object.start(0)

        try:

            move_dc_motor(v_actual)

            time.sleep(1)

            while True:
                door_open, id = self.estado.get_door_state()

                if door_open:
                    move_dc_motor(0)
                    self.estado.set_motor_on(False)
                else:
                    temperatura, humedad = self.estado.get_sensor_data()

                    velocidad = calcular_velocidad(temperatura)

                    if velocidad > 0:
                        move_dc_motor(velocidad)
                        self.estado.set_motor_on(True)


                    else:
                        move_dc_motor(0)
                        self.estado.set_motor_on(False)

                time.sleep(1)
        except KeyboardInterrupt as e:
            destroy()
            print(e)

        finally:
            destroy()