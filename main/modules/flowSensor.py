import time, sys
import math
import multiprocessing
import RPi.GPIO as GPIO
from Adafruit_LED_Backpack import BicolorBargraph24



class flowSensor (object):
    def __init__ (self):
        ### INITIALIZE DISPLAY #############
        self.fuelDisplay = fuelDisplay()
        ####################################

        ### GPIO INPUT MODE ################
        GPIO.setmode(GPIO.BCM)
        ####################################

        ### GPIO PIN 13 FLOW METER #########
        self.flowSensorInput = 13
        GPIO.setup(self.flowSensorInput, GPIO.IN)
        ####################################

        ### SET STATIC VALUES ##############
        self.maxFuel            = 100
        self.pulseIncrement     = 0.01
        self.saveDelaySeconds   = 10
        ####################################

        ### GET SAVED DATA #################
        fileLocation = '/srv/baja/BajaCore/main/saveData'
        fileName = 'currentFuel.txt'
        self.filePath = fileLocation + '/' + fileName
        self.currentFuel = round(float(self.openCurrentFuel(self.filePath)), 2)
        ####################################

        ### FUEL RESET REQUEST #############
        self.resetRequest = multiprocessing.Event()     
        self.resetRequest.clear() 
        ####################################
        

    def startSensor (self, stopFlag = None):
        print("Current fuel: " + str(self.currentFuel))

        timeOldFile    = time.time()
        timeOldDisplay = time.time()

        testCounter = 0

        gpio_last = GPIO.input(self.flowSensorInput)

        while not stopFlag.is_set():
            gpio_cur = GPIO.input(self.flowSensorInput)
            
            if gpio_cur != 0 and gpio_cur != gpio_last:
                self.currentFuel -= self.pulseIncrement

                ### TESTING ###
                testCounter += 1
                print("Counter: " + str(testCounter))  
            gpio_last = gpio_cur


            ### CHECK FOR FUEL LEVEL RESET ###
            if self.resetRequest.is_set():
                self.currentFuel = self.maxFuel
                self.resetRequest.clear()

            
            ### SAVE FUEL VALUE EVERY N SECONDS ###
            if (timeOldFile + self.saveDelaySeconds) < time.time():
                timeOldFile = time.time()
                self.saveCurrentFuel(self.filePath, self.currentFuel)


            ### UPDATE DISPLAY EVERY 1 SECOND ###
            if (timeOldDisplay + 1) < time.time():
                self.fuelDisplay.displayFuel(self.currentFuel, self.maxFuel)
                timeOldDisplay = time.time()

                ### TESTING ###
                self.currentFuel -= 0.1
                print("Fuel: " + str(round(self.currentFuel, 2))) 

        ### SAVE FUEL BEFORE EXITING ###
        self.saveCurrentFuel(self.filePath, self.currentFuel) 
        return


    def openCurrentFuel (self, filePath):
        currentFuel = 0

        try:
            saveFile    = open(filePath, "r")
            currentFuel = saveFile.read()
            saveFile.close()
            
            if currentFuel:
                return currentFuel
            else:
                print("Couldnt read fuel value. Setting to max.")
                currentFuel = self.maxFuel
                self.saveCurrentFuel(filePath, currentFuel)

                return currentFuel
            
        except IOError:
            print(filePath + "\nDoes not exist. Creating with max fuel.\n")
            currentFuel = self.maxFuel
            self.saveCurrentFuel(filePath, currentFuel)
            
            return currentFuel
            
    
    def saveCurrentFuel (self, filePath, currentFuel):
        try:
            print("Writing fuel.")
            saveFile = open(filePath, "w")
            saveFile.write(str(round(currentFuel, 2)))
            saveFile.close()
            
        except IOError:
            print(filePath + "\nError saving current fuel.\n")


    def setFuelResetFlag(self, timeout = None):
        print("Got fuel reset request")
        self.resetRequest.set()
            
        
class fuelDisplay (object):
    def __init__ (self):
        ### CREATE DISPLAY INSTANCE ########
        self.barDisplay = BicolorBargraph24.BicolorBargraph24(address=0x71, busnum=1)
        ####################################

        ### INITIALIZE DISPLAY #############
        self.barDisplay.begin()
        self.barDisplay.set_brightness(15)  
        ####################################  

        self.flashToggle = True 


    def displayFuel (self, currentFuel, maxFuel):   
        currentFuelPercentage = currentFuel / maxFuel
        
        barLevel = math.ceil(24 * currentFuelPercentage)
    
        ### Clear current display ###
        self.barDisplay.clear()

        if int(barLevel) > 4:
            for barindex in range(int(barLevel)):
                if barindex <= 4:
                    self.barDisplay.set_bar(barindex, BicolorBargraph24.RED)
                if barindex <= 12 and barindex > 4:
                    self.barDisplay.set_bar(barindex, BicolorBargraph24.YELLOW)
                if barindex <= 24 and barindex > 12:
                    self.barDisplay.set_bar(barindex, BicolorBargraph24.GREEN)

        elif int(barLevel) <= 4:
            if self.flashToggle is True:
                self.flashToggle = False

                for barindex in range(24):
                    self.barDisplay.set_bar(barindex, BicolorBargraph24.RED)    

            else:
                self.flashToggle = True

        ### UPDATE DISPLAY ###
        self.barDisplay.write_display()

        
    