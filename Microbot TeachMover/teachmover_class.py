import serial
import time
from IK import InverseKinematics

class TeachMover:
    def __init__(self, portID: str, baudRate=9600):
        try:
            # Establish the serial connection
            self.con = serial.Serial(portID, baudRate, timeout=1)
            self.root = None
            print("Connection established")

        except serial.SerialException as e:
            print(f"Failed to connect on {portID}: {e}")

    def send_cmd(self, cmd: str, waitTime=0):
        if not cmd.endswith("\r"):
            cmd += "\r"
        self.con.write(cmd.encode())

        # Wait for a short time to allow the command to be processed
        # time.sleep(waitTime)

        # Read and return any response
        response = self.con.readline().decode().strip()
        return response

    def move(self, speed=0, j1=0, j2=0, j3=0, j4=0, j5=0, j6=0):
        response = self.send_cmd(f"@STEP {speed}, {j1}, {j2}, {j3}, {j4+j5}, {j4-j5}, {j6+j3}")
        print("move to ", j1, j2, j3, j4, j5, j6)
        return response
    
    def setZero(self):
        return self.send_cmd("@RESET")
    
    def readPosition(self):
        ret = self.send_cmd("@READ")
        #Strip the leading status code
        return ret
    
    def set_default_position(self):
        self.setZero()
        default_position = self.readPosition()
        print(default_position)
    
    def print_default_position(self):
        default_position = self.readPosition()
        print(default_position)

    def returnToZero(self):
        currentPos = self.readPosition().split(',')

        speed = 220
        j1 = -int(currentPos[0])
        j2 = -int(currentPos[1])
        j3 = -int(currentPos[2])
        j4 = -int(currentPos[3])
        j5 = -int(currentPos[4])
        j6 = -int(currentPos[5])
        ret = self.move(speed, j1, j2, j3, j4, j5, j6)

        return ret
    
    # Note to add speed and gripper control 
    def move_to_xyz(self, x, y, z, lw, rw):
        ik = InverseKinematics(x, y, z, lw, rw)
        j1, j2, j3, j4, j5 = ik.FindStep(x, y, z, lw, rw)
        return self.move(200, j1, j2, j3, j4, j5, 0)
    
    def close(self):
        # Close the serial connection
        if self.con.is_open:
            self.con.close()