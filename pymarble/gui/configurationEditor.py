""" Editor to change configuration .pyMARBLE.json and file.py/defaults.py """
import logging, json
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QGroupBox,\
                              QFormLayout  # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout
from .communicate import Communicate

class ConfigurationEditor(QDialog):
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
    self.configurations:dict[str,dict[str,Any]] = {'optFind': self.comm.binaryFile.optFind,
                                                   'optAutomatic':self.comm.binaryFile.optAutomatic,
                                                   'optEntropy':self.comm.binaryFile.optEntropy}
    # GUI elements
    self.setWindowTitle('Change configuration')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, self.formL = widgetAndLayout('Form', mainL)
    #create automatic forms
    for group, subitems in self.configurations.items():
      groupBoxW = QGroupBox(f'options for {group[3:].lower()} methods')
      groupBoxL = QFormLayout()
      for key, value in subitems.items():
        setattr(self, f'widget_{group}_{key}', QLineEdit(str(value)))
        groupBoxL.addRow(QLabel(f'{key}: '), getattr(self, f'widget_{group}_{key}'))
      groupBoxW.setLayout(groupBoxL)
      mainL.addWidget(groupBoxW)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
      for group, subitems in self.configurations.items():
        for key in subitems:
          text = getattr(self, f'widget_{group}_{key}').text()
          if isinstance(subitems[key], float):
            subitems[key] = float(text)
          if isinstance(subitems[key], int):
            subitems[key] = int(text)
        self.comm.configuration[group] = subitems
      self.comm.binaryFile.optFind      = self.configurations['optFind']
      self.comm.binaryFile.optAutomatic = self.configurations['optAutomatic']
      self.comm.binaryFile.optEntropy   = self.configurations['optEntropy']
      with open(Path.home()/'.pyMARBLE.json', 'w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(self.comm.configuration, indent=2))
      self.accept()
    else:
      logging.error('configurationEditor: did not get a fitting btn %s',btn.text())
    return
