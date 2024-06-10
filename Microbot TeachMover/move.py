import serial
import socket
import keyboard
import subprocess
import threading
import tkinter as tk
import subprocess
import time
import os
import queue
from GUI import create_gui
from teachmover_class import TeachMover
from queue import Queue

# #socket for receive data
# def receive_data():
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('127.0.0.1', 7891))
#     server_socket.listen(1)
#     client_socket, address = server_socket.accept()
#     data = client_socket.recv(1024).decode('utf-8')
#     client_socket.close()
#     return float(data)

# output_buffer = Queue()
# def read_buffer(process):
#     for line in iter(process.stdout.readline, b''):
#         output_buffer.put(line.strip())

# def read_output(process):
#     while True:
#         output = process.stdout.readline()
#         if output == '' and process.poll() is not None:
#             break
#         if output:
#             print(output.strip())

def stop_program():
    print("Stopping...")
    global running  # Use a global variable to communicate with the main loop
    running = False

# Register the hotkey
keyboard.add_hotkey('q', stop_program)

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

# Example usage:
def main_program():
    output_data = SharedData()
    try:
        try:
            executable_path = './ImageSample'
            process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        except Exception as e:
            print(f"Failed to start C executable: {e}")
            return
        def read_buffer(proc, shared_data):
            for line in iter(proc.stdout.readline, ''):
                print("Debug: Line read from stdout:", line.strip())  # Debugging output
                shared_data.update(line.strip())

        output_thread = threading.Thread(target=read_buffer, args=(process, output_data))
        output_thread.start()
        running = True
        while running:
                line = output_data.get()
                if line in ['True', 'False']:  # Check if line is exactly 'True' or 'False'
                    print(f"Processing command: {line}")
                    if line == 'True':
                        teach_mover.move(200, 0, 0, 100, 0, 0, 0)
                    elif line == 'False':
                        teach_mover.move(200, 0, 0, -100, 0, 0, 0)
    except serial.SerialException:
        print("Failed to connect")

teach_mover = TeachMover('/dev/tty.usbserial-1410')
if __name__ == "__main__":
    main_program()

# create_gui(teach_mover)