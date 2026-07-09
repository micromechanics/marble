[![Pylint](https://github.com/micromechanics/marble/actions/workflows/pylint.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/pylint.yml)
[![MyPy](https://github.com/micromechanics/marble/actions/workflows/mypy.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/mypy.yml)
[![pypi](https://github.com/micromechanics/marble/actions/workflows/pypi.yml/badge.svg)](https://github.com/micromechanics/marble/actions/workflows/pypi.yml)
[![coverage](https://codecov.io/gh/micromechanics/marble/graph/badge.svg?token=3Z5TL6SG1H)](https://codecov.io/gh/micromechanics/marble)

# Software for deciphering proprietary binary data files | Developer notes


> :warning: **Users: all documentation is available on [GitHub Pages](https://micromechanics.github.io/marble/).**
>
> **This page is for developers and contains helpful project notes.**

---

## Contributors
- Steffen Brinckmann (IEK-2, FZJ) [Principal investigator]
- Volker Hofmann (IAS-9 and HMC, FZJ)
- Fiona D'Mello (IAS-9 and HMC, FZJ)

## Open Issues
Default location for open issues: this section.

1. High `pymarble/section.py:64-97` - `Section.setData()` raises `UnboundLocalError` for dict input.
2. High `pymarble/fileUtil.py:24-38` - `findValue()` fails for zero-valued searches because it divides by the target value.
3. High `setup.cfg:15`, `pymarble/cli.py:50`, `pymarble/file.py:15-16` - the declared Python 3.7 floor conflicts with runtime `list[str]` / `dict[str, ...]` annotations.
4. Medium `pymarble/fileUtil.py:26-48` - `findValue()` returns `[]` in its default verbose mode, so callers do not get the matches back.
5. Medium `pymarble/fileInputOutput.py:60-96`, `pymarble/section.py:108-116` - tag serialization is not escaped and breaks on `|` and XML metacharacters.

## Documentation
### Backend
- Located in the `pymarble/` directory.
- Entry point is `main()` in `pymarble/cli.py`.

### Frontend
- Located in the `pymarble/gui/` directory.
- Entry point is `main()` in `pymarble/gui/gui.py`.

### Tests / User-cases
- All testing files are under `tests/`.
- Primary test runner is `pytest`.
- `testBackend.sh` is a legacy tutorial/E2E script.
- Tutorials are intended for both human reading and automated testing.
- Multiple example files are available under `tests/examples/`.

## Quick developer checks
Run these before opening a PR:
``` bash
pylint $(git ls-files 'pymarble/*')
mypy pymarble
pytest tests
make -C docs html
```

### Run a single test (recommended during development)
Single file:
``` bash
pytest tests/test_section.py
```

Single test function:
``` bash
pytest tests/test_section.py::testSection
```

Name filter:
``` bash
pytest tests -k testSection
```

## Steps for publishing code
``` bash
pylint $(git ls-files 'pymarble/*')
mypy pymarble
make -C docs html

pytest tests
```

Optional legacy e2e/tutorial regression:
``` bash
bash tests/testBackend.sh
```
Note: `testBackend.sh` uses the external tool `punx` and writes generated files to `tests/examples/`.

### Create code coverage
``` bash
coverage erase
python -m coverage run --source pymarble -m pytest tests
coverage report -m
coverage html
firefox htmlcov/index.html
rm -r htmlcov
```

## For documentation: creating images / videos
- Set a fixed window size in `gui.py`.
- Change monitor resolution to `1280x720`.


## Test code with Python only
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
This table helps developers quickly find byte lengths.

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
|l     |long               |integer                |4 (not helpful)|
|L     |unsigned long      |integer                |4 (not helpful)|
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
