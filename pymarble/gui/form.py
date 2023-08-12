""" Editor to change metadata of binary file """
import struct
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox  # pylint: disable=no-name-in-module
from ..section import Section
from .style import IconButton, widgetAndLayout
from .communicate import Communicate

class Form(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, comm:Communicate, start):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    if self.comm.binaryFile is None:
      return
    self.translatePlot     = {'f':'numerical value','d':'numerical value','b':'byte value'}
    self.translateDtype    = {'f':'float = 4bytes','d':'double = 8bytes','b':'byte = 1byte', 'i':'int = 4bytes'}
    self.translateDtypeInv = {v: k for k, v in self.translateDtype.items()}
    #definitions
    section  = self.comm.binaryFile.content [start]  #no self.length etc. since content of textfields only truth
    self.lead = 20
    space = 20
    minSpace = 5

    # GUI elements
    self.setWindowTitle('Change section')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    mainL.setSpacing(space)

    #TODO_P2:
    # - plot of binary not the same as values of binary
    # - add text output of data/binary instead of graph
    # - verify entropy plot
    # - simplify refresh: x axis always bytes,....
    # - toolbar does not render correctly
    #graph
    _, graphL = widgetAndLayout('V', mainL)
    self.graph = MplCanvas(self, width=5, height=4, dpi=100)
    graphToolbar = NavigationToolbar(self.graph, self)
    graphL.addWidget(graphToolbar)
    graphL.addWidget(self.graph)

    #buttons below graph
    _, graphButtonL = widgetAndLayout('H', mainL)
    graphButtonL.addSpacing(40)
    IconButton('fa.arrow-left',  self, ['startDown'], graphButtonL, 'reduce start point')
    IconButton('fa.arrow-right', self, ['startUp'],   graphButtonL, 'increase start point')
    graphButtonL.addSpacing(200)
    self.plotCB = QComboBox()
    self.plotCB.addItems(['numerical value','byte value','entropy'])
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
    dimensionL.addWidget(self.startW, stretch=1)
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Length:'))
    self.lengthW = QSpinBox()
    self.lengthW.setRange(0, self.comm.binaryFile.fileLength)
    self.lengthW.setValue(section.length)
    dimensionL.addWidget(self.lengthW, stretch=1)
    dimensionL.addSpacing(minSpace)
    self.dTypeCB = QComboBox()
    self.dTypeCB.setToolTip('data type')
    self.dTypeCB.addItems(self.translateDtype.values())
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
    keyValueL.addWidget(self.keyW)
    keyValueL.addWidget(QLabel('  :  '))
    self.valueW = QLineEdit(section.value,self)
    self.valueW.setToolTip('value')
    keyValueL.addWidget(self.valueW, stretch=1)
    keyValueL.addSpacing(space)
    keyValueL.addWidget(QLabel('Unit:'))
    self.unitW = QLineEdit(section.unit,self)
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
    dClassL.addWidget(self.linkW)

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


  def refresh(self):
    # get values from text fields
    start  = int(self.startW.text())
    length = int(self.lengthW.text())
    dType  = self.translateDtypeInv[self.dTypeCB.currentText()]
    byteSize = struct.calcsize(dType)
    totalByteSize = str(length+2*self.lead)+dType
    self.startW.setSingleStep(byteSize)
    # make graph
    self.comm.binaryFile.file.seek(start-self.lead*byteSize)
    data = self.comm.binaryFile.file.read(struct.calcsize(totalByteSize))
    if len(data)<struct.calcsize(totalByteSize):
      data = data+bytearray(struct.calcsize(totalByteSize)-len(data))
    self.graph.axes.cla()                        # Clear the canvas.
    #    self.plotCB.addItems(['numerical value',,'entropy'])
    if self.plotCB.currentText()=='byte value':
      self.graph.axes.axvline(0, color='k')
      self.graph.axes.axvline(length*byteSize, color='k')
      valuesX = np.arange(-self.lead*byteSize, (length+self.lead)*byteSize)
      valuesY = list(data)
      self.graph.axes.plot(valuesX, valuesY, '.')
      self.graph.axes.set_ylim([0,255])
      self.graph.axes.set_xlabel('byte offset')
      self.graph.axes.set_ylabel('binary value')
    elif self.plotCB.currentText()=='numerical value':
      self.graph.axes.axvline(0, color='k')
      self.graph.axes.axvline(length, color='k')
      valuesX = np.arange(-self.lead, length+self.lead)
      valuesY = struct.unpack(totalByteSize, data) #get data
      self.graph.axes.plot(valuesX, valuesY, '-o')
      self.graph.axes.set_ylim(np.min(valuesY[self.lead:-self.lead])*0.8,np.max(valuesY[self.lead:-self.lead])*1.2)
      self.graph.axes.set_xlabel('increment')
      self.graph.axes.set_ylabel('numerical value')
    elif self.plotCB.currentText()=='entropy':
      data = struct.unpack(totalByteSize, data) #convert to byte-int
      blockSize = self.comm.binaryFile.optEntropy['blockSize']
      valuesX = np.arange(-self.lead*byteSize, (len(data)-blockSize-self.lead)*byteSize,
                          self.comm.binaryFile.optEntropy['skipEvery'])
      valuesY = []
      for startI in valuesX:
        _, counts = np.unique(data[startI:startI+blockSize], return_counts=True)
        counts    = counts/blockSize
        value    = np.sum(-counts*np.log2(counts))
        valuesY.append(value)
      self.graph.axes.axvline(0, color='k')
      self.graph.axes.axvline(len(data)-self.lead*byteSize, color='k')
      self.graph.axes.plot(valuesX, valuesY, '-o')
      self.graph.axes.set_ylim([0,8])
      self.graph.axes.set_xlabel('byte offset')
      self.graph.axes.set_ylabel('entropy')
    else:
      print('**ERROR unknown value')
    self.graph.draw() # Trigger the canvas to update and redraw.
    return


  def execute(self, command:list[str]) -> None:
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
      self.comm.binaryFile.fill()
      section.prob = int(self.probabilityW.text())
      self.comm.binaryFile.content[start] = section
      self.accept()
    else:
      print('metaEditor: did not get a fitting btn ',btn.text())
    return


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
