
###########################################################################
# TEST: tests/examples/alone.idr
#
# File with image inside
# - run automatic function to look for xml data, zero data and ascii data "x_z_a_p"
# - list only non-binary, since so many
# - note there is some periodicity STARTING AT THE FIRST SECTION
./marbleCLI.py tests/examples/alone.idr 'm; ot'
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; l'
fi

# Lets study the first 4 integers = 4x4=16bytes
# - there are four tests
# - each with 1 subtask
# - 1562 is very close to the number of double following
# - 774 or 776 seems to be the end of loading
./marbleCLI.py tests/examples/alone.idr 'pi 4'
# 0 (4, 1, 1562, 774)

# Lets draw them
# They seem to be in this order
# 1. the force in mN
# 2. the displacement in nm
#   - the first two values are strange: 2*8byte=16byte
#   - they should be cut of
#   - length decreases by 2
# 3. time with some jumps where no data was recorded
#   see the end of loading at ~770
# 4. something linear with a strange beginning and much shorter than the other data
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; d 16'
  ./marbleCLI.py tests/examples/alone.idr 'it; d 32000'
  ./marbleCLI.py tests/examples/alone.idr 'it; d 64176'
  ./marbleCLI.py tests/examples/alone.idr 'it; d 90344'
fi

# Lets look at the list again in more detail
# - we see some text that suggests that these are uninitialized areas (malloc)
#   that were dumped to the file
# - also the size of 32000 is suspicios
# - lets assume the third set starts at 64k+16 and give it a longer length
#   - at 1562 !!
# - note that these tests are not saved to file
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; l'
  ./marbleCLI.py tests/examples/alone.idr 'it; r 64016 1562|d|test; d 64016'
fi

# Lets clean up everything: assuming the length is 1562
# - changes are written to file
./marbleCLI.py tests/examples/alone.idr 'it; r 16    4000|d|force|mN||primary||1562; ot'
./marbleCLI.py tests/examples/alone.idr 'it; r 32016 4000|d|displacement|nm||primary||1562; ot'
./marbleCLI.py tests/examples/alone.idr 'it; r 64016 4000|d|time|s||primary||1562; ot'
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; l'
fi

# We observed hat there is periodicity, lets nail it down
# - the last dataset (time) runs until 96016
# - lets read the 3 numbers after that
# - looks strangely familiar to the things at position 0
# - 96016+3*4=96028 which is the identified start of the next dataset
./marbleCLI.py tests/examples/alone.idr 'g 96016; pi 3'
# 96016 (1, 1583, 781)

# Concluding:
# - first integer in file is number of periodicity, number of tests
# - 3 integers are at the beginning of each periodicity
# - then we have 3x 32k bytes
# - only some of that is required
# - once we have identified first sequence of periodicity, that should be enough
./marbleCLI.py tests/examples/alone.idr 'it; r 0 1|i|peridicity:count|||count; ot'
./marbleCLI.py tests/examples/alone.idr 'it; r 4 1|i|cycle_number; ot'
./marbleCLI.py tests/examples/alone.idr 'it; r 12 1|i|index_end_loading; ot'
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; l'
fi
./marbleCLI.py tests/examples/alone.idr 'it; t 0 4 64016; ot'

#Lets clean up
# -first check then write to file
# -it is not needed
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; y 117004 117028; l'
fi
./marbleCLI.py tests/examples/alone.idr 'it; y 117004 117028; ot'
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/alone.idr 'it; l'
fi

# write python file and test it
./marbleCLI.py tests/examples/alone.idr 'it; op'
python3 tests/examples/alone.py tests/examples/alone.idr

echo
echo "Test python import, and then compare the output, incl. diff"
# mv tests/examples/alone.idr.tags tests/examples/alone.tags
# # Read python file
# ./marbleCLI.py tests/examples/alone.idr "ip; ot"
# diff tests/examples/alone.idr.tags tests/examples/alone.tags
