import argparse
import os
import pandas as pd
import numpy as np
import sys
from glob import glob

def get_ply_files(input_path):
    if os.path.isdir(input_path):
        return glob(os.path.join(input_path, '*.ply'))
    elif os.path.isfile(input_path) and input_path.endswith('.ply'):
        return [input_path]
    else:
        raise ValueError("Input must be a .ply file or a directory containing .ply files")

def open_ply(fp, newline=None):

    if (sys.version_info > (3, 0)):
        return open(fp, encoding='ISO-8859-1', newline=newline)
    else:
        return open(fp)

def read_ply(fp):

    line = open_ply(fp).readline()
    newline = '\n' if line == 'ply\n' else None

    return read_ply_(fp, newline)
    
def read_ply_(fp, newline):

    with open_ply(fp, newline=newline) as ply:
 
        length = 0
        prop = []
        dtype_map = {'uint16':'uint16', 'uint8':'uint8', 'double':'d', 'float64':'f8', 
                     'float32':'f4', 'float': 'f4', 'uchar': 'B', 'int':'i'}
        dtype = []
        fmt = 'binary'

        for i, line in enumerate(ply.readlines()):
            length += len(line)
            if i == 1:
                if 'ascii' in line:
                    fmt = 'ascii' 
            if 'element vertex' in line: N = int(line.split()[2])
            if 'property' in line: 
                dtype.append(dtype_map[line.split()[1]])
                prop.append(line.split()[2])
            if 'element face' in line:
                raise Exception('.ply appears to be a mesh')
            if 'end_header' in line: break
    
        ply.seek(length)

        if fmt == 'binary':
            arr = np.fromfile(ply, dtype=','.join(dtype))
        else:
            arr = np.loadtxt(ply)
        df = pd.DataFrame(data=arr)
        df.columns = prop

    return df

def write_ply(output_name, pc, comments=[]):

    cols = ['x', 'y', 'z']
    pc[['x', 'y', 'z']] = pc[['x', 'y', 'z']].astype('f8')

    with open(output_name, 'w') as ply:

        ply.write("ply\n")
        ply.write('format binary_little_endian 1.0\n')
        ply.write("comment Author: Phil Wilkes\n")
        for comment in comments:
            ply.write("comment {}\n".format(comment))
        ply.write("obj_info generated with pcd2ply.py\n")
        ply.write("element vertex {}\n".format(len(pc)))
        ply.write("property float64 x\n")
        ply.write("property float64 y\n")
        ply.write("property float64 z\n")
        if 'red' in pc.columns:
            cols += ['red', 'green', 'blue']
            pc[['red', 'green', 'blue']] = pc[['red', 'green', 'blue']].astype('i')
            ply.write("property int red\n")
            ply.write("property int green\n")
            ply.write("property int blue\n")
        for col in pc.columns:
            if col in cols: continue
            try:
                pc[col] = pc[col].astype('f8')
                ply.write("property float64 {}\n".format(col))
                cols += [col]
            except:
                pass
        ply.write("end_header\n")

    with open(output_name, 'ab') as ply:
        ply.write(pc[cols].to_records(index=False).tobytes()) 


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
        print(f"Converting {f}")
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
        print(f"Saved to {os.path.join(output_dir, out_fn)}")
