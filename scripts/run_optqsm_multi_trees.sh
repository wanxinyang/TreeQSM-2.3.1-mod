#!/bin/bash
cd /PATH/TO/models/optqsm/

# Set paths (edit as needed)
TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/src/"
OPTQSM="/data/TLS2/tools/qsm/optqsm-mod-matlab/src/"
QSM_CANDIDATE_DIR="/PATH/TO/models/intermediate/qsm_candidates/"

# Loop over subdirectories
for SUBDIR in "$QSM_CANDIDATE_DIR"/*/; do
    # Check if the subdir contains any .mat files
    MAT_FILES=("$SUBDIR"*.mat)
    if [ -e "${MAT_FILES[0]}" ]; then
        # Prepare MATLAB wildcard pattern
        MATLAB_PATTERN="${SUBDIR}*.mat"
        # Use subdirectory name for log file
        SUBDIR_NAME=$(basename "$SUBDIR")
        echo "Running optqsm for: $MATLAB_PATTERN"
        matlab -nodisplay -r "addpath(genpath('${TREEQSM}')); addpath('${OPTQSM}'); runopt('${MATLAB_PATTERN}'); exit;" > "${SUBDIR_NAME}_opt.log"
    else
        echo "No .mat files found in $SUBDIR"
    fi
done