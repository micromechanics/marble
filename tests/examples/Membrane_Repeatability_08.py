#!/usr/bin/python3
# INFO: THIS PART IS IS FOR HUMANS BUT IT IS IGNORED BY MARBLE
'''
convert  mvl to .hdf5 file

in_file:
  label: 
  vendor: 
  software: 
out_file:
  label: custom HDF5 with k-tests as well as metadata and converter groups

Help:
  start as: [file-name.py] [binary-file]
  -v: verbose = adds additional output
'''
import struct, sys, os, hashlib
import h5py                                    #CWL requirement
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

convURI = b'https://raw.githubusercontent.com/main/cwl/mvl2hdf.cwl'
convVersion = b'1.5'

## COMMON PART FOR ALL CONVERTERS
fileNameIn = sys.argv[1]
fileNameOut= os.path.splitext(fileNameIn)[0]+'.hdf5'
fIn   = open(fileNameIn,'br')
fOut  = h5py.File(fileNameOut, 'w')
fOut.attrs['uri'] =     convURI
fOut.attrs['version'] = convVersion
fOut.attrs['original_file_name'] = fileNameIn
md5Hash = hashlib.md5()
md5Hash.update(fIn.read())
fOut.attrs['original_md5sum'] = md5Hash.hexdigest()
fOut.attrs['default'] = b'test_1'



def addAttrs(relPos, format, hdfBranch, key):
  '''
  helper function: add attribute to branch

  Args:
    relPos: relative file offset
    format: data to read, int=numb. of chars, otherwise 4i
    hdfBrach: branch to add
    key: name of the key

  Returns:
    none
  '''
  fIn.seek(relPos, 1)
  if '-v' in sys.argv:
    print('add Attrs', fIn.tell(), end=' ')
  key = key.lower().replace(' ','_')
  if type(format)==int:
    value = bytearray(source=fIn.read(format)).decode('latin-1')
    if hdfBranch:
      hdfBranch.attrs[key] = value.replace('\x00','')
  else:
    value = struct.unpack(format, fIn.read(struct.calcsize(format)))
    if hdfBranch:
      if len(value)==0:
        hdfBranch.attrs[key] = value[0]
      else:
        hdfBranch.attrs[key] = value
  if '-v' in sys.argv:
    print(value)
  return


def addData(relPos, format, hdfBranch, key, unit, shape=None):
  '''
  helper function: add data to branch

  Args:
    relPos: relative file offset
    format: data to read, int=numb. of chars, otherwise 4i
    hdfBrach: branch to add
    key: name of the key
    unit: scientific unit
    shape: shape of the array

  Returns:
    success
  '''
  fIn.seek(relPos, 1)
  if '-v' in sys.argv:
    print('add data', fIn.tell())
  data = fIn.read(struct.calcsize(format))
  if len(data) < struct.calcsize(format):
    return False
  data = struct.unpack(format, data)
  if shape is not None:
    data = np.array(data)[:np.prod(shape)].reshape(shape)
  if '-v' in sys.argv:
    if shape is not None and len(shape)==2:
      plt.imshow(data)
    else:
      plt.plot(data,'.')
    plt.show()
  dset = hdfBranch.create_dataset(key, data=data)
  dset.attrs['unit'] = unit
  hdfBranch.attrs['signal'] = key
  return True


def readData(relPos, format):
  '''
  helper function: read few values and return

  Args:
    relPos: relative file offset
    format: data to read, int=numb. of chars, otherwise 4i

  Returns:
    value as list
  '''
  fIn.seek(relPos, 1)
  if '-v' in sys.argv:
    print('read data', fIn.tell(), end=' ')
  data = fIn.read(struct.calcsize(format))
  if len(data) < struct.calcsize(format):
    return False
  if '-v' in sys.argv:
    print(struct.unpack(format, data))
  return struct.unpack(format, data)


###MAIN FUNCTION
try:
  fIn.seek(0)
  hdfBranch_ = fOut.create_group("test_1")
  hdfBranch_.attrs["NX_class"] = b"NXentry"
  hdfBranch = hdfBranch_.create_group("data")
  hdfBranch.attrs["NX_class"] = b"NXdata"
  if os.path.getsize(fileNameIn)-fIn.tell()!=998496:
    print("Translation NOT successful")
  else:
    print("Translation successful")

except:
  print("**ERROR** Exception in translation")



'''
# INFO: THIS PART IS LOADED BY MARBLE
# version= 1.0
# meta={"vendor": "", "label": "", "software": "", "ext": "mvl"}
# periodicity={}
# length=1
length,dType,key,unit,link,dClass,count,prob,entropy,important,value
998496,b,,,,,[],0,1.0,False,b''
'''
