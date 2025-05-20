import os
import sys
import numpy as np
import argparse

def parse_args():
    
    parser = argparse.ArgumentParser(
        description='Generate input .m files for TreeQSM modelling with configurable parameters.'
    )
    parser.add_argument('-i', '--input',
                        type=str,
                        required=True,
                        help='Path to the input point cloud file (.ply or .txt).')
    parser.add_argument('-o', '--output',
                        type=str, default='./input.m',
                        help="Full path (directory and filename) for the generated TreeQSM input script (.m). If not provided, defaults to './input.m'")
    parser.add_argument('-rdir', '--results_dir',
                        type=str,
                        default=None,
                        help='Directory to store TreeQSM result files (.mat). Defaults to current directory.')
    
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_TREEQSM_SRC = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'src'))
    parser.add_argument('--treeqsm_src',
                        type=str, default=DEFAULT_TREEQSM_SRC,
                        help="Path to TreeQSM source code (default: '%(default)s').")
    parser.add_argument('--patchdiam1',
                        type=float, nargs='+',
                        default=[0.2],
                        help=('List of candidate values for PatchDiam1 (Patch size of the first uniform-size cover). ' 
                              f'Default: [0.2].'))
    parser.add_argument('--patchdiam2min',
                        type=float, nargs='+',
                        default=[0.05],
                        help=('List of candidate values for PatchDiam2Min (Minium patch size of the cover sets in the second cover). ' 
                              f'Default: [0.05].'))
    parser.add_argument('--patchdiam2max',
                        type=float, nargs='+',
                        default=[0.15],
                        help=("List of candidate values for PatchDiam2Max (Maximum cover set size in the stem's base in the second cover). " 
                              f'Default: [0.15].'))
    parser.add_argument('-n', '--n_models',
                        type=int, default=1,
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
                        action='store_true',
                        default=True,
                        help='If set, keep only tree points and the trunk base is defined as the lowest part of the point cloud (default: True).')
    parser.add_argument('--no-onlytree',
                        action='store_false',
                        dest='onlytree')
    parser.add_argument('--tria',
                        action='store_true',
                        default=False,
                        help='If set, produce triangulation for the stem up to first branch (default: False).')
    parser.add_argument('--dist',
                        action='store_true',
                        default=True,
                        help='If set, compute point-model distances (default: True).')
    parser.add_argument('--no-dist',
                        action='store_false',
                        dest='dist')
    parser.add_argument('--mincylrad',
                        type=float, default=0.0025,
                        help='Minimum cylinder radius used particularly in the taper corrections (default: %(default)s).')
    parser.add_argument('--parentcor',
                        action='store_true',
                        default=True,
                        help='If set, assume child branch cylinder radii are always smaller than its parent branch (default: True).')
    parser.add_argument('--no-parentcor',
                        action='store_false',
                        dest='parentcor')
    parser.add_argument('--tapercor',
                        action='store_true',
                        default=True,
                        help='If set, use partially linear (stem) and parabola (branches) taper corrections (default: True).')
    parser.add_argument('--no-tapercor',
                        action='store_false',
                        dest='tapercor')
    parser.add_argument('--growthvolcor',
                        action='store_true',
                        default=False,
                        help='If set, use growth volume correction introduced by Jan Hackenberg (default: False).')
    parser.add_argument('--savemat', 
                        action='store_true',
                        default=True,
                        help='If set, save the output struct QSM in .mat format (default: True).')
    parser.add_argument('--no-savemat',
                        action='store_false',
                        dest='savemat')
    parser.add_argument('--savetxt',
                        action='store_true',
                        default=False,
                        help='If set, save the models in .txt files (default: False).')
    parser.add_argument('--plot',
                        action='store_true',
                        default=False,
                        help='If set, plot the models, segmentation of the point cloud and distributions (default: False).')
    parser.add_argument('--disp',
                        type=int, choices=[0,1,2], default=1,
                        help=('Defines what is displayed during the reconstruction: '
                              '2 = display all; 1 = display name, parameters and distances; 0 = display only the name (default: %(default)s).'))

    return parser.parse_args()


def generate_inputs(cloud_file, args):
    results_dir = args.results_dir
    if results_dir is None:
        results_dir = os.path.abspath(os.getcwd())
    else:
        results_dir = os.path.abspath(os.path.expanduser(results_dir))
    os.makedirs(results_dir, exist_ok=True)

    if not os.path.isfile(cloud_file):
        raise FileNotFoundError(f"{cloud_file} does not exist!")

    name = os.path.splitext(os.path.basename(cloud_file))[0]
    ftype = os.path.splitext(cloud_file)[1].lower().lstrip('.')

    # Extract base of the output filename (excluding .m extension)
    output_dir = os.path.dirname(os.path.abspath(args.output))
    output_base = os.path.splitext(os.path.basename(args.output))[0]

    idx_counter = 1

    for pd1 in args.patchdiam1:
        for pd2min in args.patchdiam2min:
            for pd2max in args.patchdiam2max:
                ofn = os.path.join(output_dir, f"{output_base}_{idx_counter}.m")
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
                    fh.write(f"input.OnlyTree = {int(args.onlytree)};\n")
                    fh.write(f"input.Tria = {int(args.tria)};\n")
                    fh.write(f"input.Dist = {int(args.dist)};\n")
                    fh.write(f"input.MinCylRad = {args.mincylrad};\n")
                    fh.write(f"input.ParentCor = {int(args.parentcor)};\n")
                    fh.write(f"input.TaperCor = {int(args.tapercor)};\n")
                    fh.write(f"input.GrowthVolCor = {int(args.growthvolcor)};\n")
                    fh.write(f"input.savemat = {int(args.savemat)};\n")
                    fh.write(f"input.savetxt = {int(args.savetxt)};\n")
                    fh.write(f"input.plot = {int(args.plot)};\n")
                    fh.write(f"input.disp = {args.disp};\n")
                    
                    # Unnecessary parameters for adjusted treeqsm()
                    fh.write("input.tree = 1;\n")
                    # fh.write("input.model = 1;\n")
                    
                    # Load or filter point cloud
                    if ftype == 'ply':
                        fh.write(f"cloud = read_ply('{os.path.abspath(cloud_file)}');\n")
                        fh.write("if size(cloud, 2) == 4\n")
                        fh.write("\tidx = (cloud(:, 4) == 3);\n")
                        fh.write("\tcloud = cloud(idx, 1:3);\n")
                        fh.write("else\n")
                        fh.write("\tcloud = cloud(:, 1:3);\n")
                        fh.write("end\n")
                    elif ftype == 'txt':
                        fh.write(f"fn = '{os.path.abspath(cloud_file)}';\n")
                        fh.write("data = dlmread(fn, ' ', 0, 0);\n")
                        fh.write("cloud = data(:, 1:3);\n")

                    # Iterate over models
                    fh.write(f"for i = 0:{args.n_models - 1}\n")
                    fh.write(f"\tinput.model = i;\n")
                    fh.write(f"\tinput.name = char(strcat('{results_dir}/QSM-{name}-{idx_counter}-', num2str(i), '.mat'));\n")
                    fh.write("\ttry\n")
                    fh.write("\t\ttreeqsm(cloud, input);\n")
                    fh.write("\tcatch\n")
                    fh.write("\tend\n")
                    fh.write("end\n")
                    fh.write("exit;\n")

            idx_counter += 1           
            print(f"\t{ofn}")
        

if __name__ == '__main__':
    args = parse_args()
    args.input = os.path.abspath(os.path.expanduser(args.input))
    if args.results_dir is not None:
        args.results_dir = os.path.abspath(os.path.expanduser(args.results_dir))
    else:
        args.results_dir = os.path.abspath(os.getcwd())

    # Check output's parent directory
    output_dir = os.path.dirname(os.path.abspath(args.output))
    if not os.path.isdir(output_dir):
        print(f"\nError: path is not found:\n\t{output_dir}")
        print(f"Please create the directory or change the output path.")
        sys.exit(1)

    if not os.path.isfile(args.input):
        raise FileNotFoundError(f"Point cloud file '{args.input}' does not exist.")

    print(f"\nPoint cloud file: \n\t{args.input}")
    # print(f"Path to save generated TreeQSM input script(s): \n\t{output_dir}")
    # print(f"Path to save TreeQSM result files: \n\t{args.results_dir}")
    n_files = len(args.patchdiam1) * len(args.patchdiam2min) * len(args.patchdiam2max)
    print(f"\nGenerating {n_files} parameter set(s). For each set, {args.n_models} QSM(s) will be generated and saved in:\n\t{args.results_dir}")
    print(f"\nEach file below contains one parameter set:")
    
    generate_inputs(args.input, args)
