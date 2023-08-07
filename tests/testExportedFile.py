#!/usr/bin/python3
import warnings, os, traceback
import unittest
from pymarble.file import BinaryFile
from pymarble.section import Section

class TestStringMethods(unittest.TestCase):
  def test_main(self):
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', message='divide by zero encountered in log10')
    try:
      ## KEEP THIS SIMILAR (but much shorter) TO Tests/backendTutorial.py
      #start
      print("\nSTART testExportedFile.py")
      fBIN = BinaryFile('tests/examples/Membrane_Repeatability_08.mvl')
      fBIN.useExportedFile('tests/examples/Membrane_Repeatability_08.txt')
      fBIN.file.close()
      self.assertTrue(fBIN.content[69280],'1st start wrong')
      self.assertTrue(fBIN.content[533888],'2nd start wrong')
      self.assertTrue(fBIN.content[766192],'3rd start wrong')
      print(fBIN.content[69280])
      self.assertTrue(str(fBIN.content[69280])=='58076|d|||||[44]|[58076]|90|-1.0|False|exportedData_col=1','1st start wrong')
      print(fBIN.content[533888])
      self.assertTrue(str(fBIN.content[533888])=='58076|f|||||[44]|[58076]|76|-1.0|False|exportedData_col=2','2nd start wrong')
      print(fBIN.content[766192])
      self.assertTrue(str(fBIN.content[766192])=='58076|f|||||[44]|[58076]|90|-1.0|False|exportedData_col=3','3rd start wrong')

      #FOOTER
      print('\n*** DONE WITH VERIFY ***')
    except:
      print('ERROR OCCURRED IN VERIFY TESTING')
      self.assertTrue(False,'Exception occurred')
    return

  def tearDown(self):
    return

if __name__ == '__main__':
  unittest.main()
