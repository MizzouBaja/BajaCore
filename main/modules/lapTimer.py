import RPi.GPIO as GPIO
import time, sys
from Adafruit_LED_Backpack import AlphaNum4
import threading
import multiprocessing
import datetime

class lapTimer (object):
    def __init__(self):
        ###  DEFINE EVENT FLAGS  
        self.startStoprequest = multiprocessing.Event()     
        self.startStoprequest.clear()

        self.lapResetrequest = multiprocessing.Event()     
        self.lapResetrequest.clear()

        self.counter = 0

    
    def startTimer (self, currentTimerListener):
        #startTime = time.time()
        startTime = datetime.datetime.now()
        timeOld = time.time()

        currentTime = ""

        currentSeconds = 0
        currentMinutes = 0

        while not self.stoprequest.is_set():
            elapsed = datetime.datetime.now() - startTime

            #currentSeconds += elapsed.seconds

            if (elapsed.seconds + 1) < elapsed.seconds:
                currentSeconds += 1
                if currentSeconds >= 60:
                    currentSeconds = 0
                    currentMinutes += 1

            if (timeOld + 1) < time.time():
                timeOld = time.time()

                currentTime = str(currentMinutes) + ":" + str(currentSeconds)
                currentTimerListener.put_nowait(currentTime)

        print("stopped\n")        


    def setFlag(self, timeout=None):
        print("Got stop request")
        self.stoprequest.set()
    
    def setStartStopFlag(self, timeout=None):
        print("Got Start/Stop request")
        self.startStopRequest.set()

    def setLapResetFlag(self, timeout=None):
        print("Got Lap/Reset request")
        self.lapResetRequest.set()