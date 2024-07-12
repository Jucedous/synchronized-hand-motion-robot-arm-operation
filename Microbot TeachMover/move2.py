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

def process_hand_data(output_data, hand_type, teach_mover, scaling_factors, movement_threshold, gripper_status_gap, rotation_gap, previous_gaps_rotations):
    scaling_factor_x, scaling_factor_y, scaling_factor_z = scaling_factors
    previous_gripper_gap, previous_rotation = previous_gaps_rotations[hand_type]
    running = True
    while running:
        line = output_data.get()
        if line is not None:
            match = re.search(r'Left hand data \(([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\)\. Right hand data \(([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\)\.', line)
            if match:
                base_index = 2 if hand_type == 'left' else 7
                hand_x = -(float(match.group(base_index + 1)) * scaling_factor_x)
                hand_y = -(float(match.group(base_index - 1)) * scaling_factor_y)
                hand_z = float(match.group(base_index)) * scaling_factor_z

                current_gripper_gap = float(match.group(base_index + 2))
                gripper_portion = int(current_gripper_gap) / 100

                current_rotation = float(match.group(base_index + 3))
                rotation_portion = -(current_rotation / 180)

                robot_x = teach_mover.gripper_coordinates[0]
                robot_y = teach_mover.gripper_coordinates[1]
                robot_z = teach_mover.gripper_coordinates[2]

                new_x = hand_x + robot_x
                new_y = hand_y + robot_y
                new_z = hand_z + robot_z
                
                delta_x = new_x - teach_mover.updated_gripper_coordinates[0]
                delta_y = new_y - teach_mover.updated_gripper_coordinates[1]
                delta_z = new_z - teach_mover.updated_gripper_coordinates[2]

                magnitude = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)

                if ((magnitude > movement_threshold) or 
                    (abs(current_gripper_gap - previous_gripper_gap) >= gripper_status_gap) or 
                    (abs(current_rotation - previous_rotation) >= rotation_gap)):
                    try:
                        print(f"Moving to: {new_x}, {new_y}, {new_z}, 0, {rotation_portion}, {gripper_portion}")
                        teach_mover.move_coordinates([new_x, new_y, new_z, 0, rotation_portion, gripper_portion])
                    except Exception as e:
                        print(f"Failed to move: {e}")
                        running = False

                previous_gaps_rotations[hand_type] = (current_gripper_gap, current_rotation)
        time.sleep(0.01)

        
def process_both_hands(output_data, teach_mover1, teach_mover2, scaling_factors, movement_threshold, gripper_status_gap, rotation_gap, previous_gaps_rotations):
    threads = []
    movers = {'left': teach_mover2, 'right': teach_mover1}
    for hand_type in ['left', 'right']:
        thread = threading.Thread(target=process_hand_data, args=(output_data, hand_type, movers[hand_type], scaling_factors, movement_threshold, gripper_status_gap, rotation_gap, previous_gaps_rotations))
        print(output_data.get())
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def main_program():
    teach_mover1 = TeachMover('/dev/tty.usbserial-1410')
    teach_mover2 = TeachMover('/dev/tty.usbserial-1440')
    output_data = SharedData()
    scaling_factors = (0.04, 0.033, 0.03)  # Grouped scaling factors into a tuple
    movement_threshold = 0.5
    rotation_gap = 5
    gripper_status_gap = 3
    previous_gaps_rotations = {'left': (0, 0), 'right': (0, 0)}  # Initialize previous gaps and rotations
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
        print(output_data.get())
        process_both_hands(output_data, teach_mover1, teach_mover2, scaling_factors, movement_threshold, gripper_status_gap, rotation_gap, previous_gaps_rotations)
    except serial.SerialException:
        print("Failed to connect")
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Closing...")
        process.kill()
        process.wait()
        output_thread.join()
        teach_mover1.close()
        teach_mover2.close()
        sys.exit()

if __name__ == "__main__":
    main_program()