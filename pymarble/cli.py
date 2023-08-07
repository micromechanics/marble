#!/usr/bin/env python3
""" Main function when command-line commands used
"""
import warnings, sys, traceback
from .binaryFile import BinaryFile

#Entry point to the non-gui app
def main():
  '''
  main function
  '''

  def printHelp():
    '''
    Print help information
    '''
    print('Help on commands')
    print('--- Automatic functions ---')
    print('s_ <n>       : find a streak of type _; starting at offset n')
    print('m  <seq>       : use autoMatic evaluation, with sequence seq')
    print('z            : do entropy')
    print('--- Find data ---')
    print('f_ <f>       : find _ where _ is i:integer, d:double, f:float and f is the value')
    print('b_ <f>       : find _ where _ is i,d,f and f is the value [algorithm uses binary pattern]')
    print('e <file name>: values based on exported file')
    print('               file has to be np.loadtxt readable')
    print('--- Print information ---')
    print('p_ <n>       : print next as _ where _ is i,d,f,...; n-times')
    print('a  <n>       : print ascii representation: n number of rows; omit if all rows')
    print('g  <n>       : goto n-byte (origin if omitted)')
    print('--- Read / Write identified ---')
    print('l            : list items identified')
    print('r <i> <s>    : store text string s of item starting at address i; this automatically sets')
    print('               the important flag and the probability to 100.')
    print('d <i>        : draw the data found starting at i')
    print('y <seq>      : remove list of sections ')
    print('t <c> <s> <e>: mark periodicity in multiTest file: c-position of count; s-postion of')
    print('               periodicity start; e-position of periodicity end')
    print('--- Other functions ---')
    print('c <file name>: compare / diff to other binary file')
    print('x mode       : switch between dec/hex mode')
    print('ot           : output tags file')
    print('it           : read tags file')
    print('op           : output python file')
    print('ip           : import python file')
    print('x fill       : fill content and check order')
    print('x verify     : verify some sanity tests')
    print('q            : quit')
    print('h            : help')
    print('')
    print('Alternative: marbleCLI fileName.bin "command 1; command2" ')

  warnings.filterwarnings("ignore")
  # logFile = os.path.splitext(sys.argv[1])[0]+'_rff.log'
  # sys.stdout = Logger(logFile)
  if len(sys.argv)<2:
    printHelp()

  else:
    fBIN = BinaryFile(sys.argv[1], verbose=1)
    numCommands = 99999 if len(sys.argv)==2 else len(sys.argv[2].split(';'))
    for idx in range(numCommands):
      if len(sys.argv)==2:
        command = input("\n\n>> Command: ")
      else:
        command = sys.argv[2].split(';')[idx].strip()

      try:
        # smart\automatic functions
        if command.startswith('s'):
          fBIN.findStreak(command[1],int(command.split()[1], 0))
        elif command.startswith('m'):
          methodOrder = 'x_z_p_a' if len(command.split())==1 else command.split()[1]
          fBIN.automatic(methodOrder)
        elif command.startswith('z'):
          fBIN.entropy()

        # find data
        elif   command.startswith('f'):
          fBIN.findValue(command.split()[1],command[1])
        elif   command.startswith('b'):
          fBIN.findBytes(command.split()[1],command[1])
        elif command.startswith('e'):
          fBIN.useExportedFile(command.split()[1])

        # print informaton
        elif command.startswith('p'):
          fBIN.printNext(command.split()[1],command[1])
        elif command.startswith('a'):
          fBIN.printAscii(None if len(command.split())==1 else command.split()[1])
        elif command.startswith('g'):
          fBIN.file.seek(0 if len(command.split())==1 else int(command.split()[1],0) )

        # read/write identified
        elif command.startswith('l'):
          fBIN.printList(command.endswith('a'))
        elif command.startswith('r'):  #manually labeled
          parts = command.split()
          fBIN.label(start=parts[1], data=' '.join(parts[2:]) )
        elif command.startswith('d'):
          drawMode = 1 if command.split()[0]=='d' else int(command.split()[0][1])
          fBIN.plot(command.split()[1], drawMode)
        elif command.startswith('y'):
          for start in [int(i) for i in command.split()[1].split('_')]:
            del fBIN.content[start]
        elif command.startswith('t'):
          fBIN.periodicity =  dict(zip(['count','start','end'],command.split()[1:]))

        # misc. functions
        elif command.startswith('c'):
          fBIN.compare(command.split()[1])
        elif command.startswith('n'):
          fBIN.addNote()
        elif command=='x mode':
          if fBIN.printMode=='dec':
            fBIN.printMode='hex'
          else:
            fBIN.printMode='dec'
        elif command=='ot':
          fBIN.saveTags()
        elif command=='it':
          fBIN.loadTags()
        elif command=='op':
          fBIN.savePython()
        elif command.startswith('ip'):
          pyFile = None if len(command.split())<3 else command.split()[-1]
          fBIN.loadPython(pyFile)
        elif command=='x fill':
          fBIN.fill()
        elif command=='x verify':
          fBIN.verify()
        elif command=='q':
          break
        elif command=='h':
          printHelp()
        else:
          print('I did not understand you')
      except:
        print('**ERROR occurred: verify your command')
        print(traceback.format_exc())

if __name__ == '__main__':
  main()
