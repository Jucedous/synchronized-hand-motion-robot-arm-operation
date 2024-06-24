import tkinter as tk
from tkinter import *
from tkinter import messagebox

def xyz(teach_mover):
    root = tk.Tk()
    root.title("Delta XYZ Position Input")

    # Create entry fields for X, Y, Z
    x_entry = Entry(root, width=30)
    x_entry.grid(row=0, column=1, padx=20)
    y_entry = Entry(root, width=30)
    y_entry.grid(row=1, column=1)
    z_entry = Entry(root, width=30)
    z_entry.grid(row=2, column=1)

    # Create Text Labels for the entries
    x_label = Label(root, text="delta X")
    x_label.grid(row=0, column=0)
    y_label = Label(root, text="delta Y")
    y_label.grid(row=1, column=0)
    z_label = Label(root, text="delta Z")
    z_label.grid(row=2, column=0)

    # Create a function to calculate step
    def move_by_delta():
        try:
            x = float(x_entry.get()) if x_entry.get() else 0.0
            y = float(y_entry.get()) if y_entry.get() else 0.0
            z = float(z_entry.get()) if z_entry.get() else 0.0
            teach_mover.move_delta_coordinates([x,y,z],False)
            messagebox.showinfo("Success", "Robot moved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    move_button = Button(root, text="Calculate Step", command=move_by_delta)
    move_button.grid(row=3, column=0, columnspan=2, pady=10)
    
    def move_test():
        try:
            x = float(x_entry.get()) if x_entry.get() else 0.0
            y = float(y_entry.get()) if y_entry.get() else 0.0
            z = float(z_entry.get()) if z_entry.get() else 0.0
            teach_mover.move_delta_coordinates([x,y,z],True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    print_button = Button(root, text="Move Test", command=move_test)
    print_button.grid(row=4, column=0, columnspan=2, pady=10)
    
    def print_step():
        try:
            teach_mover.print_step()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    print_button = Button(root, text="Print Step", command=print_step)
    print_button.grid(row=5, column=0, columnspan=2, pady=10)
    
    def move_to_default():
        try:
            teach_mover.returnToZero()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    move_default_button = Button(root, text="move to default", command=move_to_default)
    move_default_button.grid(row=6, column=0, columnspan=2, pady=10)
    
    root.mainloop()

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

    def print_position():
        try:
            teach_mover.print_position()
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
    button_print_default = tk.Button(root, text = "Print Current Position", command = print_position)
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