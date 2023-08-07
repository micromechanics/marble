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
  fBIN = BinaryFile('tests/examples/1-11-OA_0000.emi', verbose=2, fileType='data')
  fBIN.printMode = 'hex'
  fBIN.fill()
  fBIN.findXMLSection()
  fBIN.fill()
  fBIN.printList()
  fBIN.file.seek(0)
  text = fBIN.byteToString(fBIN.file.read(8),0)
  print('Text without spaces',text)
  text = fBIN.byteToString(fBIN.file.read(8),2)
  print('Text with spaces',text)
  print('How many bytes are coming?')
  fBIN.printNext(1,'i')
  print('What is the content?')
  fBIN.printNext(20,'s')
  print('Address of integer 20')
  fBIN.findValue(20,dType='i',offset=0)
  print('Address of float 172: ', fBIN.findValue(172,dType='f',offset=0, verbose=False))
  print('Address of float 172: ', fBIN.findBytes(172,dType='f',offset=0))
  fBIN.file.seek(0)
  fBIN.printAscii(20)


  #FOOTER
  fBIN.file.close()
  print('\n*** DONE WITH VERIFY ***')
