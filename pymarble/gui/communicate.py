""" Communication class that sends signals between widgets, incl. binaryFile"""
from typing import Any
from PySide6.QtWidgets import QProgressBar   # pylint: disable=no-name-in-module
from PySide6.QtCore import QObject, Signal   # pylint: disable=no-name-in-module
from ..file import BinaryFile

class Communicate(QObject):
  """ Communication class that sends signals between widgets, incl. binaryFile"""
  def __init__(self, binaryFile:BinaryFile | None, configuration:dict[str,Any], progress:QProgressBar):
    """
    Args:
      binaryFile: current binary file, or None before a file is opened
      configuration: GUI and processing configuration
      progress: progress bar for long-running operations
    """
    super().__init__()
    self.binaryFile = binaryFile
    self.configuration = configuration
    self.progress      = progress

  # Signals: specify emitter and receiver
  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  changeTable = Signal()            # redraw table
  toggle = Signal(str,str,str)      # toggle table: binary, dClass, important
