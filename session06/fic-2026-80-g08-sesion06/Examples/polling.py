import time, os
import sys
import RPi.GPIO as GPIO
current_environment = os.getenv("RPI_ENVIRONMENT")


BUTTON_GPIO = 16

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pressed = False
        while True:
            # button is pressed when pin is LOW
            if GPIO.input(BUTTON_GPIO) == GPIO.LOW:
                if not pressed:
                    print("Button pressed!")
                    pressed = True
            # button not pressed (or released)
            else:
                pressed = False
            time.sleep(0.1)
    except Exception as e:
        print(e)
        GPIO.cleanup()
        sys.exit(0)