import serial
import keyboard
import subprocess
import threading
import subprocess
import sys
import re
import math
import time
from GUI import *
from teachmover_class import TeachMover

class SharedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = None

    def update(self, new_data):
        with self.lock:
            self.data = new_data

    def get(self):
        with self.lock:
            return self.data
            
def test_program():
    teach_mover = TeachMover('/dev/tty.usbserial-1410')
    while True:
        try:
            teach_mover.move_ik(240, 400, 0, 0, 0, 0, 0)
            teach_mover.move_ik(240, -400, 0, 0, 0, 0, 0)

        except Exception as e:
            print(f"Failed to move: {e}")
            return

def main_program():
    teach_mover = TeachMover('/dev/tty.usbserial-1410')
    output_data = SharedData()
    scaling_factor_x = 0.04
    scaling_factor_y = 0.033
    scaling_factor_z = 0.03
    movement_threshold = 0.5
    rotation_gap = 1
    gripper_status_gap = 3
    try:
        try:
            executable_path = '/Users/zhaozilin/Documents/Github/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build/ImageSample'
            process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        except Exception as e:
            print(f"Failed to start C executable: {e}")
            return
        def read_buffer(proc, shared_data):
            for line in iter(proc.stdout.readline, ''):
                shared_data.update(line.strip())

        output_thread = threading.Thread(target=read_buffer, args=(process, output_data))
        output_thread.start()
        running = True
        previous_gripper_gap = 0.0
        previous_rotation = 0.0
        while running:
            line = output_data.get()
            # if line is None:
            #     print("need data")
            if line is not None:
                if line == 'Close':
                    print('Fist')
                    if (teach_mover.returnToZero() == True):
                        running = False
                elif "Touching:" in line:
                    touch_state = "True" in line
                    if touch_state:
                        print("Close Gripper")
                        teach_mover.move(240, 0, 0, 0, 0, 0, -450)
                    elif not touch_state:
                        print("Open Gripper")
                        teach_mover.move(240, 0, 0, 0, 0, 0, 450)
                else:
                    match = re.search(r'x,y,z position: \[([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\], thumb_index_distance: ([\d\.-]+), yaw angle: ([\d\.-]+)', line)
                    if match:
                        hand_x = -(float(match.group(3)) * scaling_factor_x)
                        hand_y = -(float(match.group(1)) * scaling_factor_y)
                        hand_z = float(match.group(2)) * scaling_factor_z
                        
                        current_gripper_gap = float(match.group(4))
                        gripper_portion = int(current_gripper_gap)/100

                        current_rotation = float(match.group(5))
                        rotation_portion = -(current_rotation / 180)
                        
                        robot_x = teach_mover.gripper_coordinates[0]
                        robot_y = teach_mover.gripper_coordinates[1]
                        robot_z = teach_mover.gripper_coordinates[2]
                        
                        new_x = hand_x + robot_x
                        new_y = hand_y + robot_y
                        new_z = hand_z + robot_z
                        # print(f"New: {new_x}, {new_y}, {new_z}")
                        
                        delta_x = new_x - teach_mover.updated_gripper_coordinates[0]
                        delta_y = new_y - teach_mover.updated_gripper_coordinates[1]
                        delta_z = new_z - teach_mover.updated_gripper_coordinates[2]
                        
                        magnitude = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
                        
                        if ((magnitude > movement_threshold) or 
                            (abs(current_gripper_gap - previous_gripper_gap) >= gripper_status_gap) or 
                            (abs(current_rotation - previous_rotation) >= rotation_gap)):
                            try:
                                teach_mover.move_coordinates([new_x, new_y, new_z, 0, rotation_portion, gripper_portion])
                            except Exception as e:
                                print(f"Failed to move: {e}")
                                running = False
                        previous_gripper_gap = current_gripper_gap
                        previous_rotation = current_rotation
            time.sleep(0.01)
    except serial.SerialException:
        print("Failed to connect")
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Closing...")
        process.kill()
        process.wait()
        output_thread.join()
        teach_mover.close()
        sys.exit()

def GUI_tesing():
    teach_mover = TeachMover('/dev/tty.usbserial-1410')
    create_gui(teach_mover)
    # xyz(teach_mover)
    # gripper(teach_mover)

if __name__ == "__main__":
    # test_program()
    main_program()
    # GUI_tesing()