import RPi.GPIO as GPIO
import time

SERVO_PIN = 21


def setup():
    global servo
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(0)

def setAngle(angle):
    angle = max(0, min(180, angle))
    start = 2.5
    end = 12.5
    ratio = (end - start) / 180
    angle_as_percent = angle * ratio
    servo.ChangeDutyCycle(angle_as_percent)

if __name__ == '__main__':
    try:
        setup()
        angle = 2.5
        while (angle <= 12.5):
            servo.start(angle)
            time.sleep(3)
            angle = angle + 2.5
        while (angle >= 2.5):
            servo.start(angle)
            time.sleep(3)
            angle = angle - 2.5
    except KeyboardInterrupt:
        servo.stop()
        GPIO.cleanup()