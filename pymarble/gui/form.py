""" Editor to change metadata of binary file """
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox  # pylint: disable=no-name-in-module
from .style import IconButton, widgetAndLayout
from .communicate import Communicate

class Form(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, comm:Communicate, start):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    if self.comm.binaryFile is None:
      return
    self.start   = start
    self.section = self.comm.binaryFile.content[start]
    print(start, self.section.toCSV(), self.comm.binaryFile.fileLength)

    # GUI elements
    self.setWindowTitle('Change section')
    space = 20
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    mainL.setSpacing(space)

    #graph
    self.graph = QLabel('Graph') #TODO_P1
    mainL.addWidget(self.graph)

    #buttons below graph
    _, graphButtonL = widgetAndLayout('H', mainL)
    IconButton('fa.arrow-left',  self, ['startDown'], graphButtonL, 'reduce start point')
    IconButton('fa.arrow-right', self, ['startUp'],   graphButtonL, 'increase start point')
    graphButtonL.addSpacing(200)
    plotComboBox = QComboBox()
    translatePlot = {'f':'numerical value','d':'numerical value','b':'byte value'}
    plotComboBox.addItems(['numerical value','byte value','entropy'])
    plotComboBox.setCurrentText(translatePlot[self.section.dType])
    # plotComboBox.changeEvent()
    graphButtonL.addWidget(plotComboBox)
    graphButtonL.addSpacing(200)
    IconButton('fa.arrow-left',  self, ['endDown'],   graphButtonL, 'reduce end point')
    IconButton('fa.arrow-right', self, ['endUp'],     graphButtonL, 'increase end point')

    #dimensions
    _, dimensionL = widgetAndLayout('H', mainL)
    dimensionL.addWidget(QLabel('Start:'))
    self.startW = QSpinBox()
    self.startW.setRange(0, self.comm.binaryFile.fileLength)
    self.startW.setSingleStep(4)
    self.startW.setValue(start)
    dimensionL.addWidget(self.startW, stretch=1)
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Length:'))
    self.lengthW = QSpinBox()
    self.lengthW.setRange(0, self.comm.binaryFile.fileLength)
    self.lengthW.setValue(self.section.length)
    dimensionL.addWidget(self.lengthW, stretch=1)
    dimensionL.addSpacing(space)
    self.dTypeCB = QComboBox()
    dimensionL.addWidget(QLabel('dType:'))
    translateDtype = {'f':'float = 4byte','d':'double = 8byte','b':'byte = 1byte'}
    self.dTypeCB.addItems(['byte = 1byte', 'int = 4byte','float = 4byte','double = 8byte'])
    self.dTypeCB.setCurrentText(translateDtype[self.section.dType])
    dimensionL.addWidget(self.dTypeCB)
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Probability:'))
    self.probabilityW = QSpinBox()
    self.probabilityW.setRange(1, 100)
    self.probabilityW.setSingleStep(20)
    self.probabilityW.setValue(self.section.prob)
    dimensionL.addWidget(self.probabilityW)
    dimensionL.addSpacing(space)
    dimensionL.addWidget(QLabel('Important:'))
    self.importantW = QCheckBox()
    self.importantW.setChecked(self.section.important)
    dimensionL.addWidget(self.importantW)

    #key value unit
    _, keyValueL = widgetAndLayout('H', mainL)
    keyValueL.addWidget(QLabel('Key:'))
    self.keyW = QLineEdit(self.section.key,self)
    keyValueL.addWidget(self.keyW)
    keyValueL.addSpacing(space)
    keyValueL.addWidget(QLabel('Value:'))
    self.valueW = QLineEdit(self.section.value,self)
    keyValueL.addWidget(self.valueW, stretch=1)
    keyValueL.addSpacing(space)
    keyValueL.addWidget(QLabel('Unit:'))
    self.unitW = QLineEdit(self.section.unit,self)
    self.unitW.setMaximumWidth(60)
    keyValueL.addWidget(self.unitW)

    #dClass etc.
    _, dClassL = widgetAndLayout('H', mainL)
    dClassL.addWidget(QLabel('dClass:'))
    self.dClassCB = QComboBox()
    self.dClassCB.addItems(['metadata','primary','unknown'])
    self.dClassCB.setCurrentText(self.section.dClass)
    dClassL.addWidget(self.dClassCB)
    dClassL.addSpacing(space)
    dClassL.addWidget(QLabel('Link:'))
    self.linkW = QLineEdit(self.section.link,self)
    dClassL.addWidget(self.linkW)

    if 'advanced' in self.comm.configuration:
      # advanced items
      _, advancedL = widgetAndLayout('H', mainL)
      advancedL.addWidget(QLabel('Count:'))
      self.countW = QLineEdit(str(self.section.count),self)
      advancedL.addWidget(self.countW)
      advancedL.addSpacing(space)
      advancedL.addWidget(QLabel('Shape:'))
      self.shapeW = QLineEdit(str(self.section.shape),self)
      advancedL.addWidget(self.shapeW)
      advancedL.addSpacing(space)
      advancedL.addWidget(QLabel('Entropy:'))
      self.entropyW = QLineEdit(str(self.section.entropy),self)
      advancedL.addWidget(self.entropyW)


    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)


  def save(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save') and self.comm.binaryFile is not None:
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
