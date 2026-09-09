"""GUI tutorial screenshots for the sample tensile-machine file."""
import copy
import shutil
from pathlib import Path

from PySide6.QtCore import Qt  # pylint: disable=no-name-in-module

from pymarble.gui.defaults import defaultConfiguration
from pymarble.gui.gui import MainWindow


SCREENSHOT_NAMES = [
  '01-file-open.png',
  '02-automatic-identification.png',
  '03-time-labeled.png',
  '04-signals-labeled.png',
  '05-metadata-labeled.png',
  '06-converter-saved.png',
]


def test_gui_tutorial_screenshots(qtbot, tmp_path):
  """Run the sample workflow and save screenshots for the GUI tutorial."""
  repository = Path(__file__).parents[1]
  source = repository/'tests'/'examples'/'Membrane_Repeatability_05.mvl'
  sample = tmp_path/source.name
  shutil.copy2(source, sample)
  screenshotDirectory = repository/'docs'/'source'/'_static'/'GuiTutorial'
  screenshotDirectory.mkdir(parents=True, exist_ok=True)

  configuration = copy.deepcopy(defaultConfiguration)
  configuration['columns'] = ['start', 'length', 'dType', 'key', 'unit', 'prob', 'important', 'value']
  window = MainWindow(configuration, str(sample))
  qtbot.addWidget(window)
  window.setWindowState(Qt.WindowState.WindowNoState)
  window.setFixedSize(1400, 800)
  window.show()
  window.table.change(resizeColumns=True)
  qtbot.wait(100)

  def saveScreenshot(number:int) -> None:
    screenshot = screenshotDirectory/SCREENSHOT_NAMES[number]
    assert window.grab().save(str(screenshot))
    assert screenshot.stat().st_size > 0

  def focusOffset(offset:int) -> None:
    row = window.table.rowIDs.index(offset)
    window.table.table.setCurrentCell(row, 0)
    window.table.table.verticalScrollBar().setValue(row)
    qtbot.wait(100)

  saveScreenshot(0)

  binaryFile = window.comm.binaryFile
  assert binaryFile is not None
  binaryFile.automatic('x_z_p_a', progress=window.progressbar)
  binaryFile.fill()
  window.table.change(resizeColumns=True)
  qtbot.wait(100)
  saveScreenshot(1)

  binaryFile.label(69280, '195|d|time|s')
  window.table.change(resizeColumns=True)
  focusOffset(69280)
  qtbot.wait(100)
  saveScreenshot(2)

  binaryFile.label(70840, '195|f|displacement|mm')
  binaryFile.label(71620, '195|f|force|N|https://en.wikipedia.org/wiki/Force')
  window.table.change(resizeColumns=True)
  focusOffset(70840)
  qtbot.wait(100)
  saveScreenshot(3)

  for offset, key in [(6836, 'displacement_label'), (12832, 'force_label'),
                      (21148, 'process_name'), (32228, 'some_name'), (58448, 'path_name')]:
    binaryFile.label(offset, f'||{key}')
  window.table.change(resizeColumns=True)
  focusOffset(6836)
  qtbot.wait(100)
  saveScreenshot(4)

  window.execute(['savePython'])
  window.table.change(resizeColumns=True)
  focusOffset(71620)
  qtbot.wait(100)
  assert sample.with_suffix('.py').exists()
  saveScreenshot(5)
