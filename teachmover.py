''' 
****************************************
* Microbot TeachMover Control Software *
****************************************

This software allows for the control of a TeachMover robotic arm via serial connection. 
Ideally, this class should be imported into other programs and used solely for control.
The bot has a total of ten built-in serial commands, 8 of which will be implemented:

    @STEP       Move all steppers synchronously
    @CLOSE      Close the gripper, not much force
    @SET        Activate handheld teach control
    @RESET      Reset internal position registers / motor current shutoff
    @READ       Read values stored in internal position registers
    @QDUMP      Dump the program currently stored in memory.
    @QWRITE     Reupload a perviously dumped program.
    @RUN        Run the program currently stored in memory.

    The below commands are not implemented, mainly because there's not much
    use for them if this software is being used. 

    @ARM        Change response character from default "@"
    @DELAY      Insert a delay between TX chars.

    Potential functions to add in the future:
    HOME        home the arm (using internal position register values)
    GRIP        grip an object + 32 steps to add ~1 lb of force
    MEASURE     measure an object using the gripper

    I'd like to be able to move the bot via x, y, z coordinates as well but this could prove challenging. 
    This is more of a long-term goal. 
'''

import serial
import time
import numpy as np

#The result object consists of a success code and a data (where applicable)
#It is returned by all movement functions.
class Result:
    def __init__(self, statusCode: int, data = None):
        self.statusCode = statusCode
        self.data = data


class TeachMover:

    #Init function
    def __init__(self, portID: str, baudRate = 9600):
        try:
            '''
                TEACHMOVER DEFAULT SERIAL CONFIGURATION
                Baud rate:      9600bps
                Word length:    8 bits
                Start bits:     1
                Stop bits:      1
                Pairity bits:   None
                Duplexing:      Full duplex
            '''
            self.con = serial.Serial(portID, baudRate)

            #Motor 1 (Base)
            self.motor1 = {
                "steps_rev":7072,
                "steps_rad":1125,
                "steps_deg":19.64
            }
            #Motor 2 (Shoulder)
            self.motor2 = {
                "steps_rev":7072,
                "steps_rad":1125,
                "steps_deg":19.64
            }
            #Motor 3 (Elbow)
            self.motor3 = {
                "steps_rev":4158,
                "steps_rad":661.2,
                "steps_deg":11.55
            }
            #Motor 4 (Right Wrist)
            self.motor4 = {
                "steps_rev":1536,
                "steps_rad":241,
                "steps_deg":4.27
            }
            #Motor 5 (Left Wrist)
            self.motor5 = {
                "steps_rev":1536,
                "steps_rad":241,
                "steps_deg":4.27
            }           

        except Exception as e:
            print(e)

    #Private function to send a single command to the robot via serial.
    def __sendCmd(self, cmd: str, waitTime = 0.5) -> Result:

    #Send the command.
        if not cmd.endswith("\r"):
            cmd += "\r"
        self.con.write(cmd.encode())

    #Read/return the response as a float array for future expansion
        while self.con.in_waiting == 0:
            continue
        time.sleep(waitTime)
        statusCode = self.con.read(size=2).decode()
        if self.con.in_waiting > 2:
            temp = ""
            data = []
            for i in range(0, self.con.in_waiting):
                incomingByte = self.con.read()
                temp += incomingByte.decode()
            temp = temp.replace("\r", "")
            temp = temp.split(",")
            for i in temp:
                data.append(float(i))
        else:
            data = None

        return Result(statusCode, data)

#Tier 1 Functions (Basics)

    def setZero(self):
        return self.__sendCmd("@RESET")

    def move(self, speed = 0, j1 = 0, j2 = 0, j3 = 0, j4 = 0, j5 = 0, j6 = 0):

        return self.__sendCmd(f"@STEP {speed}, {j1}, {j2}, {j3}, {j4}, {j5}, {j6}")
    
    def readPosition(self) -> Result:
        ret = self.__sendCmd("@READ")
        #Strip the leading status code
        return ret

    def closeGripper(self):
        return self.__sendCmd("@CLOSE")

#Tier 2 Functions (Depend on tier 1, some not refactored yet)

    def gripObject(self):
        self.__sendCmd("@CLOSE")
        return self.move(200, 0, 0, 0, 0, 0, -32)

    def returnToZero(self):
        currentPos = self.readPosition().data

        speed = 220
        j1 = int(-currentPos[0])
        j2 = int(-currentPos[1])
        j3 = int(-currentPos[2])
        j4 = int(-currentPos[3])
        j5 = int(-currentPos[4])
        j6 = int(-currentPos[5])
        ret = self.move(speed, j1, j2, j3, j4, j5, j6)
        #We can execute setZero to cut current to the motors. 
        self.setZero()
        return ret

    #Right now this is the only function that does not return a "Result" object. 
    def measureObject(self):
        OFFSET = 3.3
        self.closeGripper()
        current_width_mm = (self.readPosition().data[6] / 14.6) - OFFSET
        return current_width_mm

    #In progress: Inverse kinematic functions

    def moveToCoordinates(self, x, y, z, p, r, r1):
        H = 195.0
        L = 177.8
        LL = 96.5
        p = np.radians(p)
        r = np.radians(r)

        #T1 Calculations
        if x == 0:
            T1 = (np.pi / 2) * np.sign(y)
        else:
            T1 = np.arctan(y / x)

        #RR, R0, Z0
        #TODO may need some work... IDK if we need np.degrees or not.
        RR = np.sqrt(x**2 + y**2)
        R0 = RR - LL * np.cos(np.degrees(p))
        Z0 = z - LL * np.sin(np.degrees(p)) - H

        if R0 == 0:
            B = np.sign(Z0) * (np.pi / 2)
        else:
            B = np.arctan(Z0 / R0)

        #A calculations
        A = R0**2 + Z0**2
        A = 4 * (L**2) / (A) - 1
        A = np.arctan(np.sqrt(A))

        #T2 - T5 Calculations
        T2 = (np.pi/2) - (A + B)
        T3 = B - A
        T4 = p - r - r1 * T1
        T5 = p + r + r1 * T1

        #Convert to steps and accomodate for offset start position

        currentPos = self.readPosition().data

        T1 = int(T1 * 1125) - int(currentPos[0])
        T2 = int(T2 * 1125) - int(currentPos[1])
        T3 = -int(T3 * 672) - int(currentPos[2])
        T4 = int(T4 * 241) - int(currentPos[3])
        T5 = int(T5 * 241) - int(currentPos[4])
        T6 = T3

        return self.move(220, T1, T2, T3, 0, 0, T6)
