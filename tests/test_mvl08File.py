#!/usr/bin/python3
import warnings, os
from pymarble.binaryFile import BinaryFile

def test_main():
  # initialization: create database, destroy on filesystem and database and then create new one
  warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
  warnings.filterwarnings('ignore', message='invalid escape sequence')
  warnings.filterwarnings('ignore', message='divide by zero encountered in log10')
  #clean
  files = ['Membrane_Repeatability_05.py','Membrane_Repeatability_08.hdf5','Membrane_Repeatability_05.hdf5',
           'Membrane_Repeatability_05.mvl.tags','Membrane_Repeatability_05.tags']
  for iFile in files:
    if os.path.exists('tests/examples/'+iFile):
      os.unlink('tests/examples/'+iFile)

  ## KEEP THIS SIMILAR (but much shorter) TO Tests/backendTutorial.py
  fBIN = BinaryFile('tests/examples/Membrane_Repeatability_08.mvl')
  fBIN.useExportedFile('tests/examples/Membrane_Repeatability_08.txt')
  fBIN.printList(True)

  #FOOTER
  fBIN.file.close()
  print('\n*** DONE WITH VERIFY ***')
