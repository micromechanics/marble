"""input and output to files; plot to screen"""
import os, io, struct, json, logging, html
from typing import Optional
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.axes._axes import Axes
from .section import Section, SECTION_OUTPUT_ORDER
from .fileClass import FileProtocol

class InputOutput():
  """ Mixin that includes all input and output functions """
  def __init__(self:FileProtocol):
    """ defaults if this class is used separately, aka. never.
    """
    self.file                      = io.BytesIO()
    self.periodicity:dict[str,int] = {}
    self.rowFormatMeta:list[dict[str,str]] = []
    self.rowFormatSegments:set[int]= set()
    self.meta                      = {'vendor':'', 'label':'', 'software':''}
    self.fileLength                = -1


  def initContent(self:FileProtocol) -> None:
    '''
    set binary file initially

    One could think of moving data into ram and use multiprocess to work in parallel
      - options are (disk,virt-disk, ram)
      - if running on one processor it does not make much sense / faster
      - if data too big for RAM, chunk it into pieces that fit into RAM
      - parallel actions on the self.content are difficult to coordinate
    '''
    self.fileLength = os.path.getsize(self.fileName)
    if self.fileType=='disk':
      self.file       = open(self.fileName,'br')               # pylint: disable=consider-using-with
      #runtime python test: 26.5sec # runtime shell test: 1m3.577s
    else:
      with open(self.fileName,'br') as file:
        self.file       = io.BytesIO(file.read())
      #runtime python test: 22.8sec  # runtime shell test: 1m8.051s
    # set initial content
    self.content[np.int64(0)] = Section(length=self.fileLength, dType='b',prob=0)
    # output of initialization
    if self.verbose>1:
      print("Process file:",self.fileName,' of length',self.pretty(self.fileLength),'in mode',self.printMode)
    self.meta['ext']=os.path.splitext(self.fileName)[1][1:]
    return


  def saveTags(self:FileProtocol) -> None:
    '''
    Output file content to .tags file
    '''
    if len(self.content)<2:
      logging.error("**ERROR in SaveTags: NOT ENOUGH ENTRIES in content. I exit.")
      return
    tagsFile = self.fileName+'.tags'
    with open(tagsFile, 'w', encoding='utf-8') as fOut:
      fOut.write('<?xml version="1.0" encoding="UTF-8"?>\n')
      fOut.write('<wxHexEditor_XML_TAG>\n')
      fOut.write('  <filename path="'+self.fileName+'">\n')
      for idx, start in enumerate(self.content):
        section = self.content[start]
        end     = start + struct.calcsize(str(section.length)+section.dType)
        fOut.write(f'    <TAG id="{idx}' + '">\n')
        fOut.write(f'      <start_offset>{start}' + '</start_offset>\n')
        fOut.write(f'      <end_offset>{end}' + '</end_offset>\n')
        fOut.write(f'      <tag_text>{section}' + '</tag_text>\n')
        if section.dType=='d':
          fOut.write('      <font_colour>#000000</font_colour>\n')
          fOut.write('      <note_colour>#4EB371</note_colour>\n')
        elif section.dType=='f':
          fOut.write('      <font_colour>#000000</font_colour>\n')
          fOut.write('      <note_colour>#4E5FB3</note_colour>\n')
        elif section.dType=='c':
          fOut.write('      <font_colour>#000000</font_colour>\n')
          fOut.write('      <note_colour>#B38D4E</note_colour>\n')
        elif section.dType=='i':
          fOut.write('      <font_colour>#000000</font_colour>\n')
          fOut.write('      <note_colour>#FFF700</note_colour>\n')
        elif section.dType=='B':
          fOut.write('      <font_colour>#000000</font_colour>\n')
          fOut.write('      <note_colour>#FFFFFF</note_colour>\n')
        else:
          fOut.write('      <font_colour>#000000</font_colour>\n')
          fOut.write('      <note_colour>#FF0000</note_colour>\n')
        fOut.write('    </TAG>\n')
      fOut.write('  </filename>\n')
      fOut.write(f'  <meta>{json.dumps(self.meta)}' + '</meta>\n')
      fOut.write(f'  <periodicity>{json.dumps(self.periodicity)}</periodicity>\n')
      fOut.write(f'  <row_meta>{json.dumps(self.rowFormatMeta)}</row_meta>\n')
      fOut.write(f'  <row_segments>{json.dumps([int(i) for i in self.rowFormatSegments])}</row_segments>\n')
      fOut.write('</wxHexEditor_XML_TAG>\n')
    return


  def loadTags(self:FileProtocol) -> None:
    '''
    .tags file read into content
    '''
    tagsFile = self.fileName+'.tags'
    if not os.path.exists(tagsFile):
      logging.error('loadTags: file does not exist %s. I exit.',tagsFile)
      return
    tree = ET.parse(tagsFile)
    root = tree.getroot()
    # metadata
    meta = root.find('meta')
    if meta is None:
      logging.error('could not loadTags metadata')
      return
    self.meta = json.loads(str(meta.text))
    periodicity = root.find('periodicity')
    if periodicity is None:
      logging.error('could not loadTags periodicity')
      return
    self.periodicity = json.loads(str(periodicity.text))
    rowFormatMeta = root.find('row_meta')
    if rowFormatMeta is None:
      logging.error('could not loadTags rowFormatMeta')
      return
    self.rowFormatMeta = json.loads(str(rowFormatMeta.text))
    rowFormatSegments = root.find('row_segments')
    if rowFormatSegments is None:
      logging.error('could not loadTags rowFormatSegments')
      return
    self.rowFormatSegments = set(json.loads(str(rowFormatSegments.text)))
    # other data: that of list
    filename = root.find('filename')
    for tag in list(filename):   # type: ignore[arg-type]
      start = int(tag.find('start_offset').text)
      self.content[start] = Section(data=tag.find('tag_text').text)
    return


  def savePython(self:FileProtocol) -> None:
    '''
    Output file content to .py file
    header has formalized description of file-structure

    the csv file at the end of the file is the specific version of this file:
      - byte differences are difficult to recrate original one
    '''
    pyFile = os.path.splitext(self.fileName)[0]+'.py'
    with open(pyFile, 'w', encoding='utf-8') as fOut:
      # PYTHON PART
      # header
      fOut.write("#!/usr/bin/python3\n")
      fOut.write("# INFO: THIS PART IS IS FOR HUMANS BUT IT IS IGNORED BY MARBLE")
      fOut.write(self.pythonHeader())
      fOut.write(Section.pythonHeader())
      fOut.write('\n###MAIN FUNCTION\ntry:\n')
      # body: for loop items
      inForLoop = False
      if 'count' in self.periodicity:
        start = int(self.periodicity['count'])
        line = self.content[start].toPY(start, 0, variable='numberOfTests')
        fOut.write('  fIn.seek(0)\n')
        fOut.write('  '+line)
        self.content[start].dClass='metadata'  #count->metadata
      #body: things other than foor loop
      fOut.write('  fIn.seek(0)\n')
      lastOutput = 0
      if not bool(self.periodicity):  #if no periodicity
        fOut.write('  hdfBranch_ = fOut.create_group("test_1")\n')
        fOut.write('  hdfBranch_.attrs["NX_class"] = b"NXentry"\n')
        fOut.write('  hdfBranch = hdfBranch_.create_group("data")\n')
        fOut.write('  hdfBranch.attrs["NX_class"] = b"NXdata"\n')
      for start in self.content:
        if 'start' in self.periodicity and start==int(self.periodicity['start']):
          fOut.write('  for idxTest in range(numberOfTests):\n')
          fOut.write('    hdfBranch_ = fOut.create_group("test_"+str(idxTest+1))\n')
          fOut.write('    hdfBranch_.attrs["NX_class"] = b"NXentry"\n')
          fOut.write('    hdfBranch = hdfBranch_.create_group("data")\n')
          fOut.write('    hdfBranch.attrs["NX_class"] = b"NXdata"\n')
          inForLoop = True
        sect= self.content[start]
        if not sect.important:  #don't output unimportant items
          continue
        branchName = None
        if ( sect.dClass in ['metadata','primary'] and inForLoop ) or not bool(self.periodicity):
          branchName = 'hdfBranch'
        if line := self.content[start].toPY(start, lastOutput, binaryFile=self, hdf=branchName):
          forLoopPrefix = '  ' if inForLoop else ''
          fOut.write(f'  {forLoopPrefix}{line}')
          lastOutput = start+self.content[start].byteSize()
        if 'end' in self.periodicity and start==int(self.periodicity['end']):
          inForLoop = False
      # footer
      remainderContent = 0 if 'count' in self.periodicity else self.fileLength-lastOutput
      # create periodicity function
      # - if periodicity: remainder does not always have to be zero, no better logic
      #   one should evaluate by running through actual binary file
      fOut.write(f'  if os.path.getsize(fileNameIn)-fIn.tell()!={remainderContent}:\n')
      fOut.write('    print("Translation NOT successful")\n')
      fOut.write('  else:\n')
      fOut.write('    print("Translation successful")\n')
      fOut.write('\nexcept:\n  print("**ERROR** Exception in translation")\n')

      # FORMALIZED DESCRIPTION OF BINARY-FILE-STRUCTURE
      #revert count->metadata so it can be saved again
      if 'count' in self.periodicity:
        start = int(self.periodicity['count'])
        self.content[start].dClass='count'
      fOut.write("\n\n\n'''\n")
      fOut.write("# INFO: THIS PART IS LOADED BY MARBLE\n")
      fOut.write('# version= 1.0\n')
      fOut.write(f'# meta={json.dumps(self.meta)}\n')
      fOut.write(f'# periodicity={json.dumps(self.periodicity)}\n')
      fOut.write(f'# rowFormatMeta={json.dumps(self.rowFormatMeta)}\n')
      fOut.write(f'# rowFormatSegments={json.dumps(list(self.rowFormatSegments))}\n')
      fOut.write(f'# length={len(self.content)}\n')
      dataframe = pd.DataFrame()
      for start in self.content:
        lineData = dict( self.content[start].toCSV() )  #make a copy
        #first case: if len is represented by shape and its primary data: invalidate length
        # if (lineData['shape']!=[] and np.prod(lineData['shape']) == lineData['length'] and \
        #   lineData['dClass']=='primary'):
        #   lineData['length']=-1
        lineData['value'] = lineData['value'].replace('\\','\\\\')
        lineData['entropy'] = round(lineData['entropy'],2)
        dataframe = pd.concat([dataframe, pd.Series(lineData).to_frame().T], ignore_index=True)
      dataframe = dataframe[SECTION_OUTPUT_ORDER]         #sort colums by defined order
      dataframe.to_csv(fOut, index=False)
      fOut.write("'''\n")
    return


  def loadPython(self:FileProtocol, pyFile:Optional[str]=None) -> None:
    '''
    load python file and parse its header information
    '''
    compare = True
    if pyFile is None:
      pyFile = os.path.splitext(self.fileName)[0]+'.py'
      compare = False

    with open(pyFile, 'r', encoding='utf-8') as fIn:
      for line in fIn:
        if line.strip() == '# INFO: THIS PART IS LOADED BY MARBLE':
          break
      line = fIn.readline().strip()
      if line.startswith('# version='):
        logging.info('read file version %s',line.split('=')[1])
      else:
        logging.error('python does not match loadPython version')
        return
      line = fIn.readline().strip()
      if line.startswith('# meta='):
        self.meta = json.loads(line[7:])
      else:
        logging.error('python does not match loadPython meta')
        return
      line = fIn.readline().strip()
      if line.startswith('# periodicity='):
        self.periodicity = json.loads(line[14:])
      else:
        logging.error('python does not match loadPython periodicity')
        return
      line = fIn.readline().strip()
      if line.startswith('# rowFormatMeta='):
        self.rowFormatMeta = json.loads(line[16:])
      else:
        logging.error('python does not match loadPython rowFormatMeta')
        return
      line = fIn.readline().strip()
      if line.startswith('# rowFormatSegments='):
        self.rowFormatSegments = set(json.loads(line[20:]))
      else:
        logging.error('python does not match loadPython rowFormatSegments')
        return
      line = fIn.readline().strip()
      if not line.startswith('# length='):
        logging.error('python does not match loadPython length')
        return
      numLines = int(line[9:])
      readDataFrame = pd.read_csv(fIn, nrows=numLines).fillna('')
      readData = readDataFrame.to_dict(orient='records')
      start = 0
      #Input lines
      for row in readData:
        row['count'] = [] if row['count'] =='[]' else [int(i) for i in row['count'][1:-1].split(',')]
        row['shape'] = [] if row['shape'] =='[]' else [int(i) for i in row['shape'][1:-1].split(',')]
        row['value'] = html.unescape(row['value'])
        #for all sections
        section = Section(**row)            # type: ignore
        section.value = section.value.encode('utf-8').decode('unicode_escape')
        if section.length<0:
          section.length = int(np.prod(section.shape))
        if compare and section.dType in ['b','c']:
          self.file.seek(start)
          newText = None
          if section.dType=='b':
            newText = self.byteToString(self.file.read(section.length),1)
          else:
            newText = bytearray(self.file.read(section.length)).decode('utf-8', errors='replace')
          if newText is not None:
            diffText, diffFlag = self.diffStrings(section.value,newText)
            if diffFlag and section.prob<90:
              print('\nDifferent at',start,'|py: red, data: green')
              print(diffText)
        #save and move on
        self.content[start] = section
        start += section.byteSize()
    return


  def plot(self:FileProtocol, start:int, plotMode:int=1, show:bool=True) -> Optional[Axes]:
    '''
    Plot as graph values found at location i

    Args:
        start: starting location
        plotMode: plot as 1d time-series (1) or as 2d image (2)
        show (bool): show on screen; false-return axis
    '''
    if start not in self.content:
      print("**ERROR: cannot print at start",start,'. I exit')
      return None
    section = self.content[start]
    #offsets on the x-axis
    #valuesX = np.linspace(start, start+section.byteSize(), section.length)
    #length on the x-axis
    valuesX = range(1, section.length+1)
    self.file.seek(start)
    data = self.file.read(section.byteSize())
    if len(data) !=struct.calcsize(section.size()):
      logging.error('cannot plot size does not fit byte-length')
      return None
    valuesY = struct.unpack(section.size(), data) #get data
    if plotMode==1:
      ax1 = plt.subplot(111)
      ax1.plot(valuesX, valuesY, '-o')
      def toHex(num:str, _:int) -> str:
        return f'0x{int(num)}'
      if self.printMode=='hex':
        ax1.get_xaxis().set_major_formatter(ticker.FuncFormatter(toHex))
      yMin = np.percentile(valuesY,2)
      yMax = np.percentile(valuesY,98)
      yMin = 1.1*yMin-0.1*yMax
      yMax = 1.1*yMax-0.1*yMin
      # ax1.axhline(0, color='k', linestyle='dashed')
      # ax1.axvline(1, color='k', linestyle='dashed')
      ax1.set_ylim([yMin,yMax])
      ax1.set_xlabel('increment')
      ax1.set_ylabel('value')
    elif plotMode==2:
      sideLength = int(np.sqrt(len(valuesY)))
      valuesYArray = np.array(valuesY).reshape((sideLength,sideLength))
      ax1 = plt.subplot(111)
      image = ax1.imshow(valuesYArray)
      ax1.axis('off')
      plt.colorbar(image)
    if show:
      plt.show()
      return None
    return ax1


  def pythonHeader(self:FileProtocol) -> str:
    '''
    Header written at top of python file
    - includes only the python code and not the predefined functions
    - uses metadata to infuse python header and hdf5 metadata
    '''
    return """
'''
convert """+self.meta['vendor']+" "+self.meta['ext']+""" to .hdf5 file

in_file:
  label: """+self.meta['label']+"""
  vendor: """+self.meta['vendor']+"""
  software: """+self.meta['software']+"""
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

convURI = b'https://raw.githubusercontent.com/main/cwl/"""+self.meta['ext']+"""2hdf.cwl'
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

"""
