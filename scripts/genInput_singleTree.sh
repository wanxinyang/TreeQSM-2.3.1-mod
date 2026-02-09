#!/bin/bash

TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/python/"
CLOUD_DIR="/PATH/TO/clouds/float64/TreeX.ply"
PARAMS_DIR="/PATH/TO/models/intermediate/params/TreeX"
QSM_CANDIDATE_DIR="/PATH/TO/models/qsm_candidates/TreeX"

python "${TREEQSM}/generate_inputs-updated-matlab.py" \
    -i "${CLOUD_DIR}" \
    -o "${PARAMS_DIR}" \
    -rdir "${QSM_CANDIDATE_DIR}" \
    --patchdiam1 0.2 0.25 0.3 \
    --patchdiam2min 0.05 0.1 0.15 \
    --patchdiam2max 0.15 0.2 0.25 \
    -n 3 \
    --lcyl 4