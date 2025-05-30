#!/usr/bin/env python

import sys
import os
import argparse
import numpy as np

from cyl2ply import pandas2ply
from mat2qsm import QSM

parser = argparse.ArgumentParser(description='Convert .mat files to .ply format.')
parser.add_argument('-i', '--input_mat_files', nargs='+', required=True, 
                    help='One or multiple .mat files to process')
parser.add_argument('-o', '--output', default=None, 
                    help=(
                        'Output directory or full path output filename. ' 
                        'If a dir is given, output will have the same filename as input with .ply extension. '
                        'If a filename is given, it will be used directly. '
                        'Default: current directory with same filename.'))
args = parser.parse_args()

for mat in args.input_mat_files:

    print('processing:', mat)

    try: 
        qsm = QSM(mat)
        
        input_filename = os.path.basename(mat)
        default_outdir = os.getcwd()
        default_basename = os.path.splitext(input_filename)[0] + '.ply'

        if args.output is None:
            out_ply = os.path.join(default_outdir, default_basename)
        # If -o is a directory, use the default basename
        elif os.path.isdir(args.output):
            out_ply = os.path.join(args.output, default_basename)
        # If -o is a file, use it as output filename
        else:
            out_ply = args.output

        pandas2ply(qsm.cyl2pd()[['length', 'radius', 'sx', 'sy', 'sz', 'ax', 'ay', 'az', 'branch']], 
                   'branch', 
                   out_ply) 
        
        if qsm.Tria == 1:
            
            threes = np.ones((len(qsm.tri_facet), 1)) + 2
            facets = np.hstack([threes, qsm.tri_facet])
            
            if args.output is None:
                out_tri_ply = os.path.join(default_outdir, os.path.splitext(input_filename)[0] + '_tri.ply')
            elif os.path.isdir(args.output):
                out_tri_ply = os.path.join(args.output, os.path.splitext(input_filename)[0] + '_tri.ply')
            else:
                base, ext = os.path.splitext(args.output)
                out_tri_ply = base + '_tri.ply'
            with open(out_tri_ply, 'w') as ply:
                
                ply.write("ply\n")
                ply.write("format ascii 1.0\n")
                ply.write("comment Author: Phil Wilkes\n")
                ply.write("obj_info Generated using Python\n")
                ply.write("element vertex {}\n".format(len(qsm.tri_vert)))
                ply.write("property float x\n")
                ply.write("property float y\n")
                ply.write("property float z\n")
                ply.write("element face {}\n".format(len(facets)))
                ply.write("property list uchar int vertex_indices\n")
                ply.write("end_header\n")
                
                np.savetxt(ply, qsm.tri_vert, fmt='%.3f')
                np.savetxt(ply, facets, fmt='%.i')

    except Exception as err:
        print(err)
