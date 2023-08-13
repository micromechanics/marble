""" Main table in app """
import logging
# from typing import Any
from PySide6.QtWidgets import QWidget, QMenu, QTableWidget, QTableWidgetItem  # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, QPoint, Slot                     # pylint: disable=no-name-in-module
from PySide6.QtGui import QFont                                 # pylint: disable=no-name-in-module
# from PySide6.QtGui import QColor, QBrush
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
    self.showAll = True
    _, mainL = widgetAndLayout()

    # table
    self.table = QTableWidget(self)
    self.table.verticalHeader().hide()
    # self.table.clicked.connect(self.cellClicked)
    self.table.doubleClicked.connect(self.cell2Clicked)
    header = self.table.horizontalHeader()
    header.setSectionsMovable(True)
    header.setStretchLastSection(True)
    mainL.addWidget(self.table)
    self.setLayout(mainL)
    self.change()  #paint


  @Slot()
  def change(self) -> None:
    """ Change / Refresh / Repaint """
    if self.comm.binaryFile is None:
      return
    # initialize
    content    = self.comm.binaryFile.content
    tableHeaders = self.comm.configuration['columns']
    self.table.setColumnCount(len(tableHeaders))
    self.table.setHorizontalHeaderLabels(tableHeaders)
    self.table.setRowCount(len(content))
    self.rowIDs  = []
    # use content to build models
    row = -1
    for start in content:  #loop over rows
      rowData = content[start].toCSV()
      if content[start].dType not in ['b','B'] or self.showAll :
        row += 1
        for col, key in enumerate(tableHeaders):
          if key=='start':
            item = QTableWidgetItem(self.comm.binaryFile.pretty(start)) # type: ignore[misc]
          elif key=='dType':
            translate = {'b':'byte', 'i':'int', 'f':'float', 'd':'double', 'B':'zeros', 'c':'character'}
            item = QTableWidgetItem(translate[rowData[key]])
          elif key=='entropy':
            item = QTableWidgetItem(f'{rowData[key]:.3f}')
          elif key=='important':
            item = QTableWidgetItem('\u2713' if rowData[key] else '\u00D7')
            item.setFont(QFont("Helvetica [Cronyx]", 16))
          else:
            item = QTableWidgetItem(str(rowData[key]))
          item.setFlags(Qt.ItemFlag.NoItemFlags | Qt.ItemFlag.ItemIsEnabled)   # type: ignore[operator]
          self.table.setItem(row, col, item)
        self.rowIDs.append(start)
    self.table.setRowCount(row+1)
    self.table.show()
    # TODO_P1 self.table.item(0,0).setBackground(QColor('red'))
    return


  @Slot()
  def toggle(self) -> None:
    """ toggle between showing the binary data or not """
    self.showAll = not self.showAll
    self.change()
    return


  def execute(self, command:list[str]) -> None:
    """
    execute actions from context menu, etc.

    Args:
      command (list): command to execute
    """
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


  # def cellClicked(self, item:QTableWidgetItem) -> None:
  #   """
  #   What happens when user clicks cell in table of tags, projects, samples, ...
  #   -> show details

  #   Args:
  #     item (QStandardItem): cell clicked
  #   """
  #   # row = item.row()
  #   # item = self.itemFromRow(row)
  #   return


  def cell2Clicked(self, item:QTableWidgetItem) -> None:
    """
    What happens when user double clicks cell in table of projects

    Args:
      item (QStandardItem): cell clicked
    """
    row = item.row()
    try:
      start = self.rowIDs[row]
      dialog = Form(self.comm, start)
      dialog.exec()
    except Exception:
      logging.error('cell click or form is irrational %s',row)
    return
