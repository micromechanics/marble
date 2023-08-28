""" Main table in app """
import logging
from typing import Optional, Any
import numpy as np
from PySide6.QtWidgets import QWidget, QMenu, QTableWidget, QTableWidgetItem  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, QPoint, Slot                     # pylint: disable=no-name-in-module
from PySide6.QtGui import QFont, QResizeEvent                   # pylint: disable=no-name-in-module
from .communicate import Communicate
from .style import widgetAndLayout, Action, hexToColor
from .defaults import dClass2Color, translateDtypeShort
from .form import Form
from .split import Split

class Table(QWidget):
  """ widget that shows the table of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.change)
    comm.toggle.connect(self.toggle)
    self.toggleState = {'F5':'all', 'F6':'all', 'F7':'all'}
    _, mainL = widgetAndLayout()
    self.table = QTableWidget(self)
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.doubleClicked.connect(self.cell2Clicked)
    self.table.itemChanged.connect(lambda x: self.execute(['itemChanged',x]))
    header = self.table.horizontalHeader()
    header.setSectionsMovable(True)
    header.setStretchLastSection(True)
    mainL.addWidget(self.table)
    self.setLayout(mainL)
    self.change()  #paint
    self.methods:Optional[dict[str,str]] = None


  @Slot()
  def change(self, resizeColumns:bool=False) -> None:
    """
    Change / Refresh / Repaint

    Args:
      resizeColumns (bool): resize colums depending of window width
    """
    if self.comm.binaryFile is None:
      return
    # initialize
    content    = self.comm.binaryFile.content
    self.tableHeaders = self.comm.configuration['columns']
    self.table.setColumnCount(len(self.tableHeaders))
    self.table.setHorizontalHeaderLabels(self.tableHeaders)
    if resizeColumns:
      extraSize = 4
      defaultWidth = int(self.width()/(len(self.tableHeaders)+extraSize))
      for idx,colName in enumerate(self.tableHeaders):
        if colName=='value':
          self.table.setColumnWidth(idx, defaultWidth*extraSize)
        else:
          self.table.setColumnWidth(idx, defaultWidth)
    for idx,title in enumerate(self.tableHeaders):
      if title in ['start','length','count','shape','entropy','link','dType']:
        self.table.horizontalHeaderItem(idx).setBackground(hexToColor('#d8e0f4'))
    self.table.setRowCount(len(content))
    self.rowIDs  = []
    # use content to build models
    row = -1
    for start in content:#loop over rows
      rowData = content[start].toCSV()
      #block depending on filter
      if content[start].dType in     ['b','B'] and self.toggleState['F5']=='none':
        continue
      if content[start].dType not in ['b','B'] and self.toggleState['F5']=='only':
        continue
      if     content[start].dClass             and self.toggleState['F6']=='none':
        continue
      if not content[start].dClass             and self.toggleState['F6']=='only':
        continue
      if     content[start].important          and self.toggleState['F7']=='none':
        continue
      if not content[start].important          and self.toggleState['F7']=='only':
        continue
      row += 1
      for col, key in enumerate(self.tableHeaders):
        if key == 'dType':
          item = QTableWidgetItem(translateDtypeShort[rowData[key]])
        elif key == 'entropy':
          item = QTableWidgetItem(f'{rowData[key]:.3f}')
        elif key == 'important':
          item = QTableWidgetItem('\u2713' if rowData[key] else '\u00D7')
          item.setFont(QFont("Helvetica [Cronyx]", 16))
        elif key == 'start':
          item = QTableWidgetItem(self.comm.binaryFile.pretty(start))        # type: ignore[misc]
        else:
          item = QTableWidgetItem(str(rowData[key]))
        if key in ['unit','key','value']:
          item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemIsEditable)# type: ignore
        else:
          item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled)   # type: ignore[operator]
        item.setBackground(hexToColor(dClass2Color[rowData['dClass']]))
        self.table.setItem(row, col, item)
      self.rowIDs.append(start)
    self.table.setRowCount(row+1)
    self.table.show()
    return


  @Slot(str, str, str)
  def toggle(self, f5text:str, f6text:str, f7text:str) -> None:
    """ toggle showing sections of data """
    self.toggleState = {'F5':f5text, 'F6':f6text, 'F7':f7text}
    self.change()
    return


  def execute(self, command:list[Any]) -> None:
    """
    execute actions from context menu, etc.

    Args:
      command (list): command to execute
    """
    if command[0] == 'itemChanged':
      item = command[1]
      if item.row() >= len(self.rowIDs):
        return
      start = self.rowIDs[item.row()]
      colName  = self.tableHeaders[item.column()]
      if colName not in ['unit','key','value'] or self.comm.binaryFile is None:
        return
      setattr(self.comm.binaryFile.content[start], colName, item.data(Qt.EditRole))
      return
    start = self.rowIDs[self.table.currentRow()]
    if self.comm.binaryFile is None:
      return
    if command[0]   == 'autoTime': #look for xml data, zero data, primary data and ascii data
      self.comm.binaryFile.automatic('x_z_p_a', progress=self.comm.progress)  # type: ignore[misc]
    elif command[0] == 'autoElse': #look for xml data, zero data and ascii data
      self.comm.binaryFile.automatic('x_z_a')    # type: ignore[misc]
    elif command[0] == 'split':
      dialog = Split(self.comm, start)
      dialog.exec()
      self.change()  #repaint
    elif command[0] == 'remove':
      del self.comm.binaryFile.content[start]
      self.comm.binaryFile.fill()                                 # type: ignore[misc]
    elif command[0].startswith('_') and command[0].endswith('_'):
      self.comm.binaryFile.automatic(command[0], start)           # type: ignore[misc]
      self.comm.binaryFile.fill()                                 # type: ignore[misc]
    else:
      logging.error('command unknown: %s', command)
    self.change()
    return


  def contextMenuEvent(self, point:QPoint) -> None:
    """
    assemble context menu

    Args:
      point (QPoint): point at which was clicked
    """
    if self.comm.binaryFile is None:
      return
    if self.methods is None:
      self.methods = self.comm.binaryFile.automatic('_',getMethods=True)  # type: ignore[misc]
    if self.methods is None:
      return
    context = QMenu(self)
    if len(self.comm.binaryFile.content) == 1:
      Action('Automatic for time series', self, ['autoTime'], context)
    Action('Automatic for general data',  self, ['autoElse'], context)
    context.addSeparator()
    for key, value in self.methods.items():
      Action(value,                       self, [f'_{key}_'], context)
    context.addSeparator()
    if len(self.comm.binaryFile.content) > 1:
      Action('Split into parts',          self, ['split'],    context)
      Action('Remove information',        self, ['remove'],   context)
    context.exec(point.globalPos())
    return


  def cellClicked(self, item:QTableWidgetItem) -> None:
    """
    What happens when user clicks cell in table of tags, projects, samples, ...
    -> show details

    Args:
      item (QStandardItem): cell clicked
    """
    if self.comm.binaryFile is None:
      return
    start = self.rowIDs[item.row()]
    colName  = self.tableHeaders[item.column()]
    content  = self.comm.binaryFile.content
    if colName == 'important':
      content[start].important = not content[start].important
    elif colName == 'dClass':
      orderList = ['', 'metadata', 'primary', '']
      idxList   = orderList.index(content[start].dClass)
      content[start].dClass = orderList[idxList+1]
    elif colName == 'prob':
      orderArray = np.array([49, 100, 75, 50])
      mask = orderArray>=content[start].prob
      minValue = orderArray[mask].min()
      idxArray = np.argmin(np.abs(orderArray-minValue))
      content[start].prob = orderArray[idxArray+1]
    self.change()  #repaint
    return


  def cell2Clicked(self, item:QTableWidgetItem) -> None:
    """
    What happens when user double clicks cell in table of projects

    Args:
      item (QStandardItem): cell clicked
    """
    colName  = self.tableHeaders[item.column()]
    if colName in ['unit','key','value']:
      return
    row = item.row()
    start = self.rowIDs[row]
    dialog = Form(self.comm, start)
    dialog.exec()
    self.change()  #repaint
    return


  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    executed upon resize

    Args:
      event (QResizeEvent): event
    """
    self.change(resizeColumns=True)
    return super().resizeEvent(event)
