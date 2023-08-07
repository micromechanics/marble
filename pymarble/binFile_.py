import io
from typing import Protocol, Callable, Union, Optional
from sortedcontainers import SortedDict
from .section import Section

class BinaryFileProtocol(Protocol):
  # data
  fileName: str
  file: Union[io.BufferedReader, io.BytesIO]
  fileLength: int
  fileType: str
  content: SortedDict[int,Section]
  meta: dict[str,str]
  periodicity: dict[str,int]  
  optGeneral: dict[str, int]
  optFind: dict[str, float]
  optAutomatic: dict[str, int]
  optEntropy: dict[str,int]
  verbose: int
  printMode: str

  # functions
  initContent: Callable[[],None]
  findBytes: Callable[[Union[str,float],str,int],int]
  findValue: Callable[[Union[str,float],str,bool,int],list[int]]
  automatic: Callable[[str],None]
  findXMLSection: Callable[[],None]
  findZeroSection: Callable[[int],None]
  findAsciiSection: Callable[[int],None]
  primaryTimeData: Callable[[int],None]
  fill: Callable[[],None]
  pretty: Callable[[int],str]
  pythonHeader: Callable[[],str]
  byteToString: Callable[[bytes,int],str]
  diffStrings: Callable[[str,str],list[str]]
  entropy: Callable[[int,bool],float]  
