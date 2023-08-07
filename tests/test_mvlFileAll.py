#!/usr/bin/python3
import warnings, os
from pymarble.file import BinaryFile

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
  fBIN = BinaryFile('tests/examples/Membrane_Repeatability_05.mvl', verbose=3)
  fBIN.automatic()
  fBIN.automatic()
  fBIN.label(69280, '195|d|time|s')
  fBIN.label(70840, '195|f|displacement|mm')
  fBIN.label(71620, '195|f|force|N|https://en.wikipedia.org/wiki/Force')
  fBIN.plot(71620,show=False)
  fBIN.label(6836, '||displacement_label')
  fBIN.label(12832,'||force_label')
  fBIN.label(21148,'||process_name;')
  fBIN.label(32228,'||some_name')
  fBIN.label(58448,'||path_name')
  print()
  fBIN.printList(True)
  fBIN.verify()
  print()
  fBIN.printList()
  fBIN.saveTags()
  fBIN.loadTags()
  fBIN.savePython()
  fBIN.loadPython()
  # fBIN.file.seek()
  # fBIN.findStreak()

  #FOOTER
  fBIN.file.close()
  print('\n*** DONE WITH VERIFY ***')
