#!/usr/bin/python3
# INFO: THIS PART IS IS FOR HUMANS BUT IT IS IGNORED BY MARBLE
'''
convert  emi to .hdf5 file

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

convURI = b'https://raw.githubusercontent.com/main/cwl/emi2hdf.cwl'
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
  k1 = readData(1011, "1i")[0]
  k2 = readData(0, "1i")[0]
  addData(0, str(k1*k2)+"H", hdfBranch, "image", "", shape=[k1,k2])
  addAttrs(96, 18, hdfBranch, "file_path")
  if os.path.getsize(fileNameIn)-fIn.tell()!=7652:
    print("Translation NOT successful")
  else:
    print("Translation successful")

except:
  print("**ERROR** Exception in translation")



'''
# INFO: THIS PART IS LOADED BY MARBLE
# version= 1.0
# meta={"vendor": "", "label": "", "software": "", "ext": "emi", "endian": "small"}
# periodicity={}
# length=29
length,dType,key,unit,link,dClass,count,prob,entropy,important,value
20,b,,,,,[],0,2.3943,False,b'unknown binary string'
20,c,,,,,[],40,3.5766,False,b'11.47.41 CCD Acquire'
8,b,,,,,[],0,2.1281,False,b'unknown binary string'
11,c,,,,,[],32,2.6464,False,b'4.19.0.2543'
234,b,,,,,[],0,3.7218,False,b'unknown binary string'
22,c,,,,,[],40,3.7849,False,b'Normal Image Displayp'
229,b,,,,,[],0,3.6524,False,b'unknown binary string'
28,c,,,,,[],40,3.9862,False,b'Acquire CCD Image Display C'
152,b,,,,,[],0,3.5449,False,b'unknown binary string'
22,c,,,,,[],40,3.7849,False,b'Normal Image Displayp'
54,b,,,,,[],0,3.1184,False,b'unknown binary string'
14,c,,,,,[],36,3.3927,False,b'Acquire CCD p'
197,b,,,,,[],0,3.4838,False,b'unknown binary string'
1,i,k1=4096,,,count,[],100,0.9183,True,b''
1,i,k2=4096,,,count,[],100,0.9183,True,b'unknown binary string'
-1,H,image,,,primary,"[1011, 1015]",100,4.1197,True,"b'streak of dType=H, length=16777254'"
78,b,,,,,[],0,3.8621,False,b'unknown binary string'
10,c,,,,,[],30,2.9477,False,b'Real Space'
8,b,,,,,[],0,2.1281,False,b'unknown binary string'
18,c,file_path,,,metadata,[],100,3.5725,True,b'Z:\\\\Users\\\\Nico\\\\2021'
41,b,,,,,[],0,4.1531,False,b'unknown binary string'
15,c,,,,,[],38,3.0931,False,b'OA_0000_1.ser2'
12,b,,,,,[],0,2.8454,False,b'unknown binary string'
7246,c,metadata,,,metadata,[],100,4.126,False,b'xml string'
261,b,,,,,[],0,4.4499,False,b'unknown binary string'
10,c,,,,,[],30,2.9477,False,b'Real Space'
24,b,,,,,[],0,3.0223,False,b'unknown binary string'
11,c,,,,,[],30,3.3219,False,b'ElectronsA'
32,b,,,,,[],0,2.4546,False,b'unknown binary string'
'''
