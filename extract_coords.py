import numpy as np
import gdstk

input_file = 'layout.gds'
input_cell = 'probes_4x2_240um'
output_file = 'layout_coords_extracted.csv'
lib = gdstk.read_gds(input_file)
top = lib.top_level()
cell = top[0]
refs = cell.references
coords = np.array([ref.origin for ref in refs])
np.savetxt(output_file,coords,delimiter=',',header='x,y')
print('extracted {} coordinates'.format(coords.shape[0]))
