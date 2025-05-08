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
Organise your data as follows before running the workflow:

```
DATA/
├── clouds/              # Original and converted point clouds (.ply)
│   └── float64/         # Output of ply2float64.py
├── models/              # Workspace for processing and results
│   ├── inputs/          # TreeQSM input .m files
│   ├── results/         # QSM reconstruction results (.mat)
│   └── optqsm/          # Selected best-fitting QSMs and logs
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
-i, --input INPUT       Path to a .ply file or a directory containing .ply files
-o, --output OUTPUT     Directory to save converted PLY file(s); defaults to a 'float64/'
                        directory created alongside the input
--suffix SUFFIX     Optional suffix added before the .ply extension in output filenames;
                        use 'none' to disable the suffix
```

---

### Step 2: Generate TreeQSM input files

```bash
python /PATH/TO/TreeQSM-2.3.1-mod/python/generate_inputs-updated-matlab.py -i /PATH/TO/clouds/float64/ -o /PATH/TO/inputs/ --treeqsm_src /PATH/TO/TreeQSM-2.3.1-mod/src/
```

For additional options to customise input parameters, run the script with the `-h` flag to view the help message.

A `results/` directory will be automatically generated alongside `inputs/`.

---

### Step 3: Run TreeQSM in MATLAB through command line

#### Option A: Run a single input `.m` file

```bash
matlab -nodisplay -r "run('FILENAME.m'); exit;" > FILENAME.log
```

#### Option B: Batch-run all `.m` files in a directory

```bash
cd /PATH/TO/models/inputs/TREEID/

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

## License

This repository follows the original [TreeQSM license](https://github.com/InverseTampere/TreeQSM/blob/master/LICENSE) and [optqsm license](https://github.com/apburt/optqsm/blob/master/LICENSE).

