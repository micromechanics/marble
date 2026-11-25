"""Search file and find values"""
import struct, math, re, difflib, copy, logging, os
from typing import Union, Any
import numpy as np
from .section import Section, SECTION_OUTPUT_ORDER
from .fileClass import FileProtocol

class Util():
  """ Mixin that includes all utility functions """
  def findValue(self:FileProtocol, value:Union[str,float], dType:str='d', verbose:bool=True, offset:int=0) \
    -> list[str]:
    '''
    find value in binary file by iterating all offsets

    Args:
      value: value to be found
      dType: ['d','i'] data-type: double or int
      verbose:  print to screen
      offset: offset to start from

    Returns:
      sorted by error
    '''
    if isinstance(value, str):
      value = float(value)
    allFound, allError = [], []
    byteSize = struct.calcsize(dType)
    for offsetI in range(byteSize):
      self.file.seek(offsetI+offset)
      dataByte = self.file.read()
      numData = math.floor(len(dataByte)/byteSize)
      dataByte = dataByte[:struct.calcsize(str(numData)+dType)] #crop binary data
      data = np.array(struct.unpack(str(numData)+dType, dataByte), dtype=np.float128)    #get data
      mask = np.isfinite(data)
      if value == 0:
        data[mask] = np.abs(data[mask])
      else:
        data[mask] = np.abs((data[mask]-value)/value)     #relative difference
      data[~mask] = 1.
      found = np.where(data<self.optFind['maxError'])[0]       #threshold
      output = [self.pretty(int(i)) for i in offsetI+offset+found*byteSize] #output
      if verbose:
        for idx, offsetJ in enumerate(output):
          print(f'{offsetJ}  found {value} with error {data[found][idx]}')
        if not output:
          print('... found nothing')
      allFound += output
      allError += list(data[found])
    return [x for _, x in sorted(zip(allError, allFound))]


  def findBytes(self:FileProtocol, value:Union[str,float], dType:str='d', offset:int=0) -> int:
    '''
    find value in binary file by looking for the appropriate byte string

    https://stackoverflow.com/questions/3217334/searching-reading-binary-data-in-python

    Args:
      value: value to be found
      dType: ['d','f','i', 's','c'] data-type: double or int or string
      offset: offset to start from

    Returns:
      int: location of found item
    '''
    if dType in {'s','c'} and isinstance(value, str):
      searchString = bytes(value, 'utf-8').hex()
    elif dType in {'i', 'H', 'h'}:
      searchString = struct.pack(dType, int(value)).hex()
    elif dType in {'f', 'd'}:
      searchString = struct.pack(dType, float(value)).hex()
      searchString = searchString[2:]  #chop of first byte (two chars) to allow for close values not precise
    else:
      logging.error("fileUtil:findBytes dTypes %s", dType)
      return -1
    self.file.seek(offset)
    data = self.file.read()
    found = data.hex().find(searchString)
    if found%2==1:                       #if odd: this is not a valid result, cause value not found
      found = -2
    found = int(found/2)                 #divide by 2 because byte has 2 chars
    if dType in {'f', 'd'}:
      found -= 1                         #subtract because first byte was cutoff
    if self.verbose>0:
      if found<0:
        print('Number not found in file')
      else:
        print(f'{self.pretty(found)}  found value {value}')
    return found


  def label(self:FileProtocol, start:int, data:str) -> None:
    '''
    Manually label / define key a section
    - Set probability to 100 and important to true since why would the user label it
    - if dType=f or d are labeled
      - search for that variable
      - link to that variable


    Args:
      start: start offset
      data: data of section
    '''
    if start<0 or start>self.fileLength:
      logging.error("start value does not make sense: {start}")
      return
    if start in self.content:  #edit
      self.content[start].setData(data=data)
    else:                           #create new
      self.content[start] = Section(data=data)
    self.content[start].prob = 100  #otherwise many backend scripts and backend cases do not work
    self.content[start].important = True
    if len(self.content[start].value)>40:
      self.content[start].value = ''
    runFill = not data.startswith('||')
    section = self.content[start]
    if section.dType in ['f','d','H']:
      #find count in file
      length = section.length
      if section.shape != [] and np.prod(section.shape)<length:
        # garbage at end of data-set
        length = np.prod(section.shape)
      anchor, runFill = self.findAnchor(length, start)
      #create link / enter property count
      if section.count == []:
        section.setData(count=[anchor])
      if len(section.count)>len(section.shape):
        shape = []
        for iCount in section.count:
          self.file.seek(iCount)
          iLength = self.file.read(self.content[iCount].byteSize())
          iLength = struct.unpack( self.content[iCount].size(), iLength)[0]
          shape.append(iLength)
        section.setData(shape=shape)
      section.setData(dClass='primary')
    elif 'count' not in data:
      section.setData(dClass='metadata')
    if runFill:
      self.fill()
    return


  def setRowFormat(self:FileProtocol, start:int, numColumns:int, dType:str='f', numRows:int=-1,
                   columns:list[dict[str,str]] | None=None, searchColumnCount:bool=False) -> None:
    '''
    Define primary data that is saved in rows: numRows x numColumns values, row after row

    Args:
      start: start offset of the data
      numColumns: number of values per row
      dType: data type of each value
      numRows: number of rows; -1: derive from the section at start
      columns: key, unit, link of each column
      searchColumnCount: search the file for the number of columns, otherwise it is a fixed number
    '''
    if numRows<0:
      if start not in self.content:
        logging.error('setRowFormat: no section at %s to derive the number of rows', start)
        return
      numRows = self.content[start].byteSize()//(numColumns*struct.calcsize(dType))
      for countType in ['i','H']:  #count directly in front: exact; automatic section lengths are approximate
        if start-struct.calcsize(countType)>=0:
          self.file.seek(start-struct.calcsize(countType))
          numFound = struct.unpack(countType, self.file.read(struct.calcsize(countType)))[0]
          if 0<numFound and abs(numFound-numRows)<=0.01*numRows:
            numRows = numFound
            break
    shape = [numRows, numColumns]
    count = [self.findAnchor(numRows, start)[0],
             self.findAnchor(numColumns, start)[0] if searchColumnCount else -1]
    self.content[start] = Section(length=numRows*numColumns, dType=dType, key='primary data in rows',
                                  value='primary data in rows', dClass='primary', shape=shape, count=count,
                                  prob=100, important=True, entropy=-1)
    columns = columns or []
    self.rowFormatMeta[:] = [{'key':i.get('key',''), 'unit':i.get('unit',''), 'link':i.get('link','')}
                             for i in columns+[{}]*(numColumns-len(columns))]
    self.rowFormatSegments.add(start)
    self.fill()
    return


  def compare(self:FileProtocol, otherFiles:list[str], anchor:Union[str,bytes,None]=None, verbose:bool=True) \
    -> list[dict[str,Any]]:
    '''
    Compare this file with other files: which bytes are constant, which vary

    - files: sizes, identical, common prefix, fraction of equal bytes at the same position (interpretation is up to the user)
    - with anchor (regex, e.g. a date string that starts each test): split all files at the anchor and compare the
      distinct segments: head (before first anchor), units (anchor to next anchor), tail (last anchor to end).
      Each group is compared aligned at its start and aligned at its end; segment lengths are reported.

    Args:
      otherFiles: file names to compare with
      anchor: regular expression (str or bytes) that marks the start of each unit
      verbose: print results

    Returns:
      list of results: numbers per file pair and, per group/alignment, ranges with state constant/varying
    '''
    allData:list[tuple[str,bytes]] = []
    for fileName in [self.fileName]+otherFiles:
      with open(fileName, 'rb') as fIn:
        allData.append((fileName, fIn.read()))
    results:list[dict[str,Any]] = []
    for idx, (fileName1, data1) in enumerate(allData):
      for fileName2, data2 in allData[idx+1:]:
        minLen = min(len(data1), len(data2))
        equal = np.frombuffer(data1[:minLen], np.uint8)==np.frombuffer(data2[:minLen], np.uint8)
        prefix = int(np.argmin(equal)) if not equal.all() else minLen
        fraction = float(equal.mean()) if minLen else 0.
        results.append({'group':'file', 'files':[fileName1, fileName2], 'sizes':[len(data1), len(data2)],
                        'commonPrefix':prefix, 'equalFraction':round(fraction,4), 'identical':data1==data2})
    if anchor is not None:
      pattern = re.compile(anchor.encode('latin-1') if isinstance(anchor, str) else anchor)
      groups:dict[str,list[bytes]] = {'head':[], 'unit':[], 'tail':[]}
      for _, data in allData:
        starts = [i.start() for i in pattern.finditer(data)]
        if not starts:
          continue
        groups['head'].append(data[:starts[0]])
        groups['unit'] += [data[i:j] for i,j in zip(starts[:-1], starts[1:])]
        groups['tail'].append(data[starts[-1]:])
      for group, segments in groups.items():
        segments = list(dict.fromkeys(segments))  #distinct, keep order
        if len(segments)<2:
          results.append({'group':group, 'segments':len(segments), 'lengths':[len(i) for i in segments]})
          continue
        lengths = [len(i) for i in segments]
        minLen = min(lengths)
        for align in ['start'] if len(set(lengths))==1 else ['start','end']:
          aligned = np.array([np.frombuffer(i[:minLen] if align=='start' else i[-minLen:], np.uint8) for i in segments])
          varying = np.where((aligned!=aligned[0]).any(axis=0))[0]
          ranges:list[list[int]] = []
          for i in varying:   #merge varying bytes that are close
            if ranges and i-ranges[-1][1]<=3:
              ranges[-1][1] = int(i)
            else:
              ranges.append([int(i), int(i)])
          offset = 0 if align=='start' else -minLen
          ranges_ = [{'start':a+offset, 'end':b+offset+1,
                      'values':[aligned[k][a:b+1].tobytes().hex() for k in range(len(segments))] if b-a<16 else []}
                     for a,b in ranges]
          results.append({'group':group, 'align':align, 'segments':len(segments), 'lengths':lengths,
                          'compared':minLen, 'varying':ranges_})
    if verbose:
      fileResults = [i for i in results if i['group']=='file']
      print(f'{len(allData)} files, {len(fileResults)} pairs; equal bytes = fraction of equal bytes at the same position')
      for res in fileResults:
        print(f"  {os.path.basename(res['files'][0])} - {os.path.basename(res['files'][1])}: sizes {res['sizes']}, "
              f"common prefix {res['commonPrefix']}, equal bytes {res['equalFraction']:.1%}"
              f"{', identical' if res['identical'] else ''}")
      for res in results:
        if res['group']=='file':
          continue
        if 'varying' not in res:
          print(f"{res['group']}: {res['segments']} distinct segment(s), lengths {res['lengths']}")
        else:
          print(f"{res['group']} aligned at {res['align']}: {res['segments']} distinct segments, lengths "
                f"{res['lengths']}, {res['compared']} bytes compared; all other bytes constant")
          shown = res['varying'] if len(res['varying'])<=30 else res['varying'][:15]+res['varying'][-15:]
          for idxRange, rng in enumerate(shown):
            if len(shown)<len(res['varying']) and idxRange==15:
              print(f"  ... {len(res['varying'])-30} more varying ranges ...")
            print(f"  varying {rng['start']}..{rng['end']} ({rng['end']-rng['start']} bytes)", end='')
            print(':  '+' '.join(rng['values']) if rng['values'] else '')
            if rng['values'] and len(rng['values'][0]) in (4,8,16):
              fmt = {4:'<H', 8:'<I', 16:'<d'}[len(rng['values'][0])]
              numbers = [struct.unpack(fmt, bytes.fromhex(i))[0] for i in rng['values']]
              print(f'    as {fmt}: {numbers}')
              if fmt=='<I':
                floats = [float(f"{struct.unpack('<f', bytes.fromhex(i))[0]:.6g}") for i in rng['values']]
                print(f'    as <f: {floats}')
    return results


  def coverage(self:FileProtocol, otherFiles:list[str] | None=None, anchor:Union[str,bytes,None]=None,
               verbose:bool=True) -> dict[str,Any]:
    '''
    How much of the file is understood; labelled = important sections

    - fields: each labelled section counts as one field, regardless of size; unknown bytes (dType b) count as
      one potential field per 4 bytes, at most optAutomatic['maxFieldsPerRegion'] per region (larger regions are
      likely one structure: array, image, table); unlabelled typed sections count as one potential field; zeros count nothing
    - bytes: fraction of the file in labelled sections (dominated by large data arrays)
    - varying (with otherFiles): bytes that vary between samples carry the information; labelled sections that
      contain varying bytes vs. regions of varying bytes outside of labelled sections

    Args:
      otherFiles: other samples, see compare()
      anchor: regular expression that starts each measurement unit, see compare()
      verbose: print results

    Returns:
      dictionary with the coverages
    '''
    labelled = [(start, start+sec.byteSize()) for start, sec in self.content.items() if sec.important]
    # ponytail: 4 bytes per field and the cap per region are assumptions
    potential = sum(min(math.ceil(sec.byteSize()/4), self.optAutomatic['maxFieldsPerRegion']) if sec.dType=='b' else 1
                    for sec in self.content.values()
                    if not sec.important and sec.dType!='B')
    result:dict[str,Any] = {'fields': {'labelled':len(labelled), 'potential':potential,
                                       'fraction':len(labelled)/max(len(labelled)+potential,1)},
                            'bytes':  sum(end-start for start,end in labelled)/max(self.fileLength,1)}
    if otherFiles:
      pattern = re.compile(anchor.encode('latin-1') if isinstance(anchor, str) else anchor) if anchor is not None \
                else re.compile(rb'\A')   #no anchor: compare complete files
      with open(self.fileName, 'rb') as fIn:
        anchors = [i.start() for i in pattern.finditer(fIn.read())]
      segments = {'head':[(0, anchors[0])] if anchors else [], 'unit':list(zip(anchors[:-1], anchors[1:])),
                  'tail':[(anchors[-1], self.fileLength)] if anchors else []}
      varying = np.zeros(self.fileLength, dtype=bool)   #varying bytes in this file
      for res in self.compare(otherFiles, pattern.pattern, verbose=False):
        if 'varying' in res:
          for segStart, segEnd in segments[res['group']]:
            base = segStart if res['align']=='start' else segEnd
            for rng in res['varying']:
              varying[max(base+rng['start'], segStart):min(base+rng['end'], segEnd)] = True
      inLabelled = np.zeros(self.fileLength, dtype=bool)
      for start, end in labelled:
        inLabelled[start:end] = True
      covered = sum(1 for start,end in labelled if varying[start:end].any())
      outside = np.flatnonzero(varying & ~inLabelled)
      # ponytail: varying bytes closer than 16 bytes form one region; data arrays become one region, close header
      # fields may merge
      regions = int(len(outside)>0) + int(np.count_nonzero(np.diff(outside)>16))
      result['varying'] = {'labelledSections':covered, 'regionsOutside':regions,
                           'fraction':covered/max(covered+regions,1)}
    if verbose:
      print(f"fields:  {result['fields']['labelled']} labelled, {result['fields']['potential']} potential fields in "
            f"unknown regions -> {result['fields']['fraction']:.1%}")
      print(f"bytes:   {result['bytes']:.1%} of the file in labelled sections")
      if 'varying' in result:
        print(f"varying: {result['varying']['labelledSections']} labelled sections contain varying bytes, "
              f"{result['varying']['regionsOutside']} varying regions outside -> {result['varying']['fraction']:.1%}")
    return result


  def fill(self:FileProtocol) -> None:
    '''
    Fill content by labeling undefined sections to be "undefined" binary data
    - cleaning / repair all cases of overlap
    - remove all 0-length items
    '''
    if len(self.content)<1:
      logging.error("FILL: One entry required. I exit.")
      return
    rerun = True
    while rerun:#loop until all changes made
      #some tests at start: use for debugging
      # print('Start')
      # for start in self.content:
      #   section = self.content[start]
      #   if section.dType=='B' and section.value=='unknown binary string':
      #     print('**ERROR: dtype==B and section.value==unknown binary string', start, section)

      rerun = False
      toDelete = []
      starts = list(self.content)
      for idx,start in enumerate(starts):
        section = self.content[start]
        if section.length==0 and section.dType=='b':  #if byte of zero length
          toDelete.append(start)
        elif section.length<self.optAutomatic['minArray'] and section.dType in ['f','d'] and \
               section.dClass!='metadata':
          #if data less that supposed
          toDelete.append(start)
        elif idx+1<len(starts) and section.dType=='c' and not section.count and not section.important and self.content[starts[idx+1]].dType=='B':
          #if text is followed by a zeros
          self.content[start].length += self.content[starts[idx+1]].length #   add zeros to text
          toDelete.append(starts[idx+1])                                   #   remove zeros
        elif section.entropy<0:  #repair missing entropies
          self.entropy(start, False)
      for start in toDelete:
        del self.content[start]
      toDelete = []
      starts = list(self.content)
      #create section before first entry
      if starts[0]>0:
        self.file.seek(0)
        text = 'unknown binary string' #self.byteToString(self.file.read(starts[0]),1)
        self.content[0] = Section(length=starts[0], dType='b', value=text)
        self.entropy(0, False)

      #create sections between sections
      for idx, start in enumerate(starts[:-1]):
        section = self.content[start]
        end = start + section.byteSize()
        if end<starts[idx+1]:
          #there is a hole, fill it with a section
          self.file.seek(end)
          text = 'unknown binary string' #self.byteToString(self.file.read(starts[idx+1]-end),1)
          self.content[end] = Section(length=starts[idx+1]-end, dType='b', value=text)
          self.entropy(end, False)
        elif end>starts[idx+1]:
          #there is an overlap, shorten something
          if section.prob < self.content[ starts[idx+1] ].prob: #repair: shorten this section
            if struct.calcsize(section.dType)>1:
              # print("**WARNING: shorten this section with possibly important data, data-length>1B.")
              rerun = True
            section.length = int((starts[idx+1]-start)/struct.calcsize(section.dType))
            self.file.seek(start)
            if section.dType == 'b':
              section.value   = 'unknown binary string' #self.byteToString(self.file.read(section.length),1)
            elif section.dType == 'B':
              section.value   = f'Zeros {section.length}'
            self.content[start] = section
            self.entropy(start, False)   #set entropy
            if self.verbose>1:
              print(f'Shorten this entry {start}=>end={end}, because next section starts at {starts[idx+1]}')
          else:  #repair: move next section to end of this section; shorten next section
            toDelete.append(starts[idx+1])
            secNext = Section(data=str(self.content[starts[idx+1]]))
            secNext.length = secNext.length-(end-start)
            if secNext.length > 0:   #only add if length is positive
              self.file.seek(end)
              secNext.value   = 'unknown binary string' #self.byteToString(self.file.read(secNext.length),1)
              self.content[end] = secNext
              self.entropy(end, False)
              if self.verbose>1:
                print(f'Shorten next entry{starts[idx+1]}')
            else:
              rerun = True
              if self.verbose>1:
                print(f'Shorten next entry{starts[idx+1]}: do not since too short')
      for start in toDelete:
        del self.content[start]

      #create section after last section
      if starts[-1] in self.content:  #if last section still there
        section = self.content[starts[-1]]
        newStart = starts[-1]+struct.calcsize(str(max(section.length,0))+section.dType)#max: no neg. numbers
        if newStart<self.fileLength:
          self.file.seek(newStart)
          text = 'unknown binary string' #self.byteToString(self.file.read(self.fileLength-newStart),1)
          self.content[newStart] = Section(length=self.fileLength-newStart, dType='b', value=text)
          self.entropy(newStart, False)

      #merge sequential binary sections
      pairsAll    = zip(self.content.keys()[:-1], self.content.keys()[1:])
      #TODO: joinPattern ['b'] or ['B']
      while pairsRepair := [[i, j] for i, j in pairsAll
                            if self.content[i].dType == 'b' and self.content[j].dType == 'b' and
                            not self.content[i].important and not self.content[j].important]:  #keep labelled bytes
        first, second = pairsRepair[0]  #just take the first and then rebuild to prevent overlapping
        self.content[first].length += self.content[second].length
        self.content[first].shape  = [self.content[first].length]
        del self.content[second]
        pairsAll    = zip(self.content.keys()[:-1], self.content.keys()[1:])
      # #some tests at end: use for debugging
      # print('End')
      # for start in self.content:
      #   section = self.content[start]
      #   if section.dType=='B' and section.value=='unknown binary string':
      #     print('**ERROR: dtype==B and section.value==unknown binary string', start, section)
    return


  def split(self:FileProtocol, start:int, byteSize1:int) -> None:
    '''
    Split section into 2: length of first segment given

    Args:
      start (int): start of section
      byteSize1 (int): length of first segment
    '''
    dtypeByteSize    = struct.calcsize(self.content[start].dType)
    oldByteLength    = self.content[start].byteSize()
    length1          = int(byteSize1/dtypeByteSize)
    self.content[start].length = length1
    byteSize1        = self.content[start].byteSize()

    section2 = copy.deepcopy(self.content[start])
    section2.length = int((oldByteLength-byteSize1)/dtypeByteSize)
    self.content[start+byteSize1]  = section2
    return


  def findAnchor(self:FileProtocol, lengthSearch:int, maxOffset:int=-1) -> tuple[int, bool]:
    """
    find anchor in data, in previously identified anchors

    Args:
      lengthSearch (int): number to search
      maxOffset (int):    find anchor before this offset

    Returns:
      int: offset where anchor is located
    """
    anchor = None
    createdNew = False
    # look through existing: determine max. prevK
    prevKvariables = 0
    for startJ in self.content:
      section = self.content[startJ]
      if section.key.endswith(str(lengthSearch)) and section.dType=='i':
        anchor = startJ
        break
      if re.search(r'^k\d+=', section.key) and section.dType=='i':
        prevKvariables += 1
    # look immediately in front
    if maxOffset > 3:
      for dType in ['H','i','h']:
        byteSize = struct.calcsize(dType)
        self.file.seek(maxOffset-byteSize)
        numFound = struct.unpack(dType, self.file.read(byteSize))[0]
        if numFound==lengthSearch:
          anchor = maxOffset-byteSize
          if anchor in self.content and self.content[anchor].dType==dType and \
             self.content[anchor].key.endswith(str(lengthSearch)):
            return anchor, False
          self.content[anchor] = Section(length=1, key=f'k{prevKvariables+1}={lengthSearch}',
                                         dType=dType, prob=100, dClass='count', important=True)
          return anchor, True
    # search for new
    maxOffset = maxOffset if maxOffset>=0 else self.fileLength
    if anchor is not None and anchor<=maxOffset-4:
      anchor = None
    if anchor is None:    #only if not already found: create new
      for dType in ['i','H','h']:
        if (dType=='H' and lengthSearch>0x7fff*2+1) or (dType=='h' and lengthSearch>0x7fff):
          continue
        anchor = self.findBytes(lengthSearch, dType,0)
        if 0 <= anchor <= maxOffset-4:
          self.content[anchor] = Section(length=1, key=f'k{prevKvariables+1}={lengthSearch}',
                                         dType=dType, prob=100, dClass='count', important=True)
          createdNew = True
          break
    return (-1, False) if anchor is None else (anchor, createdNew)


  def verify(self:FileProtocol) -> None:
    '''
    Verify some sanity tests
    '''
    for start in self.content:
      sect = self.content[start]
      if sect.dType not in ['b', 'B', 'f', 'd', 'i', 'c', 'H']:
        logging.error('there is a non-defined dType %s| change to b',sect.dType)
        sect.dType='b'
      argumentsExist = sorted(list(self.content[start].__dict__))
      if argumentsExist != sorted(SECTION_OUTPUT_ORDER):
        logging.error('initialization error in Section\n    do exist: %s\nshould exist: %s',argumentsExist,
                      sorted(SECTION_OUTPUT_ORDER))
    return



  @staticmethod
  def byteToString(aBytes:bytes, spaceEvery:int=1) -> str:
    '''
    convert bytestring to easy to read string

    Args:
        aBytes: byte-string
        spaceEvery: white-space for easy reading
    Returns:
        formatted byte string
    '''
    aString = aBytes.hex().upper()
    if spaceEvery>0:
      spaceEvery *= 2
      return ' '.join(aString[i:i+spaceEvery] for i in range(0, len(aString), spaceEvery))
    aList = [int(aString[i:i+2], base=16) for i in range(0,len(aString),2) ]#list of integer/char
    listConsecutive = np.split(aList, np.where(np.diff(aList) != 0)[0]+1)   #find consecutive entries list[]
    return ''.join([''.join([hex(j)[2:].zfill(2) for j in i]) if len(i)<3 or i[0]>0 \
      else f' {len(i)}*00 ' for i in listConsecutive])


  # @staticmethod
  # def diffStrings(old:str, new:str) -> list[str]:
  #   '''
  #   determine difference between two strings and color those

  #   based on
  #   https://stackoverflow.com/questions/32500167/how-to-show-diff-of-two-string-sequences-in-colors

  #   Future questions:
  #   - try diff for byteString directly
  #   - does one need to output equal? If not, the start point does not make sense=>make sense
  #   - how can we improve (add '\n'); good for large differences
  #   - do automatically subdivide into sections: equal and differences
  #   - it would be best to have 00 00 00 reduced to 00

  #   Args:
  #     old (string): first string
  #     new (string): second string

  #   Returns:
  #     colored output
  #   '''
  #   def red(text):
  #     return f"\033[38;2;255;0;0m{text}\033[0m"
  #   def green(text):
  #     return f"\033[38;2;0;255;0m{text}\033[0m"

  #   result = ""
  #   codes = difflib.SequenceMatcher(a=old, b=new).get_opcodes()
  #   differenceFlag = False
  #   for code in codes:
  #     #length = max(code[2]-code[1], code[4]-code[3])
  #     if code[0] == "equal":
  #       result += old[code[1]:code[2]]
  #     elif code[0] == "delete" and len(bytes(filter(None,bytearray(old[code[1]:code[2]],'utf-8'))))>0:
  #       result += red(old[code[1]:code[2]])
  #       differenceFlag = True
  #     elif code[0] == "insert" and len(bytes(filter(None,bytearray(new[code[3]:code[4]],'utf-8'))))>0:
  #       result += green(new[code[3]:code[4]])
  #       differenceFlag = True
  #     elif code[0] == "replace" and (len(bytes(filter(None,bytearray(old[code[1]:code[2]],'utf-8'))))>0 \
  #                                 or len(bytes(filter(None,bytearray(new[code[3]:code[4]],'utf-8'))))>0):
  #       result += (red(old[code[1]:code[2]]) + green(new[code[3]:code[4]]))
  #       differenceFlag = True
  #   return [result, str(differenceFlag)]


  def pretty(self:FileProtocol, number:int) -> str:
    '''
    convert decimal or hexadecimal number in easy to read string

    Args:
        number: integer to convert to hex
    Returns:
        formatted decimal or hexadecimal offset
    '''
    if isinstance(number, str):
      number = int(number.replace(':',''), 0)
    if self.printMode=='dec':
      formatString = "{:0"+str(len(str(self.fileLength)))+"d}"
      return formatString.format(number)
    aString = hex(number)[2:]
    sRef = hex(self.fileLength)[2:]
    aString = '0'*(len(sRef)-len(aString)) + aString
    aList = [aString[max(i-4,0):i] for i in range(len(aString),0,-4)]
    aList.reverse()
    return '0x'+':'.join(aList)
