""" Graphical user interface includes all widgets """
import os, logging, webbrowser, json, subprocess
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt                                        # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut, QResizeEvent    # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from ..file import BinaryFile
from .defaults import defaultConfiguration
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
    Action('&Open binary file', self, ['open'],       fileMenu, shortcut='Ctrl+L')
    Action('Edit &metadata',    self, ['metaEditor'], fileMenu, shortcut='Ctrl+M')
    if 'advanced' in configuration:
      fileMenu.addSeparator()
      Action('Save tags-file',    self, ['saveTags'],   fileMenu)
      Action('Load tags-file',    self, ['loadTags'],   fileMenu)
    fileMenu.addSeparator()
    Action('&Save python-file',  self, ['savePython'], fileMenu)
    Action('Save and e&xtract',  self, ['extractPython'], fileMenu)
    if 'advanced' in configuration:
      Action('Load python-file',   self, ['loadPython'], fileMenu)
    fileMenu.addSeparator()
    Action('&Exit',             self, ['exit'],       fileMenu)

    viewMenu = menu.addMenu("&View")
    Action('&Hide binary',      self, ['hide'],       viewMenu, shortcut='Ctrl+H')
    Action('Table columns',     self, ['tableHeader'],viewMenu)

    helpMenu = menu.addMenu("&Help")
    Action('&Website',          self, ['website'],        helpMenu)
    #shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda : self.execute(['restart']))

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
      fileName = QFileDialog.getOpenFileName(self,'Open proprietary binary file', lastPath, '*.*')[0]
      if fileName:
        self.configuration['lastDirectory'] = str(Path(fileName).parent)
        with open(Path.home()/'.pyMARBLE.json', 'w', encoding='utf-8') as fOut:
          fOut.write(json.dumps(self.configuration, indent=2))
        self.comm.binaryFile = BinaryFile(fileName)
        self.comm.changeTable.emit()
    elif command[0]=='website':
      webbrowser.open('https://pypi.org/project/pymarble/')
    elif command[0]=='exit':
      self.close()
    elif command[0]=='hide':
      self.comm.toggle.emit()
    elif command[0]=='tableHeader':
      dialog = TableHeader(self.comm)
      dialog.exec()
    elif command[0]=='restart':
      restart()
    #check for existing file
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
    elif command[0]=='extractPython':
      self.comm.binaryFile.savePython()         # type: ignore[misc]
      pyFile = os.path.splitext(self.comm.binaryFile.fileName)[0]+'.py'
      result = subprocess.run(['python3', pyFile, self.comm.binaryFile.fileName], stdout=subprocess.PIPE, \
                              check=False)
      showMessage(self, 'Result of extraction', result.stdout.decode('utf-8'), 'Information')
    else:
      print(f'ERROR: unknown command {command}')
    return


  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    executed upon resize

    Args:
      event (QResizeEvent): event
    """
    if self.suggestFileOpen and self.comm.binaryFile is None:
      self.suggestFileOpen = False
      if False: #easy switch for fast testing
        self.execute(['open'])
      else:
        fileName = '/home/steffen/FZJ/DataScience/MARBLE_RFF/Software2/tests/examples/Membrane_Repeatability_05.mvl'
        self.comm.binaryFile = BinaryFile(fileName)
        if 'print_mode' in self.comm.configuration and self.comm.configuration['print_mode']=='hex':
          self.comm.binaryFile.printMode='hex'
        self.comm.binaryFile.loadTags()
        self.comm.changeTable.emit()
        # from .form import Form
        # dialog     = Form(self.comm, 70840)
        # dialog.show()

    return super().resizeEvent(event)



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
  theme = configuration['theme']
  if theme!='none':
    apply_stylesheet(app, theme=f'{theme}.xml')
  # qtawesome and matplot cannot coexist
  import qtawesome as qta
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
    print('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistance
  window.show()
  app.exec()
  logging.info('End MARBLE GUI')
  return

# called by python3 -m pymarble.gui.gui
if __name__ == '__main__':
  main()
