import serial
import time
import socket
import keyboard
import subprocess
import threading
from GUI import create_gui

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
        
        return response

    def close(self):
        # Close the serial connection
        if self.con.is_open:
            self.con.close()

# #socket for receive data
# def receive_data():
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('127.0.0.1', 7891))
#     server_socket.listen(1)
#     client_socket, address = server_socket.accept()
#     data = client_socket.recv(1024).decode('utf-8')
#     client_socket.close()
#     return float(data)

def stop_program():
    print("Stopping...")
    global running  # Use a global variable to communicate with the main loop
    running = False

# Register the hotkey
keyboard.add_hotkey('q', stop_program)

# Example usage:
def main_program():
    try:
        teach_mover = TeachMover('/dev/tty.usbserial-1410')
        # process = subprocess.Popen(["./build/ImageSample"], stdout=subprocess.PIPE)
        running = True
        while running:
            pass
            # position_y = receive_data()/10
            # teach_mover.move(200, 0, 0, 0, 0, 0, position_y)
        # process.terminate()
    except serial.SerialException:
        print("Failed to connect")

main_thread = threading.Thread(target=main_program)
main_thread.start()

teach_mover = TeachMover('/dev/tty.usbserial-1410')
create_gui(teach_mover)