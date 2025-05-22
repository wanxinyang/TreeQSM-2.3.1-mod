#!/bin/bash

QSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/python/"

python "${QSM}/generate_inputs-updated-matlab.py" \
    -i /data/TLS2/uk/epping-pollards/demo/clouds/float64/Scan_14_extracted_float64.ply \
    -o /data/TLS2/uk/epping-pollards/demo/models/param/Scan_14_param \
    -rdir /data/TLS2/uk/epping-pollards/demo/models/results/Scan_14/ \
    --patchdiam1 0.2 0.25 0.3 \
    --patchdiam2min 0.05 0.1 0.15 \
    --patchdiam2max 0.15 0.2 0.25 \
    -n 3 \
    --lcyl 4