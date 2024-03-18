# Libraries
import RPi.GPIO as GPIO
import time

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
BUZZER_PIN = 6  # تعيين المنفذ المستخدم للبازر

# LCD GPIO mapping
LCD_RS = 4
LCD_E = 17
LCD_D4 = 27
LCD_D5 = 22
LCD_D6 = 23
LCD_D7 = 25

# Define some device constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)  # تعيين المنفذ الخاص بالبازر كمخرج
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT)  # RS
GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
GPIO.setup(LCD_D7, GPIO.OUT)  # DB7

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    
    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    
    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    
    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    
    return distance

def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command

    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

def lcd_toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def main():
    try:
        lcd_init()  # Initialize LCD
        while True:
            dist = distance()
            print("Measured Distance = %.1f cm" % dist)
            if dist < 50:  # إذا كانت المسافة أقل من 30 سم
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # تشغيل البازر
                lcd_string("Object Close!%.1f cm" % dist, LCD_LINE_2)  # إظهار رسالة على الشاشة
            else:
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # إيقاف البازر
                lcd_string("Distance: %.1f cm" % dist, LCD_LINE_2)  # إظهار المسافة على الشاشة
            time.sleep(1)

    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        lcd_string("Measurement stopped", LCD_LINE_2)
        GPIO.cleanup()

if __name__ == '__main__':
    main()  # استدعاء الدالة الرئيسية
