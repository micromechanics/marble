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
  k1 = readData(44, "1i")[0]
  addAttrs(6788, 52, hdfBranch, "displacement_label")
  addAttrs(5944, 40, hdfBranch, "force_label")
  addAttrs(8276, 64, hdfBranch, "process_name")
  addAttrs(11016, 32, hdfBranch, "some_name")
  addAttrs(26188, 273, hdfBranch, "path_name")
  addData(10559, str(k1)+"d", hdfBranch, "time", "s")
  addData(0, str(k1)+"f", hdfBranch, "displacement", "mm")
  addData(0, str(k1)+"f", hdfBranch, "force", "N")
  if os.path.getsize(fileNameIn)-fIn.tell()!=0:
    print("Translation NOT successful")
  else:
    print("Translation successful")

except:
  print("**ERROR** Exception in translation")



'''
# INFO: THIS PART IS LOADED BY MARBLE
# version= 1.0
# meta={"vendor": "", "label": "", "software": "", "ext": "mvl", "endian": "small"}
# periodicity={}
# length=509
length,dType,key,unit,link,dClass,count,prob,entropy,important,value
44,b,,,,,[],0,3.3841,False,b'unknown binary string'
1,i,k1=195,,,count,[],100,0.9183,True,b''
2319,B,,,,,[],10,0.0,False,b'unknown binary string'
457,b,,,,,[],0,0.0,False,b'unknown binary string'
32,B,,,,,[],10,0.0,False,b'Zeros 32'
128,b,,,,,[],0,2.069,False,b'unknown binary string'
130,B,,,,,[],10,0.0,False,b'Zeros 130'
19,b,,,,,[],0,0.9142,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
323,B,,,,,[],10,0.0,False,b'Zeros 323'
253,b,,,,,[],0,2.2706,False,b'unknown binary string'
67,B,,,,,[],10,0.0,False,b'Zeros 67'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
143,B,,,,,[],10,0.0,False,b'Zeros 143'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
175,B,,,,,[],10,0.0,False,b'Zeros 175'
1261,b,,,,,[],0,1.222,False,b'unknown binary string'
99,B,,,,,[],10,0.0,False,b'Zeros 99'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
143,B,,,,,[],10,0.0,False,b'Zeros 143'
328,b,,,,,[],0,1.5189,False,b'unknown binary string'
400,B,,,,,[],10,0.0,False,b'Zeros 400'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
16,B,,,,,[],10,0.0,False,b'Zeros 16'
8,b,,,,,[],0,2.1281,False,b'unknown binary string'
16,B,,,,,[],10,0.0,False,b'Zeros 16'
32,b,,,,,[],0,1.7609,False,b'unknown binary string'
16,B,,,,,[],10,0.0,False,b'Zeros 16'
32,b,,,,,[],0,1.6562,False,b'unknown binary string'
16,B,,,,,[],10,0.0,False,b'Zeros 16'
32,b,,,,,[],0,1.6604,False,b'unknown binary string'
18,B,,,,,[],10,0.0,False,b'Zeros 18'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
123,B,,,,,[],10,0.0,False,b'Zeros 123'
52,c,displacement_label,,,metadata,[],100,1.7606,True,b'Corr. Le in F0'
4,b,,,,,[],0,0.0,False,b'unknown binary string'
24,B,,,,,[],10,0.0,False,b'Zeros 24'
4,b,,,,,[],0,0.0,False,b'unknown binary string'
24,B,,,,,[],10,0.0,False,b'Zeros 24'
4,b,,,,,[],0,0.0,False,b'unknown binary string'
24,B,,,,,[],10,0.0,False,b'Zeros 24'
4,b,,,,,[],0,0.0,False,b'unknown binary string'
904,B,,,,,[],10,0.0,False,b'Zeros 904'
30,b,,,,,[],0,2.2336,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
6,b,,,,,[],0,1.9219,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
7,b,,,,,[],0,2.2516,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
37,b,,,,,[],0,1.0579,False,b'unknown binary string'
43,B,,,,,[],10,0.0,False,b'Zeros 43'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
31,B,,,,,[],10,0.0,False,b'Zeros 31'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
31,B,,,,,[],10,0.0,False,b'Zeros 31'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
29,B,,,,,[],10,0.0,False,b'Zeros 29'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
31,B,,,,,[],10,0.0,False,b'Zeros 31'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
31,B,,,,,[],10,0.0,False,b'Zeros 31'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
31,B,,,,,[],10,0.0,False,b'Zeros 31'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
31,B,,,,,[],10,0.0,False,b'Zeros 31'
9,b,,,,,[],0,2.75,False,b'unknown binary string'
184,B,,,,,[],10,0.0,False,b'Zeros 184'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
159,B,,,,,[],10,0.0,False,b'Zeros 159'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
30,B,,,,,[],10,0.0,False,b'Zeros 30'
2,b,,,,,[],0,0.0,False,b'unknown binary string'
199,B,,,,,[],10,0.0,False,b'Zeros 199'
119,b,,,,,[],0,2.5428,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
29,b,,,,,[],0,1.2988,False,b'unknown binary string'
215,B,,,,,[],10,0.0,False,b'Zeros 215'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
583,B,,,,,[],10,0.0,False,b'Zeros 583'
5,b,,,,,[],0,0.8113,False,b'unknown binary string'
703,B,,,,,[],10,0.0,False,b'Zeros 703'
96,b,,,,,[],0,2.8253,False,b'unknown binary string'
40,B,,,,,[],10,0.0,False,b'Zeros 40'
48,b,,,,,[],0,3.5331,False,b'unknown binary string'
696,B,,,,,[],10,0.0,False,b'Zeros 696'
5,b,,,,,[],0,1.5,False,b'unknown binary string'
139,B,,,,,[],10,0.0,False,b'Zeros 139'
12,b,,,,,[],0,2.0049,False,b'unknown binary string'
40,c,force_label,,,metadata,[],100,2.5151,True,b'Force/Width'
110,b,,,,,[],0,1.34,False,b'unknown binary string'
18,B,,,,,[],10,0.0,False,b'Zeros 18'
30,b,,,,,[],0,2.1318,False,b'unknown binary string'
18,B,,,,,[],10,0.0,False,b'Zeros 18'
30,b,,,,,[],0,2.1318,False,b'unknown binary string'
18,B,,,,,[],10,0.0,False,b'Zeros 18'
30,b,,,,,[],0,2.1318,False,b'unknown binary string'
18,B,,,,,[],10,0.0,False,b'Zeros 18'
78,b,,,,,[],0,2.0437,False,b'unknown binary string'
18,B,,,,,[],10,0.0,False,b'Zeros 18'
31,b,,,,,[],0,2.2716,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.3199,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.5736,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.3199,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.4817,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
31,b,,,,,[],0,2.5736,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
14,b,,,,,[],0,2.3535,False,b'unknown binary string'
2194,B,,,,,[],10,0.0,False,b'Zeros 2194'
83,b,,,,,[],0,4.5801,False,b'unknown binary string'
225,B,,,,,[],10,0.0,False,b'Zeros 225'
75,b,,,,,[],0,0.406,False,b'unknown binary string'
525,B,,,,,[],10,0.0,False,b'Zeros 525'
103,b,,,,,[],0,4.317,False,b'unknown binary string'
225,B,,,,,[],10,0.0,False,b'Zeros 225'
75,b,,,,,[],0,0.406,False,b'unknown binary string'
525,B,,,,,[],10,0.0,False,b'Zeros 525'
103,b,,,,,[],0,4.317,False,b'unknown binary string'
225,B,,,,,[],10,0.0,False,b'Zeros 225'
75,b,,,,,[],0,0.406,False,b'unknown binary string'
525,B,,,,,[],10,0.0,False,b'Zeros 525'
103,b,,,,,[],0,4.317,False,b'unknown binary string'
225,B,,,,,[],10,0.0,False,b'Zeros 225'
75,b,,,,,[],0,0.406,False,b'unknown binary string'
525,B,,,,,[],10,0.0,False,b'Zeros 525'
20,b,,,,,[],0,0.9133,False,b'unknown binary string'
261,B,,,,,[],10,0.0,False,b'Zeros 261'
14,b,,,,,[],0,1.1401,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
403,b,,,,,[],0,1.5513,False,b'unknown binary string'
39,B,,,,,[],10,0.0,False,b'Zeros 39'
77,b,,,,,[],0,1.7468,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
76,B,,,,,[],10,0.0,False,b'Zeros 76'
24,b,,,,,[],0,2.4343,False,b'unknown binary string'
64,c,process_name,,,metadata,[],100,3.166,True,b'Universal Tensile / Compression Test'
79,b,,,,,[],0,1.8184,False,b'unknown binary string'
257,B,,,,,[],10,0.0,False,b'Zeros 257'
19,b,,,,,[],0,1.6122,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
403,b,,,,,[],0,1.5513,False,b'unknown binary string'
39,B,,,,,[],10,0.0,False,b'Zeros 39'
77,b,,,,,[],0,1.7468,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
76,B,,,,,[],10,0.0,False,b'Zeros 76'
24,b,,,,,[],0,2.4343,False,b'unknown binary string'
64,c,,,,,[],40,3.166,False,b'Universal Tensile / Compression Test'
79,b,,,,,[],0,1.8184,False,b'unknown binary string'
257,B,,,,,[],10,0.0,False,b'Zeros 257'
19,b,,,,,[],0,1.6122,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
403,b,,,,,[],0,1.5513,False,b'unknown binary string'
39,B,,,,,[],10,0.0,False,b'Zeros 39'
77,b,,,,,[],0,1.7468,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
76,B,,,,,[],10,0.0,False,b'Zeros 76'
24,b,,,,,[],0,2.4343,False,b'unknown binary string'
64,c,,,,,[],40,3.166,False,b'Universal Tensile / Compression Test'
79,b,,,,,[],0,1.8184,False,b'unknown binary string'
257,B,,,,,[],10,0.0,False,b'Zeros 257'
19,b,,,,,[],0,1.6122,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
403,b,,,,,[],0,1.5513,False,b'unknown binary string'
39,B,,,,,[],10,0.0,False,b'Zeros 39'
77,b,,,,,[],0,1.7468,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
76,B,,,,,[],10,0.0,False,b'Zeros 76'
24,b,,,,,[],0,2.4343,False,b'unknown binary string'
64,c,,,,,[],40,3.166,False,b'Universal Tensile / Compression Test'
79,b,,,,,[],0,1.8184,False,b'unknown binary string'
257,B,,,,,[],10,0.0,False,b'Zeros 257'
19,b,,,,,[],0,1.6122,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
403,b,,,,,[],0,1.5513,False,b'unknown binary string'
39,B,,,,,[],10,0.0,False,b'Zeros 39'
77,b,,,,,[],0,1.7468,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
76,B,,,,,[],10,0.0,False,b'Zeros 76'
24,b,,,,,[],0,2.4343,False,b'unknown binary string'
64,c,,,,,[],40,3.166,False,b'Universal Tensile / Compression Test'
79,b,,,,,[],0,1.8184,False,b'unknown binary string'
257,B,,,,,[],10,0.0,False,b'Zeros 257'
19,b,,,,,[],0,1.6122,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
25,B,,,,,[],10,0.0,False,b'Zeros 25'
403,b,,,,,[],0,1.5513,False,b'unknown binary string'
39,B,,,,,[],10,0.0,False,b'Zeros 39'
77,b,,,,,[],0,1.7468,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
76,B,,,,,[],10,0.0,False,b'Zeros 76'
24,b,,,,,[],0,2.4343,False,b'unknown binary string'
64,c,,,,,[],40,3.166,False,b'Universal Tensile / Compression Test'
79,b,,,,,[],0,1.8184,False,b'unknown binary string'
260,B,,,,,[],10,0.0,False,b'Zeros 260'
33,b,,,,,[],0,3.4056,False,b'unknown binary string'
124,B,,,,,[],10,0.0,False,b'Zeros 124'
32,b,,,,,[],0,1.7249,False,b'unknown binary string'
91,B,,,,,[],10,0.0,False,b'Zeros 91'
189,b,,,,,[],0,2.5675,False,b'unknown binary string'
88,B,,,,,[],10,0.0,False,b'Zeros 88'
158,b,,,,,[],0,3.4956,False,b'unknown binary string'
78,B,,,,,[],10,0.0,False,b'Zeros 78'
172,b,,,,,[],0,2.438,False,b'unknown binary string'
144,B,,,,,[],10,0.0,False,b'Zeros 144'
158,b,,,,,[],0,3.4956,False,b'unknown binary string'
78,B,,,,,[],10,0.0,False,b'Zeros 78'
172,b,,,,,[],0,2.438,False,b'unknown binary string'
144,B,,,,,[],10,0.0,False,b'Zeros 144'
158,b,,,,,[],0,3.4956,False,b'unknown binary string'
78,B,,,,,[],10,0.0,False,b'Zeros 78'
172,b,,,,,[],0,2.438,False,b'unknown binary string'
144,B,,,,,[],10,0.0,False,b'Zeros 144'
20,b,,,,,[],0,1.3605,False,b'unknown binary string'
10,c,,,,,[],30,2.9477,False,b'Operator:'
4,b,,,,,[],0,1.585,False,b'unknown binary string'
10,c,,,,,[],30,2.9477,False,b'Material:'
4,b,,,,,[],0,1.585,False,b'unknown binary string'
170,c,,,,,[],32,0.6522,False,b'File name:'
20,b,,,,,[],0,0.0,False,b'unknown binary string'
182,B,,,,,[],10,0.0,False,b'Zeros 182'
11,b,,,,,[],0,2.9219,False,b'unknown binary string'
189,B,,,,,[],10,0.0,False,b'Zeros 189'
13,b,,,,,[],0,3.0221,False,b'unknown binary string'
195,B,,,,,[],10,0.0,False,b'Zeros 195'
10,b,,,,,[],0,1.88,False,b'unknown binary string'
386,B,,,,,[],10,0.0,False,b'Zeros 386'
6,b,,,,,[],0,1.5219,False,b'unknown binary string'
130,B,,,,,[],10,0.0,False,b'Zeros 130'
19,b,,,,,[],0,3.7255,False,b'unknown binary string'
17,B,,,,,[],10,0.0,False,b'Zeros 17'
5,b,,,,,[],0,0.0,False,b'unknown binary string'
41,B,,,,,[],10,0.0,False,b'Zeros 41'
62,b,,,,,[],0,1.5076,False,b'unknown binary string'
36,B,,,,,[],10,0.0,False,b'Zeros 36'
20,b,,,,,[],0,0.0,False,b'unknown binary string'
940,c,,,,,[],36,0.0563,False,b'Administrator'
68,b,,,,,[],0,0.0,False,b'unknown binary string'
268,B,,,,,[],10,0.0,False,b'Zeros 268'
8,b,,,,,[],0,0.8631,False,b'unknown binary string'
32,c,some_name,,,metadata,[],100,2.7412,True,"b'Tensile, Membrne'"
88,b,,,,,[],0,2.8479,False,b'unknown binary string'
560,B,,,,,[],10,0.0,False,b'Zeros 560'
4,b,,,,,[],0,0.9183,False,b'unknown binary string'
876,B,,,,,[],10,0.0,False,b'Zeros 876'
96,b,,,,,[],0,0.0,False,b'unknown binary string'
768,B,,,,,[],10,0.0,False,b'Zeros 768'
1040,c,,,,,[],40,0.0085,False,"b'Tensile, Membrane'"
397,b,,,,,[],0,1.0414,False,b'unknown binary string'
35,B,,,,,[],10,0.0,False,b'Zeros 35'
29,b,,,,,[],0,0.8113,False,b'unknown binary string'
1407,B,,,,,[],10,0.0,False,b'Zeros 1407'
642,b,,,,,[],0,1.6646,False,b'unknown binary string'
1906,B,,,,,[],10,0.0,False,b'Zeros 1906'
120,b,,,,,[],0,0.0,False,b'unknown binary string'
132,B,,,,,[],10,0.0,False,b'Zeros 132'
40,b,,,,,[],0,0.0,False,b'unknown binary string'
304,B,,,,,[],10,0.0,False,b'Zeros 304'
20,b,,,,,[],0,0.0,False,b'unknown binary string'
1888,B,,,,,[],10,0.0,False,b'Zeros 1888'
8,b,,,,,[],0,2.5216,False,b'unknown binary string'
24,B,,,,,[],10,0.0,False,b'Zeros 24'
32,c,,,,,[],34,2.3506,False,b'Batch number'
32,c,,,,,[],34,2.1327,False,b'Order number'
32,c,,,,,[],40,2.6316,False,b'Customer number'
8,b,,,,,[],0,2.8074,False,b'unknown binary string'
24,B,,,,,[],10,0.0,False,b'Zeros 24'
32,c,,,,,[],30,1.8497,False,b'Department'
32,c,,,,,[],34,2.2216,False,b'Additional 1'
32,c,,,,,[],34,2.2216,False,b'Additional 2'
32,c,,,,,[],34,2.2216,False,b'Additional 3'
32,c,,,,,[],34,2.2216,False,b'Additional 4'
32,c,,,,,[],34,2.2216,False,b'Additional 5'
32,c,,,,,[],34,2.2216,False,b'Additional 6'
32,c,,,,,[],34,2.2216,False,b'Additional 7'
32,c,,,,,[],34,2.2216,False,b'Additional 8'
32,c,,,,,[],34,2.2216,False,b'Additional 9'
32,c,,,,,[],36,2.4039,False,b'Additional 10'
32,c,,,,,[],36,2.3394,False,b'Additional 11'
32,c,,,,,[],36,2.4039,False,b'Additional 12'
32,c,,,,,[],36,2.4039,False,b'Additional 13'
32,c,,,,,[],36,2.4039,False,b'Additional 14'
32,c,,,,,[],36,2.4039,False,b'Additional 15'
32,c,,,,,[],36,2.4039,False,b'Additional 16'
32,c,,,,,[],36,2.4039,False,b'Additional 17'
32,c,,,,,[],36,2.4039,False,b'Additional 18'
960,c,,,,,[],36,0.0061,False,b'Additional 19'
32,b,,,,,[],0,1.2092,False,b'unknown binary string'
36,B,,,,,[],10,0.0,False,b'Zeros 36'
32,b,,,,,[],0,1.2092,False,b'unknown binary string'
2068,B,,,,,[],10,0.0,False,b'Zeros 2068'
64,b,,,,,[],0,1.8984,False,b'unknown binary string'
60,B,,,,,[],10,0.0,False,b'Zeros 60'
64,b,,,,,[],0,1.8984,False,b'unknown binary string'
60,B,,,,,[],10,0.0,False,b'Zeros 60'
64,b,,,,,[],0,1.8984,False,b'unknown binary string'
56,B,,,,,[],10,0.0,False,b'Zeros 56'
68,b,,,,,[],0,1.8656,False,b'unknown binary string'
56,B,,,,,[],10,0.0,False,b'Zeros 56'
68,b,,,,,[],0,1.8656,False,b'unknown binary string'
56,B,,,,,[],10,0.0,False,b'Zeros 56'
68,b,,,,,[],0,1.8656,False,b'unknown binary string'
56,B,,,,,[],10,0.0,False,b'Zeros 56'
87,b,,,,,[],0,2.4705,False,b'unknown binary string'
106,B,,,,,[],10,0.0,False,b'Zeros 106'
5,b,,,,,[],0,1.5,False,b'unknown binary string'
97,B,,,,,[],10,0.0,False,b'Zeros 97'
5,b,,,,,[],0,1.5,False,b'unknown binary string'
8420,B,,,,,[],10,0.0,False,b'Zeros 8420'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
75,B,,,,,[],10,0.0,False,b'Zeros 75'
15,b,,,,,[],0,2.4037,False,b'unknown binary string'
105,B,,,,,[],10,0.0,False,b'Zeros 105'
14,b,,,,,[],0,2.1888,False,b'unknown binary string'
106,B,,,,,[],10,0.0,False,b'Zeros 106'
14,b,,,,,[],0,1.8543,False,b'unknown binary string'
554,B,,,,,[],10,0.0,False,b'Zeros 554'
140,b,,,,,[],0,1.265,False,b'unknown binary string'
632,B,,,,,[],10,0.0,False,b'Zeros 632'
233,b,,,,,[],0,1.2461,False,b'unknown binary string'
155,B,,,,,[],10,0.0,False,b'Zeros 155'
72,c,,,,,[],40,2.0107,False,b'Membrane_Repeatability'
7,b,,,,,[],0,0.65,False,b'unknown binary string'
73,B,,,,,[],10,0.0,False,b'Zeros 73'
7,b,,,,,[],0,0.65,False,b'unknown binary string'
257,B,,,,,[],10,0.0,False,b'Zeros 257'
20,b,,,,,[],0,0.4855,False,b'unknown binary string'
273,c,path_name,,,metadata,[],100,1.4575,True,b''
20,b,,,,,[],0,0.0,False,b'unknown binary string'
259,B,,,,,[],10,0.0,False,b'Zeros 259'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
40,B,,,,,[],10,0.0,False,b'Zeros 40'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
26,B,,,,,[],10,0.0,False,b'Zeros 26'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
263,B,,,,,[],10,0.0,False,b'Zeros 263'
33,b,,,,,[],0,2.1417,False,b'unknown binary string'
107,B,,,,,[],10,0.0,False,b'Zeros 107'
237,b,,,,,[],0,1.5891,False,b'unknown binary string'
163,B,,,,,[],10,0.0,False,b'Zeros 163'
77,b,,,,,[],0,0.8113,False,b'unknown binary string'
5531,B,,,,,[],10,0.0,False,b'Zeros 5531'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
63,B,,,,,[],10,0.0,False,b'Zeros 63'
32,b,,,,,[],0,0.0,False,b'unknown binary string'
74,B,,,,,[],10,0.0,False,b'Zeros 74'
3,b,,,,,[],0,1.0,False,b'unknown binary string'
259,B,,,,,[],10,0.0,False,b'Zeros 259'
53,b,,,,,[],0,1.0983,False,b'unknown binary string'
311,B,,,,,[],10,0.0,False,b'Zeros 311'
53,b,,,,,[],0,1.0983,False,b'unknown binary string'
311,B,,,,,[],10,0.0,False,b'Zeros 311'
53,b,,,,,[],0,1.0983,False,b'unknown binary string'
1167,B,,,,,[],10,0.0,False,b'Zeros 1167'
13,b,,,,,[],0,1.2075,False,b'unknown binary string'
519,B,,,,,[],10,0.0,False,b'Zeros 519'
158,b,,,,,[],0,3.2511,False,b'unknown binary string'
58,B,,,,,[],10,0.0,False,b'Zeros 58'
57,b,,,,,[],0,2.6018,False,b'unknown binary string'
23,B,,,,,[],10,0.0,False,b'Zeros 23'
21,b,,,,,[],0,1.054,False,b'unknown binary string'
27,B,,,,,[],10,0.0,False,b'Zeros 27'
1,b,,,,,[],0,0.0,False,b'unknown binary string'
535,B,,,,,[],10,0.0,False,b'Zeros 535'
8,b,,,,,[],0,0.0,False,b'unknown binary string'
-1,d,time,s,,primary,[44],100,5.0265,True,b''
-1,f,displacement,mm,,primary,[44],100,5.0539,True,b''
-1,f,force,N,https://en.wikipedia.org/wiki/Force,primary,[44],100,4.1571,True,b'unknown binary string'
'''
