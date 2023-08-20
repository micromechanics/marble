"""data and functions of class, have to be separate from file.py"""
import io
from typing import Protocol, Callable, Union, Any
from sortedcontainers import SortedDict
from .section import Section

class FileProtocol(Protocol):
  """ Class data and functions """
  # data
  fileName: str
  file: Union[io.BufferedReader, io.BytesIO]
  fileLength: int
  fileType: str
  content: SortedDict[int,Section]
  meta: dict[str,str]
  periodicity: dict[str,int]
  rowFormatMeta: list[dict[str,str]]
  rowFormatSegments: set[int]
  optFind: dict[str, float]
  optAutomatic: dict[str, int]
  optEntropy: dict[str,int]
  verbose: int
  printMode: str

  # functions
  automatic: Callable[[str],None]
  initContent: Callable[[],None]
  findBytes: Callable[[Union[str,float],str,int],int]
  findValue: Callable[[Union[str,float],str,bool,int],list[int]]
  findAnchor: Callable[[int,int], tuple[int, bool]]
  findXMLSection: Callable[[],None]
  findZeroSection: Callable[[int],None]
  findAsciiSection: Callable[[int],None]
  primaryTimeData: Callable[[int],None]
  find2DImage: Callable[[int], None]
  fill: Callable[[],None]
  pretty: Callable[[int],str]
  pythonHeader: Callable[[],str]
  byteToString: Callable[[bytes,int],str]
  diffStrings: Callable[[str,str],list[str]]
  entropy: Callable[[int,bool],float]
  verify: Callable[[Any], None]
