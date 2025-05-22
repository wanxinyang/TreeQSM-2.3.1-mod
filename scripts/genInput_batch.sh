#!/bin/bash

QSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/python/"
IN_DIR="/data/TLS2/uk/epping-pollards/demo/clouds/float64"
OUT_DIR="/data/TLS2/uk/epping-pollards/demo/models/param"
RDIR="/data/TLS2/uk/epping-pollards/demo/models/results"

for ply_file in "${IN_DIR}"/*.ply; do
    base_name=$(basename "${ply_file}" .ply)
    # out_file="${OUT_DIR}/${base_name}_param"

    python "${QSM}/generate_inputs-updated-matlab.py" \
        -i "${ply_file}" \
        -o "${OUT_DIR}/${base_name}" \
        -rdir "${RDIR}/${base_name}/" \
        --patchdiam1 0.2 0.25 0.3 \
        --patchdiam2min 0.05 0.1 0.15 \
        --patchdiam2max 0.15 0.2 0.25 \
        -n 3 \
        --lcyl 4
done