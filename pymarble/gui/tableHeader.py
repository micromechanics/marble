""" Table Header dialog: change which colums are shown and in which order """
import json, logging
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox  # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout
from .communicate import Communicate
from ..section import SECTION_OUTPUT_ORDER

class TableHeader(QDialog):
  """ Table Header dialog: change which colums are shown and in which order """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    self.selectedList = self.comm.configuration['columns']
    self.allSet = set(['start']+SECTION_OUTPUT_ORDER)

    # GUI elements
    self.setWindowTitle('Select table headers')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, bodyL = widgetAndLayout('H', mainL)
    self.choicesW = QListWidget()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    bodyL.addWidget(self.choicesW)
    _, centerL = widgetAndLayout('V', bodyL)
    IconButton('fa5s.angle-right',        self, ['add'], centerL, 'add to right')
    IconButton('fa5s.angle-left',         self, ['del'], centerL, 'remove right')
    IconButton('fa5s.angle-up',           self, ['up'],  centerL, 'move up')
    IconButton('fa5s.angle-down',         self, ['down'],centerL, 'move down')
    self.selectW = QListWidget()
    self.selectW.addItems(self.selectedList)
    bodyL.addWidget(self.selectW)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def execute(self, command:list[str]) -> None:
    """ Event if user clicks button in the center """
    selectedLeft   = [i.text() for i in self.choicesW.selectedItems()]
    selectedRight  = [i.text() for i in self.selectW.selectedItems()]
    oldIndex, newIndex = -1, -1
    if command[0] == 'add':
      self.selectedList += selectedLeft
    elif command[0] == 'del':
      self.selectedList = [i for i in self.selectedList if i not in selectedRight ]
    elif command[0] == 'up' and len(selectedRight)==1:
      oldIndex = self.selectedList.index(selectedRight[0])
      if oldIndex>0:
        newIndex = oldIndex-1
    elif command[0] == 'down' and len(selectedRight)==1:
      oldIndex = self.selectedList.index(selectedRight[0])
      if oldIndex<len(self.selectedList)-1:
        newIndex = oldIndex+1
    #change content
    if oldIndex>-1 and newIndex>-1:
      self.selectedList.insert(newIndex, self.selectedList.pop(oldIndex))
    self.choicesW.clear()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    self.selectW.clear()
    self.selectW.addItems(self.selectedList)
    if oldIndex>-1 and newIndex>-1:
      self.selectW.setCurrentRow(newIndex)
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      self.comm.configuration['columns'] = list(self.selectedList)
      with open(Path.home()/'.pyMARBLE.json', 'w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(self.comm.configuration, indent=2))
      self.comm.changeTable.emit()
      self.accept()
    else:
      logging.error('dialogTableHeader: did not get a fitting btn %s',btn.text())
    return
