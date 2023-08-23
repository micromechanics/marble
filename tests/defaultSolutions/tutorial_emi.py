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
import struct, sys, os, hashlib, json
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


def addData(relPos, format, hdfBranch, key, metadata, shape=None):
  '''
  helper function: add data to branch

  Args:
    relPos: relative file offset
    format: data to read, int=numb. of chars, otherwise 4i
    hdfBrach: branch to add
    key: name of the key
    metadata: metadata incl. scientific unit
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
  metadataDict = json.loads(metadata.replace("'",'"'))
  for keyI, valueI in metadataDict.items():
    dset.attrs[keyI] = valueI
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
  addData(0, f"{k1*k2}H", hdfBranch, "image", "{'unit': '', 'link': ''}", shape=[k1,k2])
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
# rowFormatMeta=[]
# rowFormatSegments=[]
# length=29
length,dType,key,unit,link,dClass,count,shape,prob,entropy,important,value
20,b,,,,,[],[20],0,2.39,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,11.47.41 CCD Acquire
8,b,,,,,[],[8],0,2.13,False,unknown binary string
11,c,,,,,[],[11],32,2.65,False,4.19.0.2543
234,b,,,,,[],[234],0,3.72,False,unknown binary string
22,c,,,,,[],[21],40,3.78,False,Normal Image Displayp
229,b,,,,,[],[229],0,3.65,False,unknown binary string
28,c,,,,,[],[27],40,3.99,False,Acquire CCD Image Display C
152,b,,,,,[],[152],0,3.54,False,unknown binary string
22,c,,,,,[],[21],40,3.78,False,Normal Image Displayp
54,b,,,,,[],[54],0,3.12,False,unknown binary string
14,c,,,,,[],[13],36,3.39,False,Acquire CCD p
197,b,,,,,[],[33554715],0,3.48,False,unknown binary string
1,i,k1=4096,,,count,[],[1],100,0.92,True,
1,i,k2=4096,,,count,[],[1],100,0.92,True,unknown binary string
16777216,H,image,,,primary,"[1011, 1015]","[4096, 4096]",100,4.12,True,"streak of dType=H, length=16777254"
78,b,,,,,[],[78],0,3.86,False,unknown binary string
10,c,,,,,[],[10],30,2.95,False,Real Space
8,b,,,,,[],[8],0,2.13,False,unknown binary string
18,c,file_path,,,metadata,[],[18],100,3.57,True,Z:\\Users\\Nico\\2021
41,b,,,,,[],[41],0,4.15,False,unknown binary string
15,c,,,,,[],[14],38,3.09,False,OA_0000_1.ser2
12,b,,,,,[],[12],0,2.85,False,unknown binary string
7246,c,metadata,,,metadata,[],[10],100,4.13,False,xml string
261,b,,,,,[],[261],0,4.45,False,unknown binary string
10,c,,,,,[],[10],30,2.95,False,Real Space
24,b,,,,,[],[24],0,3.02,False,unknown binary string
11,c,,,,,[],[10],30,3.32,False,ElectronsA
32,b,,,,,[],[32],0,2.45,False,unknown binary string
'''
