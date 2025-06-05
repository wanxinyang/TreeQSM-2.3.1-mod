#!/bin/bash

# Set directory paths
QSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/python/"
PLY_DIR="/data/TLS2/uk/epping-pollards/demo/clouds"
OUT_DIR="/data/TLS2/uk/epping-pollards/demo/clouds/float64"

# Loop over each .ply file in PLY_DIR
for ply_file in "${PLY_DIR}"/*.ply; do
    base_name=$(basename "$ply_file" .ply)
    output_file="${base_name}_float64.ply"
    python "${QSM}/ply2float64.py" -i "$ply_file" -o "${OUT_DIR}/${output_file}"
done