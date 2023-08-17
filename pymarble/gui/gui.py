""" Graphical user interface includes all widgets """
import os, logging, webbrowser, json, subprocess
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QStatusBar, QLabel # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt                                        # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut, QResizeEvent    # pylint: disable=no-name-in-module

from ..file import BinaryFile
from .defaults import defaultConfiguration, ABOUT_TEXT, INFO_EXPORTED_FILE
from .style import Action, showMessage
from .communicate import Communicate
from .table import Table
from .tableHeader import TableHeader
from .metaEditor  import MetaEditor
from .misc import restart

os.environ['QT_API'] = 'pyside6'

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """
  def __init__(self, configuration:dict[str,Any]) -> None:
    #global setting
    super().__init__()
    self.setWindowTitle('MARBLE for Python')
    self.setWindowState(Qt.WindowMaximized) # type: ignore
    resourcesDir = Path(__file__).parent/'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir/'Icons'/'favicon64.png')))

    # #Menubar
    menu = self.menuBar()
    fileMenu = menu.addMenu("&File")
    Action('&Open binary file',  self, ['open'],       fileMenu, shortcut='Ctrl+L')
    Action('&Use exported .csv', self, ['useExported'],fileMenu, shortcut='Ctrl+U')
    if 'advanced' in configuration:
      fileMenu.addSeparator()
      Action('Save corr. .tags', self, ['saveTags'],   fileMenu)
      Action('Load corr. .tags', self, ['loadTags'],   fileMenu)
    fileMenu.addSeparator()
    Action('&Save python-file',  self, ['savePython'], fileMenu)
    Action('Save and e&xtract',  self, ['extractPython'], fileMenu)
    if 'advanced' in configuration:
      Action('Load python-file',   self, ['loadPython'], fileMenu)
    fileMenu.addSeparator()
    Action('&Exit',             self, ['exit'],       fileMenu)

    viewMenu = menu.addMenu("&View")
    Action('&Hide binary',      self, ['F5'],         viewMenu, shortcut='F5')
    Action('&Hide data class',  self, ['F6'],         viewMenu, shortcut='F6')
    Action('&Hide important',   self, ['F7'],         viewMenu, shortcut='F7')
    Action('Table columns',     self, ['tableHeader'],viewMenu)

    toolsMenu = menu.addMenu("&Tools")
    Action('Edit &metadata',    self, ['metaEditor'], toolsMenu, shortcut='Ctrl+M')

    helpMenu = menu.addMenu("&Help")
    Action('&Website',          self, ['website'],        helpMenu)
    Action('&About',            self, ['about'],        helpMenu)
    #shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda : self.execute(['restart']))

    self.statusBarW =QLabel('Initialize...')
    self.toggleState = {'F5':'all', 'F6':'all', 'F7':'all'}
    self.setStatusBar(QStatusBar(self))
    self.statusBar().addWidget(self.statusBarW)
    self.changeStatusbar()

    #Content
    self.configuration = configuration
    self.comm = Communicate(None, self.configuration)
    self.table = Table(self.comm)
    self.setCentralWidget(self.table)      # Set the central widget of the Window
    self.suggestFileOpen = True


  def execute(self, command:list[str]) -> None:
    """
    execute command

    Args:
      command (list): list of commands
    """
    if command[0]=='open':
      lastPath = self.configuration['lastDirectory'] or str(Path.home())
      if fileName := QFileDialog.getOpenFileName(self,'Open proprietary binary file', lastPath, '*.*')[0]:
        self.configuration['lastDirectory'] = str(Path(fileName).parent)
        with open(Path.home()/'.pyMARBLE.json', 'w', encoding='utf-8') as fOut:
          fOut.write(json.dumps(self.configuration, indent=2))
        self.comm.binaryFile = BinaryFile(fileName)
        self.comm.changeTable.emit()
    elif command[0]=='website':
      webbrowser.open('https://pypi.org/project/pymarble/')
    elif command[0]=='about':
      showMessage(self, 'About MARBLE', ABOUT_TEXT)
    elif command[0]=='exit':
      self.close()
    elif command[0] in ['F5','F6','F7']:
      listNext = ['all', 'none', 'only', 'all']
      idx = listNext.index(self.toggleState[command[0]])
      self.toggleState[command[0]] = listNext[idx+1]
      self.comm.toggle.emit(self.toggleState['F5'],self.toggleState['F6'],self.toggleState['F7'])
      self.changeStatusbar()
    elif command[0]=='tableHeader':
      dialog = TableHeader(self.comm)
      dialog.exec()
    elif command[0]=='restart':
      restart()
    # ------------------------
    #check for existing file: as remainder use open file
    # ------------------------
    elif self.comm.binaryFile is None:
      showMessage(self, 'Error', 'An open file is required to execute the command.','Critical')
    #commands that require open binary file
    elif command[0]=='metaEditor':
      dialog = MetaEditor(self.comm)
      dialog.exec()
    elif command[0]=='saveTags':
      self.comm.binaryFile.saveTags()           # type: ignore[misc]
    elif command[0]=='loadTags':
      self.comm.binaryFile.loadTags()           # type: ignore[misc]
      self.comm.changeTable.emit()
    elif command[0]=='savePython':
      self.comm.binaryFile.savePython()         # type: ignore[misc]
    elif command[0]=='loadPython':
      self.comm.binaryFile.loadPython()         # type: ignore[misc]
      self.comm.changeTable.emit()
    elif command[0]=='useExported':
      lastPath = self.configuration['lastDirectory'] or str(Path.home())
      if fileName := QFileDialog.getOpenFileName(self,'Open exported csv file', lastPath, '*.*')[0]:
        if self.comm.binaryFile.useExportedFile(fileName):  # type: ignore[misc]
          self.comm.binaryFile.fill()            # type: ignore[misc]
          self.comm.changeTable.emit()
        else:
          showMessage(self, 'Could not use exported data', INFO_EXPORTED_FILE, 'Information')
    elif command[0]=='extractPython':
      self.comm.binaryFile.savePython()         # type: ignore[misc]
      pyFile = f'{os.path.splitext(self.comm.binaryFile.fileName)[0]}.py'
      result = subprocess.run(['python3', pyFile, self.comm.binaryFile.fileName], stdout=subprocess.PIPE, \
                              check=False)
      showMessage(self, 'Result of extraction', result.stdout.decode('utf-8'), 'Information')
    else:
      logging.error('unknown command %s', command)
    return


  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    executed upon resize

    Args:
      event (QResizeEvent): event
    """
    if self.suggestFileOpen and self.comm.binaryFile is None:
      self.suggestFileOpen = False
      ### DEFAULT CASE ###
      self.execute(['open'])
      ### FOR EASY TESTING
      # fileName = '/home/steffen/FZJ/DataScience/MARBLE_RFF/Software2/tests/examples/'+\
      #            'Membrane_Repeatability_05.mvl'
      # self.comm.binaryFile = BinaryFile(fileName)
      # if 'print_mode' in self.comm.configuration and self.comm.configuration['print_mode']=='hex':
      #   self.comm.binaryFile.printMode='hex'
      # self.comm.binaryFile.loadTags()                              # type: ignore[misc]
      # self.comm.changeTable.emit()
      ### additional part for testing of form
      # from .form import Form
      # dialog     = Form(self.comm, 70840)
      # dialog.show()
    return super().resizeEvent(event)


  def changeStatusbar(self) -> None:
    """ change statusbar slot """
    self.statusBar().removeWidget(self.statusBarW)
    allFKeys = [['F5','binary'], ['F6','data class'], ['F7','important']]
    postText = {'all':'all data', 'none':'except these', 'only':'only these'}
    newText = ''.join(f'\t{key} - toggle {text}: {postText[self.toggleState[key]]}' for key, text in allFKeys)
    self.statusBarW = QLabel(newText)
    self.statusBar().addWidget(self.statusBarW)
    return


##############
## Main function
def main() -> None:
  """ Main method and entry point for commands """
  # Configuration file: could be used for logging changes
  if not (Path.home()/'.pyMARBLE.json').exists():
    with open(Path.home()/'.pyMARBLE.json', 'w', encoding='utf-8') as fOut:
      fOut.write(json.dumps(defaultConfiguration, indent=2))
  with open(Path.home()/'.pyMARBLE.json', 'r', encoding='utf-8') as fIn:
    configuration = json.load(fIn)
  # logging has to be started first
  # - to screen
  #   logPath = Path.home()/'pyMARBLE.log'
  #   old versions of basicConfig do not know "encoding='utf-8'"
  #     filename=logPath,
  logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start MARBLE GUI')
  # remainder
  app = QApplication()
  window = MainWindow(configuration)
  # qtawesome and matplot cannot coexist
  import qtawesome as qta
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistance
  window.show()
  app.exec()
  logging.info('End MARBLE GUI')
  return

# called by python3 -m pymarble.gui.gui
if __name__ == '__main__':
  main()
