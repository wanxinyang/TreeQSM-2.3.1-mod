# Modified TreeQSM-2.3.1 and a pipeline for enhanced batch processing and ply conversion

This repository is a modified version of [TreeQSM v2.3.1](https://github.com/InverseTampere/TreeQSM/releases/tag/v2.3.1), aimed at improving I/O flexibility for batch processing of QSM (Quantitative Structure Model) reconstructions from point clouds in ply format. 

Key features of this fork:
- Easy generation of multiple, customisable TreeQSM input files.
- Batch execution of TreeQSM scripts and integration with `optqsm` for best-fit model selection.
- Additional Python tools for:
  - Converting PLY files to float64 which runqsm accepts.
  - Converting QSM `.mat` output into `.ply` files for visualisation in tools like CloudCompare.

---

## Installation

### 1. Clone the repositories
Download the modified TreeQSM and optqsm source code to your local machine:

```bash
git clone https://github.com/wanxinyang/TreeQSM-2.3.1-mod.git
git clone https://github.com/wanxinyang/optqsm-mod.git
```

### 2. Create and activate the conda environment

```bash
conda create -n treeqsm python=3.10 pandas numpy scipy -c conda-forge -y
conda activate treeqsm
```

---

## Workflow

### Directory Structure Example
Recommonded file structure:

```
DATA/
├── clouds/                     # Original and converted point clouds (.ply)
│   └── float64/                # Output of ply2float64.py
├── models/                     # Workspace for processing and results
│   ├── param/                  # TreeQSM input parameter sets (.m files)       
│   ├── results/                # QSM reconstruction results using all parameter sets
│   │   └── Tree_A/  
│   │   │   └── Tree_A-1-1.mat  # QSM using parameter set 1, model 1
│   │   │   └── Tree_A-1-2.mat  # QSM using parameter set 1, model 2
│   │   │   └── Tree_A-2-1.mat  # QSM using parameter set 2, model 1
│   │   │   └── ...
│   │   └── Tree_B/   
│   │       └── Tree_B-1-1.mat
│   │       └── ...      
│   └── optqsm/                 # Selected best-fitting QSMs
│       └── Tree_A_opt.mat
│       └── Tree_B_opt.mat
```


### Step 1: Convert point cloud files to float64 (if needed)

#### Option A: Convert all `.ply` files in a directory

Replace /PATH/TO/ in all following commands according to your local file structure.

```bash
python /PATH/TO/TreeQSM-2.3.1-mod/python/ply2float64.py -i /PATH/TO/clouds/
```

#### Option B: Convert a single `.ply` file

```bash
python /PATH/TO/TreeQSM-2.3.1-mod/python/ply2float64.py -i /PATH/TO/file.ply
```
**Available Flags:**

```
-i, --input       Path to a .ply file or a directory containing .ply files
-o, --output      Directory to save converted PLY file(s); defaults to a 'float64/'
--suffix          Optional suffix added before the .ply extension in output filenames; use 'none' to disable the suffix
```
---

### Step 2: Generate TreeQSM input files

The script requires a single point cloud file (`-i` / `--input`) in either .ply or .txt format. 

```bash
python /PATH/TO/TreeQSM-2.3.1-mod-matlab/python/generate_inputs-updated-matlab.py -i /PATH/TO/POINT_CLOUD.ply
```

The optional arguments to customise the output filename and directory:

```
-o, --output          Path and filename for the generated TreeQSM parameter set (.m file). Note, the filename must not contain arithmetic operators such as . + - * / .
-rdir, --results_dir  Directory where TreeQSM results (.mat files) will be stored. Defaults to the current working directory.
```

The optional arguments to customise key TreeQSM input parameters for QSM generation:
( for additional parameters, run the script with the `-h` flag to view the help message. )
```
--patchdiam1         List of candidate values for PatchDiam1 (patch size of the first uniform-size cover). Default: [0.2]
--patchdiam2min      List of candidate values for PatchDiam2Min (minimum patch size of cover sets in the second cover). Default: [0.05]
--patchdiam2max      List of candidate values for PatchDiam2Max (maximum cover set size in the stem's base for the second cover). Default: [0.15]
-n, --n_models       Number of iterations to run TreeQSM for each parameter set. Default: 1
--lcyl               (length/radius) ratio of fitting cylinders; controls the aspect ratio of model cylinders. Default: 4
```

Example with custom parameter values:
```
python generate_inputs-updated-matlab.py \
  -i clouds/float64/Tree_A.ply \
  -o models/param/Tree_A_param.m \
  -rdir models/results/Tree_A/ \
  --patchdiam1 0.2 0.25 0.3 \
  --patchdiam2min 0.05 0.1 0.15 \
  --patchdiam2max 0.15 0.2 0.25 \
  -n 3 \
  --lcyl 4
```


---

### Step 3: Run TreeQSM in MATLAB through command line

#### Option A: Run a single input `.m` file

```bash
matlab -nodisplay -r "run('FILENAME.m'); exit;" > FILENAME.log
```

#### Option B: Batch-run all `.m` files in a directory

```bash
cd /PATH/TO/models/param/

total=$(ls *.m | wc -l)
count=0
for f in *.m; do
  count=$((count+1))
  echo "[$count/$total] Running $f..."
  matlab -nodisplay -nosplash -r "run(fullfile(pwd,'$f')); exit;" > "${f%%.m}.log"
done
```

---

### Step 4: Run `optqsm` to select the best-fitting QSM

```bash
cd /PATH/TO/models/
mkdir -p optqsm && cd optqsm/

matlab -nodisplay -r "addpath(genpath('/PATH/TO/TreeQSM-2.3.1-mod/src/')); \
addpath('/PATH/TO/optqsm-mod/src/'); runopt('../results/*/*.mat'); exit;" > optqsm-log.log
```

---

### Step 5: Convert best-fitting QSM `.mat` files into `.ply`

```bash
conda activate treeqsm
cd /PATH/TO/models/optqsm/

python /PATH/TO/TreeQSM-2.3.1-mod/python/mat2ply.py ./*.mat
```

---

## Example for batch processing
```bash
conda activate treeqsm
/PATH/TO/TreeQSM-2.3.1-mod/scripts/genInput_batch.sh
/PATH/TO/TreeQSM-2.3.1-mod/scripts/runqsm.sh
/PATH/TO/TreeQSM-2.3.1-mod/scripts/run_optqsm.sh
```

---

## License

This repository follows the original [TreeQSM license](https://github.com/InverseTampere/TreeQSM/blob/master/LICENSE) and [optqsm license](https://github.com/apburt/optqsm/blob/master/LICENSE).
