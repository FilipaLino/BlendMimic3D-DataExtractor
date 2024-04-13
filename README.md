# BlendMimic3D-DataExtractor: Blender Data Extraction Tool

## Overview
The BlendMimic3D-DataExtractor is designed to convert .fbx files to .npy format, specifically for human motion analysis. This repository contains scripts that require Blender to run.
<p align="left">
  <img src="https://github.com/FilipaLino/BlendMimic3D-DataExtractor/assets/102179022/822a0ad3-0944-40a4-b720-27f116984e42" width="40%" height="40%">
</p>


Blender can be downloaded from the [official website](https://www.blender.org/download/).

## Dependencies
- Blender
- Python

## Contents
- `2D_extraction.py`: Extracts 2D joint data.
- `3D_extraction.py`: Converts .fbx files to .npz files containing 3D joint data.
- `camParams.py`: Extracts camera parameters used in the animations.
- `occlusion.py`: Simulates occlusions in the data.
- `fbx2jason/`: Intended for storing .fbx files converted to JSON.
- `regular/`: Default directory for placing sample .fbx files.

## Setup
1. Clone or download this repository to your local machine.
2. Ensure Blender is installed and added to your system PATH.

## Usage Instructions

### General Usage
Before running the scripts, download a sample .fbx file from Mixamo ([link](https://www.mixamo.com/#/?page=1&type=Motion%2CMotionPack)) and place it into the `regular` folder.

### 3D Data Extraction
1. Move the .fbx file to the `regular` folder.
2. Open a command prompt with administrator permissions.
3. Change to the directory containing `3D_extraction.py`.
4. Execute the script with the following command:
   ```
   blender --background -P 3D_extraction.py -- --joint-id 8 --armature-name Armature.001 --subject S1
   ```

### Camera Parameters Extraction
1. Change to the directory containing `camParams.py`.
2. Execute the script with the following command:
   ```
   blender --background H3.6M.blend --python camParams.py -- S1
   ```

### 2D Data Conversion
1. Change to the directory containing `2D_extraction.py`.
2. Execute the script with the following command:
   ```
   blender --background H3.6M.blend --python 2D_extraction.py -- S1 WalkCircle
   ```

### Occlusion Handling
1. Change to the directory containing `occlusion.py`.
2. Execute the script with the following command:
   ```
   blender --background H3.6M.blend --python occlusion.py -- --joint-id 8 --armature-name Armature.001 --subject S1
   ```

## Contributing
Contributions are welcome. Please open an issue or submit a pull request with your suggested changes.

## Citation
If you use our code in your research, please cite our paper: 
```
[ citation format]
```

## Aknowledgements
This work was supported by LARSyS funding (DOI: 10.54499/LA/P/0083/2020, 10.54499/UIDP/50009/2020, and 10.54499/UIDB/50009/2020) and 10.54499/2022.07849.CEECIND/CP1713/CT0001, through Fundação para a Ciência e a Tecnologia, and by the SmartRetail project [PRR - C645440011-00000062], through IAPMEI - Agência para a Competitividade e Inovação.
<p align="center">
  <img src="https://github.com/FilipaLino/BlendMimic3D/assets/102179022/670897d0-1f7d-43e8-b63b-b2b961242730" width="50%" height="50%">
</p>

