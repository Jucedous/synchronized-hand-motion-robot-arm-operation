import serial
import subprocess
import threading
import subprocess
import sys
import data_process_script
from GUI import *
from teachmover_class import TeachMover

def main_program():
    teach_mover1 = TeachMover('/dev/tty.usbserial-1410')
    teach_mover2 = TeachMover('/dev/tty.usbserial-1440')
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
        data_process_script.process_both_hands(output_data, teach_mover1, teach_mover2, xyz_scaling_factors, check_threshold, previous_gaps_rotations)
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