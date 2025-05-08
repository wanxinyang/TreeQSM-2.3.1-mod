import argparse
import os
from glob import glob
from ply_io import read_ply, write_ply

def get_ply_files(input_path):
    if os.path.isdir(input_path):
        return glob(os.path.join(input_path, '*.ply'))
    elif os.path.isfile(input_path) and input_path.endswith('.ply'):
        return [input_path]
    else:
        raise ValueError("Input must be a .ply file or a directory containing .ply files")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert the datatype from double to float64 in PLY file(s)')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to a .ply file or a directory containing .ply files')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Directory to save converted PLY file(s); default is a 'float64/' dir alongside input")
    parser.add_argument('--suffix', type=str, default='_float64',
                        help="Suffix to add before .ply in output filenames, use 'none' to disable suffix")
    args = parser.parse_args()

    input_abs = os.path.abspath(args.input)
    input_base_dir = input_abs if os.path.isdir(input_abs) else os.path.dirname(input_abs)
    output_dir = args.output if args.output else os.path.join(input_base_dir, 'float64')

    ply_files = get_ply_files(args.input)
    os.makedirs(output_dir, exist_ok=True)

    for f in ply_files:
        print(f)
        # filename
        fn = os.path.basename(f)
        name, ext = os.path.splitext(fn)

        # read the ply file
        df = read_ply(f)

        # construct output filename
        if args.suffix.lower() != 'none':
            out_fn = f"{name}{args.suffix}.ply"
        else:
            out_fn = fn

        # write the ply file
        write_ply(os.path.join(output_dir, out_fn), df)
