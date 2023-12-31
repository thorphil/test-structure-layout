# Test structure layout
These scripts can be used to generate a probecard contact pattern and layout over a wafer for automated testing.

The main use is to distribute completed structures over a wafer layout and capture their locations in file that can be supplied to an automated tester or other metrology tool.

## Example workflow:

- Run _generate_probe_contacts.py_ to generate a contact array.
- Modify the generated GDS file to add the remaining test structure design.
- Run _generate_layout.py_ to generate a design and a csv file with structure locations.
- Alternatively, run _extract_coords.py_ to extract structure locations by directly parsing a GDS layout file. 

The scripts can be configured by adjusting the internal variables as appropriate.


### Generate a 4 by 2 array with 120$`\mu`$m contacts on a 240$`\mu`$m pitch:
![](/img/resize_probes_4x2_480um.png)

### Add a design in an external editor:
![](/img/resize_teststructure.png)

### Generate the layout:
![](/img/resize_layout_zoom.png)

![](/img/resize_layout.png)

### Collect the coordinate file for metrology:

***x,y***

-1.262500000000000000e+02,-4.779000000000000000e+04

-1.186125000000000000e+04,-4.558000000000000000e+04

-8.927500000000000000e+03,-4.558000000000000000e+04

-5.993750000000000000e+03,-4.558000000000000000e+04

-3.060000000000000000e+03,-4.558000000000000000e+04

-1.262500000000000000e+02,-4.558000000000000000e+04

2.807500000000000000e+03,-4.558000000000000000e+04

5.741250000000000000e+03,-4.558000000000000000e+04

8.675000000000000000e+03,-4.558000000000000000e+04

...

## Requirements:
- [gdstk](https://github.com/heitzmann/gdstk)
- [NumPy](https://numpy.org)
