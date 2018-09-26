import RPi.GPIO as GPIO
import time, sys
from Adafruit_LED_Backpack import AlphaNum4
from Adafruit_LED_Backpack import BicolorBargraph24
import math
import multiprocessing

currentFuelGlobal = 0

class flowSensor(object):
    def __init__(self):
        # Create display instance on default I2C address (0x70) and bus number.
        #self.display = AlphaNum4.AlphaNum4(address=0x70)
        self.barDisplay = BicolorBargraph24.BicolorBargraph24(address=0x71, busnum=1)

        # Initialize the display.
        #self.display.begin()
        self.barDisplay.begin()
        self.barDisplay.set_brightness(15)


        ####################################
        ## GPIO INPUT MODE
        ####################################
        GPIO.setmode(GPIO.BCM)
        ####################################


        ####################################
        ## GPIO PIN 13 FLOW METER
        ####################################
        self.inpt_flow = 13
        GPIO.setup(self.inpt_flow, GPIO.IN)
        ####################################


        ####################################
        ## GPIO PIN 16 RESET FUEL
        ####################################
        self.inpt_btn = 16
        #GPIO.setup(self.inpt_btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        ####################################


        ####################################
        ## SET STATIC VALUES
        ####################################
        self.maxFuel = 100
        self.pulseIncrement = 0.01
        self.saveDelaySeconds = 10
        ####################################

        
        ####################################
        ## GET SAVED DATA
        ####################################
        fileLocation = '/srv/baja/BajaCore/main/saveData'
        fileName = 'currentFuel.txt'
        self.filePath = fileLocation + '/' + fileName
        self.currentFuel = float(self.openCurrentFuel(self.filePath))
        print("Current fuel: " + str(self.currentFuel))
        ####################################

        ####################################
        ## THREAD RESET REQUEST
        ####################################
        self.resetRequest = multiprocessing.Event()     
        self.resetRequest.clear()

        self.processStopFlag = multiprocessing.Event() 
        self.processStopFlag.clear()   
        ####################################
        

    def startSensor(self, currentFuelListener):
        gpio_last = 0
        
        timeOld = time.time()

        timeOldTESTING = time.time()

        testCounter = 0

        gpio_last = GPIO.input(self.inpt_flow)

        flashToggle = False

        while not self.processStopFlag.is_set():
            gpio_cur = GPIO.input(self.inpt_flow)
            
            if gpio_cur != 0 and gpio_cur != gpio_last:
                self.currentFuel -= 0.1 
                testCounter += 1
                print("Counter: " + str(testCounter))
                #100 mL == 487 pulses
                #100 mL == 488 pulses
                #100 mL == 426 pulses poured fast
                #200 mL == 976 pulses
                #100 mL == 447 pulses half fast 
                #200 mL == 847 pulses slow
                #print("input\n")
        
            gpio_last = gpio_cur

            #if GPIO.input(self.inpt_btn) == True:
            #    print("Button press")
            #    self.currentFuel = self.maxFuel
            #    time.sleep(1)

            if self.resetRequest.is_set():
                self.currentFuel = self.maxFuel
                self.resetRequest.clear()


            #self.displayCurrentValue(self.currentFuel)
            #self.displayCurrentValueBar(self.currentFuel)
            
            ### SAVE FUEL VALUE EVERY N SECONDS ###
            if (timeOld + self.saveDelaySeconds) < time.time():
                print("Writing fuel.")
                timeOld = time.time()
                self.saveCurrentFuel(self.filePath, self.currentFuel)
                #print("Fuel: " + str(self.currentFuel))

            
            ### TETSING ###
            
            if (timeOldTESTING + 1) < time.time():
                self.displayCurrentValueBar(self.currentFuel, flashToggle)
                timeOldTESTING = time.time()
                if flashToggle is True:
                    flashToggle = False
                elif flashToggle is False:
                    flashToggle = True
                self.currentFuel -= 0.01
                print("Fuel: " + str(self.currentFuel)) 
                #currentFuelListener.put_nowait(self.currentFuel)


            #self.currentFuel -= 0.001 
            #print("Fuel: " + str(self.currentFuel))
            #currentFuelListener.put_nowait(self.currentFuel)
            #time.sleep(1)

        self.saveCurrentFuel(self.filePath, self.currentFuel)

        #self.display.clear()
        #self.display.print_str('Baja')
        #self.display.write_display()

    def getCurrentFuel(self):
        return self.currentFuel

    def displayCurrentValue (self, currentFuel):
        # Clear current display
        self.display.clear()

        # Write to display buffer
        self.display.print_float(currentFuel)

        # Update display with buffer
        self.display.write_display()

        
        
    def displayCurrentValueBar (self, currentFuel, flashToggle):
        currentFuelPercentage = currentFuel / self.maxFuel
        
        barLevel = math.ceil(24 * currentFuelPercentage)
    
        
        # Clear current display
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
            if flashToggle is True:
                for barindex in range(24):
                    self.barDisplay.set_bar(barindex, BicolorBargraph24.RED)


        # Update display with buffer
        self.barDisplay.write_display()
        
        
    def openCurrentFuel (self, filePath):
        currentFuel = 0

        try:
            saveFile = open(filePath, "r")
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
            saveFile = open(filePath, "w")
            saveFile.write(str(currentFuel))
            saveFile.close()
            
        except IOError:
            print(filePath + "\nError saving current fuel.\n")


    def setFuelResetFlag(self, timeout=None):
        print("Got fuel reset request")
        self.resetRequest.set()


    def setProcessStopFlag(self, timeout=None):
        print("Got process request")
        self.processStopFlag.set()
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        