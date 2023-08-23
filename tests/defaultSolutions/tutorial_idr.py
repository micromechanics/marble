#!/usr/bin/python3
# INFO: THIS PART IS IS FOR HUMANS BUT IT IS IGNORED BY MARBLE
'''
convert  idr to .hdf5 file

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

convURI = b'https://raw.githubusercontent.com/main/cwl/idr2hdf.cwl'
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
  numberOfTests = readData(0, "1i")[0]
  fIn.seek(0)
  addAttrs(0, "1i", fOut, "peridicity_count")
  for idxTest in range(numberOfTests):
    hdfBranch_ = fOut.create_group("test_"+str(idxTest+1))
    hdfBranch_.attrs["NX_class"] = b"NXentry"
    hdfBranch = hdfBranch_.create_group("data")
    hdfBranch.attrs["NX_class"] = b"NXdata"
    addAttrs(0, "1i", hdfBranch, "cycle_number")
    k1 = readData(0, "1i")[0]
    addAttrs(0, "1i", hdfBranch, "index_end_loading")
    addData(0, f"{4000}d", hdfBranch, "force", "{'unit': 'mN', 'link': ''}", shape=[k1])
    addData(0, f"{4000}d", hdfBranch, "displacement", "{'unit': 'nm', 'link': ''}", shape=[k1])
    addData(0, f"{4000}d", hdfBranch, "time", "{'unit': 's', 'link': ''}", shape=[k1])
  if os.path.getsize(fileNameIn)-fIn.tell()!=0:
    print("Translation NOT successful")
  else:
    print("Translation successful")

except:
  print("**ERROR** Exception in translation")



'''
# INFO: THIS PART IS LOADED BY MARBLE
# version= 1.0
# meta={"vendor": "", "label": "", "software": "", "ext": "idr", "endian": "small"}
# periodicity={"count": 0, "start": 4, "end": 64016}
# rowFormatMeta=[]
# rowFormatSegments=[]
# length=170
length,dType,key,unit,link,dClass,count,shape,prob,entropy,important,value
1,i,peridicity:count,,,count,[],[1],100,1.15,True,unknown binary string
1,i,cycle_number,,,metadata,[],[1],100,0.92,True,unknown binary string
1,i,k1=1562,,,count,[],[1],100,1.58,True,
1,i,index_end_loading,,,metadata,[],[1],100,1.58,True,unknown binary string
4000,d,force,mN,,primary,[8],[1562],100,6.15,True,
4000,d,displacement,nm,,primary,[8],[1562],100,6.32,True,unknown binary string
4000,d,time,s,,primary,[8],[1562],100,0.0,True,unknown binary string
12,b,,,,,[],[12],0,2.05,False,unknown binary string
1584,d,,,,primary,[],[1584],20,6.08,False,"1584 doubles with mean 1.032e+02, minimum -1.175e-02, maximum 2.096e+02"
24,b,,,,,[],[24],0,3.15,False,unknown binary string
20,B,,,,,[],[20],10,0.0,False,Zeros 20
8,b,,,,,[],[8],0,1.56,False,unknown binary string
60,B,,,,,[],[60],10,0.0,False,Zeros 60
28,b,,,,,[],[28],0,2.36,False,unknown binary string
36,B,,,,,[],[36],10,0.0,False,Zeros 36
240,b,,,,,[],[240],0,4.23,False,unknown binary string
32,B,,,,,[],[32],10,0.0,False,Zeros 32
2922,b,,,,,[],[2922],0,4.77,False,unknown binary string
374,B,,,,,[],[374],10,0.0,False,Zeros 374
28,b,,,,,[],[28],0,2.36,False,unknown binary string
108,B,,,,,[],[108],10,0.0,False,Zeros 108
4,b,,,,,[],[4],0,1.58,False,unknown binary string
244,B,,,,,[],[244],10,0.0,False,Zeros 244
111,b,,,,,[],[111],0,4.25,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
4072,b,,,,,[],[4072],0,4.55,False,unknown binary string
21,c,,,,,[],[20],40,3.45,False,added messageToFIFO
67,b,,,,,[],[67],0,4.33,False,unknown binary string
22,c,,,,,[],[22],40,3.88,False,CInterface::AddNewByte
2,b,,,,,[],[2],0,0.0,False,unknown binary string
41,c,,,,,[],[20],40,4.29,False,added messageToFIFO
539,b,,,,,[],[539],0,3.74,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
1424,b,,,,,[],[1424],0,4.37,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,CInterface::readLine
2,b,,,,,[],[2],0,0.0,False,unknown binary string
14,c,,,,,[],[13],36,2.82,False,COM_NO_ERROR
72,b,,,,,[],[72],0,4.38,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,CInterface::readLine
2,b,,,,,[],[2],0,0.0,False,unknown binary string
33,c,,,,,[],[13],36,3.69,False,COM_NO_ERROR
660,b,,,,,[],[660],0,4.58,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1239,b,,,,,[],[1239],0,4.17,False,unknown binary string
35,c,,,,,[],[35],40,4.24,False,CPiGcs2Functions::ReadStringCommand
1253,b,,,,,[],[1253],0,4.44,False,unknown binary string
2007,c,,,,,[],[13],36,1.7,False,eitForSocket
2938,b,,,,,[],[2938],0,0.0,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
316,b,,,,,[],[316],0,4.04,False,unknown binary string
28,B,,,,,[],[28],10,0.0,False,Zeros 28
40,b,,,,,[],[40],0,2.82,False,unknown binary string
20,B,,,,,[],[20],10,0.0,False,Zeros 20
136,b,,,,,[],[136],0,4.41,False,unknown binary string
1584,d,,,,primary,[],[1584],20,6.32,False,"1584 doubles with mean 7.415e+02, minimum -4.305e+02, maximum 1.014e+03"
19488,B,,,,,[],[19497],10,0.0,False,Zeros 19488
1563,d,,,,primary,[],[1563],20,5.92,False,"1563 doubles with mean 4.938e+01, minimum 0.000e+00, maximum 1.244e+02"
13664,B,,,,,[],[13680],10,0.0,False,Zeros 13664
661,d,,,,primary,[],[661],20,6.29,False,"661 doubles with mean 3.246e-01, minimum 0.000e+00, maximum 4.177e-01"
384,B,,,,,[],[384],10,0.0,False,Zeros 384
12,b,,,,,[],[12],0,2.05,False,unknown binary string
1584,d,,,,primary,[],[1584],20,6.16,False,"1584 doubles with mean 9.821e+01, minimum -1.175e-02, maximum 2.046e+02"
24,b,,,,,[],[24],0,3.15,False,unknown binary string
20,B,,,,,[],[20],10,0.0,False,Zeros 20
8,b,,,,,[],[8],0,1.56,False,unknown binary string
60,B,,,,,[],[60],10,0.0,False,Zeros 60
28,b,,,,,[],[28],0,2.36,False,unknown binary string
36,B,,,,,[],[36],10,0.0,False,Zeros 36
240,b,,,,,[],[240],0,4.23,False,unknown binary string
32,B,,,,,[],[32],10,0.0,False,Zeros 32
2922,b,,,,,[],[2922],0,4.77,False,unknown binary string
374,B,,,,,[],[374],10,0.0,False,Zeros 374
28,b,,,,,[],[28],0,2.36,False,unknown binary string
108,B,,,,,[],[108],10,0.0,False,Zeros 108
4,b,,,,,[],[4],0,1.58,False,unknown binary string
244,B,,,,,[],[244],10,0.0,False,Zeros 244
111,b,,,,,[],[111],0,4.25,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
4048,b,,,,,[],[4048],0,4.55,False,unknown binary string
22,c,,,,,[],[22],40,3.88,False,CInterface::AddNewByte
2,b,,,,,[],[2],0,0.0,False,unknown binary string
21,c,,,,,[],[20],40,3.45,False,added messageToFIFO
67,b,,,,,[],[67],0,4.33,False,unknown binary string
22,c,,,,,[],[22],40,3.88,False,CInterface::AddNewByte
2,b,,,,,[],[2],0,0.0,False,unknown binary string
41,c,,,,,[],[20],40,4.29,False,added messageToFIFO
539,b,,,,,[],[539],0,3.74,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
1424,b,,,,,[],[1424],0,4.37,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,CInterface::readLine
2,b,,,,,[],[2],0,0.0,False,unknown binary string
14,c,,,,,[],[13],36,2.82,False,COM_NO_ERROR
72,b,,,,,[],[72],0,4.38,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,CInterface::readLine
2,b,,,,,[],[2],0,0.0,False,unknown binary string
33,c,,,,,[],[13],36,3.69,False,COM_NO_ERROR
660,b,,,,,[],[660],0,4.58,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1239,b,,,,,[],[1239],0,4.12,False,unknown binary string
35,c,,,,,[],[35],40,4.24,False,CPiGcs2Functions::ReadStringCommand
1253,b,,,,,[],[1253],0,4.44,False,unknown binary string
2007,c,,,,,[],[13],36,1.7,False,eitForSocket
2938,b,,,,,[],[2938],0,0.0,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
316,b,,,,,[],[316],0,4.05,False,unknown binary string
28,B,,,,,[],[28],10,0.0,False,Zeros 28
40,b,,,,,[],[40],0,2.82,False,unknown binary string
20,B,,,,,[],[20],10,0.0,False,Zeros 20
136,b,,,,,[],[136],0,4.25,False,unknown binary string
1584,d,,,,primary,[],[1584],20,6.32,False,"1584 doubles with mean 7.322e+02, minimum -4.114e+02, maximum 1.011e+03"
19488,B,,,,,[],[19497],10,0.0,False,Zeros 19488
1563,d,,,,primary,[],[1563],20,5.92,False,"1563 doubles with mean 1.721e+02, minimum 0.000e+00, maximum 5.132e+03"
13664,B,,,,,[],[13680],10,0.0,False,Zeros 13664
661,d,,,,primary,[],[661],20,6.29,False,"661 doubles with mean 3.246e-01, minimum 0.000e+00, maximum 4.177e-01"
384,B,,,,,[],[384],10,0.0,False,Zeros 384
12,b,,,,,[],[12],0,2.05,False,unknown binary string
1584,d,,,,primary,[],[1584],20,6.16,False,"1584 doubles with mean 9.545e+01, minimum -1.100e-02, maximum 2.016e+02"
24,b,,,,,[],[24],0,3.15,False,unknown binary string
20,B,,,,,[],[20],10,0.0,False,Zeros 20
8,b,,,,,[],[8],0,1.56,False,unknown binary string
60,B,,,,,[],[60],10,0.0,False,Zeros 60
28,b,,,,,[],[28],0,2.36,False,unknown binary string
36,B,,,,,[],[36],10,0.0,False,Zeros 36
240,b,,,,,[],[240],0,4.23,False,unknown binary string
32,B,,,,,[],[32],10,0.0,False,Zeros 32
2922,b,,,,,[],[2922],0,4.77,False,unknown binary string
374,B,,,,,[],[374],10,0.0,False,Zeros 374
28,b,,,,,[],[28],0,2.36,False,unknown binary string
108,B,,,,,[],[108],10,0.0,False,Zeros 108
4,b,,,,,[],[4],0,1.58,False,unknown binary string
244,B,,,,,[],[244],10,0.0,False,Zeros 244
111,b,,,,,[],[111],0,4.25,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
4048,b,,,,,[],[4048],0,4.55,False,unknown binary string
22,c,,,,,[],[22],40,3.88,False,CInterface::AddNewByte
2,b,,,,,[],[2],0,0.0,False,unknown binary string
21,c,,,,,[],[20],40,3.45,False,added messageToFIFO
67,b,,,,,[],[67],0,4.33,False,unknown binary string
22,c,,,,,[],[22],40,3.88,False,CInterface::AddNewByte
2,b,,,,,[],[2],0,0.0,False,unknown binary string
41,c,,,,,[],[20],40,4.29,False,added messageToFIFO
539,b,,,,,[],[539],0,3.74,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
1424,b,,,,,[],[1424],0,4.37,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,CInterface::readLine
2,b,,,,,[],[2],0,0.0,False,unknown binary string
14,c,,,,,[],[13],36,2.82,False,COM_NO_ERROR
72,b,,,,,[],[72],0,4.38,False,unknown binary string
20,c,,,,,[],[20],40,3.58,False,CInterface::readLine
2,b,,,,,[],[2],0,0.0,False,unknown binary string
33,c,,,,,[],[13],36,3.69,False,COM_NO_ERROR
660,b,,,,,[],[660],0,4.58,False,unknown binary string
17,B,,,,,[],[17],10,0.0,False,Zeros 17
1239,b,,,,,[],[1239],0,4.12,False,unknown binary string
35,c,,,,,[],[35],40,4.24,False,CPiGcs2Functions::ReadStringCommand
1253,b,,,,,[],[1253],0,4.44,False,unknown binary string
2007,c,,,,,[],[13],36,1.7,False,eitForSocket
2938,b,,,,,[],[2938],0,0.0,False,unknown binary string
16,B,,,,,[],[16],10,0.0,False,Zeros 16
316,b,,,,,[],[316],0,4.05,False,unknown binary string
28,B,,,,,[],[28],10,0.0,False,Zeros 28
40,b,,,,,[],[40],0,2.82,False,unknown binary string
20,B,,,,,[],[20],10,0.0,False,Zeros 20
136,b,,,,,[],[136],0,4.34,False,unknown binary string
1584,d,,,,primary,[],[1584],20,6.32,False,"1584 doubles with mean 7.349e+02, minimum -4.551e+02, maximum 1.014e+03"
19488,B,,,,,[],[19498],10,0.0,False,Zeros 19488
1563,d,,,,primary,[],[1563],20,5.91,False,"1563 doubles with mean 2.484e+02, minimum 0.000e+00, maximum 5.289e+03"
13664,B,,,,,[],[13680],10,0.0,False,Zeros 13664
661,d,,,,primary,[],[661],20,6.29,False,"661 doubles with mean 3.246e-01, minimum 0.000e+00, maximum 4.177e-01"
384,B,,,,,[],[384],10,0.0,False,Zeros 384
'''
