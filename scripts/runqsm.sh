#!/bin/bash
cd /data/TLS2/uk/epping-pollards/demo/models/param/

total=$(ls *.m | wc -l)
count=0
for f in *.m; do
  count=$((count+1))
  echo "[$count/$total] Running $f..."
  matlab -nodisplay -nosplash -r "run(fullfile(pwd,'$f')); exit;" > "${f%%.m}.log"
done