import math

class InverseKinematics:
    H = 7.625   #The length of Base to Shoulder
    L = 7.0     #The length of Shoulder to Elbow and Elbow to Wrist
    LL = 3.8    #The length of Wrist
    
    D_PI = 2 * math.pi
    B_C = 7072 / D_PI      # Base motor:             7072 steps in 1 rotation
    S_C = 7072 / D_PI      # Shoulder motor:         7072 steps in 1 rotation
    E_C = 4158 / D_PI      # Elbow motor:            4158 steps in 1 rotation
    W_C = 1536 / D_PI      # Right/Left Wrist motor: 1536 steps in 1 rotation
    G_C = 2330 / D_PI      # Gripper motor:          2330 steps in 1 rotation
        
    def FindStep(self, x, y, z, dlw, drw):
        
        RR = math.sqrt(x**2 + y**2)  # intermediate value
        r0 = RR
        z0 = z - self.H

        # Get intermediate angles (radian)
        alpha = math.acos(math.sqrt((r0**2 + z0**2) / (4 * self.L**2)))
        beta = math.atan2(z0, r0)
        
        #Calculate the angle of the base motor
        theta1 = math.atan2(y, x)
        theta2 = (alpha + beta)
        theta3 = (beta - alpha)
        #Calculate the angle of the right/left wrist motor
        theta4 = (dlw + drw) / 2
        
        #Calculate the angle of the gripper motor
        theta5 = (dlw - drw) / 2

        step1 = int(theta1 * self.B_C)
        step2 = int(theta2 * self.S_C)
        step3 = int(theta3 * self.E_C)
        step4 = int(theta4 * self.W_C)
        step5 = int(theta5 * self.G_C)
        
        return step1, step2, step3, step4, step5

    # def moveTo(self, new_x, new_y, new_z, new_left_wrist_motor, new_right_wrist_motor):
    #     if not self.is_reachable(new_x, new_y, new_z, new_left_wrist_motor, new_right_wrist_motor):
    #         return None
    #     StepValue = self.FindStep(new_x, new_y, new_z, new_left_wrist_motor, new_right_wrist_motor)
    #     self.make_move(StepValue)
        
        
    #     self.x = new_x
    #     self.y = new_y
    #     self.z = new_z
    #     self.left_wrist_motor = new_left_wrist_motor
    #     self.right_wrist_motor = new_right_wrist_motor
        
    #     return StepValue
    
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