import modules.flowSensor as flowSensorModule
import modules.lapTimer as lapTimerModule
import time, sys
import threading
import signal
import multiprocessing
import RPi.GPIO as GPIO



def main ():
    coreController = controller()
    #currentFuel = multiprocessing.Queue()

    #flowSensor = flowSensorModule.flowSensor()
    #flowSensorThread = multiprocessing.Process(target=flowSensor.startSensor , args=(currentFuel,))
    #flowSensorThread.start()


    #currentTimer = multiprocessing.Queue()

    #lapTimer = lapTimerModule.lapTimer()
    #lapTimerThread = multiprocessing.Process(target=lapTimer.startTimer, args=(currentTimer,))
    #lapTimerThread.start()


    #time.sleep(10)
    #print("setting flag\n")
    #lapTimer.setFlag()

    ### BUTTON EVENT HANDLERS
    # GPIO.setmode(GPIO.BCM)
    # inpt_btn = 16
    # GPIO.setup(inpt_btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.add_event_detect(inpt_btn, GPIO.RISING, callback=resetFuelEvent, bouncetime = 500)



    try:
        # timeOld = time.time()
        # fuel = 0
        # timer = 0
        while True:
            # if not currentFuel.empty():
            #     fuel = currentFuel.get_nowait()
            #     #print("Fuel: " + str(fuel))

            # if not currentTimer.empty():
            #     timer = currentTimer.get_nowait()
            #     #print("Time: " + str(timer) + "\n")

            # if (timeOld + 1) < time.time():
            #     timeOld = time.time()
            #     print("Fuel: " + str(fuel))
            #     print("Time: " + str(timer) + "\n")

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Terminating all processes.")
        coreController.killProcesses()
        #flowSensorThread.terminate()
        #lapTimerThread.terminate()

class controller(object):
    def __init__(self):
        ### CREATE PROCESS ARRAY ###
        self.processes = []

        self.flowSensor = self.setupFlowSensorProcesses()
        self.lapTimer = self.setupLapTimerProcess()

        ### SETUP BUTTON INPUT
        self.buttonController = buttons()
        self.setupButtons()

        ### START ALL PROCESSES
        self.startProcesses()


        time.sleep(8)
        self.buttonController.resetFuelTest()
        

    def startProcesses (self):
        for process in self.processes:
            try:
                process[1].start()
                print("Starting: " + str(process[0]))
            except:
                print("Error starting: " + str(process[0]))


    def killProcesses (self):
        for process in self.processes:
            try:
                process[1].terminate()
                print("Stopping: " + str(process[0]))
            except:
                print("Error stopping: " + str(process[0]))


    def setupButtons (self):
        self.buttonController.setFlowSensor(self.flowSensor)
        self.buttonController.setLapTimer(self.lapTimer)


    def setupFlowSensorProcesses (self):
        currentFuel = multiprocessing.Queue()

        flowSensor = flowSensorModule.flowSensor()
        flowSensorProcess = multiprocessing.Process(target = flowSensor.startSensor , args = (currentFuel,))
        
        process = ('Flow Sensor', flowSensorProcess)
        self.processes.append(process)

        return flowSensor


    def setupLapTimerProcess (self):
        currentTimer = multiprocessing.Queue()

        lapTimer = lapTimerModule.lapTimer()
        lapTimerProcess = multiprocessing.Process(target = lapTimer.startTimer, args = (currentTimer,))
        
        process = ('Lap Timer', lapTimerProcess)
        #self.processes.append(process)

        return lapTimer



class buttons (object):
    def __init__(self):
        ### DEFINE GPIO INPUT MODE
        GPIO.setmode(GPIO.BCM)

        ### DEFINE BUTTON PIN ASSIGNMENTS
        self.resetFuelButtonGPIO = 16 
        self.lapResetButtonGPIO = 21
        self.startStopButtonGPIO = 22
        self.modeButtonGPIO = 23
        self.buttonBounce = 400 
        ################################

        self.flowSensor = 0
        self.lapTimer = 0

        #time.sleep(2)
        #self.resetFuelTest()

    def setFlowSensor (self, flowSensor):
        self.flowSensor = flowSensor
    
        GPIO.setup(self.resetFuelButtonGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.resetFuelButtonGPIO, GPIO.RISING, callback = self.resetFuelEvent, bouncetime = self.buttonBounce)

    def setLapTimer (self, lapTimer):
        self.lapTimer = lapTimer

        GPIO.setup(self.startStopButtonGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.startStopButtonGPIO, GPIO.RISING, callback = self.timerStartStopEvent, bouncetime = self.buttonBounce)

        GPIO.setup(self.lapResetButtonGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.lapResetButtonGPIO, GPIO.RISING, callback = self.timerLapResetEvent, bouncetime = self.buttonBounce)
        

    def resetFuelEvent (channel):  
        self.flowSensor.setFuelResetFlag()

    def timerStartStopEvent (channel):  
        self.lapTimer.setStartStopFlag()

    def timerLapResetEvent (channel):  
        self.lapTimer.setLapResetFlag()

    def resetFuelTest (self):  
        self.flowSensor.setFuelResetFlag()    



if __name__== "__main__":
  main()