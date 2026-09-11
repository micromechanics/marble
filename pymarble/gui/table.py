""" Main table in app """
import logging
from typing import Any
from PySide6.QtWidgets import QWidget, QComboBox, QMenu, QMessageBox, QTableWidget, QTableWidgetItem, QToolButton  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, QPoint, Slot                     # pylint: disable=no-name-in-module
from PySide6.QtGui import QFont, QResizeEvent # pylint: disable=no-name-in-module
from .communicate import Communicate
from .style import widgetAndLayout, Action, dClassColor
from .defaults import dClass2Color, translateDtypeShort
from .form import Form
from .split import Split

COLUMN_TOOLTIPS = {
  'actions':'Edit this section',
  'start':'Byte offset at which this section starts',
  'length':'Number of values in this section',
  'dType':'Data type used to interpret this section',
  'key':'Click to edit the section key',
  'unit':'Click to edit the physical unit',
  'link':'Reference or terminology link for this section',
  'dClass':'Choose whether this section is metadata, primary data, a count, or unknown',
  'count':'Offsets of sections that define the dimensions',
  'shape':'Dimensions of the interpreted data',
  'prob':'Choose the confidence assigned to this identification',
  'entropy':'Calculated entropy of this section',
  'important':'Click to include or exclude this section from generated output',
  'value':'Click to edit the displayed value or description',
}

class Table(QWidget):
  """ widget that shows the table of the items """
  def __init__(self, comm:Communicate):
    """
    Args:
      comm: communication channel shared between GUI widgets
    """
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.change)
    comm.toggle.connect(self.toggle)
    self.toggleState = {'F5':'all', 'F6':'all', 'F7':'all'}
    _, mainL = widgetAndLayout()
    self.table = QTableWidget(self)
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.itemChanged.connect(lambda x: self.execute(['itemChanged',x]))
    self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.table.customContextMenuRequested.connect(self.openContextMenu)
    header = self.table.horizontalHeader()
    header.setSectionsMovable(True)
    header.setStretchLastSection(True)
    mainL.addWidget(self.table)
    self.setLayout(mainL)
    self.change()  #paint
    self.methods:dict[str,str] | None = None


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
    self.tableHeaders = ['actions'] + self.comm.configuration['columns']
    self.table.setColumnCount(len(self.tableHeaders))
    self.table.setHorizontalHeaderLabels(['Edit' if key == 'actions' else key for key in self.tableHeaders])
    if resizeColumns:
      extraSize = 4
      defaultWidth = int(self.width()/(len(self.tableHeaders)+extraSize))
      for idx,colName in enumerate(self.tableHeaders):
        if colName == 'actions':
          self.table.setColumnWidth(idx, 44)
        elif colName=='value':
          self.table.setColumnWidth(idx, defaultWidth*extraSize)
        else:
          self.table.setColumnWidth(idx, defaultWidth)
    for idx,title in enumerate(self.tableHeaders):
      headerItem = self.table.horizontalHeaderItem(idx)
      if headerItem is not None:
        headerItem.setToolTip(COLUMN_TOOLTIPS.get(title, f'Section {title}'))
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
        if key == 'actions':
          item = QTableWidgetItem()
          item.setToolTip(COLUMN_TOOLTIPS[key])
          button = QToolButton()
          button.setText('✎')
          button.setToolTip(COLUMN_TOOLTIPS[key])
          button.clicked.connect(lambda _checked=False, start=start: self.execute(['edit', str(start)]))
          self.table.setItem(row, col, item)
          self.table.setCellWidget(row, col, button)
          continue
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
        item.setToolTip(COLUMN_TOOLTIPS.get(key, f'Section {key}'))
        if key in ['unit','key','value']:
          item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemIsEditable)# type: ignore
        else:
          item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled)   # type: ignore[operator]
        if backgroundColor := dClassColor(rowData['dClass'], dClass2Color):
          item.setBackground(backgroundColor)
        self.table.setItem(row, col, item)
        if key == 'dClass':
          combo = QComboBox()
          combo.addItems(['unknown', 'metadata', 'primary', 'count'])
          combo.setCurrentText(rowData[key] or 'unknown')
          combo.setToolTip(COLUMN_TOOLTIPS[key])
          combo.activated.connect(lambda _index, start=start, combo=combo:
                                  self.execute(['setDClass', start, combo.currentText()]))
          self.table.setCellWidget(row, col, combo)
        elif key == 'prob':
          combo = QComboBox()
          probabilities = sorted({0, 25, 50, 75, 100, int(rowData[key])})
          combo.addItems([str(probability) for probability in probabilities])
          combo.setCurrentText(str(rowData[key]))
          combo.setToolTip(COLUMN_TOOLTIPS[key])
          combo.activated.connect(lambda _index, start=start, combo=combo:
                                  self.execute(['setProbability', start, combo.currentText()]))
          self.table.setCellWidget(row, col, combo)
      self.rowIDs.append(start)
    self.table.setRowCount(row+1)
    self.table.show()
    return


  @Slot(str, str, str)
  def toggle(self, f5text:str, f6text:str, f7text:str) -> None:
    """
    toggle showing sections of data

    Args:
      f5text: binary-section filter state
      f6text: data-class filter state
      f7text: important-section filter state
    """
    self.toggleState = {'F5':f5text, 'F6':f6text, 'F7':f7text}
    self.change()
    return


  def execute(self, command:list[Any]) -> None:
    """
    execute actions from context menu, etc

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
      setattr(self.comm.binaryFile.content[start], colName, item.data(Qt.ItemDataRole.EditRole))
      return
    if self.comm.binaryFile is None:
      return
    start = int(command[1]) if len(command)>1 else self.rowIDs[self.table.currentRow()]
    if command[0] == 'setDClass':
      self.comm.binaryFile.content[start].dClass = '' if command[2] == 'unknown' else command[2]
    elif command[0] == 'setProbability':
      self.comm.binaryFile.content[start].prob = int(command[2])
    elif command[0] == 'edit':
      formDialog = Form(self.comm, start)
      formDialog.exec()
    elif command[0] == 'autoTime': #look for xml data, zero data, primary data and ascii data
      self.comm.binaryFile.automatic('x_z_p_a', progress=self.comm.progress)  # type: ignore[misc]
    elif command[0] == 'autoElse': #look for xml data, zero data and ascii data
      self.comm.binaryFile.automatic('x_z_a')    # type: ignore[misc]
    elif command[0] == 'split':
      splitDialog = Split(self.comm, start)
      splitDialog.exec()
      self.change()  #repaint
    elif command[0] == 'remove':
      answer = QMessageBox.question(self, 'Remove information',
        f'Remove the section at {self.comm.binaryFile.pretty(start)}?',  # type: ignore[misc]
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
      if answer != QMessageBox.StandardButton.Yes:
        return
      del self.comm.binaryFile.content[start]
      self.comm.binaryFile.fill()                                 # type: ignore[misc]
    elif command[0].startswith('_') and command[0].endswith('_'):
      self.comm.binaryFile.automatic(command[0], start)           # type: ignore[misc]
      self.comm.binaryFile.fill()                                 # type: ignore[misc]
    else:
      logging.error('command unknown: %s', command)
    self.change()
    return


  def openContextMenu(self, point:QPoint) -> None:
    """
    Open the action menu for the row under the pointer

    Args:
      point: position within the table viewport
    """
    row = self.table.indexAt(point).row()
    if row < 0:
      return
    self.showContextMenu(row, self.table.viewport().mapToGlobal(point))


  def showContextMenu(self, row:int, globalPoint:QPoint) -> None:
    """Assemble and show the action menu for one row"""
    if self.comm.binaryFile is None:
      return
    if self.methods is None:
      self.methods = self.comm.binaryFile.automatic('_',getMethods=True)  # type: ignore[misc]
    if self.methods is None:
      return
    start = self.rowIDs[row]
    self.table.setCurrentCell(row, 0)
    context = QMenu(self)
    Action('Edit section', self, ['edit', str(start)], context)
    context.addSeparator()
    if len(self.comm.binaryFile.content) == 1:
      Action('Automatic for time series', self, ['autoTime', str(start)], context)
    Action('Automatic for general data',  self, ['autoElse', str(start)], context)
    context.addSeparator()
    for key, value in self.methods.items():
      Action(value,                       self, [f'_{key}_', str(start)], context)
    context.addSeparator()
    if len(self.comm.binaryFile.content) > 1:
      Action('Split into parts',          self, ['split', str(start)],    context)
      Action('Remove information',        self, ['remove', str(start)],   context)
    context.exec(globalPoint)
    return


  def cellClicked(self, item:QTableWidgetItem) -> None:
    """
    What happens when user clicks cell in table
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
