import RPi.GPIO as GPIO
from time import sleep

# BCM-Nummerierung verwenden
GPIO.setmode(GPIO.BCM)

# GPIO 17 (Pin 11) als Eingang setzen
GPIO.setup(17, GPIO.IN)
GPIO.setup(18, GPIO.IN)

# Wiederholung (Endlos-Schleife)
while True:
    value_d1 = GPIO.input(17)
    value_d2 = GPIO.input(18)
    print(value_d1, value_d2)
    sleep(0.2)
    
# Benutzte GPIOs freigeben
GPIO.cleanup()
