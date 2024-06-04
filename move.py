import serial
import time

class TeachMover:
    def __init__(self, portID: str, baudRate=9600):
        try:
            # Establish the serial connection
            self.con = serial.Serial(portID, baudRate, timeout=1)
            print("Connection established")

        except serial.SerialException as e:
            print(f"Failed to connect on {portID}: {e}")

    def send_cmd(self, cmd: str, waitTime=0.5):
        if not cmd.endswith("\r"):
            cmd += "\r"
        self.con.write(cmd.encode())

        # Wait for a short time to allow the command to be processed
        time.sleep(waitTime)

        # Read and return any response
        response = self.con.readline().decode().strip()
        return response

    def move(self, speed=0, j1=0, j2=0, j3=0, j4=0, j5=0, j6=0):
        response = self.send_cmd(f"@STEP {speed}, {j1}, {j2}, {j3}, {j4}, {j5}, {j6}")
        
        # Close the serial connection after use
        self.close()
        
        return response

    def close(self):
        # Close the serial connection
        if self.con.is_open:
            self.con.close()

# Example usage:
try:
    teach_mover = TeachMover('COM7')
    teach_mover.move(200, 0, 0, -30, 0, 0, -90)

except serial.SerialException:
    print("Failed to connect on COM7")
