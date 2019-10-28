#!/usr/bin/env python

import time
import bluetooth
# ---------------------------------

# Wiiboard Parameters
CONTINUOUS_REPORTING = "04"  # Easier as string with leading zero
COMMAND_LIGHT = 11
COMMAND_REPORTING = 12
COMMAND_REQUEST_STATUS = 15
COMMAND_REGISTER = 16
COMMAND_READ_REGISTER = 17
INPUT_STATUS = 20
INPUT_READ_DATA = 21
EXTENSION_8BYTES = 32
BUTTON_DOWN_MASK = 8
TOP_RIGHT = 0
BOTTOM_RIGHT = 1
TOP_LEFT = 2
BOTTOM_LEFT = 3
BLUETOOTH_NAME = "Nintendo RVL-WBC-01"

################## NINTENDO WII Dimensions ########################
L=5.11 #cm
W=31.6 #cm

class Wiiboard:
    def __init__(self):
        # Sockets and status
        self.receivesocket = None
        self.controlsocket = None

        self.calibration = []
        self.calibrationRequested = False
        self.LED = False
        self.address = None
        self.buttonDown = False

        self.topLeft=0
        self.topRight=0
        self.bottomLeft=0
        self.bottomRight=0
        self.totalWeight=0
        
        ######################### Adjust factor calibration  #####################
        self.intercept_tl=-2.499061103079594
        self.intercept_tr=0.390595968811315
        self.intercept_bl=-0.12960121824766802
        self.intercept_br=-8.531223046687874
        
        self.slope_tl=0.2116462082928203
        self.slope_tr=0.3020363415303818
        self.slope_bl=0.2978469218881838
        self.slope_br=0.20257640991656814

        
        self.x = 0
        self.y = 0
        
        for i in xrange(3):
            self.calibration.append([])
            for j in xrange(4):
                self.calibration[i].append(10000)  # high dummy value so events with it don't register

        try:
            self.receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        except ValueError:
            raise Exception("Error: Bluetooth not found")

    def isConnected(self):
        return self.status == "Connected"

    # Connect to the Wiiboard at bluetooth address <address>
    def connect(self, address):
        if address is None:
            print "Non existant address"
            return
        self.receivesocket.connect((address, 0x13))
        self.controlsocket.connect((address, 0x11))
        if self.receivesocket and self.controlsocket:
            print "Connected to Wiiboard at address " + address
            self.status = "Connected"
            self.address = address
            self.calibrate()
            useExt = ["00", COMMAND_REGISTER, "04", "A4", "00", "40", "00"]
            self.send(useExt)
            self.setReportingType()
            print "Wiiboard connected"
        else:
            print "Could not connect to Wiiboard at address " + address
    def receive(self):
            data = self.receivesocket.recv(25)

            intype = int(data.encode("hex")[2:4])
        
            if intype == INPUT_STATUS:
                # TODO: Status input received. It just tells us battery life really
                self.setReportingType()
            elif intype == INPUT_READ_DATA:
                if self.calibrationRequested:
                    packetLength = (int(str(data[4]).encode("hex"), 16) / 16 + 1)
                    self.parseCalibrationResponse(data[7:(7 + packetLength)])

                    if packetLength < 16:
                        self.calibrationRequested = False
            elif intype == EXTENSION_8BYTES:
                self.createBoardEvent(data[2:12])
            else:
                print "ACK to data write received"

    def disconnect(self):
        if self.status == "Connected":
            self.status = "Disconnecting"
            while self.status == "Disconnecting":
                self.wait(100)
        try:
            self.receivesocket.close()
        except:
            pass
        try:
            self.controlsocket.close()
        except:
            pass
        print "WiiBoard disconnected"
	
    # Try to discover a Wiiboard
    def discover(self):
        print "Press the red sync button on the board now"
        
        address = None
        bluetoothdevices = bluetooth.discover_devices(duration=4, lookup_names=True)
        for bluetoothdevice in bluetoothdevices:
            if bluetoothdevice[1] == BLUETOOTH_NAME:
                address = bluetoothdevice[0]
                print "Found Wiiboard at address " + address
        if address is None:
            print "No Wiiboards discovered."
        return address

    def createBoardEvent(self, bytes):
        bytes = bytes[2:12]


        rawTR = (int(bytes[0].encode("hex"), 16) << 8) + int(bytes[1].encode("hex"), 16)
        rawBR = (int(bytes[2].encode("hex"), 16) << 8) + int(bytes[3].encode("hex"), 16)
        rawTL = (int(bytes[4].encode("hex"), 16) << 8) + int(bytes[5].encode("hex"), 16)
        rawBL = (int(bytes[6].encode("hex"), 16) << 8) + int(bytes[7].encode("hex"), 16)

#######################  Original equation ##########################
        # self.topLeft = self.calcMass(rawTL, TOP_LEFT)
        # self.topRight = self.calcMass(rawTR, TOP_RIGHT)
        # self.bottomLeft = self.calcMass(rawBL, BOTTOM_LEFT)
        # self.bottomRight = self.calcMass(rawBR, BOTTOM_RIGHT)

        ##### 0.25 = 1/4 of total mass value used in the calibration protocol

#######################  Adjust factor equation #######################
        self.topLeft = self.calcMass(rawTL, TOP_LEFT)*0.25/self.slope_tl-self.intercept_tl
        self.topRight = self.calcMass(rawTR, TOP_RIGHT)*0.25/self.slope_tr-self.intercept_tr
        self.bottomLeft = self.calcMass(rawBL, BOTTOM_LEFT)*0.25/self.slope_bl-self.intercept_bl
        self.bottomRight = self.calcMass(rawBR, BOTTOM_RIGHT)*0.25/self.slope_br-self.intercept_br

        self.totalWeight=self.topRight+self.bottomRight+self.topLeft+self.bottomLeft
        
        #self.x=L/2*((self.topRight+self.bottomRight)-(self.topLeft+self.bottomLeft))/self.totalWeight
        #self.y=W/2*((self.topRight+self.topLeft)-(self.bottomRight+self.bottomLeft))/self.totalWeight
        
        if self.totalWeight>0: 
      ####################### normalized -1:1  ################################
            self.x=((self.topRight+self.bottomRight)-(self.topLeft+self.bottomLeft))/self.totalWeight
            
            self.y=((self.topRight+self.topLeft)-(self.bottomRight+self.bottomLeft))/self.totalWeight


    def calcMass(self, raw, pos):
        val = 0.0
        #calibration[0] is calibration values for 0kg
        #calibration[1] is calibration values for 17kg
        #calibration[2] is calibration values for 34kg
        if raw < self.calibration[0][pos]:
            return val
        elif raw < self.calibration[1][pos]:
            val = 17 * ((raw - self.calibration[0][pos]) / float((self.calibration[1][pos] - self.calibration[0][pos])))
        elif raw > self.calibration[1][pos]:
            val = 17 + 17 * ((raw - self.calibration[1][pos]) / float((self.calibration[2][pos] - self.calibration[1][pos])))

        return val

    def getEvent(self):
        return self.lastEvent

    def getLED(self):
        return self.LED

    def parseCalibrationResponse(self, bytes):
        index = 0
        if len(bytes) == 16:
            for i in xrange(2):
                for j in xrange(4):
                    self.calibration[i][j] = (int(bytes[index].encode("hex"), 16) << 8) + int(bytes[index + 1].encode("hex"), 16)
                    index += 2
        elif len(bytes) < 16:
            for i in xrange(4):
                self.calibration[2][i] = (int(bytes[index].encode("hex"), 16) << 8) + int(bytes[index + 1].encode("hex"), 16)
                index += 2

    # Send <data> to the Wiiboard
    # <data> should be an array of strings, each string representing a single hex byte
    def send(self, data):
        if self.status != "Connected":
            return
        data[0] = "52"

        senddata = ""
        for byte in data:
            byte = str(byte)
            senddata += byte.decode("hex")

        self.controlsocket.send(senddata)

    #Turns the power button LED on if light is True, off if False
    #The board must be connected in order to set the light
    def setLight(self, light):
        if light:
            val = "10"
        else:
            val = "00"

        message = ["00", COMMAND_LIGHT, val]
        self.send(message)
        self.LED = light

    def calibrate(self):
        message = ["00", COMMAND_READ_REGISTER, "04", "A4", "00", "24", "00", "18"]
        self.send(message)
        self.calibrationRequested = True

    def setReportingType(self):
        bytearr = ["00", COMMAND_REPORTING, CONTINUOUS_REPORTING, EXTENSION_8BYTES]
        self.send(bytearr)

    def wait(self, millis):
        time.sleep(millis / 1000.0)


 


        



