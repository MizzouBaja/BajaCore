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
        self.buttonBounce           = 400 
        ####################################

        ### MODULE OBJECTS #################
        self.flowSensor = 0
        self.lapTimer   = 0
        ####################################

    def setFlowSensor (self, flowSensor):
        self.flowSensor = flowSensor
    
        GPIO.setup(self.resetFuelButtonGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        #GPIO.add_event_detect(self.resetFuelButtonGPIO, GPIO.RISING, callback = self.resetFuelEvent, bouncetime = self.buttonBounce)

    def setLapTimer (self, lapTimer):
        self.lapTimer = lapTimer

        GPIO.setup(self.startStopButtonGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.startStopButtonGPIO, GPIO.FALLING, callback = self.timerStartStopEvent, bouncetime = self.buttonBounce)

        GPIO.setup(self.lapResetButtonGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.lapResetButtonGPIO, GPIO.FALLING, callback = self.timerLapResetEvent, bouncetime = self.buttonBounce)
        

    def resetFuelEvent (self, channel):  
        self.flowSensor.setFuelResetFlag()

    def timerStartStopEvent (self, channel):  
        self.lapTimer.setStartStopFlag()

    def timerLapResetEvent (self, channel):  
        self.lapTimer.setLapResetFlag()

    
    ### TESTING ###
    def resetFuelTest (self):  
        self.flowSensor.setFuelResetFlag()  

    def timerStartStopTest (self):  
        self.lapTimer.setStartStopFlag()

    def timerLapResetTest (self):  
        self.lapTimer.setLapResetFlag()  