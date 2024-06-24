import serial
import keyboard
import subprocess
import threading
import tkinter as tk
import subprocess
import sys
import re
import math
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
    scale_factor = 0.05
    step_factor = 0.5
    scaling_factor_x = 0.3
    scaling_factor_y = 0.3
    scaling_factor_z = 0.3
    threshold = 1
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
                    match = re.search(r'x,y,z position: \[([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\]', line)
                    if match:
                        target_x = float(match.group(3)) * scale_factor
                        target_y = float(match.group(1)) * scale_factor
                        target_z = float(match.group(2)) * scale_factor
                        
                        robot_x = teach_mover.updated_gripper_coordinates[0]
                        robot_y = teach_mover.updated_gripper_coordinates[1]
                        robot_z = teach_mover.updated_gripper_coordinates[2]
                        
                        delta_x = target_x - robot_x
                        delta_y = target_y - robot_y
                        delta_z = target_z - robot_z
                        
                        magnitude = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
                        
                        if (magnitude > threshold):
                            move_x = delta_x * scale_factor + robot_x
                            move_y = delta_y * scale_factor + robot_y
                            move_z = delta_z * scale_factor + robot_z
                            try:
                                teach_mover.move_delta_coordinates([move_x, move_y, move_z], False)
                            except Exception as e:
                                print(f"Failed to move: {e}")
                                running = False
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