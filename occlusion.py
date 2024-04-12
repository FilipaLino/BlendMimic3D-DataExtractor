import bpy
import sys
import os
from mathutils import Vector
from bpy import context
import bpy_extras
import numpy as np
#from bpy_extras import object_utils

#Crucial joints sufficient for visualisation #FIX ME - Add more joints if desirable for MixamRig
BASE_JOINT_NAMES = ['Hips', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot', 
                    'Spine1', 'Neck','Head', 'HeadTop_End', 'RightArm', 'RightForeArm', 'RightHand', 
                    'LeftArm', 'LeftForeArm', 'LeftHand',
                    ]

#Source directory where .fbx exist
SRC_DATA_DIR ='regular'

def remove_trailing_numbers(bone_name):
    # Initialize an empty string to hold the result
    result = ""

    # Iterate through each character in the bone_name
    for char in bone_name:
        # Check if the character is a digit (0-9)
        if char.isdigit():
            # If a digit is found, stop the iteration
            break
        # Add the character to the result string
        result += char

    return result                   

def is_keypoint_out_of_view(keypoint, keypoint_location, camera):
    scene = bpy.context.scene
    #camera = bpy.context.scene.camera
    
    # Get the 3D location of the keypoint
    #keypoint_location = keypoint.matrix @ bpy.context.object.matrix_world @ keypoint.location

    # Project the 3D location of the keypoint onto the camera's image plane
    projected_co = bpy_extras.object_utils.world_to_camera_view(scene, camera, keypoint_location)

    # Check if the projected 2D point is outside the image boundaries
    if 0 <= projected_co.x <= 1 and 0 <= projected_co.y <= 1 and projected_co.z > 0:
        # The keypoint is within the camera's viewport
        return False
    else:
        # The keypoint is outside the camera's viewport
        return True

def is_occluded(keypoint, kpt_global_location, camera):
   
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    #camera = bpy.context.scene.camera
   
    # Calculate the direction from the camera to the keypoint
    direction = (kpt_global_location - camera.location).normalized()

    # Define the ray's starting and ending points
    ray_start = camera.location
    ray_end = kpt_global_location
    
    # Perform the ray casting
    result, location, normal, index, object, matrix = scene.ray_cast(depsgraph,ray_start, direction)
    #print(keypoint.name)
    #print(object.name) 
    

    if result and  remove_trailing_numbers(object.name) not in keypoint.name :
        #print(keypoint.name)
        #print(object.name)    
        return True

    return False


if __name__ == '__main__':
    
    start_frame = 0
    end_frame = 0
    argv = sys.argv[sys.argv.index("--") + 1:]  # Get arguments after "--"
    # Parse the command-line arguments
    if argv:
        for i in range(0, len(argv), 2):
            if argv[i] == "--joint-id":
                joint_id = argv[i + 1]
            elif argv[i] == "--armature-name":
                armature_name = argv[i + 1]
            elif argv[i] == "--subject":
                subject = argv[i + 1]
            elif argv[i] == "--start_frame":
                start_frame = argv[i + 1]
            elif argv[i] == "--end_frame":
                end_frame = argv[i + 1]
               

    #Number of joints to be used from MixamoRig
    joint_names = ['mixamorig'+ joint_id +':' + x for x in BASE_JOINT_NAMES]
    
    OUT_DATA_DIR = f"../../BlendMimic3D/{subject}/Occlusions"
    
    # List of camera names
    camera_names = ['Camera_0', 'Camera_1', 'Camera_2', 'Camera_3'] #Same order as H3.6M dataset 
   
    # Replace 'Armature' with the actual name of your armature object
    armature = bpy.data.objects[armature_name]
    keypoints = armature.pose.bones
    bone_struct = bpy.data.objects[armature_name].pose.bones
    
  
    #Get animation(.fbx) file paths
    anims_path = os.listdir(SRC_DATA_DIR)
    
    #Make OUT_DATA_DIR
    if not os.path.exists(OUT_DATA_DIR):
        os.makedirs(OUT_DATA_DIR)
    
    cam_idx = 0
    
    for anim_name in anims_path:
        # Replace 'start_frame' and 'end_frame' with the range of frames you want to process
        # Find the action and assign it to the armature's active action
        print(anim_name.split('.')[0])
        action = bpy.data.actions.get(anim_name.split('.')[0])
        if action:
            armature.animation_data.action = action
            start_frame = int(action.frame_range[0])
            end_frame = int(action.frame_range[1])
        else:
            print("No action found.")
                
        
        save_dir = os.path.join(OUT_DATA_DIR,anim_name.split('.')[0])
        #Make save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Create a dictionary to store 'prob' vectors for each camera
        occlusions_dict = {}
        
        for cam_name in camera_names:
            print("--------------------------------------------\n")
            print(cam_name)
            cam = bpy.data.objects.get(cam_name)
            prob = np.ones(( end_frame-start_frame+1 , 17))
            print(start_frame)
            for frame in range(start_frame, end_frame + 1):
                # Set the current frame
                bpy.context.scene.frame_set(frame)

                occluded_keypoints = []
                out_of_view_keypoints = []
                all_occlusions = []
                
                # Iterate over the keypoints (bones) of the armature
                for idx, name in enumerate(joint_names):
                    keypoint = armature.pose.bones[name]
                    global_location = armature.matrix_world @ bone_struct[name].matrix @ Vector((0, 0, 0))
                    
                    # Check if the keypoint is out of the viewport
                    if is_keypoint_out_of_view(keypoint, global_location, cam):
                        out_of_view_keypoints.append(keypoint.name)
                        all_occlusions.append(keypoint.name)
                        prob[frame-start_frame][idx] = 0
                        
                    elif is_occluded(keypoint, global_location, cam):
                        # Keypoint is occluded
                        occluded_keypoints.append(keypoint.name)
                        all_occlusions.append(keypoint.name)
                        prob[frame-start_frame][idx] = 0
                    
                   
                #if occluded_keypoints:
                    #print("Occluded keypoints in frame", frame)
                    #for keypoint_name in occluded_keypoints:
                        #print(keypoint_name)
                #else:
                    #print("No occluded keypoints in frame", frame)

                #if out_of_view_keypoints:
                    #print("Out-of-view keypoints:")
                    #for keypoint_name in out_of_view_keypoints:
                        #print(keypoint_name)
                #else:
                    #print("All keypoints are within the camera's viewport.")
                '''
                if occluded_keypoints or out_of_view_keypoints:
                    print("\n")
                    print("Camera", cam_name)
                    print("Frame", frame)
                    print("List of non visible keypoints: ")
                    for keypoint_name in all_occlusions:
                        print(keypoint_name)
                    print("---------------------------------------")
                    #exit(0)
                '''
            # Save 'prob' vector for this camera to a separate NPZ file
            print("Frame", frame)
            ''' # Get the absolute path of the script location
            script_path = bpy.path.abspath("//")
            # Create the directory to save the NPZ file if it does not exist
            save_path = os.path.join(script_path, save_dir)
            os.makedirs(save_path, exist_ok=True)
                        
            np.savez_compressed(os.path.join(save_path, f"occluded_kpt_Camera_{cam_idx}.npz"), prob=prob)'''
                   
            # Store the 2D positions in the dictionary with camera name as the key
            occlusions_dict[f'Camera_{cam_idx}'] = prob 
            cam_idx = cam_idx+1
               
    # Save 2D positions to another NPZ file
    # Get the absolute path of the script location
    script_path = bpy.path.abspath("//")
    # Create the directory to save the NPZ file if it does not exist
    save_path = os.path.join(script_path, save_dir)
    os.makedirs(save_path, exist_ok=True)
    np.savez_compressed(os.path.join(save_path, "occluded_kpt.npz"), Cam_0=occlusions_dict['Camera_0'],  Cam_1=occlusions_dict['Camera_1'],  Cam_2=occlusions_dict['Camera_2'],  Cam_3=occlusions_dict['Camera_3'])
    