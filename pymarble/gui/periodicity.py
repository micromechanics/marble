""" Editor to identify periodicity: multiple tests in one file """
from typing import Optional
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QComboBox, QWidget, QLineEdit  # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout, showMessage
from .communicate import Communicate
from .defaults import HELP_PERIODICITY

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
    self.domain = 64
    self.space = 20
    content = self.comm.binaryFile.content
    listCounts=[f'at {i} - {content[i].key}:{content[i].value}' for i in content if content[i].dClass=='count']
    listOther =[f'at {i} - {content[i].key}:{content[i].value}' for i in content if content[i].dClass!='count'
                and content[i].important]

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
    _, mainBarL = widgetAndLayout('H', mainL)
    self.plotCB = QComboBox()
    self.plotCB.addItems(['Plot entropy', 'Plot byte value'])
    self.plotCB.currentTextChanged.connect(self.refresh)
    mainBarL.addWidget(self.plotCB, stretch=1)                        # type: ignore[call-arg]
    mainBarL.addSpacing(self.space)
    self.widgetCB = QComboBox()
    self.widgetCB.addItems(['Select one section', 'Enter numbers directly'])
    self.widgetCB.currentTextChanged.connect(lambda: self.execute(['widgetCB']))
    mainBarL.addWidget(self.widgetCB, stretch=1)                        # type: ignore[call-arg]
    mainBarL.addSpacing(self.space*3)
    mainBarL.addWidget(QLabel('Count:'))
    self.countCB = QComboBox()
    self.countCB.addItems(listCounts)
    if 'count' in self.comm.binaryFile.periodicity:
      searchValue = self.comm.binaryFile.periodicity['count']
      self.countCB.setCurrentText([i for i in listCounts if i.startswith(f'at {searchValue}')][0])
    self.countCB.currentTextChanged.connect(self.refresh)
    mainBarL.addWidget(self.countCB, stretch=1)                        # type: ignore[call-arg]
    self.countLE = QLineEdit('')
    self.countLE.textChanged.connect(self.refresh)
    self.countLE.hide()
    mainBarL.addWidget(self.countLE, stretch=1)                        # type: ignore[call-arg]
    mainBarL.addSpacing(self.space)
    mainBarL.addWidget(QLabel('Start:'))
    self.startCB = QComboBox()
    self.startCB.addItems(listOther)
    if 'start' in self.comm.binaryFile.periodicity:
      searchValue = self.comm.binaryFile.periodicity['start']
      self.startCB.setCurrentText([i for i in listOther if i.startswith(f'at {searchValue}')][0])
    self.startCB.currentTextChanged.connect(self.refresh)
    mainBarL.addWidget(self.startCB, stretch=1)                        # type: ignore[call-arg]
    self.startLE = QLineEdit('')
    self.startLE.textChanged.connect(self.refresh)
    self.startLE.hide()
    mainBarL.addWidget(self.startLE, stretch=1)                        # type: ignore[call-arg]
    mainBarL.addSpacing(self.space)
    mainBarL.addWidget(QLabel('Last:'))
    self.lastCB = QComboBox()
    self.lastCB.addItems(listOther)
    if 'end' in self.comm.binaryFile.periodicity:
      searchValue = self.comm.binaryFile.periodicity['end']
      self.lastCB.setCurrentText([i for i in listOther if i.startswith(f'at {searchValue}')][0])
    self.lastCB.currentTextChanged.connect(self.refresh)
    mainBarL.addWidget(self.lastCB, stretch=1)                        # type: ignore[call-arg]
    self.lastLE = QLineEdit('')
    self.lastLE.textChanged.connect(self.refresh)
    self.lastLE.hide()
    mainBarL.addWidget(self.lastLE, stretch=1)                        # type: ignore[call-arg]

    #final button box
    self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Help)
    self.buttonBox.clicked.connect(self.save)
    mainL.addWidget(self.buttonBox)
    self.skipEvery = self.comm.binaryFile.optEntropy['skipEvery']
    self.entropy   = self.comm.binaryFile.entropy(average=False)       # type: ignore[misc]
    length         = len(self.entropy) if isinstance(self.entropy, list) else 1
    self.xValues   = np.arange(length)*self.skipEvery
    self.refresh()


  def refresh(self) -> None:
    """ repaint form incl. graph """
    if self.comm.binaryFile is None:
      return
    if self.widgetCB.currentText()=='Select one section':
      start = int(self.startCB.currentText().split(' - ')[0][3:])
      endOffset   = int(self.lastCB.currentText().split(' - ')[0][3:])
      sectionEnd = self.comm.binaryFile.content[endOffset]
      end = endOffset+sectionEnd.byteSize()
    elif self.startLE.text()=='' or self.lastLE.text()=='':
      start = end = 0
    else:
      start = int(self.startLE.text())
      end   = int(self.lastLE.text())
    #start plotting
    self.graph.axes.cla()                        # Clear the canvas
    if self.plotCB.currentText()=='Plot entropy':
      self.graph.axes.plot(self.xValues, self.entropy, label='default')
      offset = end-start
      self.graph.axes.plot(self.xValues-offset, self.entropy, '--', label='shifed by one period')
      self.graph.axes.legend()
      self.graph.axes.axvline(start, c='r', linewidth=2)
      self.graph.axes.axvline(end+1, c='r', linewidth=2)
      self.graph.axes.set_xlim(left=0)
      self.graph.axes.set_ylabel('entropy')
      self.graph.axes.set_xlabel('increment')
    else:
      xValues = np.arange(-self.domain, self.domain, 1)
      # line 1
      startD = start-self.domain
      endD   = start+self.domain
      preData = bytearray(0)
      if startD < 0:
        preData = bytearray(-startD)
        startD = 0
      self.comm.binaryFile.file.seek(startD)
      data = self.comm.binaryFile.file.read(endD-startD)
      data = preData+data if len(preData)>1 else data
      try:
        self.graph.axes.plot(xValues, list(data), 'o-', label='default')
      except Exception:  #do not plot if input numbers not correct
        pass
      # line 2
      startD = end+1 - self.domain
      endD   = end+1 + self.domain
      preData = bytearray(0)
      if startD < 0:
        preData = bytearray(-startD)
        startD = 0
      self.comm.binaryFile.file.seek(startD)
      data = self.comm.binaryFile.file.read(endD-startD)
      try:
        self.graph.axes.plot(xValues, list(data), 'o--', label='shifted by one period')
      except Exception:  #do not plot if input numbers not correct
        pass
      self.graph.axes.legend()
      self.graph.axes.axvline(0, c='r', linewidth=2)
      self.graph.axes.set_ylabel('byte value')
      self.graph.axes.set_xlabel('period start')
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
    if command[0] == 'widgetCB':
      if self.widgetCB.currentText()=='Select one section':
        self.countCB.setDisabled(False)
        self.startCB.show()
        self.lastCB.show()
        self.startLE.hide()
        self.lastLE.hide()
        self.buttonBox.buttons()[0].setDisabled(False)
      else:
        self.countCB.setDisabled(True)
        self.startCB.hide()
        self.lastCB.hide()
        self.startLE.show()
        self.lastLE.show()
        start = int(self.startCB.currentText().split(' - ')[0][3:])
        endOffset   = int(self.lastCB.currentText().split(' - ')[0][3:])
        sectionEnd = self.comm.binaryFile.content[endOffset]
        end = endOffset+sectionEnd.byteSize()
        self.startLE.setText(str(start))
        self.lastLE.setText(str(end))
        self.buttonBox.buttons()[0].setDisabled(True)
    else:
      print('**ERROR unknown command', command)
    self.refresh()
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None and  \
         self.widgetCB.currentText()=='Select one section':
      count = self.countCB.currentText().split(' - ')[0][3:]
      start = self.startCB.currentText().split(' - ')[0][3:]
      end   = self.lastCB.currentText().split(' - ')[0][3:]
      self.comm.binaryFile.periodicity =  {'count':int(count), 'start':int(start), 'end':int(end)}
      self.accept()
    elif btn.text().endswith('Help'):
      showMessage(self, 'Help', HELP_PERIODICITY, 'Information')
    else:
      showMessage(self, 'Information','Can only save when you select sections', 'Information')
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
