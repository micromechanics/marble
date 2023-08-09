"""module that describes binary file that is to be deciphered"""
import os, io
from sortedcontainers import SortedDict
from .fileClass import FileProtocol
from .fileInputOutput import InputOutput
from .fileAutomaticIdentify import Automatic
from .fileUtil import Util
from .fileCommandLine import Commandline

class BinaryFile(InputOutput, Automatic, Util, Commandline):
  """
  class that describes binary file that is to be deciphered
  """
  def __init__(self:FileProtocol, fileName:str, verbose:int=1, fileType:str='disk'):
    '''
    initialize

    Args:
      filename: name of file
      verbose: verbose output. 0=no output; 1=minmal; 2=more
      fileType: disk or data

    '''
    super().__init__()
    #All options should be here. GUI can change these defaults
    self.optGeneral   = {'maxSize':-1}
    self.optFind      = {'maxError':1e-4}
    self.optAutomatic = {'minChars':10,   'minArray': 50, 'maxExp':11, 'minZeros':16, 'minEntropy':3}
    self.optEntropy   = {'blockSize':256, 'skipEvery':5}

    self.fileType   = fileType  #'disk': read directly from disk; 'ram' copy file in ram and work in virt. disk
                                #'data': #futureFeature copy file into data & work on different sections
                                #   in parallel
    self.fileName                  = fileName
    self.fileLength                = -1
    self.content                   = SortedDict()
    self.periodicity:dict[str,int] = {}
    self.file                      = io.BytesIO()
    self.printMode                 = 'dec' #      printMode: dec-decimal, hex-hexadecimal
    self.verbose                   = verbose
    self.meta                      = {'vendor':'', 'label':'', 'software':'',\
                                      'ext':os.path.splitext(fileName)[1][1:], 'endian':'small'}

    self.initContent()
    return
