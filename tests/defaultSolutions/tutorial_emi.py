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
# meta={"vendor": "", "label": "", "software": "", "ext": "emi"}
# periodicity={}
# length=29
length,dType,key,unit,link,dClass,count,prob,entropy,important,value
20,b,,,,,[],0,2.3943,False,b'4A 4B 00 02 00 00 00 00 04 4D 01 00 60 00 00 01 14 00 00 00'
20,c,,,,,[],40,3.5766,False,b'11.47.41 CCD Acquire'
8,b,,,,,[],0,2.1281,False,b'60 00 12 07 0B 00 00 00'
11,c,,,,,[],32,2.6464,False,b'4.19.0.2543'
234,b,,,,,[],0,3.7218,False,b'60 00 08 52 00 00 00 00 60 00 0C 52 00 00 00 00 60 00 10 52 00 00 00 00 60 00 00 05 06 00 00 00 4E 6F 72 6D 61 6C 70 00 02 05 01 70 00 04 05 00 31 00 06 05 00 00 00 00 70 00 07 05 01 34 43 02 07 2C 43 00 01 20 00 00 04 F9 20 00 01 04 FB 20 00 02 04 EE 00 00 2C 43 10 01 20 00 00 04 FF 20 00 01 04 FF 20 00 02 04 FF 00 00 02 21 40 01 0C 00 00 00 08 00 00 00 FF FF FF FF FF FF FF FF 31 00 30 01 01 00 00 00 31 00 50 01 03 00 00 00 00 00 70 00 04 07 00 50 43 06 07 32 00 00 01 02 00 41 00 00 02 00 00 00 00 00 00 E0 3F 00 00 20 43 00 07 31 00 00 01 27 00 00 00 31 00 01 01 FF 00 00 00 31 00 02 01 CE 03 00 00 31 00 03 01 82 06 00 00 00 00 56 44 10 07 00 00 08 44 08 07 00 44 00 01 60 00 00 01 14 00 00 00'
22,c,,,,,[],40,3.7849,False,b'Normal Image Displayp'
229,b,,,,,[],0,3.6524,False,b'02 02 00 70 00 00 02 00 2C 43 00 03 20 00 00 04 E3 20 00 01 04 F4 20 00 02 04 FD 00 00 2C 43 02 03 20 00 00 04 FB 20 00 01 04 FC 20 00 02 04 F3 00 00 2C 43 04 03 20 00 00 04 76 20 00 01 04 CB 20 00 02 04 EB 00 00 31 00 06 03 00 00 00 00 70 00 08 03 00 70 00 0A 03 00 00 00 02 45 00 01 60 00 00 01 06 00 00 00 4E 6F 72 6D 61 6C 70 00 02 02 00 70 00 00 02 00 31 00 00 04 02 00 00 00 31 00 02 04 02 00 00 00 41 00 04 04 56 0E 2D B2 9D EF EF 3F 42 43 06 04 2C 43 00 01 20 00 00 04 00 20 00 01 04 00 20 00 02 04 00 00 00 40 43 00 02 41 00 00 01 00 00 00 00 00 00 F0 3F 2C 43 00 02 20 00 00 04 FF 20 00 01 04 FF 20 00 02 04 FF 00 00 00 00 00 00 00 00 00 00 50 45 10 06 60 00 00 01 19 00 00 00'
28,c,,,,,[],40,3.9862,False,b'Acquire CCD Image Display C'
152,b,,,,,[],0,3.5449,False,b'06 31 00 00 01 00 00 00 00 31 00 01 01 00 00 00 00 31 00 02 01 88 03 00 00 31 00 03 01 77 05 00 00 00 00 20 43 02 06 31 00 00 01 07 00 00 00 31 00 01 01 07 00 00 00 31 00 02 01 82 03 00 00 31 00 03 01 71 05 00 00 00 00 32 41 04 06 41 00 00 02 00 00 00 00 00 B0 11 3C 41 00 02 02 00 00 00 00 00 B0 11 3C 41 00 04 02 E9 43 41 4E 09 E0 E1 3E 41 00 06 02 15 72 EB 84 1D F9 D6 3E 41 00 08 02 00 00 00 00 00 00 00 00 00 00 70 00 0E 06 00 60 00 00 05 14 00 00 00'
22,c,,,,,[],40,3.7849,False,b'Normal Image Displayp'
54,b,,,,,[],0,3.1184,False,b'02 05 01 70 00 04 05 00 31 00 06 05 00 00 00 00 70 00 07 05 01 31 00 00 08 00 00 00 00 70 00 02 08 01 31 00 12 09 02 00 00 00 B0 49 10 06 60 00 00 01 0C 00 00 00'
14,c,,,,,[],36,3.3927,False,b'Acquire CCD p'
197,b,,,,,[],0,3.4838,False,b'12 04 01 60 41 42 00 70 00 00 01 01 31 00 02 01 10 00 00 00 31 00 04 01 ED 20 00 00 31 00 06 01 FF FF FF FF 70 00 08 01 00 31 00 0A 01 00 00 00 00 31 00 0C 01 00 00 00 00 31 00 0E 01 00 00 00 00 31 00 10 01 01 00 00 00 70 00 2A 01 00 70 00 12 01 00 70 00 14 01 00 70 00 16 01 00 70 00 18 01 00 41 00 1A 01 00 00 00 A0 97 BE EA 3F 41 00 1C 01 00 00 00 00 00 00 00 00 41 00 1E 01 00 00 00 00 00 00 00 00 41 00 20 01 00 00 00 00 00 00 00 00 34 00 22 01 41 81 78 2A 52 C4 05 00 31 00 24 01 FF FF FF FF 31 00 26 01 E9 32 00 00 31 00 28 01 FF FF FF FF 00 00 20 00 00 02 05 04 22 02 02 08 00 00 02'
1,i,k1=4096,,,count,[],100,0.9183,True,b''
1,i,k2=4096,,,count,[],100,0.9183,True,b'00 10 00 00'
-1,H,image,,,primary,"[1011, 1015]",100,4.1197,True,"b'streak of dType=H, length=16777254'"
78,b,,,,,[],0,3.8621,False,b'02 41 00 03 41 00 00 01 CA ED A8 18 D2 4D C6 BE 41 00 20 01 00 F0 A8 18 D2 4D 16 3E 31 00 40 01 00 00 00 00 41 00 10 01 CA ED A8 18 D2 4D C6 BE 41 00 30 01 00 F0 A8 18 D2 4D 16 3E 31 00 50 01 00 00 00 00 00 00 60 00 00 04 0A 00 00 00'
10,c,,,,,[],30,2.9477,False,b'Real Space'
8,b,,,,,[],0,2.1281,False,b'60 00 40 04 48 00 00 00'
18,c,file_path,,,meta,[],100,3.5725,True,b'Z:\\\\Users\\\\Nico\\\\2021'
41,b,,,,,[],0,4.1531,False,b'2D 30 36 2D 30 39 2D 54 45 4D 2D 67 78 41 6C 32 43 61 2D 43 68 75 6E 68 75 61 2D 49 6E 64 65 6E 74 31 5C 2D 31 2D 31 31 2D'
15,c,,,,,[],38,3.0931,False,b'OA_0000_1.ser2'
12,b,,,,,[],0,2.8454,False,b'42 04 02 00 60 00 19 04 50 1C 00 00'
7246,c,metadata,,,meta,[],100,4.126,False,b'xml string'
261,b,,,,,[],0,4.4499,False,b'0D 0A 60 00 00 05 06 00 00 00 4E 6F 72 6D 61 6C 70 00 02 05 01 70 00 04 05 00 31 00 06 05 01 00 00 00 70 00 07 05 01 30 41 00 07 41 00 00 02 58 EE 69 84 E5 9E 62 40 41 00 02 02 86 61 18 86 61 18 86 40 00 00 41 00 02 07 00 00 00 00 00 00 E0 3F 41 00 04 07 00 00 00 00 00 00 F0 3F 41 00 06 07 00 00 00 00 00 00 F0 3F 70 00 1A 07 00 70 00 18 07 01 32 41 08 07 41 00 00 02 1C DD 32 E7 1A C0 7A 40 41 00 02 02 15 50 01 15 50 01 65 3F 41 00 04 02 E8 D8 7C 37 FC 28 8A 40 41 00 06 02 15 50 01 15 50 01 75 3F 41 00 08 02 00 00 00 00 00 00 00 00 00 00 70 00 1C 07 01 30 00 20 07 02 00 30 00 21 07 00 00 70 00 30 07 01 41 00 32 07 6C 84 0C A2 97 BE EA 3F 70 00 34 07 01 31 00 36 07 0E 00 00 00 00 00 31 00 04 08 01 00 00 00 70 00 00 09 01 70 00 02 09 01 70 00 10 09 01 60 00 00 0A 0A 00 00 00'
10,c,,,,,[],30,2.9477,False,b'Real Space'
24,b,,,,,[],0,3.0223,False,b'86 42 02 0A 30 00 00 01 03 00 00 00 82 42 04 0A 60 00 00 01 09 00 00 00'
11,c,,,,,[],30,3.3219,False,b'ElectronsA'
32,b,,,,,[],0,2.4546,False,b'10 01 00 00 00 00 00 00 F0 3F 00 00 70 00 06 0A 00 70 00 08 0A 01 00 00 03 4D 00 08 00 00 00 00'
'''
