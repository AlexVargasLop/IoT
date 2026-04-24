#!/usr/bin/env python3
# Detecting both rising and falling signals
import signal
import os
import sys

BUTTON_GPIO = 16

current_environment = os.getenv("RPI_ENVIRONMENT")
if current_environment == "Mac":
    import FakeRPi.GPIO as GPIO
else:
    import RPi.GPIO as GPIO


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)


def button_callback(channel):
    if GPIO.input(BUTTON_GPIO) == GPIO.LOW:
        print("Button pressed!")
    else:
        print("Button released!")


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH,
                              callback=button_callback, bouncetime=50)

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
    except Exception as e:
        print(e)
        GPIO.cleanup()
        sys.exit(0)