#!/bin/bash
cd /data/TLS2/uk/epping-pollards/demo/models/newoptqsm/

# Set paths (edit as needed)
TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/src/"
OPTQSM="/data/TLS2/tools/qsm/optqsm-mod-matlab/src/"
QSMs="/data/TLS2/uk/epping-pollards/demo/models/results/Scan_11_extracted_float64/*.mat"
QSMs_DIR=$(dirname "${QSMs}")
QSMs_DIR=$(basename "${QSMs_DIR}")

echo "Running optqsm from results in: ${QSMs}"

matlab -nodisplay -r "addpath(genpath('${TREEQSM}')); addpath('${OPTQSM}'); \
runopt('${QSMs}'); exit;" > ${QSMs_DIR}_opt.log