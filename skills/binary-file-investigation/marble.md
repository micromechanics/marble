# marble path: pymarble API reference

Read this for files that marble can describe: one linear sequence of values. Offsets below are placeholders (`<offset>`); replace them with the offsets of your file.

## Label fields: the `tag()` helper

Define this helper first; the sections below use it.

```python
from pymarble.file import BinaryFile
from pymarble.section import Section
fBIN = BinaryFile('<scratchpad>/data.bin_investigation/data.bin', verbose=1)

def tag(start, length, dType, key, unit='', note='', prob=100, dClass='metadata', count=None, shape=None):
  '''label one confirmed field; prob: high 100, medium 75, low 50; note: source types + short chain
     count: offsets of the count sections that give the size; shape: dimensions of an array'''
  old = fBIN.content.get(start)
  if old is not None and old.length==length and old.dType==dType:
    old.key, old.unit, old.note, old.prob, old.dClass, old.important = key, unit, note, prob, dClass, True
    old.count, old.shape = count or old.count, shape or old.shape
  else:
    fBIN.content[start] = Section(length=length, dType=dType, key=key, unit=unit, note=note, prob=prob,
                                  dClass=dClass, important=True, count=count or [], shape=shape or [])
    fBIN.fill()

tag(<offset>, 1, 'f', 'speed', 'm/s', 'B+E: f32 = TXT "Speed 1 mm/min" as 1.667e-5 m/s; C: varies per test')
tag(<offset>, 4096*4096, 'H', 'image', 'counts', dClass='primary', count=[<offset of k1>, <offset of k2>],
    shape=[4096, 4096])   # the count sections must be labelled first, with dClass='count'
```

- Use `tag` rather than `label()` for single values: `label()` treats every `f`/`d` section as an array and forces `prob` to 100.
- `fBIN.content` is a `SortedDict[int, Section]` keyed by start offset; the fields are described in `pymarble/section.py`.
- Look at values: `fBIN.file.seek(<offset>); fBIN.printNext(20, 'f')`, `fBIN.printAscii(10)`, `fBIN.findStreak('d', <offset>)`.
- Tune the automatic search with `fBIN.optAutomatic`, `fBIN.optFind` and `fBIN.optEntropy`.

## Automatic search

- `fBIN.automatic('x_z_p_a')`: x XML, z zero sections, p time series (primary data), a ascii incl. length-prefixed strings.
- `p` can be very slow on large files (minutes on a 33 MB image file, where `x_z_a` takes seconds). Run it on one section only: `fBIN.automatic('p', start=<offset>)`.

## Exports

`useExportedFile` matches each export column with the binary; it needs a file readable by `np.loadtxt`. Clean a copy in the investigation folder (cut the header, convert decimal commas, remove CR); never modify the original:

```bash
awk 'f{gsub(",",".");print} /^<first header word>/{f=1}' "export.TXT" | tr -d '\r' > <scratchpad>/data.bin_investigation/export_clean.txt
```

```python
fBIN.useExportedFile('<scratchpad>/data.bin_investigation/export_clean.txt')
```

Columns whose best match deviates by more than `fBIN.optFind['maxErrorExport']` (default 1 %) are rejected and logged. It assumes one continuous array per column; for data stored row by row, see below.

## Compare samples

```python
fBIN.compare(['<scratchpad>/data.bin_investigation/other1.bin', '<scratchpad>/data.bin_investigation/other2.bin'],
             anchor=rb'<regex that starts each measurement, e.g. a date string>')
```

- **Files first.** Per file pair: sizes, whether identical, common prefix, fraction of equal bytes at the same positions. Interpret yourself:
  - **Identical files** are duplicates.
  - **A high fraction of equal bytes** can mean a shared header, or cumulative files (the smaller file's measurements reappear in the larger one). Check which by looking at where the bytes differ.
  - Cumulative files contain the same measurements several times, so compare **measurements**, not files.
- **Anchor.** Something that repeats once per measurement (a date string, a count). `compare()` splits all files at the anchor into head, units and tail, compares the distinct segments aligned at their start and at their end, and reports the segment lengths.
- **Reading the results.**
  - Varying bytes are settings or results that change per measurement.
  - Constant bytes are instrument constants, or settings nobody changed in this batch; say so as a caveat.
  - Long runs of varying ranges are data blocks.
  - Segment lengths that differ by multiples of one number hint at the record size.
- **CLI:** `c <files> anchor=<regex>`.

## Search known values (batch)

```python
known = {'radius 200 µm': [200, 200e-6], 'speed 1 mm/min': [1, 1/60000], 'length 2 mm': [2, 0.002]}  # display unit, SI unit
for name, values in known.items():
  for value in values:
    for dType in ('f', 'd'):
      hits = [h for h in fBIN.findValue(value, dType, verbose=False) if int(h) < <end of region>]   # offsets are decimal strings
      if hits: print(f'{name:22s} {value:<10g} {dType} {hits[:5]}')
```

- `findValue` tests every byte offset; headers are often packed, so values sit at odd offsets.
- Search each value in display and SI units (mm → m, µm → m, nm → m, mm/min → m/s, N/min → N/s), and in the instrument's unit system once you know it (e.g. kgf).
- Restrict hits to the region under investigation: values common in the data (start loads, 0, 1.0) give many hits elsewhere. Resolve ambiguous hits through neighbouring fields or by comparing samples.
- **Rounded export values:** if a value is not found, search again with `fBIN.optFind['maxError'] = 2e-2`, then reset it to `1e-4`. A loose match is medium confidence until neighbouring fields or other samples confirm it.

## Data stored row by row

`automatic()` and `useExportedFile` assume one continuous array per channel. If a large float array has a count N just before it, test whether its length is k × N (k values per point): reshape to (N, k) with numpy, compare each column with the export (try unit scalings), then record the format:

```python
fBIN.setRowFormat(<offset>, <k>, 'f', columns=[{'key':'x','unit':'m'}, {'key':'force','unit':'N'}, ...])   # N read from the count in front
```

CLI: `rf <start> <k> <dType> key:unit,...`

## Several measurements per file (periodicity)

marble wraps the sections of the first measurement in a loop, `for idxTest in range(numberOfTests)`, and reads them sequentially with the relative offsets of the first measurement:

```python
fBIN.periodicity = {'count': <offset of the number of measurements>, 'start': <first section of a measurement>,
                    'end': <last section of a measurement>}
```

- **Count:** label the number of measurements as a count section: `tag(<offset>, 1, 'i', 'number_of_tests', dClass='count')`.
- **First and last section** must be labelled (important); otherwise the loop's position is off by the unlabelled length.
- **Equal gaps:** the gap from the last written section before the loop to `start` must equal the gap from the end of `end` to the next measurement's `start`. If they differ, label a small section before the loop so that they match.
- **Sections after the first measurement** must be unimportant: `for k in fBIN.content: if k > <end>: fBIN.content[k].important = False`.
- **Irregular measurements** (different gaps, e.g. embedded images only between test 1 and 2): periodicity cannot be used. Label each measurement separately with key suffixes `_t<k>` (`speed_t1`, `speed_t2`, …); the converter then reads fixed offsets, fits only files with the same layout, and writes everything into `test_1`. Say so in `format.md`.
- **Values outside the measurements** (file header, common settings) labelled with dClass `metadata` or `primary` go into the HDF5 group `/settings` (NXparameters).
- **Size check:** with a trailer after the last measurement, the converter prints "Translation NOT successful" although the data is read correctly; check the `.hdf5`.
- CLI: `t <count> <start> <end>`.

## Strings

- `automatic()` detects strings with a 2- or 4-byte length prefix; each gets a count section `strLen<offset>=<length>`, and the converter reads the string via that prefix. Trust the prefix over `strings` and plain ASCII detection, which can cut a string short or add neighbouring bytes.
- `automatic()` finds only strings of at least `optAutomatic['minChars']` (10) characters. Find shorter ones with `strings -n 4 -t d` and `xxd`, and label them: `tag(<offset>, <length>, 'c', '<key>')`. With a 4-byte prefix in front, also `tag(<offset>-4, 1, 'i', 'strLen<offset>=<length>', dClass='count')` and pass `count=[<offset>-4]`.

## Embedded images and files

Embedded files (JPEG, PNG, BMP, …) and raw byte images are dType `b`, important; the converter writes them as uint8 datasets. Find the length in the file header (e.g. BMP size field, a length field in front) or at the end marker (JPEG `ffd9`):

```python
tag(<offset>, <length>, 'b', 'image_jpeg', dClass='primary')
tag(<offset>, 64*64*4, 'b', 'image_bmp_pixels', dClass='primary', shape=[64, 64, 4])   # raw pixels: shape reshapes the uint8 array
```

## Coverage

```python
fBIN.coverage(['<scratchpad>/data.bin_investigation/other.bin'], anchor=rb'...')   # without samples: fBIN.coverage()
```

It reports fields (labelled sections vs. potential fields: 4 bytes per field, at most `optAutomatic['maxFieldsPerRegion']` = 32 per unknown region), varying (with samples) and bytes. Count the export coverage yourself.

## The marble converter

- `fBIN.savePython()` writes `data.py`: a converter whose end block describes every section (`key`, `unit`, `prob`, `note`, row format, periodicity). The user opens the symlinked binary in the marble GUI and then "Open python-file".
- Run it with `python data.py data.bin`; it writes `data.hdf5` next to the input (hence the symlinks).
- Hand-editing the generated converter is a last resort: mark the edit with a comment. The GUI regenerates the converter on every save, so hand edits get lost.
