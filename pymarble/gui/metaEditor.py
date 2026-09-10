""" Editor to change metadata of binary file """
import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit  # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout
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
    if self.comm.binaryFile is None:
      return
    self.metaFields = self.comm.binaryFile.meta

    # GUI elements
    self.setWindowTitle('Change metadata of binary file')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, self.formL = widgetAndLayout('Form', mainL)
    for key, value in self.metaFields.items():
      if key == 'endian':
        continue
      # MARBLE supports only typical little-endian systems and input files
      # The metadata is retained for compatibility but is not configurable
      #
      # self.endianComboBox = QComboBox()
      # self.endianComboBox.addItems(['big','small'])
      # self.formL.addRow(QLabel('Endian encoding'), self.endianComboBox)
      setattr(self, f'key_{key}', QLineEdit(value))
      self.formL.addRow(QLabel(key.capitalize()), getattr(self, f'key_{key}'))
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def save(self, btn:IconButton) -> None:
    """
    save selectedList to configuration and exit

    Args:
      btn: button that triggered the save action
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
      for key in self.metaFields.keys():
        if key == 'endian':
          continue
          # self.metaFields[key]=self.endianComboBox.currentText()
        self.metaFields[key]=getattr(self, f'key_{key}').text().strip()
      self.comm.binaryFile.meta = self.metaFields
      self.accept()
    else:
      logging.error('metaEditor: did not get a fitting btn %s',btn.text())
    return
