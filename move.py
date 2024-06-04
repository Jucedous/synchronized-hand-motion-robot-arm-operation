import serial
import socket
import keyboard
import subprocess
import threading
import tkinter as tk
from GUI import create_gui
from teachmover_class import TeachMover

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