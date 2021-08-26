#!/usr/bin/env python3

import os
import flywheel
import shutil
from pathlib import PosixPath

# Get relevant container objects
context = flywheel.GearContext()
config = context.config
analysis_id = context.destination['id']
gear_output_dir = str(PosixPath(context.output_dir))

fw = flywheel.Client(context.get_input('api_key')['key'])
analysis_container = fw.get(analysis_id)
project_container = fw.get(analysis_container.parents['project'])
session_container = fw.get(analysis_container.parent['id'])
subject_container = fw.get(session_container.parents['subject'])
subject_label = subject_container.label

#output_file_FLAIR_name = 'subject' + '_sysu2_FLAIR_' + analysis_id + '.nii.gz'
# output_file_T1_name = 'subject' + '_sysu2_T1_' + analysis_id + '.nii.gz'
outfile_root = 'sub-' + subject_label + '_' + analysis_id + '_sysu2'
output_file_FLAIR_name = outfile_root+'_space-flair_desc-dseg.nii.gz'
output_file_T1_name = outfile_root+'_space-T1w_desc-dseg.nii.gz'

# Inputs and configs
os.system('mkdir -p /output')
os.system('mkdir -p /input/pre')
os.system('mkdir -p /input/mat')

flair_file = context.get_input_path('FLAIR')
flair_path = os.path.dirname(flair_file) # get the path minus the filename
new_flair_file = os.path.join(flair_path, 'FLAIR.nii.gz')
if os.path.isfile(flair_file) and not os.path.isfile(new_t1_file): # Don't run if already renamed (i.e. in debugging)
    os.rename(flair_file, new_flair_file)

t1_file = context.get_input_path('T1')
t1_path = os.path.dirname(t1_file) # get the path minus the filename
new_t1_file = os.path.join(t1_path, 'T1_INPUT.nii.gz')
if os.path.isfile(t1_file) and not os.path.isfile(new_t1_file):
    os.rename(t1_file, new_t1_file)

# RUN PROGRAM STEPS
# 1) Trim T1
# 2) Register T1 to FLAIR
# 3) Run SYSU2 which will output the segmented mask
# 4) Estimate FLAIR-T1 (just the inverse of the previous registration)
# 5) Warp the segmentation in the FLAIR space to the T1 space. This will help in subsequent normalization step.

# Trim T1
trim_output = os.path.join(gear_output_dir, outfile_root+'_TrimNeckOutput.txt')
cmd = "bash trim_neck.sh -d {0} {0} > {1} || echo 'Neck trimming exited with nonzero status';exit".format(new_t1_file, trim_output)
print(cmd)
os.system(cmd)
shutil.copy(new_t1_file, os.path.join(gear_output_dir, outfile_root+'_desc-necktrim_T1w.nii.gz')) # copy results to output folder

# Register T1 to FLAIR (Transform using FSL)
t1_in_flair = os.path.join(t1_path, 'T1.nii.gz')
os.system('/usr/share/fsl/bin/flirt -in {} -ref {} -out {} -dof 6 -searchrx -180 180 -searchry -180 180 -searchrz -180 180 -omat /input/mat/T12FLAIR.mat'.format(new_t1_file, new_flair_file, t1_in_flair)) #possible straight directory for -out flag
shutil.copy(t1_in_flair, os.path.join(gear_output_dir, outfile_root+'_space-flair_desc-necktrim_T1w.nii.gz'))

# Run SYSU2 which will output the segmented mask in FLAIR space
# copy T1 and FLAIR to location where main algo can find e.g. /input/pre/T1.nii.gz
for fname in os.listdir('/flywheel/v0/input'):
      if os.path.isfile(new_flair_file):
          shutil.copy(new_flair_file, '/input/pre/FLAIR.nii.gz')
      if os.path.isfile(t1_in_flair):
           shutil.copy(t1_in_flair, '/input/pre/T1.nii.gz')

os.system("python /wmhseg_example/example.py") # RUN ALGORITHM
os.system('/opt/bin/c3d /input/pre/FLAIR.nii.gz /output/result.nii.gz -copy-transform -o /output/result.nii.gz') # copy FLAIR transform to results
shutil.copy('/output/result.nii.gz', os.path.join(gear_output_dir, output_file_FLAIR_name)) # copy result to outputfolder

# Estimate FLAIR-T1 (just the inverse of the previous registration) (convert to FLAIR space and write)
os.system('/usr/share/fsl/bin/convert_xfm -omat /input/mat/FLAIR2T1.mat -inverse /input/mat/T12FLAIR.mat')

# Warp the segmentation in the FLAIR space to the T1 space. This will help in subsequent normalization step.
os.system('/usr/share/fsl/bin/applywarp --ref={} --in=/output/result.nii.gz --out=/output/resultT1.nii.gz --premat=/input/mat/FLAIR2T1.mat --interp=nn'.format(new_t1_file))

# copy segmentation in T1 space to output folder
shutil.copy('/output/resultT1.nii.gz', os.path.join(gear_output_dir, output_file_T1_name))
