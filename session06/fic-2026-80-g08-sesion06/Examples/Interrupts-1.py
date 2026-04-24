import os
import sys

current_environment = os.getenv("RPI_ENVIRONMENT")
if current_environment == "Mac":
    import FakeRPi.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

BUTTON_GPIO = 16

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        while True:
            GPIO.wait_for_edge(BUTTON_GPIO, GPIO.BOTH)
            if GPIO.input(BUTTON_GPIO) == GPIO.LOW:
                print("Button pressed!")
            else:
                print("Button released!")
    except Exception as e:
        print(e)
        GPIO.cleanup()
        sys.exit(0)