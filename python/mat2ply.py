#!/usr/bin/env python

import sys
import os
import argparse
import numpy as np

from cyl2ply import pandas2ply
from mat2qsm import QSM

parser = argparse.ArgumentParser(description='Convert .mat files to .ply format.')
parser.add_argument('-i', '--input_mat_files', nargs='+', required=True, help='One or multiple .mat files to process')
parser.add_argument('-odir', '--outdir', default=os.getcwd(), help='Directory to store output .ply file(s). Default: current working directory.')
args = parser.parse_args()

for mat in args.input_mat_files:

    print('processing:', mat)
   
    try: 
        qsm = QSM(mat)
        
        out_ply = os.path.join(args.outdir, os.path.basename(mat).replace('.mat', '.ply'))
        pandas2ply(qsm.cyl2pd()[['length', 'radius', 'sx', 'sy', 'sz', 'ax', 'ay', 'az', 'branch']], 
                   'branch', 
                   out_ply) 
        
        if qsm.Tria == 1:
            
            threes = np.ones((len(qsm.tri_facet), 1)) + 2
            facets = np.hstack([threes, qsm.tri_facet])
            
            out_tri_ply = os.path.join(args.outdir, os.path.basename(mat).replace('.mat', '_tri.ply'))
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
