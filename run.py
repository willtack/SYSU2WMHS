#!/usr/bin/env python3

import os
import flywheel
import shutil
from pathlib import PosixPath


# Get relevant container objects
context = flywheel.GearContext()
config = context.config
analysis_id = context.destination['id']

fw = flywheel.Client(context.get_input('api_key')['key'])
analysis_container = fw.get(analysis_id)
project_container = fw.get(analysis_container.parents['project'])
session_container = fw.get(analysis_container.parent['id'])
subject_container = fw.get(session_container.parents['subject'])
subject_label = subject_container.label

output_file_FLAIR_name = 'subject' + '_sysu2_FLAIR_' + analysis_id + '.nii.gz'
output_file_T1_name = 'subject' + '_sysu2_T1_' + analysis_id + '.nii.gz'

# Inputs and configs
os.system('mkdir /input')
os.system('mkdir /output')
os.system('mkdir /input/pre')
os.system('mkdir /input/mat')

flair_path = context.get_input_path('FLAIR')
path = os.path.dirname(flair_path) # get the path minus the filename
newname = os.path.join(path, 'FLAIR.nii.gz') # new name is path plus 'FLAIR_INPUT.nii.gz'
os.rename(flair_path, newname) # do the rename

t1_path = context.get_input_path('T1')
path = os.path.dirname(t1_path) # get the path minus the filename
newname = os.path.join(path, 'T1_INPUT.nii.gz') # new name is path plus 'T1.nii.gz'
os.rename(t1_path, newname) # do the rename

# Transform using FSL
os.system('/usr/share/fsl/bin/flirt -in /flywheel/v0/input/T1/T1_INPUT.nii.gz -ref /flywheel/v0/input/FLAIR/FLAIR.nii.gz -out /flywheel/v0/input/T1/T1.nii.gz -dof 6 -searchrx -180 180 -searchry -180 180 -searchrz -180 180 -omat /input/mat/T12FLAIR.mat') #possible straight directory for -out flag

for fname in os.listdir('/flywheel/v0/input'):
      if os.path.isfile(os.path.join('/flywheel/v0/input/FLAIR', 'FLAIR.nii.gz')):
          shutil.copy(os.path.join('/flywheel/v0/input/FLAIR', 'FLAIR.nii.gz'), os.path.join('/input/pre', 'FLAIR.nii.gz'))
      if os.path.isfile(os.path.join('/flywheel/v0/input/T1', 'T1.nii.gz')):
           shutil.copy(os.path.join('/flywheel/v0/input/T1', 'T1.nii.gz'), os.path.join('/input/pre', 'T1.nii.gz'))

# Commands
os.system("python /wmhseg_example/example.py")
os.system('/opt/convert3d-nightly/bin/c3d /input/pre/FLAIR.nii.gz /output/result.nii.gz -copy-transform -o /output/result.nii.gz')
shutil.copy(os.path.join('/output', 'result.nii.gz'), os.path.join('/flywheel/v0/output', output_file_FLAIR_name))



# convert to FLAIR space and write
os.system('/usr/share/fsl/bin/convert_xfm -omat /input/mat/FLAIR2T1.mat -inverse /input/mat/T12FLAIR.mat')
os.system('/usr/share/fsl/bin/applywarp --ref=/flywheel/v0/input/T1/T1_INPUT.nii.gz --in=/output/result.nii.gz --out=/output/resultT1.nii.gz --premat=/input/mat/FLAIR2T1.mat --interp=nn')
shutil.copy(os.path.join('/output','resultT1.nii.gz'), os.path.join('/flywheel/v0/output', output_file_T1_name))

