""" Editor to change metadata of binary file """
import json
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox  # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout, showMessage
from .communicate import Communicate

class MetaEditor(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    self.metaFields = self.comm.binaryFile.meta

    # GUI elements
    self.setWindowTitle('Change metadata of binary file')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, self.formL = widgetAndLayout('Form', mainL)
    for key, value in self.metaFields.items():
      if key == 'endian':
        self.endianComboBox = QComboBox()
        self.endianComboBox.addItems(['big','small'])
        self.formL.addRow(QLabel('Endian encoding'), self.endianComboBox)
      else:
        setattr(self, f'key_{key}', QLineEdit(value))
        self.formL.addRow(QLabel(key.capitalize()), getattr(self, f'key_{key}'))
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      for key in self.metaFields.keys():
        if key == 'endian':
          self.metaFields[key]=self.endianComboBox.currentText()
        else:
          self.metaFields[key]=getattr(self, f'key_{key}').text().strip()
      self.comm.binaryFile.meta = self.metaFields
      self.accept()
    else:
      print('metaEditor: did not get a fitting btn ',btn.text())
    return
