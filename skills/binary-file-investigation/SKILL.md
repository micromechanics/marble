---
name: binary-file-investigation
description: Investigate an unknown binary file (e.g. an instrument's .bin/.dat/.mst/.mvl file) together with the user, using a fast scan, informed questions, binary-archaeologist and the pymarble Python API. Produces a pymarble .py (converter and GUI-readable description) and a format description with traceable reasoning. Use when the user wants to decode, reverse-engineer or understand the content of a binary file without format documentation.
---

# Binary file investigation

Goal: understand an unknown binary file together with the user.

Deliverables:
- **For the user**, in the marble GUI: the marble `.py`.
- **For LLMs**: `format.md`, with the reasoning chains.

Run all commands from the pymarble repository root, with its `.venv`. Scripts saved elsewhere need `PYTHONPATH=<repo root>` to import pymarble.

## Provenance rule (applies to every step)

Every claim states where it came from and how it was reached: in the discussion, in `format.md` and in each section's `note`.

**Source types:**

| Code | Source |
|---|---|
| **B** | byte observation (tool + command + offset) |
| **U** | user statement |
| **E** | exported file |
| **A** | binary-archaeologist finding (with its confidence) |
| **C** | comparison across samples |
| **I** | inference |

- **Chain**: the steps from the first lead to the conclusion. Example: "`strings` shows `npts=4096` at 0x1F0 → 4096 × 8 B = 32768 B → `findStreak('d', 0x400)` finds 4096 doubles ending at 0x8400 → hypothesis: spectrum → confirmed by user."
- Mark inferences as inferences. Never present them as facts.

## 0. Working folder

Converters, marble and binary-archaeologist write their outputs next to the file they read. Work on symlinks in a separate folder, never on files in the user's data folder: existing outputs there (e.g. `.hdf5` from an earlier converter) would be overwritten.

```bash
mkdir -p data.bin_investigation && ln -sf "$(realpath data.bin)" data.bin_investigation/data.bin
```

Symlink every further sample into that folder in the same way before running any tool on it.

## 1. Fast scan (seconds, before any questions)

List the folder next to the file immediately. Sibling files can be any of:
- exports (.txt/.csv, often oddly named, like `name#Auto-created gr#1.TXT`)
- other samples
- images, logs
- earlier converter outputs

Open them as far as useful. Match related files by file stem and by the date/time inside them.

```bash
ls -la "$(dirname "$(realpath data.bin)")"
file -L data.bin; ls -lL data.bin
xxd data.bin | head -n 32
strings -n 6 -t d data.bin | head -n 100        # ASCII
strings -n 6 -el -t d data.bin | head -n 50     # UTF-16LE
LC_ALL=C grep -obUaP '<\?xml|\{"|\xff\xd8\xff|\x89PNG|BM6' data.bin | head    # XML, JSON, JPEG, PNG, BMP
```

```python
from pymarble.file import BinaryFile
from pymarble.section import Section
fBIN = BinaryFile('data.bin_investigation/data.bin', verbose=1)
print(fBIN.entropy())          # average entropy: < 3.3 metadata, > 4 real data
fBIN.automatic('x_z_p_a')      # x: XML, z: zero sections, p: primary data, a: ascii (incl. length-prefixed strings)
for k, s in fBIN.content.items():   # identified sections, compact; fBIN.printList() shows all columns but is very wide
  if s.dType not in 'bB': print(k, s.dType, s.length, s.key, s.prob, s.value[:40])
```

`p` (search for time series) can be very slow on large files: on a 33 MB image file, `x_z_p_a` was still running after 8 minutes, while `x_z_a` took 3 s. If a time series is unlikely (e.g. images, large files), use `automatic('x_z_a')`, and run `p` later only on a specific section: `fBIN.automatic('p', start=<offset>)`.

If there are several samples, run the file-level comparison right away: `fBIN.compare([other files])`. It reports sizes, common prefix and equal bytes per file pair. See section 3.

Report the scan results to the user, with sources and offsets.

## 2. Questions to the user

1. **Hypotheses from the scan.** Name concrete offsets. Example: "XML at 0x200 names InstrumentX v3. Is that the program that wrote the file?" Or: "0x1000–0x9000 looks like 4096 doubles. Is that a spectrum?"
2. **Open questions** for what the scan cannot show:
   - Which program and instrument wrote the file?
   - Which files belong together?
   - Is there an exported text/CSV version of the same measurement?
   - What values, units and array lengths are expected?

**Exports** are the strongest lead. Use them as follows:
- **Clean a copy** in the investigation folder: cut the header, convert decimal commas, remove CR characters. Never modify the original. `useExportedFile` needs a file readable by `np.loadtxt`:
  ```bash
  awk 'f{gsub(",",".");print} /^X \(mm\)/{f=1}' "export.TXT" | tr -d '\r' > data.bin_investigation/export_clean.txt   # adapt the header pattern
  ```
- **Keep the export header.** Its parameters (settings, units, date and time) are the known values for the batch search in section 3.
- **Row and point counts can differ by a few points.** For example, an export may drop the last point, so don't expect an exact match.

```python
fBIN.useExportedFile('data.bin_investigation/export_clean.txt'); fBIN.printList(True)
```

## 3. Deeper phase

### binary-archaeologist (optional)

Use it only for small files (under about 5 MB), and only when marble and the manual scan leave large regions unknown. It takes minutes on large files.
Expect mostly noise with rare great finds:
- **Noise:** padding, and false timestamps, UUIDs and zlib/BMP/MZ signatures inside float or pixel data.
- **Rare great finds:** repeated fixed-width records or patterns (e.g. a table of 20 × 13-byte records), and confirmation that there are no checksums, compression or embedded files.

```bash
.venv/bin/binary-archaeologist --version || echo "missing: .venv/bin/pip install git+https://github.com/i3T4AN/binary-archaeologist"
echo "$PWD/data.bin_investigation/data.bin" | .venv/bin/binary-archaeologist --quiet     # reads the path from a prompt
grep -n "HIGH\|MEDIUM" data.bin_investigation/data.bin.analysis.txt | head -60          # then read sections with sed -n
```

If it is missing, report the install command and wait. Do not install it unasked.

Read the HIGH and MEDIUM findings first: signatures, records, repeated patterns, strings, checksums. LOW findings (timestamps, UUIDs, zlib headers inside float data) are leads only.

### Compare samples

```python
fBIN.compare(['data.bin_investigation/other1.bin', 'data.bin_investigation/other2.bin'],
             anchor=rb'\x0a\x00\x00\x00\d\d\.\d\d\.\d{4}')   # regex that starts each measurement unit
```

- **Files first.** For each file pair, `compare()` reports sizes, whether they are identical, the common prefix and the fraction of equal bytes at the same positions. Interpret these yourself:
  - **Identical files** are duplicates.
  - **A high fraction of equal bytes** can mean a shared header (e.g. a small file of mostly header and padding), or cumulative files (the smaller file's measurements reappear in the larger one). Check which by looking at where the bytes differ.
  - Cumulative files contain the same measurements several times, so compare **units**, not files.
- **Anchor.** Use something that repeats once per unit, e.g. a date string or a count. `compare()` splits all files at the anchor into three groups: head, units and tail. It compares the distinct segments aligned at their start and aligned at their end, and reports the segment lengths.
- **Reading the results.**
  - Varying bytes are settings or results that change per measurement.
  - Constant bytes are instrument constants, or settings nobody changed in this batch. Say so as a caveat.
  - Long runs of varying ranges are data blocks.
  - Segment lengths that differ by multiples of one number hint at the record size.
- **CLI equivalent:** `c <files> anchor=<regex>`.

### Locate known values (batch)

```python
known = {'radius 200 µm': [200, 200e-6], 'speed 1 mm/min': [1, 1/60000], 'length 2 mm': [2, 0.002]}  # displayed unit, SI unit
for name, values in known.items():
  for value in values:
    for dType in ('f', 'd'):
      hits = [h for h in fBIN.findValue(value, dType, verbose=False) if int(h) < 474]   # restrict to the region; offsets are decimal strings
      if hits: print(f'{name:22s} {value:<10g} {dType} {hits[:5]}')
```

- **`findValue` tests every byte offset.** Headers are often packed, so values sit at odd offsets.
- **Search each value in the displayed unit and in SI units:** mm → m, µm → m, nm → m, mm/min → m/s, N/min → N/s.
- **Restrict hits to the region under investigation.** Values that are common in the data (start loads, 0, 1.0) give many hits elsewhere. Values that occur more than once are ambiguous: resolve them through neighbouring fields or by comparing samples.
- **Rounded export values.** If a value is not found, search again with `fBIN.optFind['maxError'] = 2e-2`, then reset it to `1e-4`. A loose match counts as B + E with medium confidence until neighbouring fields or other samples confirm it.

### Data stored row by row

`automatic()` and `useExportedFile` assume one continuous array per channel. If a large float array is found and a count N sits just before it, test whether its length is k × N, i.e. k values per point:
1. Reshape the floats to (N, k) with numpy.
2. Compare each column with the export, trying unit scalings (m → mm/nm).
3. Record the format:

```python
fBIN.setRowFormat(474, 11, 'f', columns=[{'key':'x','unit':'m'}, {'key':'ft','unit':'N'}, ...])   # N read from the count in front
```

**Several measurements per file (periodicity).** marble wraps the sections of the first measurement in a loop, `for idxTest in range(numberOfTests)`. It reads them sequentially with the relative offsets of the first measurement, so the following rules apply:
- **Count:** label the count of measurements as a count section, e.g. `tag(29, 1, 'i', 'number_of_tests', dClass='count')`.
- **First and last section:** both must be important (labelled). The last section of the measurement must be labelled too, otherwise the loop's position is off by its length.
- **Equal gaps:** the gap from the last written section *before* the loop to `start` must equal the gap from the end of `end` to the next measurement's `start`. If they differ, label a small section before the loop so that they match.
- **Sections after the first measurement:** all of them must be unimportant: `for k in fBIN.content: if k > end: fBIN.content[k].important = False`.
- **Irregular measurements:** if the gaps between measurements differ (e.g. embedded images between test 1 and 2 only), periodicity cannot be used. Label each measurement's sections separately and give keys the suffix `_t<k>` (`speed_t1`, `speed_t2`, …). The converter then reads fixed offsets, so it only fits files with the same layout, and everything lands in the HDF5 group `test_1`. Say so in `format.md`.
- **Values outside the measurements** (file header, settings common to all tests) labelled with dClass `metadata` or `primary` go into the HDF5 group `/settings` (NXparameters).
- **Size check:** if the file has a trailer after the last measurement, the converter's final check prints "Translation NOT successful" although the data is read correctly. Check the `.hdf5` instead.

```python
fBIN.periodicity = {'count': 29, 'start': 62, 'end': 78368}   # offsets: count of measurements, first and last section of one measurement
```

- **CLI equivalents:** `rf <start> <k> <dType> key:unit,...` and `t <count> <start> <end>`.
- **Hand-editing the generated converter is a last resort.** Mark the edit with a comment. The GUI regenerates the converter on every save, so hand edits get lost.

### Embedded images and files

Embedded files (JPEG, PNG, BMP, …) and raw byte images are labelled as dType `b`, important; the converter writes them as uint8 dataset. Find the length in the file header (e.g. BMP size field, a length field in front) or the end marker (JPEG `ffd9`):

```python
fBIN.content[66911] = Section(length=25464, dType='b', key='image_jpeg', important=True, prob=100, dClass='primary'); fBIN.fill()
fBIN.content[92556] = Section(length=16384, dType='b', key='image_bmp_pixels', shape=[64,64,4], important=True, prob=100,
                              dClass='primary'); fBIN.fill()   # raw pixels: shape reshapes the uint8 array
```

### Strings with a length prefix

`automatic()` detects strings that have a 2- or 4-byte length prefix. Each such string gets a separate count section `strLen<offset>=<length>`, and the converter reads the string via that prefix. Trust the prefix over `strings` and over plain ASCII detection, both of which can cut a string short or add neighbouring bytes.

`automatic()` only finds strings of at least `optAutomatic['minChars']` (10) characters. Find shorter ones (e.g. "V-294") in the manual scan with `strings -n 4 -t d` and `xxd`, and label them with `tag(offset, length, 'c', key)`. If a length prefix is in front, also tag it as count section (`tag(offset-4, 1, 'i', 'strLen<offset>=<length>', dClass='count')`) and pass `count=[offset-4]`.

### Look and label

```python
fBIN.file.seek(0x400); fBIN.printNext(20, 'f')   # also fBIN.printAscii(10), fBIN.findStreak('d', 0x400)
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
tag(126, 1, 'f', 'speed', 'm/s', 'B+E: f32 = TXT "Speed 1 mm/min" as 1.667e-5 m/s; C: varies per test', 100)
tag(1019, 4096*4096, 'H', 'image', 'counts', dClass='primary', count=[1011, 1015], shape=[4096, 4096])  # count sections must exist
```

- Use `tag` rather than `label()` for single values. `label()` treats every `f`/`d` section as an array, and it forces `prob` to 100.
- **Keys in NeXus style:** lower case letters, digits and underscores, starting with a letter (`test_duration`, `pixel_size_x`, not `testDuration`). The HDF5 follows the NeXus convention (validated with `punx`), and the converter lowercases keys anyway; choosing them this way from the start keeps the names identical in the GUI, `format.md` and the HDF5. Units go into `unit` (written as `<key>_units`), not into the key.
- `fBIN.content` is a `SortedDict[int, Section]` keyed by start offset. The fields are described in `pymarble/section.py`.
- Tune the automatic search with `fBIN.optAutomatic`, `fBIN.optFind` and `fBIN.optEntropy`.

**Check in batches.** Work for a while, then present several findings at once. For each finding, give offset, length, type, suspected meaning, confidence and its chain. Let the user confirm or correct, then continue.

**The investigation is done when the user says so.**

## 4. Deliverables (in the `_investigation/` folder)

1. **`fBIN.savePython()` → `data.py`. This is the main deliverable.**
   - It is a converter, and its end block describes every section (`key`, `unit`, `prob`, `note`, row format, periodicity).
   - The user opens the symlinked binary in the marble GUI, then uses "Open python-file".
   - Test it with `python data.py data.bin`, which writes `data.hdf5` in the same folder. Also test it on a second, symlinked sample.
   - Check the values, not only that it runs: a converter can print "Translation successful" and still read wrong offsets. Open the `.hdf5`, compare every labelled value with its expectation (export, user statements, plausible ranges and units), and check array shapes against the counts:
     ```python
     import h5py
     with h5py.File('data.hdf5') as f:
       f.visititems(lambda name, obj: print(name, getattr(obj, 'shape', ''), dict(obj.attrs)))
     ```
2. **`format.md`:**
   - at the top, a coverage block: how much of the file is understood. Report each measure that is available:
     ```python
     fBIN.coverage(['data.bin_investigation/other.bin'], anchor=rb'...')   # without samples: fBIN.coverage()
     ```
     - **fields:** labelled sections vs. potential fields in unknown regions (4 bytes per field, at most 32 per region). This is the main measure: metadata counts as much as a large data array.
     - **varying** (with samples): labelled sections that contain bytes varying between samples vs. varying regions outside labelled sections.
     - **export** (with an export): number of export columns and header parameters located in the binary, e.g. "14 of 16". Count these yourself.
     - **bytes:** fraction of the file in labelled sections; context only, since it is dominated by data arrays.
   - a table with offset, length, type, meaning, unit, whether the field changes between measurements, confidence and evidence
   - each row's reasoning chain below the table
   - open questions

