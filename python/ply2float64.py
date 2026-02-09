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
                     'float32':'f4', 'float': 'f4', 'uchar': 'B', 'int':'i', 'int32':'i'}
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
                        help='Path to a .ply file')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Path to save converted PLY file; default is current directory with suffix '_float64.ply'")
    args = parser.parse_args()

    if not args.input.lower().endswith('.ply'):
        raise ValueError("The input file must be a .ply file")

    if args.output:
        output_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    else:
        name, ext = os.path.splitext(os.path.basename(args.input))
        output_path = os.path.join(os.getcwd(), f"{name}_float64.ply")

    df = read_ply(args.input)
    print(f"\nConverting: \n{os.path.abspath(args.input)}\n")
    write_ply(output_path, df)
    print(f"Saved to: \n{output_path}\n")
