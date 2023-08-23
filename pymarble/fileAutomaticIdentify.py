"""All functions that identify content in binary file automatically"""
import math, struct, re, time, logging
from typing import Optional, Union
import xml.etree.ElementTree as ET
import numpy as np
from PySide6.QtWidgets import QWidget                            # pylint: disable=no-name-in-module
from .section import Section
from .fileClass import FileProtocol

class Automatic():
  """ Mixin that includes all functions that identify sections """
  def automatic(self:FileProtocol, methodOrder:str='x_z_p_a', start:int=-1, getMethods:bool=False,
                progress:Optional[QWidget]=None) -> Optional[dict[str,str]]:
    '''
    Wrapper that calls the different methods. This is generally the first step

    - x Search for a XML string
    - z Search for zero bytes (no information in them)
    - a Search for text / ascii bytes;
      Sometimes these results makes search for primary data impossible, use afterwards
    - p Search for primary data

    The default order is good for small time-series data-files

    Args:
      file
      methodOrder of methods: method order to be used.
    '''
    allMethods:dict[str,str] = {}
    if progress is not None:
      progress.setValue(2)
    for idx, method in enumerate(methodOrder.split('_')):
      if self.verbose>1:
        print("Start method",method)
        startTime = time.time()
      if getMethods:
        allMethods |= {'a': 'Search for text / ascii'}
      if method == 'a':
        # Runtime comparison for loop and map
        # map(lambda i: self.findAsciiSection(i) if self.content[i].dType=='b' else None, self.content)
        # map run time: 0m1.951s, 0m1.994s, 0m1.934s
        # for loop run time: 0m2.091s, 0m2.029s, 0m1.975s
        # for loop easy to read, keep for now
        for startI in self.content if start==-1 else [start]:
          if self.content[startI].dType=='b':
            self.findAsciiSection(startI)
      if getMethods:
        allMethods |= {'i': 'Search for image'}
      if method == 'i':
        for startI in self.content if start==-1 else [start]:
          self.find2DImage(start)
      if getMethods:
        allMethods |= {'p': 'Search for time series data'}
      if method == 'p':
        for startI in self.content if start==-1 else [start]:
          section = self.content[startI]
          if section.dType=='b' and \
              section.length>= self.optAutomatic['minArray']*4 and \
              section.entropy> self.optAutomatic['minEntropy']: #at least minArray 4byte size
            self.primaryTimeData(startI)
      if getMethods:
        allMethods |= {'x': 'Search for xml data'}
      if method == 'x':
        self.findXMLSection()
      if getMethods:
        allMethods |= {'z': 'Search for sections with zero values'}
      if method == 'z':
        self.findZeroSection(max(0, start))
      self.fill()
      if progress is not None:
        progress.setValue(int((idx+1)*100/len(methodOrder.split('_'))))
      if self.verbose>1:
        print(f'  End method {method}. Duration={str(round(time.time() - startTime))}sec')
    if progress is not None:
      progress.reset()
    return allMethods if getMethods else None


  def findZeroSection(self:FileProtocol, start:int=0) -> None:
    '''
    Find zeros in file and mark probability as low, to not block other entries

    Args:
      start: start position
    '''
    self.file.seek(start)
    dataBin = struct.unpack(f'{str(self.fileLength)}B', self.file.read())
    dataZero = np.where(np.array(dataBin)==0)[0]                  #where is zero
    dataConsecutive = np.split(dataZero, np.where(np.diff(dataZero)!=1)[0]+1) #find consecutive areas
    data = [ [i[0],len(i)] for i in dataConsecutive if len(i)>=self.optAutomatic['minZeros'] ]
    for i in data:
      section = Section(length=i[1], dType='B', value=f'Zeros {i[1]}', prob=10, entropy=0)
      self.content[i[0]] = section
    return


  def findAsciiSection(self:FileProtocol, start:int) -> None:
    '''
    Find sections of Ascii letters in file

    Args:
      start: start position of section
    '''
    self.file.seek(start)
    data = bytearray(self.file.read(self.content[start].byteSize()))
    found = False
    # REMOVED \d in next re
    for i in re.finditer(b'[\w\.\ \\\/;:,]{'+str.encode(str(self.optAutomatic['minChars']))+b',}',data): #pylint: disable=anomalous-backslash-in-string
      [startI, endI], text = i.span(), i[0].decode('utf-8')
      nonZero = np.where(np.array(data[endI:])>0)[0]  #add trailing zeros
      if len(nonZero)>0:
        endI += nonZero[0]
      prob = 10+min(len(text)*2, 30)
      self.content[start+startI] = Section(length=endI-startI, dType='c', value=text, prob=prob)
      if startI>0:
        found = True
    if found:  #if found, remove parent
      del self.content[start]
    return


  def findXMLSection(self:FileProtocol) -> None:
    '''
    Find xml sections in file
    '''
    self.file.seek(0)
    data = bytearray(self.file.read(self.fileLength))
    xmlStartIterator = re.finditer(b'<\w+>'   ,data) #pylint: disable=anomalous-backslash-in-string
    xmlStartList = [(i.start(),i.end(),i.group()) for i in xmlStartIterator]
    if not xmlStartList:
      logging.info("no xml string found")
      return
    xmlStart = xmlStartList[0]
    xmlEndIterator = re.finditer(b'<\/\w+>' ,data) #pylint: disable=anomalous-backslash-in-string
    xmlEndList = [(i.start(),i.end(),i.group())   for i in xmlEndIterator]
    if not xmlEndList:
      return
    xmlEnd = xmlEndList[-1]
    if xmlStart[2][1:] == xmlEnd[2][2:] and xmlStart[1]<xmlEnd[0]:
      try:
        xmlString = data[xmlStart[0]:xmlEnd[1]]
        _ = ET.fromstring(xmlString)
      except ET.ParseError:
        logging.error('XML incorrect:\n%s\n',xmlString)
      self.content[xmlStart[0]]=Section(length=xmlEnd[1]-xmlStart[0], dType='c', value='xml string',
                                        key='metadata', dClass='metadata', prob=100)
      del self.content[0]
    return


  def useExportedFile(self:FileProtocol, exportedFile:str) -> bool:
    '''
    Using exported file, try to find those occurrences in binary file. Zero at beginning taking
    somewhat into account. Difficult to account for trailing zeros since those difficult to
    differentiate from garbage

    return to zero at end

    crop first zeros since finding them is problematic:
    - too many occurrences
    - difficult to evaluate error

    Args:
        exportedFile: file name of exported file: has to be np.loadtxt readable

    Returns:
        bool: success
    '''
    # #identify number separators, decimal separators
    # with open(exportedFile,'r', encoding='ISO-8859-1') as fIn:
    #   text = fIn.read()
    #   numLines = text.count('\n')
    #   relComma = text.count(',')/float(numLines)
    #   relPoint = text.count('.')/float(numLines)
    #   relSemicolon = text.count(';')/float(numLines)
    #   relTab = text.count('\t')/float(numLines)
    #   fIn.close()
    # print("Info file: num. lines:",numLines,'rel. ","',relComma,'rel. "."',relPoint,
    #   'rel. ";"',relSemicolon,'rel. tab',relTab)
    # if relComma>0.99 and relTab>0.99:
    #   print('  Tab separated numbers with ,-decimal')
    # if relPoint>0.99 and relTab>0.99:
    #   print('  Tab separated numbers with .-decimal')
    # if relPoint>0.99 and relComma>0.99:
    #   print('  ,-separated numbers with .-decimal. CSV file')
    #load data
    dataTXT = np.loadtxt(exportedFile)
    lenData = dataTXT.shape[0]
    for col in range(dataTXT.shape[1]):
      idxMax = np.argmax(dataTXT[:,col])
      valMax = dataTXT[idxMax,col]
      # Above change allowed fot test script to run successfully.
      if self.verbose>1:
        print('\nStart with column:',col,' max. value:',valMax)
      bestOffset, bestMax, bestDType = None, None, None
      for dType in ['d','f']:
        offsetsMax = self.findValue(valMax, dType, False, 0)
        for offsetMax in [int(i) for i in offsetsMax]:
          start = offsetMax - int(idxMax*struct.calcsize(dType))
          end   = offsetMax + (lenData-idxMax)*struct.calcsize(dType)
          if start<0 or end>self.fileLength:
            continue
          self.file.seek(start)
          dataBin = self.file.read(struct.calcsize(str(lenData)+dType))
          dataBINARY = np.array(struct.unpack(str(lenData)+dType, dataBin))
          maxDiff = np.max(dataBINARY-dataTXT[:,col])
          if bestMax is None or abs(maxDiff)<abs(bestMax):
            bestOffset, bestMax, bestDType = start, maxDiff, dType
      if bestOffset is None or bestMax is None or bestDType is None:
        logging.error('no fitting best value found')
        return False
      prob = bestMax/valMax if bestDType=='d' else (bestMax/valMax)**2
      prob = min( int(np.log10(1./prob)*3+50), 90) #probability has max. value of 90
      if self.verbose>1:
        print(f'  Best fit: dType={bestDType} start={bestOffset} length={lenData} end=',
              f'{bestOffset+struct.calcsize(str(lenData)+bestDType)-1}, probability={prob}')
      # create link / enter property count; adopt shape correspondingly
      count=[self.findAnchor(lenData, bestOffset)[0]]
      section = Section(length=lenData, dType=bestDType, value=f'from exported data column {col+1}',
        prob=prob, count=count, shape=[lenData], dClass='primary')
      self.content[bestOffset] = section
    return True


  def findStreak(self:FileProtocol, dType:str='d', start:int=0) -> None:
    '''
    Go through the file and try to read numbers,
      if make sense continue reading
      go only forward

    do not move to array based because this function is not that slow

    Args:
      dType: ['d','i'] data-type: double or int
      start: offset at which to start / start-position of section
    '''
    self.file.seek(start)
    diffToStart = np.array(list(self.content), dtype=int)-start
    diffToStart = diffToStart[diffToStart<=0][-1]  #take last that is negative
    startSection= start+diffToStart
    endSection  = startSection+self.content[startSection].byteSize()
    found = []
    #go forward
    while True:
      data  = self.file.read(struct.calcsize(dType))
      if len(data)<struct.calcsize(dType) or self.file.tell()>=endSection:
        if self.verbose>1:
          print('Find streak: reached end of file')
        break
      try:
        value = struct.unpack(dType, data)[0]
        baseD = 0.0 if value == 0.0 else abs(math.log10(abs(value)))
      except Exception as ex:
        logging.error('Exception at %s| %s',self.pretty(self.file.tell()), ex)
        baseD = 999
      if baseD<self.optAutomatic['maxExp'] or value==0.0:
        found.append(value)
      else:
        if self.verbose>1:
          logging.error('Failed at value, baseD %s, %s',value, baseD)
        break
      if start in self.content and self.file.tell() > start+self.content[start].length:
        break
    #
    if self.verbose>1:
      print(f'{start} - {self.pretty(self.file.tell())}: streak of dType={dType}, length={len(found)}')
    self.content[start] = Section(length=len(found), value=f'streak of dType={dType}, length={len(found)}',
                                  dType=dType, prob=20)
    return


  def primaryTimeData(self:FileProtocol, start:int=0) -> None:
    '''
    Go through the file and read numbers based on if they and next numbers make sense

    Unknown: could be garbage

    Return to zero at the end

    Args:
      start: offset at which to start / start-position of section
    '''
    #move start backward if zeros before that
    length = self.content[start].byteSize()
    startInit = start
    starts = list(self.content)
    idx = starts.index(start)
    sectionBefore = self.content[starts[idx-1]]
    if sectionBefore.dType == 'B':
      start -= min(16, sectionBefore.byteSize())
      start = max(0, start)
      length+= min(16, sectionBefore.byteSize())
    #start process
    self.file.seek(start)
    data = self.file.read(length)
    found = False
    while True:
      numData = math.floor(len(data)/8)               #double is largest, use it to determine max. size
      if numData==0:                                  #stop if nothing left
        break
      tempData = data[:struct.calcsize(f'{str(numData)}d')]
      valuesD = np.array(struct.unpack(f'{str(numData)}d', tempData))
      valuesF = np.array(struct.unpack(f'{str(numData * 2)}f', tempData))
      maskD    = np.abs(np.log10(np.abs(valuesD)))  < self.optAutomatic['maxExp']
      maskF    = np.abs(np.log10(np.abs(valuesF)))  < self.optAutomatic['maxExp']
      maskD    = np.logical_or(maskD, valuesD==0)
      maskF    = np.logical_or(maskF, valuesF==0)
      lenD     = np.where(~maskD)[0][0] if np.any(~maskD) else len(maskD) #first value that is true
      lenF     = np.where(~maskF)[0][0] if np.any(~maskF) else len(maskF)
      if lenD>lenF and lenD>=self.optAutomatic['minArray']:
        mean    = np.mean(valuesD[:lenD])
        minimum = np.min(valuesD[:lenD])
        maximum = np.max(valuesD[:lenD])
        label = f'{lenD} doubles with mean {mean:.3e}, minimum {minimum:.3e}, maximum {maximum:.3e} '
        if self.verbose>1:
          print(f'{self.pretty(start)} - {self.pretty(start+lenD*8)} double| {label}')
        self.content[start] = Section(length=lenD, dType='d', value=label, prob=20, dClass='primary')
        found = True
        data = data[lenD*8:]
        start+= lenD*8
      elif lenF>lenD and lenF>=self.optAutomatic['minArray']:
        mean    = np.mean(valuesF[:lenF])
        minimum = np.min(valuesF[:lenF])
        maximum = np.max(valuesF[:lenF])
        label = f'{lenF} floats with mean {mean:.3e}, minimum {minimum:.3e}, maximum {maximum:.3e} '
        if self.verbose>1:
          print(f'{self.pretty(start)} - {self.pretty(start+lenF*4)} float | {label}')
        self.content[start] = Section(length=lenF,dType='f', value=label, prob=20, dClass='primary')
        found = True
        data = data[lenF*4:]
        start+= lenF*4
      else:
        data = data[1:]
        start += 1
    if found:
      del self.content[startInit]
    return


  def entropy(self:FileProtocol, start:int=-1, average:bool=True) -> Union[float,list[float]]:
    '''
    inspired by but not more than inspired by
    - http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html

    Hints:
    - entropy < 3.3 metadata et al
    - entropy > 4 real data

    Args:
      start (int): starting position of section; if -1 is given use entire file
      average (bool): return avelage value or all-values

    Return:
      entropy
    '''
    results = []
    blockSize = self.optEntropy['blockSize']
    if start in self.content:
      self.file.seek(start)
      dataBin = self.file.read( self.content[start].byteSize() )  #read data
      data = struct.unpack(f'{self.content[start].byteSize()}B', dataBin) #convert to byte-int
      blockSize = min(blockSize, self.content[start].byteSize()-1)
      skipEvery = max(self.optEntropy['skipEvery'], int(self.content[start].byteSize()/1024))#max. of 1024tests
    else:
      self.file.seek(0)
      dataBin = self.file.read()  #read data
      data = struct.unpack(f'{self.fileLength}B', dataBin) #convert to byte-int
      skipEvery = self.optEntropy['skipEvery']
    startPoints = np.arange(0,len(data)-blockSize,skipEvery)
    for startI in startPoints:
      _, counts = np.unique(data[startI:startI+blockSize], return_counts=True)
      counts    = counts/blockSize
      yValue    = np.sum(-counts*np.log2(counts))
      results.append(yValue)
    if start in self.content:
      self.content[start].entropy = np.average(results)
    elif self.verbose>0:
      print('Average entropy:', np.round(np.average(results),4))
    return np.average(results) if average else results


  def find2DImage(self:FileProtocol, start:int) -> None:
    '''
    find a 2D image in section with this start and label accordingly

    Args:
      start: starting position of section; if none is given use entire file
    '''
    section = self.content[start]
    foundLocations = {}
    for exponent in range(8,13):
      for bit in ['H','b']:
        dimension = 2**exponent
        imgSize = struct.calcsize(f'{dimension**2}{bit}')
        sizeByLength = imgSize /  section.length
        if 0.1 < sizeByLength < 1.5:
          if dimension not in foundLocations:
            locations = np.array([int(i) for i  in self.findValue(dimension,'i',False,0)], dtype=np.int32)
            foundLocations[dimension] = locations
          else:
            locations = foundLocations[dimension]
          if np.any(np.logical_and(np.diff(locations)>=4, np.diff(locations)<= 400)):
            startData = np.max(locations)+4
            # self.file.seek(startData)
            # data = struct.unpack(f'{dimension**2}{bit}', self.file.read(imgSize)) # read and convert
            # use first two locations, if more than 2 are found
            img = Section(length=dimension**2, dType=bit, value='automatically identified image',
                          dClass='primary', count=list(locations[:2]), shape=[dimension, dimension], prob=99)
            self.content[startData] = img
            # create anchors
            prevKvariables = 0
            for startJ in self.content:
              sectionJ = self.content[startJ]
              if re.search(r'^k\d+=', sectionJ.key) and sectionJ.dType=='i':
                prevKvariables += 1
            self.content[locations[0]] = Section(length=1, key=f'k{prevKvariables+1}={dimension}',
                                                 dType='i', prob=100, dClass='count', important=True)
            self.content[locations[1]] = Section(length=1, key=f'k{prevKvariables+2}={dimension}',
                                                 dType='i', prob=100, dClass='count', important=True)
            del self.content[start]
            break
    return
