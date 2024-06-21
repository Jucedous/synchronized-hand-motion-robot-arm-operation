import serial
import copy
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
        self.ik = InverseKinematics()
        self.gripper_coordinates = [(self.ik.L+self.ik.LL), 0, (self.ik.H+self.ik.L), 0, 0, 0]
        self.updated_gripper_coordinates = copy.deepcopy(self.gripper_coordinates)
        self.default_step = self.ik.FindStep(*self.gripper_coordinates[:5])
        self.updated_step = self.default_step


    def print_step(self):
        print(self.updated_step)
    
    def find_step(self, new_x, new_y, new_z, new_lw, new_rw):
        return self.ik.FindStep(new_x, new_y, new_z, new_lw, new_rw)
    
    def update_coordinates(self, new_coordinates):
        # This method allows updating the coordinates safely without affecting the original
        self.updated_gripper_coordinates = new_coordinates

    def move_coordinates(self, coordinates):
        new_step = self.ik.FindStep(coordinates[0], coordinates[1], coordinates[2], coordinates[3], coordinates[4])
        step_difference = [new - current for new, current in zip(new_step, self.updated_step)]
        self.move(240, *step_difference, 0)
        self.updated_gripper_coordinates = [coordinates[0], coordinates[1], coordinates[2], coordinates[3], coordinates[4], 0]
        self.updated_step = new_step
        print(self.updated_gripper_coordinates)
        print(self.updated_step)
        print()
    
    def move_delta_coordinates(self, delta_coordinates):
        # Calculate new coordinates by adding the changes to the current coordinates
        new_coordinates = [current + delta for current, delta in zip(self.updated_gripper_coordinates[:3], delta_coordinates)]
        # Append the remaining coordinates (if any)
        new_coordinates.extend(self.updated_gripper_coordinates[3:])
        print(new_coordinates)
        # Use the existing move_coordinates function to move to the new coordinates
        self.move_coordinates(new_coordinates)


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
        if (response == "1"):
            return True
        else:
            return False
    
    def move_to_coordinates(self, coordinates):
        self.coordinates = coordinates
        step = self.ik.FindStep(coordinates[0], coordinates[1], coordinates[2], coordinates[3], coordinates[4])
        ret = self.move(200, step[0], step[1], step[2], step[3], step[4], 0)
        return ret
    
    def setZero(self):
        return self.send_cmd("@RESET")
    
    def readPosition(self):
        ret = self.send_cmd("@READ")
        #Strip the leading status code
        ret = ret.split('\r')[-1]
        return ret
    
    def set_default_position(self):
        self.setZero()
        default_position = self.readPosition()
        print(default_position)
    
    def print_position(self):
        position = self.readPosition()
        print(position)

    def reset_to_default(self):
        self.updated_gripper_coordinates = copy.deepcopy(self.gripper_coordinates)
        self.updated_step = self.default_step
    
    def returnToZero(self):
        self.reset_to_default()
        
        currentPos = self.readPosition().split(',')

        speed = 240
        j1 = -int(currentPos[0])
        j2 = -int(currentPos[1])
        j3 = -int(currentPos[2])
        j4 = -int(currentPos[3])
        j5 = -int(currentPos[4])
        j6 = -int(currentPos[5])-j3
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