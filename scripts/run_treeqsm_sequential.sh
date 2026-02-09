#!/bin/bash

# Sequential version of runqsm.sh with output file checking
# Runs TreeQSM .m files one at a time, skipping files with existing outputs

cd /PATH/TO/models/intermediate/params

# Function to check if output files already exist
check_output_exists() {
    local f="$1"
    # Extract the base name and parameters from the .m file
    local base=$(basename "$f" .m)
    
    # Parse the output directory from the .m file (look for input.name pattern)
    local result_dir=$(grep -m 1 "input.name.*strcat" "$f" | sed -n "s/.*'\(.*\)\/[^/]*'.*/\1/p")
    
    if [ -z "$result_dir" ]; then
        # Fallback: try to extract from direct path assignment
        result_dir=$(grep -m 1 "input.name = " "$f" | sed -n "s/.*'\(.*\)\/[^/]*'.*/\1/p")
    fi
    
    # Extract the expected number of models from the for loop in the .m file
    # Look for patterns like "for i = 1:3" or "for i = 1:5"
    local expected_models=$(grep -oP 'for\s+i\s*=\s*1:\K\d+' "$f" | head -1)
    
    # Default to 3 if not found
    if [ -z "$expected_models" ]; then
        expected_models=3
    fi
    
    if [ -n "$result_dir" ] && [ -d "$result_dir" ]; then
        # Extract tree name and parameter set from filename
        # e.g., Ashtead_P1_T01_1.m -> Ashtead_P1_T01-1-*.mat
        local tree_param=$(echo "$base" | sed 's/_\([0-9]*\)$/-\1-/')
        
        # Check if all expected .mat files exist
        local mat_count=$(ls "${result_dir}/${tree_param}"*.mat 2>/dev/null | wc -l)
        
        if [ "$mat_count" -ge "$expected_models" ]; then
            return 0  # Files exist, skip
        fi
    fi
    
    return 1  # Files don't exist, need to run
}

# Count total files
total=$(ls *.m | wc -l)
echo "Found $total .m files to process"

# Check how many need to run (pre-scan)
need_run=0
for f in *.m; do
    if ! check_output_exists "$f"; then
        need_run=$((need_run+1))
    fi
done
echo "Files needing processing: $need_run (skipping $((total-need_run)) with existing outputs)"
echo "Starting sequential execution..."
echo "----------------------------------------"

# Process files sequentially
count=0
processed=0
skipped=0
for f in *.m; do
    count=$((count+1))
    
    # Check if output already exists
    if check_output_exists "$f"; then
        echo "[$count/$total] Skipping $f (output files already exist)"
        skipped=$((skipped+1))
    else
        echo "[$count/$total] Running $f..."
        matlab -nodisplay -nosplash -r "run(fullfile(pwd,'$f')); exit;" > "${f%%.m}.log" 2>&1
        echo "[$count/$total] Completed $f"
        processed=$((processed+1))
    fi
done

echo "----------------------------------------"
echo "All jobs completed!"
echo "Total files checked: $total"
echo "Files processed: $processed"
echo "Files skipped: $skipped"
echo ""
echo "Check individual log files (*.log) for details"

# Generate summary of results
echo "Generating summary..."
success=0
failed=0
for log in *.log; do
    if grep -q "error\|Error\|ERROR" "$log" 2>/dev/null; then
        failed=$((failed+1))
    else
        success=$((success+1))
    fi
done

echo "Summary: $success succeeded, $failed may have errors"
echo "Review log files for details."