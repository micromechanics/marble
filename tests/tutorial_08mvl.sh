##KEEP THIS THE SLOWER VERSION TO tutorial_08.sh
# this is a much larger file and simply takes longer
# add 'm' without any quotation to do manual test with lots of output

# Load file, magic analyse to find items of interest, save work-in-progress to xml-based file
#   - save so that next time, no magic-analyse has to be done
#   - fill is helpfull to mark unidentified domains
#   - the printed list is already interesting
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "m; ot"
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; l"
fi

# List all items; draw item starting at 69272; edit/save that information
#   - !!!This is the same location as in the _05.mvl file!!!
#     - we can learn from the comparison of files
#     - let's not use this information for now
#   - Linear increasing first element: time-signal: 58077-length
# Let's try something, without saving:
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 69272 58077|d|time|s"
# Says: number not found in file.
# Let's not use the initial 0: is not part of data
#       - it starts 8-byte later
#       - it has -1 length
# Let's try something else, without saving:
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 69280 58076|d|time|s"
# Says: number is found at 000044: before the data
# - it is the same location as in ...05.mvl
# Let's use that and save
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 69280 58076|d|time|s; ot"

# The rest of the binary file was totally mangled: not identified. We have to use some common
# sense. If we have some primary data -- then in many cases -- this primary data is followed by
# more primary data until all primary data are saved. Moreover, all primary data have the same
# length.
# What is the end of the first primary data? We also want to include all (la) to be
# sure that we don't miss anything
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; la"
fi
# 533888 is the possible start that we use for creating a section and plotting it
# - SOMETIMES: although the graph looks like some data, it also is strange
#   - no value that we measured goes but to 500000
# - OTHERTIMES: the command fails
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 533888 58076|d|something|1; d 533888"
fi
# lets try the same but what if it is a float (instread of double)
# - this makes sense, as the displacement went up to 100mm and was linearly increasing
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 533888 58076|f|something|1; d 533888"
fi
# save it
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 533888 58076|f|displacement|mm; ot"

# Now we redo the last steps: check the current state, list all:
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; la"
fi
# Try double first
# - this should always fail
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 766192 58076|d|something|1; d 766192"
fi
# Try float accuracy second
# - this looks like the force
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 766192 58076|f|something|1; d 766192"
fi
# save it and list all
# - the force runs all the way to the end of the file
# - this makes us somewhat certain that we deciphered it accurately
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 766192 58076|f|force|N; ot"
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; la"
fi


# Label some identified metadata
#  - first list everything
#  - it has the same coordinates as the .._05.mvl file
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; l"
fi
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 6836  ||displacement_label; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 12832 ||force_label; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 21148 ||process_name; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 32228 ||some_name; ot"
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; r 58448 ||path_name; ot"

# Save to python file
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; op"
#use this python file to decipher this datafile and other raw datafile
echo
echo "Test Python script"
python tests/examples/Membrane_Repeatability_08.py tests/examples/Membrane_Repeatability_08.mvl
python tests/examples/Membrane_Repeatability_08.py tests/examples/Membrane_Repeatability_08.mvl


echo
echo "Test python import, and then compare the output, incl. diff"
echo "**WARNING SKIP APPLICATION TO OTHER FOR NOW"
#  mv tests/examples/Membrane_Repeatability_08.mvl.tags tests/examples/Membrane_Repeatability_05.tags
# Read python file
#  ./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "ip; ot"
#  diff tests/examples/Membrane_Repeatability_08.mvl.tags tests/examples/Membrane_Repeatability_05.tags

echo
echo "Python import and compare to real other file 08.mvl"
echo "**WARNING SKIP APPLICATION TO OTHER FOR NOW"
#./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "ip tests/examples/Membrane_Repeatability_05.py"

# Some sanity checks just for this testBackend script and programming
./marbleCLI.py tests/examples/Membrane_Repeatability_08.mvl "it; x verify"

