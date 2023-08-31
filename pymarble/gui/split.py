""" Editor to change metadata of binary file """
import re, struct
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout
from .communicate import Communicate

class Split(QDialog):
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
    self.length = self.comm.binaryFile.content[self.start].byteSize()

    # GUI elements
    self.setWindowTitle('Split into sections')
    self.setMinimumWidth(450)
    mainL = QVBoxLayout(self)
    mainL.addWidget(QLabel('You can enter into both boxes the size. For example: 2, 3i or 6d'))
    self.interactionOn = False

    #dimensions
    _, dimensionL = widgetAndLayout('H', mainL)
    dimensionL.addWidget(QLabel('First:'))
    self.firstW = QLineEdit(str(int(self.length/2)))
    dimensionL.addWidget(self.firstW, stretch=1)                           # type: ignore[call-arg]
    dimensionL.addSpacing(50)
    dimensionL.addWidget(QLabel('Second:'))
    self.secondW = QLineEdit(str(int(self.length-self.length/2)))
    dimensionL.addWidget(self.secondW, stretch=1)                           # type: ignore[call-arg]

    self.firstW.textChanged.connect(lambda: self.execute(1))
    self.secondW.textChanged.connect(lambda: self.execute(2))

    #final button box
    self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    self.buttonBox.clicked.connect(self.save)
    mainL.addWidget(self.buttonBox)


  def execute(self, segment:int) -> None:
    """ Execute events after human changed text fields

    Args:
      segment (int): which segment was changed
    """
    if (segment==1 and self.secondW.hasFocus()) or (segment==2 and self.firstW.hasFocus()):
      return
    text = self.firstW.text() if segment==1 else self.secondW.text()
    allNumbers = re.findall(r'\d+',text)
    allLetters = re.findall(r'[bcdfih]',text.lower())
    number = allNumbers[0] if allNumbers else ''
    letter = allLetters[0] if allLetters else 'b'
    otherLength = self.length-struct.calcsize(number+letter)
    if otherLength > 0:
      otherText = str(otherLength)
      self.buttonBox.buttons()[0].setDisabled(False)
    else:
      otherText = 'Error: too long'
      self.buttonBox.buttons()[0].setDisabled(True)
    if segment==1:
      self.secondW.setText(otherText)
    else:
      self.firstW.setText(otherText)
    return


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('OK') and self.comm.binaryFile is not None:
      text = self.firstW.text()
      allNumbers = re.findall(r'\d+',text)
      allLetters = re.findall(r'[bcdfiH]',text)
      number = allNumbers[0] if allNumbers else ''
      letter = allLetters[0] if allLetters else 'b'
      self.comm.binaryFile.split(self.start, struct.calcsize(number+letter))         # type: ignore[misc]
      self.accept()
    return
