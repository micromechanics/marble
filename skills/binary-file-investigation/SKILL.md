---
name: binary-file-investigation
description: Investigate an unknown binary file (e.g. an instrument's .bin/.dat/.mst/.mvl/.mss file) together with the user, with a fast scan, informed questions and traceable reasoning. Produces a converter to NeXus-style HDF5 (a pymarble .py, or a standalone Python converter for compressed or container files) and a format description. Use when the user wants to decode, reverse-engineer or understand the content of a binary file without format documentation.
---

# Binary file investigation

Goal: understand an unknown binary file together with the user, and deliver
- a **converter** to NeXus-style HDF5: the marble `.py`, which the user can also open in the marble GUI, or a standalone Python converter if the file is out of marble's scope (see step 1)
- **`format.md`** for LLMs and humans: the layout, coverage, reasoning chains and open questions.

Run commands from the pymarble repository root, with its `.venv`. Scripts saved elsewhere need `PYTHONPATH=<repo root>` to import pymarble.

**Third-party tools and Python packages:** use any tool or package that helps (e.g. `olefile`, `xlrd`, `openpyxl`, decompressors), installed in the scratchpad, not in the user's environment: `python3 -m venv <scratchpad>/venv` or `pip install --target <scratchpad>/pylib <package>`. Just use them; no need to ask. If a third-party tool already extracts all scientific data of the file, say so and do not create a converter.

**Reference files** in this folder, read them when the step says so:
- `marble.md`: the pymarble API for labelling, comparing, searching values, row-wise data, several measurements per file, strings, images, coverage and the marble converter.
- `containers.md`: compressed data and container files (out of marble's scope).

## Provenance rule (applies to every step)

Every claim states where it came from and how it was reached: in the discussion, in `format.md` and in each labelled section's `note`.

| Code | Source |
|---|---|
| **B** | byte observation (tool + command + offset) |
| **U** | user statement |
| **E** | exported file |
| **A** | binary-archaeologist finding (with its confidence) |
| **C** | comparison across samples |
| **I** | inference |

- **Chain**: the steps from the first lead to the conclusion. Example: "`strings` shows `npts=4096` at 0x1F0 → 4096 × 8 B = 32768 B → 4096 doubles from 0x400 end at 0x8400 → hypothesis: spectrum → confirmed by user."
- Mark inferences as inferences. Never present them as facts.

## 0. Working folder

Converters and analysis tools write their outputs next to the file they read. Work on symlinks in a separate folder in the scratchpad, never on files in the user's data folder: existing outputs there (e.g. `.hdf5` from an earlier converter) would be overwritten.

```bash
mkdir -p <scratchpad>/data.bin_investigation && ln -sf "$(realpath data.bin)" <scratchpad>/data.bin_investigation/data.bin
```

Symlink every further sample and export into that folder in the same way before running any tool on it.

## 1. Fast scan (seconds, before any questions)

List the folder next to the file immediately. Sibling files can be exports (.txt/.csv/.xls/.xlsx, often oddly named, like `name#Auto-created gr#1.TXT`), other samples, images, logs, earlier converter outputs or earlier decoding attempts. Open them as far as useful. Match related files by file stem and by the date/time inside them.

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
fBIN = BinaryFile('<scratchpad>/data.bin_investigation/data.bin', verbose=1)
print(fBIN.entropy())          # average entropy: < 3.3 metadata, > 4 real data, close to 8 compressed
fBIN.automatic('x_z_a')        # x: XML, z: zero sections, a: ascii (incl. length-prefixed strings)
for k, s in fBIN.content.items():   # compact list of identified sections
  if s.dType not in 'bB': print(k, s.dType, s.length, s.key, s.prob, s.value[:40])
```

`automatic('x_z_p_a')` also searches time series (`p`), but it can run for minutes on large files; run `p` later on a specific section (see `marble.md`).

**Decide the path:**
- **marble path:** the file is one linear sequence of values. Continue with steps 2–4 and use `marble.md`.
- **Container path:** an entropy close to 8 bits per byte throughout, or container signatures such as `d0 cf 11 e0` (OLE2 compound file) or `PK` (ZIP), mean compressed data or a container (see docs/source/concepts.rst, "Compressed data and container files"). marble cannot generate their converter. Continue with steps 2–4 and use `containers.md`.

Report the scan results to the user, with sources and offsets.

## 2. Questions to the user

1. **Hypotheses from the scan.** Name concrete offsets. Example: "XML at 0x200 names InstrumentX v3. Is that the program that wrote the file?" Or: "0x1000–0x9000 looks like 4096 doubles. Is that a spectrum?"
2. **Open questions** for what the scan cannot show:
   - Which program and instrument wrote the file?
   - Which files belong together?
   - Is there an exported text/CSV/Excel version of the same measurement?
   - What values, units and array lengths are expected?

## 3. Leads

- **Exports are the strongest lead.** Excel exports (.xls/.xlsx) count as exports: always read them, like csv (`pandas.read_excel`, with `xlrd` for .xls, `openpyxl` for .xlsx). Their header parameters (settings, units, date and time) are known values to search for. Row and point counts can differ by a few points from the binary (e.g. the export drops the last point or starts at surface contact).
- **Units before typos.** File names and user statements can be wrong; trust the data, report a mismatch as a lead, and note it in `format.md`. Before suspecting a typo, check unit conversions (g = 9.80665, 1000, 25.4, …): a file named `..._150mN` stored its loads in kgf, which looked like 15 mN when read as N. Legacy instruments often use one consistent unit system (e.g. kgf, mm, s); once two channels fit it, test the others against it.
- **The vendor's self-description.** Files often contain their own definitions: channel or parameter objects with display names, descriptions, formulas and unit codes. Look for them before guessing; they settle names and units at once (e.g. a unit code whose high word is the physical quantity).
- **Search for known values** (from exports, the user, plausible constants such as 9.80665 or diamond's 1141 GPa / 0.07) at every byte offset, as float32 and float64, in display and SI units (see `marble.md`).
- **Record streams with an index.** If reading records in sequence gives contradictory results (a value followed by the name of a different object, texts starting mid-word), the buffer probably holds stale records from older versions. Look for an index before resorting to heuristics:
  - **Recognise it:** a block of the same size in every object, holding small integers (types), seemingly random values (hashes of the key names) and integers that lie inside the buffer (offsets).
  - **Test it:** check whether these offsets land exactly on record starts, and whether the key and value found there belong together.
  - **Use it:** read every object only through its index; records no index references are leftovers. An entry can also reference another object (nested objects, e.g. a current and an original configuration).
- **binary-archaeologist (optional)** for small files (under about 5 MB) when large regions stay unknown. Expect mostly noise (padding, false timestamps, UUIDs and signatures inside float or pixel data) with rare great finds (repeated fixed-width records, confirmation that there are no checksums, compression or embedded files). Install it in the scratchpad (`pip install git+https://github.com/i3T4AN/binary-archaeologist`); it reads the path from a prompt: `echo <path> | binary-archaeologist --quiet`; then read the HIGH and MEDIUM findings of `<file>.analysis.txt` first.

## 4. Deeper phase

Work through the leads with the reference file of your path: `marble.md` or `containers.md`.

**Check in batches.** Work for a while, then present several findings at once. For each finding, give offset, length, type, suspected meaning, unit, confidence and its chain. Let the user confirm or correct, then continue.

**Choose keys in NeXus style:** lower case letters, digits and underscores, starting with a letter (`test_duration`, `pixel_size_x`, not `testDuration`). The HDF5 follows the NeXus convention (validated with `punx`); units go into a separate unit field (written as `<key>_units` or `@units`), not into the key.

**The investigation is done when the user says so.**

## 5. Deliverables

1. **Converter**
   - marble path: the marble `.py` from `fBIN.savePython()` (details in `marble.md`).
   - Container path: a standalone `<name>_converter.py` (details in `containers.md`).
   - Test it on the file and on a second, symlinked sample if available.
   - **Check the values, not only that it runs:** a converter can report success and still read wrong offsets. Open the `.hdf5`, compare every value with its expectation (export, user statements, plausible ranges and units), check array shapes against the counts, and validate with `punx validate <file>.hdf5`:
     ```python
     import h5py
     with h5py.File('data.hdf5') as f:
       f.visititems(lambda name, obj: print(name, getattr(obj, 'shape', ''), dict(obj.attrs)))
     ```
2. **`format.md`:**
   - at the top, a **coverage block** with each measure that is available:
     - **fields:** labelled sections vs. potential fields in unknown regions (marble: `fBIN.coverage()`); for containers: decoded streams vs. all streams. This is the main measure: metadata counts as much as a large data array.
     - **varying** (with samples): labelled sections that contain bytes varying between samples vs. varying regions outside them.
     - **export** (with an export): export columns and header parameters located in the binary, e.g. "14 of 16".
     - **bytes:** fraction of the file in labelled sections or decoded streams; context only, since it is dominated by data arrays.
   - a table with offset (or stream), length, type, meaning, unit, whether it changes between measurements, confidence and evidence
   - each row's reasoning chain below the table
   - open questions
3. **Copy** the converter, `format.md` and the HDF5 files into a new subfolder of the source data folder (e.g. `<name>_investigation/`). Never overwrite existing files there.
