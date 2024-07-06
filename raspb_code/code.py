import RPi.GPIO as GPIO
import time
import datetime
from mfrc522 import SimpleMFRC522
from supabase import create_client

# Set up GPIO pins
GPIO.setmode(GPIO.BOARD)
PIN_TRIGGER = 7
PIN_ECHO = 11
SERVO_PIN = 12

# Set up Supabase connection
url = 'https://bgynecsgqrdfrkcyshsz.supabase.co'
key = '*********'
supabase = create_client(url, key)

# Set up HC-SR04 sensor
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

# Set up servo motor
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# Function to read RFID tag
def read_rfid():
    try:
        reader = SimpleMFRC522()
        id_, _ = reader.read()  # Ignore the text, only capture the ID
        return id_
    finally:
        pass

# Function to check pending bookings
def check_pending_bookings(rfid):
    try:
        response = supabase.table("booking").select("*").eq("rfid", rfid).eq("status", "pending").execute()
        data = response.data
        return data
    except Exception as e:
        print("Error checking pending bookings:", e)
        return None

# Function to check if the booking is valid
def check_valid_booking(booking):
    try:
        # Extract booking details
        start_time = booking['start_time']
        end_time = booking['end_time']
        booking_date = booking['date']

        # Get current date and time
        current_date = datetime.datetime.now().date()
        current_time = datetime.datetime.now().time()

        # Convert start_time and end_time strings to time objects
        start_time_obj = datetime.datetime.strptime(start_time, '%H:%M:%S').time()
        end_time_obj = datetime.datetime.strptime(end_time, '%H:%M:%S').time()
        booking_date_obj = datetime.datetime.strptime(booking_date, '%Y-%m-%d').date()

        # Check if the booking date is the current date
        if booking_date_obj == current_date:
            # Check if the current time is between start_time and end_time
            if start_time_obj <= current_time <= end_time_obj:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("Error checking valid booking:", e)
        return False

# Function to measure distance
def measure_distance():
    try:
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        while GPIO.input(PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO) == 1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        return distance
    except Exception as e:
        print("Error measuring distance:", e)
        return None

# Function to control the gate using the servo motor
def control_gate():
    try:
        # Open gate
        servo.ChangeDutyCycle(0)
        time.sleep(1)
        servo.ChangeDutyCycle(2)
        time.sleep(1)
        servo.ChangeDutyCycle(4)
        time.sleep(1)
        servo.ChangeDutyCycle(6)
        time.sleep(1)
        servo.ChangeDutyCycle(8)
        time.sleep(6)
        # Close gate
        servo.ChangeDutyCycle(7)
        time.sleep(1)
        servo.ChangeDutyCycle(5)
        time.sleep(1)
        servo.ChangeDutyCycle(3)
        time.sleep(1)
        servo.ChangeDutyCycle(1)
        time.sleep(1)
        servo.ChangeDutyCycle(0)
    except Exception as e:
        print("Error opening gate:", e)

# Function to update the booking status in supabase
def update_active_booking(rfid):
    try:
        # Get the current time
        current_time = datetime.datetime.now().isoformat()
        # Perform the update operation in the Supabase table
        response = supabase.table("booking").update({"status": "active", "check_in_time": current_time}).eq("rfid", rfid).execute()
    except Exception as e:
        print("Error updating booking status:", e)

# Main function
if __name__ == "__main__":
    try:
        while True:
            # Read RFID tag
            rfid = read_rfid()
            if rfid:
                # Check if the booking is pending
                data = check_pending_bookings(rfid)
                # Check if the booking is valid
                isBookingValid = False
                if data:
                    isBookingValid = check_valid_booking(data[0])
                if isBookingValid:
                    # Activate the distance sensor
                    calculateDistance = True
                    while calculateDistance:
                        distance = measure_distance()
                        # Open the gate
                        if distance and distance < 10:
                            calculateDistance = False
                        control_gate()
                        update_active_booking(rfid)
                time.sleep(1)
                time.sleep(1)
    except Exception as e:
        print("Error main:", e)
