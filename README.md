# Software for deciphering proprietary binary data-files | Developer notes

# Contributors
- Steffen Brinckmann (IEK-2, FZJ) [Principal investigator]
- Volker Hofmann (IAS-9 and HMC, FZJ)
- Fiona D'Mello (IAS-9 and HMC, FZJ)

## Using 'Poetry' dependency management
1. Activate poetry in terminal window in the 'Software' directory
```
poetry shell
```
to have a virtual env created. It is within this environment all development activities can be comfortably continued in a clean and isolated manner.

2. (one-time) run
```
poetry install
```
to have all project dependencies installed within the environment.

3. Use either command to stat backend or frontend application
```
marble-cli
marble-gui
```
## Code
### Backend
- Can be found within the 'pymarble/' directory.
- Entry point is the main function in rff.py file within 'pymarble/'

### Frontend
- Can be found within the 'pymarble/' directory.
- Entry point is the main function in app.py file

## Tests / User-cases
- All testing related files can be found under the 'tests/' folder
- testBackend.sh tests all tutorials
- tutorials are for human reading as well as automatic testing
  - backendTutorial python implementation of a typical run
- Three example files are supplied

## For publishing code
From within Software directory:

Before:
``` bash
pylint pymarble

#TODO_P1 create more tests!!
mypy pymarble/backend/*.py
coverage erase; coverage run --source pymarble/backend -m pytest tests; coverage html
firefox htmlcov/index.html 

poetry shell
> tests/testBackend.sh
> exit
rm dist/pymarble-*
```
and increase version number in pyproject.toml

For publication
``` bash
cp ../Documentation/README.md README_pypi.md
poetry build
poetry publish
git commit -a -m 'Version 0.9.4'
git push
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
