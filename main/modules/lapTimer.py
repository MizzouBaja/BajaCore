import RPi.GPIO as GPIO
import time, sys
import multiprocessing
from Adafruit_LED_Backpack import SevenSegment

class lapTimer (object):
    def __init__ (self):
        ### DEFINE EVENT FLAGS #############
        self.startStopRequest = multiprocessing.Event()     
        self.startStopRequest.clear()

        self.lapResetRequest = multiprocessing.Event()     
        self.lapResetRequest.clear()
        ####################################

        ### SETUP DISPLAYS #################
        #self.currentLapDisplay = SevenSegment.SevenSegment(address=0x72)
        #self.currentLapDisplay.begin()

        #self.lastLapDisplay = SevenSegment.SevenSegment(address=0x73)
        #self.lastLapDisplay.begin()
        ####################################

        self.isRunning = False

        self.elapsedTime = 0
        self.startTime   = 0

        self.currentSeconds = 0
        self.currentMinutes = 0

        self.previousSeconds = 0
        self.previousMinutes = 0

    
    def startTimer (self, stopFlag = None):
        timeOld = time.time()

        self.startClock()

        while not stopFlag.is_set():

            if self.startStopRequest.is_set():
                self.startStopToggle()
                self.startStopRequest.clear()

            if self.lapResetRequest.is_set():
                self.lapResetToggle()
                self.lapResetRequest.clear()

            if self.isRunning:
                self.elapsedTime = time.time() - self.startTime
                timeStr = self.getTime(self.elapsedTime)


            if (timeOld + 1) < time.time():
                timeOld = time.time()
                #print(timeStr)

        return

    def lapResetToggle (self):
        if self.isRunning:
            self.previousSeconds = self.currentSeconds
            self.previousMinutes = self. currentMinutes

        elif not self.isRunning:
            self.currentSeconds = 0
            self.currentMinutes = 0
            self.elapsedTime    = 0


    def startStopToggle (self):
        if self.isRunning:
            self.stopTimer()
            self.isRunning = False
        elif not self.isRunning:
            self.startClock()
            self.isRunning = True


    def getTime(self, elap):
        minutes = int(elap/60)
        seconds = int(elap - minutes * 60.0) 

        self.currentMinutes = minutes     
        self.currentSeconds = seconds 
        timeStr = (str(minutes).zfill(2) + ":" + str(seconds).zfill(2))   
        return timeStr 


    def startClock (self):
        if not self.isRunning:
            self.startTime = time.time() - self.elapsedTime
            self.isRunning = True


    def stopTimer (self):
        if self.isRunning:
            self.isRunning = False
    

    def setStartStopFlag (self, timeout=None):
        print("Got Start/Stop request")
        self.startStopRequest.set()


    def setLapResetFlag (self, timeout=None):
        print("Got Lap/Reset request")
        self.lapResetRequest.set()


