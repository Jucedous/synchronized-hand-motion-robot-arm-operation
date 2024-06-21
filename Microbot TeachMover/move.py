import serial
import keyboard
import subprocess
import threading
import tkinter as tk
import subprocess
import sys
import re
import time
from GUI import *
from teachmover_class import TeachMover
from IK import InverseKinematics

class SharedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = None
        self.read = False

    def update(self, new_data):
        with self.lock:
            self.data = new_data
            self.read = False

    def get(self):
        with self.lock:
            if self.read:
                return None
            else:
                self.read = True
                return self.data

def main_program():
    teach_mover = TeachMover('/dev/tty.usbserial-1410')
    output_data = SharedData()
    try:
        try:
            executable_path = '/Users/zhaozilin/Documents/Github/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build/ImageSample'
            process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        except Exception as e:
            print(f"Failed to start C executable: {e}")
            return
        def read_buffer(proc, shared_data):
            for line in iter(proc.stdout.readline, ''):
                # print("Debug: Line read from stdout:", line.strip())  # Debugging output
                shared_data.update(line.strip())

        output_thread = threading.Thread(target=read_buffer, args=(process, output_data))
        output_thread.start()
        running = True
        while running:
            line = output_data.get()
            if line is not None:
                if line == 'Fist':
                    print('Fist')
                    if (teach_mover.returnToZero() == True):
                        running = False
                else:
                    # teach_mover.move(200, 0, 0, 100,0,0,0)
                    match = re.search(r'Change in position: \[([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\]', line)
                    if match:
                        change_x = float(match.group(1))
                        change_y = float(match.group(2))
                        change_z = float(match.group(3))
                        print(f"Change in position: [{change_x}, {change_y}, {change_z}]")
                        # teach_mover.move_delta_coordinates(change_x, change_y, change_z)
            # if line is not None:
            #     if line == 'True':
            #         teach_mover.move(240, 0, 0, 100, 0, 0, 0)
            #     elif line == 'False':
            #         teach_mover.move(240, 0, 0, -100, 0, 0, 0)
            #     elif line == 'Fist':
            #         print('Fist')
            #         if (teach_mover.returnToZero() == True):
            #             running = False
    except serial.SerialException:
        print("Failed to connect")
    finally:
        print("Closing...")
        process.kill()
        process.wait()
        output_thread.join()
        teach_mover.close()
        sys.exit()

def GUI_tesing():
    teach_mover = TeachMover('/dev/tty.usbserial-1410')
    # create_gui(teach_mover)
    xyz(teach_mover)

if __name__ == "__main__":
    # main_program()
    GUI_tesing()