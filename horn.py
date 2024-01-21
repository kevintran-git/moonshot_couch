try:
    # RPI GPIO docs: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


def call_horn():
    # PIN Output is GPIO4, pin 7
    output_pin = 7 # pin number that we are outputting. If it is going to be changed, refer to this chart: https://raspi.tv/2013/rpi-gpio-basics-4-setting-up-rpi-gpio-numbering-systems-and-inputs
    # Initialize input/output
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(output_pin, GPIO.OUT)

    try:  
        while True:            # this will carry on until you hit CTRL+C  
            if GPIO.input(25): # if port 25 == 1  
                # print "Port 25 is 1/GPIO.HIGH/True - button pressed"  
                GPIO.output(output_pin, GPIO.HIGH)
            else:  
                # print "Port 25 is 0/GPIO.LOW/False - button not pressed"  
            sleep(0.1)         # wait 0.1 seconds  
    
    except KeyboardInterrupt:  
        GPIO.cleanup() 
    return True

call_horn()