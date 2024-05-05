from gpiozero import DistanceSensor, Buzzer
from rpi_lcd import LCD
from RPi import GPIO
from time import sleep
import board
import adafruit_dht
import math

sound = DistanceSensor(echo=20, trigger=21)
temp = adafruit_dht.DHT11(board.D26)
buzzer = Buzzer(16)
lcd = LCD()
reset = 12

GPIO.setup(reset, GPIO.OUT)

count = 0


def buzz():
    buzzer.on()
    sleep(0.1)
    buzzer.off()
    sleep(0.06)
    buzzer.on()
    sleep(0.1)
    buzzer.off()



try:
    while True:
        GPIO.output(reset, GPIO.HIGH)
        #print("high")
        #measuring distance
        distance = math.floor(sound.value1000)/10
        sleep (1)
        value = math.floor(sound.value1000)/10

        #temp and humi sensor
        #temp_c = temp.temperature
        humi = temp.humidity


        #display printing
        #print ("distance: ", distanc e, "  value ", value)
        lcd.text("distance:" + str(distance), 1)
        lcd.text("Temp:{0:0.1f}C".format(temp.temperature), 2)
        lcd.text("Humi:{0:0.1f}%".format(humi), 3)
        lcd.text(f"Mail: " + str(count), 4)

        if GPIO.input(reset) == GPIO.LOW:
            count = 0
        else:
            pass

        if value < distance:
            #print ("buzz")
            buzz()
            count = count+1

        elif value == distance:
            pass


except KeyboardInterrupt:
    print ("closing. . .")
    sound.close()
    temp.exit()
    lcd.clear()
    GPIO.cleanup() 
