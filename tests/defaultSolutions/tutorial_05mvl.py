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
import struct, sys, os, hashlib, json
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
  k1 = readData(44, "1i")[0]
  addAttrs(6788, 52, hdfBranch, "displacement_label")
  addAttrs(5944, 40, hdfBranch, "force_label")
  addAttrs(8276, 64, hdfBranch, "process_name")
  addAttrs(11016, 32, hdfBranch, "some_name")
  addAttrs(26188, 273, hdfBranch, "path_name")
  addData(10559, f"{k1}d", hdfBranch, "time", "{'unit': 's', 'link': ''}")
  addData(0, f"{k1}f", hdfBranch, "displacement", "{'unit': 'mm', 'link': ''}")
  addData(0, f"{k1}f", hdfBranch, "force", "{'unit': 'N', 'link': 'https://en.wikipedia.org/wiki/Force'}")
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
# rowFormatMeta=[]
# rowFormatSegments=[]
# length=509
length,dType,key,unit,link,dClass,count,shape,prob,entropy,important,value
44,b,,,,,[],[72400],0,3.38,False,unknown binary string
1,i,k1=195,,,count,[],[1],100,0.92,True,
2319,B,,,,,[],[2323],10,0.0,False,unknown binary string
457,b,,,,,[],[457],0,0.0,False,unknown binary string
32,B,,,,,[],[32],10,0.0,False,Zeros 32
128,b,,,,,[],[128],0,2.07,False,unknown binary string
130,B,,,,,[],[130],10,0.0,False,Zeros 130
19,b,,,,,[],[19],0,0.91,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
323,B,,,,,[],[323],10,0.0,False,Zeros 323
253,b,,,,,[],[253],0,2.27,False,unknown binary string
67,B,,,,,[],[67],10,0.0,False,Zeros 67
1,b,,,,,[],[1],0,0.0,False,unknown binary string
143,B,,,,,[],[143],10,0.0,False,Zeros 143
1,b,,,,,[],[1],0,0.0,False,unknown binary string
175,B,,,,,[],[175],10,0.0,False,Zeros 175
1261,b,,,,,[],[1261],0,1.22,False,unknown binary string
99,B,,,,,[],[99],10,0.0,False,Zeros 99
1,b,,,,,[],[1],0,0.0,False,unknown binary string
143,B,,,,,[],[143],10,0.0,False,Zeros 143
328,b,,,,,[],[328],0,1.52,False,unknown binary string
400,B,,,,,[],[400],10,0.0,False,Zeros 400
6,b,,,,,[],[6],0,1.92,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
8,b,,,,,[],[8],0,2.13,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
32,b,,,,,[],[32],0,1.76,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
32,b,,,,,[],[32],0,1.66,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
32,b,,,,,[],[32],0,1.66,False,unknown binary string
18,B,,,,,[],[18],10,0.0,False,Zeros 18
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
1,b,,,,,[],[1],0,0.0,False,unknown binary string
123,B,,,,,[],[123],10,0.0,False,Zeros 123
52,c,displacement_label,,,metadata,[],[52],100,1.76,True,Corr. Le in F0
4,b,,,,,[],[4],0,0.0,False,unknown binary string
24,B,,,,,[],[24],10,0.0,False,Zeros 24
4,b,,,,,[],[4],0,0.0,False,unknown binary string
24,B,,,,,[],[24],10,0.0,False,Zeros 24
4,b,,,,,[],[4],0,0.0,False,unknown binary string
24,B,,,,,[],[24],10,0.0,False,Zeros 24
4,b,,,,,[],[4],0,0.0,False,unknown binary string
904,B,,,,,[],[904],10,0.0,False,Zeros 904
30,b,,,,,[],[30],0,2.23,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
6,b,,,,,[],[6],0,1.92,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
7,b,,,,,[],[7],0,2.25,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
37,b,,,,,[],[37],0,1.06,False,unknown binary string
43,B,,,,,[],[43],10,0.0,False,Zeros 43
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
1,b,,,,,[],[1],0,0.0,False,unknown binary string
31,B,,,,,[],[31],10,0.0,False,Zeros 31
1,b,,,,,[],[1],0,0.0,False,unknown binary string
31,B,,,,,[],[31],10,0.0,False,Zeros 31
3,b,,,,,[],[3],0,1.0,False,unknown binary string
29,B,,,,,[],[29],10,0.0,False,Zeros 29
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
1,b,,,,,[],[1],0,0.0,False,unknown binary string
31,B,,,,,[],[31],10,0.0,False,Zeros 31
1,b,,,,,[],[1],0,0.0,False,unknown binary string
31,B,,,,,[],[31],10,0.0,False,Zeros 31
1,b,,,,,[],[1],0,0.0,False,unknown binary string
31,B,,,,,[],[31],10,0.0,False,Zeros 31
1,b,,,,,[],[1],0,0.0,False,unknown binary string
31,B,,,,,[],[31],10,0.0,False,Zeros 31
9,b,,,,,[],[9],0,2.75,False,unknown binary string
184,B,,,,,[],[184],10,0.0,False,Zeros 184
1,b,,,,,[],[1],0,0.0,False,unknown binary string
159,B,,,,,[],[159],10,0.0,False,Zeros 159
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
30,B,,,,,[],[30],10,0.0,False,Zeros 30
2,b,,,,,[],[2],0,0.0,False,unknown binary string
199,B,,,,,[],[199],10,0.0,False,Zeros 199
119,b,,,,,[],[119],0,2.54,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
29,b,,,,,[],[29],0,1.3,False,unknown binary string
215,B,,,,,[],[215],10,0.0,False,Zeros 215
1,b,,,,,[],[1],0,0.0,False,unknown binary string
583,B,,,,,[],[583],10,0.0,False,Zeros 583
5,b,,,,,[],[5],0,0.81,False,unknown binary string
703,B,,,,,[],[703],10,0.0,False,Zeros 703
96,b,,,,,[],[96],0,2.83,False,unknown binary string
40,B,,,,,[],[40],10,0.0,False,Zeros 40
48,b,,,,,[],[48],0,3.53,False,unknown binary string
696,B,,,,,[],[696],10,0.0,False,Zeros 696
5,b,,,,,[],[5],0,1.5,False,unknown binary string
139,B,,,,,[],[139],10,0.0,False,Zeros 139
12,b,,,,,[],[12],0,2.0,False,unknown binary string
40,c,force_label,,,metadata,[],[40],100,2.52,True,Force/Width
110,b,,,,,[],[110],0,1.34,False,unknown binary string
18,B,,,,,[],[18],10,0.0,False,Zeros 18
30,b,,,,,[],[30],0,2.13,False,unknown binary string
18,B,,,,,[],[18],10,0.0,False,Zeros 18
30,b,,,,,[],[30],0,2.13,False,unknown binary string
18,B,,,,,[],[18],10,0.0,False,Zeros 18
30,b,,,,,[],[30],0,2.13,False,unknown binary string
18,B,,,,,[],[18],10,0.0,False,Zeros 18
78,b,,,,,[],[78],0,2.04,False,unknown binary string
18,B,,,,,[],[18],10,0.0,False,Zeros 18
31,b,,,,,[],[31],0,2.27,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.32,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.57,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.32,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.48,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
31,b,,,,,[],[31],0,2.57,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
14,b,,,,,[],[14],0,2.35,False,unknown binary string
2194,B,,,,,[],[2194],10,0.0,False,Zeros 2194
83,b,,,,,[],[83],0,4.58,False,unknown binary string
225,B,,,,,[],[225],10,0.0,False,Zeros 225
75,b,,,,,[],[75],0,0.41,False,unknown binary string
525,B,,,,,[],[525],10,0.0,False,Zeros 525
103,b,,,,,[],[103],0,4.32,False,unknown binary string
225,B,,,,,[],[225],10,0.0,False,Zeros 225
75,b,,,,,[],[75],0,0.41,False,unknown binary string
525,B,,,,,[],[525],10,0.0,False,Zeros 525
103,b,,,,,[],[103],0,4.32,False,unknown binary string
225,B,,,,,[],[225],10,0.0,False,Zeros 225
75,b,,,,,[],[75],0,0.41,False,unknown binary string
525,B,,,,,[],[525],10,0.0,False,Zeros 525
103,b,,,,,[],[103],0,4.32,False,unknown binary string
225,B,,,,,[],[225],10,0.0,False,Zeros 225
75,b,,,,,[],[75],0,0.41,False,unknown binary string
525,B,,,,,[],[525],10,0.0,False,Zeros 525
20,b,,,,,[],[20],0,0.91,False,unknown binary string
261,B,,,,,[],[261],10,0.0,False,Zeros 261
14,b,,,,,[],[14],0,1.14,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1,b,,,,,[],[1],0,0.0,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
403,b,,,,,[],[403],0,1.55,False,unknown binary string
39,B,,,,,[],[39],10,0.0,False,Zeros 39
77,b,,,,,[],[77],0,1.75,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
8,b,,,,,[],[8],0,0.0,False,unknown binary string
76,B,,,,,[],[76],10,0.0,False,Zeros 76
24,b,,,,,[],[24],0,2.43,False,unknown binary string
64,c,process_name,,,metadata,[],[64],100,3.17,True,Universal Tensile / Compression Test
79,b,,,,,[],[79],0,1.82,False,unknown binary string
257,B,,,,,[],[257],10,0.0,False,Zeros 257
19,b,,,,,[],[19],0,1.61,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1,b,,,,,[],[1],0,0.0,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
403,b,,,,,[],[403],0,1.55,False,unknown binary string
39,B,,,,,[],[39],10,0.0,False,Zeros 39
77,b,,,,,[],[77],0,1.75,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
8,b,,,,,[],[8],0,0.0,False,unknown binary string
76,B,,,,,[],[76],10,0.0,False,Zeros 76
24,b,,,,,[],[24],0,2.43,False,unknown binary string
64,c,,,,,[],[36],40,3.17,False,Universal Tensile / Compression Test
79,b,,,,,[],[79],0,1.82,False,unknown binary string
257,B,,,,,[],[257],10,0.0,False,Zeros 257
19,b,,,,,[],[19],0,1.61,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1,b,,,,,[],[1],0,0.0,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
403,b,,,,,[],[403],0,1.55,False,unknown binary string
39,B,,,,,[],[39],10,0.0,False,Zeros 39
77,b,,,,,[],[77],0,1.75,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
8,b,,,,,[],[8],0,0.0,False,unknown binary string
76,B,,,,,[],[76],10,0.0,False,Zeros 76
24,b,,,,,[],[24],0,2.43,False,unknown binary string
64,c,,,,,[],[36],40,3.17,False,Universal Tensile / Compression Test
79,b,,,,,[],[79],0,1.82,False,unknown binary string
257,B,,,,,[],[257],10,0.0,False,Zeros 257
19,b,,,,,[],[19],0,1.61,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1,b,,,,,[],[1],0,0.0,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
403,b,,,,,[],[403],0,1.55,False,unknown binary string
39,B,,,,,[],[39],10,0.0,False,Zeros 39
77,b,,,,,[],[77],0,1.75,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
8,b,,,,,[],[8],0,0.0,False,unknown binary string
76,B,,,,,[],[76],10,0.0,False,Zeros 76
24,b,,,,,[],[24],0,2.43,False,unknown binary string
64,c,,,,,[],[36],40,3.17,False,Universal Tensile / Compression Test
79,b,,,,,[],[79],0,1.82,False,unknown binary string
257,B,,,,,[],[257],10,0.0,False,Zeros 257
19,b,,,,,[],[19],0,1.61,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1,b,,,,,[],[1],0,0.0,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
403,b,,,,,[],[403],0,1.55,False,unknown binary string
39,B,,,,,[],[39],10,0.0,False,Zeros 39
77,b,,,,,[],[77],0,1.75,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
8,b,,,,,[],[8],0,0.0,False,unknown binary string
76,B,,,,,[],[76],10,0.0,False,Zeros 76
24,b,,,,,[],[24],0,2.43,False,unknown binary string
64,c,,,,,[],[36],40,3.17,False,Universal Tensile / Compression Test
79,b,,,,,[],[79],0,1.82,False,unknown binary string
257,B,,,,,[],[257],10,0.0,False,Zeros 257
19,b,,,,,[],[19],0,1.61,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1,b,,,,,[],[1],0,0.0,False,unknown binary string
25,B,,,,,[],[25],10,0.0,False,Zeros 25
403,b,,,,,[],[403],0,1.55,False,unknown binary string
39,B,,,,,[],[39],10,0.0,False,Zeros 39
77,b,,,,,[],[77],0,1.75,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
8,b,,,,,[],[8],0,0.0,False,unknown binary string
76,B,,,,,[],[76],10,0.0,False,Zeros 76
24,b,,,,,[],[24],0,2.43,False,unknown binary string
64,c,,,,,[],[36],40,3.17,False,Universal Tensile / Compression Test
79,b,,,,,[],[79],0,1.82,False,unknown binary string
260,B,,,,,[],[260],10,0.0,False,Zeros 260
33,b,,,,,[],[33],0,3.41,False,unknown binary string
124,B,,,,,[],[124],10,0.0,False,Zeros 124
32,b,,,,,[],[32],0,1.72,False,unknown binary string
91,B,,,,,[],[91],10,0.0,False,Zeros 91
189,b,,,,,[],[189],0,2.57,False,unknown binary string
88,B,,,,,[],[88],10,0.0,False,Zeros 88
158,b,,,,,[],[158],0,3.5,False,unknown binary string
78,B,,,,,[],[78],10,0.0,False,Zeros 78
172,b,,,,,[],[172],0,2.44,False,unknown binary string
144,B,,,,,[],[144],10,0.0,False,Zeros 144
158,b,,,,,[],[158],0,3.5,False,unknown binary string
78,B,,,,,[],[78],10,0.0,False,Zeros 78
172,b,,,,,[],[172],0,2.44,False,unknown binary string
144,B,,,,,[],[144],10,0.0,False,Zeros 144
158,b,,,,,[],[158],0,3.5,False,unknown binary string
78,B,,,,,[],[78],10,0.0,False,Zeros 78
172,b,,,,,[],[172],0,2.44,False,unknown binary string
144,B,,,,,[],[144],10,0.0,False,Zeros 144
20,b,,,,,[],[20],0,1.36,False,unknown binary string
10,c,,,,,[],[10],30,2.95,False,Operator:
4,b,,,,,[],[4],0,1.58,False,unknown binary string
10,c,,,,,[],[10],30,2.95,False,Material:
4,b,,,,,[],[4],0,1.58,False,unknown binary string
170,c,,,,,[],[11],32,0.65,False,File name:
20,b,,,,,[],[20],0,0.0,False,unknown binary string
182,B,,,,,[],[182],10,0.0,False,Zeros 182
11,b,,,,,[],[11],0,2.92,False,unknown binary string
189,B,,,,,[],[189],10,0.0,False,Zeros 189
13,b,,,,,[],[13],0,3.02,False,unknown binary string
195,B,,,,,[],[195],10,0.0,False,Zeros 195
10,b,,,,,[],[10],0,1.88,False,unknown binary string
386,B,,,,,[],[386],10,0.0,False,Zeros 386
6,b,,,,,[],[6],0,1.52,False,unknown binary string
130,B,,,,,[],[130],10,0.0,False,Zeros 130
19,b,,,,,[],[19],0,3.73,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
5,b,,,,,[],[5],0,0.0,False,unknown binary string
41,B,,,,,[],[41],10,0.0,False,Zeros 41
62,b,,,,,[],[62],0,1.51,False,unknown binary string
36,B,,,,,[],[36],10,0.0,False,Zeros 36
20,b,,,,,[],[20],0,0.0,False,unknown binary string
940,c,,,,,[],[13],36,0.06,False,Administrator
68,b,,,,,[],[68],0,0.0,False,unknown binary string
268,B,,,,,[],[268],10,0.0,False,Zeros 268
8,b,,,,,[],[8],0,0.86,False,unknown binary string
32,c,some_name,,,metadata,[],[32],100,2.74,True,"Tensile, Membrne"
88,b,,,,,[],[88],0,2.85,False,unknown binary string
560,B,,,,,[],[560],10,0.0,False,Zeros 560
4,b,,,,,[],[4],0,0.92,False,unknown binary string
876,B,,,,,[],[876],10,0.0,False,Zeros 876
96,b,,,,,[],[96],0,0.0,False,unknown binary string
768,B,,,,,[],[768],10,0.0,False,Zeros 768
1040,c,,,,,[],[17],40,0.01,False,"Tensile, Membrane"
397,b,,,,,[],[397],0,1.04,False,unknown binary string
35,B,,,,,[],[35],10,0.0,False,Zeros 35
29,b,,,,,[],[29],0,0.81,False,unknown binary string
1407,B,,,,,[],[1407],10,0.0,False,Zeros 1407
642,b,,,,,[],[642],0,1.66,False,unknown binary string
1906,B,,,,,[],[1906],10,0.0,False,Zeros 1906
120,b,,,,,[],[120],0,0.0,False,unknown binary string
132,B,,,,,[],[132],10,0.0,False,Zeros 132
40,b,,,,,[],[40],0,0.0,False,unknown binary string
304,B,,,,,[],[304],10,0.0,False,Zeros 304
20,b,,,,,[],[20],0,0.0,False,unknown binary string
1888,B,,,,,[],[1888],10,0.0,False,Zeros 1888
8,b,,,,,[],[8],0,2.52,False,unknown binary string
24,B,,,,,[],[24],10,0.0,False,Zeros 24
32,c,,,,,[],[12],34,2.35,False,Batch number
32,c,,,,,[],[12],34,2.13,False,Order number
32,c,,,,,[],[15],40,2.63,False,Customer number
8,b,,,,,[],[8],0,2.81,False,unknown binary string
24,B,,,,,[],[24],10,0.0,False,Zeros 24
32,c,,,,,[],[10],30,1.85,False,Department
32,c,,,,,[],[12],34,2.22,False,Additional 1
32,c,,,,,[],[12],34,2.22,False,Additional 2
32,c,,,,,[],[12],34,2.22,False,Additional 3
32,c,,,,,[],[12],34,2.22,False,Additional 4
32,c,,,,,[],[12],34,2.22,False,Additional 5
32,c,,,,,[],[12],34,2.22,False,Additional 6
32,c,,,,,[],[12],34,2.22,False,Additional 7
32,c,,,,,[],[12],34,2.22,False,Additional 8
32,c,,,,,[],[12],34,2.22,False,Additional 9
32,c,,,,,[],[13],36,2.4,False,Additional 10
32,c,,,,,[],[13],36,2.34,False,Additional 11
32,c,,,,,[],[13],36,2.4,False,Additional 12
32,c,,,,,[],[13],36,2.4,False,Additional 13
32,c,,,,,[],[13],36,2.4,False,Additional 14
32,c,,,,,[],[13],36,2.4,False,Additional 15
32,c,,,,,[],[13],36,2.4,False,Additional 16
32,c,,,,,[],[13],36,2.4,False,Additional 17
32,c,,,,,[],[13],36,2.4,False,Additional 18
960,c,,,,,[],[13],36,0.01,False,Additional 19
32,b,,,,,[],[32],0,1.21,False,unknown binary string
36,B,,,,,[],[36],10,0.0,False,Zeros 36
32,b,,,,,[],[32],0,1.21,False,unknown binary string
2068,B,,,,,[],[2068],10,0.0,False,Zeros 2068
64,b,,,,,[],[64],0,1.9,False,unknown binary string
60,B,,,,,[],[60],10,0.0,False,Zeros 60
64,b,,,,,[],[64],0,1.9,False,unknown binary string
60,B,,,,,[],[60],10,0.0,False,Zeros 60
64,b,,,,,[],[64],0,1.9,False,unknown binary string
56,B,,,,,[],[56],10,0.0,False,Zeros 56
68,b,,,,,[],[68],0,1.87,False,unknown binary string
56,B,,,,,[],[56],10,0.0,False,Zeros 56
68,b,,,,,[],[68],0,1.87,False,unknown binary string
56,B,,,,,[],[56],10,0.0,False,Zeros 56
68,b,,,,,[],[68],0,1.87,False,unknown binary string
56,B,,,,,[],[56],10,0.0,False,Zeros 56
87,b,,,,,[],[87],0,2.47,False,unknown binary string
106,B,,,,,[],[106],10,0.0,False,Zeros 106
5,b,,,,,[],[5],0,1.5,False,unknown binary string
97,B,,,,,[],[97],10,0.0,False,Zeros 97
5,b,,,,,[],[5],0,1.5,False,unknown binary string
8420,B,,,,,[],[8420],10,0.0,False,Zeros 8420
1,b,,,,,[],[1],0,0.0,False,unknown binary string
75,B,,,,,[],[75],10,0.0,False,Zeros 75
15,b,,,,,[],[15],0,2.4,False,unknown binary string
105,B,,,,,[],[105],10,0.0,False,Zeros 105
14,b,,,,,[],[14],0,2.19,False,unknown binary string
106,B,,,,,[],[106],10,0.0,False,Zeros 106
14,b,,,,,[],[14],0,1.85,False,unknown binary string
554,B,,,,,[],[554],10,0.0,False,Zeros 554
140,b,,,,,[],[140],0,1.26,False,unknown binary string
632,B,,,,,[],[632],10,0.0,False,Zeros 632
233,b,,,,,[],[233],0,1.25,False,unknown binary string
155,B,,,,,[],[155],10,0.0,False,Zeros 155
72,c,,,,,[],[22],40,2.01,False,Membrane_Repeatability
7,b,,,,,[],[7],0,0.65,False,unknown binary string
73,B,,,,,[],[73],10,0.0,False,Zeros 73
7,b,,,,,[],[7],0,0.65,False,unknown binary string
257,B,,,,,[],[257],10,0.0,False,Zeros 257
20,b,,,,,[],[20],0,0.49,False,unknown binary string
273,c,path_name,,,metadata,[],[273],100,1.46,True,
20,b,,,,,[],[20],0,0.0,False,unknown binary string
259,B,,,,,[],[259],10,0.0,False,Zeros 259
1,b,,,,,[],[1],0,0.0,False,unknown binary string
40,B,,,,,[],[40],10,0.0,False,Zeros 40
1,b,,,,,[],[1],0,0.0,False,unknown binary string
26,B,,,,,[],[26],10,0.0,False,Zeros 26
1,b,,,,,[],[1],0,0.0,False,unknown binary string
263,B,,,,,[],[263],10,0.0,False,Zeros 263
33,b,,,,,[],[33],0,2.14,False,unknown binary string
107,B,,,,,[],[107],10,0.0,False,Zeros 107
237,b,,,,,[],[237],0,1.59,False,unknown binary string
163,B,,,,,[],[163],10,0.0,False,Zeros 163
77,b,,,,,[],[77],0,0.81,False,unknown binary string
5531,B,,,,,[],[5531],10,0.0,False,Zeros 5531
1,b,,,,,[],[1],0,0.0,False,unknown binary string
63,B,,,,,[],[63],10,0.0,False,Zeros 63
32,b,,,,,[],[32],0,0.0,False,unknown binary string
74,B,,,,,[],[74],10,0.0,False,Zeros 74
3,b,,,,,[],[3],0,1.0,False,unknown binary string
259,B,,,,,[],[259],10,0.0,False,Zeros 259
53,b,,,,,[],[53],0,1.1,False,unknown binary string
311,B,,,,,[],[311],10,0.0,False,Zeros 311
53,b,,,,,[],[53],0,1.1,False,unknown binary string
311,B,,,,,[],[311],10,0.0,False,Zeros 311
53,b,,,,,[],[53],0,1.1,False,unknown binary string
1167,B,,,,,[],[1167],10,0.0,False,Zeros 1167
13,b,,,,,[],[13],0,1.21,False,unknown binary string
519,B,,,,,[],[519],10,0.0,False,Zeros 519
158,b,,,,,[],[158],0,3.25,False,unknown binary string
58,B,,,,,[],[58],10,0.0,False,Zeros 58
57,b,,,,,[],[57],0,2.6,False,unknown binary string
23,B,,,,,[],[23],10,0.0,False,Zeros 23
21,b,,,,,[],[21],0,1.05,False,unknown binary string
27,B,,,,,[],[27],10,0.0,False,Zeros 27
1,b,,,,,[],[1],0,0.0,False,unknown binary string
535,B,,,,,[],[545],10,0.0,False,Zeros 535
8,b,,,,,[],[8],0,0.0,False,unknown binary string
195,d,time,s,,primary,[44],[195],100,5.03,True,
195,f,displacement,mm,,primary,[44],[195],100,5.05,True,
195,f,force,N,https://en.wikipedia.org/wiki/Force,primary,[44],[195],100,4.16,True,unknown binary string
'''
