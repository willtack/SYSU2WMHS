i)                    For each subject, the **_flair.nii.gz** and **_T1w_trim_to_flair.nii.gz** files were uploaded to Flywheel with `upload_data.ipynb` and used as inputs to the SYSU2 WMH segmentation algorithm.

ii)                   The FLAIR images had weird orientations, so `fslreorient2std` was used to bring the **FLAIR** and **T1_trim_to_flair** images into the correct orientation. Each FLAIR image was scaled by a factor of 10. `organizeAndReorient.sh` was called to accomplish these steps.

iii)                  The SYSU2 gear was run on these data in Flywheel using `run_gear.ipynb`. The **T1w_trim_to_flair** had already been registered to the FLAIR. The calculated segmentations were downloaded from Flywheel with `download_WMH_segmentations.ipynb`

v)                    The DICE coefficient for each segmentation was calculated with `dice_calculation.ipynb` using the *EDIT1* files as reference. The output is `overlap_data.csv`. 
