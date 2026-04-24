#!/usr/bin/env python3
import signal
import os
import sys
import RPi.GPIO as GPIO

current_environment = os.getenv("RPI_ENVIRONMENT")


BUTTON_GPIO = 16


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)


def button_pressed_callback(channel):
    print("Button pressed!")


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING,
                              callback=button_pressed_callback, bouncetime=150)
        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
    except Exception as e:
        print(e)
        GPIO.cleanup()
        sys.exit(0)