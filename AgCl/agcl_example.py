#!/usr/bin/python
'''

# Automatic prober example script

*Paul Sullivan*, October 2021.

* * * * *

This Script is an example automation structures measurement on wafer or chip level.  It was written in Python 3 for measuring four different test structures,
 fabricated using different materials and hierarchically laid out on a wafer.
The Structures were designed by Jamie Marland as part of the IMPACT project.
The chip and test structures are detailed in a paper presented at ICMTS 2019:

*C. Dunare et al.*, **"Test Structures for Characterising the Silver Chlorination Process During Integrated Ag/AgCl Reference Electrode Fabrication,"**
 ICMTS, 2019, pp. 58-63.

The script makes use of the *Pyvisa* library for communication with the instruments and the *Numpy* and *Pandas* libraries for data manipulation.

The code is run by navigating to the directory where the file is stored and executing:

~~~~~
python agcl_example.py
~~~~~

or:

~~~~~
./agcl_example.py -h
~~~~~

to get usage information.

This document has been written with the intention of providing a starting point for the development of new structure layouts and to provide information necessary for maintenance and future development of the system.
It is written to act as functional code but also using *Pandoc* markdown and so may be directly compiled to pdf:

~~~~~~
pandoc -f markdown --toc -o README.pdf agcl_example.py
~~~~~~



## Power up system

1. Green button on HP 4062 rack
2. Green button on PA200 power supply (under Prober)
3. Microscope light and intensity control
4. Turn on the ATT temperature controlled vacuum chuck (default: 25C)
5. Camera connect USB cable to USB-3.0 port on a computer with camera software installed (see below)
6. Login to control PC

## Control PC

~~~~
Username: probebench
Password: probebench

Root: automat10n
~~~~

Make a directory for your work and copy this file along with *probebench.py* and the file containing the structure coordinates into it.

~~~~
mkdir My_directory
~~~~

For editing the code, configuration files, the coordinate file or to view results files, use the installed *Atom* text editor.

## Communication:

On startup or after altering the configuration run *gpib_config* as root
to reload the configuration file:

~~~~
sudo gpib_config
password: User password
gpib_config
~~~~

or alternatively:

~~~~
su
Root password
cd /etc
./gpib_config
<Ctrl D> (logout)
~~~~

Communication details are set using the configuration file: **/etc/gpib.conf**, on a per device basis.
A device refers to connected instrument and an interface to the pci-gpib board used to communicate across the bus to the instruments.


Communication with instruments is currently via a single GPIB interface card, one of two installed in the PC.
The instruments are daisy chained an messages are sent and received from each instrument via the Python PyVISA library,
which is configured to use the Linux-GPIB backend.
An alternative backend is available from National Instruments, but is not installed or configured.

### Primary GPIB bus addresses

To connect to an instrument it's primary address on the bus is required.  To confirm the addresses of connected devices run scripts/lr.py (list resources) script:

**Address**      **Instrument**
----------- -------------------
01          Probebench  (PA200)
12                    3458A DMM
16                    ATT Chuck
22          4084B Switch Matrix
23                    4142B SMU
-------------------------------

Most of the instruments have commands to re-configure the primary address which could be used to prevent collisions with additional instruments on the bus.

## Probebench

There are currently timing issues in read and write from the probebench, if
communication commands are sent faster than the ability of the tool to
respond, then it will crash. If this occurs the tool/interface must be
reset. The easiest way to achieve this is to power cycle the tool, there may be gpib based techniques of resetting and clearing the interface, however these are undeveloped.

### Stage motion
There are several motion strategies available, these are detailed in the PA200 documentation.
The first and least useful is the absolute position of the stage as measured by the positioning sensors, this will likely bear no resemblance to the sample structures.
There is also a relative motion command that moves the stage relative to it's current position.
Finally, the way the movement code is currently setup is to use the **SET HOME** function.
This sets a local origin at the current stage position and all supplied translation command coordinates are subsequently assumed to be relative to this point.
By default the system will use the first coordinate supplied by the file and so this structure must first be found on the sample and set as **HOME** using the manual control before starting any measurements.
This behaviour can be overridden by supplying the row index in the coordinate list of the new **HOME** structure or other recognisable point on the sample.

### Probecard

Probe layout: (240um pitch) Pad size - 120x120um:

* Numbered connections go to top-side contacts
* Lettered connections to to bot-side contacts

The diagram below shows the connection matrix pin number associated with each contact and the the logical naming convention that has been adopted in the code.
The diagram below shows two versions a contact layout for the probecard that has been used up until now.
This convention follows from subscript notation commonly used in the derivation of sheet resistance.

~~~~



             17  14  11  8      A   B   H   F
              _   _   _   _     _   _   _   _
             |_| |_| |_| |_|   |_| |_| |_| |_|  _
             <->    <-->                        |
             120um  240um                       | 120um
              _   _   _   _     _   _   _   _   _
             |_| |_| |_| |_|   |_| |_| |_| |_|

             20  23   2   5     D   C   G   E
~~~~

It is difficult to trace the pins into the probecard backplane connector,
so it is assumed that matrix pins go to identically numbered probecard contacts.

### Manual controller

Manual stage control and computer control commands to the stage are not exclusive.
On the Control box press ALT twice then press F1 "Remote" to start remote mode.
This locks out the control box until F1 "Local" is pressed and should be used to prevent triggering inadvertent stage motion, while the system is simultaneously under computer control.

The control box with the joystick has a menu  (F1, F2, F3) which is stepped through using the ALT button.  The ALT button has two lights which indicates which of the four menu selections has been selected.

**ALT Right** **ALT left**        **F1**   **F2**   **F3**
------------- ------------ ------------- -------- --------
Off		      Off		   ALIGN		 GO HOME  SET HOME
Off		      On		   SET CONT	     Z UP     Z DOWN
On		      Off		   REMOTE		 THETA    INDEX
On		      On		   IDX POS		 REAL POS QUIET
----------------------------------------------------------

**Function**   **Description**
-------------- ---------------------------------------------------------
ALIGN          Uses to horizontal reference locations to set stage theta
GO HOME        Moves the stage to the home position
SET HOME       Sets the current stage position as HOME
SET CONT       Sets the current stage z as contact
Z UP           Moves the stage up towards the probes
Z DOWN         Moves the stage down away from the probes
REMOTE         Locks out the control box, press local to reactivate
THETA          Manually adjust the stage theta travel (+/-15 degrees)
INDEX          N/A
IDX POS        N/A
REAL POS       N/A
QUIET          N/A


## Switching Matrix

The switching matrix allows dynamic connection from the instruments to the probe card.  The instruments connect to ports
and the pins are connected to the probecard.  Ports can connect to multiple pins simultaneously, however, each pin can only connect to one port.
The 4084B and 4085B system has 8 ports capable of connecting to 48 pins.

The switching matrix should be regularly exercised to keep the relay contacts clean, a protocol is available in the manual.

### Relay test

A diagnostic is available for the switching matrix, requiring connection of 16075A relay
test adapter.  A script is available in *scripts/* that will send a command to the connection matrix and prints the result.
If a defective relay board is discovered the identity of the board will be returned and the test aborted. This means that only a single defective board can be found at each time the test is run.
A salvage repair procedure is discussed in the manual, several defective boards have been found to date. The strategy has been to mark them and translocate above the highest numbered relay used (23), allowing validation that all relays boards used for the measurements are functional.

**Port** **Instrument**
-------- --------------------------
1         4142B Ch-1 40uV-100V 100mA
2         4142B Ch-3 40uV-200V 1A
3         4142B Ch-4 40uV-100V 100mA
4         4142B Ch-5 40uV-100V 100mA
5         4142B Ch-6 +/- 40V
7         4142B GND
8(vm1)    3458A high
9(vm2)    3458A low
-------------------------------------

### Force, Sense, Guard:
Sense is not used and is tied to Force in relay ports 2,3,4.  Sense is open in Port 1

## Camera

The camera requires a USB-3.0 interface.  The control PC does not currently have one so an external laptop should be used.
The required software is named "Touplite" and can be downloaded for the manufacturer's website.

**Note**: The microscope camera mount and eyepiece have slightly different focal planes, both cannot be in focus simultaneously.
It is suggested to get set up a measurement run with the eyepiece first, then focus the camera.

## Resources

### Manuals

There are several pdf manuals in the document directory that may need to be consulted in order to implement alternate measurement setups:

* Suss PA 200 User Manual (Paper copy also available)
* Suss short user manual
* 3458A Multimeter
* 4085M Switching matrix Manual
* 4085M GPIB reference
* ATT temperature controlled chuck manual
* 4142 SMU manual
* 4142 SMU GPIB reference

### Software and Documentation

* **<https://pandoc.org/>**
* **<https://linux-gpib.sourceforge.io/>**
* **<https://pyvisa.readthedocs.io/en/latest/>**
* **<http://touptek.com/download/>**
* **<http://numpy.org>**
* **<https://pandas.pydata.org>**

## General advice on creating new layouts

The first task is to decide on a probecard to use, this selection depends on what cards are available and also on the number of connections required to complete the measurements of the structure.
Probe cards have two main features: the number and arrangment of probe needles, usually given as rows, columns and The pitch or spacing between adjacent probe needles.
Contact pads are then designed in a pattern around the probe positions. The larger the contact pad the greater the tolerance for translational and rotational misalignment when probing.

Structures may be placed freely on a layout, there is no requirement to place structures on a regular grid in order to perform automated measurement.  As the stage has only limited theta travel the structures all need to be oriented the same way.
To capture the coordinates of the structures, the absolute coordinates in the layout are used. Units should be in microns as this is what the probestation stage commands use.
However the choice of the origin, however is completely arbritary.
If capturing froma GDSII file it would be easiest to use the inbuilt coordinates of the viewer software.
It is assumed they are cartesian: x(left to right) y(bottom to top).
For each structure a single point is needed. This can be selected anywhere on the structure but must be consistent across all structures on the layout.
A good choice is the lower left corner of the lower left contact pad.
The x and y coordinates of a structure should be written into separate column fields of a *.csv* file with each structure occupying a row.
Additional data about each structure required to configure measurements or needed for the analysis should also be included.
This list can be assembled manually or the GDSII file can be parsed to extract the coordinates where the appropriate geometry can be easily identified (consistently named cells).
If the layout itself is being programmatically generated or the structures are being injected into the layout then the coordinates are best captured at this stage.

Once a coordinate file has been obtained and the sample, fabricated, there are several options for setting up the automated probing. Currently, a single easily found structure is identified on the wafer, the probes are positined over this structure and it is set as **HOME**.
The absolute coordinates of the other structures are then transformed to relative coordinates with reference to this structure.

As a final note, the x and y values of the user supplied coordinates are negated before being used to move the stage.  The reason for this is that the stage moves the sample and not the turret (camera and probes).
As a result, from the frame of reference of the camera (and the supplied coordinates), the stage motions are reversed.
The way the camera is physically oriented on the turret interacts with the image formed on the sensor (flipped due to the optics) means that the image should flipped horizontally inside the software before viewing.

## AgCl structures

The coordinate file for the structure was created by examining the GDSII layout file: *AgAgCl_TS_Kelvin_R2_00_03.csv*

The start point  (**HOME**) for the AgCl structure is lower-left (LL) coordinate of contact D of the Pt LW300 structure on block 1. On the AgCl chips this is the top left structure of the top left block.
structure in the top LHS chip.  The origin for the coordinates on each chip is the LL corner of the LL structure of the LL block on each die/chip.
Practically, this means correctly aligning the probes over the contacts of the first structure on a theta aligned wafer is sufficient to guarantee electrical connection with all test structures.
Configurations of the matrix are supplied for each individual measurement of the device via callback functions that return a measurement name that is stored as a field in the output data.

### Measurement configuration
The script allows configuration of measurement parameters for each structure.  This includes number of measurements, how each probe is connected to the instruments and the driving currents for each type of structure and material.
For each structure these parameters are captured along with a single sampled measurement and a calculated resistance.

Usually all structures on the sample will be measured in one session, but filtering out subsets and control of the sequence the structures are measured in is possible.
This can easily be achieved via the software but the coordinates file can also be rearranged to produce the same effect.  Some examples of filter-strings and their function:

Measure only platinum structures:

\small
~~~~
--filter-string='material=="Pt"'
~~~~
\normalsize

Measure only blocks 3,6 and 10:

\small
~~~~
--filter-string='block in [3,6,10]'
~~~~
\normalsize

Measure LW300 and LW600 structures on all materials in block 4 and only the AgCl material on other blocks:

\small
~~~~
--filter-string='structure in ["LW300", "LW600"] and (block==4 or material=="Ag_Cl")'
~~~~
\normalsize

The supplied string is passed to the *Pandas* DataFrame.query function.  The Pandas documentation should be consulted for more involved filtering requirements.

## Setting up a measurement run

1. Power up the instruments (recommended 30 minutes prior to high precision measurements).
2. Connect camera USB to a laptop
3. Start the *Touplite* software
4. Tick the horizontal flip checkbox in camera options. Framerate can be increased by lowering the Live resolution
5. Ensure microscope light source is on and adjust the brightness.
6. Change to **LOCAL** mode on the remote
7. Raise the turret on the probebench - toggle switch on right side of microscope
8. Select appropriate microscope objective
9. Insert the probecard and tighten retention screws
10. Press **LOAD** on the control box
11. Ensure **VACUUM** is off
12. Manually centre the chuck **THETA** in its travel (the chuck has a limited motorised adjustment +/- 15 degrees)
13. Place sample on the chuck centred and press **VACUUM** to toggle vacuum on
14. Lower turret
15. Select a **SPEED 4** and move stage to bring sample under objective
16. Bring the probes into focus using the eyepiece
17. Ensure the camera image is square to the probes and that the probes are centred in the image, adjust only if required.
18. Ensure the probe rows are aligned with the x motion of the stage adjust as necessary (PA200 manual section 3 p12 for alignment procedure)
19. Bring the substrate into focus
20. Use "ALIGN" and two distant reference points/structures that share a y coordinate to theta align the sample.
21. Find and move the probes over the first structure (top left corner structure of the top left block)
22. Bring the probe tips back into focus
23. Select **SPEED 2** or **SPEED 3** and navigate to the **Z UP/DOWN** menu and carefully bring the stage up until all the probes make contact
24. Take care to ensure no probes ever hang over the substrate - if the probes are down an the home button is pressed the probes might catch the substrate edge and be damaged.
25. Press **SET CONT** to set this position of the stage z as contact. **ALIGN** and **SEPARATE** z values are automatically set
26. Press **SET HOME** to set this as the position of the first structure. Accuracy is important as motions to other structures are calculated from this point
27. Press **SEPARATE** the structure should go out of focus again
28. Bring the probes into focus on the camera
29. Navigate the menu and select **REMOTE** to lock out the control box
30. On the computer navigate to the directory for the session
31. Open the script in an editor (*Atom*)
32. Open a terminal on the computer and navigate to the directory for the session
33. Run the script as a dry run:

~~~~~
    ./agcl_example.py --dry-run
~~~~~

34. Confirm correct stage motion and alignment of the probes with the structures
35. Re-run the script to perform the measurements, replacing the wafer and die values:

~~~~~
    ./agcl_example.py --measure --wafer=1 --die=1
~~~~~

36. Results files default to a automatically named file to prevent clobbering previous data, see options to alter this behaviour.




## Code
\scriptsize
~~~~{.python}
#'''
import sys
import os
import getopt
import pyvisa
import numpy
import pandas
import pandas as pd
import time
import datetime
from probebench import Probebench

#default states
dry_run = True#prevent contacting
wafer = None
die = None
overwrite=False
append=False
output_file=None
coordinates=None
coordinate_file = '/home/probebench/20200907-Ag_AgCl_TS/AgAgCl_TS_Kelvin_R2_00_03.csv'#hard coded coordinate file
home_index=0 #set home above the 0th item in the subset, change this if using a subset
start_index=0#ignore structures before this index
filter_string = 'structure == "LW300" and material == "Pt"'#first structure in each block
filter_string_reset = False
filter_structures = False # set to true to generate a subset of structures

usage='''
Probestation automation script\n
[-h --help]
       Print help message and exit\n
[-d --dry-run]
       visit structures without dropping probes, perform electrical measurements but not save (junk) data\n
[-m --measure]
       Perform measurements, probe contacting enabled and data saved to output file\n
[-w --wafer=]
       wafer number, required for measuements\n
[-d --die=]
       die/chip number, required for measurements\n
[-c --coordinates=]
       path to CSV file containing structure coordinates and parameters\n       default hard-coded in coordinate_file variable\n
[-o --output=]
       path to file to write the output data to, if unsupplied a timestamped file is produced\n
[--output-append]
       append data to the file rather than overwrite\n
[--output-overwrite]
       overwrite the supplied output file\n
[--filter]
       filters the coordinates using the "filter_string" option, defaults first structure of each block\n
[--filter-string]
       query to produce a subset of structures. see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html\n
[--home]
       the index of the structure that is set as HOME; default 0\n
[--offset]
       the index of the structure to start measuring from; default 0\n

Examples:

Check the wafer and tool has been setup correctly:

./measure.py --dry-run

Check the first structure of each block

./measure.py --dry-run --filter

Perform measurements on die 1 of wafer 1; save data to auto-generated file:

./measure.py --measure --wafer=1 --die=1

Restart a measurement run after abort, starting at structure 10 and appending to an existing file:

./measure.py -m -w1 -d1 --offset=10 --output data.csv --output-append

Perform measurement over a filtered subsets of platinum structures only:

./measure.py -m -w1 -d1 --filter --filter-string="material == 'Pt'"
'''

#Command line options
opts,args = getopt.getopt(sys.argv[1:],'ho:w:d:m',['measure','dry-run','wafer=','die=','coordinates=','output=','output-overwrite','output-append','help','filter','home=','offset=','filter-string='])
if opts == []:
    print(usage)
    exit()
for o,a in opts:
    if o=='-h' or o=='--help':
        print(usage)
        exit()
    if o=='--measure' or o=='-m':
        dry_run=False#diable contacting disable measurement
    if o=='--dry-run':
        dry_run=True
    if o=='--wafer' or o=='-w':
        try:
            wafer = int(a)
            print('WAFER set as {}'.format(int(a)))
        except:
            print('ERROR: WAFER={} value must be an integer'.format(a))
            exit()
        #isinstance int
    if o=='--die' or o=='-d':
        try:
            die = int(a)
            print('DIE set as {}'.format(int(a)))
        except:
            print('ERROR: DIE={} value must be an integer'.format(a))
            exit()
    if o=='--filter':
        filter_structures = True
    if o=='--coordinates':
        if os.path.isfile(a):
            coordinate_file=a
        else:
            print('ERROR: coordinate file {} not found'.format(a))
    if o=='--output-overwrite':
        overwrite=True
    if o=='--output-append':
        append=True
    if o=='--filter':
        filter_structure=True
    if o=='--output-file' or o=='-o':
        output_file = a
    if o=='--home':
        try:
            home_index = int(a)
            print('HOME assumed to be structure: {}'.format(int(a)))
        except:
            print('ERROR: home-index value must be an integer'.format(a))
            exit()
    if o=='--filter-string':
        filter_string=a
        filter_string_reset=True
    if o=='--offset':
        try:
            start_index = int(a)
            print('measurements will start from structure: {}'.format(int(a)))
        except:
            print('offset value must be an integer'.format(a))
            exit()


if not dry_run and (wafer is None or die is None):
    print('ERROR: WAFER and DIE both need to be set for measurement run')
    exit()


if overwrite and append:
    print('ERROR: pass either --output-overwrite or --output-append')
    exit()


def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

output_open_mode = 'w' if overwrite and not append else 'a'

if output_file is None:
    output_file = '{}_wafer{}_die{}.csv'.format(timestamp(),wafer,die)
    output_open_mode = 'w'


if os.path.isfile(output_file) and not overwrite and not append:
    print('ERROR: output file {} already exists. Use --overwrite or --append to replace or add to this file'.format(output_file))
    exit()

if not dry_run:
    results = open(output_file,mode=output_open_mode) # open file to store results

if dry_run:
    print('INFO: dry run mode, probe contacting is disabled')
    time.sleep(1)
else:
    print('WARNING: probe contacting is enabled!\n<ctrl>+c to abort.')
    time.sleep(4)

df = pd.read_csv('coords.csv')
if filter_string_reset and not filter_structures:
    print('ERROR: filter option must be used when setting filter-string')
    exit()
try:
    subset = df.query(filter_string)#apply filter string
except:
    print('ERROR: malformed filter query')
    exit()
if subset.empty:
    print('ERROR: filter query did not match any structures')
    exit()



rm = pyvisa.ResourceManager() # create the resource manager osbject
pb = Probebench(rm) # create a probebench object

 # initialise Matrix
matrix = rm.open_resource('GPIB0::22::INSTR')
matrix.write_termination = '\n' # taken from manual could also use "EX"

 # initialise SMU
smu = rm.open_resource('GPIB0::23::INSTR')
smu.read_termination = "\r\n"
smu.write_termination = '\r\n' # taken from manual could also use "EX"

 # initialise DMM
dmm = rm.open_resource('GPIB0::12::INSTR')
dmm.read_termination = "\r\n"
dmm.write_termination = '\r\n' # taken from manual could also use "EX"

 # configure dmm
dmm.write("PRESET NORM") # trying to stop any subprograms that are sending voltages
dmm.write("TRIG HOLD")# Disable readings
dmm.write("DCV 10") # 100nV resolution DCV 1 10nv resolution
dmm.write("NPLC 1")
dmm.write("TRIG SGL")# Trigger once then return to HOLD state

 # matrix pins for connecting to probes
 # These values come from examining to silkscreen on the probe card and
 # are valid for 240um and 480um pitch 4x2 probecards
A = 17
B = 14
C = 23
D = 20
E = 5
F = 8
G = 2
H = 11

# matrix port numbers - channel numbers refer to how the SMUs are
# installed in the rack, see manual
smu1 = 1 # 40uV-100V 100mA, 4142B channel  # 1
smu2 = 2 # 40uV-200V 1A, 4142B channel  # 3
smu3 = 3 # 40uV-100V 100mA, 4142B channel  # 4
smu4 = 4 # 40uV-100V 100mA, 4142B channel  # 5
smu5 = 5 # +/- 40V, 4142B channel  # 6
gnd = 7 # SMU ground
dmm_hi = 8
dmm_lo = 9

# NOTE: indent in python  Groups together instructions (as with begin - end
#       in other languages)

#Matrix commands
def connect(port,pin):
    cmd = 'PC{}ON{:02d}'.format(port,pin) # generate command string for matrix
    matrix.write(cmd)
     #  print('matrix {} connected to {}'.format(port,pin)) # uncomment to debug

def clear_matrix():
    cmd = "CL"
    matrix.write(cmd)
     #  print('matrix clear') # uncomment to debug

#DMM measurement
def sample(): # need to read byte at a time otherwise causes a crash. TODO fix this
    dmm.write("TRIG SGL")
    message = ''
    byte = ''
    while byte != '\r': # look for first character of read termination
        message += byte
        byte = dmm.read_bytes(1)
    return message
     #  print('dmm send sample') # uncomment to debug

 # Measurement configurations
def LW300_plus(): #Test structure 1. 300 um linewidth - positive current
    clear_matrix()
    connect(smu1,D)
    connect(gnd,G)
    connect(dmm_hi,A)
    connect(dmm_lo,H)
    return 'LW300_plus'

def LW300_minus(): #Test structure 1. 300 um linewidth - neg current
    clear_matrix()
    connect(smu1,G)
    connect(gnd,D)
    connect(dmm_hi,H)
    connect(dmm_lo,A)
    return 'LW300_minus'

def LW600_plus(): #Test structure 2. 600 um linewidth - positive current
    clear_matrix()
    connect(smu1,D)
    connect(gnd,E)
    connect(dmm_hi,A)
    connect(dmm_lo,F)
    return 'LW600_plus'

def LW600_minus(): #Test structure 2. 600 um linewidth - neg current
    clear_matrix()
    connect(smu1,E)
    connect(gnd,D)
    connect(dmm_hi,F)
    connect(dmm_lo,A)
    return 'LW600_minus'

def SC300_plus(): #Test structure 3. 300 um semi circle - positive current
    clear_matrix()
    connect(smu1,F)
    connect(gnd,E)
    connect(dmm_hi,H)
    connect(dmm_lo,G)
    return 'SC300_plus'

def SC300_minus(): #Test structure 3. 300 um semi circle - neg current
    clear_matrix()
    connect(smu1,E)
    connect(gnd,F)
    connect(dmm_hi,G)
    connect(dmm_lo,H)
    return 'SC300_minus'

 # Change this for GC20 - Greek cross - Test structure 4
 # Note that the GX measurements should be disregarded if usint AgCl layers

 # R_0(+I) connect D & C to DMM, connect A & B to smu
def R_0_I_plus():
    clear_matrix()
    connect(smu1,A) # smu 1 to contact A
    connect(gnd,B) # gnd to contact B
    connect(dmm_hi,D)
    connect(dmm_lo,C)
    return 'R_0_I_plus'


 # R_0(-I) connect C & D to DMM, connect B & A to SMU
def R_0_I_minus():
    clear_matrix()
    connect(smu1,B) # smu 1 to contact A
    connect(gnd,A) # gnd to contact B
    connect(dmm_hi,C)
    connect(dmm_lo,D)
    return 'R_0_I_minus'

 # R_90(+I) connect C & B to DMM, connect D & A to SMU
def R_90_I_plus():
    clear_matrix()
    connect(smu1,D) # smu 1 to contact A
    connect(gnd,A) # gnd to contact B
    connect(dmm_hi,C)
    connect(dmm_lo,B)
    return 'R_90_I_plus'

 # R_90(-I) connect B & C to DMM, connect A & D to SMU
def R_90_I_minus():
    clear_matrix()
    connect(smu1,A) # smu 1 to contact A
    connect(gnd,D) # gnd to contact B
    connect(dmm_hi,B)
    connect(dmm_lo,C)
    return 'R_90_I_minus'


configurations = {'LW300':[LW300_plus,LW300_minus],'LW600':[LW600_minus,LW600_plus],'GC20_SC300':[R_0_I_plus,R_0_I_minus,R_90_I_plus,R_90_I_minus,SC300_plus,SC300_minus]}# measurement configurations for each structure

exponent = -6  # muA this is combined with values below when configuring the SMU - look like the unit of the forced current is are now Amps

measurements_lw = {'Pt':100,'Pt_Cl':100,'Ag':100,'Ag_Cl':100,'Pt_Ag':100,'Pt_Ag_Cl':100} # per material driving currents for LW300,LW600 and SC300 (muA)

measurements_rs = {'Pt':50,'Pt_Cl':50,'Ag':50,'Ag_Cl':50,'Pt_Ag':50,'Pt_Ag_Cl':50} # per material driving currents for GC20 (muA)

with open(coordinate_file,'r') as f: # read the csv file into a pandas DataFrame
    df = pandas.read_csv(f)

home = pd.DataFrame([df.iloc[home_index]],index=[0]) # choose the first coordinate in the dataframe as the home position
home_coords = home[['x','y']].values[0]*-1.0 # extract the coordinates of the home position and transform into chuck coordinates

if filter_structures==True:
    try:
        subset = df.query(filter_string)#apply filter string
    except:
        print('ERROR: Malformed filter query')
        exit()
    if subset.empty:
        print('ERROR: filter query did not match any structures')
    # subset = df.query('structure in ["LW300","LW600","GC20_SC300"] & material == "Pt"') # filter the structures to create a subset to visit
     #  subset = df.query('structure in ["LW300","LW600","GC20_SC300"] & material == "Pt" & block<12') # filter the structures to create a subset to visit
    df = subset
    print('filter')
df['x'] = df['x']*-1.0 # scope is fixed and stage moves underneath so apparent motions are reversed
df['y'] = df['y']*-1.0

coords = zip(df.x,df.y)
coords = [numpy.array(c)-numpy.array(home_coords) for c in coords] # establishes all structures relative to stage home position
structure_names = df.index
structures = zip(structure_names,coords) # creeate a list of structures to visit

if len(structures)<start_index:
    print('start index out of bounds')
    exit()

results.write('index,wafer,die,block,material,structure,config,current,voltage,resistance\n')
#perform the measurement
pb.chuckSeparation() # ensure/chuck is separated before moving, hardware also ensures this
for i,structure in enumerate(structures): # iterate over all structures
    if i < start_index:#ignore structures before start index
        continue
    pb.translate(*structure[1])
    time.sleep(2.5) # wait in seconds to arrive TODO replace with chuck status check
    if not dry_run:
        pb.chuckContact() # move z stage to probe contact position
    time.sleep(0.5) # wait for contact to occur
    smu.write('DZ1') # ensure the smu is disconnected
    material = df.iloc[i].material # get the material type of this structure
    structure_type = df.iloc[i].structure # get the structure type
    block = df.iloc[i].block#extract the block value of the structure

    smu.write('DZ1') # measure the smu is disconnected
    selected_configs = configurations[structure_type] # choose measurement configurations based on structure type
    for configuration in selected_configs:
        config  = configuration() # setup the appropriate configuration
        if configuration in [R_0_I_plus,R_0_I_minus,R_90_I_plus,R_90_I_minus]: # if configured for sheet resistance use those currents
            current_value = measurements_rs[material] # pick from sheet resistance currents
        else:
            current_value = measurements_lw[material] # pick from linewidth currents
        smu.write('CN1')
        smu.write('DI1,0,{}E{},10'.format(current_value,exponent)) # set SMU constant current
        time.sleep(0.2) # allow to settle
        samp = sample() # get a sample from dmm
        current = current_value*10**exponent
        resistance = samp/current
        if not dry_run:
            results.write('{},{},{},{},{},{},{},{},{},{}\n'.format(i,wafer,die,block,material,structure_type,config,current,samp,resistance)) # write sample along with structure information to file
            print('index: {}\nwafer: {}\ndie: {}\nblock: {}\nmaterial: {}\nstructure: {}\nmeasurement: {}\ncurrent: {}\nvoltage: {}\nresistance: {}\n{}\n'.format(i,wafer,die,block,material,structure_type,config,current,samp,resistance,'-'*40))
        else:
            print('index: {}\nwafer: {}\ndie: {}\nblock: {}\nmaterial: {}\nstructure: {}\n{}\n'.format(i,wafer,die,block,material,structure_type,config,current,samp,resistance,'-'*40))
        smu.write('DZ1') # TODO double check this disable to smu
    pb.chuckSeparation() # separate contacts after measurements
    print('='*40) # delineate each structure
     #  time.sleep(1)

results.close()#close the data file
print('Complete')
'''
~~~~
'''
