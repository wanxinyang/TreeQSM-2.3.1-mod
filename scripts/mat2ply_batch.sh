#!/bin/bash

TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/python/"
OPTQSM_DIR="/data/TLS2/uk/ashtead/2025-12-11_Ashtead_P2.PROJ/models/optqsm"

python "${TREEQSM}/mat2ply.py" -i "${OPTQSM_DIR}"/*.mat -o "${OPTQSM_DIR}"
