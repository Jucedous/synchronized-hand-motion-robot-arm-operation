import threading
import math
import time
import re

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

def process_hand_data(output_data, hand_type, teach_mover, scaling_factors, check_threshold, previous_gaps_rotations):
    scaling_factor_x, scaling_factor_y, scaling_factor_z = scaling_factors
    xyz_check, gripper_check, rotation_check = check_threshold
    previous_gripper_gap, previous_rotation = previous_gaps_rotations[hand_type]
    running = True
    while running:
        line = output_data.get()
        if line is not None:
            match = re.search(r'Left hand data \(([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\)\. Right hand data \(([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)\)\.', line)
            if match:
                base_index = 2 if hand_type == 'left' else 7
                hand_x = -(float(match.group(base_index + 1)) * scaling_factor_x)
                hand_y = -(float(match.group(base_index - 1)) * scaling_factor_y)
                hand_z = float(match.group(base_index)) * scaling_factor_z

                current_gripper_gap = float(match.group(base_index + 2))
                gripper_portion = int(current_gripper_gap) / 100

                current_rotation = float(match.group(base_index + 3))
                rotation_portion = -(current_rotation / 180)

                robot_x = teach_mover.gripper_coordinates[0]
                robot_y = teach_mover.gripper_coordinates[1]
                robot_z = teach_mover.gripper_coordinates[2]

                new_x = hand_x + robot_x
                new_y = hand_y + robot_y
                new_z = hand_z + robot_z
                
                delta_x = new_x - teach_mover.updated_gripper_coordinates[0]
                delta_y = new_y - teach_mover.updated_gripper_coordinates[1]
                delta_z = new_z - teach_mover.updated_gripper_coordinates[2]

                magnitude = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)

                if ((magnitude > xyz_check) or 
                    (abs(current_gripper_gap - previous_gripper_gap) >= gripper_check) or 
                    (abs(current_rotation - previous_rotation) >= rotation_check)):
                    try:
                        print(f"Moving to: {new_x}, {new_y}, {new_z}, 0, {rotation_portion}, {gripper_portion}")
                        teach_mover.move_coordinates([new_x, new_y, new_z, 0, rotation_portion, gripper_portion])
                    except Exception as e:
                        print(f"Failed to move: {e}")
                        running = False

                previous_gaps_rotations[hand_type] = (current_gripper_gap, current_rotation)
        time.sleep(0.01)

        
def process_both_hands(output_data, teach_mover1, teach_mover2, scaling_factors, check_threshold, previous_gaps_rotations):
    threads = []
    movers = {'left': teach_mover2, 'right': teach_mover1}
    for hand_type in ['left', 'right']:
        thread = threading.Thread(target=process_hand_data, args=(output_data, hand_type, movers[hand_type], scaling_factors, check_threshold, previous_gaps_rotations))
        print(output_data.get())
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
        
                        # potential fix on structure and better status update. Waiting for testing.
                        
                        # magnitude_condition_met = magnitude > movement_threshold
                        # gripper_condition_met = abs(current_gripper_gap - previous_gripper_gap) >= gripper_status_gap
                        # rotation_condition_met = abs(current_rotation - previous_rotation) >= rotation_gap

                        # # Initialize movement parameters with default values
                        # move_params = [0, 0, 0, 0]  # Assuming these are the default positions for x, y, z, and a placeholder 0 for future use
                        # rotation_portion_param = 0  # Default rotation portion
                        # gripper_portion_param = 0  # Default gripper portion

                        # # Update movement parameters based on conditions met
                        # if magnitude_condition_met:
                        #     # Update move_params to include new_x, new_y, new_z if magnitude condition is met
                        #     move_params = [new_x, new_y, new_z, 0]

                        # if gripper_condition_met:
                        #     # Update gripper_portion_param if gripper condition is met
                        #     gripper_portion_param = gripper_portion
                        #     previous_gripper_gap = current_gripper_gap

                        # if rotation_condition_met:
                        #     # Update rotation_portion_param if rotation condition is met
                        #     rotation_portion_param = rotation_portion
                        #     previous_rotation = current_rotation

                        # # Perform movement if any of the conditions are met
                        # if magnitude_condition_met or gripper_condition_met or rotation_condition_met:
                        #     try:
                        #         print(f"Moving to: {move_params}, {rotation_portion_param}, {gripper_portion_param}")
                        #         teach_mover.move_coordinates(move_params + [rotation_portion_param, gripper_portion_param])
                        #     except Exception as e:
                        #         print(f"Failed to move: {e}")
                        #         running = False