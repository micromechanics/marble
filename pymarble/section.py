"""Section of data"""
from __future__ import annotations
import logging, struct
from typing import Union, Optional, Any
import numpy as np

# length: length of section, responsible for size, byteSize of section
#   - generally length = shape[0]*shape[1]
#   - in case garbage (malloc) is in section: length is larger than product of shape
# dClass: metadata, primary, count/parameter, ''=unknown
# count: offset/location of the count
#   - relates to the shape
#   - cannot be the variable name because formalized description should not have variable name
# shape: shape of array for primary data
#   - linear vector is turned into shape
#   - each primary data should have one.
#   - however, not really needed since count says it all
#     benefit is only the ability for user to supply shape

# prob = probability: 0, 25, 50,75, 100 = 1-5 stars!
#   - 0 unidentified
#   - 10 sequences of 00 or FF
#   - 40-60 ascii strings: the longer the higher with cutoff at 10-long;
#           ascii stings include the following 00
#   - 40-60 sequences: tho longer the higher: cutoff at 100-long
#   - 100   if manually set key,unit,link
# entropy -> see automaticIdentify:entropy
SECTION_OUTPUT_ORDER = ['length','dType','key','unit','link','dClass','count','shape','prob','entropy',\
                        'important','value']

class Section:
  """
  class that represents each identified section of data
  """
  def __init__(self, length:int=0, dType:str='', key:str='', unit:str='', value:str='', link:str='',
               dClass:str='', count:list[int]=[], shape:list[int]=[], prob:int=0, entropy:float=-1.0,
               important:bool=False, data:Union[str,dict[str,str]]=''):
    # structural properties
    self.dType     = dType
    self.dClass    = dClass
    self.length    = length
    self.shape     = shape
    self.count     = count
    # content properties
    self.key       = key
    self.unit      = unit
    self.link      = link
    self.value     = value
    self.prob      = prob
    self.entropy   = entropy
    self.important = important
    if data:
      self.setData(data)
    # set shape if unset
    if not self.shape and self.length>0:
      if self.dType=='c' and self.value!='':
        self.shape=[len(self.value)]
      else:
        self.shape=[self.length]
    return


  def setData(self, data:Union[str,dict[str,str]]='', count:list[int]=[], dClass:str='', shape:list[int]=[]) \
    -> None:
    '''
    Change values

    Args:
       data (str,dict): string of | separated list with possible spaces
       count: where are the anchor points to find the size of the array
       dClass: data class: metadata, primary, count, ''
       shape: shape of the array

    '''
    if isinstance(data, str):
      dataList = [i.strip() for i in data.split('|')]
      for idx, name in enumerate(SECTION_OUTPUT_ORDER):
        if idx<len(dataList) and len(dataList[idx])>0:
          if isinstance( getattr(self,name), list):
            content = dataList[idx]
            if len(content)>0:
              setattr(self, name, [int(i) for i in content.split(',')] )
          elif isinstance( getattr(self,name), bool) and isinstance(dataList[idx],str):
            setattr(self, name, dataList[idx]=='True' )
          elif isinstance( getattr(self,name), (int,np.int64)):
            setattr(self, name, int(dataList[idx]))
          elif isinstance( getattr(self,name), float):
            setattr(self, name, float(dataList[idx]))
          else:
            setattr(self, name, dataList[idx])
    else:
      for key,value in data.items():
        setattr(self,key, value)
    #add shape if not given
    if ((SECTION_OUTPUT_ORDER.index('shape')>=len(dataList) > 1) or self.shape==[]) and self.length>0:
      self.shape=[self.length]
    #overwrite with manual given ones
    if count:
      self.count = count
    if shape:
      self.shape = shape
    if dClass:
      self.dClass = dClass
    return


  def __repr__(self) -> str:
    '''
    Used for print(Section) or str(Section)
    - use |-system for easy to reading
    - complete data
    - is the text label in the .tags file
    '''
    strList = [str(i) for i in self.toList()]
    return '|'.join( strList )


  def toCSV(self) -> dict[str,Union[str,int,float,bool]]:
    '''
    Return dictionary for csv format for header of .py file
    - used for save/load of structure information
    '''
    return {i:getattr(self,i) for i in SECTION_OUTPUT_ORDER}


  def toList(self) -> list[str]:
    '''
    Return list of all arguments
    - used for printing of table
    - clean output before printing / saving in .tags file
    '''
    localCopy = self.__dict__.copy()
    localCopy['entropy'] = f"{localCopy['entropy']:.2f}"     #Prevent issues with diff in tags file
    localCopy['count'] = str(localCopy['count'])[1:-1]
    localCopy['shape'] = str(localCopy['shape'])[1:-1]
    return [localCopy[i] for i in SECTION_OUTPUT_ORDER]


  def toPY(self, offset:int, lastOffset:int, variable:str='', binaryFile:Any=None, hdf:Optional[str]=None) \
    -> Optional[str]:
    '''
    Return one-line string in python format for body of .py file
    - not used for save/load of structure information

    Args:
      offset: current start position
      lastOffset: last offset position
      variable: variable used to this section
      binaryFile: to get list of content from calling entity
      hdf: hdf5Branch to save into
    '''
    if hdf is None:
      hdf = 'fOut'
    if self.dType in ['b','B']:
      return None
    relPos = offset - lastOffset
    if self.dType=='c' or self.dClass=='metadata':
      length = str(self.length) if self.dType=='c' else f'"{self.size()}"'  #default: char or
      key = self.key.replace(':','_')
      return f'addAttrs({relPos}, {length}, {hdf}, "{key}' + '")\n'
    if self.dType=='i':
      variable = variable or self.key.split('=')[0]
      return f'{variable} = readData({relPos}, "{self.size()}' + '")[0]\n'
    if binaryFile is None:
      return ''
    content = binaryFile.content
    #if data with dTypes: d,f,H
    if len(self.shape) in {0,1} and len(self.count)==1  and np.prod(self.shape)==self.length:
      #default case: shape (un)identified and one count
      variable = content[self.count[0]].key.split('=')[0]
      metadata = {'unit':self.unit, 'link':self.link}
      return f'addData({relPos}, f"{{{variable}}}{self.dType}", {hdf}, "{self.key}", "{metadata}")\n'
    if len(self.shape) == len(self.count) and np.prod(self.shape)==self.length:
      #case: image with x,y count and shape
      variables = [str(self.shape[idx]) if i==-1 else content[i].key.split('=')[0]
                   for idx,i in enumerate(self.count)]
      prodVariables = '*'.join(variables)
      metadata = {'unit':self.unit, 'link':self.link}
      if offset in binaryFile.rowFormatSegments:
        metadata = {'description': 'data in columns; metadata in corresponding lists',
                    'labels': [i['key'] for i in binaryFile.rowFormatMeta],   # type: ignore[dict-item]
                    'units':  [i['unit'] for i in binaryFile.rowFormatMeta],  # type: ignore[dict-item]
                    'links':  [i['link'] for i in binaryFile.rowFormatMeta]}  # type: ignore[dict-item]
      return f'addData({relPos}, f"{{{prodVariables}}}{self.dType}", {hdf}, "{self.key}", "{metadata}", '\
               f'shape=[{",".join(variables)}])\n'
    if len(self.shape)>0 and len(self.shape)==len(self.count) and self.length>np.prod(self.shape):
      #garbage case: lots of garbage behind real data specified by shape
      variables = ['x' if i<0 else content[i].key.split('=')[0] for i in self.count]
      metadata = {'unit':self.unit, 'link':self.link}
      return f'addData({relPos}, f"{{{self.length}}}{self.dType}", {hdf}, "{self.key}", "{metadata}", '\
               f'shape=[{",".join(variables)}])\n'
    #output anyhow: user has to adopt it
    logging.error(".py file has bad code: shape %s, count %s, length %s", self.shape,self.count,self.length)
    metadata = {'unit':self.unit, 'link':self.link}
    return f'addData({relPos}, f"{{{self.length}}}{self.dType}", {hdf}, "{self.key}", "{metadata}", '\
             f'shape=[...])  #Adopt this line\n'


  def byteSize(self) -> int:
    '''
    return the byte size of this item
    '''
    if self.dType=='':
      return -1
    return struct.calcsize(str(self.length)+self.dType)


  def size(self) -> str:
    '''
    return the size string: e.g. 600d
    '''
    return str(self.length)+self.dType


  @staticmethod
  def pythonHeader() -> str:
    '''
    Python header including all python function since
    - they depend on which properties in the section exist (e.g. links)
    - these functions are called by the output of toPY()
    '''
    return """

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
      hdfBranch.attrs[key] = value.replace('\\x00','')
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

"""
