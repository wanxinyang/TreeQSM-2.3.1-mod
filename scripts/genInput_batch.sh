#!/bin/bash

TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/python/"
CLOUD_DIR="/PATH/TO/clouds/float64"
PARAMS_DIR="/PATH/TO/models/intermediate/params"
QSM_CANDIDATE_DIR="/PATH/TO/models/qsm_candidates"

for ply_file in "${CLOUD_DIR}"/*.ply; do
    base_name=$(basename "${ply_file}" .ply)
    # out_file="${OUT_DIR}/${base_name}_param"

    python "${TREEQSM}/generate_inputs-updated-matlab.py" \
        -i "${ply_file}" \
        -o "${PARAMS_DIR}/${base_name}" \
        -rdir "${QSM_CANDIDATE_DIR}/${base_name}/" \
        --patchdiam1 0.2 0.25 0.3 \
        --patchdiam2min 0.05 0.1 0.15 \
        --patchdiam2max 0.15 0.2 0.25 \
        -n 3 \
        --lcyl 4
done