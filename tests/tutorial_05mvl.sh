##KEEP THIS SIMILAR TO pymarble/tests/backendTutorial.py
# this is longer and contains all the functions, verifications
# add 'm' without any quotation to do manual test with lots of output

# Load file, magic analyse to find items of interest, save work-in-progress to xml-based file
#   - save so that next time, no magic-analyse has to be done
#   - fill is helpfull to mark unidentified domains
#   - the printed list is already interesting
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "m; ot"
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; l"
fi

# One can also start with some previously exported data from the proprietary software
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "e tests/examples/Membrane_Repeatability_08.txt"

# List all items; draw item starting at 69272; edit/save that information
#   - First load previously identified information
#   - Linear increasing first element: time-signal: 196-length
#   - it has a length of 195, since next data-elements 2*195
#     - initial 0 is not part of data
#     - we have to correct things:
#       - it starts 8-byte later
#       - it has -1 length
#   - save tags files after any modification
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; d 69272"
fi
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 69280 195|d|time|s; ot"
# Note that the old segment got deleted because it would overlap
#    - it also removes the value-label
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; l"
fi

# these are for testing
#   moving and printing, not required for tutorial
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; bi 195; fi 195"
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; g 69272; pd 5"
#   filling is not needed anymore, here just for testing (it is run in other part as well)
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; x fill"


# Draw item starting at 70840; analyse that information, read; edit and save that information
#   - Clearly, two different data are there
#   - This data is twice as long as the 195 observed before
#   - First part of this data is the displacement then the force
#   - afterwards list all to see remaning part at end of file
# Humans add the next line for more information
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; d 70840"
fi
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 70840 195|f|displacement|mm; ot"
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; la"
fi

# Scan new area
#   - find the sequence in that area
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; sf 71620"
# We can skip that step since we know its float so use that information
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 71620 195|f|force|N|https://en.wikipedia.org/wiki/Force; ot"


# Label some identified metadata
#  - first list everything
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; l"
fi
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 6836  ||displacement_label; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 12832 ||force_label; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 21148 ||process_name; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 32228 ||some_name; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; r 58448 ||path_name; ot"


# Save to python file
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; op"

# Calculate entroy of data file
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; z"

#use this python file to decipher this datafile and other raw datafile
echo
echo "Test Python script"
python3 tests/examples/Membrane_Repeatability_05.py tests/examples/Membrane_Repeatability_05.mvl
python3 tests/examples/Membrane_Repeatability_05.py tests/examples/Membrane_Repeatability_08.mvl


echo
echo "Test python import, and then compare the output, incl. diff"
echo "**WARNING SKIP APPLICATION TO OTHER FOR NOW"
#  mv tests/examples/Membrane_Repeatability_05.mvl.tags tests/examples/Membrane_Repeatability_05.tags
# Read python file
#  ./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "ip; ot"
#  diff tests/examples/Membrane_Repeatability_05.mvl.tags tests/examples/Membrane_Repeatability_05.tags

echo
echo "Python import and compare to real other file 08.mvl"
echo "**WARNING SKIP APPLICATION TO OTHER FOR NOW"
#./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "ip tests/examples/Membrane_Repeatability_05.py"

# Some sanity checks just for this testBackend script and programming
./marbleCLI.py tests/examples/Membrane_Repeatability_05.mvl "it; x verify"

