import gdstk
import numpy as np
import pandas as pd
import datetime

'''
This version uses polar magnitude only to decide if a structure's bounding box is within a wafer region.  Additional wafer features such as major and minor flats and notches are not taken into account.
'''

input_file = 'probes_4x2_240um.gds'
input_cell_name = 'probes_4x2_240um'
output_file = 'layout.gds'
output_coords = 'layout_coords.csv'
output_wafer = 100.0#mm
output_edge_exclusion = 1000.0
output_spacing = 500.0

include_timestamp = False

def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

if include_timestamp:
    t = timestamp()
    output_file = t + '-' + output_file 
    output_coords = t + '-' + output_coords


def _in_wafer(coords,radius,exclusion=0.0):
        radius -= exclusion
        for coord in coords:#for each coord of bounding box
            mag = np.sqrt(np.sum(coord**2)) 
            if mag>radius:
                return False
        return True

def populate(geometry,wafer=100.0,exclusion=0.0,spacing=0.0,vspacing=None,hspacing=None):
    #geometry is bbox [[x_min,y_min],[x_max,y_max]]
    wafer_diameter = wafer * 1000.0#db units microns
    if vspacing==None or hspacing==None:
        vspacing = spacing
        hspacing = spacing
    ll = np.array([geometry[0][0]-hspacing,geometry[0][1]-vspacing])
    lr = np.array([geometry[1][0]+hspacing,geometry[0][1]-vspacing])
    ul = np.array([geometry[0][0]-hspacing,geometry[1][1]+vspacing])
    ur = np.array([geometry[1][0]+hspacing,geometry[1][1]+vspacing])
    bbox_coords = np.row_stack([ll,lr,ul,ur])
    x_interval = (geometry[1][0]+hspacing)-(geometry[0][0]-hspacing)
    y_interval = (geometry[1][1]+vspacing)-(geometry[0][1]-vspacing)
    x = np.arange(-wafer_diameter/2.0,wafer_diameter/2.0,x_interval)
    y = np.arange(-wafer_diameter/2.0,wafer_diameter/2.0,y_interval)
    x,y = np.meshgrid(x,y)
    coords = np.column_stack([x.ravel(),y.ravel()])
    output = []
    for coord in coords:
        if _in_wafer(coord+bbox_coords,wafer_diameter/2.0,exclusion=exclusion):
            output.append(coord)
    return np.array(output)

input_lib = gdstk.read_gds(input_file)
input_cell = input_lib[input_cell_name]
output_lib = gdstk.Library()
top = output_lib.new_cell('Top')
output_lib.add(input_cell)
coords = populate(input_cell.bounding_box(),wafer=output_wafer,exclusion=output_edge_exclusion,spacing=output_spacing)
for coord in coords:
    top.add(gdstk.Reference(input_cell,origin=coord))

#write out files
output_lib.write_gds(output_file)
np.savetxt(output_coords,coords,delimiter=',',header='x,y')
