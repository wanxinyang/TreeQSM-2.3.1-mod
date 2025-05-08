import os
import glob
import sys
import numpy as np
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate input .m files for TreeQSM modelling with configurable parameters.'
    )
    parser.add_argument('-i', '--inputs',
                        nargs='+', required=True,
                        help=('One or more paths to point cloud files (.ply/.txt) or a directory. ' 
                              'If a directory is provided, all .ply files within (recursively) will be used.'))
    parser.add_argument('-o', '--output_path',
                        type=str, required=True,
                        help='Directory to store generated .m input scripts.')
    parser.add_argument('--treeqsm_src',
                        type=str, default='/data/TLS2/tools/qsm/TreeQSM_2.3.1-matlab/src/',
                        help="Path to TreeQSM source code (default: '%(default)s').")
    parser.add_argument('--optqsm_src',
                        type=str, default='/data/TLS2/tools/qsm/optqsm/src/',
                        help="Path to OptQSM source code (default: '%(default)s').")
    parser.add_argument('--patchdiam1',
                        type=float, nargs='+',
                        default=[0.2, 0.25, 0.3],
                        help=('List of candidate values for PatchDiam1 (Patch size of the first uniform-size cover). ' 
                              f'Default: [0.2, 0.25, 0.3].'))
    parser.add_argument('--patchdiam2min',
                        type=float, nargs='+',
                        default=[0.05, 0.1, 0.15],
                        help=('List of candidate values for PatchDiam2Min (Minium patch size of the cover sets in the second cover). ' 
                              f'Default: [0.05, 0.1, 0.15].'))
    parser.add_argument('--patchdiam2max',
                        type=float, nargs='+',
                        default=[0.15, 0.2, 0.25],
                        help=("List of candidate values for PatchDiam2Max (Maximum cover set size in the stem's base in the second cover). " 
                              f'Default: [0.15, 0.2, 0.25].'))
    parser.add_argument('-n', '--n_models',
                        type=int, default=5,
                        help='Number of iterations to run TreeQSM for the same parameter set (default: %(default)s).')
    parser.add_argument('--lcyl',
                        type=int, default=4,
                        help='(length/radius) ratio of fitting cylinders (default: %(default)s).')
    parser.add_argument('--filrad',
                        type=float, default=3.5,
                        help=('Relative radius for outlier filtering (default: %(default)s).'
                              'Radius is estimated from the region and FilRad*radius is the limit for outlier filtering.'))
    parser.add_argument('--ballrad1_factor',
                        type=float, default=1.1,
                        help=('Scale factor for BallRad1 = patchdiam1 * factor (default: %(default)s.)'
                              'BallRad1 is the ball size used for the first cover generation.'))
    parser.add_argument('--ballrad2_factor',
                        type=float, default=1.1,
                        help=('Scale factor for BallRad2 = patchdiam2max * factor (default: %(default)s). '
                              'BallRad2 is the maximum ball radius used for the second cover generation.'))
    parser.add_argument('--nmin1',
                        type=int, default=3,
                        help='Minimum number of points in BallRad1 balls (default: %(default)s).')
    parser.add_argument('--nmin2',
                        type=int, default=1,
                        help='Minimum number of points in BallRad2 balls (default: %(default)s).')
    parser.add_argument('--onlytree',
                        type=int, choices=[0,1], default=1,
                        help='If true then keep only tree points and the trunk base is defined as the lowest part of the point cloud (default: %(default)s).')
    parser.add_argument('--tria',
                        type=int, choices=[0,1], default=0,
                        help='If true then produce triangulation for the stem up to first branch (default: %(default)s).')
    parser.add_argument('--dist',
                        type=int, choices=[0,1], default=1,
                        help='If true then compute point-model distances (default: %(default)s).')
    parser.add_argument('--mincylrad',
                        type=float, default=0.0025,
                        help='Minimum cylinder radius used particularly in the taper corrections (default: %(default)s).')
    parser.add_argument('--parentcor',
                        type=int, choices=[0,1], default=1,
                        help='If true then assume child branch cylinder radii are always smaller than its parent branch (default: %(default)s).')
    parser.add_argument('--tapercor',
                        type=int, choices=[0,1], default=1,
                        help='If true then use partially linear (stem) and parabola (branches) taper corrections (default: %(default)s).')
    parser.add_argument('--growthvolcor',
                        type=int, choices=[0,1], default=0,
                        help='If true then use growth volume correction introduced by Jan Hackenberg (default: %(default)s).')
    parser.add_argument('--savemat', 
                        type=int, choices=[0,1], default=1,
                        help='If true then save the output struct QSM in .mat format (default: %(default)s).')
    parser.add_argument('--savetxt',
                        type=int, choices=[0,1], default=0,
                        help='If true then save the models in .txt files (default: %(default)s).')
    parser.add_argument('--plot',
                        type=int, choices=[0,1], default=0,
                        help='If true then plot the models, segmentation of the point cloud and distributions (default: %(default)s).')
    parser.add_argument('--disp',
                        type=int, choices=[0,1,2], default=2,
                        help=('Defines what is displayed during the reconstruction: '
                              '2 = display all; 1 = display name, parameters and distances; 0 = display only the name (default: %(default)s).'))
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Print outputs.')
    return parser.parse_args()


def collect_files(input_paths):
    files = []
    for path in input_paths:
        if os.path.isdir(path):
            # recursively collect all .ply files
            for root, _, fnames in os.walk(path):
                for fname in fnames:
                    if fname.lower().endswith('.ply') or fname.lower().endswith('.txt'):
                        files.append(os.path.join(root, fname))
        else:
            if os.path.isfile(path):
                files.append(path)
            else:
                # glob pattern fallback
                matched = glob.glob(path)
                files.extend(matched)
    if not files:
        raise FileNotFoundError("No point cloud files found for the given inputs.")
    return sorted(set(files))


def generate_inputs(flist, args):
    # Prepare directories
    parent_dir = os.path.dirname(args.output_path)
    results_dir = os.path.join(parent_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    for tree in flist:
        if not os.path.isfile(tree):
            raise FileNotFoundError(f"{tree} does not exist!")

        name = os.path.splitext(os.path.basename(tree))[0]
        ftype = os.path.splitext(tree)[1].lower().lstrip('.')

        subdir = os.path.join(args.output_path, name)
        os.makedirs(subdir, exist_ok=True)

        idx_counter = 0
        # Nested loops over user-defined candidates
        for pd1 in args.patchdiam1:
            for pd2min in args.patchdiam2min:
                for pd2max in args.patchdiam2max:
                    fn_index = idx_counter // args.n_models
                    ofn = os.path.join(subdir, f"{name}_{fn_index}.m")
                    with open(ofn, 'w') as fh:
                        # Header: add paths of source code
                        fh.write(f"addpath(genpath('{args.treeqsm_src}'));\n")
                        # fh.write(f"addpath('{args.optqsm_src}');\n")
                        # Inputs
                        fh.write(f"input.PatchDiam1 = {pd1};\n")
                        fh.write(f"input.PatchDiam2Min = {pd2min};\n")
                        fh.write(f"input.PatchDiam2Max = {pd2max};\n")
                        fh.write(f"input.lcyl = {args.lcyl};\n")
                        fh.write(f"input.FilRad = {args.filrad};\n")
                        # Ball radii
                        ball1 = round(pd1 * args.ballrad1_factor, 3)
                        ball2 = round(pd2max * args.ballrad2_factor, 3)
                        fh.write(f"input.BallRad1 = {ball1};\n")
                        fh.write(f"input.BallRad2 = {ball2};\n")
                        fh.write(f"input.nmin1 = {args.nmin1};\n")
                        fh.write(f"input.nmin2 = {args.nmin2};\n")
                        fh.write(f"input.OnlyTree = {args.onlytree};\n")
                        fh.write(f"input.Tria = {args.tria};\n")
                        fh.write(f"input.Dist = {args.dist};\n")
                        fh.write(f"input.MinCylRad = {args.mincylrad};\n")
                        fh.write(f"input.ParentCor = {args.parentcor};\n")
                        fh.write(f"input.TaperCor = {args.tapercor};\n")
                        fh.write(f"input.GrowthVolCor = {args.growthvolcor};\n")
                        fh.write(f"input.savemat = {args.savemat};\n")
                        fh.write(f"input.savetxt = {args.savetxt};\n")
                        fh.write(f"input.plot = {args.plot};\n")
                        fh.write(f"input.disp = {args.disp};\n")
                        # Unnecessary parameters for adjusted treeqsm()
                        fh.write("input.tree = 1;\n")
                        # fh.write("input.model = 1;\n")
                        

                        # Load or filter point cloud
                        if ftype == 'ply':
                            fh.write(f"cloud = read_ply('{os.path.abspath(tree)}');\n")
                            fh.write("if size(cloud, 2) == 4\n")
                            fh.write("\tidx = (cloud(:, 4) == 3);\n")
                            fh.write("\tcloud = cloud(idx, 1:3);\n")
                            fh.write("else\n")
                            fh.write("\tcloud = cloud(:, 1:3);\n")
                            fh.write("end\n")
                        elif ftype == 'txt':
                            fh.write(f"fn = '{os.path.abspath(tree)}';\n")
                            fh.write("data = dlmread(fn, ' ', 0, 0);\n")
                            fh.write("cloud = data(:, 1:3);\n")

                        # Iterate over models
                        fh.write(f"for i = {idx_counter}:{idx_counter + args.n_models - 1}\n")
                        fh.write("\tinput.model = i;\n")

                        # Save path for results
                        tree_res_dir = os.path.join(results_dir, name)
                        os.makedirs(tree_res_dir, exist_ok=True)
                        fh.write(
                            f"input.name = char(strcat('{tree_res_dir}/{name}-', num2str(i), '.mat'));\n"
                        )
                        fh.write("\ttry\n")
                        fh.write("\t\ttreeqsm(cloud, input);\n")
                        fh.write("\tcatch\n")
                        fh.write("\tend\n")
                        fh.write("end\n")
                        fh.write("exit;\n")

                    idx_counter += args.n_models
                    if args.verbose:
                        print(f"Generated: {ofn}")

if __name__ == '__main__':
    args = parse_args()
    args.output_path = os.path.abspath(os.path.expanduser(args.output_path))
    # collect input files flexibly
    flist = collect_files(args.inputs)
    print(f"Found {len(flist)} point cloud files.")
    print(f"Output directory: {args.output_path}")
    print(f"Using {len(args.patchdiam1)*len(args.patchdiam2min)*len(args.patchdiam2max)} parameter sets, {args.n_models} models each.")
    generate_inputs(flist, args)
