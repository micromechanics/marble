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



def addAttrs(relPos, format, hdfBranch, key, unit=''):
  '''
  helper function: add attribute to branch

  Args:
    relPos: relative file offset
    format: data to read, int=numb. of chars, otherwise 4i
    hdfBrach: branch to add
    key: name of the key
    unit: unit of the value, saved as attribute key_units

  Returns:
    none
  '''
  fIn.seek(relPos, 1)
  if '-v' in sys.argv:
    print('add Attrs', fIn.tell(), end=' ')
  key = key.lower().replace(' ','_')
  if hdfBranch and unit:
    hdfBranch.attrs[key+'_units'] = unit
  if type(format)==int:
    value = bytearray(source=fIn.read(format)).decode('latin-1')
    if hdfBranch:
      hdfBranch.attrs[key] = value.split('\x00')[0]
  else:
    value = struct.unpack(format, fIn.read(struct.calcsize(format)))
    if hdfBranch:
      if len(value)==1:
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
  strLen16 = readData(16, "1i")[0]
  strLen44 = readData(24, "1i")[0]
  strLen289 = readData(241, "1i")[0]
  strLen540 = readData(247, "1i")[0]
  strLen720 = readData(176, "1i")[0]
  strLen796 = readData(72, "1i")[0]
  k1 = readData(211, "1i")[0]
  k2 = readData(0, "1i")[0]
  addData(0, f"{k1*k2}H", hdfBranch, "image", "{'unit': '', 'link': ''}", shape=[k1,k2])
  strLen33555525 = readData(74, "1i")[0]
  strLen33555543 = readData(14, "1i")[0]
  addAttrs(0, strLen33555543, hdfBranch, "file_path")
  strLen33555629 = readData(10, "1i")[0]
  strLen33563136 = readData(7503, "1i")[0]
  strLen33563170 = readData(30, "1i")[0]
  if os.path.getsize(fileNameIn)-fIn.tell()!=43:
    print("Translation NOT successful")
  else:
    print("Translation successful")

except Exception as error:
  print(f"**ERROR** {type(error).__name__}: {error}")



'''
# INFO: THIS PART IS LOADED BY MARBLE
# version= 1.0
# meta={"vendor": "", "label": "", "software": "", "ext": "emi", "endian": "small"}
# periodicity={}
# rowFormatMeta=[]
# rowFormatSegments=[]
# length=38
length,dType,key,unit,link,dClass,count,shape,prob,entropy,important,value
16,b,,,,,[],[16],0,2.31,False,unknown binary string
1,i,strLen16=20,,,count,[],[1],40,0.92,True,
20,c,,,,,[16],[20],40,3.58,False,11.47.41 CCD Acquire
4,b,,,,,[],[4],0,1.58,False,unknown binary string
1,i,strLen44=11,,,count,[],[1],32,0.92,True,
11,c,,,,,[44],[11],32,2.65,False,4.19.0.2543
230,b,,,,,[],[230],0,3.72,False,unknown binary string
1,i,strLen289=20,,,count,[],[1],40,0.92,True,
20,c,,,,,[289],[20],40,3.68,False,Normal Image Display
227,b,,,,,[],[227],0,3.64,False,unknown binary string
1,i,strLen540=25,,,count,[],[1],40,0.92,True,
25,c,,,,,[540],[25],40,3.97,False,Acquire CCD Image Display
151,b,,,,,[],[151],0,3.55,False,unknown binary string
1,i,strLen720=20,,,count,[],[1],40,0.92,True,
20,c,,,,,[720],[20],40,3.68,False,Normal Image Display
52,b,,,,,[],[52],0,3.08,False,unknown binary string
1,i,strLen796=12,,,count,[],[1],36,0.92,True,
12,c,,,,,[796],[12],36,3.28,False,Acquire CCD
199,b,,,,,[],[33554713],0,3.48,False,unknown binary string
1,i,k1=4096,,,count,[],[1],100,0.92,True,
1,i,k2=4096,,,count,[],[1],100,0.92,True,unknown binary string
16777216,H,image,,,primary,"[1011, 1015]","[4096, 4096]",100,4.12,True,"streak of dType=H, length=16777252"
74,b,,,,,[],[74],0,3.82,False,unknown binary string
1,i,strLen33555525=10,,,count,[],[1],30,0.92,True,
10,c,,,,,[33555525],[10],30,2.95,False,Real Space
4,b,,,,,[],[4],0,1.58,False,unknown binary string
1,i,strLen33555543=72,,,count,[],[1],40,0.92,True,
72,c,file_path,,,metadata,[33555543],[72],100,4.7,True,
10,b,,,,,[],[10],0,2.64,False,unknown binary string
1,i,strLen33555629=7248,,,count,[],[1],100,1.58,True,
7248,c,metadata,,,metadata,[33555629],[10],100,4.13,False,xml string
255,b,,,,,[],[255],0,4.41,False,unknown binary string
1,i,strLen33563136=10,,,count,[],[1],30,0.92,True,
10,c,,,,,[33563136],[10],30,2.95,False,Real Space
20,b,,,,,[],[20],0,3.0,False,unknown binary string
1,i,strLen33563170=9,,,count,[],[1],30,0.92,True,
9,c,,,,,[33563170],[9],30,3.0,False,Electrons
34,b,,,,,[],[34],0,2.53,False,unknown binary string
'''
