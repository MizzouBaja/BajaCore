import modules.flowSensor as flowSensorModule
import modules.lapTimer as lapTimerModule
import modules.buttons as buttonsModule
import time, sys
import multiprocessing


def main ():
    ### INITIALIZE CONTROLLER ##########
    coreController = controller()
    ####################################

    ### START ALL PROCESSES ############
    coreController.startProcesses()
    ####################################


    ### WAIT FOR KEYBOARD INPUT ########
    try:
        print("\nEnter \"q\" to quit.")
        print("Enter \"s\" to start/stop timer.")
        print("Enter \"r\" to lap/reset timer.\n")
        while True:
            inputBuffer = input()
            if inputBuffer:
                if inputBuffer == "q":
                    break
                if inputBuffer == "s":
                    coreController.buttonController.timerStartStopTest()
                if inputBuffer == "r":
                    coreController.buttonController.timerLapResetTest()
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
        lapTimerProcess = multiprocessing.Process(target = lapTimer.startLapTimer, args = (self.stopFlag,))
        
        process = ('Lap Timer', lapTimerProcess)
        self.processes.append(process)

        return lapTimer


if __name__ == "__main__":
  main()