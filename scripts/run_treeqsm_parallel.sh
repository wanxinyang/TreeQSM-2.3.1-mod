#!/bin/bash

# Parallel version of runqsm.sh
# Runs multiple TreeQSM .m files in parallel using GNU parallel or background jobs
#
# USAGE:
#   ./runqsm_parallel.sh
#
# ENVIRONMENT VARIABLES (optional):
#   MATLAB_MEM_GB    - Estimated memory per MATLAB job in GB (default: 12)
#   MAX_JOBS         - Manually override maximum parallel jobs
#
# EXAMPLES:
#   # Use default settings (max 5 jobs, accounting for MATLAB's internal parallelism)
#   ./runqsm_parallel.sh
#
#   # For large point clouds requiring more memory per job
#   MATLAB_MEM_GB=16 ./runqsm_parallel.sh
#
#   # Manually limit to 3 parallel jobs for best performance
#   MAX_JOBS=3 ./runqsm_parallel.sh

cd /PATH/TO/models/intermediate/params

# Function to check if output files already exist
check_output_exists() {
    local f="$1"
    # Extract the base name and parameters from the .m file
    # Expected pattern: TreeName_ParamSet_ModelNum.m -> TreeName-ParamSet-*.mat
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

# Function to run a single MATLAB file
run_matlab() {
    local f="$1"
    local idx="$2"
    local total="$3"
    
    # Check if output already exists
    if check_output_exists "$f"; then
        echo "[$idx/$total] Skipping $f (output files already exist)"
        return 0
    fi
    
    echo "[$idx/$total] Starting $f..."
    matlab -nodisplay -nosplash -r "run(fullfile(pwd,'$f')); exit;" > "${f%%.m}.log" 2>&1
    echo "[$idx/$total] Completed $f"
}

export -f run_matlab
export -f check_output_exists

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

# Detect number of CPU cores (leave 1 core free for system)
if command -v nproc &> /dev/null; then
    N_CORES=$(nproc)
elif command -v sysctl &> /dev/null; then
    N_CORES=$(sysctl -n hw.ncpu)
else
    N_CORES=4  # fallback default
fi

# Detect available memory and estimate safe number of parallel jobs
# Each MATLAB/TreeQSM process can use 8-15GB depending on point cloud size
# Default to 12GB per process based on observed usage, but allow override via environment variable
MATLAB_MEM_PER_JOB=${MATLAB_MEM_GB:-12}  # GB per MATLAB process (based on typical TreeQSM usage)

if [ -f /proc/meminfo ]; then
    # Linux: Get available memory in GB
    TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_MEM_GB=$((TOTAL_MEM_KB / 1024 / 1024))
    # Reserve 4GB for system, use remaining for jobs
    AVAILABLE_MEM_GB=$((TOTAL_MEM_GB - 4))
    AVAILABLE_MEM_GB=$((AVAILABLE_MEM_GB < 4 ? 4 : AVAILABLE_MEM_GB))
    
    # Calculate max jobs based on memory
    MEM_BASED_JOBS=$((AVAILABLE_MEM_GB / MATLAB_MEM_PER_JOB))
    MEM_BASED_JOBS=$((MEM_BASED_JOBS < 1 ? 1 : MEM_BASED_JOBS))
    
    echo "System memory: ${TOTAL_MEM_GB}GB total, ~${AVAILABLE_MEM_GB}GB available for jobs"
    echo "Memory-based limit: $MEM_BASED_JOBS parallel jobs (assuming ${MATLAB_MEM_PER_JOB}GB per job)"
elif command -v sysctl &> /dev/null && sysctl -n hw.memsize &> /dev/null; then
    # macOS: Get memory in bytes, convert to GB
    TOTAL_MEM_BYTES=$(sysctl -n hw.memsize)
    TOTAL_MEM_GB=$((TOTAL_MEM_BYTES / 1024 / 1024 / 1024))
    AVAILABLE_MEM_GB=$((TOTAL_MEM_GB - 4))
    AVAILABLE_MEM_GB=$((AVAILABLE_MEM_GB < 4 ? 4 : AVAILABLE_MEM_GB))
    
    MEM_BASED_JOBS=$((AVAILABLE_MEM_GB / MATLAB_MEM_PER_JOB))
    MEM_BASED_JOBS=$((MEM_BASED_JOBS < 1 ? 1 : MEM_BASED_JOBS))
    
    echo "System memory: ${TOTAL_MEM_GB}GB total, ~${AVAILABLE_MEM_GB}GB available for jobs"
    echo "Memory-based limit: $MEM_BASED_JOBS parallel jobs (assuming ${MATLAB_MEM_PER_JOB}GB per job)"
else
    # Fallback: be very conservative
    MEM_BASED_JOBS=2
    echo "Warning: Could not detect system memory, using conservative limit of $MEM_BASED_JOBS jobs"
fi

# Use available cores minus 1 (safer approach), but also respect memory limit
N_JOBS=$((N_CORES - 1))
N_JOBS=$((N_JOBS < 1 ? 1 : N_JOBS))
# Apply memory-based limit (choose the smaller of CPU-based or memory-based)
N_JOBS=$((N_JOBS < MEM_BASED_JOBS ? N_JOBS : MEM_BASED_JOBS))
# IMPORTANT: Each MATLAB job uses ~3 CPU cores internally
# So divide available cores by 3 to avoid oversubscription
MATLAB_CORES_PER_JOB=3
CPU_BASED_LIMIT=$((N_CORES / MATLAB_CORES_PER_JOB))
CPU_BASED_LIMIT=$((CPU_BASED_LIMIT < 1 ? 1 : CPU_BASED_LIMIT))
N_JOBS=$((N_JOBS < CPU_BASED_LIMIT ? N_JOBS : CPU_BASED_LIMIT))
# Additional safety: cap at 5 jobs to prevent overload (was 10, now more conservative)
N_JOBS=$((N_JOBS > 5 ? 5 : N_JOBS))
# Don't exceed files needing processing
N_JOBS=$((N_JOBS > need_run ? need_run : N_JOBS))

# Allow manual override via environment variable
if [ -n "$MAX_JOBS" ]; then
    echo "Manual override: MAX_JOBS=$MAX_JOBS"
    N_JOBS=$MAX_JOBS
fi

echo "Final decision: Using $N_JOBS parallel jobs"
echo "  - CPU cores available: $((N_CORES - 1)) (of $N_CORES total)"
echo "  - Memory-based limit: $MEM_BASED_JOBS jobs"
echo "  - Files to process: $need_run"
echo "Starting parallel execution..."
echo "----------------------------------------"

# Check if GNU parallel is available
if command -v parallel &> /dev/null; then
    # Method 1: Use GNU parallel (preferred - better load balancing)
    echo "Using GNU parallel for job execution"
    ls *.m | nl | parallel -j $N_JOBS --colsep '\t' run_matlab {2} {1} $total
else
    # Method 2: Use background jobs with manual process control
    echo "Using bash background jobs for execution"
    echo "(Tip: Install GNU parallel for better performance: sudo apt-get install parallel)"
    
    count=0
    running=0
    
    for f in *.m; do
        count=$((count+1))
        
        # Start job in background
        run_matlab "$f" "$count" "$total" &
        running=$((running+1))
        
        # Wait if we've reached max parallel jobs
        if [ $running -ge $N_JOBS ]; then
            wait -n  # Wait for any job to finish
            running=$((running-1))
        fi
    done
    
    # Wait for all remaining jobs to complete
    wait
fi

echo "----------------------------------------"
echo "All jobs completed!"
echo "Total files checked: $total"
echo "Files processed: $need_run"
echo "Files skipped: $((total-need_run))"
echo ""
echo "Check individual log files (*.log) for details"

# Optional: Generate summary of results
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
