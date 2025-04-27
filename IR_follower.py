import RPi.GPIO as GPIO
import time

# Motor pins
ENA = 11
IN1 = 32
IN2 = 33
ENB = 13
IN3 = 12
IN4 = 35

# IR sensor pins
IR_LEFT = 8
IR_MIDDLE = 38
IR_RIGHT = 40

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup([IR_LEFT, IR_MIDDLE, IR_RIGHT], GPIO.IN)
GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)

GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.LOW)
GPIO.output(IN4, GPIO.LOW)

motor_left = GPIO.PWM(ENA, 50)
motor_right = GPIO.PWM(ENB, 50)
motor_left.start(0)
motor_right.start(0)

# PID constants
KP = 8
BASE_SPEED = 15

def drive(left_speed, right_speed):
    GPIO.output(IN1, GPIO.HIGH if left_speed >= 0 else GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW if left_speed >= 0 else GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW if right_speed >= 0 else GPIO.HIGH)
    GPIO.output(IN4, GPIO.HIGH if right_speed >= 0 else GPIO.LOW)
    motor_left.ChangeDutyCycle(abs(left_speed))
    motor_right.ChangeDutyCycle(abs(right_speed))

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    motor_left.ChangeDutyCycle(0)
    motor_right.ChangeDutyCycle(0)

def read_sensors():
    left = GPIO.input(IR_LEFT)
    middle = GPIO.input(IR_MIDDLE)
    right = GPIO.input(IR_RIGHT)
    return left, middle, right

try:
    while True:
        left, middle, right = read_sensors()
        error = (-1 * left) + (1 * right)
        correction = KP * error
        left_speed = max(0, min(100, BASE_SPEED - correction))
        right_speed = max(0, min(100, BASE_SPEED + correction))
        drive(left_speed, right_speed)
        time.sleep(0.001)
except KeyboardInterrupt:
    stop()
    GPIO.cleanup()
