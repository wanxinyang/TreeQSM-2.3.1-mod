#!/bin/bash
cd /data/TLS2/uk/epping-pollards/demo/models/optqsm/

TREEQSM="/data/TLS2/tools/qsm/TreeQSM-2.3.1-mod-matlab/src/"
OPTQSM="/data/TLS2/tools/qsm/optqsm-mod-matlab/src/"
RESULTS="/data/TLS2/uk/epping-pollards/demo/models/results/*/*.mat"

echo "Running optqsm from results in: ${RESULTS}"

matlab -nodisplay -r "addpath(genpath('${TREEQSM}')); addpath('${OPTQSM}'); \
runopt('${RESULTS}'); exit;" > optqsm-log.log