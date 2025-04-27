import numpy as np
import cv2
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2
from libcamera import controls

# Motor GPIO pins
ENA, IN1, IN2 = 22, 24, 26  # Left motor
ENB, IN3, IN4 = 36, 38, 40  # Right motor

# Motor PWM settings
PWM_FREQUENCY = 1000
PWM_DUTY_CYCLE = 42  # Base motor speed percentage

# HSV color range for line detection
LOWER_COLOR = np.array([65, 190, 75])
UPPER_COLOR = np.array([80, 210, 115])

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)

motor_left = GPIO.PWM(ENA, PWM_FREQUENCY)
motor_right = GPIO.PWM(ENB, PWM_FREQUENCY)
motor_left.start(PWM_DUTY_CYCLE)
motor_right.start(PWM_DUTY_CYCLE)

# Initialize camera
picam2 = Picamera2()
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
picam2.start()
time.sleep(1)

# Motor control functions
def move_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def stop_motors():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# Last known direction for search behavior
last_known_direction = "left"

try:
    while True:
        image = picam2.capture_array("main")
        height, width, _ = image.shape
        cropped = image[int(height * 0.6):height, int(width * 0.1):int(width * 0.9)]

        blurred = cv2.medianBlur(cropped, 5)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                center_range = cropped.shape[1] * 0.5
                left_threshold = (cropped.shape[1] // 2) - (center_range // 2)
                right_threshold = (cropped.shape[1] // 2) + (center_range // 2)

                if left_threshold < cx < right_threshold:
                    move_forward()
                elif cx <= left_threshold:
                    turn_left()
                    last_known_direction = "left"
                else:
                    turn_right()
                    last_known_direction = "right"
            else:
                stop_motors()
        else:
            if last_known_direction == "left":
                turn_right()
                last_known_direction = "right"
            else:
                turn_left()
                last_known_direction = "left"
            time.sleep(0.5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass
finally:
    stop_motors()
    GPIO.cleanup()
    cv2.destroyAllWindows()
