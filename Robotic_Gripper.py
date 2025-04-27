import RPi.GPIO as GPIO
import time
import curses

GPIO.setmode(GPIO.BCM) 

# Define the GPIO pins for the L298N motor driver 
OUT1 = 12
OUT2 = 11
OUT3 = 13
OUT4 = 15

# Define the GPIO pins for the second motor
MOTOR2_PIN1 = 20  # Use BCM mode
MOTOR2_PIN2 = 21  # Use BCM mode

# Set the GPIO pins as output
GPIO.setup(OUT1, GPIO.OUT)
GPIO.setup(OUT2, GPIO.OUT)
GPIO.setup(OUT3, GPIO.OUT)
GPIO.setup(OUT4, GPIO.OUT)
GPIO.setup(MOTOR2_PIN1, GPIO.OUT)  
GPIO.setup(MOTOR2_PIN2, GPIO.OUT)

GPIO.output(OUT1, GPIO.LOW)
GPIO.output(OUT2, GPIO.LOW)
GPIO.output(OUT3, GPIO.LOW)
GPIO.output(OUT4, GPIO.LOW)
GPIO.output(MOTOR2_PIN1, GPIO.LOW)
GPIO.output(MOTOR2_PIN2, GPIO.LOW)
