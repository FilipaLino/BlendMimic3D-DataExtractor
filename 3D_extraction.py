import bpy
import os
import sys
import json
from mathutils import Vector
import numpy as np 

HOME_FILE_PATH = os.path.abspath('homefile.blend')

RESOLUTION = (1000, 1002)

#Crucial joints sufficient for visualisation #FIX ME - Add more joints if desirable for MixamRig
BASE_JOINT_NAMES = ['Hips', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot', 
                    'Spine1', 'Neck','Head', 'HeadTop_End', 'RightArm', 'RightForeArm', 'RightHand', 
                    'LeftArm', 'LeftForeArm', 'LeftHand',
                    ]
#Source directory where .fbx exist
SRC_DATA_DIR ='regular'

#Ouput directory where .fbx to JSON dict will be stored
OUT_DATA_DIR ='fbx2json'

#Final directory where NPY files will ve stored
#FINAL_DIR_PATH ='json2npy'


def fbx2jointDict(joint_names, armature_name):
    
    
    #Remove 'Cube' object if exists in the scene
    if bpy.data.objects.get('Cube') is not None:
        cube = bpy.data.objects['Cube']
        bpy.data.objects.remove(cube)
    
    #Intensify Light Point in the scene
    if bpy.data.objects.get('Light') is not None:
        bpy.data.objects['Light'].data.energy = 2
        bpy.data.objects['Light'].data.type = 'POINT'
    
    #Set resolution and it's rendering percentage
    bpy.data.scenes['Scene'].render.resolution_x = RESOLUTION[0]
    bpy.data.scenes['Scene'].render.resolution_y = RESOLUTION[1]
    bpy.data.scenes['Scene'].render.resolution_percentage = 100
    
    #Base file for blender
    bpy.ops.wm.save_as_mainfile(filepath=HOME_FILE_PATH)
    
    #Get animation(.fbx) file paths
    anims_path = os.listdir(SRC_DATA_DIR)
  
    #Make OUT_DATA_DIR
    if not os.path.exists(OUT_DATA_DIR):
        os.makedirs(OUT_DATA_DIR)    
    
    for anim_name in anims_path:
        
        anim_file_path = os.path.join(SRC_DATA_DIR,anim_name)
        save_dir = os.path.join(OUT_DATA_DIR,anim_name.split('.')[0],'JointDict')
        
        #Make save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        #Load HOME_FILE and .fbx file
        bpy.ops.wm.read_homefile(filepath=HOME_FILE_PATH)
        bpy.ops.import_scene.fbx(filepath=anim_file_path)
       
        #End Frame Index for .fbx file
        frame_end = bpy.data.actions[0].frame_range[1]
        print(bpy.data.actions[0])
        #print(bpy.data.actions[1])
        print("Frames:")
        print(frame_end)
        
        
        for i in range(int(frame_end)):
           
            bpy.context.scene.frame_set(i+1)
            
            bone_struct = bpy.data.objects[armature_name].pose.bones
            armature = bpy.data.objects[armature_name]

            out_dict = {'pose_keypoints_3d': []}
        
            for name in joint_names:
                global_location = armature.matrix_world @ bone_struct[name].matrix @ Vector((0, 0, 0))
                l = [global_location[0], global_location[1], global_location[2]]
                out_dict['pose_keypoints_3d'].extend(l)
            
            save_path = os.path.join(save_dir,'%04d_keypoints.json'%i)
            with open(save_path,'w') as f:
                json.dump(out_dict, f)

def jointDict2npy(subject):
    
    json_dir = OUT_DATA_DIR
    npz_dir = f"../../BlendMimic3D/{subject}/D3_Positions"
    
    if not os.path.exists(npz_dir):
        os.makedirs(npz_dir)
        
    anim_names = os.listdir(json_dir)
   
    for anim_name in anim_names:
        files_path = os.path.join(json_dir,anim_name,'jointDict')
        frame_files = os.listdir(files_path)
        
        motion = []
        
        for frame_file in frame_files:
            file_path = os.path.join(files_path,frame_file)
            
            with open(file_path) as f:
                info = json.load(f)
                joint = np.array(info['pose_keypoints_3d']).reshape((-1, 3))
            motion.append(joint[:17,:])
            
            
        motion = np.stack(motion,axis=2)
        
        save_path = os.path.join(npz_dir,anim_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        print('Saving...')
        positions = motion.transpose(2, 0, 1)
        np.savez_compressed(os.path.join(save_path, anim_name + ".npz"), positions_3d=positions)
        
        print('Done.')

        data = motion
        print(data.shape)
        reshaped_data = np.reshape(data, (data.shape[0], -1))
        np.savetxt(save_path+'/'+'data3D.txt', reshaped_data, delimiter=' ') 
        
        ''' 
        cdf_data = data.transpose(2, 0, 1)
        # Define the attributes
        attributes = {
            'Version': '3.3.0',
            'Encoding': 6,
            'Majority': 'Column_major',
            'zVariables': ['Pose'],
            'Copyright': '\nCommon Data Format (CDF)\n(C) Copyright 1990-2009 NASA/GSFC\nSpace Physics Data Facility\nNASA/Goddard Space Flight Center\nGreenbelt, Maryland 20771 USA\n(Internet -- CDFSUPPORT@LISTSERV.GSFC.NASA.GOV)\n',
        }

        # Create a CDF file and open it for writing
        filename = 'data.cdf'
        cdffile = cdflib.CDF(filename, '')

        # Write the data to the CDF file
        cdffile.write(data)

        # Set the CDF attributes
        cdffile.attrs.update(attributes)

        # Close the CDF file
        cdffile.close()
        '''
    
        

        
if __name__ == '__main__':
    
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
               

    #Number of joints to be used from MixamoRig
    joint_names = ['mixamorig'+ joint_id +':' + x for x in BASE_JOINT_NAMES]
   
    #Convert .fbx files to JSON dict
    fbx2jointDict(joint_names, armature_name)
    
    #Convert JSON dict to NPY 
    jointDict2npy(subject)   

         


