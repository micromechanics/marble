""" Main table in app """
import logging
from typing import Any
from PySide6.QtWidgets import QWidget, QMenu, QTableView    # pylint: disable=no-name-in-module
from PySide6.QtCore import QPoint, Slot                     # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont # pylint: disable=no-name-in-module

from .communicate import Communicate
from .style import widgetAndLayout, Action
from .form import Form

class Table(QWidget):
  """ widget that shows the table of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.change)
    comm.toggle.connect(self.toggle)
    self.showBinary = True
    _, mainL = widgetAndLayout()

    # table
    self.table = QTableView(self)
    self.table.verticalHeader().hide()
    self.table.clicked.connect(self.cellClicked)
    self.table.doubleClicked.connect(self.cell2Clicked)
    header = self.table.horizontalHeader()
    header.setSectionsMovable(True)
    header.setStretchLastSection(True)
    mainL.addWidget(self.table)
    self.setLayout(mainL)

    #initialize models
    self.tableHeaders = self.comm.configuration['columns']
    nrows, ncols = 0, len(self.tableHeaders)
    self.modelAll   = QStandardItemModel(nrows, ncols)
    self.modelAll.setHorizontalHeaderLabels(self.tableHeaders)
    self.modelHide  = QStandardItemModel(nrows, ncols)
    self.modelHide.setHorizontalHeaderLabels(self.tableHeaders)
    self.rowIDsAll  = []
    self.rowIDsHide = []


  @Slot()
  def change(self) -> None:
    """ Change / Refresh / Repaint """
    if self.comm.binaryFile is None:
      return
    # initialize models
    self.tableHeaders = self.comm.configuration['columns']
    nrows, ncols = 0, len(self.tableHeaders)
    self.modelAll   = QStandardItemModel(nrows, ncols)
    self.modelAll.setHorizontalHeaderLabels(self.tableHeaders)
    self.modelHide  = QStandardItemModel(nrows, ncols)
    self.modelHide.setHorizontalHeaderLabels(self.tableHeaders)
    self.rowIDsAll  = []
    self.rowIDsHide = []
    # use content to build models
    content    = self.comm.binaryFile.content
    nrows      = len(content)
    self.modelAll.setRowCount(nrows)
    self.modelHide.setRowCount(nrows)
    iHide = -1
    for i,start in enumerate(content):  #loop over rows
      rowData = content[start].toCSV()
      # build model that has all the information
      self.rowIDsAll.append(start)
      self.addRow(self.modelAll, i, start, rowData)
      # build model that has only non-binary data
      if content[start].dType not in ['b','B']:
        self.rowIDsHide.append(start)
        iHide += 1
        self.addRow(self.modelHide, iHide, start, rowData)
    self.modelHide.setRowCount(iHide+1)
    self.table.setModel(self.modelAll)
    return


  def addRow(self, model:QStandardItemModel, row:int, start:int, rowData:dict[str,Any]) -> None:
    """
    Helper function to add a row

    Args:
      model (QStandardItemModel): model to add to
      row (int): row to add
      start (int): start value
    """
    for j, key in enumerate(self.tableHeaders):
      if key=='start':
          item = QStandardItem(self.comm.binaryFile.pretty(start))
      elif key=='dType':
        translate = {'b':'byte', 'i':'int', 'f':'float', 'd':'double', 'B':'zeros', 'c':'character'}
        item = QStandardItem(translate[rowData[key]])
      elif key=='entropy':
        item = QStandardItem(f'{rowData[key]:.3f}')
      elif key=='important':
        item = QStandardItem('\u2713') if rowData[key] else QStandardItem('\u00D7')
        item.setFont(QFont("Helvetica [Cronyx]", 16))
      else:
        item = QStandardItem(str(rowData[key]))
      model.setItem(row, j, item)
    return


  @Slot()
  def toggle(self) -> None:
    """ toggle between showing the binary data or not """
    if self.showBinary:
      self.table.setModel(self.modelHide)
    else:
      self.table.setModel(self.modelAll)
    self.showBinary = not self.showBinary
    return


  def execute(self, command:list[str]) -> None:
    """ execute actions from context menu, etc. """
    if self.comm.binaryFile is None:
      return
    if command[0] == 'autoTime':
      self.comm.binaryFile.automatic('x_z_p_a')  # type: ignore[misc]
    elif command[0] == 'autoElse':
      self.comm.binaryFile.automatic('x_z_p')  # type: ignore[misc]
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
    context = QMenu(self)
    if len(self.comm.binaryFile.content) == 1:
      Action('Automatic for time series', self, ['autoTime'], context)
      Action('Automatic for other data', self, ['autoElse'], context)
    index = self.table.currentIndex()
    print(index)
    context.exec(point.globalPos())
    return


  def cellClicked(self, item:QStandardItem) -> None:
    """
    What happens when user clicks cell in table of tags, projects, samples, ...
    -> show details

    Args:
      item (QStandardItem): cell clicked
    """
    # row = item.row()
    # item = self.itemFromRow(row)
    return


  def cell2Clicked(self, item:QStandardItem) -> None:
    """
    What happens when user double clicks cell in table of projects

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
    try:
      if self.showBinary:
        start = self.rowIDsAll[row]
      else:
        start = self.rowIDsHide[row]
      dialog = Form(self.comm, start)
      dialog.exec()
    except:
      logging.error('cell click is irrational', row)
      print(self.rowIDsAll, self.rowIDsHide)
    return
