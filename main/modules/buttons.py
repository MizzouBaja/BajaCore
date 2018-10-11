import time, sys
import RPi.GPIO as GPIO

class buttons (object):
    def __init__ (self):
        ### GPIO INPUT MODE ################
        GPIO.setmode(GPIO.BCM)
        ####################################

        ### DEFINE BUTTON PIN ASSIGNMENTS ##
        self.resetFuelButtonGPIO    = 5  # YELLOW
        self.lapResetButtonGPIO     = 13  # ORANGE 
        self.startStopButtonGPIO    = 26  # WHITE
        self.modeButtonGPIO         = 6  # GRAY
        self.buttonBounce           = 1000
        ####################################

        ### MODULE OBJECTS #################
        self.flowSensor = 0
        self.lapTimer   = 0
        ####################################

    def setFlowSensor (self, flowSensor):
        self.flowSensor = flowSensor
    
        GPIO.setup(self.resetFuelButtonGPIO, GPIO.IN)
        GPIO.add_event_detect(self.resetFuelButtonGPIO, GPIO.RISING, callback = self.resetFuelEvent, bouncetime = self.buttonBounce)

    def setLapTimer (self, lapTimer):
        self.lapTimer = lapTimer

        GPIO.setup(self.startStopButtonGPIO, GPIO.IN)
        GPIO.add_event_detect(self.startStopButtonGPIO, GPIO.RISING, callback = self.timerStartStopEvent, bouncetime = self.buttonBounce)

        GPIO.setup(self.lapResetButtonGPIO, GPIO.IN)       
        GPIO.add_event_detect(self.lapResetButtonGPIO, GPIO.RISING, callback = self.timerLapResetEvent, bouncetime = self.buttonBounce)

        GPIO.setup(self.modeButtonGPIO , GPIO.IN)        
        GPIO.add_event_detect(self.modeButtonGPIO , GPIO.RISING, callback = self.multiModeEvent, bouncetime = self.buttonBounce)

    def resetFuelEvent (self, channel): 
        if self.getHoldTime(channel) > 3:   
            self.flowSensor.setFuelResetFlag()

    def timerStartStopEvent (self, channel): 
        holdTime = self.getHoldTime(self.startStopButtonGPIO)

        if holdTime < 2 and holdTime > 0.1 and GPIO.input(self.startStopButtonGPIO) is 0: 
            self.lapTimer.setStartStopFlag()
        elif holdTime >= 2: 
            self.lapTimer.setLapModeToggleFlag()
            #time.sleep(1)
            
    def timerLapResetEvent (self, channel):  
        self.lapTimer.setLapResetFlag()

    def multiModeEvent (self, channel): 
        if GPIO.input(self.modeButtonGPIO) is 1:
            self.lapTimer.setMultiModeFlag()
        #time.sleep(0.1)

    def getHoldTime (self, channel):
        start = time.time()
        gpio_cur = GPIO.input(channel)
        while gpio_cur is 1:
            #time.sleep(0.02)
            gpio_cur = GPIO.input(channel)

        length = time.time() - start
        return length
    
    ### TESTING ###
    def resetFuelTest (self):  
        self.flowSensor.setFuelResetFlag()  

    def timerStartStopTest (self):  
        self.lapTimer.setStartStopFlag()

    def timerLapResetTest (self):  
        self.lapTimer.setLapResetFlag()  
