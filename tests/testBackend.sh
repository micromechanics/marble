#!/usr/bin/env bash
#TEST TUTORIALS
export PATH="$PWD/.venv/bin:$PATH"
export PYTHON="${PYTHON:-$PWD/.venv/bin/python}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/pymarble-matplotlib}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/tmp/pymarble-config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/pymarble-cache}"
mkdir -p "$MPLCONFIGDIR"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"

echo
echo "Run first test: tests/examples/Membrane_Repeatability_05.mvl"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5  # Remove all previously generated files
./tests/tutorial_05mvl.sh > thisOutput.log
punx validate --report NOTE,WARN,ERROR tests/examples/Membrane_Repeatability_05.hdf5| grep 'NOTE\|does not meet NeXus specification, not generally acceptable\|ERROR'
punx validate --report NOTE,WARN,ERROR tests/examples/Membrane_Repeatability_08.hdf5| grep 'NOTE\|does not meet NeXus specification, not generally acceptable\|ERROR'
echo "check if python & output are equal to supposted output: diff.."
diff -bZw tests/examples/Membrane_Repeatability_05.py tests/defaultSolutions/tutorial_05mvl.py
diff -bZw thisOutput.log tests/defaultSolutions/tutorial_05mvl.log
echo "======================================================================"

echo
echo "Run the Python unit-test: short siblings of previous"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5  # Remove all previously generated files
"$PYTHON" -m unittest discover tests/ > thisOutput.log
echo "check if output are equal to supposted output: diff.."
diff -bZw thisOutput.log tests/defaultSolutions/unittest.log
echo "======================================================================"

echo
echo "Run third test: tests/examples/1-11-OA_0000.emi"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5
./tests/tutorial_emi.sh > thisOutput.log
punx validate --report NOTE,WARN,ERROR tests/examples/1-11-OA_0000.hdf5| grep 'NOTE\|does not meet NeXus specification, not generally acceptable\|ERROR'
echo "check if python & output are equal to supposted output: diff.."
diff -bZw tests/examples/1-11-OA_0000.py tests/defaultSolutions/tutorial_emi.py
diff -bZw thisOutput.log tests/defaultSolutions/tutorial_emi.log
echo "======================================================================"

echo
echo "Run forth test: tests/examples/alone.idr"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5
./tests/tutorial_idr.sh > thisOutput.log
punx validate --report NOTE,WARN,ERROR tests/examples/alone.hdf5| grep 'NOTE\|does not meet NeXus specification, not generally acceptable\|ERROR'
echo "check if python & output are equal to supposted output: diff.."
diff -bZw tests/examples/alone.py tests/defaultSolutions/tutorial_idr.py
diff -bZw thisOutput.log tests/defaultSolutions/tutorial_idr.log
echo "======================================================================"

echo
echo "Run fifth test: tests/examples/Membrane_Repeatability_08.mvl"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5
./tests/tutorial_08mvl.sh > thisOutput.log
punx validate --report NOTE,WARN,ERROR tests/examples/Membrane_Repeatability_08.hdf5| grep 'NOTE\|does not meet NeXus specification, not generally acceptable\|ERROR'
echo "check if python & output are equal to supposted output: diff.."
diff -bZw tests/examples/Membrane_Repeatability_08.py tests/defaultSolutions/tutorial_08mvl.py
diff -bZw thisOutput.log tests/defaultSolutions/tutorial_08mvl.log
echo "======================================================================"

echo
echo "Run the ALL Python test"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5  # Remove all previously generated files
"$PYTHON" -m pytest tests > thisOutput.log
echo "======================================================================"
