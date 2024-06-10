import math

class InverseKinematics:
    #TeachMover2 Geometrical Paramaters (inches)3
    H = 7.625   #The length of Base to Shoulder
    L = 7.0     #The length of Shoulder to Elbow and Elbow to Wrist
    LL = 3.8    #The length of Wrist
    
    D_PI = 2 * math.pi
    B_C = 7072 / D_PI      # Base motor:             7072 steps in 1 rotation
    S_C = 7072 / D_PI      # Shoulder motor:         7072 steps in 1 rotation
    E_C = 4158 / D_PI      # Elbow motor:            4158 steps in 1 rotation
    W_C = 1536 / D_PI      # Right/Left Wrist motor: 1536 steps in 1 rotation
    G_C = 2330 / D_PI      # Gripper motor:          2330 steps in 1 rotation
    
    def __init__(self, x, y, z, left_wrist_motor, right_wrist_motor):
        self.x = x;
        self.y = y;
        self.z = z;
        self.left_wrist_motor = left_wrist_motor
        self.right_wrist_motor = right_wrist_motor
        
    def FindStep(self, dx, dy, dz, dlw, drw):
        
        #Calculate the angle of the base motor
        theta1 = math.atan2(dy, dx)
        
        #Calculate the angle of the shoulder motor
        D = math.sqrt(dx**2 + dy**2) - self.L
        E = dz - self.H
        F = math.sqrt(D**2 + E**2)
        G = math.sqrt(F**2 - self.LL**2)
        theta2 = math.atan2(E, D) + math.acos(self.LL / F)
        
        #Calculate the angle of the elbow motor
        theta3 = math.acos((self.L**2 + self.L**2 - G**2) / (2 * self.L * self.L))
        
        #Calculate the angle of the right/left wrist motor
        theta4 = (dlw + drw) / 2
        
        #Calculate the angle of the gripper motor
        theta5 = (dlw - drw) / 2
        
        #Convert the angles to steps
        step1 = int(theta1 * self.B_C)
        step2 = int(theta2 * self.S_C)
        step3 = int(theta3 * self.E_C)
        step4 = int(theta4 * self.W_C)
        step5 = int(theta5 * self.G_C)
        
        return step1, step2, step3, step4, step5

    def moveTo(self, new_x, new_y, new_z, new_left_wrist_motor, new_right_wrist_motor):
        if not self.is_reachable(new_x, new_y, new_z, new_left_wrist_motor, new_right_wrist_motor):
            return None
        StepValue = self.FindStep(new_x, new_y, new_z, new_left_wrist_motor, new_right_wrist_motor)
        
        
        self.x = new_x
        self.y = new_y
        self.z = new_z
        self.left_wrist_motor = new_left_wrist_motor
        self.right_wrist_motor = new_right_wrist_motor
        
        return StepValue
    
    def is_reachable(self, x, y, z):
        #Calculate the distance from the base to the target
        distance = math.sqrt(x**2 + y**2)
        
        #Check if the target is reachable
        if distance > self.L + self.LL:
            return False
        if z > self.H + self.L:
            return False
        if z < self.H - self.L:
            return False
        
        return True
    
    def set_default_position(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.left_wrist_motor = 0
        self.right_wrist_motor = 0
    
    def reset_to_default(self):
        self.set_default_position()