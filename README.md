[![Pylint](https://github.com/micromechanics/marble/actions/workflows/pylint.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/pylint.yml)
[![MyPy](https://github.com/micromechanics/marble/actions/workflows/mypy.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/mypy.yml)
[![pypi](https://github.com/micromechanics/marble/actions/workflows/pypi.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/pypi.yml)

# Software for deciphering proprietary binary data-files | Developer notes


> :warning: **Users: all documentation can be found at [Pypi-pages](https://pypi.org/project/pymarble/)**
>
> **This page / area is for developers and contains some helpful information for them**

---

## Contributors
- Steffen Brinckmann (IEK-2, FZJ) [Principal investigator]
- Volker Hofmann (IAS-9 and HMC, FZJ)
- Fiona D'Mello (IAS-9 and HMC, FZJ)

## Documentation
### Backend
- Can be found within the 'pymarble/' directory.
- Entry point is the main function in cli.py file within 'pymarble/'

### Frontend
- Can be found within the 'pymarble/GUI' directory.
- Entry point is the main function in gui.py file

### Tests / User-cases
- All testing related files can be found under the 'tests/' folder
- testBackend.sh tests all tutorials
- tutorials are for human reading as well as automatic testing
  - backendTutorial python implementation of a typical run
- Three example files are supplied

## Steps for publishing code
``` bash
pylint pymarble/*
mypy pymarble/
make -C docs html

tests/testBackend.sh

coverage erase; coverage run --source pymarble -m pytest tests; coverage html
firefox htmlcov/index.html
rm -r htmlcov
```

## For documentation: creating images / videos
- gui.py set fixed size
- change monitor settings to 1280,720


## Test code with python only
``` python
from pymarble.file import BinaryFile
bf = BinaryFile('tests/examples/1-11-OA_0000.emi')
bf.loadTags()
bf.automatic(methodOrder='i', start=814)
methods = bf.automatic(methodOrder='_', getMethods=True)
bf.printList()
bf.printList(True)
```

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
