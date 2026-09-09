Binary data concepts for scientists
************************************

This page introduces the concepts needed to use MARBLE when you are not
already familiar with binary files or programming data types.

What is a byte?
================

Computers store files as a sequence of small units called **bytes**. One byte
contains eight bits, and each bit is either 0 or 1. A byte can represent 256
different values, from 0 to 255.

Binary files are usually described using byte positions, also called
**offsets**. The first byte has offset 0, the second has offset 1, and so on.
An offset is therefore a location in the file, not a measurement value.

Numbers and their sizes
=======================

The same bytes can represent different values depending on the data type used
to interpret them. Common types are:

.. list-table:: Common MARBLE data types
   :header-rows: 1
   :widths: 18 18 18 46

   * - Type
     - Size
     - Example
     - Meaning
   * - ``b``
     - 1 byte
     - ``-4``
     - Signed whole number from -128 to 127
   * - ``B``
     - 1 byte
     - ``250``
     - Unsigned whole number from 0 to 255
   * - ``i``
     - 4 bytes
     - ``-12``
     - Signed integer
   * - ``f``
     - 4 bytes
     - ``3.14``
     - Decimal number with ordinary precision
   * - ``d``
     - 8 bytes
     - ``3.1415926535``
     - Decimal number with higher precision
   * - ``c``
     - 1 byte
     - ``A``
     - One text character
   * - ``s``
     - Variable
     - ``hello``
     - A sequence of bytes, often used for text

For example, 100 values stored as ``float`` values occupy 400 bytes, while
100 values stored as ``double`` values occupy 800 bytes. This relationship
between the number of values and the number of bytes is one of the clues MARBLE
uses when identifying sections.

The letters in this table are the format codes used by Python's ``struct``
module and by MARBLE's CLI. They are not file extensions.

Byte order
==========

Multi-byte values can store their bytes in different orders. This is called
**endianness**. MARBLE supports the common little-endian order, shown as
``small`` in its metadata. It is intended for typical desktop
computers and instrument files.

Sections, lengths, and counts
=============================

MARBLE treats a binary file as a sequence of **sections**. A section has:

* a start offset;
* a length, meaning how many values it contains;
* a data type, such as ``i``, ``f``, or ``d``;
* optional metadata such as a key, unit, and link.

A **count** is a value in the file that tells how many items belong to another
section. For example, a file may store the number ``100`` followed by 100
temperature values. If the values are doubles, the data section should occupy
800 bytes. Checking this relationship is often a useful way to confirm or
reject a proposed interpretation.

Metadata describes the experiment, such as the operator or measurement unit.
Primary data is what was measured, such as force, displacement, or time.
Undefined sections are portions MARBLE has not identified yet.

Worked workflow
===============

The following is the typical workflow for a new binary file.

#. Install MARBLE and open the GUI, or start with the CLI::

      pip install pymarble
      marbleGUI

#. Load the binary file. MARBLE initially shows the file as one unknown
   section.
#. Run automatic identification. Treat its results as suggestions, not as
   proof that the sections have been identified correctly.
#. Inspect candidate sections. Compare their offsets, lengths, data types, and
   values. Use known facts about the instrument, such as the expected number
   of measurements or the physical units.
#. Label sections manually. For measured data, record a meaningful key such
   as ``temperature`` or ``force`` and add the unit, such as ``degC`` or ``N``.
#. Mark the sections that should be exported as important.
#. Save a ``.tags`` file while working. It preserves the current annotations
   and allows them to be reloaded later.
#. Save the generated Python converter when the interpretation is complete.
#. Run the converter on a source binary file. The converter creates an HDF5
   file containing the selected primary data and metadata::

      python generated_converter.py source_file.dat

#. Check the converter's success message and inspect the HDF5 contents with
   an HDF5 viewer or a Python library such as ``h5py``.

If the result is implausible, return to the section labels. The most common
causes are an incorrect start offset, length, data type, or count relationship.

How to interpret confidence
===========================

Each section has a probability or confidence value. It is intentionally a
user-editable heuristic that helps organize review work, rather than a
mathematical certainty score. Use it as a review queue:

* **0** means that the section is still unidentified.
* **10-40** usually means that an automatic method found a weak clue, such as
  a run of zeros or a short text fragment.
* **20** is commonly used for a candidate numeric series found by a pattern
  search. It is useful evidence, but it does not identify the scientific
  meaning of the values.
* **50-90** indicates a stronger numerical fit or a longer recognizable text
  fragment.
* **99-100** is useful for sections that have been manually reviewed or have
  particularly strong automatic evidence.

Adjust the value as your understanding develops. It helps distinguish sections
you still need to inspect from those you have already reviewed. Before marking
a section important, verify that its values, byte size, length, and units agree
with the experiment.



Working example with a real sample file (command line interface)
================================================================

The repository includes a sample tensile-machine file at
``tests/examples/Membrane_Repeatability_05.mvl``. The following commands are
run from the repository root.

Start by asking MARBLE to identify likely sections and save the working
annotations::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "m; ot"

The ``m`` command runs automatic identification. The ``ot`` command writes a
``.tags`` file next to the binary file. Automatic identification is a starting
point: inspect the proposed sections and use knowledge of the instrument to
confirm them.

In this sample, the first useful signal starts at byte offset 69280. It has
195 values, and the values are 8-byte doubles. The command below labels it as
time in seconds and saves the updated annotations::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 69280 195|d|time|s; ot"

Here ``it`` loads the annotations, and ``r`` replaces the section at the given
offset. The section description has the form
``length|type|key|unit|link``. Thus ``195|d|time|s`` means 195 double values
with the key ``time`` and unit ``s``. Since a double occupies 8 bytes, this
section occupies 1560 bytes.

The next two signals contain 195 4-byte float values. Label them as
displacement in millimetres and force in newtons::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 70840 195|f|displacement|mm; ot"
   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 71620 195|f|force|N|https://en.wikipedia.org/wiki/Force; ot"

Each float section occupies 780 bytes. The offsets and lengths are not guessed
from the physical units alone: they are checked against the instrument's expected data layout.

The sample also contains metadata labels. Metadata has no numeric type in the
command because the empty fields tell MARBLE to keep the existing section
format::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 6836  ||displacement_label; ot"
   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 12832 ||force_label; ot"
   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 21148 ||process_name; ot"
   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 32228 ||some_name; ot"
   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 58448 ||path_name; ot"

Finally, generate the converter and run it on the sample file::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; op"
   python tests/examples/Membrane_Repeatability_05.py tests/examples/Membrane_Repeatability_05.mvl

The generated converter creates an HDF5 file next to the input file. A
successful conversion prints ``Translation successful``. The converter can
also be tested on the related ``Membrane_Repeatability_08.mvl`` sample::

   python tests/examples/Membrane_Repeatability_05.py tests/examples/Membrane_Repeatability_08.mvl

This example illustrates the main decision: a proposed interpretation must
make sense both scientifically and structurally. For 195 floats, for example,
the expected section size is ``195 * 4 = 780`` bytes. If the size, values, or
neighbouring offsets do not fit, revisit the start offset or data type.

Inspecting the generated HDF5 file
==================================

After running the worked example, the generated file is
``tests/examples/Membrane_Repeatability_05.hdf5``. You can inspect its groups,
datasets, shapes, units, and first values with ``h5py``::

   import h5py

   with h5py.File("tests/examples/Membrane_Repeatability_05.hdf5", "r") as h5:
       print("groups:", list(h5.keys()))
       data = h5["test_1/data"]
       print("datasets:", list(data.keys()))
       for name, dataset in data.items():
           print(name, "shape=", dataset.shape,
                 "unit=", dataset.attrs.get("unit", ""))
           print("  first values:", dataset[:5])

The expected structure for this sample is a ``test_1/data`` group containing
the ``time``, ``displacement``, and ``force`` datasets. Dataset attributes hold
information such as units and links. If a dataset is missing, has an
unexpected shape, or contains implausible values, revisit the corresponding
section annotation and regenerate the converter.

Troubleshooting section identification
=======================================

Incorrect start offset
----------------------

If the first values look like noise, the section may start a few bytes too
early or too late. Try nearby offsets and compare the resulting values. A
correct start normally gives a smooth signal or recognizable metadata, while
an incorrect offset often produces extreme values, ``nan``, or an unrelated
pattern. Use the CLI to inspect a candidate region before relabeling it::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; d 69272"

Incorrect data type
-------------------

If values are plausible but their scale is wrong, compare ``f`` and ``d``.
Floats use 4 bytes and doubles use 8 bytes, so changing the type also changes
the expected end offset. A candidate that looks like a signal with ``f`` but
random values with ``d`` is evidence for the float interpretation; confirm it
using the instrument documentation and neighbouring sections::

   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 70840 195|f|displacement|mm"
   marbleCLI tests/examples/Membrane_Repeatability_05.mvl "it; r 70840 195|d|displacement|mm"

The second command is an experiment. Save the interpretation you decide to
keep with ``ot``.

Incorrect length or count
-------------------------

If a section overlaps the next section, leaves an unexpected gap, or produces
the wrong number of measurements, check its length and any count field. The
expected byte size is ``length * size_of_one_value``. For example, 195 floats
occupy 780 bytes. For repeated measurements, the count should agree with the
number of data values in each test. A converter may also report a translation
failure when the interpreted sections do not consume the expected file layout.

Incorrect byte order
--------------------

MARBLE supports only ``small`` (little-endian) files on typical little-endian
computers. Big-endian files are outside the current scope. If every multi-byte
value is implausibly large, tiny, or patterned, first confirm that the source
file is little-endian; otherwise use a tool that supports its byte order.

General recovery procedure
--------------------------

Keep the last working ``.tags`` file, change one property at a time, and save
the result. Re-run the converter after each meaningful change. This makes it
possible to identify whether the problem is the offset, type, length, count,
or byte order rather than changing several explanations at once.

Glossary
========

**Binary file**
   A file represented as bytes rather than human-readable text.

**Byte offset**
   The zero-based position of a byte in a file.

**Data type**
   The rule used to interpret bytes as a character, integer, or decimal number.

**Float**
   A 4-byte decimal number. It usually provides less precision than a double.

**Double**
   An 8-byte decimal number. It usually provides more precision than a float.

**Integer**
   A whole number without a fractional part. Its range depends on its size and
   whether it is signed.

**Metadata**
   Information describing the experiment or the measured data.

**Primary data**
   The measurements the instrument was intended to record.

**HDF5**
   A structured output format that stores datasets, attributes, and groups in
   a way that can be read by many programming languages and scientific tools.
