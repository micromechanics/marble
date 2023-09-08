""" Editor to change metadata of binary file """
import struct, logging
from typing import Optional
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox, \
                              QSpinBox, QCheckBox, QWidget, QTextEdit  # pylint: disable=no-name-in-module
from PySide6.QtGui import QFont  # pylint: disable=no-name-in-module
from ..section import Section
from .style import IconButton, widgetAndLayout
from .communicate import Communicate
from .terminologyLookup import TerminologyLookup
from .defaults import WARNING_LARGE_DATA, translateDtype, translateDtypeInv, translatePlot

class Form(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, comm:Communicate, start:int):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      start (int): location of section which should be edited
    """
    super().__init__()
    self.comm = comm
    if self.comm.binaryFile is None:
      return
    self.colorbarPresent = False
    #definitions: no self.length etc. since content of textfields only truth
    section  = self.comm.binaryFile.content[start]
    self.lengthInitial = int(section.length)
    self.lead = 20
    self.critPlot = 50000
    self.critPrint= 200
    space = 20
    minSpace = 5

    # GUI elements
    self.setWindowTitle('Change section')
    self.setMinimumWidth(1050)  #set size to match 4 blocks of 8bytes
    mainL = QVBoxLayout(self)
    mainL.setSpacing(space)

    #graph
    self.graphW, graphL = widgetAndLayout('V', None)
    self.graph = MplCanvas(self, width=5, height=4, dpi=100)
    self.graphToolbar = NavigationToolbar(self.graph, self)
    graphL.addWidget(self.graphToolbar)
    graphL.addWidget(self.graph)
    mainL.addWidget(self.graphW, stretch=1)
    self.textEditW = QTextEdit()
    self.textEditW.hide()
    self.textEditW.setReadOnly(True)
    self.textEditW.setFont(QFont('Monospace', pointSize=12))
    mainL.addWidget(self.textEditW, stretch=1)

    #buttons below graph
    _, graphButtonL = widgetAndLayout('H', mainL)
    graphButtonL.addSpacing(40)
    IconButton('fa.arrow-left',  self, ['startDown'], graphButtonL, 'reduce start point')
    IconButton('fa.arrow-right', self, ['startUp'],   graphButtonL, 'increase start point')
    graphButtonL.addSpacing(200)
    self.plotCB = QComboBox()
    plotTypes = ['plot numerical value', 'plot byte value', 'plot entropy','2D graph of numerical value',
                 'print numerical value','print byte value','print character']
    if section.length > self.critPrint:
      plotTypes += ['warning']
    self.plotCB.addItems(plotTypes)
    self.plotCB.setCurrentText(translatePlot[section.dType])
    if section.length > self.critPlot:
      self.plotCB.setCurrentText('warning')
    self.plotCB.currentTextChanged.connect(self.refresh)
    # plotComboBox.changeEvent()
    graphButtonL.addWidget(self.plotCB)
    graphButtonL.addSpacing(200)
    IconButton('fa.arrow-left',  self, ['endDown'],   graphButtonL, 'reduce end point')
    IconButton('fa.arrow-right', self, ['endUp'],     graphButtonL, 'increase end point')
    graphButtonL.addSpacing(40)

    #dimensions
    _, dimensionL = widgetAndLayout('H', mainL)
    dimensionL.addWidget(QLabel('Start:'))
    self.startW = QSpinBox()
    self.startW.setRange(0, self.comm.binaryFile.fileLength)
    self.startW.setSingleStep(struct.calcsize(section.dType))
    self.startW.setValue(start)
    self.startW.valueChanged.connect(self.refresh)
    dimensionL.addWidget(self.startW, stretch=1)                           # type: ignore[call-arg]
    dimensionL.addSpacing(space)
    self.lengthLabelW = QLabel('Length:')
    dimensionL.addWidget(self.lengthLabelW)
    self.lengthW = QSpinBox()
    self.lengthW.setRange(0, self.comm.binaryFile.fileLength)
    self.lengthW.setValue(section.length)
    self.lengthW.valueChanged.connect(self.refresh)
    dimensionL.addWidget(self.lengthW, stretch=1)                          # type: ignore[call-arg]
    self.heightWidthW, heightWidthL = widgetAndLayout('H', dimensionL)
    if len(section.shape)==2:
      self.widthW = QLineEdit(str(section.shape[0]))
      self.heightW = QLineEdit(str(section.shape[1]))
    else:
      self.widthW = QLineEdit('1024')
      self.heightW = QLineEdit('1024')
    heightWidthL.addWidget(QLabel('Width:'))
    self.widthW.textChanged.connect(self.refresh)
    heightWidthL.addWidget(self.widthW, stretch=1)                          # type: ignore[call-arg]
    heightWidthL.addSpacing(minSpace)
    heightWidthL.addWidget(QLabel('Height:'))
    self.heightW.textChanged.connect(self.refresh)
    heightWidthL.addWidget(self.heightW, stretch=1)                          # type: ignore[call-arg]
    self.heightWidthW.setHidden(True)
    dimensionL.addSpacing(minSpace)
    self.dTypeCB = QComboBox()
    self.dTypeCB.setToolTip('data type')
    self.dTypeCB.addItems(list(translateDtype.values()))
    self.dTypeCB.setCurrentText(translateDtype[section.dType.lower()])
    self.dTypeCB.currentTextChanged.connect(lambda: self.execute(['changeDtype']))
    dimensionL.addWidget(self.dTypeCB)
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Probability:'))
    self.probabilityW = QSpinBox()
    self.probabilityW.setRange(1, 100)
    self.probabilityW.setSingleStep(20)
    self.probabilityW.setValue(section.prob)
    dimensionL.addWidget(self.probabilityW)
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Important:'))
    self.importantW = QCheckBox()
    self.importantW.setChecked(section.important)
    dimensionL.addWidget(self.importantW)

    #key value unit
    _, keyValueL = widgetAndLayout('H', mainL)
    self.keyW = QLineEdit(section.key,self)
    self.keyW.setToolTip('key')
    self.keyW.setStyleSheet('background-color:#d8e0f4')
    keyValueL.addWidget(self.keyW)
    keyValueL.addWidget(QLabel('  :  '))
    self.valueW = QLineEdit(section.value,self)
    self.valueW.setToolTip('value')
    keyValueL.addWidget(self.valueW, stretch=1)                     # type: ignore[call-arg]
    keyValueL.addWidget(QLabel('Auto'))
    self.autoW = QCheckBox()
    self.autoW.setChecked(False)
    keyValueL.addWidget(self.autoW)
    keyValueL.addSpacing(space)
    keyValueL.addWidget(QLabel('Unit:'))
    self.unitW = QLineEdit(section.unit,self)
    self.unitW.setStyleSheet('background-color:#d8e0f4')
    self.unitW.setMaximumWidth(60)
    keyValueL.addWidget(self.unitW)

    #dClass etc.
    _, dClassL = widgetAndLayout('H', mainL)
    dClassL.addWidget(QLabel('dClass:'))
    self.dClassCB = QComboBox()
    self.dClassCB.addItems(['metadata','primary','unknown','count'])
    self.dClassCB.setCurrentText(section.dClass)
    dClassL.addWidget(self.dClassCB)
    dClassL.addSpacing(space)
    dClassL.addWidget(QLabel('Link:'))
    self.linkW = QLineEdit(section.link,self)
    self.linkW.setStyleSheet('background-color:#d8e0f4')
    dClassL.addWidget(self.linkW)
    IconButton('fa5s.search', self, ['terminologyLookup'], dClassL, 'Lookup from terminology servers')

    if 'advanced' in self.comm.configuration:
      # advanced items
      _, advancedL = widgetAndLayout('H', mainL)
      advancedL.addWidget(QLabel('Count:'))
      self.countW = QLineEdit(str(section.count),self)
      advancedL.addWidget(self.countW)
      advancedL.addSpacing(space)
      advancedL.addWidget(QLabel('Shape:'))
      self.shapeW = QLineEdit(str(section.shape),self)
      advancedL.addWidget(self.shapeW)
      advancedL.addSpacing(space)
      advancedL.addWidget(QLabel('Entropy:'))
      self.entropyW = QLineEdit(str(section.entropy),self)
      advancedL.addWidget(self.entropyW)

    if section.dClass == 'count':
      self.startW.setDisabled(True)
      self.lengthW.setDisabled(True)
      self.dTypeCB.setDisabled(True)
      self.probabilityW.setDisabled(True)
      self.importantW.setDisabled(True)
      self.keyW.setDisabled(True)
      self.valueW.setDisabled(True)
      self.unitW.setDisabled(True)
      self.linkW.setDisabled(True)
      self.countW.setDisabled(True)
      self.shapeW.setDisabled(True)
      self.entropyW.setDisabled(True)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)
    self.refresh()


  def refresh(self) -> None:
    """ repaint form incl. graph """
    if self.comm.binaryFile is None:
      return
    # get values from text fields
    if self.plotCB.currentText().startswith('2D graph'):
      self.lengthW.setHidden(True)
      self.lengthLabelW.setHidden(True)
      self.heightWidthW.setHidden(False)
      self.lengthW.setValue(int(self.widthW.text())*int(self.heightW.text()))
      lead = 0
    else:
      self.lengthW.setHidden(False)
      self.lengthLabelW.setHidden(False)
      self.heightWidthW.setHidden(True)
      lead = self.lead
    start       = self.startW.value()
    length      = self.lengthW.value()
    dType       = translateDtypeInv[self.dTypeCB.currentText()]
    byteSize    = struct.calcsize(dType)
    startAll    = start-lead*byteSize
    lengthAll   = length+2*lead
    dTypeAll    = str(lengthAll)+dType
    byteSizeAll = struct.calcsize(dTypeAll)
    preData = bytearray(0)
    if startAll < 0:
      preData = bytearray(-startAll)
      startAll = 0
    # use the values
    self.startW.setSingleStep(byteSize)
    self.comm.binaryFile.file.seek(startAll)
    dataAll = self.comm.binaryFile.file.read(byteSizeAll)
    if len(preData)>1:
      dataAll = preData + dataAll[:-len(preData)]
    if len(dataAll)<byteSizeAll:
      dataAll = dataAll + bytearray(byteSizeAll-len(dataAll))
    # depending on plot/print type
    if self.plotCB.currentText().endswith('byte value') or self.plotCB.currentText().endswith('character') or\
       (dType in {'b', 'B'} and self.plotCB.currentText().endswith('numerical value')):
      valuesX = np.arange(-lead*byteSize, (length+lead)*byteSize)
      self.valuesY = list(dataAll)
      limitX  = length*byteSize
      labelY  = 'byte value'
      limitY  = [0.0, 255.0]
      lineStyle= '.'
    elif self.plotCB.currentText().endswith('numerical value'):
      valuesX = np.arange(-lead, length+lead)
      self.valuesY = list(struct.unpack(dTypeAll, dataAll))
      limitX  = length
      labelY  = 'numerical value'
      limitY  = [np.min(self.valuesY[self.lead:-self.lead])*0.8,  #here self.lead to prevent it from being 0
                 np.max(self.valuesY[self.lead:-self.lead])*1.2]
      lineStyle= 'o-'
    elif self.plotCB.currentText().endswith('plot entropy'):
      dataBin = list(dataAll) #convert to byte-int
      blockSize = self.comm.binaryFile.optEntropy['blockSize']
      valuesX = np.arange(-lead*byteSize, (length+lead-blockSize)*byteSize, byteSize)
      self.valuesY = []
      for startI in valuesX:
        _, counts = np.unique(dataBin[startI:startI+blockSize], return_counts=True)
        valueI    = np.sum(-counts/blockSize*np.log2(counts/blockSize))
        self.valuesY.append(valueI)
      labelY  = 'entropy'
      limitX  = (length-blockSize)*byteSize
      limitY  = [0.0, 7.8]
      lineStyle= '-'
    elif not self.plotCB.currentText().endswith('warning'):
      logging.error('unknown value in form')
    # graph / print
    if self.plotCB.currentText().startswith('plot'):
      if len(dataAll)>self.critPlot:
        scaleDown = max(int(length/self.critPlot), 1)
        logging.info('Data too large: plot only every %sth point', scaleDown)
        valuesX = valuesX[::scaleDown]
        self.valuesY = self.valuesY[::scaleDown]
      self.graph.axes.cla()                        # Clear the canvas.
      self.graph.axes.axvline(0, color='k')
      self.graph.axes.axvline(limitX-1, color='k')  #plot from 0 to limit-1
      self.graph.axes.plot(valuesX, self.valuesY, lineStyle)
      self.graph.axes.set_ylim(limitY)
      self.graph.axes.set_xlabel('bytes')
      self.graph.axes.set_ylabel(labelY)
      self.graph.draw() # Trigger the canvas to update and redraw.
      self.textEditW.hide()
      self.graphToolbar.show()
      self.graph.show()
    elif self.plotCB.currentText().startswith('2D graph'):
      width, height = int(self.widthW.text()), int(self.heightW.text())
      self.graph.axes.cla()                        # Clear the canvas.
      img = self.graph.axes.imshow(np.reshape(self.valuesY, (height, width)), cmap='Greys_r')
      if not self.colorbarPresent:
        self.graph.axes.get_figure().colorbar(img)
        self.colorbarPresent = True
      self.graph.draw() # Trigger the canvas to update and redraw.
      self.textEditW.hide()
      self.graphToolbar.show()
      self.graph.show()
    elif self.plotCB.currentText().startswith('print'): #many bugs and formating issues -> to html
      # - if integer and integer is small print as 0001
      if len(dataAll)>self.critPrint:
        scaleDown = max(int(length/self.critPrint), 1)
        logging.info('Data too large: print only every %sth point', scaleDown)
        valuesX = valuesX[::scaleDown]
        self.valuesY = self.valuesY[::scaleDown]
        dataAll = dataAll[::scaleDown]
      self.textEditW.show()
      idxStart = np.argmin(np.abs(valuesX))
      idxEnd   = np.argmin(np.abs(valuesX-limitX))
      if labelY == 'numerical value':
        if np.all(self.valuesY[idxStart:idxEnd])<1000 and dType in {'f','d'}:
          style1, style2 = '7.3f', '.3f'
        elif np.all(self.valuesY[idxStart:idxEnd])<10000 and dType in {'i'}:
          style1, style2 = '6', '6'
        else:
          style1, style2 = '9.3e', '.3e'
        text  =     ' '.join([f'<font color="#888888">{i:{style1}}</font>' for i in self.valuesY[:idxStart]])
        text += ' '+' '.join([f'<b>{i:{style2}}</b>'                 for i in self.valuesY[idxStart:idxEnd]])
        text += ' '+' '.join([f'<font color="#888888">{i:{style1}}</font>' for i in self.valuesY[idxEnd:]])
        self.textEditW.setHtml(text)
      elif self.plotCB.currentText().endswith('byte value'):
        textArray = self.comm.binaryFile.byteToString(dataAll, 1).split(' ')
        textArray = [f'<font color="#888888">{i}</font>' for i in textArray[:self.lead]]+ \
                    [f'<b>{i}</b>'                       for i in textArray[self.lead:-self.lead]]+ \
                    [f'<font color="#888888">{i}</font>' for i in textArray[-self.lead:]]
        text  = ' _ '.join([' '.join(textArray[i:i+8]) for i in range(0, len(textArray), 8)])
        self.textEditW.setHtml(text)
      else: #character
        text = bytearray(dataAll).decode('utf-8', errors='replace').replace('\x00','~')
        text = f'<font color="#888888">{text[:idxStart]}</font><b>{text[idxStart:idxEnd]}</b>'+\
               f'<font color="#888888">{text[idxEnd:]}</font>'
        self.textEditW.setHtml(text)
      self.graph.hide()
      self.graphToolbar.hide()
    elif self.plotCB.currentText().endswith('warning'):
      self.textEditW.show()
      htmlText = WARNING_LARGE_DATA.replace('$max_plot$',str(self.critPlot))\
                      .replace('$max_print$',str(self.critPrint))\
                      .replace('$scale$',f'{int(length/self.critPlot)}th /{int(length/self.critPrint)}th')
      self.textEditW.setHtml(htmlText)
      self.graph.hide()
      self.graphToolbar.hide()
    else:
      logging.error('unknown value in plot/print')
    return


  def execute(self, command:list[str]) -> None:
    """
    Execute action

    Args:
      command (list): command to be executed
    """
    start    = int(self.startW.text())
    length   = int(self.lengthW.text())
    dType    = translateDtypeInv[self.dTypeCB.currentText()]
    byteSize = struct.calcsize(dType)
    if command[0] == 'startDown':
      start -= byteSize
      length+= 1
    elif command[0] == 'startUp':
      start += byteSize
      length-= 1
    elif command[0] == 'endDown':
      length -= 1
    elif command[0] == 'endUp':
      length += 1
    elif command[0] == 'changeDtype':
      length = int(self.lengthInitial/byteSize)
    elif command[0] == 'terminologyLookup':
      dialog = TerminologyLookup([self.keyW.text()])
      dialog.exec()
      self.linkW.setText(' '.join(dialog.returnValues[0]))
    else:
      logging.error('Command unknown %s', command)
    self.startW.setValue(start)
    self.lengthW.setValue(length)
    self.refresh()
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
      start  = self.startW.value()
      length = self.lengthW.value()
      dType  = translateDtypeInv[self.dTypeCB.currentText()]
      shape  = [int(i) for i in self.shapeW.text()[1:-1].split(',') if len(i)>0]
      binaryFile = self.comm.binaryFile
      #find count in file
      if dType in {'f','d','H'}:
        lengthSearch = min(length, int(np.prod(shape))) #remember garbage at end of data-set
        #create link / enter property count; adopt shape correspondingly
        count =[self.comm.binaryFile.findAnchor(lengthSearch, start)[0]]     # type: ignore[misc]
        shape = []
        for iCount in count:
          if iCount<0:
            shape.append(-1)
          else:
            binaryFile.file.seek(iCount)
            iLength = binaryFile.file.read(binaryFile.content[iCount].byteSize())
            iLength = struct.unpack( binaryFile.content[iCount].size(), iLength)[0]
            shape.append(int(iLength))
      else:
        count  = [int(i) for i in self.countW.text()[1:-1].split(',') if len(i)>0]
        if dType in {'b', 'c'}:  #check if small b=random bytes or B=zeros
          self.comm.binaryFile.file.seek(start)
          data = self.comm.binaryFile.file.read(length)
          if dType == 'b':
            dType = 'B' if np.all(np.array(list(data), dtype=np.uint8)==0) else 'b'
      value = self.valueW.text()
      if self.autoW.isChecked():
        mean    = np.mean(self.valuesY[self.lead:-self.lead])  #here self.lead to prevent it from being 0
        minimum = np.min(self.valuesY[self.lead:-self.lead])
        maximum = np.max(self.valuesY[self.lead:-self.lead])
        if dType=='f':
          value = f'{length} floats with mean {mean:.4f}, minimum {minimum:.4f}, maximum {maximum:.4f}'
        elif dType=='d':
          value = f'{length} doubles with mean {mean:.3e}, minimum {minimum:.3e}, maximum {maximum:.3e}'
        elif dType=='c':
          value = bytearray(data).decode('utf-8', errors='replace').replace('\x00','~')
        else:
          value = 'Unknown datatype'
      entropy = -1.0
      dClass = '' if self.dClassCB.currentText()=='unknown' else self.dClassCB.currentText()
      section = Section(length=length, dType=dType,
                        key=self.keyW.text(), unit=self.unitW.text(), value=value,
                        link=self.linkW.text(), dClass=dClass, count=count, shape=shape,
                        prob=200, entropy=entropy, important=self.importantW.isChecked())
      #first save section with semi-infinite probability, fill/clean, save real section
      binaryFile.content[start] = section
      binaryFile.fill()                                   # type: ignore[misc]
      section.prob = int(self.probabilityW.text())
      binaryFile.content[start] = section
      self.accept()
    else:
      logging.error('unknown command %s', btn.text())
    return


class MplCanvas(FigureCanvas):
  """ Canvas to draw upon """
  def __init__(self, _:Optional[QWidget]=None, width:float=5, height:float=4, dpi:int=100):
    """
    Args:
      width (float): width in inch
      height (float): height in inch
      dpi (int): dots per inch
    """
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = fig.add_subplot(111)
    super().__init__(fig)
