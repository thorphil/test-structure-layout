import gdstk
import numpy as np
import pandas as pd

#generate probe contact features

#Probecard parameters
rows = 2
cols = 4
pad_side = 100#micron
pad_sides = np.array([pad_side,pad_side])
pitch = 200#micron
gap = pitch-pad_side 
layer = 0#GDS layer to create the geometry on
name = 'probes_{cols}x{rows}_{pitch}um'.format(cols=cols,rows=rows,pitch=pitch)
origin = np.array((0,0))

# The GDSII file is called a library, which contains multiple cells.
lib = gdstk.Library()

# Geometry must be placed in cells.
cell = lib.new_cell(name)


# Calculate the dimensions of the structure
width = (pad_side+pitch)*(cols-1)
height = (pad_side+pitch)*(rows-1)

# Generate coordinates of each contact
cx = np.linspace(origin[0]-width/2.0,origin[0]+width/2.0,num=cols)#centre of each pad
cy = np.linspace(origin[1]-height/2.0,origin[1]+height/2.0,num=rows)#centre of each pad
cx,cy = np.meshgrid(cx,cy)
coords = np.column_stack([cx.flatten(),cy.flatten()])

# Create the geometry (a single rectangle) and add it to the cell.
for coord in coords:
    cell.add(gdstk.rectangle(coord-pad_sides/2.0,coord+pad_sides/2.0,layer=layer))

#write out file
lib.write_gds(name+'.gds')
