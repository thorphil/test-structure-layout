# Test structure layout
Simple scripts to generate a probecard contact pattern and layout over a wafer for automated testing.

The main use is to distribute completed structures over a wafer layout and capture their locations in file that can be supplied to an automated tester.

Example workflow:

- Run _generate_probe_cell.py_ to generate a contact array.
- modify the generated GDS file to add rest of the test structure design.
- Run _generate_layout.py_ to generate a design and a csv file with structure locations.

Both scripts can be configured by adjusting the internal variables as appropriate.

required Python libraries:
- numpy
- gdstk
