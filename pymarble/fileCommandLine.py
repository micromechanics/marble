"""Functions that output to commandline in commandline usage"""
import re, struct
from prettytable import PrettyTable
from .section import SECTION_OUTPUT_ORDER
from .fileClass import FileProtocol

class Commandline():
  """ Mixin that includes all functions for the commandline """
  def printNext(self:FileProtocol, count:int, dType:str='i') -> None:
    '''
    print next variables in file

    Args:
        count: number of items printed
        dType: ['d','i','f'] data-type: double, int, float
    '''
    currPosition = self.file.tell()
    byteSize = struct.calcsize(dType)
    dataBin = self.file.read(count*byteSize)
    data = struct.unpack(str(count)+dType, dataBin) #get data
    if len(data)==1:
      if isinstance(data[0], bytes):
        print(currPosition,': ',data[0].decode('utf-8'))
      else:
        print(currPosition,': ',data[0])
    else:
      print(currPosition,data)
    return


  def printAscii(self:FileProtocol, numRows:int=-1) -> None:
    '''
    print the file as ascii and return to zero position

    Args:
        numRows: number of rows to print; default=None: print all
    '''
    bytesPerRow = 64
    offset = 0
    while True:
      dataBin = self.file.read(bytesPerRow)
      if len(dataBin)==0:
        break
      data = bytearray(dataBin).decode('utf-8', errors='replace')
      data = ''.join(re.findall(r'[ -~]',data))
      if len(data)>1:
        print(f'{self.pretty(offset)}: {data}')
      offset += bytesPerRow
      if numRows>-1 and offset/bytesPerRow > numRows-1:
        break
    self.file.seek(0)
    return


  def printList(self:FileProtocol, printBinary:bool=False) -> None:
    '''
    print list of all items
    - shorten long texts to 30 chars

    Args:
      printBinary: print also binary entries
    '''
    table = PrettyTable()
    table.field_names = ['position']+SECTION_OUTPUT_ORDER
    for start in self.content:
      if self.content[start].dType not in ['b','B'] or printBinary:
        row = [start]+self.content[start].toList()
        if self.printMode=='hex':
          row[0] = self.pretty(row[0])
          row[1] = self.pretty(row[1])
        row = [str(i)[:30] for i in row]
        table.add_row(row)
    table.align = "l"
    # table.border = False
    table.padding_width = 0
    print(table)
    return
