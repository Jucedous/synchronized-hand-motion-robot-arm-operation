import tkinter as tk
from tkinter import messagebox

def create_gui(teach_mover):

    labels = ["Speed", "Body", "Upper Arm", "Forearm", "Wrist Vertical", "Wrist Rotate", "Gripper"]
    entries = []
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
    
    def set_to_default():
        try:
            teach_mover.set_default_position()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def print_to_default():
        try:
            teach_mover.print_default_position()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def move_to_default():
        try:
            teach_mover.returnToZero()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # def reset():
    #     try:
    #         teach_mover.setZero()
    #     except Exception as e:
    #         messagebox.showerror("Error", str(e))
    
    # def exit_program():
    #     root.destroy()
    #     exit(0)
            
    root = tk.Tk()
    
    for i, label in enumerate(labels):
        tk.Label(root, text=label).grid(row=i+5, column=0)
        entry = tk.Entry(root)
        entry.grid(row=i+5, column=1)
        entries.append(entry)

    def move():
        try:
            values = [int(entry.get()) if entry.get() else 0 for entry in entries]
            teach_mover.move(*values)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    move_button = tk.Button(root, text="Move", command=move)
    
    button_up = tk.Button(root, text = "Move Up", command = move_up)
    button_down = tk.Button(root, text = "Move Down", command = move_down)
    button_set_default = tk.Button(root, text = "Set to Default", command = set_to_default)
    button_print_default = tk.Button(root, text = "Print Current Position", command = print_to_default)
    button_move_default = tk.Button(root, text = "Move to Default", command = move_to_default)
    # button_reset = tk.Button(root, text = "Reset", command = reset)
    # button_exit = tk.Button(root, text = "Exit", command=exit_program)
    
    button_up.grid(row=0, column=0)
    button_down.grid(row=1, column=0)
    button_set_default.grid(row=2, column=0)
    button_print_default.grid(row=3, column=0)
    button_move_default.grid(row=4,column=0)
    move_button.grid(row=len(labels)+5, column=0, columnspan=2)
    # button_reset.pack()
    # button_exit.pack()
    
    root.mainloop()