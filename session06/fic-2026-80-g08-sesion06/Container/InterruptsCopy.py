import os, sys
import signal
import RPi.GPIO as GPIO
import threading

current_environment = os.getenv("RPI_ENVIRONMENT")

BUTTON_PIN = 16
pause_event = threading.Event()

class Button:
    def ejecutar(self):
        setup()
        signal.pause()

def setup():

    print("Ejecutando la configuración de los dispositivos")
    GPIO.setmode(GPIO.BCM)
    print("La configuración de los dispositivos ha finalizado")
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                          callback=button_pressed_callback, bouncetime=150)

    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):
    global pause_event
    if pause_event.is_set():
        pause_event.clear()
        print("Parado\n")
    else:
        pause_event.set()
        print("Reanudado\n")


if __name__ == '__main__':
    try:
        setup()
        signal.pause()
    except Exception as e:
        print(e)
        GPIO.cleanup()
        sys.exit(0)