#!/bin/bash
cd /data/TLS2/uk/epping-pollards/demo/models/newoptqsm/

# Set paths (edit as needed)
TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/src/"
OPTQSM="/data/TLS2/tools/qsm/optqsm-mod-matlab/src/"
PARENT_DIR="/data/TLS2/uk/epping-pollards/demo/models/results/"

# Loop over subdirectories
for SUBDIR in "$PARENT_DIR"/*/; do
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