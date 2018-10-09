import time, sys
import multiprocessing
from Adafruit_LED_Backpack import SevenSegment
from Adafruit_LED_Backpack import AlphaNum4


class lapTimer (object):
    def __init__ (self):
        ### DEFINE EVENT FLAGS #############
        self.startStopRequest = multiprocessing.Event()     
        self.startStopRequest.clear()

        self.lapResetRequest = multiprocessing.Event()     
        self.lapResetRequest.clear()
        ####################################


        ### SETUP DISPLAYS #################
        self.lapTimerDisplay = lapTimerDisplay()
        ####################################

    
        ### TIMER VALUES ###################
        self.currentElapsedTime  = 0
        self.previousElapsedTime = 0
        self.startTime           = 0
        self.isRunning           = False
        self.lapCounter          = 0
        ####################################

    
    def startLapTimer (self, stopFlag = None):
        timeOldDisplay = time.time()

        while not stopFlag.is_set():

            if self.startStopRequest.is_set():
                self.startStopToggle()
                self.startStopRequest.clear()

            if self.lapResetRequest.is_set():
                self.lapResetToggle()
                self.lapResetRequest.clear()

            if self.isRunning:
                self.currentElapsedTime = time.time() - self.startTime


            ### UPDATE DISPLAY EVERY 0.5 SECONDS ###
            if (timeOldDisplay + 0.5) < time.time():
                if self.isRunning:              
                    self.lapTimerDisplay.displayTime(self.currentElapsedTime, self.previousElapsedTime)
                    self.lapTimerDisplay.displayLap(self.lapCounter)
                timeOldDisplay = time.time()
 
        return


    def lapResetToggle (self):
        if self.isRunning:
            self.previousElapsedTime = self.currentElapsedTime
            self.currentElapsedTime  = 0
            self.startTime           = time.time()
            self.lapCounter         += 1

        elif not self.isRunning:
            self.currentElapsedTime  = 0
            self.previousElapsedTime = 0
            self.lapTimerDisplay.displayTime(self.currentElapsedTime, self.previousElapsedTime)

    def startStopToggle (self):
        if self.isRunning:
            self.stopTimer()
        elif not self.isRunning:
            self.startTimer()


    def startTimer (self):
        if not self.isRunning:
            self.startTime = time.time() - self.currentElapsedTime
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


class lapTimerDisplay (object):
    def __init__ (self):
        ### SETUP DISPLAYS #################
        self.currentLapDisplay = SevenSegment.SevenSegment(address=0x72)
        self.currentLapDisplay.begin()

        self.previousLapDisplay = SevenSegment.SevenSegment(address=0x73)
        self.previousLapDisplay.begin()

        self.lapDisplay = AlphaNum4.AlphaNum4(address=0x70)
        self.lapDisplay.begin()
        ####################################
        
        self.displayTime(0, 0)

    def displayLap (self, lapCount):
        self.lapDisplay.clear()

        self.lapDisplay.print_str(str(lapCount)[0:3])

        self.lapDisplay.write_display()

    def displayTime (self, currentElapsed, previousElapsed):
        ### FORMAT TIMES ###
        formatCurrent  = self.formatTime(currentElapsed)
        formatPrevious = self.formatTime(previousElapsed)

        ### UPDATE DISPLAYS ###
        self.setDisplay(self.currentLapDisplay, formatCurrent)
        self.setDisplay(self.previousLapDisplay, formatPrevious)

        ### TESTING ###
        #print("Current: " + str(formatCurrent[0]).zfill(2) + ":" + str(formatCurrent[1]).zfill(2) + \
        #      "  |  Previous: " + str(formatPrevious[0]).zfill(2) + ":" + str(formatPrevious[1]).zfill(2)) 


    def setDisplay (self, display, time):
        display.clear()

        ### SET MINUTES ###
        display.set_digit(0, int(time[0] / 10))
        display.set_digit(1, time[0] % 10)

        ### SET SECONDS ###
        display.set_digit(2, int(time[1] / 10))
        display.set_digit(3, time[1] % 10)

        display.set_colon(1)    

        display.write_display()
    
    def formatTime (self, elapsed):
        minutes = int(elapsed/60)
        seconds = int(elapsed - minutes * 60.0) 

        time = (minutes, seconds)   
        return time