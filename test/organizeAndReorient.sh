#!/bin/bash
#
# Put image files in acquisition folders to facilitate Flywheel upload and reorient images to
# standard coordinates. Also, scale by factor of 10

dataDir='./test-data'

for subj in ${dataDir}/*S*; do
  for ses in ${subj}/20*; do
    # reorient and scale
    subName=$(basename $subj)
    sesName=$(basename $ses)
    root=${ses}/${sesName}_${subName}
    fslreorient2std ${root}_flair.nii.gz ${root}_reorient_flair.nii.gz
    fslreorient2std ${root}_T1w_trim_to_flair.nii.gz ${root}_reorient_T1w_trim_to_flair.nii.gz
    fslmaths ${root}_reorient_flair.nii.gz -mul 10 ${root}_reorient_10_flair.nii.gz

    #reorganize
    mkdir -p ${ses}/T1w
    mkdir -p ${ses}/FLAIR
    flair_list=$(find ${ses} -type f | grep _flair.nii.gz | grep -v T1w)
    for f in ${flair_list}; do
      cp $f ${ses}/FLAIR/ # inc. normal flair, *reorient_flair, *reorient_10_flair
    done
    cp ${ses}/*_T1w_trim*.nii.gz ${ses}/T1w/ # inc. normal T1w, *reorient_T1w, *reorient_10_T1w
  done
done
