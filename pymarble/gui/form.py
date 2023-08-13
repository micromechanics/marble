""" Editor to change metadata of binary file """
import struct
from typing import Optional
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox, \
                              QSpinBox, QCheckBox, QWidget, QTextEdit  # pylint: disable=no-name-in-module
from ..section import Section
from .style import IconButton, widgetAndLayout
from .communicate import Communicate

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
    self.translatePlot     = {'f':'plot numerical value','d':'plot numerical value','b':'plot byte value',\
                              'B':'plot byte value','c':'plot byte value'}
    self.translateDtype    = {'f':'float = 4bytes','d':'double = 8bytes','b':'byte = 1byte', \
                              'i':'int = 4bytes','B':'byte = 1byte','c':'character = 1byte'}
    self.translateDtypeInv = {v: k for k, v in self.translateDtype.items()}
    #definitions: no self.length etc. since content of textfields only truth
    section  = self.comm.binaryFile.content [start]
    self.lead = 20
    space = 20
    minSpace = 5

    # GUI elements
    self.setWindowTitle('Change section')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    mainL.setSpacing(space)

    #graph
    self.graphW, graphL = widgetAndLayout('V', mainL)
    self.graph = MplCanvas(self, width=5, height=4, dpi=100)
    graphToolbar = NavigationToolbar(self.graph, self)
    graphL.addWidget(graphToolbar)
    graphL.addWidget(self.graph)
    self.textEditW = QTextEdit()
    self.textEditW.hide()
    mainL.addWidget(self.textEditW)

    #buttons below graph
    _, graphButtonL = widgetAndLayout('H', mainL)
    graphButtonL.addSpacing(40)
    IconButton('fa.arrow-left',  self, ['startDown'], graphButtonL, 'reduce start point')
    IconButton('fa.arrow-right', self, ['startUp'],   graphButtonL, 'increase start point')
    graphButtonL.addSpacing(200)
    self.plotCB = QComboBox()
    self.plotCB.addItems(['plot numerical value','plot byte value','plot entropy',\
                          'print numerical value', 'print byte value'])
    self.plotCB.setCurrentText(self.translatePlot[section.dType])
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
    dimensionL.addWidget(self.startW, stretch=1)                           # type: ignore[call-arg]
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Length:'))
    self.lengthW = QSpinBox()
    self.lengthW.setRange(0, self.comm.binaryFile.fileLength)
    self.lengthW.setValue(section.length)
    dimensionL.addWidget(self.lengthW, stretch=1)                          # type: ignore[call-arg]
    dimensionL.addSpacing(minSpace)
    self.dTypeCB = QComboBox()
    self.dTypeCB.setToolTip('data type')
    self.dTypeCB.addItems(list(self.translateDtype.values()))
    self.dTypeCB.setCurrentText(self.translateDtype[section.dType])
    self.dTypeCB.currentTextChanged.connect(self.refresh)
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
    self.dClassCB.addItems(['metadata','primary','unknown'])
    self.dClassCB.setCurrentText(section.dClass)
    dClassL.addWidget(self.dClassCB)
    dClassL.addSpacing(space)
    dClassL.addWidget(QLabel('Link:'))
    self.linkW = QLineEdit(section.link,self)
    self.linkW.setStyleSheet('background-color:#d8e0f4')
    dClassL.addWidget(self.linkW)

    #TODO_P1 refresh table after save
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
    start       = int(self.startW.text())
    length      = int(self.lengthW.text())
    dType       = self.translateDtypeInv[self.dTypeCB.currentText()]
    byteSize    = struct.calcsize(dType)
    startAll    = start-self.lead*byteSize
    lengthAll   = length+2*self.lead
    dTypeAll    = str(lengthAll)+dType
    byteSizeAll = struct.calcsize(dTypeAll)
    # use the values
    self.startW.setSingleStep(byteSize)
    self.comm.binaryFile.file.seek(startAll)
    dataAll = self.comm.binaryFile.file.read(byteSizeAll)
    if len(dataAll)<byteSizeAll:
      dataAll = dataAll+bytearray(byteSizeAll-len(dataAll))
    # depending on plot/print type
    if self.plotCB.currentText().endswith('byte value') or \
       (dType in ['b','B'] and self.plotCB.currentText().endswith('numerical value')):
      valuesX = np.arange(-self.lead*byteSize, (length+self.lead)*byteSize)
      valuesY = list(dataAll)
      labelY  = 'byte value'
      limitX  = length*byteSize
      limitY  = [0,255]
      lineStyle= '.'
    elif self.plotCB.currentText().endswith('numerical value'):
      valuesX = np.arange(-self.lead, length+self.lead)
      valuesY = list(struct.unpack(dTypeAll, dataAll))
      labelY  = 'numerical value'
      limitX  = length
      limitY  = [np.min(valuesY[self.lead:-self.lead])*0.8, np.max(valuesY[self.lead:-self.lead])*1.2]
      lineStyle= 'o-'
    elif self.plotCB.currentText().endswith('plot entropy'):
      dataBin = list(dataAll) #convert to byte-int
      blockSize = self.comm.binaryFile.optEntropy['blockSize']
      valuesX = np.arange(-self.lead*byteSize, (length+self.lead-blockSize)*byteSize, byteSize)
      valuesY = []
      for startI in valuesX:
        _, counts = np.unique(dataBin[startI:startI+blockSize], return_counts=True)
        valueI    = np.sum(-counts/blockSize*np.log2(counts/blockSize))
        valuesY.append(valueI)
      labelY  = 'entropy'
      limitX  = (length-blockSize)*byteSize
      limitY  = [0, 7.8]
      lineStyle= '-'
    else:
      print('**ERROR unknown value in form')
    # graph / print
    if self.plotCB.currentText().startswith('plot'):
      self.graph.axes.cla()                        # Clear the canvas.
      self.graph.axes.axvline(0, color='k')
      self.graph.axes.axvline(limitX, color='k')
      self.graph.axes.plot(valuesX, valuesY, lineStyle)
      self.graph.axes.set_ylim(limitY)
      self.graph.axes.set_xlabel('bytes')
      self.graph.axes.set_ylabel(labelY)
      self.graph.draw() # Trigger the canvas to update and redraw.
      self.textEditW.hide()
      self.graph.show()
    elif self.plotCB.currentText().startswith('print'):
      self.textEditW.show()
      idxStart = np.argmin(np.abs(valuesX))
      idxEnd   = np.argmin(np.abs(valuesX-limitX))
      if labelY == 'numerical value':
        text  = '  '.join([f'{i:.3e}'     for i in valuesY[:idxStart]])
        text += ' '+'  '.join([f'**{i:.3e}**' for i in valuesY[idxStart:idxEnd]])
        text += ' '+'  '.join([f'{i:.3e}'     for i in valuesY[idxEnd:]])
      else:
        text  = self.comm.binaryFile.byteToString(dataAll[:idxStart], 1, 8)
        text += '  **'+self.comm.binaryFile.byteToString(dataAll[idxStart:idxEnd], 1, 8)+'**  '
        text += self.comm.binaryFile.byteToString(dataAll[idxEnd:], 1, 8)
      self.textEditW.setMarkdown(text)
      self.graph.hide()
    else:
      print('**ERROR unknown value in plot/print')
    return


  def execute(self, command:list[str]) -> None:
    """
    Execute action

    Args:
      command (list): command to be executed
    """
    start    = int(self.startW.text())
    length   = int(self.lengthW.text())
    dType    = self.translateDtypeInv[self.dTypeCB.currentText()]
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
    else:
      print(f"Command unknown {command}")
    self.startW.setValue(start)
    self.lengthW.setValue(length)
    self.refresh()
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
      start = int(self.startW.text())
      section = Section(length=int(self.lengthW.text()),
                        dType=self.translateDtypeInv[self.dTypeCB.currentText()],
                        key=self.keyW.text(), unit=self.unitW.text(), value=self.valueW.text(),
                        link=self.linkW.text(), dClass=self.dClassCB.currentText(),
                        count=[int(i) for i in self.countW.text()[1:-1].split(',') if len(i)>0],
                        shape=[int(i) for i in self.shapeW.text()[1:-1].split(',') if len(i)>0],
                        prob=200,
                        entropy=float(self.entropyW.text()),
                        important=self.importantW.isChecked()
                        )
      #first save section with semi-infinite probability, fill/clean, save real section
      self.comm.binaryFile.content[start] = section
      self.comm.binaryFile.fill()                                 # type: ignore[misc]
      section.prob = int(self.probabilityW.text())
      self.comm.binaryFile.content[start] = section
      self.accept()
    else:
      print('metaEditor: did not get a fitting btn ',btn.text())
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
