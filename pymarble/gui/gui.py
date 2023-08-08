""" Graphical user interface includes all widgets """
import os, logging, webbrowser, json
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt                                        # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut, QResizeEvent    # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from ..file import BinaryFile
from .defaults import defaultConfiguration
from .style import Action
from .communicate import Communicate
from .table import Table

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
    fileMenu.addSeparator()
    Action('Save tags-file',    self, ['saveTags'],   fileMenu)
    Action('Load tags-file',    self, ['loadTags'],   fileMenu)
    fileMenu.addSeparator()
    Action('Save python-file',  self, ['savePython'], fileMenu)
    Action('&Load python-file', self, ['loadPython'], fileMenu)
    fileMenu.addSeparator()
    Action('&Exit',             self, ['exit'],       fileMenu)

    viewMenu = menu.addMenu("&View")
    Action('&Hide binary',      self, ['hide'],       viewMenu, shortcut='Ctrl+H')

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
    elif command[0]=='saveTags':
      pass
    elif command[0]=='loadTags':
      pass
    elif command[0]=='savePython':
      pass
    elif command[0]=='loadPython':
      pass
    elif command[0]=='exit':
      self.close()
    elif command[0]=='hide':
      self.comm.toggle.emit()
    elif command[0]=='website':
      webbrowser.open('https://pypi.org/project/pymarble/')
    else:
      print(f'ERROR: unknown command {command}')


  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    executed upon resize

    Args:
      event (QResizeEvent): event
    """
    if self.suggestFileOpen and self.comm.binaryFile is None:
      self.suggestFileOpen = False
      self.execute(['open'])
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
