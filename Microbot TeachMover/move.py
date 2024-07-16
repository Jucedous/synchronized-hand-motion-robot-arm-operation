import serial
import subprocess
import threading
import subprocess
import sys

import data_process_script
from GUI import *
from teachmover_class import TeachMover
            
def test_program():
    teach_mover1 = TeachMover('/dev/tty.usbserial-1410')
    teach_mover2 = TeachMover('/dev/tty.usbserial-1440')
    def move_group1():
        while True:
            try:
                teach_mover1.move_ik(240, 400, 0, 0, 0, 0, 0)
                teach_mover1.move_ik(240, -400, 0, 0, 0, 0, 0)
            except Exception as e:
                print(f"Failed to move group 1: {e}")
                break

    def move_group2():
        while True:
            try:
                teach_mover2.move_ik(240, 0, 0, 0, 200, 0, 0)
                teach_mover2.move_ik(240, 0, 0, 0, -200, 0, 0)
                teach_mover2.move_ik(240, 0, 0, 0, 0, 200, 0)
                teach_mover2.move_ik(240, 0, 0, 0, 0, -200, 0)
            except Exception as e:
                print(f"Failed to move group 2: {e}")
                break

    thread1 = threading.Thread(target=move_group1)
    thread2 = threading.Thread(target=move_group2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

def main_program():
    teach_mover = TeachMover('/dev/tty.usbserial-1410')
    output_data = data_process_script.SharedData()
    xyz_scaling_factors = (0.04, 0.033, 0.03)
    check_threshold = (0.5, 3, 5) # movement_threshold, gripper_status_gap, rotation_gap
    previous_gaps_rotations = {'left': (0, 0), 'right': (0, 0)}
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
        hand_type = 'right'
        data_process_script.process_hand_data(output_data, hand_type, teach_mover, xyz_scaling_factors, check_threshold, previous_gaps_rotations)
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