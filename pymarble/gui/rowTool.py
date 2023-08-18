""" Editor to identify data saved in rows """
import struct, re, logging
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
from .defaults import WARNING_LARGE_DATA

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
    minSpace = 5

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
    graphL.addWidget(self.graph, stretch=1)

    #main row
    content = self.comm.binaryFile.content
    _, startBarL = widgetAndLayout('H', mainL)
    segmentLabels = {i:f'start: {i} - {content[i].value}' for i in content if content[i].dClass=='primary'}
    segmentLabels[-1] = 'Custom start, length, dType'
    self.start         = list(segmentLabels.keys())[-2]
    self.sectionCB = QComboBox()
    self.sectionCB.addItems(segmentLabels.values())
    self.sectionCB.setCurrentText(segmentLabels[self.start])
    self.sectionCB.currentTextChanged.connect(lambda: self.execute(['comboBox']))
    startBarL.addWidget(self.sectionCB, stretch=1)
    startBarL.addSpacing(self.space*2)
    startBarL.addWidget(QLabel('Row number:'))
    self.numberW = QSpinBox()
    self.numberW.setRange(2, 100)
    self.numberW.setSingleStep(1)
    self.numberW.valueChanged.connect(lambda: self.execute(['changeNumber']))
    startBarL.addWidget(self.numberW)

    #custom rows
    _, self.propertyRowsL = widgetAndLayout('V', mainL)
    self.keyWs = []
    self.unitWs= []
    self.linkWs= []
    self.plotWs= []
    self.propertyRowsWs = []
    for i in range(2):
      self.addRow(i)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)
    self.refresh()


  def addRow(self, i):
    propertyRowW, propertyRowL = widgetAndLayout('H', self.propertyRowsL)
    propertyRowL.addWidget(QLabel('key:'))
    self.keyWs.append(QLineEdit(''))
    propertyRowL.addWidget(self.keyWs[i])
    propertyRowL.addSpacing(self.space)
    propertyRowL.addWidget(QLabel('unit:'))
    self.unitWs.append(QLineEdit(''))
    propertyRowL.addWidget(self.unitWs[i])
    propertyRowL.addSpacing(self.space)
    propertyRowL.addWidget(QLabel('link:'))
    self.linkWs.append(QLineEdit(''))
    propertyRowL.addWidget(self.linkWs[i], stretch=1)
    propertyRowL.addSpacing(self.space)
    propertyRowL.addWidget(QLabel('plot:'))
    self.plotWs.append(QCheckBox())
    self.plotWs[i].setChecked(True)
    self.plotWs[i].stateChanged.connect(self.refresh)
    propertyRowL.addWidget(self.plotWs[i])
    self.propertyRowsWs.append(propertyRowW)



  def refresh(self) -> None:
    """ repaint form incl. graph """
    if self.comm.binaryFile is None:
      return
    start      = self.start
    section    = self.comm.binaryFile.content[start]
    byteSize   = section.byteSize()
    byteFormat = section.size()
    #use data
    self.comm.binaryFile.file.seek(start)
    data = struct.unpack(byteFormat ,self.comm.binaryFile.file.read(byteSize))
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
          widget.setParent(None)
    elif command[0] == 'comboBox':
      print('show row with start, length, dtype') #TODO_P1
    else:
      logging.error('Command unknown %s', command)
    self.refresh()
    return


  def save(self, btn:IconButton) -> None:
    # sourcery skip: extract-method
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:  #TODO_P1 HOW
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
