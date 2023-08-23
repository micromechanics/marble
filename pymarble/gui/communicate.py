""" Communication class that sends signals between widgets, incl. binaryFile"""
from typing import Any, Optional
from PySide6.QtWidgets import QWidget        # pylint: disable=no-name-in-module
from PySide6.QtCore import QObject, Signal   # pylint: disable=no-name-in-module
from ..file import BinaryFile

class Communicate(QObject):
  """ Communication class that sends signals between widgets, incl. binaryFile"""
  def __init__(self, binaryFile:Optional[BinaryFile], configuration:dict[str,Any], progress:QWidget):
    super().__init__()
    self.binaryFile = binaryFile
    self.configuration = configuration
    self.progress      = progress

  # Signals: specify emitter and receiver
  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  changeTable = Signal()            # redraw table
  toggle = Signal(str,str,str)      # toggle table: binary, dClass, important
