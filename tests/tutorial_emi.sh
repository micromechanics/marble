###########################################################################
# TEST: tests/examples/1-11-OA_0000.emi
# add 'm' without any quotation to do manual test with lots of output
#
# File with image inside
# - run automatic functino to look for xml data, zero data and ascii data "x_z_a"
# - list all and note that there is a huge chunk unidetifed at 814

./marbleCLI.py tests/examples/1-11-OA_0000.emi 'm x_z_a; ot'
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; la'
fi


# Image starts at 1019 and 'streak finding' sees it (always works)
# - set it to real length
# - fill afterwards
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; sH 1019; r 1019 16777216|H|image; x fill; ot'
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'fi 4096'
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; r 1011 1|i|k1=4096|||count; x fill; ot'
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; r 1015 1|i|k2=4096|||count; x fill; ot'
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; r 1019 16777216|H|image|||primary|1011,1015; ot'


# Plot/Draw it in 2D
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; d2 1019'
fi

# Add some metadata, list all non-binary entries and output python file
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; r 33555547 ||file_path; ot'
if [[ -n "$1" ]] && [ $1 = m ]; then
  ./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; l'
fi
./marbleCLI.py tests/examples/1-11-OA_0000.emi 'it; op'

# Test
python3 tests/examples/1-11-OA_0000.py tests/examples/1-11-OA_0000.emi

# echo
# echo "Test python import, and then compare the output, incl. diff"
# mv tests/examples/1-11-OA_0000.emi.tags tests/examples/1-11-OA_0000.tags
## Read python file
# ./marbleCLI.py tests/examples/1-11-OA_0000.emi "ip; ot"
# diff -q tests/examples/1-11-OA_0000.emi.tags tests/examples/1-11-OA_0000.tags


