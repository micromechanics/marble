"""All functions that identify content in binary file automatically"""
import math, struct, re, time
import xml.etree.ElementTree as ET
import numpy as np
from .section import Section
from .binFile_ import BinaryFileProtocol

class Mixin_Automatic():
  def automatic(self:BinaryFileProtocol, methodOrder:str='x_z_p_a') -> None:
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
    if len(self.content)>1:
      print("**ERROR: do not use automatic if content already exists")
      return
    for method in methodOrder.split('_'):
      if self.verbose>1:
        print("Start method",method)
        startTime = time.time()
      if method=='x':
        self.findXMLSection()
      elif method=='z':
        self.findZeroSection(0)
      elif method=='a':
        # Runtime comparison for loop and map
        # map(lambda i: self.findAsciiSection(i) if self.content[i].dType=='b' else None, self.content)
        # map run time: 0m1.951s, 0m1.994s, 0m1.934s
        # for loop run time: 0m2.091s, 0m2.029s, 0m1.975s
        # for loop easy to read, keep for now
        for startI in self.content:
          if self.content[startI].dType=='b':
            self.findAsciiSection(startI)
      elif method=='p':
        for startI in self.content:
          section = self.content[startI]
          if section.dType=='b' and \
            section.length>= self.optAutomatic['minArray']*4 and \
            section.entropy> self.optAutomatic['minEntropy']: #at least minArray 4byte size
            self.primaryTimeData(startI)
      self.fill()
      if self.verbose>1:
        print("  End method "+method+". Duration="+str(round(time.time()-startTime))+'sec')
    return


  def findZeroSection(self:BinaryFileProtocol, start:int=0) -> None:
    '''
    Find zeros in file and mark probability as low, to not block other entries

    Args:
      start: start position
    '''
    self.file.seek(start)
    dataBin = struct.unpack( str(self.fileLength)+'B', self.file.read())
    dataZero = np.where(np.array(dataBin)==0)[0]                  #where is zero
    dataConsecutive = np.split(dataZero, np.where(np.diff(dataZero)!=1)[0]+1) #find consecutive areas
    data = [ [i[0],len(i)] for i in dataConsecutive if len(i)>=self.optAutomatic['minZeros'] ]
    for i in data:
      section = Section(length=i[1], dType='B', value='Zeros '+str(i[1]), prob=10, entropy=0)
      self.content[i[0]] = section
    return


  def findAsciiSection(self:BinaryFileProtocol, start:int) -> None:
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


  def findXMLSection(self:BinaryFileProtocol) -> None:
    '''
    Find xml sections in file
    '''
    self.file.seek(0)
    data = bytearray(self.file.read(self.fileLength))
    xmlStartIterator = re.finditer(b'<\w+>'   ,data) #pylint: disable=anomalous-backslash-in-string
    xmlStartList = [(i.start(),i.end(),i.group()) for i in xmlStartIterator]
    if len(xmlStartList)==0:
      print("**INFO: no xml string found")
      return
    xmlStart = xmlStartList[0]
    xmlEndIterator = re.finditer(b'<\/\w+>' ,data) #pylint: disable=anomalous-backslash-in-string
    xmlEnd = [(i.start(),i.end(),i.group())   for i in xmlEndIterator][-1] #if start exist, end should too
    if xmlStart[2][1:] == xmlEnd[2][2:] and xmlStart[1]<xmlEnd[0]:
      try:
        xmlString = data[xmlStart[0]:xmlEnd[1]]
        _ = ET.fromstring(xmlString)
      except ET.ParseError:
        print("XML incorrect:\n",xmlString,'\n')
      self.content[xmlStart[0]]=Section(length=xmlEnd[1]-xmlStart[0], dType='c', value='xml string',
                                        key='metadata', dClass='meta', prob=100)
      del self.content[0]
    return


  def useExportedFile(self:BinaryFileProtocol, exportedFile:str) -> None:
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
    '''
    #identify number separators, decimal separators
    fIn = open(exportedFile,'r')
    text = fIn.read()
    numLines = text.count('\n')
    relComma = text.count(',')/float(numLines)
    relPoint = text.count('.')/float(numLines)
    relSemicolon = text.count(';')/float(numLines)
    relTab = text.count('\t')/float(numLines)
    fIn.close()
    print("Info file: num. lines:",numLines,'rel. ","',relComma,'rel. "."',relPoint,
      'rel. ";"',relSemicolon,'rel. tab',relTab)
    if relComma>0.99 and relTab>0.99:
      print('  Tab separated numbers with ,-decimal')
    if relPoint>0.99 and relTab>0.99:
      print('  Tab separated numbers with .-decimal')
    if relPoint>0.99 and relComma>0.99:
      print('  ,-separated numbers with .-decimal. CSV file')

    #load data
    dataTXT = np.loadtxt(exportedFile)
    lenData = dataTXT.shape[0]
    # find count: location where the count is saved
    count = self.findBytes(lenData, 'i',0)
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
      print(col)
      if bestOffset is None or bestMax is None or bestDType is None:
        print('**ERROR no fitting best value found')
        return
      prob = bestMax/valMax if bestDType=='d' else (bestMax/valMax)**2
      prob = min( int(np.log10(1./prob)*3+50), 90) #probability has max. value of 90
      if self.verbose>1:
        print('  Best fit: dType='+bestDType,' start='+str(bestOffset),' length='+str(lenData),
          ' end='+str(bestOffset+struct.calcsize(str(lenData)+bestDType)-1), ' probability='+str(prob))
      section = Section(length=lenData, dType=bestDType, value='exportedData_col='+str(col+1),
        prob=prob, count=[count])
      self.content[bestOffset] = section
    return


  def findStreak(self:BinaryFileProtocol, dType:str='d', start:int=0) -> None:
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
        if value == 0.0:
          baseD = 0.0
        else:
          baseD = abs(math.log10(abs(value)))
      except Exception as ex:
        print('**Exception at',self.pretty(self.file.tell()),'|',ex)
        baseD = 999
      if baseD<self.optAutomatic['maxExp'] or value==0.0:
        found.append(value)
      else:
        if self.verbose>1:
          print('**Failed at value,baseD',value,baseD)
        break
      if start in self.content and self.file.tell() > start+self.content[start].length:
        break
    #
    if self.verbose>1:
      print(start,'- '+self.pretty(self.file.tell())+': streak of dType='+dType+', length='+str(len(found)))
    self.content[start] = Section(length=len(found), value='streak of dType='+dType+', length='+str(len(found)),\
      dType=dType, prob=20)
    return


  def primaryTimeData(self:BinaryFileProtocol, start:int=0) -> None:
    '''
    Go through the file and read numbers based on if they and next numbers make sense

    Unknown: could be garbage

    Return to zero at the end

    Args:
      start: offset at which to start / start-position of section
    '''
    #move start backward if zeros before that
    length = self.content[start].byteSize()
    startInit = int(start)
    starts = list(self.content)
    idx = starts.index(start)
    sectionBefore = self.content[starts[idx-1]]
    if sectionBefore.dType == 'B':
      start -= min(16, sectionBefore.byteSize())
      if start<0:
        start=0
      length+= min(16, sectionBefore.byteSize())
    #start process
    self.file.seek(start)
    data = self.file.read(length)
    found = False
    while True:
      numData = math.floor(len(data)/8)               #double is largest, use it to determine max. size
      if numData==0:                                  #stop if nothing left
        break
      tempData = data[:struct.calcsize(str(numData)+'d')] #crop binary data
      valuesD = np.array(struct.unpack(str(numData  )+'d', tempData))
      valuesF = np.array(struct.unpack(str(numData*2)+'f', tempData))
      maskD    = np.abs(np.log10(np.abs(valuesD)))  < self.optAutomatic['maxExp']
      maskF    = np.abs(np.log10(np.abs(valuesF)))  < self.optAutomatic['maxExp']
      maskD    = np.logical_or(maskD, valuesD==0)
      maskF    = np.logical_or(maskF, valuesF==0)
      lenD     = np.where(~maskD)[0][0] if np.any(~maskD) else len(maskD) #first value that is true
      lenF     = np.where(~maskF)[0][0] if np.any(~maskF) else len(maskF)
      if lenD>lenF and lenD>=self.optAutomatic['minArray']:
        label = str(lenD)+' doubles with average '+str(np.mean(valuesD[:lenD]))
        if self.verbose>1:
          print(self.pretty(start)+'-'+self.pretty(start+lenD*8),"double|",label)
        self.content[start] = Section(length=lenD, dType='d', value=label, prob=20, dClass='primary')
        found = True
        data = data[lenD*8:]
        start+= lenD*8
      elif lenF>lenD and lenF>=self.optAutomatic['minArray']:
        label = str(lenF)+' floats with average '+str(np.mean(valuesF[:lenF]))
        if self.verbose>1:
          print(self.pretty(start)+'-'+self.pretty(start+lenF*4),"float |",label)
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


  def entropy(self:BinaryFileProtocol, start:int=-1, plot:bool=False) -> float:
    '''
    inspired by but not more than inspired by
    - http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html

    Hints:
    - entropy < 3.3 metadata et al
    - entropy > 4 real data

    Args:
      start: starting position of section; if -1 is given use entire file
      plot: plot graph at end

    Return:
      entropy
    '''
    results = []
    blockSize = self.optEntropy['blockSize']
    if start in self.content:
      self.file.seek(start)
      dataBin = self.file.read( self.content[start].byteSize() )  #read data
      data = struct.unpack(str(self.content[start].byteSize())+'B', dataBin) #convert to byte-int
      blockSize = min(blockSize, self.content[start].byteSize()-1)
      skipEvery = max(self.optEntropy['skipEvery'], int(self.content[start].byteSize()/1024)) #max. of 1024 tests
    else:
      self.file.seek(0)
      dataBin = self.file.read()  #read data
      data = struct.unpack(str(self.fileLength)+'B', dataBin) #convert to byte-int
      skipEvery = self.optEntropy['skipEvery']
    startPoints = np.arange(0,len(data)-blockSize,skipEvery)
    for startI in startPoints:
      _, counts = np.unique(data[startI:startI+blockSize], return_counts=True)
      counts    = counts/blockSize
      yValue    = np.sum(-counts*np.log2(counts))
      results.append(yValue)
    if plot:
      import matplotlib.pyplot as plt
      plt.plot(startPoints, results, '-')
      plt.xlim(left=0)
      plt.ylim(bottom=0)
      plt.xlabel('offset')
      plt.ylabel('entropy')
      plt.show()
    if start in self.content:
      self.content[start].entropy = np.average(results)
    elif not plot and self.verbose>0:
      print('Average entropy:', np.round(np.average(results),4))
    return np.average(results)


  def find2DImage(self:BinaryFileProtocol, start:int) -> None:
    '''
    find a 2D image in section with this start and label accordingly

    Args:
      start: starting position of section; if none is given use entire file
    '''
    #in development
    print('Start',start, self.content[start])
