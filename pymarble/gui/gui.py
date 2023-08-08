""" Graphical user interface includes all widgets """
import os, logging, webbrowser, json, sys
from typing import Any
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QScrollArea # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot      # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut  # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

os.environ['QT_API'] = 'pyside6'

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """
  def __init__(self) -> None:
    #global setting
    super().__init__()
    venv = ' without venv' if sys.prefix == sys.base_prefix and 'CONDA_PREFIX' not in os.environ else ' in venv'
    self.setWindowTitle(f"MARBLE for Python")
    self.setWindowState(Qt.WindowMaximized) # type: ignore
    # resourcesDir = Path(__file__).parent/'Resources'
    # self.setWindowIcon(QIcon(QPixmap(resourcesDir/'Icons'/'favicon64.png')))

    # #Menubar
    # menu = self.menuBar()
    # projectMenu = menu.addMenu("&Project")
    # Action('&Export .eln',          self, [Command.EXPORT], projectMenu)
    # Action('&Import .eln',          self, [Command.IMPORT], projectMenu)
    # projectMenu.addSeparator()
    # Action('&Exit',                 self, [Command.EXIT],   projectMenu)

    # viewMenu = menu.addMenu("&Lists")
    # if hasattr(self.backend, 'db'):
    #   for docType, docLabel in self.comm.backend.db.dataLabels.items():
    #     if docType[0]=='x' and docType[1]!='0':
    #       continue
    #     shortcut = f"Ctrl+{shortCuts[docType]}" if docType in shortCuts else None
    #     Action(docLabel,            self, [Command.VIEW, docType], viewMenu, shortcut=shortcut)
    #     if docType=='x0':
    #       viewMenu.addSeparator()
    #   viewMenu.addSeparator()
    #   Action('&Tags',               self, [Command.VIEW, '_tags_'], viewMenu, shortcut='Ctrl+T')
    #   Action('&Unidentified',       self, [Command.VIEW, '-'],      viewMenu, shortcut='Ctrl+U')
    #     #TODO_P5 create list of unaccessible files: linked with accessible files

    # systemMenu = menu.addMenu("&System")
    # Action('&Project groups',       self, [Command.PROJECT_GROUP],    systemMenu)
    # changeProjectGroups = systemMenu.addMenu("&Change project group")
    # if hasattr(self.backend, 'configuration'):                       #not case in fresh install
    #   for name in self.backend.configuration['projectGroups'].keys():
    #     Action(name,                self, [Command.CHANGE_PG, name], changeProjectGroups)
    # Action('&Syncronize',           self, [Command.SYNC],            systemMenu, shortcut='F5')
    # Action('&Questionaires',        self, [Command.ONTOLOGY],        systemMenu)
    # systemMenu.addSeparator()
    # Action('&Test extraction from a file',   self, [Command.TEST1],  systemMenu)
    # Action('Test &selected item extraction', self, [Command.TEST2],  systemMenu, shortcut='F2')
    # Action('Update &Extractor list',         self, [Command.UPDATE], systemMenu)
    # systemMenu.addSeparator()
    # Action('&Configuration',         self, [Command.CONFIG],         systemMenu, shortcut='Ctrl+0')

    # helpMenu = menu.addMenu("&Help")
    # Action('&Website',               self, [Command.WEBSITE],        helpMenu)
    # Action('&Verify database',       self, [Command.VERIFY_DB],      helpMenu, shortcut='Ctrl+?')
    # Action('Shortcuts',              self, [Command.SHORTCUTS],      helpMenu)
    # Action('Todo list',              self, [Command.TODO],           helpMenu)
    # helpMenu.addSeparator()
    # #shortcuts for advanced usage (user should not need)
    # QShortcut('F9', self, lambda : self.execute('restart'))

    #GUI elements
    # mainWidget, mainLayout = widgetAndLayout('H')
    # self.setCentralWidget(mainWidget)      # Set the central widget of the Window
    # body = Body(self.comm)        #body with information
    # self.sidebar = Sidebar(self.comm)  #sidebar with buttons
    # sidebarScroll = QScrollArea()
    # sidebarScroll.setWidget(self.sidebar)
    # if hasattr(self.comm.backend, 'configuration'):
    #   sidebarScroll.setFixedWidth(self.comm.backend.configuration['GUI']['sidebarWidth']+10)
    # mainLayout.addWidget(sidebarScroll)
    # mainLayout.addWidget(self.sidebar)
    # mainLayout.addWidget(body)
    # self.comm.changeTable.emit('x0','')



##############
## Main function
def main() -> None:
  """ Main method and entry point for commands """
  # logging has to be started first
  logPath = Path.home()/'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  # remainder
  app = QApplication()
  window = MainWindow()
  theme = 'none' #window.backend.configuration['GUI']['theme']
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
  logging.info('End PASTA GUI')
  return

# called by python3 -m pymarble.gui.gui
if __name__ == '__main__':
  main()
