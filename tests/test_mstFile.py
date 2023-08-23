#!/usr/bin/python3
import warnings, os
from pymarble.file import BinaryFile

def test_main():
  # initialization: create database, destroy on filesystem and database and then create new one
  warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
  warnings.filterwarnings('ignore', message='invalid escape sequence')
  warnings.filterwarnings('ignore', message='divide by zero encountered in log10')
  #clean
  # files = ['1.py','1.hdf5','1.mst.tags']
  # for iFile in files:
  #   if os.path.exists('tests/examples/'+iFile):
  #     os.unlink('tests/examples/'+iFile)

  ## KEEP THIS SIMILAR (but much shorter) TO Tests/backendTutorial.py
  fBIN = BinaryFile('tests/examples/1.mst')
  fBIN.automatic()
  fBIN.label(8,   '17|c|Type of file|||metadata|[]|[18]|100|3.452819531114783|True|Scratch test file')
  fBIN.label(470, '1|i|k1=1500|||count|[]|[1]|100|1.584962500721156|True|')
  fBIN.label(474, '16500|f|primary data in rows|||primary|[470, -1]|[1500, 11]|100|4.704180709093521|True|primary data in rows')
  fBIN.fill()
  fBIN.rowFormatSegments = {474}
  fBIN.rowFormatMeta = [{"key": "friction distance x", "unit": "m", "link": ""},
                        {"key": "friction force", "unit": "N", "link": ""},
                        {"key": "acoustic emmision", "unit": "%", "link": ""},
                        {"key": "normal depth Pd", "unit": "m", "link": ""},
                        {"key": "normal force Fn", "unit": "N", "link": ""},
                        {"key": "pre profile ", "unit": "m", "link": ""},
                        {"key": "post profile", "unit": "m", "link": ""},
                        {"key": "time", "unit": "s", "link": ""},
                        {"key": "measured Fn", "unit": "N", "link": ""},
                        {"key": "zero10", "unit": "", "link": ""},
                        {"key": "zero11", "unit": "", "link": ""}]
  fBIN.saveTags()
  fBIN.savePython()

  #FOOTER
  fBIN.file.close()
  print('\n*** DONE WITH VERIFY ***')
