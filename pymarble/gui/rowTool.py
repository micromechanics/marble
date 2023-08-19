""" Editor to identify data saved in rows """
import struct, logging
from typing import Optional
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox, \
                              QSpinBox, QCheckBox, QWidget  # pylint: disable=no-name-in-module
from ..section import Section
from .style import IconButton, widgetAndLayout
from .communicate import Communicate
from .defaults import translateDtype, translateDtypeInv

class RowTool(QDialog):
  """ Editor to identify data saved in rows """
  def __init__(self, comm:Communicate):
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
    self.space = 20

    # GUI elements
    self.setWindowTitle('Identify rows of data')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    mainL.setSpacing(self.space)

    #graph
    self.graphW, graphL = widgetAndLayout('V', mainL)
    self.graph = MplCanvas(self, width=5, height=4, dpi=100)
    self.graphToolbar = NavigationToolbar(self.graph, self)
    graphL.addWidget(self.graphToolbar)
    graphL.addWidget(self.graph, stretch=1)                               # type: ignore[call-arg]

    #main row
    content = self.comm.binaryFile.content
    _, startBarL = widgetAndLayout('H', mainL)
    #Text format: if you change here: change also below
    segmentLabels = {i:f'start: {i} - {content[i].value}' for i in content if content[i].dClass=='primary'}
    segmentLabels[-1] = 'Custom start, length, dType'
    self.start         = list(segmentLabels.keys())[-2]
    self.sectionCB = QComboBox()
    self.sectionCB.addItems(list(segmentLabels.values()))
    self.sectionCB.setCurrentText(segmentLabels[self.start])
    self.sectionCB.currentTextChanged.connect(lambda: self.execute(['comboBox']))
    startBarL.addWidget(self.sectionCB, stretch=1)                        # type: ignore[call-arg]
    startBarL.addSpacing(self.space*2)
    startBarL.addWidget(QLabel('Row number:'))
    self.numberW = QSpinBox()
    self.numberW.setRange(2, 100)
    self.numberW.setSingleStep(1)
    self.numberW.valueChanged.connect(lambda: self.execute(['changeNumber']))
    startBarL.addWidget(self.numberW)

    #row custom for dimensions
    self.dimensionsW, dimensionL = widgetAndLayout('H', mainL)
    dimensionL.addWidget(QLabel('Start:'))
    self.startW = QSpinBox()
    self.startW.setRange(0, self.comm.binaryFile.fileLength)
    self.startW.setSingleStep(struct.calcsize(content[self.start].dType))
    self.startW.setValue(self.start)
    self.startW.valueChanged.connect(self.refresh)
    dimensionL.addWidget(self.startW, stretch=1)                           # type: ignore[call-arg]
    dimensionL.addSpacing(self.space)
    self.lengthLabelW = QLabel('Length:')
    dimensionL.addWidget(self.lengthLabelW)
    self.lengthW = QSpinBox()
    self.lengthW.setRange(0, self.comm.binaryFile.fileLength)
    self.lengthW.setValue(content[self.start].length)
    self.lengthW.valueChanged.connect(self.refresh)
    dimensionL.addWidget(self.lengthW, stretch=1)                          # type: ignore[call-arg]
    dimensionL.addSpacing(self.space)
    self.dTypeCB = QComboBox()
    self.dTypeCB.setToolTip('data type')
    self.dTypeCB.addItems(list(translateDtype.values()))
    self.dTypeCB.setCurrentText(translateDtype[content[self.start].dType])
    self.dTypeCB.currentTextChanged.connect(self.refresh)
    dimensionL.addWidget(self.dTypeCB)
    self.dimensionsW.hide()

    #custom rows: initial fill
    _, self.propertyRowsL  = widgetAndLayout('V', mainL)
    self.keyWs:list[QWidget]          = []
    self.unitWs:list[QWidget]         = []
    self.linkWs:list[QWidget]         = []
    self.plotWs:list[QWidget]         = []
    self.propertyRowsWs:list[QWidget] = []
    #   use existing data and fill
    rowFormatMeta = self.comm.binaryFile.rowFormatMeta
    numRows = max(2, len(rowFormatMeta))
    for i in range(numRows):
      self.addRow(i,    rowFormatMeta[i] if i<len(rowFormatMeta) else {} )
    self.numberW.setValue(numRows)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)
    self.refresh()


  def addRow(self, i:int, initValues:dict[str,str]={}) -> None:
    """
    Add a row for one plot-line to the interface

    Args:
      i (int): index of row to add
      initValues (dict): initial values
    """
    propertyRowW, propertyRowL = widgetAndLayout('H', self.propertyRowsL)
    propertyRowL.addWidget(QLabel(f'{i+1:02d}  plot:'))
    self.plotWs.append(QCheckBox())
    self.plotWs[i].setChecked(True)
    self.plotWs[i].stateChanged.connect(self.refresh)
    propertyRowL.addWidget(self.plotWs[i])
    propertyRowL.addSpacing(self.space)
    propertyRowL.addWidget(QLabel('key:'))
    self.keyWs.append(QLineEdit(initValues.get('key', '')))
    propertyRowL.addWidget(self.keyWs[i])
    propertyRowL.addSpacing(self.space)
    propertyRowL.addWidget(QLabel('unit:'))
    self.unitWs.append(QLineEdit(initValues.get('unit', '')))
    propertyRowL.addWidget(self.unitWs[i])
    propertyRowL.addSpacing(self.space)
    propertyRowL.addWidget(QLabel('link:'))
    self.linkWs.append(QLineEdit(initValues.get('link', '')))
    propertyRowL.addWidget(self.linkWs[i], stretch=1)             # type: ignore[call-arg]
    self.propertyRowsWs.append(propertyRowW)
    return


  def refresh(self) -> None:
    """ repaint form incl. graph """
    if self.comm.binaryFile is None:
      return
    if self.dimensionsW.isHidden():     #use given segment information
      start      = int(self.sectionCB.currentText().split(' - ')[0][7:]) #change here if text format changes
      self.start = start
      section    = self.comm.binaryFile.content[start]
      byteFormat = section.size()
      byteSize   = section.byteSize()
    else:                               #use information as given by this gui's start, length
      start      = self.startW.value()
      byteFormat = str(int(self.lengthW.text())*self.numberW.value())+\
                   translateDtypeInv[self.dTypeCB.currentText()]
      byteSize   = struct.calcsize(byteFormat)
    #use data
    self.comm.binaryFile.file.seek(start)
    dataBin = self.comm.binaryFile.file.read(byteSize)
    if len(dataBin)<byteSize:
      dataBin = dataBin + bytearray(byteSize-len(dataBin))
    data = struct.unpack(byteFormat, dataBin)
    self.graph.axes.cla()                        # Clear the canvas
    numberCurves = self.numberW.value()
    for i in range(numberCurves):
      if self.plotWs[i].isChecked():
        label = self.keyWs[i].text() or f'curve {i+1}'
        self.graph.axes.plot(data[i::numberCurves], '.-', label=label)
    self.graph.axes.legend()
    self.graph.axes.set_xlabel('increment')
    self.graph.axes.set_ylabel('numerical value')
    self.graph.draw() # Trigger the canvas to update and redraw.
    return


  def execute(self, command:list[str]) -> None:
    """
    Execute action

    Args:
      command (list): command to be executed
    """
    if self.comm.binaryFile is None:
      return
    if command[0] == 'changeNumber':
      while self.numberW.value() != len(self.plotWs):
        if   self.numberW.value() > len(self.plotWs):
          self.addRow(self.numberW.value()-1)
        elif self.numberW.value() < len(self.plotWs):
          self.keyWs.pop()
          self.unitWs.pop()
          self.linkWs.pop()
          self.plotWs.pop()
          widget = self.propertyRowsWs.pop()
          widget.setParent(None)                                                  # type: ignore[call-overload]
    elif command[0] == 'comboBox' and self.sectionCB.currentText()=='Custom start, length, dType':
      self.dimensionsW.show()
      self.sectionCB.hide()
      self.numberW.setEnabled(False)
      self.startW.setValue(self.start)
      section = self.comm.binaryFile.content[self.start]
      self.lengthW.setValue(int(section.length/self.numberW.value()))
      self.dTypeCB.setCurrentText(translateDtype[section.dType])
      self.refresh()
    self.refresh()
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
      if self.dimensionsW.isHidden():
        start      = self.start
        section    = self.comm.binaryFile.content[start]
        shape      = [int(section.length/self.numberW.value()), self.numberW.value()]
      else:
        start      = self.startW.value()
        shape      = [int(self.lengthW.text()), self.numberW.value()]
      count = [self.comm.binaryFile.findAnchor(shape[0], start)[0],                   # type: ignore[misc]
               self.comm.binaryFile.findAnchor(shape[1], start)[0]]                   # type: ignore[misc]
      section = Section(length=int(np.prod(shape)), dType=translateDtypeInv[self.dTypeCB.currentText()],
                        key='primary data in rows', value='primary data in rows', dClass='primary',
                        shape=shape, count=count, prob=100, important=True, entropy=-1)
      del self.comm.binaryFile.content[self.start]
      self.comm.binaryFile.content[start] = section
      self.comm.binaryFile.rowFormatMeta = [{'key':self.keyWs[i].text(), 'unit':self.unitWs[i].text(),
                                            'link':self.linkWs[i].text()} for i in range(self.numberW.value())]
      self.comm.binaryFile.rowFormatSegments.add(start)
      self.comm.changeTable.emit()
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
