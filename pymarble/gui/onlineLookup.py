"""Non-blocking GUI presentation for an online format lookup"""
from typing import Any
from PySide6.QtCore import QThread, Signal  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPlainTextEdit, QVBoxLayout  # pylint: disable=no-name-in-module
from ..onlineLookup import lookup


class LookupThread(QThread):
  """Run the shared lookup outside the GUI thread"""
  finishedReport = Signal(str)

  def __init__(self, binaryFile:Any, configuration:dict[str, Any]):
    super().__init__()
    self.binaryFile = binaryFile
    self.configuration = configuration

  def run(self) -> None:
    """Run the lookup and emit its report when complete"""
    self.finishedReport.emit(lookup(self.binaryFile, self.configuration))


class OnlineLookup(QDialog):
  """Read-only, copyable lookup report dialog"""
  def __init__(self, binaryFile:Any, configuration:dict[str, Any], parent:Any=None):
    super().__init__(parent)
    self.setWindowTitle('Online lookup')
    self.resize(700, 450)
    layout = QVBoxLayout(self)
    self.report = QPlainTextEdit('Looking up the file format…')
    self.report.setReadOnly(True)
    layout.addWidget(self.report)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    buttons.rejected.connect(self.reject)
    layout.addWidget(buttons)
    self.lookupThread = LookupThread(binaryFile, configuration)
    self.lookupThread.finishedReport.connect(self.report.setPlainText)
    self.lookupThread.start()
