# Test structure layout
Simple scripts to generate a probecard contact pattern and layout over a wafer for automated testing.

The main use is to distribute completed structures over a wafer layout and capture their locations in file that can be supplied to an automated tester.

## Example workflow:

- Run _generate_probe_contacts.py_ to generate a contact array.
- Modify the generated GDS file to add the remaining test structure design.
- Run _generate_layout.py_ to generate a design and a csv file with structure locations.

The scripts can be configured by adjusting the internal variables as appropriate.

## Requirements:
- [gdstk](https://github.com/heitzmann/gdstk)
- [NumPy](https://numpy.org)


!(/img/layout.png)
!(/img/layout_zoom.png)
!(/img/probes_4x2_480um.png)
!(/img/teststructure.png)
