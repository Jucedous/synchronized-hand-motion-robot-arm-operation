import tkinter as tk
from tkinter import messagebox

def create_gui(teach_mover):
    def move_up():
        try:
            teach_mover.move(200,0,0,0,0,0,60)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def move_down():
        try:
            teach_mover.move(200,0,0,0,0,0,-60)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def exit_program():
        root.destroy()
        teach_mover.stop()
        exit(0)
            
    root = tk.Tk()
    
    button_up = tk.Button(root, text = "Move Up", command = move_up)
    button_down = tk.Button(root, text = "Move Down", command = move_down)
    button_exit = tk.Button(root, text = "Exit", command=exit_program)
    
    button_up.pack()
    button_down.pack()
    button_exit.pack()
    
    root.mainloop()