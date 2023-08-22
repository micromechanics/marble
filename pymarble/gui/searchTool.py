""" Editor to change metadata of binary file """
import logging
from typing import Any
from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox, QTextEdit  # pylint: disable=no-name-in-module
from .style import TextButton, showMessage
from .communicate import Communicate
from ..section import Section

class SearchTool(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    if self.comm.binaryFile is None:
      return

    self.setWindowTitle('Search tool')
    self.setMinimumWidth(400)
    mainL = QFormLayout(self)

    self.searchMethodCB = QComboBox()
    self.searchMethodCB.addItems(['Search for value','Search by bytes'])
    mainL.addRow(QLabel('Search method'), self.searchMethodCB)
    self.searchDTypeCB = QComboBox()
    self.searchDTypeCB.addItems(['i','f','d','c'])
    mainL.addRow(QLabel('Data type'),     self.searchDTypeCB)
    self.searchValue   = QLineEdit()
    mainL.addRow(QLabel('Value'),         self.searchValue)
    self.searchBtn     = TextButton('Search', self, ['search'], mainL)
    self.searchResult  = QTextEdit()
    mainL.addRow(QLabel('Result'),         self.searchResult)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
    buttonBox.addButton("Mark in list", QDialogButtonBox.AcceptRole)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def execute(self, _:list[str]) -> None:
    """ Execute command
    """
    if self.comm.binaryFile is None:
      return
    dType = self.searchDTypeCB.currentText()
    value:Any = 0
    if dType in {'f','d'}:
      value = float(self.searchValue.text())
    elif dType in {'i'}:
      value = int(self.searchValue.text())
    elif dType in {'c'}:
      value = self.searchValue.text()
    else:
      print('**ERROR searchTool, undefined dType', dType)
      return
    if self.searchMethodCB.currentText() == 'Search for value':
      if dType == 'c':
        result = 'Cannot search for value of character. Use "Search by bytes".'
      else:
        result = ' '.join(self.comm.binaryFile.findValue(value, dType, verbose=False))     # type: ignore[misc]
    else:
      result = str(self.comm.binaryFile.findBytes(value, dType))                           # type: ignore[misc]
    self.searchResult.setText(result)
    return


  def save(self, btn:TextButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().startswith('Mark') and self.comm.binaryFile is not None:
      try:
        start = int(self.searchResult.toPlainText())
        dType = self.searchDTypeCB.currentText()
        value = f'manually searched value {self.searchValue.text()}'
        self.comm.binaryFile.content[start] = Section(1, dType, '', '', value, '', 'metadata', [], [], 100)
        print(start, self.comm.binaryFile.content[start])
        self.accept()
      except Exception:
        showMessage(self, 'Error','There should only be one start position in the text field','Critical')
    else:
      logging.error('metaEditor: did not get a fitting btn %s',btn.text())
    return
