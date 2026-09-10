""" Editor to change configuration .pyMARBLE.json and file.py/defaults.py """
import logging, json
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QGroupBox, QMessageBox, QTextEdit,\
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
    self.configurations:dict[str,dict[str,Any]] = {}
    if self.comm.binaryFile is not None:
      self.configurations = {'optFind': self.comm.binaryFile.optFind,
                             'optAutomatic':self.comm.binaryFile.optAutomatic,
                             'optEntropy':self.comm.binaryFile.optEntropy}
    self.llmConfiguration = {'type':'openAI', 'server':'https://api.openai.com/v1', 'model':'',
                             'keyringId':'pymarble-openai-default', 'comment':'', 'keyStorage':'keyring'} | self.comm.configuration.get('llm', {})
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
    llmBox = QGroupBox('LLM online lookup')
    llmLayout = QFormLayout()
    for key in ('type', 'server', 'model', 'keyringId', 'comment'):
      widget:Any = QTextEdit(str(self.llmConfiguration[key])) if key == 'comment' else QLineEdit(str(self.llmConfiguration[key]))
      if key == 'comment':
        widget.setMinimumHeight(70)
      setattr(self, f'widget_llm_{key}', widget)
      llmLayout.addRow(QLabel(f'{key}: '), widget)
    self.widget_llm_apiKey = QLineEdit()
    self.widget_llm_apiKey.setEchoMode(QLineEdit.EchoMode.Password)
    self.widget_llm_apiKey.setPlaceholderText('Stored in keyring unless plaintext fallback is active')
    llmLayout.addRow(QLabel('API key: '), self.widget_llm_apiKey)
    llmLayout.addRow(QLabel('Storage: '), QLabel(str(self.llmConfiguration.get('keyStorage', 'keyring'))))
    llmBox.setLayout(llmLayout)
    mainL.addWidget(llmBox)
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
    elif btn.text().endswith('Save'):
      for key in ('type', 'server', 'model', 'keyringId', 'comment'):
        widget = getattr(self, f'widget_llm_{key}')
        self.llmConfiguration[key] = widget.toPlainText() if key == 'comment' else widget.text()
      apiKey = self.widget_llm_apiKey.text()
      if apiKey:
        try:
          import keyring
          backend = keyring.get_keyring()
          if backend.priority <= 0:
            raise RuntimeError('no usable keyring backend')
          keyring.set_password('pymarble', self.llmConfiguration['keyringId'], apiKey)
          self.llmConfiguration['keyStorage'] = 'keyring'
          self.llmConfiguration.pop('apiKey', None)
        except Exception:
          answer = QMessageBox.warning(self, 'No usable keyring',
            'No usable keyring backend is available. Store this API key in plaintext in ~/.pyMARBLE.json?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
          if answer != QMessageBox.StandardButton.Yes:
            return
          self.llmConfiguration['keyStorage'] = 'plaintext'
          self.llmConfiguration['apiKey'] = apiKey
      self.comm.configuration['llm'] = self.llmConfiguration
      for group, subitems in self.configurations.items():
        for key in subitems:
          text = getattr(self, f'widget_{group}_{key}').text()
          if isinstance(subitems[key], float):
            subitems[key] = float(text)
          if isinstance(subitems[key], int):
            subitems[key] = int(text)
        self.comm.configuration[group] = subitems
      if self.comm.binaryFile is not None:
        self.comm.binaryFile.optFind      = self.configurations['optFind']
        self.comm.binaryFile.optAutomatic = self.configurations['optAutomatic']
        self.comm.binaryFile.optEntropy   = self.configurations['optEntropy']
      with open(Path.home()/'.pyMARBLE.json', 'w', encoding='utf-8') as fOut:
        fOut.write(json.dumps(self.comm.configuration, indent=2))
      self.accept()
    else:
      logging.error('configurationEditor: did not get a fitting btn %s',btn.text())
    return
