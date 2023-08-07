#!/usr/bin/env bash
#TEST TUTORIALS

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
python3 -m unittest discover tests/ > thisOutput.log
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
# TODO_P1 for now
# echo "check if python & output are equal to supposted output: diff.."
# diff -bZw tests/examples/alone.py tests/defaultSolutions/tutorial_idr.py
# diff -bZw thisOutput.log tests/defaultSolutions/tutorial_idr.log
# echo "======================================================================"

echo
echo "Run fifth test: tests/examples/Membrane_Repeatability_08.mvl"
rm -f tests/examples/*.tags tests/examples/*.py tests/examples/*.hdf5
./tests/tutorial_08mvl.sh > thisOutput.log
punx validate --report NOTE,WARN,ERROR tests/examples/Membrane_Repeatability_08.hdf5| grep 'NOTE\|does not meet NeXus specification, not generally acceptable\|ERROR'
echo "check if python & output are equal to supposted output: diff.."
diff -bZw tests/examples/Membrane_Repeatability_08.py tests/defaultSolutions/tutorial_08mvl.py
diff -bZw thisOutput.log tests/defaultSolutions/tutorial_08mvl.log
echo "======================================================================"
