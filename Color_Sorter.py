import RPi.GPIO as GPIO
import time
import math

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Color sensor pins
s0, s1, s2, s3, sig = 13, 15, 16, 18, 22
cycles = 100

# Motor 1 (feeder) pins
MOTOR1_OUT1, MOTOR1_OUT2, MOTOR1_OUT3, MOTOR1_OUT4 = 40, 38, 36, 32

# Motor 2 (sorter) pins
MOTOR2_OUT1, MOTOR2_OUT2, MOTOR2_OUT3, MOTOR2_OUT4 = 12, 8, 26, 26

# Set up GPIO
for pin in [s0, s1, s2, s3, MOTOR1_OUT1, MOTOR1_OUT2, MOTOR1_OUT3, MOTOR1_OUT4, MOTOR2_OUT1, MOTOR2_OUT2, MOTOR2_OUT3, MOTOR2_OUT4]:
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(sig, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Set frequency scaling
GPIO.output(s0, GPIO.HIGH)
GPIO.output(s1, GPIO.LOW)

# Calibration data
CALIBRATION = {
    "white": {"red": None, "green": None, "blue": None},
    "black": {"red": None, "green": None, "blue": None},
}

def get_color_value(s2_state, s3_state):
    GPIO.output(s2, s2_state)
    GPIO.output(s3, s3_state)
    time.sleep(0.1)
    start = time.time()
    for _ in range(cycles):
        GPIO.wait_for_edge(sig, GPIO.FALLING)
    duration = time.time() - start
    return cycles / duration

def get_average_color_value(s2_state, s3_state, samples=5):
    for _ in range(3):
        get_color_value(s2_state, s3_state)
        time.sleep(0.05)
    total = 0
    for _ in range(samples):
        total += get_color_value(s2_state, s3_state)
        time.sleep(0.05)
    return total / samples

def normalize_with_black_white(red, green, blue):
    if None in CALIBRATION["white"].values() or None in CALIBRATION["black"].values():
        return red, green, blue

    def scale(value, black_ref, white_ref):
        return int(255 * (value - black_ref) / (white_ref - black_ref))

    r = max(0, min(255, scale(red, CALIBRATION["black"]["red"], CALIBRATION["white"]["red"])))
    g = max(0, min(255, scale(green, CALIBRATION["black"]["green"], CALIBRATION["white"]["green"])))
    b = max(0, min(255, scale(blue, CALIBRATION["black"]["blue"], CALIBRATION["white"]["blue"])))
    return r, g, b

def closest_color_match(r, g, b):
    references = {
        "Red": (255, 0, 0),
        "Blue": (0, 0, 255),
        "Green": (0, 255, 0),
        "Yellow": (255, 255, 0)
    }
    min_dist = float('inf')
    match = None
    for color, (ref_r, ref_g, ref_b) in references.items():
        dist = math.sqrt((r - ref_r)**2 + (g - ref_g)**2 + (b - ref_b)**2)
        if dist < min_dist:
            min_dist = dist
            match = color
    return match

def detect_color():
    red = get_average_color_value(GPIO.LOW, GPIO.LOW)
    green = get_average_color_value(GPIO.HIGH, GPIO.HIGH)
    blue = get_average_color_value(GPIO.LOW, GPIO.HIGH)
    r_norm, g_norm, b_norm = normalize_with_black_white(red, green, blue)
    print(f"RGB: R={r_norm}, G={g_norm}, B={b_norm}")
    color = closest_color_match(r_norm, g_norm, b_norm)
    print(f"Detected: {color}")
    move_sorter_motor(color)
    return color

def move_motor(pins, steps=25, delay=0.005):
    sequence = [
        (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.LOW),
        (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW),
        (GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.LOW),
        (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
        (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.LOW),
        (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH),
        (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.HIGH),
        (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH)
    ]
    for _ in range(steps):
        for step in sequence:
            for pin, val in zip(pins, step):
                GPIO.output(pin, val)
            time.sleep(delay)

def move_sorter_motor(color):
    steps_for_color = {
        "Red": 30,
        "Blue": 60,
        "Green": 90,
        "Yellow": 120
    }
    if color in steps_for_color:
        steps = steps_for_color[color]
        print(f"Moving sorter motor {steps} steps for {color}")
        move_motor([MOTOR2_OUT1, MOTOR2_OUT2, MOTOR2_OUT3, MOTOR2_OUT4], steps)

def calibrate_color(ref):
    print(f"Calibrating {ref}... Place {ref} object under sensor.")
    time.sleep(3)
    CALIBRATION[ref]["red"] = get_average_color_value(GPIO.LOW, GPIO.LOW)
    CALIBRATION[ref]["green"] = get_average_color_value(GPIO.HIGH, GPIO.HIGH)
    CALIBRATION[ref]["blue"] = get_average_color_value(GPIO.LOW, GPIO.HIGH)
    print(f"{ref.capitalize()} calibration: {CALIBRATION[ref]}")

def main():
    try:
        calibrate_color("white")
        calibrate_color("black")
        print("\nCommands:")
        print("S - Spin feeder motor to get ball")
        print("C - Scan ball color")
        print("Q - Quit\n")
        while True:
            cmd = input("Enter command (S/C/Q): ").strip().upper()
            if cmd == "S":
                print("Spinning feeder motor...")
                move_motor([MOTOR1_OUT1, MOTOR1_OUT2, MOTOR1_OUT3, MOTOR1_OUT4])
            elif cmd == "C":
                print("Scanning color...")
                detect_color()
            elif cmd == "Q":
                print("Exiting...")
                break
            else:
                print("Invalid input.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
