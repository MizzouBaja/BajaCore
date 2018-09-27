import modules.flowSensor as flowSensorModule
import modules.lapTimer as lapTimerModule
import modules.buttons as buttonsModule
import time, sys
import multiprocessing
import RPi.GPIO as GPIO


def main ():
    ### INITIALIZE CONTROLLER ##########
    coreController = controller()
    ####################################

    ### START ALL PROCESSES ############
    coreController.startProcesses()
    ####################################

    ### WAIT FOR KEYBOARD INPUT ########
    try:
        print("Enter \"q\" to quit.\n\n")
        while True:
            inputBuffer = input()
            if inputBuffer:
                if inputBuffer == "q":
                    break
            else:
                pass

        coreController.killProcesses()

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt: Terminating all processes.")
        coreController.killProcesses()


class controller (object):
    def __init__ (self):
        ### CREATE PROCESS ARRAY ###########
        self.processes = []
        ####################################

        ### CREATE PROCESS STOP FLAG #######
        self.stopFlag = multiprocessing.Event()
        ####################################

        ### MODULE OBJECTS #################
        self.flowSensor = self.setupFlowSensorProcesses()
        self.lapTimer   = self.setupLapTimerProcess()
        ####################################

        ### SETUP BUTTON INPUT #############
        self.buttonController = buttonsModule.buttons()
        self.setupButtons()
        ####################################
        
        ### TESTING ###
        # time.sleep(8)
        # self.buttonController.resetFuelTest()
        # self.buttonController.timerStartStopTest()
        # self.buttonController.timerLapResetTest()
        # time.sleep(2)
        # self.buttonController.timerStartStopTest()
        

    def startProcesses (self):
        for process in self.processes:
            processName = str(process[0])
            try:
                print("Starting: " + processName)
                process[1].start()
            except:
                print("Error starting: " + processName)


    def killProcesses (self):
        print("\nStopping processes...")

        self.stopFlag.set()

        for process in self.processes:
            processName = str(process[0])
            try:   
                process[1].join()   
                print("Stopped: " + processName)            
            except:
                print("Error stopping: " + processName)


    def setupButtons (self):
        self.buttonController.setFlowSensor(self.flowSensor)
        self.buttonController.setLapTimer(self.lapTimer)


    def setupFlowSensorProcesses (self):
        flowSensor = flowSensorModule.flowSensor()
        flowSensorProcess = multiprocessing.Process(target = flowSensor.startSensor , args = (self.stopFlag,))
        
        process = ('Flow Sensor', flowSensorProcess)
        self.processes.append(process)

        return flowSensor


    def setupLapTimerProcess (self):
        lapTimer = lapTimerModule.lapTimer()
        lapTimerProcess = multiprocessing.Process(target = lapTimer.startTimer, args = (self.stopFlag,))
        
        process = ('Lap Timer', lapTimerProcess)
        self.processes.append(process)

        return lapTimer


if __name__ == "__main__":
  main()