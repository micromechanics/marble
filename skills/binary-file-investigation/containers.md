# Container path: compressed data and container files

Read this when the fast scan shows an entropy close to 8 bits per byte, or a container signature (`d0 cf 11 e0` OLE2 compound file, `PK` ZIP). marble cannot generate converters for these files (docs/source/concepts.rst, "Compressed data and container files"); deliver a standalone Python converter. marble can still analyse streams once they are extracted and decompressed.

## 1. Open the container

- **OLE2 compound file** (Microsoft CFB; e.g. MTS/Agilent NanoSuite `.mss`): `olefile` lists and reads all streams (`OleFileIO(f).listdir()`, `.openstream(path).read()`). The directory is a tree of storages and streams; streams are scattered over sectors, so never read them from the raw file.
- **ZIP**: `zipfile` from the standard library.
- List every stream with path, size, entropy and first 16 bytes. Streams of the same kind share a header (magic bytes), e.g. one header type for data arrays, another for metadata.

## 2. Identify the compression

- Entropy 7–8 inside a stream means compressed or encrypted.
- Look at the first bytes after the stream header and try decompressors at several offsets: `zlib` (also raw deflate `wbits=-15`, gzip `wbits=31`), `lzma`, `bz2`, and PKWARE DCL "implode" (header `00 04/05/06` = binary, `01 ..` = ASCII, then dictionary size; decompress with the `dclimplode` package).
- **Verify with a second, independent implementation** when possible: byte-identical output from two decoders rules out decoder bugs. Old copies of decoders can be buggy (an old pure-Python `pwexplode.py` encoded every byte ≥ 0x80 as UTF-8 and silently corrupted the output).
- Check the decompressed length against a length or count field in the stream header (e.g. n × 8 bytes for n float64).

## 3. Decode the streams

- **Data streams:** usually a header (magic, flags, count, compressed length) followed by an array. A flag byte can switch compression per stream; handle both variants.
- **Units:** compare with exports and known values; legacy unit systems (kgf, mm, s) are common. Look for the vendor's channel or unit definitions in the metadata streams (display name, description, formula, unit code).
- **Metadata streams:** often pages of key/value records (u32 length + payload) holding objects. Pages can start with a partial record and hold stale records; read objects through their index (see "Record streams with an index" in `SKILL.md`). Nested objects (an index entry referencing another object's index) are common for configurations, e.g. an indenter tip with its area function.
- **marble on extracted streams:** write a decompressed stream to a file in the investigation folder and use `BinaryFile`, `findValue`, `compare` etc. on it (`marble.md`).
- **Order and identity:** containers often name measurements randomly (e.g. 11-letter storage names); look for an order stream, and confirm the order by matching data against the export.

## 4. The standalone converter

- Name: `<name>_converter.py`; usage `python <name>_converter.py <file>` writes `<file>.hdf5` next to the input.
- Same HDF5 structure as marble's converters:
  - one group `test_<k>` (`NX_class` NXentry) per measurement, with a subgroup `data` (NXdata, `signal` and `axes` set)
  - one dataset per channel with `@units`; add the vendor's display name, description and formula as `long_name`, `description`, `formula` if available
  - common settings in `/settings` (NXparameters); scalar values as attributes with `<key>_units`
  - NeXus-style keys (lower case, underscores)
- Keep dependencies to the standard library, numpy, h5py and well-maintained packages from PyPI (e.g. `dclimplode`); prefer own short readers over large third-party code with an unclear license.
- Write values as stored and state the units explicitly; mark units that are only inferred in `format.md`.
- Validate with `punx validate <file>.hdf5` and check the values against the export (SKILL.md, step 5).

## 5. Coverage for containers

`fBIN.coverage()` does not apply to the container itself. Report instead:
- **fields:** decoded streams vs. all streams, and within metadata streams the identified objects
- **export:** export columns and parameters located
- **bytes:** fraction of stream bytes decoded (context only)
