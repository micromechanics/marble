""" Editor to change metadata of binary file """
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QSpinBox # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout
from .communicate import Communicate

class FormSplit(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, comm:Communicate, start:int):
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
    self.start = start

    # GUI elements
    self.setWindowTitle('Split into sections')
    self.setMinimumWidth(400)
    mainL = QVBoxLayout(self)

    #dimensions
    _, dimensionL = widgetAndLayout('H', mainL)
    dimensionL.addWidget(QLabel('Number of sections:'))
    self.numberW = QSpinBox()
    self.numberW.setRange(2, 100)
    self.numberW.setSingleStep(1)
    dimensionL.addWidget(self.numberW, stretch=1)                           # type: ignore[call-arg]

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('OK') and self.comm.binaryFile is not None:
      self.comm.binaryFile.split(self.start, self.numberW.value())         # type: ignore[misc]
      self.accept()
    return
