# Software for deciphering proprietary binary data-files | Developer notes

# Contributors
- Steffen Brinckmann (IEK-2, FZJ) [Principal investigator]
- Volker Hofmann (IAS-9 and HMC, FZJ)
- Fiona D'Mello (IAS-9 and HMC, FZJ)

## Code
### Backend
- Can be found within the 'pymarble/' directory.
- Entry point is the main function in cli.py file within 'pymarble/'

### Frontend
- Can be found within the 'pymarble/GUI' directory.
- Entry point is the main function in gui.py file

## Tests / User-cases
- All testing related files can be found under the 'tests/' folder
- testBackend.sh tests all tutorials
- tutorials are for human reading as well as automatic testing
  - backendTutorial python implementation of a typical run
- Three example files are supplied

## For publishing code
#TODO_P1 create more tests, reduce type: ignore !!
``` bash
pylint pymarble
mypy pymarble

tests/testBackend.sh

coverage erase; coverage run --source pymarble -m pytest tests; coverage html
firefox htmlcov/index.html

cp ../Documentation/README.md README_pypi.md
```



rm dist/pymarble-*



## Python data-types and their byteSize
This table is helpful for developers to quickly find byte-lengths

|Format|C Type             |Python type            |Standard size |
|------|-------------------|-----------------------|--------------|
|x     |pad byte           |no value               |              |
|c     |char               |bytes of length 1      |1             |
|b     |signed char        |integer                |1             |
|B     |unsigned char      |integer                |1             |
|?     |_Bool              |bool                   |1             |
|h     |short              |integer                |2             |
|H     |unsigned short     |integer                |2             |
|i     |int                |integer                |4             |
|I     |unsigned int       |integer                |4             |
|l     |long               |integer                |4 -not helpful|
|L     |unsigned long      |integer                |4 -not helpful|
|q     |long long          |integer                |8             |
|Q     |unsigned long long |integer                |8             |
|n     |ssize_t            |integer                |              |
|N     |size_t             |integer                |              |
|e     |                   |float                  |2             |
|f     |float              |float                  |4             |
|d     |double             |float                  |8             |
|s     |char[]             |bytes                  |              |
|p     |char[]             |bytes                  |              |
|P     |void*              |integer                |              |
