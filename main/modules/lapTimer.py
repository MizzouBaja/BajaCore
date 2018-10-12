import time, sys
import datetime
import multiprocessing
from Adafruit_LED_Backpack import SevenSegment
from Adafruit_LED_Backpack import AlphaNum4


class lapTimer (object):
    def __init__ (self):
        ### DEFINE EVENT FLAGS #############
        self.initEvents()
        ####################################

        ### SETUP LOGGER ###################
        self.timeLogger = timeLogger()
        ####################################

        ### SETUP DISPLAYS #################
        self.lapTimerDisplay = lapTimerDisplay()
        ####################################

    
        ### TIMER VALUES ###################
        self.currentElapsedTime  = 0
        self.fastestTime         = 0
        self.previousElapsedTime = 0
        self.startTime           = 0
        self.isRunning           = False
        self.lapCounter          = 0
        ####################################


        ### SETUP DISPLAYS #################
        self.currentLapMode = 0
        self.currentMultiMode = 0
        ####################################

    
    def startLapTimer (self, stopFlag = None):
        timeOldDisplay = time.time()

        while not stopFlag.is_set():
            self.checkFlags()

            if self.isRunning:
                self.currentElapsedTime = time.time() - self.startTime

            ### UPDATE DISPLAY EVERY 0.5 SECONDS ###
            if (timeOldDisplay + 0.5) < time.time():
                self.updateDisplays()
                timeOldDisplay = time.time()
 
        return


    def updateDisplays (self):
        ### CURRENT LAP MODE ###
        if self.currentLapMode is 0:
            self.lapTimerDisplay.displayTime(self.currentElapsedTime, self.previousElapsedTime)
        if self.currentLapMode is 1:
            self.lapTimerDisplay.displayTime(self.currentElapsedTime, self.fastestTime)

        ### CURRENT MULTI-MODE ###
        if self.currentMultiMode is 0:
            self.lapTimerDisplay.displayLap(self.lapCounter)
        if self.currentMultiMode is 1:
            self.lapTimerDisplay.displayShowOff()


    def lapModeToggle (self):
        maxMode = 1

        running = self.isRunning
        if self.currentLapMode < maxMode:
            self.currentLapMode += 1
        elif self.currentLapMode >= maxMode:
            self.currentLapMode = 0

        self.lapTimerDisplay.displayMode(self.currentLapMode)
        self.isRunning = running


    def multiModeToggle (self):
        maxMode = 1

        if self.currentMultiMode < maxMode:
            self.currentMultiMode += 1
        elif self.currentMultiMode >= maxMode:
            self.currentMultiMode = 0


    def resetLapCount (self):
        self.lapCounter = 0
        self.fastestTime = 0
        self.lapTimerDisplay.displayMessage('LAP RESET')


    def lapResetToggle (self):
        if self.isRunning:
            if self.currentElapsedTime < self.fastestTime:
                self.fastestTime = self.currentElapsedTime
                #self.lapTimerDisplay.displayMessage('NEW BEST')
            elif self.fastestTime is 0:
                self.fastestTime = self.currentElapsedTime

            if self.currentElapsedTime > 30:
                self.timeLogger.writeLap(self.currentElapsedTime, self.lapCounter)

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

    def displayFuelReset (self):
        self.lapTimerDisplay.displayMessage('FUEL RESET')

    def setStartStopFlag (self, timeout=None):
        #print("Got Start/Stop request")
        self.startStopRequest.set()

    def setLapResetFlag (self, timeout=None):
        #print("Got Lap/Reset request")
        self.lapResetRequest.set()

    def setLapCoutnerResetFlag (self, timeout=None):
        #print("Got Lap Counter Reset request")
        self.lapCounterResetRequest.set()

    def setLapModeToggleFlag (self, timeout=None):
        #print("Got Mode toggle request")
        self.lapModeToggleRequest.set()

    def setMultiModeFlag (self, timeout=None):
        #print("Got multi Mode toggle request")
        self.multiModeToggleRequest.set()

    def setFuelResetFlag (self, timeout=None):
        #print("Got fuel reset display request")
        self.fuelResetRequest.set()


    def checkFlags (self):
        if self.startStopRequest.is_set():
            self.startStopToggle()
            self.startStopRequest.clear()

        if self.lapResetRequest.is_set():
            self.lapResetToggle()
            self.lapResetRequest.clear()

        if self.lapCounterResetRequest.is_set():
            self.resetLapCount()
            self.lapCounterResetRequest.clear()

        if self.lapModeToggleRequest.is_set():
            self.lapModeToggle()
            self.lapModeToggleRequest.clear()

        if self.multiModeToggleRequest.is_set():
            self.multiModeToggle()
            self.multiModeToggleRequest.clear()
        
        if self.fuelResetRequest.is_set():
            self.displayFuelReset()
            self.fuelResetRequest.clear()

    def initEvents (self):
        self.startStopRequest = multiprocessing.Event()     
        self.startStopRequest.clear()

        self.lapResetRequest = multiprocessing.Event()     
        self.lapResetRequest.clear()

        self.lapCounterResetRequest = multiprocessing.Event()     
        self.lapCounterResetRequest.clear()

        self.lapModeToggleRequest = multiprocessing.Event()     
        self.lapModeToggleRequest.clear()

        self.multiModeToggleRequest = multiprocessing.Event()     
        self.multiModeToggleRequest.clear()

        self.fuelResetRequest = multiprocessing.Event()     
        self.fuelResetRequest.clear() 

class lapTimerDisplay (object):
    def __init__ (self):
        ### SETUP DISPLAYS #################
        self.currentLapDisplay = SevenSegment.SevenSegment(address=0x72)
        self.currentLapDisplay.begin()
        self.currentLapDisplay.clear()

        self.previousLapDisplay = SevenSegment.SevenSegment(address=0x73)
        self.previousLapDisplay.begin()
        self.previousLapDisplay.clear()

        self.multiDisplay = AlphaNum4.AlphaNum4(address=0x70)
        self.multiDisplay.begin()
        self.multiDisplay.clear()
        ####################################
        
        self.displayTime(0, 0)
        self.textIndex = 0


    def displayLap (self, lapCount):
        self.multiDisplay.clear()
        self.multiDisplay.print_str(str(lapCount)[0:3])
        self.multiDisplay.write_display()


    def displayMode (self, mode):
        if mode is 0:
            message = 'LAST'
        if mode is 1:
            message = 'FAST'

        self.displayMessage(message)


    def displayShowOff (self):
        #message = '   Mizzou Baja    '
        message = '   MIZZOU BAJA    '

        self.multiDisplay.clear()
        self.multiDisplay.print_str(message[self.textIndex:self.textIndex+4])
        self.multiDisplay.write_display()

        self.textIndex += 1
        if self.textIndex > len(message)-4:
            self.textIndex = 0


    def displayTime (self, currentElapsed, previousElapsed):
        ### FORMAT TIMES ###
        formatCurrent  = self.formatTime(currentElapsed)
        formatPrevious = self.formatTime(previousElapsed)

        ### UPDATE DISPLAYS ###
        self.setDisplay(self.currentLapDisplay, formatCurrent)
        self.setDisplay(self.previousLapDisplay, formatPrevious)


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

    def displayMessage (self, message):
        messageIndex = 0
        message = '    ' + message + '   '

        while messageIndex < len(message):
            self.multiDisplay.clear()
            self.multiDisplay.print_str(message[messageIndex:messageIndex+4])
            self.multiDisplay.write_display()

            messageIndex += 1
            if messageIndex < len(message) + 2:
                time.sleep(0.2)


class timeLogger (object):
    def __init__ (self):
        self.logCount = 0

        ### FILE SETTINGS ##################
        fileLocation = '/srv/baja/BajaCore/main/saveData'
        fileName = 'lapLog.txt'
        self.filePath = fileLocation + '/' + fileName
        ####################################
        
    def writeLap (self, time, lap):
        newLog = '< ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' > | '
        newLog += 'Lap: ' + str(lap) + ' | '
        newLog += 'Time: ' + self.formatTime(time) + ' |'
        newLog += '\n'

        try:
            saveFile = open(self.filePath, "a")
            saveFile.write(newLog)
            saveFile.close()
            print("Writing Lap")
            
        except IOError:
            print(self.filePath + "\nError saving lap log.\n")

    def formatTime (self, elapsed):
        minutes = int(elapsed/60)
        seconds = int(elapsed - minutes * 60.0) 

        time = str(minutes) + ':' + str(seconds)   
        return time