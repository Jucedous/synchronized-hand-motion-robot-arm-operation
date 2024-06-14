import serial
import keyboard
import subprocess
import threading
import tkinter as tk
import subprocess
import sys
import time
from GUI import create_gui
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
                start_time = time.time()
                line = output_data.get()
                # print(f"{time.time() - start_time}s: Processing command: {line}")
                start_time = time.time()
                if line == 'True':
                    teach_mover.move(200, 0, 0, 100, 0, 0, 0)
                elif line == 'False':
                    teach_mover.move(200, 0, 0, -100, 0, 0, 0)
                elif line == 'Fist':
                    print('Fist')
                    if (teach_mover.returnToZero() == True):
                        running = False
                # print(f"{time.time() - start_time}s: Finished processing command: {line}")
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
    create_gui(teach_mover)

if __name__ == "__main__":
    main_program()
    # GUI_tesing()