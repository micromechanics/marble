""" Editor to identify periodicity: multiple tests in one file """
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

class Periodicity(QDialog):
  """ Editor to identify periodicity: multiple tests in one file """
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
    self.setWindowTitle('Identify multiple tests in one file')
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
    #fBIN.periodicity =  dict(zip(['count','start','end'],[int(i) for i in command.split()[1:]]))
    content = self.comm.binaryFile.content
    listCounts=[f'at {i} - {content[i].key}:{content[i].value}' for i in content if content[i].dClass=='count']
    listOther =[f'at {i} - {content[i].key}:{content[i].value}' for i in content if content[i].dClass!='count']
    _, mainBarL = widgetAndLayout('H', mainL)
    mainBarL.addWidget(QLabel('Count:'))
    self.countCB = QComboBox()
    self.countCB.addItems(listCounts)
    self.countCB.currentTextChanged.connect(lambda: self.execute(['countCB']))
    mainBarL.addWidget(self.countCB, stretch=1)                        # type: ignore[call-arg]
    mainBarL.addSpacing(self.space*2)
    mainBarL.addWidget(QLabel('Start:'))
    self.startCB = QComboBox()
    self.startCB.addItems(listOther)
    self.startCB.currentTextChanged.connect(lambda: self.execute(['startCB']))
    mainBarL.addWidget(self.startCB, stretch=1)                        # type: ignore[call-arg]
    mainBarL.addSpacing(self.space*2)
    mainBarL.addWidget(QLabel('Last:'))
    self.lastCB = QComboBox()
    self.lastCB.addItems(listOther)
    self.lastCB.currentTextChanged.connect(lambda: self.execute(['lastCB']))
    mainBarL.addWidget(self.lastCB, stretch=1)                        # type: ignore[call-arg]

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)
    self.skipEvery = self.comm.binaryFile.optEntropy['skipEvery']
    self.entropy   = self.comm.binaryFile.entropy(average=False)
    self.xValues   = np.arange(len(self.entropy))*self.skipEvery
    self.refresh()


  def refresh(self) -> None:
    """ repaint form incl. graph """
    if self.comm.binaryFile is None:
      return
    count = int(self.countCB.currentText().split(' - ')[0][3:])
    start = int(self.startCB.currentText().split(' - ')[0][3:])
    end   = int(self.lastCB.currentText().split(' - ')[0][3:])
    sectionEnd = self.comm.binaryFile.content[end]
    self.graph.axes.cla()                        # Clear the canvas
    self.graph.axes.plot(self.xValues, self.entropy)
    self.graph.axes.axvline(start, c='r', linewidth=2)
    self.graph.axes.axvline(end+sectionEnd.byteSize(), c='r', linewidth=2)
    self.graph.axes.set_xlabel('increment')
    self.graph.axes.set_xlim(left=0)
    self.graph.axes.set_ylabel('entropy')
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
    self.refresh()
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
      count = self.countCB.currentText().split(' - ')[0][3:]
      start = self.startCB.currentText().split(' - ')[0][3:]
      end   = self.lastCB.currentText().split(' - ')[0][3:]
      self.comm.binaryFile.periodicity =  {'count':count, 'start':start, 'end':end}
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
