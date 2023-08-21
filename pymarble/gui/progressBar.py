""" Progress bar """
from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar   # pylint: disable=no-name-in-module
from .communicate import Communicate

class progressBar(QDialog):
  """ Progress bar """
  #INCOMPLETE SINCE I DON'T KNOW HOW TO DO IT
  def __init__(self, comm:Communicate, progressBar:QProgressBar):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    if self.comm.binaryFile is None:
      return

    self.setWindowTitle('Change metadata of binary file')
    self.setMinimumWidth(600)
    self.progress = QProgressBar(self)
    mainL = QVBoxLayout(self)
    mainL.addWidget(self.progress)
    progressBar.setValue(int(100))