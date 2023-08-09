""" Misc. functions for MARBLE """
import os, sys

def restart() -> None:
  """
  Complete restart: cold restart
  """
  try:
    os.execv('marbleGUI',[''])  #installed version
  except Exception:
    os.execv(sys.executable, ['python3','-m','pymarble.gui.gui']) #started for programming or debugging
  return
